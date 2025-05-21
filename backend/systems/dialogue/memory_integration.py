"""
Memory system integration for the dialogue system.

This module provides functionality for creating memories from dialogue content
and retrieving relevant memories to enhance dialogue context.
"""

from typing import Dict, Any, List, Optional, Set
import logging
from datetime import datetime

# Import memory system components
from backend.systems.memory.memory_manager import MemoryManager
from backend.systems.dialogue.utils import extract_key_info, KEYWORDS

# Configure logger
logger = logging.getLogger(__name__)


class DialogueMemoryIntegration:
    """
    Integration between dialogue and memory systems.
    
    Allows creating memories from dialogue interactions and enhancing
    dialogue context with relevant memories.
    """
    
    def __init__(self, memory_manager=None):
        """
        Initialize the dialogue memory integration.
        
        Args:
            memory_manager: Optional memory manager instance
        """
        self.memory_manager = memory_manager or MemoryManager.get_instance()
    
    def create_memory_from_dialogue(
        self,
        character_id: str,
        speaker_id: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a memory for a character based on a dialogue interaction.
        
        Args:
            character_id: ID of the character who will hold the memory
            speaker_id: ID of the character who spoke
            message: Content of the message
            metadata: Optional additional metadata (e.g., location, time)
            
        Returns:
            ID of the created memory
        """
        # Extract important information from the message
        # In a real implementation, this would use more sophisticated NLP techniques
        important = self._extract_important_info(message)
        
        if not important:
            logger.debug(f"No important information found in message: {message}")
            return None
        
        # Prepare memory data
        memory_data = {
            "character_id": character_id,
            "type": "dialogue",
            "importance": self._calculate_importance(message),
            "content": {
                "speaker_id": speaker_id,
                "message": message,
                "extracted_info": important,
                "metadata": metadata or {}
            },
            "timestamp": datetime.utcnow(),
            "source": "dialogue_system",
            "metadata": metadata or {}
        }
        
        # Create the memory
        memory_id = self.memory_manager.create_memory(memory_data)
        logger.debug(f"Created memory {memory_id} for character {character_id} from dialogue")
        
        return memory_id
    
    def add_memories_to_context(
        self,
        character_id: str,
        context: Dict[str, Any],
        limit: int = 5
    ) -> Dict[str, Any]:
        """
        Add relevant memories to dialogue context.
        
        Args:
            character_id: ID of the character whose memories to add
            context: The existing dialogue context
            limit: Maximum number of memories to add
            
        Returns:
            Updated context with memories added
        """
        # Create a copy of the context
        updated_context = dict(context)
        
        # Get relevant memories based on context
        # In a real implementation, this would use more sophisticated relevance matching
        query = self._build_memory_query(context)
        memories = self.memory_manager.get_memories(
            character_id=character_id,
            query=query,
            limit=limit
        )
        
        # Add memories to context
        if memories:
            if "memories" not in updated_context:
                updated_context["memories"] = []
                
            updated_context["memories"].extend(memories)
            logger.debug(f"Added {len(memories)} memories to context for character {character_id}")
        
        return updated_context
    
    def add_specific_character_memories(
        self,
        character_id: str,
        about_character_id: str,
        context: Dict[str, Any],
        limit: int = 3
    ) -> Dict[str, Any]:
        """
        Add memories specifically about another character.
        
        Args:
            character_id: ID of the character whose memories to add
            about_character_id: ID of the character the memories should be about
            context: The existing dialogue context
            limit: Maximum number of memories to add
            
        Returns:
            Updated context with specific memories added
        """
        # Create a copy of the context
        updated_context = dict(context)
        
        # Get memories about the specific character
        memories = self.memory_manager.get_memories_about_character(
            character_id=character_id,
            about_character_id=about_character_id,
            limit=limit
        )
        
        # Add memories to context
        if memories:
            if "character_memories" not in updated_context:
                updated_context["character_memories"] = {}
                
            if about_character_id not in updated_context["character_memories"]:
                updated_context["character_memories"][about_character_id] = []
                
            updated_context["character_memories"][about_character_id].extend(memories)
            logger.debug(f"Added {len(memories)} memories about character {about_character_id}")
        
        return updated_context
    
    def _extract_important_info(self, message: str) -> Dict[str, Any]:
        """
        Extract important information from a dialogue message.
        
        Args:
            message: Content of the message
            
        Returns:
            Dictionary with extracted important information
        """
        # In a real implementation, this would use more sophisticated NLP techniques
        # For now, we'll use a simple keyword-based approach
        important = {}
        
        # Check for locations
        location_keywords = ["at", "in", "near", "by", "around"]
        for keyword in location_keywords:
            if keyword in message.lower():
                # Find the word after the location keyword
                parts = message.lower().split(keyword + " ")
                if len(parts) > 1 and parts[1]:
                    first_word = parts[1].split()[0]
                    if first_word and len(first_word) > 3:  # Avoid short words
                        important["location"] = first_word
                        break
        
        # Check for time references
        time_keywords = ["yesterday", "today", "tomorrow", "last", "next", "morning", "evening", "night"]
        for keyword in time_keywords:
            if keyword in message.lower():
                important["time"] = keyword
                break
        
        # Check for quest references
        quest_keywords = ["quest", "task", "mission", "job", "favor", "help"]
        for keyword in quest_keywords:
            if keyword in message.lower():
                important["quest"] = True
                break
        
        # Check for item references
        item_keywords = ["sword", "shield", "potion", "book", "scroll", "map", "key", "ring", "amulet"]
        for keyword in item_keywords:
            if keyword in message.lower():
                important["item"] = keyword
                break
        
        return important
    
    def _calculate_importance(self, message: str) -> float:
        """
        Calculate the importance score of a message for memory creation.
        
        Args:
            message: Content of the message
            
        Returns:
            Importance score between 0.0 and 1.0
        """
        # In a real implementation, this would use more sophisticated NLP techniques
        # For now, we'll use a simple length-based approach with keyword boosting
        
        # Base importance on length (longer messages are usually more important)
        base_importance = min(0.3 + (len(message) / 500), 0.7)
        
        # Boost importance based on keywords
        importance_keywords = ["important", "urgent", "critical", "remember", "forget", "never", "always"]
        keyword_boost = 0.0
        
        for keyword in importance_keywords:
            if keyword in message.lower():
                keyword_boost += 0.1
        
        # Cap at 1.0
        return min(base_importance + keyword_boost, 1.0)
    
    def _build_memory_query(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build a query for retrieving relevant memories based on dialogue context.
        
        Args:
            context: The dialogue context
            
        Returns:
            Query dictionary for memory retrieval
        """
        query = {}
        
        # Add location to query if available
        if "location_id" in context:
            query["location_id"] = context["location_id"]
        
        # Add recency preference
        query["recency_weight"] = 0.6
        
        # Add importance preference
        query["importance_weight"] = 0.4
        
        # Add topic from recent messages if available
        if "recent_messages" in context and context["recent_messages"]:
            recent_content = " ".join([m.get("content", "") for m in context["recent_messages"][-3:]])
            query["text_query"] = recent_content
        
        return query
    
    def get_relevant_memories(self, character_id: str, context: Dict[str, Any], 
                            max_memories: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve memories relevant to the current dialogue context.
        
        Args:
            character_id: ID of the character whose memories to retrieve
            context: Current dialogue context
            max_memories: Maximum number of memories to retrieve
            
        Returns:
            List of relevant memories as dictionaries
        """
        # Extract keywords from context
        keywords = []
        
        # Extract from recent messages
        if 'recent_messages' in context:
            for msg in context['recent_messages']:
                for kw in KEYWORDS:
                    if kw in msg['message'].lower():
                        keywords.append(kw)
        
        # Extract from participants
        if 'participants' in context:
            for participant in context['participants']:
                keywords.append(participant)
                
        # Extract from location
        if 'location' in context:
            keywords.append(context['location'])
            
        # Extract from topics
        if 'topics' in context:
            keywords.extend(context['topics'])
            
        # Get unique keywords
        unique_keywords = list(set(keywords))
        
        try:
            # Query memories using keywords for relevance
            memories = self.memory_manager.get_memories_by_keywords(
                entity_id=character_id,
                keywords=unique_keywords,
                limit=max_memories
            )
            
            # Convert to dictionary format
            return [m.to_dict() for m in memories]
        except Exception as e:
            logger.error(f"Failed to retrieve memories for character {character_id}: {e}")
            return []
    
    def reinforce_memory(self, memory_id: str, reinforcement_value: float = 0.1):
        """
        Reinforce an existing memory based on dialogue reference.
        
        Args:
            memory_id: ID of the memory to reinforce
            reinforcement_value: Value to increase relevance by (0.0-1.0)
        """
        try:
            self.memory_manager.reinforce_memory(memory_id, reinforcement_value)
            logger.info(f"Reinforced memory {memory_id} with value {reinforcement_value}")
        except Exception as e:
            logger.error(f"Failed to reinforce memory {memory_id}: {e}")
    
    def _calculate_significance(self, message: str, extracted_info: List[Dict[str, Any]]) -> float:
        """
        Calculate the significance of a dialogue message for memory creation.
        
        Args:
            message: The dialogue message
            extracted_info: Extracted information from the message
            
        Returns:
            Significance score (0.0-1.0)
        """
        # Base significance
        significance = 0.3
        
        # More extracted info = more significant
        significance += min(0.3, len(extracted_info) * 0.1)
        
        # Presence of keywords increases significance
        for kw in KEYWORDS:
            if kw in message.lower():
                significance += 0.1
                
        # Longer messages might be more significant (up to a point)
        significance += min(0.2, len(message) / 500)
        
        # Cap at 1.0
        return min(1.0, significance)
    
    def _determine_memory_type(self, message: str, extracted_info: List[Dict[str, Any]]) -> str:
        """
        Determine the type of memory to create based on dialogue content.
        
        Args:
            message: The dialogue message
            extracted_info: Extracted information from the message
            
        Returns:
            Memory type string
        """
        # Default type
        memory_type = "conversation"
        
        # Check extracted info for type hints
        for info in extracted_info:
            if info['type'] == 'quest':
                return "quest"
            elif info['type'] == 'location':
                return "location"
            elif info['type'] == 'item':
                return "item"
                
        # Check message content for keywords
        if any(kw in message.lower() for kw in ['secret', 'confidential', 'private']):
            return "secret"
        elif any(kw in message.lower() for kw in ['quest', 'mission', 'task']):
            return "quest"
        elif any(kw in message.lower() for kw in ['danger', 'threat', 'warn']):
            return "warning"
            
        return memory_type 