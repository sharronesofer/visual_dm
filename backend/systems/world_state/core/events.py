"""
Event definitions for the World State system.

Defines all events that can be emitted by the World State system.
"""
from typing import Optional, Any, Dict, List
from datetime import datetime
from pydantic import Field

from backend.systems.events.models.event_dispatcher import EventBase
from backend.systems.world_state.core.types import StateChangeType, WorldRegion, StateCategory

class WorldStateEvent(EventBase):
    """Base event emitted when world state changes occur."""
    state_key: str
    change_type: StateChangeType
    old_value: Optional[Any] = None
    new_value: Any
    region: WorldRegion = WorldRegion.GLOBAL
    category: StateCategory = StateCategory.OTHER
    entity_id: Optional[str] = None

class WorldStateCreatedEvent(WorldStateEvent):
    """Event emitted when a new state variable is created."""
    change_type: StateChangeType = StateChangeType.CREATED

class WorldStateUpdatedEvent(WorldStateEvent):
    """Event emitted when a state variable is updated."""
    change_type: StateChangeType = StateChangeType.UPDATED

class WorldStateDeletedEvent(WorldStateEvent):
    """Event emitted when a state variable is deleted."""
    change_type: StateChangeType = StateChangeType.DELETED

class WorldStateCalculatedEvent(WorldStateEvent):
    """Event emitted when a calculated state variable changes."""
    change_type: StateChangeType = StateChangeType.CALCULATED
    formula: Optional[str] = None
    dependencies: List[str] = Field(default_factory=list)

class WorldStateBatchChangedEvent(EventBase):
    """Event emitted when multiple state variables change at once."""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    changes: List[Dict[str, Any]] = Field(default_factory=list)
    source: Optional[str] = None
    region: Optional[WorldRegion] = None

class WorldStateEffectAppliedEvent(EventBase):
    """Event emitted when an effect is applied to the world state."""
    effect_id: str
    effect_type: str
    target_key: str
    value: Any
    duration: Optional[float] = None  # Duration in seconds, if temporary
    source: str  # Source of the effect (e.g., spell, item, event) 