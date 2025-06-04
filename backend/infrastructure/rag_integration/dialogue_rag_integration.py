"""
RAG (Retrieval-Augmented Generation) integration for the dialogue system.

This module provides functionality to enhance dialogue responses by retrieving 
relevant information from various knowledge sources and augmenting AI-generated 
responses with factual, contextual information.
"""

from typing import Dict, Any, List, Optional, Tuple, Union
import logging
import json
from datetime import datetime
import asyncio

# Vector database and embedding imports
try:
    import chromadb
    from chromadb.config import Settings
    HAS_CHROMADB = True
except ImportError:
    HAS_CHROMADB = False
    chromadb = None

try:
    from sentence_transformers import SentenceTransformer
    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False
    SentenceTransformer = None

# LLM integration
from backend.infrastructure.llm.services.llm_service import LLMService, get_llm_service

# Configure logger
logger = logging.getLogger(__name__)


class DialogueRAGIntegration:
    """
    RAG integration for dialogue system.
    
    Provides retrieval-augmented generation capabilities to enhance dialogue
    responses with relevant factual information from various knowledge sources.
    """
    
    def __init__(
        self,
        embedding_model_name: str = "all-MiniLM-L6-v2",
        vector_db_path: str = "./data/dialogue_knowledge",
        llm_manager: Optional[LLMService] = None,
        enable_fallback: bool = True
    ):
        """
        Initialize the RAG integration.
        
        Args:
            embedding_model_name: Name of the sentence transformer model
            vector_db_path: Path to the vector database
            llm_manager: Optional LLM manager instance
            enable_fallback: Whether to enable fallback when RAG is unavailable
        """
        self.embedding_model_name = embedding_model_name
        self.vector_db_path = vector_db_path
        self.llm_manager = llm_manager  # Will be set later via async initialization
        self.enable_fallback = enable_fallback
        
        # Initialize components
        self.embedding_model = None
        self.vector_db = None
        self.collection = None
        
        # Knowledge source configurations
        self.knowledge_sources = {
            "lore": {"collection": "lore_knowledge", "weight": 0.8},
            "characters": {"collection": "character_knowledge", "weight": 0.9},
            "locations": {"collection": "location_knowledge", "weight": 0.7},
            "factions": {"collection": "faction_knowledge", "weight": 0.6},
            "quests": {"collection": "quest_knowledge", "weight": 0.8},
            "items": {"collection": "item_knowledge", "weight": 0.5},
            "events": {"collection": "event_knowledge", "weight": 0.7}
        }
        
        # Initialize RAG system
        self._initialize_rag_system()
    
    async def async_init(self):
        """Async initialization for LLM service."""
        if not self.llm_manager:
            try:
                self.llm_manager = await get_llm_service()
            except Exception as e:
                logger.warning(f"Failed to initialize LLM service: {e}")
                self.llm_manager = None
    
    def _initialize_rag_system(self) -> bool:
        """
        Initialize the RAG system components.
        
        Returns:
            Whether initialization was successful
        """
        try:
            # Initialize embedding model
            if HAS_SENTENCE_TRANSFORMERS:
                self.embedding_model = SentenceTransformer(self.embedding_model_name)
                logger.info(f"Initialized embedding model: {self.embedding_model_name}")
            else:
                logger.warning("Sentence transformers not available, RAG functionality limited")
                return False
            
            # Initialize vector database
            if HAS_CHROMADB:
                self.vector_db = chromadb.PersistentClient(
                    path=self.vector_db_path,
                    settings=Settings(anonymized_telemetry=False)
                )
                logger.info(f"Initialized vector database at: {self.vector_db_path}")
                
                # Initialize collections for each knowledge source
                self._initialize_collections()
            else:
                logger.warning("ChromaDB not available, RAG functionality limited")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize RAG system: {e}")
            return False
    
    def _initialize_collections(self):
        """Initialize vector database collections for knowledge sources."""
        for source_name, config in self.knowledge_sources.items():
            try:
                collection_name = config["collection"]
                
                # Get or create collection
                self.vector_db.get_or_create_collection(
                    name=collection_name,
                    metadata={"source": source_name, "created_at": datetime.now().isoformat()}
                )
                
                logger.debug(f"Initialized collection: {collection_name}")
                
            except Exception as e:
                logger.error(f"Failed to initialize collection {config['collection']}: {e}")
    
    async def enhance_dialogue_response(
        self,
        base_response: str,
        dialogue_context: Dict[str, Any],
        character_id: str,
        max_retrieved_items: int = 5,
        relevance_threshold: float = 0.7
    ) -> Dict[str, Any]:
        """
        Enhance a dialogue response with RAG-retrieved information.
        
        Args:
            base_response: The original dialogue response
            dialogue_context: Current dialogue context
            character_id: ID of the responding character
            max_retrieved_items: Maximum number of items to retrieve
            relevance_threshold: Minimum relevance score for retrieved items
            
        Returns:
            Enhanced response with RAG information
        """
        try:
            if not self._is_rag_available():
                return {
                    "enhanced_response": base_response,
                    "retrieval_used": False,
                    "retrieved_sources": [],
                    "enhancement_confidence": 0.0
                }
            
            # Extract query from context and response
            query = self._build_retrieval_query(base_response, dialogue_context)
            
            # Retrieve relevant information
            retrieved_info = self.retrieve_relevant_information(
                query=query,
                context=dialogue_context,
                max_items=max_retrieved_items,
                threshold=relevance_threshold
            )
            
            if not retrieved_info["items"]:
                return {
                    "enhanced_response": base_response,
                    "retrieval_used": False,
                    "retrieved_sources": [],
                    "enhancement_confidence": 0.0
                }
            
            # Enhance response with retrieved information
            enhancement_result = await self._enhance_response_with_retrieval(
                base_response=base_response,
                retrieved_info=retrieved_info,
                character_id=character_id,
                dialogue_context=dialogue_context
            )
            
            return {
                "enhanced_response": enhancement_result["enhanced_response"],
                "retrieval_used": True,
                "retrieved_sources": retrieved_info["items"],
                "enhancement_confidence": enhancement_result["confidence"],
                "enhancement_reasoning": enhancement_result.get("reasoning", "")
            }
            
        except Exception as e:
            logger.error(f"Error enhancing dialogue response: {e}")
            return {
                "enhanced_response": base_response,
                "retrieval_used": False,
                "retrieved_sources": [],
                "enhancement_confidence": 0.0,
                "error": str(e)
            }
    
    def retrieve_relevant_information(
        self,
        query: str,
        context: Dict[str, Any],
        max_items: int = 5,
        threshold: float = 0.7,
        source_filter: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Retrieve relevant information from knowledge sources.
        
        Args:
            query: Search query
            context: Dialogue context for filtering
            max_items: Maximum items to retrieve
            threshold: Relevance threshold
            source_filter: Optional list of knowledge sources to search
            
        Returns:
            Retrieved information with relevance scores
        """
        try:
            if not self._is_rag_available():
                return {"items": [], "total_searched": 0}
            
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query).tolist()
            
            # Determine which sources to search
            sources_to_search = source_filter or list(self.knowledge_sources.keys())
            
            retrieved_items = []
            total_searched = 0
            
            # Search each knowledge source
            for source_name in sources_to_search:
                if source_name not in self.knowledge_sources:
                    continue
                
                source_config = self.knowledge_sources[source_name]
                collection_name = source_config["collection"]
                source_weight = source_config["weight"]
                
                try:
                    collection = self.vector_db.get_collection(collection_name)
                    
                    # Perform similarity search
                    results = collection.query(
                        query_embeddings=[query_embedding],
                        n_results=max_items,
                        include=["documents", "metadatas", "distances"]
                    )
                    
                    # Process results
                    if results["documents"] and results["documents"][0]:
                        for i, (doc, metadata, distance) in enumerate(zip(
                            results["documents"][0],
                            results["metadatas"][0], 
                            results["distances"][0]
                        )):
                            # Convert distance to similarity score
                            similarity = 1.0 - distance
                            weighted_score = similarity * source_weight
                            
                            if weighted_score >= threshold:
                                retrieved_items.append({
                                    "content": doc,
                                    "metadata": metadata,
                                    "source": source_name,
                                    "relevance_score": weighted_score,
                                    "raw_similarity": similarity
                                })
                            
                            total_searched += 1
                    
                except Exception as e:
                    logger.error(f"Error searching collection {collection_name}: {e}")
                    continue
            
            # Sort by relevance score and limit results
            retrieved_items.sort(key=lambda x: x["relevance_score"], reverse=True)
            retrieved_items = retrieved_items[:max_items]
            
            return {
                "items": retrieved_items,
                "total_searched": total_searched,
                "query": query,
                "threshold_used": threshold
            }
            
        except Exception as e:
            logger.error(f"Error retrieving information: {e}")
            return {"items": [], "total_searched": 0, "error": str(e)}
    
    def add_knowledge_to_rag(
        self,
        content: str,
        source_type: str,
        metadata: Dict[str, Any],
        doc_id: Optional[str] = None
    ) -> bool:
        """
        Add new knowledge content to the RAG system.
        
        Args:
            content: The text content to add
            source_type: Type of knowledge source
            metadata: Additional metadata for the content
            doc_id: Optional document ID
            
        Returns:
            Whether addition was successful
        """
        try:
            if not self._is_rag_available():
                logger.warning("RAG system not available for adding knowledge")
                return False
            
            if source_type not in self.knowledge_sources:
                logger.error(f"Unknown knowledge source type: {source_type}")
                return False
            
            collection_name = self.knowledge_sources[source_type]["collection"]
            collection = self.vector_db.get_collection(collection_name)
            
            # Generate embedding for content
            content_embedding = self.embedding_model.encode(content).tolist()
            
            # Prepare metadata
            enhanced_metadata = {
                **metadata,
                "source_type": source_type,
                "added_at": datetime.now().isoformat(),
                "content_length": len(content)
            }
            
            # Generate ID if not provided
            if not doc_id:
                doc_id = f"{source_type}_{datetime.now().timestamp()}"
            
            # Add to collection
            collection.add(
                documents=[content],
                metadatas=[enhanced_metadata],
                embeddings=[content_embedding],
                ids=[doc_id]
            )
            
            logger.info(f"Added knowledge to {collection_name}: {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding knowledge to RAG: {e}")
            return False
    
    def update_character_knowledge(
        self,
        character_id: str,
        knowledge_updates: List[Dict[str, Any]]
    ) -> bool:
        """
        Update character-specific knowledge in the RAG system.
        
        Args:
            character_id: ID of the character
            knowledge_updates: List of knowledge updates
            
        Returns:
            Whether update was successful
        """
        try:
            success_count = 0
            
            for update in knowledge_updates:
                content = update.get("content", "")
                knowledge_type = update.get("type", "general")
                
                metadata = {
                    "character_id": character_id,
                    "knowledge_type": knowledge_type,
                    "source": update.get("source", "dialogue_interaction"),
                    **update.get("metadata", {})
                }
                
                doc_id = f"char_{character_id}_{knowledge_type}_{datetime.now().timestamp()}"
                
                if self.add_knowledge_to_rag(content, "characters", metadata, doc_id):
                    success_count += 1
            
            logger.info(f"Updated {success_count}/{len(knowledge_updates)} character knowledge items")
            return success_count == len(knowledge_updates)
            
        except Exception as e:
            logger.error(f"Error updating character knowledge: {e}")
            return False
    
    def get_contextual_knowledge_suggestions(
        self,
        dialogue_context: Dict[str, Any],
        character_id: str,
        max_suggestions: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Get knowledge-based suggestions for dialogue responses.
        
        Args:
            dialogue_context: Current dialogue context
            character_id: ID of the character
            max_suggestions: Maximum number of suggestions
            
        Returns:
            List of knowledge-based dialogue suggestions
        """
        try:
            if not self._is_rag_available():
                return []
            
            # Build context-aware query
            context_query = self._build_context_query(dialogue_context, character_id)
            
            # Retrieve relevant knowledge
            retrieved_info = self.retrieve_relevant_information(
                query=context_query,
                context=dialogue_context,
                max_items=max_suggestions * 2,  # Get more to filter from
                threshold=0.6  # Lower threshold for suggestions
            )
            
            suggestions = []
            
            for item in retrieved_info["items"][:max_suggestions]:
                suggestion = self._generate_dialogue_suggestion(item, dialogue_context)
                if suggestion:
                    suggestions.append(suggestion)
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error getting contextual knowledge suggestions: {e}")
            return []
    
    def _is_rag_available(self) -> bool:
        """Check if RAG system is available and functional."""
        return (
            self.embedding_model is not None and 
            self.vector_db is not None and
            HAS_CHROMADB and 
            HAS_SENTENCE_TRANSFORMERS
        )
    
    def _build_retrieval_query(self, response: str, context: Dict[str, Any]) -> str:
        """Build a search query from response and context."""
        query_parts = []
        
        # Add key terms from response
        query_parts.append(response)
        
        # Add context information
        if context.get("current_topic"):
            query_parts.append(context["current_topic"])
        
        if context.get("location_id"):
            query_parts.append(f"location:{context['location_id']}")
        
        if context.get("participant_ids"):
            for participant_id in context["participant_ids"]:
                query_parts.append(f"character:{participant_id}")
        
        return " ".join(query_parts)
    
    def _build_context_query(self, context: Dict[str, Any], character_id: str) -> str:
        """Build a context-aware query for knowledge suggestions."""
        query_parts = []
        
        # Add character information
        query_parts.append(f"character:{character_id}")
        
        # Add conversation context
        if context.get("conversation_history"):
            # Extract key topics from recent messages
            recent_messages = context["conversation_history"][-3:]  # Last 3 messages
            for message in recent_messages:
                if isinstance(message, dict) and message.get("content"):
                    # Add key nouns/topics (simplified extraction)
                    query_parts.append(message["content"])
        
        # Add location context
        if context.get("location_id"):
            query_parts.append(f"location:{context['location_id']}")
        
        # Add faction context
        if context.get("faction_context", {}).get("character_faction"):
            faction = context["faction_context"]["character_faction"]
            query_parts.append(f"faction:{faction['name']}")
        
        return " ".join(query_parts)
    
    async def _enhance_response_with_retrieval(
        self,
        base_response: str,
        retrieved_info: Dict[str, Any],
        character_id: str,
        dialogue_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Enhance response using retrieved information."""
        try:
            # Prepare enhancement prompt
            enhancement_prompt = self._build_enhancement_prompt(
                base_response, retrieved_info, character_id, dialogue_context
            )
            
            # Use LLM to enhance response
            if self.llm_manager:
                enhanced_response_data = await self.llm_manager.generate_content(
                    prompt=enhancement_prompt,
                    max_tokens=500,
                    temperature=0.7
                )
                enhanced_response = enhanced_response_data.get("response", base_response)
            else:
                enhanced_response = base_response
            
            # Calculate confidence based on retrieval quality
            confidence = self._calculate_enhancement_confidence(retrieved_info)
            
            return {
                "enhanced_response": enhanced_response,
                "confidence": confidence,
                "reasoning": "Enhanced with retrieved knowledge from game lore and context"
            }
            
        except Exception as e:
            logger.error(f"Error enhancing response with retrieval: {e}")
            return {
                "enhanced_response": base_response,
                "confidence": 0.0,
                "reasoning": f"Enhancement failed: {e}"
            }
    
    def _build_enhancement_prompt(
        self,
        base_response: str,
        retrieved_info: Dict[str, Any],
        character_id: str,
        dialogue_context: Dict[str, Any]
    ) -> str:
        """Build prompt for LLM enhancement."""
        prompt_parts = [
            "Enhance the following dialogue response with relevant retrieved information.",
            "Keep the character's voice and personality consistent.",
            "Only add information that naturally fits the conversation context.",
            "",
            f"Character ID: {character_id}",
            f"Original Response: {base_response}",
            "",
            "Retrieved Information:"
        ]
        
        for i, item in enumerate(retrieved_info["items"][:3]):  # Use top 3 items
            prompt_parts.append(f"{i+1}. {item['content']} (Source: {item['source']}, Relevance: {item['relevance_score']:.2f})")
        
        prompt_parts.extend([
            "",
            "Enhanced Response:"
        ])
        
        return "\n".join(prompt_parts)
    
    def _calculate_enhancement_confidence(self, retrieved_info: Dict[str, Any]) -> float:
        """Calculate confidence score for enhancement."""
        if not retrieved_info["items"]:
            return 0.0
        
        # Average relevance score of retrieved items
        avg_relevance = sum(item["relevance_score"] for item in retrieved_info["items"]) / len(retrieved_info["items"])
        
        # Factor in number of retrieved items (more is better, up to a point)
        item_count_factor = min(len(retrieved_info["items"]) / 3.0, 1.0)
        
        return avg_relevance * item_count_factor
    
    def _generate_dialogue_suggestion(
        self,
        knowledge_item: Dict[str, Any],
        dialogue_context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Generate a dialogue suggestion from a knowledge item."""
        try:
            content = knowledge_item["content"]
            source = knowledge_item["source"]
            relevance = knowledge_item["relevance_score"]
            
            # Simple suggestion generation (could be enhanced with LLM)
            suggestion_text = f"Based on {source} knowledge: {content[:100]}..."
            
            return {
                "suggestion": suggestion_text,
                "source": source,
                "relevance": relevance,
                "full_content": content,
                "metadata": knowledge_item["metadata"]
            }
            
        except Exception as e:
            logger.error(f"Error generating dialogue suggestion: {e}")
            return None
    
    def get_rag_system_status(self) -> Dict[str, Any]:
        """Get status information about the RAG system."""
        status = {
            "available": self._is_rag_available(),
            "embedding_model": self.embedding_model_name if self.embedding_model else None,
            "vector_db_path": self.vector_db_path,
            "knowledge_sources": {}
        }
        
        if self._is_rag_available():
            # Get collection statistics
            for source_name, config in self.knowledge_sources.items():
                try:
                    collection = self.vector_db.get_collection(config["collection"])
                    count = collection.count()
                    status["knowledge_sources"][source_name] = {
                        "collection": config["collection"],
                        "document_count": count,
                        "weight": config["weight"]
                    }
                except Exception as e:
                    status["knowledge_sources"][source_name] = {
                        "collection": config["collection"],
                        "error": str(e)
                    }
        
        return status


# Utility functions for RAG integration

async def initialize_dialogue_rag() -> DialogueRAGIntegration:
    """Initialize and return a dialogue RAG integration instance."""
    try:
        rag_integration = DialogueRAGIntegration()
        await rag_integration.async_init()  # Initialize LLM service
        logger.info("Dialogue RAG integration initialized successfully")
        return rag_integration
    except Exception as e:
        logger.error(f"Failed to initialize dialogue RAG integration: {e}")
        # Return a mock integration for fallback
        return DialogueRAGIntegration(enable_fallback=True)


def populate_initial_knowledge(rag_integration: DialogueRAGIntegration) -> bool:
    """Populate the RAG system with initial game knowledge."""
    try:
        # Sample initial knowledge - in practice this would come from game data
        initial_knowledge = [
            {
                "content": "The ancient ruins of Eldergloom hold mysterious artifacts from a forgotten civilization.",
                "source_type": "lore",
                "metadata": {"location": "eldergloom", "type": "ruins", "importance": "high"}
            },
            {
                "content": "Captain Marcus leads the city guard with honor and dedication to protecting citizens.",
                "source_type": "characters",
                "metadata": {"character_id": "captain_marcus", "role": "guard_captain", "faction": "city_guard"}
            },
            {
                "content": "The Merchant's Quarter bustles with trade activity from dawn until dusk.",
                "source_type": "locations",
                "metadata": {"location_id": "merchants_quarter", "type": "district", "activity_level": "high"}
            }
        ]
        
        success_count = 0
        for knowledge in initial_knowledge:
            if rag_integration.add_knowledge_to_rag(
                content=knowledge["content"],
                source_type=knowledge["source_type"],
                metadata=knowledge["metadata"]
            ):
                success_count += 1
        
        logger.info(f"Populated {success_count}/{len(initial_knowledge)} initial knowledge items")
        return success_count == len(initial_knowledge)
        
    except Exception as e:
        logger.error(f"Error populating initial knowledge: {e}")
        return False 