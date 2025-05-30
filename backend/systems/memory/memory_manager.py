"""
This class manages the collection of memories for NPCs, integrating with:
- Vector DB for memory storage and query
- Persistent storage for summaries
- LLM for summarization
- Conversation tracking and cleanup logic
"""

import uuid
import logging
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Protocol, TypeVar, Callable
from dateutil.parser import parse as parse_iso

# Import local memory model
from .memory import Memory, MemoryCreatedEvent, MemoryDecayedEvent, MemoryReinforcedEvent

# Import event dispatcher
from backend.systems.events.models.event_dispatcher import EventDispatcher

logger = logging.getLogger(__name__)

# Define a Protocol for VectorDBCollection for better abstraction
class VectorDBCollection(Protocol):
    def add(self, documents: List[str], metadatas: List[Dict[str, Any]], ids: List[str]) -> None:
        ...
    def get(self, where: Dict[str, Any]) -> Dict[str, List[Any]]: 
        ...
    def query(self, query_texts: List[str], n_results: int, where: Optional[Dict[str, Any]] = None) -> Dict[str, List[List[Any]]]:
        ...
    def delete(self, ids: List[str]) -> None:
        ...

# Import custom summarization styles
from .summarization_styles import SummarizationStyle, SummarizationDetail, SummarizationConfig

# Default summarization configurations (using new style system)
DEFAULT_SUMMARIZATION_CONFIG = {
    "chunk_summary": SummarizationConfig.get_config(
        style=SummarizationStyle.CONCISE,
        detail=SummarizationDetail.MEDIUM
    ),
    "memory_summary": SummarizationConfig.get_config(
        style=SummarizationStyle.NEUTRAL,
        detail=SummarizationDetail.MEDIUM
    )
}

class MockChromaCollection:
    """Mock implementation of VectorDBCollection for testing."""
    def add(self, documents, metadatas, ids):
        logging.info(f"[MockChroma] ADD: ids={ids}, docs={documents}, meta={metadatas}")
    def get(self, where):
        logging.info(f"[MockChroma] GET: where={where}")
        return {"ids": [], "metadatas": [], "documents": []}
    def query(self, query_texts, n_results, where):
        logging.info(f"[MockChroma] QUERY: texts={query_texts}, n={n_results}, where={where}")
        return {"documents": [[]]}
    def delete(self, ids):
        logging.info(f"[MockChroma] DELETE: ids={ids}")

class MemoryManager:
    """
    Manages a collection of memories for an NPC, including decay, event emission, and queries.
    This class is instantiated per NPC.
    """
    _instances: Dict[str, 'MemoryManager'] = {}
    _lock = asyncio.Lock() # Lock for thread-safe/async-safe instantiation of NPC managers
    
    def __init__(self, npc_id: str,
                 short_term_db: VectorDBCollection,
                 long_term_db: VectorDBCollection,
                 event_dispatcher: EventDispatcher,
                 character_id: Optional[str] = None,
                 summarization_config: Optional[Dict[str, Any]] = None):
        """
        Initialize a new MemoryManager for an entity.
        :param npc_id: The NPC/entity ID.
        :param short_term_db: VectorDB collection for short-term memories.
        :param long_term_db: VectorDB collection for long-term/archival memories.
        :param event_dispatcher: The central event dispatcher.
        :param character_id: Optional character ID.
        :param summarization_config: Optional configuration for summarization.
        """
        self.npc_id = npc_id
        self.character_id = character_id
        self.short_term_db = short_term_db
        self.long_term_db = long_term_db
        
        self.max_chars_for_summarization = 4000
        self.chunk_size_for_summarization = 1000
        self.conversation_mem: List[Dict[str, str]] = [] # Stores messages for current summarization window
        self.summaries: List[str] = [] # Stores generated summaries from conversation_mem chunks
        self.current_char_count_for_summarization = 0
        
        self.memories: Dict[str, Memory] = {} # In-memory cache of Memory objects, keyed by memory.id
        self.decay_threshold = 0.1
        self.event_dispatcher = event_dispatcher
        self.summarization_config = summarization_config or DEFAULT_SUMMARIZATION_CONFIG
        
        # Initialize memory association manager
        from .memory_associations import MemoryAssociationManager
        self.association_manager = MemoryAssociationManager()
        
        logger.info(f"MemoryManager for NPC {self.npc_id} initialized.")

    @classmethod
    async def get_instance(cls, npc_id: str,
                           short_term_db: VectorDBCollection,
                           long_term_db: VectorDBCollection,
                           event_dispatcher: EventDispatcher,
                           character_id: Optional[str] = None,
                           summarization_config: Optional[Dict[str, Any]] = None) -> 'MemoryManager':
        """Gets or creates a MemoryManager instance for a specific NPC."""
        if npc_id not in cls._instances:
            async with cls._lock:
                if npc_id not in cls._instances: # Double check after acquiring lock
                    cls._instances[npc_id] = cls(
                        npc_id,
                        short_term_db,
                        long_term_db,
                        event_dispatcher,
                        character_id,
                        summarization_config
                    )
        manager = cls._instances[npc_id]
        if character_id and not manager.character_id: # Update character_id if it wasn't set initially
            manager.character_id = character_id
        return manager

    def store_interaction(self, text: str, tags: Optional[Dict[str, Any]] = None, associated_entities: Optional[List[str]] = None) -> str:
        """
        Stores an interaction as a document in the short-term vector DB and accumulates for summarization.
        :param text: The text content of the interaction.
        :param tags: Optional metadata tags for the interaction.
        :param associated_entities: Optional associated entity IDs.
        :return: The memory ID of the stored interaction.
        """
        memory_id = str(uuid.uuid4())
        metadata = {
            "npc_id": self.npc_id,
            "character_id": self.character_id,
            "timestamp": datetime.utcnow().isoformat(),
            **(tags or {})
        }
        
        if associated_entities:
            metadata["associated_entities"] = associated_entities

        self.short_term_db.add(
            documents=[text],
            metadatas=[metadata],
            ids=[memory_id]
        )
        self._accumulate_for_summarization("user", text)
        return memory_id

    def _accumulate_for_summarization(self, role: str, content: str) -> None:
        """
        Accumulate content for summarization, summarize chunks as needed.
        :param role: The role (e.g., 'user', 'assistant') for the content.
        :param content: The text content to accumulate.
        """
        self.conversation_mem.append({"role": role, "content": content})
        self.current_char_count_for_summarization += len(content)
        
        # If we exceed max chars, summarize chunks until we're under the limit
        while self.current_char_count_for_summarization > self.max_chars_for_summarization:
            chunk, size = [], 0
            while self.conversation_mem and size < self.chunk_size_for_summarization:
                msg = self.conversation_mem.pop(0)
                msg_size = len(msg["content"])
                size += msg_size
                self.current_char_count_for_summarization -= msg_size
                chunk.append(msg)
            
            if chunk:  # Ensure we have something to summarize
                summary = self._summarize_chunk(chunk)
                self.summaries.append(summary)

    def _summarize_chunk(self, messages: List[Dict[str, str]], 
                         style: Optional[SummarizationStyle] = None,
                         detail: Optional[SummarizationDetail] = None) -> str:
        """
        Summarize a chunk of messages using an LLM.
        :param messages: The messages to summarize.
        :param style: Optional style override (default: use config)
        :param detail: Optional detail level override (default: use config)
        :return: A summary of the messages.
        """
        import openai
        
        try:
            # Prepare the messages for the LLM
            combined = "".join(f"{m['role'].upper()}: {m['content']}\n" for m in messages)
            
            # Get summarization config
            config = self.summarization_config["chunk_summary"]
            
            # Override style and detail if provided
            if style or detail:
                custom_config = SummarizationConfig.get_config(
                    style=style or SummarizationStyle.NEUTRAL,
                    detail=detail or SummarizationDetail.MEDIUM,
                    model=config.get("model", "gpt-4")
                )
                config = custom_config
            
            res = openai.ChatCompletion.create(
                model=config["model"],
                messages=[
                    {"role": "system", "content": config["system_prompt"]},
                    {"role": "user", "content": combined}
                ],
                temperature=config["temperature"],
                max_tokens=config["max_tokens"]
            )
            return res.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Summarization error: {e}")
            return "(error summarizing)"

    def update_long_term_summary(self, region: Optional[str] = None, 
                                style: Optional[SummarizationStyle] = None,
                                detail: Optional[SummarizationDetail] = None) -> Optional[str]:
        """
        Create or update a long-term summary based on recent interactions.
        :param region: Optional region filter for interactions.
        :param style: Optional summarization style (default: use config)
        :param detail: Optional detail level (default: use config)
        :return: The generated summary, or None if no summary was generated.
        """
        recent_interactions = self.query_recent_interaction_logs(n_results=10, character_id_filter=self.character_id)
        if not recent_interactions:
            return None

        summary = self._summarize_memory_from_docs(recent_interactions, style=style, detail=detail)
        if summary:
            # Update persistence layer with the new summary
            try:
                from firebase_admin import db
                ref = db.reference(f"/npcs/{self.npc_id}/long_term_memory/{self.character_id}")
                ref.set({
                    "last_summary": summary,
                    "summary_date": datetime.utcnow().isoformat(),
                    "style": style.value if style else None,
                    "detail": detail.value if detail else None
                })
            except Exception as e:
                logger.error(f"Error saving summary to persistence layer: {e}")
            
            return summary
        return None

    def _summarize_memory_from_docs(self, docs: List[Dict[str, Any]], 
                                style: Optional[SummarizationStyle] = None,
                                detail: Optional[SummarizationDetail] = None) -> Optional[str]:
        """
        Generate a memory summary from document logs.
        :param docs: The document logs to summarize.
        :param style: Optional style override (default: use config)
        :param detail: Optional detail level override (default: use config)
        :return: A summary of the documents, or None if no summary was generated.
        """
        import openai
        
        if not docs:
            return None
            
        # Extract text content from documents
        if all(isinstance(doc, dict) and "text" in doc for doc in docs):
            log_texts = [doc["text"] for doc in docs]
        elif all(isinstance(doc, dict) and "content" in doc for doc in docs):
            log_texts = [doc["content"] for doc in docs]
        else:
            # If neither format is consistent, try to extract something meaningful
            log_texts = []
            for doc in docs:
                if isinstance(doc, dict):
                    for key in ["text", "content"]:
                        if key in doc:
                            log_texts.append(doc[key])
                            break
                    else:
                        # If we can't find a standard key, use the whole doc as string
                        log_texts.append(str(doc))
                else:
                    log_texts.append(str(doc))

        # Format logs for summarization
        lines = [f"- {text}" for text in log_texts]
        prompt = "\n".join(lines)
        
        try:
            # Get summarization config
            config = self.summarization_config["memory_summary"]
            
            # Override style and detail if provided
            if style or detail:
                custom_config = SummarizationConfig.get_config(
                    style=style or SummarizationStyle.NEUTRAL,
                    detail=detail or SummarizationDetail.MEDIUM,
                    model=config.get("model", "gpt-4")
                )
                config = custom_config
            
            res = openai.ChatCompletion.create(
                model=config["model"],
                messages=[
                    {"role": "system", "content": config["system_prompt"]},
                    {"role": "user", "content": prompt}
                ],
                temperature=config["temperature"],
                max_tokens=config["max_tokens"]
            )
            return res.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Memory summary generation failed: {e}")
            return None

    def add_memory(self, memory: Memory) -> None:
        """
        Add a new memory and emit a creation event.
        :param memory: The Memory instance to add.
        """
        # Store the memory in our in-memory cache
        self.memories[memory.id] = memory
        
        # Emit event via the event dispatcher
        self.event_dispatcher.publish_sync(MemoryCreatedEvent(
            memory_id=memory.id,
            npc_id=memory.npc_id,
            content=memory.content,
            memory_type=memory.type,
            event_type="memory.created"
        ))
        
        logger.debug(f"Memory {memory.id} added for NPC {memory.npc_id}")

    def decay_memories(self, delta_seconds: float) -> None:
        """
        Apply decay to all memories and emit events for those that cross the threshold.
        :param delta_seconds: Time in seconds to decay.
        """
        # Track expired memories for removal
        expired_memories = []
        
        for memory_id, memory in self.memories.items():
            # Skip core memories (they don't decay)
            if memory.type == 'core':
                continue
                
            # Store importance before decay for threshold check
            importance_before = memory.current_importance
            
            # Apply decay
            memory.decay(delta_seconds)
            
            # Check if memory crossed the decay threshold
            if importance_before >= self.decay_threshold and memory.current_importance < self.decay_threshold:
                # Emit decay event
                self.event_dispatcher.publish_sync(MemoryDecayedEvent(
                    memory_id=memory.id,
                    npc_id=memory.npc_id,
                    new_importance=memory.current_importance,
                    event_type="memory.decayed"
                ))
                
                # Mark for removal if expired
                if memory.is_expired(self.decay_threshold):
                    expired_memories.append(memory_id)
        
        # Remove expired memories
        for memory_id in expired_memories:
            if memory_id in self.memories:
                del self.memories[memory_id]
                
        logger.debug(f"Decayed {len(self.memories)} memories for NPC {self.npc_id}, removed {len(expired_memories)} expired memories")

    def prune_expired(self) -> None:
        """
        Remove expired regular memories from the collection.
        """
        expired_ids = [
            memory_id for memory_id, memory in self.memories.items() 
            if memory.is_expired(self.decay_threshold)
        ]
        
        for memory_id in expired_ids:
            del self.memories[memory_id]
            
        if expired_ids:
            logger.debug(f"Pruned {len(expired_ids)} expired memories for NPC {self.npc_id}")

    def reinforce_memory(self, memory_id: str, amount: float) -> Optional[Memory]:
        """
        Reinforce a regular memory, increasing its importance and emitting an event.
        :param memory_id: The ID of the memory to reinforce.
        :param amount: Amount to increase importance by.
        :return: The reinforced memory, or None if not found.
        """
        if memory_id not in self.memories:
            logger.warning(f"Cannot reinforce memory {memory_id}: not found")
            return None
            
        memory = self.memories[memory_id]
        if memory.type != 'regular':
            logger.warning(f"Cannot reinforce memory {memory_id}: not a regular memory")
            return None
            
        # Reinforce up to the initial importance (cap)
        memory.current_importance = min(memory.initial_importance, memory.current_importance + amount)
        
        # Emit event
        self.event_dispatcher.publish_sync(MemoryReinforcedEvent(
            memory_id=memory.id,
            npc_id=memory.npc_id,
            new_importance=memory.current_importance,
            event_type="memory.reinforced"
        ))
        
        logger.debug(f"Memory {memory_id} reinforced for NPC {memory.npc_id}, new importance: {memory.current_importance}")
        return memory

    def get_memory_by_id(self, memory_id: str) -> Optional[Memory]:
        """
        Get a memory by its ID.
        :param memory_id: The ID of the memory to get.
        :return: The memory instance, or None if not found.
        """
        return self.memories.get(memory_id)

    def add_link_between_memories(self, source_memory_id: str, target_memory_id: str, relationship_type: str, strength: float = 1.0) -> bool:
        """
        Add a link between two memories.
        :param source_memory_id: The ID of the source memory.
        :param target_memory_id: The ID of the target memory.
        :param relationship_type: The type of relationship.
        :param strength: The strength of the relationship (0.0 to 1.0).
        :return: True if the link was added, False otherwise.
        """
        if source_memory_id not in self.memories or target_memory_id not in self.memories:
            logger.warning(f"Cannot link memories: one or both not found")
            return False
            
        source_memory = self.memories[source_memory_id]
        source_memory.add_link(target_memory_id, relationship_type, strength)
        logger.debug(f"Link added from memory {source_memory_id} to {target_memory_id} with type {relationship_type}")
        return True

    def get_related_memories(self, memory_id: str, min_strength: float = 0.0) -> List[Memory]:
        """
        Get memories related to a given memory.
        :param memory_id: The ID of the memory to get related memories for.
        :param min_strength: The minimum strength of the relationship to include.
        :return: A list of related memories.
        """
        if memory_id not in self.memories:
            logger.warning(f"Cannot get related memories: memory {memory_id} not found")
            return []
            
        source_memory = self.memories[memory_id]
        return [
            self.memories[link.target_memory_id] 
            for link in source_memory.links 
            if link.strength >= min_strength and link.target_memory_id in self.memories
        ]

    def query_memories(self, query_text: str, n_results: int = 5, tags: Optional[List[str]] = None, type_: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Query memories based on a text query.
        :param query_text: The text query to search for.
        :param n_results: The maximum number of results to return.
        :param tags: Optional list of tags to filter by.
        :param type_: Optional memory type to filter by.
        :return: A list of memory dictionaries.
        """
        # Build where clause for chromadb
        where_clause = {"npc_id": self.npc_id}
        
        if tags:
            # Note: This assumes tags are stored in a way that ChromaDB can query them
            where_clause["tags"] = {"$in": tags}
            
        if type_:
            where_clause["type"] = type_
            
        # Query the vector database
        results = self.short_term_db.query(
            query_texts=[query_text],
            n_results=n_results,
            where=where_clause
        )
        
        # Process the results
        if not results or not results.get("documents") or not results["documents"][0]:
            logger.debug(f"No memories found for query: {query_text}")
            return []
            
        # Assuming 'ids', 'documents', and 'metadatas' are properly aligned
        memories_data = []
        if all(key in results for key in ["ids", "documents", "metadatas"]):
            for i, (doc_id, text, metadata) in enumerate(zip(results["ids"][0], results["documents"][0], results["metadatas"][0])):
                memories_data.append({
                    "id": doc_id,
                    "content": text,
                    "metadata": metadata,
                    "distance": results.get("distances", [[0] * len(results["ids"][0])])[0][i]
                })
                
        logger.debug(f"Found {len(memories_data)} memories for query: {query_text}")
        return memories_data

    def query_recent_interaction_logs(self, n_results: int = 5, character_id_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Query recent interaction logs from the long-term database.
        :param n_results: The maximum number of results to return.
        :param character_id_filter: Optional character ID to filter by.
        :return: A list of interaction log dictionaries.
        """
        # Define the cutoff time (e.g., last 3 hours)
        cutoff = datetime.utcnow() - timedelta(hours=3)
        
        # Build query filters
        filters = {
            "npc_id": self.npc_id,
            "timestamp": {"$gt": cutoff.isoformat()}
        }
        
        if character_id_filter:
            filters["character_id"] = character_id_filter
            
        # Query the long-term database
        results = self.long_term_db.get(where=filters)
        
        # Process the results
        if not results or not results.get("documents"):
            logger.debug(f"No recent interaction logs found for NPC {self.npc_id}")
            return []
            
        # Create a list of document dictionaries
        docs = []
        for i, (doc_id, content, metadata) in enumerate(zip(results["ids"], results["documents"], results["metadatas"])):
            docs.append({
                "id": doc_id,
                "content": content,
                "metadata": metadata
            })
            
        # Sort by timestamp (most recent first)
        docs.sort(key=lambda x: parse_iso(x["metadata"].get("timestamp", "")), reverse=True)
        
        # Limit to n_results
        docs = docs[:n_results]
        
        logger.debug(f"Found {len(docs)} recent interaction logs for NPC {self.npc_id}")
        return docs

    def summarize_and_clean_short_term(self, days_old: int = 3) -> Dict[str, Any]:
        """
        Summarize and clean short-term memories older than a specified number of days.
        :param days_old: Number of days to consider memories as old.
        :return: A dictionary with the result of the operation.
        """
        # Define the cutoff time
        cutoff = datetime.utcnow() - timedelta(days=days_old)
        
        # Build query filters
        filters = {"npc_id": self.npc_id}
        if self.character_id:
            filters["character_id"] = self.character_id
            
        # Query the short-term database
        results = self.short_term_db.get(where=filters)
        
        # Determine expired entries
        expired = []
        if results and "ids" in results and "metadatas" in results and "documents" in results:
            for doc_id, metadata, text in zip(results["ids"], results["metadatas"], results["documents"]):
                # Skip if timestamp is missing or invalid
                if "timestamp" not in metadata:
                    continue
                    
                try:
                    timestamp = parse_iso(metadata["timestamp"])
                except (ValueError, TypeError):
                    continue
                    
                # Check if the memory is old enough to expire
                if timestamp < cutoff:
                    expired.append((doc_id, text))
                    
        # If no expired entries, return early
        if not expired:
            return {"message": "No expired entries.", "count": 0}
            
        # Generate a summary of the expired entries
        summary = " ".join(text for _, text in expired)
        
        # Store the summary in the persistence layer
        try:
            from firebase_admin import db
            mem_ref = db.reference(f"/npc_memory/{self.npc_id.lower()}")
            existing = mem_ref.get() or {}
            combined = (existing.get("summary", "") + "\n" + summary).strip()
            mem_ref.update({"summary": combined})
        except Exception as e:
            logger.error(f"Error saving summary to persistence layer: {e}")
            
        # Delete the expired entries from the short-term database
        doc_ids = [doc_id for doc_id, _ in expired]
        self.short_term_db.delete(ids=doc_ids)
        
        logger.info(f"Cleaned {len(expired)} expired entries for NPC {self.npc_id}")
        return {
            "message": f"Cleaned {len(expired)} entries.",
            "count": len(expired),
            "summary": summary[:200] + "..." if len(summary) > 200 else summary
        }

    def get_recent_interactions(self, limit: int = 5) -> List[str]:
        """
        Get recent interactions from the short-term database.
        :param limit: The maximum number of interactions to return.
        :return: A list of interaction texts.
        """
        query_params = {
            "query_texts": ["recent conversation"],
            "n_results": limit,
            "where": {"npc_id": self.npc_id}
        }
        
        if self.character_id:
            query_params["where"]["character_id"] = self.character_id
            
        results = self.short_term_db.query(**query_params)
        
        # Extract and return the documents
        if not results or not results.get("documents") or not results["documents"][0]:
            return []
            
        return results["documents"][0]

    def get_available_summarization_styles(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get a list of all available summarization styles and detail levels.
        
        Returns:
            Dictionary with "styles" and "detail_levels" lists
        """
        return {
            "styles": SummarizationConfig.get_all_styles(),
            "detail_levels": SummarizationConfig.get_all_detail_levels()
        }

    def retrieve_memories_by_emotion(self, 
                               emotion: str, 
                               min_intensity: float = 0.3,
                               limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieve memories associated with a specific emotion.
        
        Args:
            emotion: The emotion to filter by (e.g., 'joy', 'fear')
            min_intensity: Minimum emotional intensity threshold (0.0-1.0)
            limit: Maximum number of memories to return
            
        Returns:
            List of memories with this emotional association
        """
        # Query the vector database for memories with emotional metadata
        results = []
        
        try:
            filter_condition = {
                "metadata.emotions": {
                    "$elemMatch": {
                        "name": emotion,
                        "intensity": {"$gte": min_intensity}
                    }
                }
            }
            
            # Execute search
            results = self.long_term_db.query(
                filter=filter_condition,
                limit=limit
            )
            
            # Convert results to memory objects
            return [self._doc_to_memory(doc) for doc in results]
        except Exception as e:
            logging.error(f"Error retrieving memories by emotion: {str(e)}")
            return []
    
    def retrieve_memories_by_cognitive_frame(self, 
                                   frame: str,
                                   limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieve memories associated with a specific cognitive frame.
        
        Args:
            frame: The cognitive frame to filter by (e.g., 'hero', 'victim')
            limit: Maximum number of memories to return
            
        Returns:
            List of memories with this cognitive frame
        """
        # Import the cognitive frame module
        from .cognitive_frames import CognitiveFrame
        
        try:
            # Convert string to enum value
            frame_enum = CognitiveFrame(frame.lower())
        except ValueError:
            raise ValueError(f"Invalid cognitive frame: {frame}")
            
        # Query the vector database for memories with this frame
        results = []
        
        try:
            filter_condition = {
                "metadata.cognitive_frames": {"$contains": frame}
            }
            
            docs = self.long_term_db.query(
                query_texts=[""], 
                n_results=limit,
                where=filter_condition
            )
            
            # Convert documents to memory objects
            for doc in docs:
                memory = self._doc_to_memory(doc)
                if memory:
                    results.append(memory)
                    
            return results
        except Exception as e:
            print(f"Error retrieving memories by cognitive frame: {e}")
            return []
            
    def retrieve_memories_with_complex_query(self,
                                           query: dict,
                                           limit: int = 10) -> List[Dict[str, Any]]:
        """
        Perform a complex memory retrieval with multiple filter criteria.
        
        Args:
            query: Dictionary containing filter criteria with these optional keys:
                - emotions: List of emotion filters, each with name and min_intensity
                - categories: List of memory categories to include
                - timeframe: Dict with start_date and end_date
                - importance: Minimum importance score
                - cognitive_frames: List of cognitive frames to filter by
            limit: Maximum number of memories to return
            
        Returns:
            List of memories matching the complex query
        """
        filter_conditions = {}
        
        # Add emotion filters if present
        if "emotions" in query and query["emotions"]:
            emotion_filters = []
            for emotion in query["emotions"]:
                emotion_filters.append({
                    "name": emotion["name"],
                    "intensity": {"$gte": emotion.get("min_intensity", 0.3)}
                })
            
            filter_conditions["metadata.emotions"] = {
                "$elemMatch": {"$or": emotion_filters}
            }
        
        # Add category filters if present
        if "categories" in query and query["categories"]:
            filter_conditions["metadata.categories"] = {
                "$in": query["categories"]
            }
        
        # Add timeframe filters if present
        if "timeframe" in query and query["timeframe"]:
            timeframe = query["timeframe"]
            if "start_date" in timeframe:
                filter_conditions["metadata.created_at"] = {
                    "$gte": timeframe["start_date"]
                }
            if "end_date" in timeframe:
                if "metadata.created_at" in filter_conditions:
                    filter_conditions["metadata.created_at"]["$lte"] = timeframe["end_date"]
                else:
                    filter_conditions["metadata.created_at"] = {
                        "$lte": timeframe["end_date"]
                    }
        
        # Add importance filter if present
        if "importance" in query and query["importance"]:
            filter_conditions["metadata.importance"] = {
                "$gte": query["importance"]
            }
        
        # Add cognitive frame filters if present
        if "cognitive_frames" in query and query["cognitive_frames"]:
            frame_filters = []
            for frame in query["cognitive_frames"]:
                frame_filters.append({"name": frame})
            
            filter_conditions["metadata.cognitive_frames"] = {
                "$elemMatch": {"$or": frame_filters}
            }
        
        try:
            # Execute the query with all filters
            results = self.long_term_db.query(
                filter=filter_conditions,
                limit=limit
            )
            
            # Convert results to memory objects
            return [self._doc_to_memory(doc) for doc in results]
        except Exception as e:
            logging.error(f"Error performing complex memory query: {str(e)}")
            return []

    def _doc_to_memory(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert a document from the vector database to a memory object.
        
        Args:
            doc: The document retrieved from the vector database
            
        Returns:
            A memory object with standardized structure
        """
        if not doc:
            return None
            
        # Extract metadata from the document
        metadata = doc.get("metadata", {})
        
        # Create a standardized memory object
        memory = {
            "id": doc.get("id") or str(uuid.uuid4()),
            "content": doc.get("text", ""),
            "summary": metadata.get("summary", ""),
            "created_at": metadata.get("created_at", datetime.now().isoformat()),
            "importance": metadata.get("importance", 0.5),
            "last_accessed": metadata.get("last_accessed", datetime.now().isoformat()),
            "categories": metadata.get("categories", []),
            "emotions": metadata.get("emotions", []),
            "cognitive_frames": metadata.get("cognitive_frames", []),
            "is_core_memory": metadata.get("is_core_memory", False),
            "associations": metadata.get("associations", []),
            "decay_rate": metadata.get("decay_rate", 0.1),
            "memory_strength": metadata.get("memory_strength", 1.0)
        }
        
        return memory

    def consolidate_memories(
        self,
        memory_ids: List[str],
        consolidation_type: str = "default"
    ) -> Dict[str, Any]:
        """
        Consolidate a group of related memories into a higher-level memory.
        
        Args:
            memory_ids: List of memory IDs to consolidate
            consolidation_type: Type of consolidation to perform
            
        Returns:
            The newly created consolidated memory
        """
        if not memory_ids or len(memory_ids) < 2:
            raise ValueError("At least two memories are required for consolidation")
            
        # Retrieve the memories to consolidate
        memories = []
        for mem_id in memory_ids:
            memory = self.retrieve_memory_by_id(mem_id)
            if not memory:
                raise ValueError(f"Memory with ID {mem_id} not found")
            memories.append(memory)
            
        # Prepare memory content for consolidation
        memory_texts = []
        for i, memory in enumerate(memories):
            content = memory.get("content", "")
            summary = memory.get("summary", "")
            when = memory.get("created_at", "")
            memory_texts.append(f"Memory {i+1} ({when}): {content}")
            
        combined_text = "\n\n".join(memory_texts)
        
        # Generate the consolidated memory
        consolidated_content = self._generate_consolidated_memory(
            combined_text, 
            consolidation_type
        )
        
        # Create a new memory object
        memory_id = str(uuid.uuid4())
        consolidated_memory = {
            "id": memory_id,
            "content": consolidated_content,
            "summary": f"Consolidated memory from {len(memories)} related memories",
            "created_at": datetime.now().isoformat(),
            "is_consolidated": True,
            "source_memory_ids": memory_ids,
            "consolidation_type": consolidation_type
        }
        
        # Create associations between the consolidated memory and source memories
        for mem_id in memory_ids:
            self.create_memory_association(
                source_memory_id=memory_id,
                target_memory_id=mem_id,
                association_type="contains",
                bidirectional=True
            )
            
        # Store the consolidated memory in the long-term database
        self._store_memory_in_long_term(consolidated_memory)
        
        return consolidated_memory
        
    def _generate_consolidated_memory(
        self, 
        combined_text: str,
        consolidation_type: str
    ) -> str:
        """
        Generate a consolidated memory from combined memory texts.
        
        Args:
            combined_text: Combined memory texts
            consolidation_type: Type of consolidation to perform
            
        Returns:
            Consolidated memory content
        """
        import openai
        
        # Define prompts for different consolidation types
        prompts = {
            "default": "Synthesize these memories into a single cohesive memory, maintaining the most important details.",
            "narrative": "Create a narrative that connects these memories into a meaningful story.",
            "causal": "Create a memory that explains the causal relationships between these events.",
            "emotional": "Create a memory that captures the emotional significance of these related events.",
            "thematic": "Identify and emphasize the common themes across these memories."
        }
        
        # Use default prompt if the consolidation type is not recognized
        prompt = prompts.get(consolidation_type, prompts["default"])
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": f"You are creating a consolidated memory from related memories. {prompt}"},
                    {"role": "user", "content": combined_text}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error generating consolidated memory: {e}")
            return f"Consolidated memory of events: {combined_text[:200]}..."

    def retrieve_memory_by_id(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific memory by its ID.
        
        Args:
            memory_id: The ID of the memory to retrieve
            
        Returns:
            The memory object or None if not found
        """
        try:
            # Query the database for this specific memory ID
            results = self.long_term_db.query(
                filter={"id": memory_id},
                limit=1
            )
            
            if not results:
                return None
                
            # Convert to memory object
            return self._doc_to_memory(results[0])
        except Exception as e:
            logging.error(f"Error retrieving memory by ID: {str(e)}")
            return None
    
    def create_memory_association(
        self,
        source_memory_id: str,
        target_memory_id: str,
        association_type: str,
        strength: float = 1.0,
        bidirectional: bool = True,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create an association between two memories.
        
        Args:
            source_memory_id: ID of the source memory
            target_memory_id: ID of the target memory
            association_type: Type of association (from MemoryAssociationType)
            strength: Association strength (0.0-1.0)
            bidirectional: Whether to create the inverse association
            metadata: Optional additional metadata
            
        Returns:
            Dictionary with association information
        """
        # Import the association type enum
        from .memory_associations import MemoryAssociationType
        
        try:
            # Convert string to enum value
            association_type_enum = MemoryAssociationType(association_type.lower())
        except ValueError:
            raise ValueError(f"Invalid association type: {association_type}")
        
        # Create the association
        primary, inverse = self.association_manager.add_association(
            source_id=source_memory_id,
            target_id=target_memory_id,
            association_type=association_type_enum,
            strength=strength,
            bidirectional=bidirectional,
            metadata=metadata
        )
        
        # Return information about the created association(s)
        result = {
            "primary": primary.to_dict(),
            "inverse": inverse.to_dict() if inverse else None,
            "success": True
        }
        
        return result
    
    def get_memory_associations(
        self,
        memory_id: str,
        association_types: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all associations for a memory.
        
        Args:
            memory_id: ID of the memory
            association_types: Optional list of association types to filter by
            
        Returns:
            List of association dictionaries
        """
        # Convert string association types to enum values if specified
        from .memory_associations import MemoryAssociationType
        
        enum_types = None
        if association_types:
            enum_types = []
            for type_str in association_types:
                try:
                    enum_types.append(MemoryAssociationType(type_str.lower()))
                except ValueError:
                    print(f"Warning: Invalid association type: {type_str}")
        
        # Get the associations
        associations = self.association_manager.get_associations(memory_id, enum_types)
        
        # Convert to dictionary representation
        return [assoc.to_dict() for assoc in associations]
    
    def detect_memory_associations(
        self,
        memory_a_id: str,
        memory_b_id: str
    ) -> List[Dict[str, Any]]:
        """
        Detect and create associations between two memories.
        
        Args:
            memory_a_id: ID of the first memory
            memory_b_id: ID of the second memory
            
        Returns:
            List of created association dictionaries
        """
        # Retrieve the memories
        memory_a = self.retrieve_memory_by_id(memory_a_id)
        memory_b = self.retrieve_memory_by_id(memory_b_id)
        
        if not memory_a or not memory_b:
            raise ValueError("One or both memories not found")
        
        # Import association utilities
        from .memory_associations import detect_memory_associations
        
        # Detect associations based on content
        memory_a_content = memory_a.get("content", "")
        memory_b_content = memory_b.get("content", "")
        
        detected_types = detect_memory_associations(memory_a_content, memory_b_content)
        
        # Create the detected associations
        created_associations = []
        for assoc_type in detected_types:
            result = self.create_memory_association(
                source_memory_id=memory_a_id,
                target_memory_id=memory_b_id,
                association_type=assoc_type.value,
                bidirectional=True
            )
            created_associations.append(result["primary"])
        
        return created_associations
    
    def get_memory_network(
        self,
        memory_id: str,
        max_depth: int = 2
    ) -> Dict[str, Any]:
        """
        Get a network of memories connected to the specified memory.
        
        Args:
            memory_id: ID of the central memory
            max_depth: Maximum traversal depth in the association graph
            
        Returns:
            Dictionary with nodes and edges representing the memory network
        """
        # Create sets to track visited memories and edges
        visited_memories = set()
        edges = []
        
        # Function to recursively explore the association graph
        def explore_associations(current_id, current_depth):
            if current_depth > max_depth or current_id in visited_memories:
                return
            
            visited_memories.add(current_id)
            
            # Get associations for the current memory
            associations = self.association_manager.get_associations(current_id)
            
            for assoc in associations:
                # Add edge to the result
                edge = {
                    "source": assoc.source_id,
                    "target": assoc.target_id,
                    "type": assoc.association_type.value,
                    "strength": assoc.strength
                }
                edges.append(edge)
                
                # Recursively explore connected memories
                if assoc.target_id not in visited_memories:
                    explore_associations(assoc.target_id, current_depth + 1)
        
        # Start exploration from the specified memory
        explore_associations(memory_id, 0)
        
        # Retrieve memory content for all nodes
        nodes = []
        for mem_id in visited_memories:
            memory = self.retrieve_memory_by_id(mem_id)
            if memory:
                node = {
                    "id": mem_id,
                    "content": memory.get("content", ""),
                    "summary": memory.get("summary", ""),
                    "created_at": memory.get("created_at", "")
                }
                nodes.append(node)
        
        return {
            "nodes": nodes,
            "edges": edges,
            "central_memory_id": memory_id
        } 