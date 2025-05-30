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
from backend.systems.dialogue.analytics_integration import DialogueAnalyticsIntegration
from backend.systems.dialogue.events import DialogueEventEmitter, DialogueStartedEvent, DialogueMessageEvent, DialogueEndedEvent

# Import language generation (assuming an LLM or template-based system)
from backend.systems.language.language_generator import LanguageGenerator

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


class DialogueSystem:
    """
    Core dialogue system that integrates with all subsystems.
    
    Responsible for managing conversations, dialogue generation, and integration
    with other systems through event-driven architecture.
    """
    
    def __init__(
        self,
        memory_integration: Optional[DialogueMemoryIntegration] = None,
        rumor_integration: Optional[DialogueRumorIntegration] = None,
        motif_integration: Optional[DialogueMotifIntegration] = None,
        faction_integration: Optional[DialogueFactionIntegration] = None,
        population_integration: Optional[DialoguePopulationIntegration] = None,
        world_state_integration: Optional[DialogueWorldStateIntegration] = None,
        time_integration: Optional[DialogueTimeIntegration] = None,
        poi_integration: Optional[DialoguePOIIntegration] = None,
        quest_integration: Optional[DialogueQuestIntegration] = None,
        region_integration: Optional[DialogueRegionIntegration] = None,
        war_integration: Optional[DialogueWarIntegration] = None,
        relationship_integration: Optional[DialogueRelationshipIntegration] = None,
        analytics_integration: Optional[DialogueAnalyticsIntegration] = None,
        language_generator: Optional[LanguageGenerator] = None,
        event_emitter: Optional[DialogueEventEmitter] = None
    ):
        """
        Initialize the dialogue system with integrations.
        
        Args:
            memory_integration: Memory system integration
            rumor_integration: Rumor system integration
            motif_integration: Motif system integration
            faction_integration: Faction system integration
            population_integration: Population system integration
            world_state_integration: World state integration
            time_integration: Time system integration
            poi_integration: POI state integration
            quest_integration: Quest and arc integration
            region_integration: Region and biome integration
            war_integration: War and conflict integration
            relationship_integration: Character relationship integration
            analytics_integration: Analytics and logging integration
            language_generator: Language generation system
            event_emitter: Event emitter for dialogue events
        """
        # Initialize integrations (create default instances if none provided)
        self.memory_integration = memory_integration or DialogueMemoryIntegration()
        self.rumor_integration = rumor_integration or DialogueRumorIntegration()
        self.motif_integration = motif_integration or DialogueMotifIntegration()
        self.faction_integration = faction_integration or DialogueFactionIntegration()
        self.population_integration = population_integration or DialoguePopulationIntegration()
        self.world_state_integration = world_state_integration or DialogueWorldStateIntegration()
        self.time_integration = time_integration or DialogueTimeIntegration()
        self.poi_integration = poi_integration or DialoguePOIIntegration()
        self.quest_integration = quest_integration or DialogueQuestIntegration()
        self.region_integration = region_integration or DialogueRegionIntegration()
        self.war_integration = war_integration or DialogueWarIntegration()
        self.relationship_integration = relationship_integration or DialogueRelationshipIntegration()
        self.analytics_integration = analytics_integration or DialogueAnalyticsIntegration()
        
        # Set up language generator and event emitter
        self.language_generator = language_generator or LanguageGenerator()
        self.event_emitter = event_emitter or DialogueEventEmitter()
        
        # Store active conversations
        self.conversations = {}
        
        logger.info("Dialogue system initialized with all integrations")
    
    def start_conversation(
        self,
        participants: Dict[str, str],
        location_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Start a new conversation.
        
        Args:
            participants: Dictionary mapping participant IDs to their roles
            location_id: Optional ID of the location where conversation occurs
            metadata: Optional additional metadata for the conversation
            
        Returns:
            ID of the new conversation
        """
        # Create new conversation
        conversation = Conversation(
            participants=participants,
            location_id=location_id,
            metadata=metadata
        )
        
        # Store conversation
        self.conversations[conversation.id] = conversation
        
        # Enhance conversation context with integrated systems
        self._enhance_conversation_context(conversation)
        
        # Emit dialogue started event
        self.event_emitter.emit_dialogue_started(
            conversation.id,
            participants,
            location_id,
            metadata
        )
        
        return conversation.id
    
    def send_message(
        self,
        conversation_id: str,
        sender_id: str,
        content: str,
        message_type: str = "dialogue",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Send a message in a conversation.
        
        Args:
            conversation_id: ID of the conversation
            sender_id: ID of the message sender
            content: Content of the message
            message_type: Type of message (dialogue, action, emote, etc.)
            metadata: Optional additional metadata for the message
            
        Returns:
            Message dictionary if successful, None otherwise
        """
        # Get conversation
        conversation = self.conversations.get(conversation_id)
        
        if not conversation or not conversation.is_active():
            logger.warning(f"Attempted to send message to inactive conversation {conversation_id}")
            return None
        
        # Add message to conversation
        message = conversation.add_message(
            sender_id=sender_id,
            content=content,
            message_type=message_type,
            metadata=metadata
        )
        
        if not message:
            return None
        
        # Process message with integrations
        self._process_message_with_integrations(conversation, message)
        
        # Emit dialogue message event
        self.event_emitter.emit_dialogue_message(
            conversation_id,
            message["id"],
            sender_id,
            content,
            message_type,
            metadata
        )
        
        return message
    
    def generate_response(
        self,
        conversation_id: str,
        responder_id: str,
        target_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Generate an NPC response in a conversation.
        
        Args:
            conversation_id: ID of the conversation
            responder_id: ID of the character generating the response
            target_id: Optional ID of the target character for the response
            metadata: Optional additional metadata to include
            
        Returns:
            Generated message dictionary if successful, None otherwise
        """
        # Get conversation
        conversation = self.conversations.get(conversation_id)
        
        if not conversation or not conversation.is_active():
            logger.warning(f"Attempted to generate response in inactive conversation {conversation_id}")
            return None
        
        # Ensure responder is a participant
        if responder_id not in conversation.participants:
            logger.warning(f"Response generator {responder_id} is not a participant in conversation {conversation_id}")
            return None
        
        # Get enhanced context for response generation
        enhanced_context = self._get_response_context(conversation, responder_id, target_id)
        
        # Generate response using language generator
        try:
            generated_content = self.language_generator.generate_dialogue(
                character_id=responder_id,
                context=enhanced_context
            )
            
            # Apply faction-based modifications if target exists
            if target_id:
                generated_content = self.faction_integration.modify_dialogue_for_faction(
                    generated_content,
                    responder_id,
                    target_id
                )
            
            # Apply motif-based styling if location exists
            if conversation.location_id:
                generated_content = self.motif_integration.apply_motif_style(
                    generated_content,
                    conversation.location_id
                )
                
                # Apply demographic awareness
                generated_content = self.population_integration.modify_dialogue_for_demographics(
                    generated_content,
                    conversation.location_id
                )
            
            # Send the generated message
            return self.send_message(
                conversation_id=conversation_id,
                sender_id=responder_id,
                content=generated_content,
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Failed to generate response: {e}")
            return None
    
    def end_conversation(
        self,
        conversation_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        End an active conversation.
        
        Args:
            conversation_id: ID of the conversation to end
            metadata: Optional additional metadata about the ending
            
        Returns:
            True if successful, False otherwise
        """
        # Get conversation
        conversation = self.conversations.get(conversation_id)
        
        if not conversation or not conversation.is_active():
            logger.warning(f"Attempted to end inactive conversation {conversation_id}")
            return False
        
        # End conversation
        if conversation.end_conversation():
            # Process conversation ending with integrations
            self._process_conversation_end(conversation, metadata)
            
            # Emit dialogue ended event
            self.event_emitter.emit_dialogue_ended(
                conversation_id,
                conversation.participants,
                metadata
            )
            
            # Remove from active conversations (but keep in memory for reference)
            # In a production system, this might be persisted to storage
            return True
            
        return False
    
    def get_conversation_context(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the current context for a conversation.
        
        Args:
            conversation_id: ID of the conversation
            
        Returns:
            Conversation context dictionary or None if not found
        """
        conversation = self.conversations.get(conversation_id)
        
        if not conversation:
            logger.warning(f"Attempted to get context for unknown conversation {conversation_id}")
            return None
            
        return conversation.get_context()
    
    def _enhance_conversation_context(self, conversation: Conversation) -> None:
        """
        Enhance conversation context with information from integrated systems.
        
        Args:
            conversation: Conversation to enhance
        """
        context = conversation.get_context()
        
        # Add world state information
        world_state_context = self.world_state_integration.add_world_state_context(context)
        conversation.context.update(world_state_context)
        
        # Add time information
        time_context = self.time_integration.add_time_context(context)
        conversation.context.update(time_context)
        
        # Add location/POI information if location is provided
        if conversation.location_id:
            # Add POI state information
            poi_context = self.poi_integration.add_poi_context(
                context,
                conversation.location_id
            )
            conversation.context.update(poi_context)
            
            # Add motif information 
            motif_context = self.motif_integration.add_motifs_to_context(
                context,
                conversation.location_id
            )
            conversation.context.update(motif_context)
            
            # Add population data
            population_context = self.population_integration.add_population_data_to_context(
                context,
                conversation.location_id
            )
            conversation.context.update(population_context)
            
            # Add region/biome information
            region_context = self.region_integration.add_region_context(
                context,
                conversation.location_id
            )
            conversation.context.update(region_context)
        
        # Add faction information if participants are present
        if len(conversation.participants) > 0:
            # Add faction relationships for participants
            faction_context = self.faction_integration.add_faction_context_to_conversation(
                context,
                conversation.participants
            )
            conversation.context.update(faction_context)
            
            # Get faction IDs from participants (assuming relationship exists)
            participant_faction_ids = []
            for participant_id in conversation.participants:
                faction_id = self.faction_integration.get_faction_for_character(participant_id)
                if faction_id:
                    participant_faction_ids.append(faction_id)
            
            # Add war information if we have factions
            if participant_faction_ids and len(participant_faction_ids) > 0:
                # Add war context for the most prominent faction
                war_context = self.war_integration.add_war_context_to_dialogue(
                    context,
                    faction_id=participant_faction_ids[0],
                    location_id=conversation.location_id,
                    include_local_only=True
                )
                conversation.context.update(war_context)
        
        # Add active quest information
        quest_context = self.quest_integration.add_quest_context(context)
        conversation.context.update(quest_context)
        
        # Add relationship context for participants
        if len(conversation.participants) >= 2:
            participant_ids = list(conversation.participants.keys())
            relationship_context = self.relationship_integration.add_relationships_context(
                context,
                participant_ids
            )
            conversation.context.update(relationship_context)
        
        # Log enhanced context via analytics
        try:
            self.analytics_integration.log_dialogue_context(
                conversation.id,
                conversation.context
            )
        except Exception as e:
            logger.warning(f"Failed to log dialogue context: {e}")
    
    def _process_message_with_integrations(
        self,
        conversation: Conversation,
        message: Dict[str, Any]
    ) -> None:
        """
        Process a new message with integrated systems.
        
        Args:
            conversation: Conversation containing the message
            message: The message to process
        """
        sender_id = message["sender_id"]
        content = message["content"]
        
        # Try to create a memory from the message
        if len(content) > 10:  # Only process substantial messages
            try:
                self.memory_integration.create_memory_from_dialogue(
                    speaker_id=sender_id,
                    message=content,
                    conversation_id=conversation.id,
                    location_id=conversation.location_id,
                    participants=conversation.participants,
                    metadata=message.get("metadata", {})
                )
            except Exception as e:
                logger.error(f"Failed to create memory from dialogue: {e}")
        
        # Try to generate a rumor from the message
        try:
            self.rumor_integration.generate_rumor_from_dialogue(
                speaker_id=sender_id,
                message=content,
                location_id=conversation.location_id,
                metadata=message.get("metadata", {})
            )
        except Exception as e:
            logger.error(f"Failed to generate rumor from dialogue: {e}")
            
        # Log dialogue message in analytics
        try:
            self.analytics_integration.log_dialogue_message(
                conversation_id=conversation.id,
                message=message
            )
        except Exception as e:
            logger.error(f"Failed to log dialogue message in analytics: {e}")
        
        # Check for quest triggers in dialogue
        try:
            self.quest_integration.check_dialogue_triggers(
                speaker_id=sender_id,
                message=content,
                conversation_id=conversation.id,
                participants=conversation.participants,
                location_id=conversation.location_id
            )
        except Exception as e:
            logger.error(f"Failed to check quest triggers: {e}")
        
        # Update relationship based on dialogue
        if len(conversation.participants) >= 2:
            try:
                # For each other participant, update relationship
                for receiver_id in conversation.participants:
                    if receiver_id != sender_id:
                        self.relationship_integration.update_relationship_from_dialogue(
                            speaker_id=sender_id,
                            receiver_id=receiver_id,
                            message=content,
                            metadata=message.get("metadata", {})
                        )
            except Exception as e:
                logger.error(f"Failed to update relationship from dialogue: {e}")
    
    def _get_response_context(
        self,
        conversation: Conversation,
        responder_id: str,
        target_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get enhanced context for response generation.
        
        Args:
            conversation: The conversation to generate response for
            responder_id: ID of the character generating the response
            target_id: Optional ID of the target character for the response
            
        Returns:
            Enhanced context dictionary for response generation
        """
        # Start with base conversation context
        context = dict(conversation.get_context())
        
        # Add target information
        if target_id:
            context["target_id"] = target_id
        
        # Enhance with memories
        try:
            memory_context = self.memory_integration.add_memories_to_context(
                responder_id=responder_id,
                context=context,
                target_id=target_id,
                limit=5
            )
            context.update(memory_context)
        except Exception as e:
            logger.error(f"Failed to add memories to context: {e}")
        
        # Enhance with rumors
        try:
            rumor_context = self.rumor_integration.add_rumors_to_context(
                character_id=responder_id,
                context=context,
                limit=3
            )
            context.update(rumor_context)
        except Exception as e:
            logger.error(f"Failed to add rumors to context: {e}")
            
        # Add world state knowledge
        try:
            world_state_context = self.world_state_integration.add_character_world_state_knowledge(
                context,
                responder_id
            )
            context.update(world_state_context)
        except Exception as e:
            logger.error(f"Failed to add world state knowledge: {e}")
            
        # Add time awareness for responder
        try:
            time_context = self.time_integration.add_character_time_awareness(
                context,
                responder_id
            )
            context.update(time_context)
        except Exception as e:
            logger.error(f"Failed to add time awareness: {e}")
            
        # Add POI knowledge if location is provided
        if conversation.location_id:
            try:
                poi_context = self.poi_integration.add_character_poi_knowledge(
                    context,
                    responder_id,
                    conversation.location_id
                )
                context.update(poi_context)
            except Exception as e:
                logger.error(f"Failed to add POI knowledge: {e}")
                
            # Add region knowledge
            try:
                region_context = self.region_integration.add_character_region_knowledge(
                    context,
                    responder_id,
                    conversation.location_id
                )
                context.update(region_context)
            except Exception as e:
                logger.error(f"Failed to add region knowledge: {e}")
        
        # Add quest knowledge
        try:
            quest_context = self.quest_integration.add_character_quest_knowledge(
                context,
                responder_id,
                target_id
            )
            context.update(quest_context)
        except Exception as e:
            logger.error(f"Failed to add quest knowledge: {e}")
            
        # Add faction knowledge
        try:
            responder_faction = self.faction_integration.get_faction_for_character(responder_id)
            if responder_faction:
                faction_context = self.faction_integration.add_character_faction_knowledge(
                    context,
                    responder_id,
                    target_id
                )
                context.update(faction_context)
                
                # Add war knowledge if faction exists
                try:
                    war_context = self.war_integration.add_war_context_to_dialogue(
                        context,
                        faction_id=responder_faction,
                        include_tensions=True
                    )
                    context.update(war_context)
                except Exception as e:
                    logger.error(f"Failed to add war knowledge: {e}")
        except Exception as e:
            logger.error(f"Failed to add faction knowledge: {e}")
            
        # Add relationship context for speaking with target
        if target_id:
            try:
                relationship_context = self.relationship_integration.add_character_relationship_context(
                    context,
                    responder_id,
                    target_id
                )
                context.update(relationship_context)
            except Exception as e:
                logger.error(f"Failed to add relationship context: {e}")
        
        return context
    
    def _process_conversation_end(
        self,
        conversation: Conversation,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Process the end of a conversation with integrated systems.
        
        Args:
            conversation: The conversation that ended
            metadata: Optional additional metadata about the ending
        """
        # Create a final memory of the conversation
        try:
            participants_str = ", ".join(conversation.participants.keys())
            memory_content = f"Had a conversation with {participants_str}"
            
            # Add location if available
            if conversation.location_id:
                memory_content += f" at {conversation.location_id}"
            
            for participant_id in conversation.participants.keys():
                self.memory_integration.create_memory_from_dialogue(
                    speaker_id=participant_id,
                    message=memory_content,
                    conversation_id=conversation.id,
                    location_id=conversation.location_id,
                    participants=conversation.participants,
                    metadata={
                        "summary": True,
                        "conversation_length": len(conversation.messages),
                        **(metadata or {})
                    }
                )
        except Exception as e:
            logger.error(f"Failed to create conversation summary memory: {e}")
            
        # Log conversation analytics
        try:
            self.analytics_integration.log_dialogue_ended(
                conversation_id=conversation.id,
                conversation_data={
                    "duration": self._calculate_conversation_duration(conversation),
                    "message_count": len(conversation.messages),
                    "participants": conversation.participants,
                    "location_id": conversation.location_id,
                    **(metadata or {})
                }
            )
        except Exception as e:
            logger.error(f"Failed to log conversation analytics: {e}")
            
        # Update relationship data based on full conversation
        try:
            if len(conversation.participants) >= 2:
                participant_ids = list(conversation.participants.keys())
                for i in range(len(participant_ids)):
                    for j in range(i+1, len(participant_ids)):
                        self.relationship_integration.update_relationship_from_conversation(
                            character1_id=participant_ids[i],
                            character2_id=participant_ids[j],
                            conversation=conversation
                        )
        except Exception as e:
            logger.error(f"Failed to update relationships from conversation: {e}")
            
        # Check for quest completion events
        try:
            self.quest_integration.check_conversation_quest_triggers(
                conversation=conversation,
                metadata=metadata
            )
        except Exception as e:
            logger.error(f"Failed to check conversation quest triggers: {e}")
            
    def _calculate_conversation_duration(self, conversation: Conversation) -> int:
        """
        Calculate the duration of a conversation in seconds.
        
        Args:
            conversation: The conversation to calculate duration for
            
        Returns:
            Duration in seconds, or -1 if unknown
        """
        try:
            start_time = conversation.context.get("started_at")
            end_time = conversation.context.get("ended_at")
            
            if start_time and end_time:
                # Parse ISO format strings to datetime
                start_dt = datetime.fromisoformat(start_time)
                end_dt = datetime.fromisoformat(end_time)
                
                # Calculate duration in seconds
                return int((end_dt - start_dt).total_seconds())
        except Exception as e:
            logger.error(f"Failed to calculate conversation duration: {e}")
            
        return -1


# Singleton instance
_DIALOGUE_SYSTEM_INSTANCE = None

def get_dialogue_system() -> DialogueSystem:
    """
    Get the singleton instance of the dialogue system.
    
    Returns:
        DialogueSystem instance
    """
    global _DIALOGUE_SYSTEM_INSTANCE
    
    if _DIALOGUE_SYSTEM_INSTANCE is None:
        # Import integration instances
        from backend.systems.memory.memory_manager import MemoryManager
        from backend.systems.rumors.rumor_manager import RumorManager
        from backend.systems.motifs.motif_manager import MotifManager
        from backend.systems.factions.faction_manager import FactionManager
        from backend.systems.population.population_manager import PopulationManager
        from backend.systems.world_state.world_state_manager import WorldStateManager
        from backend.systems.time.time_manager import TimeManager
        from backend.systems.locations.poi_manager import POIManager
        from backend.systems.quests.quest_manager import QuestManager
        from backend.systems.regions.region_manager import RegionManager
        from backend.systems.factions.war_manager import WarManager
        from backend.systems.characters.relationship_manager import RelationshipManager
        from backend.systems.analytics.analytics_manager import AnalyticsManager
        
        # Create integrations
        memory_integration = DialogueMemoryIntegration(MemoryManager.get_instance())
        rumor_integration = DialogueRumorIntegration(RumorManager.get_instance())
        motif_integration = DialogueMotifIntegration(MotifManager.get_instance())
        faction_integration = DialogueFactionIntegration(FactionManager.get_instance())
        population_integration = DialoguePopulationIntegration(PopulationManager.get_instance())
        world_state_integration = DialogueWorldStateIntegration(WorldStateManager.get_instance())
        time_integration = DialogueTimeIntegration(TimeManager.get_instance())
        poi_integration = DialoguePOIIntegration(POIManager.get_instance())
        quest_integration = DialogueQuestIntegration(QuestManager.get_instance())
        region_integration = DialogueRegionIntegration(RegionManager.get_instance())
        war_integration = DialogueWarIntegration(WarManager.get_instance())
        relationship_integration = DialogueRelationshipIntegration(RelationshipManager.get_instance())
        analytics_integration = DialogueAnalyticsIntegration(AnalyticsManager.get_instance())
        
        # Create language generator
        from backend.systems.language.language_generator import LanguageGenerator
        language_generator = LanguageGenerator()
        
        # Create dialogue event emitter
        from backend.systems.dialogue.events import DialogueEventEmitter
        event_emitter = DialogueEventEmitter()
        
        # Initialize dialogue system with all integrations
        _DIALOGUE_SYSTEM_INSTANCE = DialogueSystem(
            memory_integration=memory_integration,
            rumor_integration=rumor_integration,
            motif_integration=motif_integration,
            faction_integration=faction_integration,
            population_integration=population_integration,
            world_state_integration=world_state_integration,
            time_integration=time_integration,
            poi_integration=poi_integration,
            quest_integration=quest_integration,
            region_integration=region_integration,
            war_integration=war_integration,
            relationship_integration=relationship_integration,
            analytics_integration=analytics_integration,
            language_generator=language_generator,
            event_emitter=event_emitter
        )
        
        logger.info("Initialized singleton dialogue system with all integrations")
    
    return _DIALOGUE_SYSTEM_INSTANCE 