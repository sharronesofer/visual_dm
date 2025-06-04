"""
Dialogue Manager - Central orchestrator for all dialogue functionality.

This is the main entry point for dialogue operations, providing a clean interface
for conversation management, response generation, and system integration.
"""

import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import asyncio

from backend.systems.dialogue.dialogue_system_new import DialogueSystemNew, get_dialogue_system
from backend.infrastructure.dialogue_models.dialogue_models import (
    StartConversationRequest, SendMessageRequest, ConversationResponse,
    DialogueResponse, ConversationState
)

logger = logging.getLogger(__name__)


class DialogueManager:
    """
    Central manager for all dialogue operations.
    
    Provides simplified interface for:
    - Starting/ending conversations
    - Sending messages and generating responses
    - RAG-enhanced context retrieval
    - Integration with all game systems
    """
    
    def __init__(self):
        self.dialogue_system: Optional[DialogueSystemNew] = None
        self._rag_enabled = True
        self._cache_ttl = 300  # 5 minutes
        self._response_cache: Dict[str, Any] = {}
    
    async def initialize(self):
        """Initialize the dialogue manager and underlying systems."""
        self.dialogue_system = get_dialogue_system()
        logger.info("DialogueManager initialized with RAG support")
    
    async def start_conversation(
        self,
        player_id: str,
        npc_id: str,
        location_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Start a new conversation between player and NPC.
        
        Args:
            player_id: ID of the player
            npc_id: ID of the NPC
            location_id: Optional location where conversation occurs
            context: Optional initial context
            
        Returns:
            Conversation ID
        """
        if not self.dialogue_system:
            await self.initialize()
        
        participants = {
            player_id: "player",
            npc_id: "npc"
        }
        
        metadata = context or {}
        if location_id:
            metadata["location_id"] = location_id
        
        conversation_id = self.dialogue_system.start_conversation(
            participants=participants,
            location_id=location_id,
            metadata=metadata
        )
        
        logger.info(f"Started conversation {conversation_id} between {player_id} and {npc_id}")
        return conversation_id
    
    async def send_message(
        self,
        conversation_id: str,
        sender_id: str,
        content: str,
        message_type: str = "dialogue"
    ) -> Optional[Dict[str, Any]]:
        """
        Send a message in a conversation.
        
        Args:
            conversation_id: ID of the conversation
            sender_id: ID of the sender
            content: Message content
            message_type: Type of message
            
        Returns:
            Message data or None if failed
        """
        if not self.dialogue_system:
            await self.initialize()
        
        return self.dialogue_system.send_message(
            conversation_id=conversation_id,
            sender_id=sender_id,
            content=content,
            message_type=message_type
        )
    
    async def generate_response(
        self,
        conversation_id: str,
        responder_id: str,
        use_rag: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Generate an AI response with RAG enhancement.
        
        Args:
            conversation_id: ID of the conversation
            responder_id: ID of the character responding
            use_rag: Whether to use RAG for context enhancement
            
        Returns:
            Generated response data
        """
        if not self.dialogue_system:
            await self.initialize()
        
        # Generate response with RAG if enabled
        if use_rag and self._rag_enabled:
            return await self._generate_rag_enhanced_response(
                conversation_id, responder_id
            )
        else:
            return self.dialogue_system.generate_response(
                conversation_id=conversation_id,
                responder_id=responder_id
            )
    
    async def _generate_rag_enhanced_response(
        self,
        conversation_id: str,
        responder_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Generate response enhanced with RAG context retrieval.
        
        This is the core RAG implementation for dialogue.
        """
        try:
            # Get conversation context
            conversation = self.dialogue_system.conversations.get(conversation_id)
            if not conversation:
                logger.error(f"Conversation {conversation_id} not found")
                return None
            
            # Step 1: Extract query from recent conversation
            recent_messages = conversation.messages[-5:]  # Last 5 messages
            query_text = " ".join([msg.get("content", "") for msg in recent_messages])
            
            # Step 2: Retrieve relevant context using RAG
            rag_context = await self._retrieve_relevant_context(
                query_text, responder_id, conversation.location_id
            )
            
            # Step 3: Enhance conversation context with retrieved information
            enhanced_context = conversation.get_context()
            enhanced_context["rag_context"] = rag_context
            
            # Step 4: Generate response with enhanced context
            response = self.dialogue_system.generate_response(
                conversation_id=conversation_id,
                responder_id=responder_id,
                metadata={"enhanced_context": enhanced_context}
            )
            
            # Step 5: Store successful retrieval for future reference
            if response:
                response["rag_enhanced"] = True
                response["context_sources"] = rag_context.get("sources", [])
            
            return response
            
        except Exception as e:
            logger.error(f"RAG enhancement failed: {e}")
            # Fallback to standard response
            return self.dialogue_system.generate_response(
                conversation_id=conversation_id,
                responder_id=responder_id
            )
    
    async def _retrieve_relevant_context(
        self,
        query: str,
        character_id: str,
        location_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Core RAG retrieval function.
        
        Retrieves relevant information from multiple knowledge sources:
        - Character memories
        - Conversation history
        - World state
        - Faction information
        - Quest context
        """
        context = {
            "memories": [],
            "relationships": [],
            "world_events": [],
            "location_info": [],
            "quest_context": [],
            "sources": []
        }
        
        try:
            # Retrieve from memory system
            if self.dialogue_system.memory_integration:
                memories = await self._retrieve_memory_context(query, character_id)
                context["memories"] = memories
                if memories:
                    context["sources"].append("character_memories")
            
            # Retrieve relationship context
            if self.dialogue_system.relationship_integration:
                relationships = await self._retrieve_relationship_context(query, character_id)
                context["relationships"] = relationships
                if relationships:
                    context["sources"].append("character_relationships")
            
            # Retrieve world state context
            if self.dialogue_system.world_state_integration:
                world_events = await self._retrieve_world_context(query, location_id)
                context["world_events"] = world_events
                if world_events:
                    context["sources"].append("world_state")
            
            # Retrieve location context
            if location_id and self.dialogue_system.poi_integration:
                location_info = await self._retrieve_location_context(query, location_id)
                context["location_info"] = location_info
                if location_info:
                    context["sources"].append("location_data")
            
            # Retrieve quest context
            if self.dialogue_system.quest_integration:
                quest_context = await self._retrieve_quest_context(query, character_id)
                context["quest_context"] = quest_context
                if quest_context:
                    context["sources"].append("quest_system")
            
        except Exception as e:
            logger.error(f"Error during context retrieval: {e}")
        
        return context
    
    async def _retrieve_memory_context(self, query: str, character_id: str) -> List[Dict[str, Any]]:
        """Retrieve relevant memories using semantic search."""
        try:
            # Use memory integration to search for relevant memories
            relevant_memories = self.dialogue_system.memory_integration.get_relevant_context(
                user_id=character_id,
                current_message=query,
                max_context=3
            )
            return relevant_memories
        except Exception as e:
            logger.error(f"Memory retrieval failed: {e}")
            return []
    
    async def _retrieve_relationship_context(self, query: str, character_id: str) -> List[Dict[str, Any]]:
        """Retrieve relevant relationship information."""
        try:
            # Extract potential character mentions from query
            # This is simplified - in production you'd use NER
            words = query.lower().split()
            potential_characters = [word for word in words if len(word) > 3]
            
            relationships = []
            for mentioned_char in potential_characters[:2]:  # Limit to 2
                rel_info = self.dialogue_system.relationship_integration._get_relationship_info(
                    character_id, mentioned_char
                )
                if rel_info:
                    relationships.append(rel_info)
            
            return relationships
        except Exception as e:
            logger.error(f"Relationship retrieval failed: {e}")
            return []
    
    async def _retrieve_world_context(self, query: str, location_id: Optional[str]) -> List[Dict[str, Any]]:
        """Retrieve relevant world state information."""
        try:
            if not location_id:
                return []
            
            # Get world state context for the location
            world_context = self.dialogue_system.world_state_integration.add_character_world_state_knowledge(
                context={}, character_id="system"  # Using system to get general world state
            )
            
            # Filter relevant information based on query
            relevant_events = []
            query_words = set(query.lower().split())
            
            for event_key, event_data in world_context.items():
                if isinstance(event_data, str):
                    event_words = set(event_data.lower().split())
                    if len(query_words.intersection(event_words)) > 0:
                        relevant_events.append({
                            "type": event_key,
                            "content": event_data
                        })
            
            return relevant_events[:3]  # Limit to 3 most relevant
        except Exception as e:
            logger.error(f"World context retrieval failed: {e}")
            return []
    
    async def _retrieve_location_context(self, query: str, location_id: str) -> List[Dict[str, Any]]:
        """Retrieve relevant location information."""
        try:
            # Get POI context for the location
            location_context = self.dialogue_system.poi_integration.add_poi_context_to_dialogue(
                context={}, location_id=location_id
            )
            
            return [{"location_data": location_context}]
        except Exception as e:
            logger.error(f"Location context retrieval failed: {e}")
            return []
    
    async def _retrieve_quest_context(self, query: str, character_id: str) -> List[Dict[str, Any]]:
        """Retrieve relevant quest information."""
        try:
            # This would integrate with quest system
            # For now, return empty list since quest integration is a stub
            return []
        except Exception as e:
            logger.error(f"Quest context retrieval failed: {e}")
            return []
    
    async def end_conversation(self, conversation_id: str) -> bool:
        """End a conversation and clean up resources."""
        if not self.dialogue_system:
            await self.initialize()
        
        return self.dialogue_system.end_conversation(conversation_id)
    
    async def get_conversation_state(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Get current conversation state."""
        if not self.dialogue_system:
            await self.initialize()
        
        return self.dialogue_system.get_conversation_context(conversation_id)
    
    def enable_rag(self, enabled: bool = True):
        """Enable or disable RAG enhancement."""
        self._rag_enabled = enabled
        logger.info(f"RAG enhancement {'enabled' if enabled else 'disabled'}")
    
    def get_rag_status(self) -> Dict[str, Any]:
        """Get RAG system status."""
        return {
            "rag_enabled": self._rag_enabled,
            "cache_size": len(self._response_cache),
            "integrations_available": {
                "memory": self.dialogue_system.memory_integration is not None if self.dialogue_system else False,
                "relationships": self.dialogue_system.relationship_integration is not None if self.dialogue_system else False,
                "world_state": self.dialogue_system.world_state_integration is not None if self.dialogue_system else False,
                "poi": self.dialogue_system.poi_integration is not None if self.dialogue_system else False,
                "quest": self.dialogue_system.quest_integration is not None if self.dialogue_system else False,
            }
        }


# Global instance
_dialogue_manager = None

async def get_dialogue_manager() -> DialogueManager:
    """Get the global dialogue manager instance."""
    global _dialogue_manager
    if _dialogue_manager is None:
        _dialogue_manager = DialogueManager()
        await _dialogue_manager.initialize()
    return _dialogue_manager
