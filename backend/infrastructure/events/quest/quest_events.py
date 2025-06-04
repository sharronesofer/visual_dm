"""
Quest Event System
Handles quest lifecycle events and integration with other systems.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# Import event infrastructure
try:
    from backend.infrastructure.events import EventBase, get_dispatcher
    HAS_EVENT_SYSTEM = True
except ImportError:
    # Fallback event base
    class EventBase(BaseModel):
        event_type: str
        event_id: str = Field(default_factory=lambda: f"evt_{datetime.utcnow().timestamp()}")
        timestamp: datetime = Field(default_factory=datetime.utcnow)
        source: str = "quest_system"
        metadata: Dict[str, Any] = Field(default_factory=dict)
    
    HAS_EVENT_SYSTEM = False
    logger.warning("Event system not available, quest events will be logged only")


class QuestCreated(EventBase):
    """Event emitted when a new quest is created"""
    quest_id: UUID
    title: str
    npc_id: Optional[str] = None
    player_id: Optional[str] = None
    difficulty: str
    theme: str
    generation_method: str = "procedural"  # procedural, ai_generated, hybrid
    
    def __init__(self, **data):
        data["event_type"] = "quest.created"
        super().__init__(**data)


class QuestOffered(EventBase):
    """Event emitted when an NPC offers a quest to a player"""
    quest_id: UUID
    npc_id: str
    player_id: str
    offer_reason: str  # npc_need, scheduled, random, triggered
    context: Dict[str, Any] = Field(default_factory=dict)
    
    def __init__(self, **data):
        data["event_type"] = "quest.offered"
        super().__init__(**data)


class QuestAccepted(EventBase):
    """Event emitted when a player accepts a quest"""
    quest_id: UUID
    player_id: str
    npc_id: Optional[str] = None
    accepted_at: datetime = Field(default_factory=datetime.utcnow)
    
    def __init__(self, **data):
        data["event_type"] = "quest.accepted"
        super().__init__(**data)


class QuestAbandoned(EventBase):
    """Event emitted when a player abandons a quest"""
    quest_id: UUID
    player_id: str
    npc_id: Optional[str] = None
    reason: str = "player_choice"
    progress_lost: float = 0.0
    abandoned_at: datetime = Field(default_factory=datetime.utcnow)
    
    def __init__(self, **data):
        data["event_type"] = "quest.abandoned"
        super().__init__(**data)


class QuestCompleted(EventBase):
    """Event emitted when a quest is completed"""
    quest_id: UUID
    player_id: str
    npc_id: Optional[str] = None
    success: bool = True
    completion_time: float = 0.0  # minutes taken
    rewards_given: Dict[str, Any] = Field(default_factory=dict)
    
    def __init__(self, **data):
        data["event_type"] = "quest.completed"
        super().__init__(**data)


class QuestFailed(EventBase):
    """Event emitted when a quest fails"""
    quest_id: UUID
    player_id: str
    npc_id: Optional[str] = None
    failure_reason: str
    penalty_applied: bool = False
    failed_at: datetime = Field(default_factory=datetime.utcnow)
    
    def __init__(self, **data):
        data["event_type"] = "quest.failed"
        super().__init__(**data)


class QuestStepCompleted(EventBase):
    """Event emitted when a quest step is completed"""
    quest_id: UUID
    step_id: int
    player_id: str
    step_type: str
    completion_data: Dict[str, Any] = Field(default_factory=dict)
    
    def __init__(self, **data):
        data["event_type"] = "quest.step_completed"
        super().__init__(**data)


class QuestExpired(EventBase):
    """Event emitted when a quest expires due to time limits"""
    quest_id: UUID
    npc_id: Optional[str] = None
    player_id: Optional[str] = None
    expiry_reason: str = "time_limit"
    
    def __init__(self, **data):
        data["event_type"] = "quest.expired"
        super().__init__(**data)


class QuestGenerationRequested(EventBase):
    """Event emitted when quest generation is requested"""
    npc_id: str
    generation_context: Dict[str, Any]
    generation_method: str = "ai_assisted"  # procedural, ai_assisted, hybrid
    urgency: str = "normal"  # low, normal, high, critical
    
    def __init__(self, **data):
        data["event_type"] = "quest.generation_requested"
        super().__init__(**data)


class QuestEventPublisher:
    """Publisher for quest system events"""
    
    def __init__(self):
        self.dispatcher = get_dispatcher() if HAS_EVENT_SYSTEM else None
    
    def _publish(self, event: EventBase) -> bool:
        """Publish an event"""
        try:
            if self.dispatcher:
                self.dispatcher.dispatch(event)
                return True
            else:
                # Log event if no dispatcher available
                logger.info(f"Quest Event: {event.event_type} - {event.dict()}")
                return True
        except Exception as e:
            logger.error(f"Failed to publish quest event {event.event_type}: {str(e)}")
            return False
    
    def publish_quest_created(self, quest_id: UUID, title: str, npc_id: Optional[str] = None,
                            player_id: Optional[str] = None, difficulty: str = "medium",
                            theme: str = "exploration", generation_method: str = "procedural") -> bool:
        """Publish quest created event"""
        event = QuestCreated(
            quest_id=quest_id,
            title=title,
            npc_id=npc_id,
            player_id=player_id,
            difficulty=difficulty,
            theme=theme,
            generation_method=generation_method
        )
        return self._publish(event)
    
    def publish_quest_offered(self, quest_id: UUID, npc_id: str, player_id: str,
                            offer_reason: str = "npc_need", context: Optional[Dict[str, Any]] = None) -> bool:
        """Publish quest offered event"""
        event = QuestOffered(
            quest_id=quest_id,
            npc_id=npc_id,
            player_id=player_id,
            offer_reason=offer_reason,
            context=context or {}
        )
        return self._publish(event)
    
    def publish_quest_accepted(self, quest_id: UUID, player_id: str, npc_id: Optional[str] = None) -> bool:
        """Publish quest accepted event"""
        event = QuestAccepted(
            quest_id=quest_id,
            player_id=player_id,
            npc_id=npc_id
        )
        return self._publish(event)
    
    def publish_quest_abandoned(self, quest_id: UUID, player_id: str, npc_id: Optional[str] = None,
                              reason: str = "player_choice", progress_lost: float = 0.0) -> bool:
        """Publish quest abandoned event"""
        event = QuestAbandoned(
            quest_id=quest_id,
            player_id=player_id,
            npc_id=npc_id,
            reason=reason,
            progress_lost=progress_lost
        )
        return self._publish(event)
    
    def publish_quest_completed(self, quest_id: UUID, player_id: str, npc_id: Optional[str] = None,
                              success: bool = True, completion_time: float = 0.0,
                              rewards_given: Optional[Dict[str, Any]] = None) -> bool:
        """Publish quest completed event"""
        event = QuestCompleted(
            quest_id=quest_id,
            player_id=player_id,
            npc_id=npc_id,
            success=success,
            completion_time=completion_time,
            rewards_given=rewards_given or {}
        )
        return self._publish(event)
    
    def publish_quest_failed(self, quest_id: UUID, player_id: str, failure_reason: str,
                           npc_id: Optional[str] = None, penalty_applied: bool = False) -> bool:
        """Publish quest failed event"""
        event = QuestFailed(
            quest_id=quest_id,
            player_id=player_id,
            npc_id=npc_id,
            failure_reason=failure_reason,
            penalty_applied=penalty_applied
        )
        return self._publish(event)


# Global publisher instance
_quest_event_publisher = None

def get_quest_event_publisher() -> QuestEventPublisher:
    """Get the global quest event publisher instance"""
    global _quest_event_publisher
    if _quest_event_publisher is None:
        _quest_event_publisher = QuestEventPublisher()
    return _quest_event_publisher 