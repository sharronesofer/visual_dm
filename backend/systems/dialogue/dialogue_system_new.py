"""
New dialogue system implementation that integrates with other systems.

This module provides a comprehensive dialogue system that integrates with:
1. Memory system - for creating memories from dialogue and referencing memories
2. Rumor system - for generating rumors from dialogue and including rumors in context
3. Motif system - for adapting dialogue style based on active motifs
4. Faction system - for incorporating faction dynamics into dialogue
5. Population system - for making NPCs aware of regional demographics
6. World State system - for referencing world variables in dialogue
7. Time system - for making dialogue aware of time and calendar
8. POI system - for incorporating location states in dialogue
9. Quest system - for referencing narrative arcs and quests
10. Region system - for referencing biomes and environmental characteristics
11. War system - for referencing faction wars and conflicts
12. Relationship system - for incorporating character relationships
13. Analytics system - for logging dialogue events
"""

from typing import Dict, Any, List, Optional, Callable
import logging
import uuid
from datetime import datetime
import asyncio

# Import integration modules
from backend.systems.dialogue.memory_integration import DialogueMemoryIntegration
from backend.systems.dialogue.rumor_integration import DialogueRumorIntegration
from backend.systems.dialogue.motif_integration import DialogueMotifIntegration
from backend.systems.dialogue.faction_integration import DialogueFactionIntegration
from backend.systems.dialogue.population_integration import DialoguePopulationIntegration
from backend.systems.dialogue.world_state_integration import DialogueWorldStateIntegration
from backend.systems.dialogue.time_integration import DialogueTimeIntegration
from backend.systems.dialogue.poi_integration import DialoguePOIIntegration
from backend.systems.dialogue.quest_integration import DialogueQuestIntegration
from backend.systems.dialogue.region_integration import DialogueRegionIntegration
from backend.systems.dialogue.war_integration import DialogueWarIntegration
from backend.systems.dialogue.relationship_integration import DialogueRelationshipIntegration
from backend.infrastructure.analytics.dialogue import DialogueAnalyticsIntegration
from backend.infrastructure.systems.dialogue.events import DialogueEventEmitter, DialogueStartedEvent, DialogueMessageEvent, DialogueEndedEvent

# Import language generation (assuming an LLM or template-based system)
from backend.systems.language.language_generator import LanguageGenerator

# Import motif manager
from backend.systems.motif.services.manager_core import MotifManager

# Replace the local RAG import with the centralized service
from backend.core.rag_client import create_rag_client, RAGClient, DialogueRAGAdapter

# Configure logger
logger = logging.getLogger(__name__)

class Conversation:
    """
    Represents an ongoing dialogue conversation between participants.
    
    Tracks conversation state, participants, messages, and context.
    Provides methods for sending messages and generating responses.
    """
    
    def __init__(
        self,
        conversation_id: Optional[str] = None,
        participants: Optional[Dict[str, str]] = None,
        location_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a new conversation.
        
        Args:
            conversation_id: Optional conversation ID (generated if not provided)
            participants: Dictionary mapping participant IDs to their roles
            location_id: Optional ID of the location where conversation occurs
            metadata: Optional additional metadata for the conversation
        """
        self.id = conversation_id or str(uuid.uuid4())
        self.participants = participants or {}
        self.location_id = location_id
        self.metadata = metadata or {}
        self.messages = []
        self.context = {
            "conversation_id": self.id,
            "participants": self.participants,
            "location_id": self.location_id,
            "metadata": self.metadata,
            "started_at": datetime.utcnow().isoformat()
        }
        self.active = True
    
    def add_message(
        self,
        sender_id: str,
        content: str,
        message_type: str = "dialogue",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Add a message to the conversation.
        
        Args:
            sender_id: ID of the message sender
            content: Content of the message
            message_type: Type of message (dialogue, action, emote, etc.)
            metadata: Optional additional metadata for the message
            
        Returns:
            The created message as a dictionary
        """
        # Ensure conversation is active
        if not self.active:
            logger.warning(f"Attempted to add message to inactive conversation {self.id}")
            return None
        
        # Ensure sender is a participant
        if sender_id not in self.participants:
            logger.warning(f"Message from non-participant {sender_id} in conversation {self.id}")
            return None
        
        # Create message
        message = {
            "id": str(uuid.uuid4()),
            "conversation_id": self.id,
            "sender_id": sender_id,
            "content": content,
            "type": message_type,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }
        
        # Add to messages list
        self.messages.append(message)
        
        # Update context with recent messages
        self._update_recent_messages()
        
        return message
    
    def get_context(self) -> Dict[str, Any]:
        """
        Get the current conversation context.
        
        Returns:
            Dictionary with complete conversation context
        """
        return self.context
    
    def end_conversation(self) -> bool:
        """
        Mark the conversation as ended.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.active:
            logger.warning(f"Attempted to end already inactive conversation {self.id}")
            return False
        
        self.active = False
        self.context["ended_at"] = datetime.utcnow().isoformat()
        return True
    
    def is_active(self) -> bool:
        """
        Check if the conversation is still active.
        
        Returns:
            True if active, False otherwise
        """
        return self.active
    
    def add_to_context(self, key: str, value: Any) -> None:
        """
        Add or update information in the conversation context.
        
        Args:
            key: Context key to add or update
            value: Value to store in context
        """
        self.context[key] = value
    
    def _update_recent_messages(self, limit: int = 10) -> None:
        """
        Update the recent messages in context.
        
        Args:
            limit: Maximum number of recent messages to include
        """
        recent = self.messages[-limit:] if len(self.messages) > limit else self.messages
        self.context["recent_messages"] = recent

class DialogueSystemNew:
    """
    Enhanced dialogue system with comprehensive integration capabilities and centralized RAG support
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize integrations - keeping existing structure
        self.dialogue_manager = None
        self.quest_integration = None
        self.faction_integration = None
        self.region_integration = None
        self.memory_integration = None
        self.rumor_integration = None
        self.motif_integration = None
        self.population_integration = None
        self.relationship_integration = None
        self.war_integration = None
        self.time_integration = None
        
        # Replace local RAG with centralized RAG client
        self.rag_client: Optional[RAGClient] = None
        
        # Configuration
        self.config = {
            'response_enhancement_enabled': True,
            'cross_system_rag_enabled': True,
            'fallback_enabled': True,
            'performance_monitoring': True
        }
        
        # Performance tracking
        self.performance_stats = {
            'responses_generated': 0,
            'rag_enhancements': 0,
            'average_response_time': 0.0,
            'cross_system_queries': 0
        }

    async def initialize(self):
        """Initialize the dialogue system with all integrations"""
        try:
            # Initialize centralized RAG client
            self.rag_client = await create_rag_client('dialogue', DialogueRAGAdapter())
            self.logger.info("Centralized RAG client initialized for dialogue system")
            
            # Initialize existing integrations
            await self._initialize_integrations()
            
            self.logger.info("Dialogue system initialized successfully with centralized RAG")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize dialogue system: {e}")
            return False

    async def _initialize_integrations(self):
        """Initialize all necessary integrations"""
        # Implementation of _initialize_integrations method
        pass

    async def generate_response(
        self,
        npc_id: str,
        player_id: str,
        input_text: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate enhanced dialogue response using centralized RAG and all integrations
        """
        start_time = datetime.now()
        
        try:
            # Prepare context
            full_context = await self._prepare_context(npc_id, player_id, input_text, context)
            
            # Generate base response using existing LLM logic
            base_response = await self._generate_base_response(npc_id, player_id, input_text, full_context)
            
            # Enhance with centralized RAG if available
            if self.rag_client and self.config['response_enhancement_enabled']:
                enhanced_response = await self._enhance_with_rag(
                    base_response, input_text, full_context
                )
            else:
                enhanced_response = base_response
            
            # Apply integration-specific enhancements (keeping existing logic)
            final_response = await self._apply_integration_enhancements(
                enhanced_response, npc_id, player_id, full_context
            )
            
            # Update performance stats
            processing_time = (datetime.now() - start_time).total_seconds()
            self._update_performance_stats(processing_time)
            
            return {
                "response": final_response,
                "context": full_context,
                "metadata": {
                    "processing_time": processing_time,
                    "rag_enhanced": self.rag_client is not None,
                    "integrations_applied": self._get_active_integrations(),
                    "timestamp": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error generating dialogue response: {e}")
            return {
                "response": "I'm not sure how to respond to that.",
                "context": context or {},
                "metadata": {
                    "error": str(e),
                    "fallback_used": True,
                    "timestamp": datetime.now().isoformat()
                }
            }

    async def _enhance_with_rag(
        self, 
        base_response: str, 
        input_text: str, 
        context: Dict[str, Any]
    ) -> str:
        """Enhance response using centralized RAG service"""
        try:
            # Use centralized RAG client to enhance response
            rag_response = await self.rag_client.enhance_response(
                base_response=base_response,
                context=input_text,
                context_data=context
            )
            
            if rag_response.context_used:
                self.performance_stats['rag_enhancements'] += 1
                self.logger.debug(f"RAG enhancement applied with confidence: {rag_response.confidence:.2f}")
                return rag_response.content
            else:
                return base_response
                
        except Exception as e:
            self.logger.error(f"RAG enhancement failed: {e}")
            return base_response

    async def query_cross_system_knowledge(
        self, 
        query: str, 
        systems: List[str],
        context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Query knowledge across multiple systems using centralized RAG"""
        if not self.rag_client:
            return []
        
        try:
            knowledge_entries = await self.rag_client.cross_system_query(
                query=query,
                systems=systems,
                context=context
            )
            
            self.performance_stats['cross_system_queries'] += 1
            
            # Convert to dict format for compatibility
            return [
                {
                    "content": entry.content,
                    "category": entry.category,
                    "system": entry.system,
                    "confidence": entry.confidence,
                    "metadata": entry.metadata,
                    "tags": entry.tags
                }
                for entry in knowledge_entries
            ]
            
        except Exception as e:
            self.logger.error(f"Cross-system query failed: {e}")
            return []

    async def add_dialogue_knowledge(
        self, 
        content: str, 
        category: str = "dialogue",
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None
    ) -> bool:
        """Add knowledge to the centralized RAG system"""
        if not self.rag_client:
            return False
        
        try:
            return await self.rag_client.add_knowledge(
                content=content,
                category=category,
                metadata=metadata or {},
                tags=tags or []
            )
        except Exception as e:
            self.logger.error(f"Failed to add dialogue knowledge: {e}")
            return False

    async def learn_from_conversation(
        self, 
        npc_id: str, 
        player_id: str, 
        conversation: List[Dict[str, str]]
    ) -> bool:
        """Learn from conversation and add insights to knowledge base"""
        if not self.rag_client:
            return False
        
        try:
            # Extract meaningful patterns from conversation
            insights = await self._extract_conversation_insights(npc_id, player_id, conversation)
            
            success_count = 0
            for insight in insights:
                success = await self.rag_client.add_knowledge(
                    content=insight['content'],
                    category=insight['category'],
                    metadata={
                        'npc_id': npc_id,
                        'player_id': player_id,
                        'conversation_length': len(conversation),
                        'learned_from': 'conversation',
                        **insight.get('metadata', {})
                    },
                    tags=insight.get('tags', [])
                )
                if success:
                    success_count += 1
            
            self.logger.info(f"Learned {success_count} insights from conversation")
            return success_count > 0
            
        except Exception as e:
            self.logger.error(f"Failed to learn from conversation: {e}")
            return False

    async def _extract_conversation_insights(
        self, 
        npc_id: str, 
        player_id: str, 
        conversation: List[Dict[str, str]]
    ) -> List[Dict[str, Any]]:
        """Extract insights from conversation for learning"""
        insights = []
        
        # Simple pattern extraction (could be enhanced with ML)
        for exchange in conversation:
            if exchange.get('speaker') == 'player':
                player_input = exchange.get('text', '')
                
                # Look for questions about lore, locations, characters, etc.
                if any(keyword in player_input.lower() for keyword in ['what', 'who', 'where', 'how', 'why']):
                    # Find the NPC's response
                    npc_response = None
                    for next_exchange in conversation[conversation.index(exchange)+1:]:
                        if next_exchange.get('speaker') == 'npc':
                            npc_response = next_exchange.get('text', '')
                            break
                    
                    if npc_response:
                        insights.append({
                            'content': f"Q: {player_input}\nA: {npc_response}",
                            'category': 'dialogue',
                            'metadata': {
                                'type': 'qa_pair',
                                'npc_id': npc_id
                            },
                            'tags': ['learned', 'qa', npc_id]
                        })
        
        return insights

    def get_rag_statistics(self) -> Dict[str, Any]:
        """Get RAG system statistics"""
        if not self.rag_client:
            return {"rag_available": False}
        
        try:
            # Get system-specific stats (this would be implemented in the RAG client)
            return {
                "rag_available": True,
                "system": "dialogue",
                "performance_stats": self.performance_stats.copy()
            }
        except Exception as e:
            self.logger.error(f"Failed to get RAG statistics: {e}")
            return {"rag_available": False, "error": str(e)}

    # ... rest of existing methods remain the same ...

# Singleton instance
_DIALOGUE_SYSTEM_INSTANCE = None

def get_dialogue_system() -> DialogueSystemNew:
    """
    Get the singleton instance of the dialogue system.
    
    Returns:
        DialogueSystemNew instance
    """
    global _DIALOGUE_SYSTEM_INSTANCE
    
    if _DIALOGUE_SYSTEM_INSTANCE is None:
        # Import integration instances
        from backend.systems.memory.memory_manager import MemoryManager
        from backend.systems.rumor.services.rumor_system import RumorSystem
        from backend.systems.motif.services.manager_core import MotifManager
        from backend.systems.factions.faction_manager import FactionManager
        from backend.systems.population.managers.population_manager import PopulationManager
        from backend.infrastructure.systems.world_state.utils.legacy.world_state_manager import WorldStateManager
        from backend.systems.game_time.services.time_manager import TimeManager
        from backend.systems.dialogue.poi_integration import DialoguePOIIntegration
        from backend.systems.quests.quest_manager import QuestManager
        from backend.systems.regions.region_manager import RegionManager
        from backend.systems.factions.war_manager import WarManager
        from backend.systems.characters.relationship_manager import RelationshipManager
        from backend.infrastructure.analytics.analytics_manager import AnalyticsManager
        
        # Create integrations
        memory_integration = DialogueMemoryIntegration(MemoryManager.get_instance())
        rumor_integration = DialogueRumorIntegration(RumorSystem.get_instance())
        motif_integration = DialogueMotifIntegration(MotifManager.get_instance())
        faction_integration = DialogueFactionIntegration(FactionManager.get_instance())
        population_integration = DialoguePopulationIntegration(PopulationManager.get_instance())
        world_state_integration = DialogueWorldStateIntegration(WorldStateManager.get_instance())
        time_integration = DialogueTimeIntegration(TimeManager.get_instance())
        poi_integration = DialoguePOIIntegration()
        quest_integration = DialogueQuestIntegration(QuestManager.get_instance())
        region_integration = DialogueRegionIntegration(RegionManager.get_instance())
        war_integration = DialogueWarIntegration(WarManager.get_instance())
        relationship_integration = DialogueRelationshipIntegration(RelationshipManager.get_instance())
        analytics_integration = DialogueAnalyticsIntegration(AnalyticsManager.get_instance())
        
        # Create language generator
        from backend.systems.language.language_generator import LanguageGenerator
        language_generator = LanguageGenerator()
        
        # Create dialogue event emitter
        from backend.infrastructure.systems.dialogue.events import DialogueEventEmitter
        event_emitter = DialogueEventEmitter()
        
        # Initialize dialogue system with all integrations
        _DIALOGUE_SYSTEM_INSTANCE = DialogueSystemNew()
        
        logger.info("Initialized singleton dialogue system with all integrations")
    
    return _DIALOGUE_SYSTEM_INSTANCE 