"""
Memory System Event Integration
------------------------------

Event definitions and handlers for memory system integration with the event bus.
Provides cross-system communication for memory operations.
"""

from typing import Dict, List, Optional, Any, TYPE_CHECKING
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import logging

from backend.infrastructure.events.base import BaseEvent, EventHandler, EventDispatcher

if TYPE_CHECKING:
    from backend.systems.memory.services.memory import Memory

logger = logging.getLogger(__name__)


class MemoryEventType(Enum):
    """Types of memory events."""
    
    # Core memory operations
    MEMORY_CREATED = "memory.created"
    MEMORY_UPDATED = "memory.updated"
    MEMORY_DELETED = "memory.deleted"
    MEMORY_ACCESSED = "memory.accessed"
    
    # Memory analysis events
    MEMORY_IMPORTANCE_CHANGED = "memory.importance_changed"
    MEMORY_ASSOCIATION_CREATED = "memory.association_created"
    MEMORY_SUMMARIZED = "memory.summarized"
    
    # Cross-system integration events
    DIALOGUE_COMPLETED = "dialogue.completed"
    FACTION_EVENT_OCCURRED = "faction.event_occurred"
    ALLIANCE_FORMED = "alliance.formed"
    ALLIANCE_BROKEN = "alliance.broken"
    BETRAYAL_DETECTED = "betrayal.detected"
    
    # Behavior influence events
    TRUST_LEVEL_CHANGED = "trust.level_changed"
    EMOTIONAL_TRIGGER_ACTIVATED = "emotion.trigger_activated"
    RISK_ASSESSMENT_UPDATED = "risk.assessment_updated"


@dataclass
class MemoryEvent(BaseEvent):
    """Base event for memory system operations."""
    
    entity_id: str  # NPC/entity that owns the memory
    entity_type: str = "npc"
    memory_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MemoryCreatedEvent(MemoryEvent):
    """Event emitted when a new memory is created."""
    
    event_type = MemoryEventType.MEMORY_CREATED.value
    
    content: str
    memory_type: str
    categories: List[str]
    importance: float
    auto_categorized: bool = True


@dataclass
class MemoryUpdatedEvent(MemoryEvent):
    """Event emitted when a memory is updated."""
    
    event_type = MemoryEventType.MEMORY_UPDATED.value
    
    updated_fields: Dict[str, Any]
    previous_importance: Optional[float] = None
    new_importance: Optional[float] = None


@dataclass
class MemoryAccessedEvent(MemoryEvent):
    """Event emitted when a memory is accessed."""
    
    event_type = MemoryEventType.MEMORY_ACCESSED.value
    
    access_context: str
    access_count: int
    saliency_boost: float = 0.0


@dataclass
class MemoryAssociationCreatedEvent(MemoryEvent):
    """Event emitted when a memory association is created."""
    
    event_type = MemoryEventType.MEMORY_ASSOCIATION_CREATED.value
    
    memory_a_id: str
    memory_b_id: str
    association_type: str
    strength: float


@dataclass
class DialogueCompletedEvent(MemoryEvent):
    """Event emitted when dialogue is completed."""
    
    event_type = MemoryEventType.DIALOGUE_COMPLETED.value
    
    participant_id: str
    dialogue_content: str
    sentiment: str  # positive, negative, neutral
    topics: List[str] = field(default_factory=list)
    duration_minutes: Optional[int] = None


@dataclass
class FactionEventOccurredEvent(MemoryEvent):
    """Event emitted when a faction-related event occurs."""
    
    event_type = MemoryEventType.FACTION_EVENT_OCCURRED.value
    
    faction_id: str
    event_description: str
    event_impact: str  # major, minor, neutral
    involved_entities: List[str] = field(default_factory=list)


@dataclass
class TrustLevelChangedEvent(MemoryEvent):
    """Event emitted when trust level changes significantly."""
    
    event_type = MemoryEventType.TRUST_LEVEL_CHANGED.value
    
    target_entity_id: str
    previous_trust: float
    new_trust: float
    change_reason: str
    contributing_memories: List[str] = field(default_factory=list)


# Event Handlers
class MemoryEventHandler(EventHandler):
    """Base handler for memory events."""
    
    def __init__(self, memory_manager=None):
        self.memory_manager = memory_manager
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    async def handle(self, event: BaseEvent) -> None:
        """Handle memory events."""
        if isinstance(event, MemoryCreatedEvent):
            await self.handle_memory_created(event)
        elif isinstance(event, MemoryUpdatedEvent):
            await self.handle_memory_updated(event)
        elif isinstance(event, MemoryAccessedEvent):
            await self.handle_memory_accessed(event)
        elif isinstance(event, DialogueCompletedEvent):
            await self.handle_dialogue_completed(event)
        elif isinstance(event, FactionEventOccurredEvent):
            await self.handle_faction_event(event)
        elif isinstance(event, TrustLevelChangedEvent):
            await self.handle_trust_level_changed(event)
    
    async def handle_memory_created(self, event: MemoryCreatedEvent) -> None:
        """Handle memory creation event."""
        self.logger.info(f"Memory created for {event.entity_id}: {event.memory_id}")
        
        # Update saliency based on importance
        if self.memory_manager and event.importance > 0.7:
            # High importance memories get saliency boost
            await self._boost_memory_saliency(event.memory_id, 0.1)
    
    async def handle_memory_updated(self, event: MemoryUpdatedEvent) -> None:
        """Handle memory update event."""
        if event.new_importance and event.previous_importance:
            importance_change = event.new_importance - event.previous_importance
            if abs(importance_change) > 0.2:  # Significant change
                self.logger.info(f"Significant importance change for memory {event.memory_id}: {importance_change}")
    
    async def handle_memory_accessed(self, event: MemoryAccessedEvent) -> None:
        """Handle memory access event."""
        if event.access_count > 5:  # Frequently accessed memory
            await self._boost_memory_saliency(event.memory_id, 0.05)
    
    async def handle_dialogue_completed(self, event: DialogueCompletedEvent) -> None:
        """Handle dialogue completion by creating memory."""
        if not self.memory_manager:
            return
        
        # Create memory of the dialogue
        memory_content = f"I {event.sentiment} conversation with {event.participant_id}: {event.dialogue_content}"
        
        # Determine importance based on sentiment and topics
        importance = 0.5
        if event.sentiment == "positive":
            importance += 0.1
        elif event.sentiment == "negative":
            importance += 0.2  # Negative experiences are more memorable
        
        if any(topic in ["betrayal", "alliance", "secret", "threat"] for topic in event.topics):
            importance += 0.2
        
        importance = min(importance, 1.0)
        
        # Create the memory
        from backend.systems.memory.memory_categories import MemoryCategory
        await self.memory_manager.create_memory(
            content=memory_content,
            category=MemoryCategory.CONVERSATION,
            importance=importance,
            metadata={
                "participant_id": event.participant_id,
                "sentiment": event.sentiment,
                "topics": event.topics,
                "dialogue_source": True
            }
        )
    
    async def handle_faction_event(self, event: FactionEventOccurredEvent) -> None:
        """Handle faction events by creating memories."""
        if not self.memory_manager:
            return
        
        # Create memory of faction event
        memory_content = f"Faction event involving {event.faction_id}: {event.event_description}"
        
        # Determine importance based on impact
        importance_map = {
            "major": 0.8,
            "minor": 0.4,
            "neutral": 0.3
        }
        importance = importance_map.get(event.event_impact, 0.5)
        
        from backend.systems.memory.memory_categories import MemoryCategory
        await self.memory_manager.create_memory(
            content=memory_content,
            category=MemoryCategory.FACTION,
            importance=importance,
            metadata={
                "faction_id": event.faction_id,
                "event_impact": event.event_impact,
                "involved_entities": event.involved_entities,
                "faction_source": True
            }
        )
    
    async def handle_trust_level_changed(self, event: TrustLevelChangedEvent) -> None:
        """Handle trust level changes."""
        trust_change = event.new_trust - event.previous_trust
        
        if abs(trust_change) > 0.3:  # Significant trust change
            # Update importance of contributing memories
            for memory_id in event.contributing_memories:
                if self.memory_manager:
                    memory = await self.memory_manager.get_memory(memory_id)
                    if memory:
                        # Boost importance for memories that caused significant trust changes
                        new_importance = min(memory.importance + 0.1, 1.0)
                        await self.memory_manager.update_memory_importance(memory_id, new_importance)
    
    async def _boost_memory_saliency(self, memory_id: str, boost_amount: float) -> None:
        """Boost memory saliency."""
        if self.memory_manager:
            memory = await self.memory_manager.get_memory(memory_id)
            if memory and hasattr(memory, 'saliency'):
                new_saliency = min(memory.saliency + boost_amount, 1.0)
                # Update saliency if needed (implementation depends on memory structure)
                self.logger.debug(f"Boosted saliency for memory {memory_id} by {boost_amount}")


class CrossSystemMemoryIntegrator:
    """Integrates memory system with other game systems via events."""
    
    def __init__(self, event_dispatcher: EventDispatcher, memory_manager=None):
        self.event_dispatcher = event_dispatcher
        self.memory_manager = memory_manager
        self.event_handler = MemoryEventHandler(memory_manager)
        self.logger = logging.getLogger(__name__)
        
        # Subscribe to relevant events
        self._setup_event_subscriptions()
    
    def _setup_event_subscriptions(self) -> None:
        """Setup event subscriptions for cross-system integration."""
        # Subscribe to dialogue system events
        self.event_dispatcher.subscribe(MemoryEventType.DIALOGUE_COMPLETED.value, self.event_handler.handle)
        
        # Subscribe to faction system events
        self.event_dispatcher.subscribe(MemoryEventType.FACTION_EVENT_OCCURRED.value, self.event_handler.handle)
        
        # Subscribe to trust and behavior events
        self.event_dispatcher.subscribe(MemoryEventType.TRUST_LEVEL_CHANGED.value, self.event_handler.handle)
        
        self.logger.info("Memory system event subscriptions established")
    
    async def emit_memory_created(self, memory: "Memory") -> None:
        """Emit memory created event."""
        event = MemoryCreatedEvent(
            entity_id=memory.npc_id,
            memory_id=memory.memory_id,
            content=memory.content,
            memory_type=memory.memory_type,
            categories=memory.categories,
            importance=memory.importance,
            auto_categorized=True  # Assume auto-categorized by default
        )
        await self.event_dispatcher.dispatch(event)
    
    async def emit_memory_updated(self, memory: "Memory", updated_fields: Dict[str, Any],
                                 previous_importance: Optional[float] = None) -> None:
        """Emit memory updated event."""
        event = MemoryUpdatedEvent(
            entity_id=memory.npc_id,
            memory_id=memory.memory_id,
            updated_fields=updated_fields,
            previous_importance=previous_importance,
            new_importance=memory.importance
        )
        await self.event_dispatcher.dispatch(event)
    
    async def emit_memory_accessed(self, memory: "Memory", context: str) -> None:
        """Emit memory accessed event."""
        event = MemoryAccessedEvent(
            entity_id=memory.npc_id,
            memory_id=memory.memory_id,
            access_context=context,
            access_count=memory.access_count,
            saliency_boost=0.01  # Small boost for each access
        )
        await self.event_dispatcher.dispatch(event)
    
    async def emit_trust_level_changed(self, entity_id: str, target_entity_id: str,
                                     previous_trust: float, new_trust: float,
                                     reason: str, contributing_memories: List[str]) -> None:
        """Emit trust level changed event."""
        event = TrustLevelChangedEvent(
            entity_id=entity_id,
            target_entity_id=target_entity_id,
            previous_trust=previous_trust,
            new_trust=new_trust,
            change_reason=reason,
            contributing_memories=contributing_memories
        )
        await self.event_dispatcher.dispatch(event)
    
    async def handle_external_event(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """Handle events from external systems."""
        if event_type == "dialogue.completed":
            dialogue_event = DialogueCompletedEvent(
                entity_id=event_data.get("entity_id", ""),
                participant_id=event_data.get("participant_id", ""),
                dialogue_content=event_data.get("content", ""),
                sentiment=event_data.get("sentiment", "neutral"),
                topics=event_data.get("topics", [])
            )
            await self.event_handler.handle(dialogue_event)
        
        elif event_type == "faction.event_occurred":
            faction_event = FactionEventOccurredEvent(
                entity_id=event_data.get("entity_id", ""),
                faction_id=event_data.get("faction_id", ""),
                event_description=event_data.get("description", ""),
                event_impact=event_data.get("impact", "neutral"),
                involved_entities=event_data.get("involved_entities", [])
            )
            await self.event_handler.handle(faction_event)


def create_memory_event_integrator(event_dispatcher: EventDispatcher, 
                                 memory_manager=None) -> CrossSystemMemoryIntegrator:
    """Factory function for creating memory event integrator."""
    return CrossSystemMemoryIntegrator(event_dispatcher, memory_manager) 