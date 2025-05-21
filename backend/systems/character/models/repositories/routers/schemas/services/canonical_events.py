"""
Canonical event types for the Visual DM system.

This module defines all the standard event types used throughout the application,
as documented in the Development Bible.
"""
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from pydantic import Field, validator
import time
import datetime

from .event_dispatcher import EventBase

class SystemEventType(Enum):
    """System-level event types."""
    STARTUP = 'system:startup'
    SHUTDOWN = 'system:shutdown'
    ERROR = 'system:error'
    WARNING = 'system:warning'
    INFO = 'system:info'

class SystemEvent(EventBase):
    """System-level event."""
    event_type: str
    component: str
    details: Optional[Dict[str, Any]] = None
    
    @validator('event_type')
    def validate_event_type(cls, v):
        # Allow using either the enum value or string
        if isinstance(v, SystemEventType):
            return v.value
        if any(v == e.value for e in SystemEventType):
            return v
        raise ValueError(f"Invalid system event type: {v}")

class MemoryEventType(Enum):
    """Memory-related event types."""
    CREATED = 'memory:created'
    REINFORCED = 'memory:reinforced'
    DELETED = 'memory:deleted'
    ACCESSED = 'memory:accessed'
    MODIFIED = 'memory:modified'

class MemoryEvent(EventBase):
    """Memory system event."""
    event_type: str
    entity_id: str
    memory_id: str
    memory_type: str
    core_memory: bool = False
    relevance: Optional[float] = None
    content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    @validator('event_type')
    def validate_event_type(cls, v):
        if isinstance(v, MemoryEventType):
            return v.value
        if any(v == e.value for e in MemoryEventType):
            return v
        raise ValueError(f"Invalid memory event type: {v}")

class RumorEventType(Enum):
    """Rumor-related event types."""
    SPREAD = 'rumor:spread'
    CREATED = 'rumor:created'
    MUTATED = 'rumor:mutated'
    VERIFIED = 'rumor:verified'
    DEBUNKED = 'rumor:debunked'
    FORGOTTEN = 'rumor:forgotten'

class RumorEvent(EventBase):
    """Rumor system event."""
    event_type: str
    rumor_id: str
    rumor_type: str
    source_entity_id: Optional[str] = None
    target_entity_id: Optional[str] = None
    truth_value: float = 0.5
    severity: int = 1
    content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    @validator('event_type')
    def validate_event_type(cls, v):
        if isinstance(v, RumorEventType):
            return v.value
        if any(v == e.value for e in RumorEventType):
            return v
        raise ValueError(f"Invalid rumor event type: {v}")

class MotifEventType(Enum):
    """Motif-related event types."""
    CHANGED = 'motif:changed'
    ACTIVATED = 'motif:activated'
    DEACTIVATED = 'motif:deactivated'
    REINFORCED = 'motif:reinforced'

class MotifEvent(EventBase):
    """Motif system event."""
    event_type: str
    motif_type: str
    scope: str  # 'global' or 'regional'
    region_id: Optional[str] = None
    intensity: int = 1
    previous_motif: Optional[str] = None
    duration: Optional[int] = None  # in days
    metadata: Optional[Dict[str, Any]] = None
    
    @validator('event_type')
    def validate_event_type(cls, v):
        if isinstance(v, MotifEventType):
            return v.value
        if any(v == e.value for e in MotifEventType):
            return v
        raise ValueError(f"Invalid motif event type: {v}")

class PopulationEventType(Enum):
    """Population-related event types."""
    CHANGED = 'population:changed'
    BIRTH = 'population:birth'
    DEATH = 'population:death'
    MIGRATION = 'population:migration'

class PopulationEvent(EventBase):
    """Population system event."""
    event_type: str
    poi_id: str
    previous_value: int
    current_value: int
    change_type: str  # 'natural', 'migration', 'catastrophe', etc.
    change_reason: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    @validator('event_type')
    def validate_event_type(cls, v):
        if isinstance(v, PopulationEventType):
            return v.value
        if any(v == e.value for e in PopulationEventType):
            return v
        raise ValueError(f"Invalid population event type: {v}")

class POIEventType(Enum):
    """POI-related event types."""
    STATE_CHANGED = 'poi:state_changed'
    CREATED = 'poi:created'
    DESTROYED = 'poi:destroyed'
    DISCOVERED = 'poi:discovered'
    MODIFIED = 'poi:modified'

class POIEvent(EventBase):
    """POI system event."""
    event_type: str
    poi_id: str
    poi_type: str
    previous_state: Optional[str] = None
    current_state: str
    region_id: Optional[str] = None
    trigger_type: Optional[str] = None  # What caused the state change
    metadata: Optional[Dict[str, Any]] = None
    
    @validator('event_type')
    def validate_event_type(cls, v):
        if isinstance(v, POIEventType):
            return v.value
        if any(v == e.value for e in POIEventType):
            return v
        raise ValueError(f"Invalid POI event type: {v}")

class FactionEventType(Enum):
    """Faction-related event types."""
    CHANGED = 'faction:changed'
    CREATED = 'faction:created'
    DISSOLVED = 'faction:dissolved'
    REPUTATION_CHANGED = 'faction:reputation_changed'
    TERRITORY_CHANGED = 'faction:territory_changed'
    RELATIONSHIP_CHANGED = 'faction:relationship_changed'

class FactionEvent(EventBase):
    """Faction system event."""
    event_type: str
    faction_id: str
    target_id: Optional[str] = None  # Entity ID, POI ID, or other faction ID
    target_type: Optional[str] = None  # 'entity', 'poi', 'faction'
    previous_value: Optional[Any] = None
    current_value: Any
    change_type: str
    metadata: Optional[Dict[str, Any]] = None
    
    @validator('event_type')
    def validate_event_type(cls, v):
        if isinstance(v, FactionEventType):
            return v.value
        if any(v == e.value for e in FactionEventType):
            return v
        raise ValueError(f"Invalid faction event type: {v}")

class QuestEventType(Enum):
    """Quest-related event types."""
    UPDATED = 'quest:updated'
    STARTED = 'quest:started'
    COMPLETED = 'quest:completed'
    FAILED = 'quest:failed'
    MILESTONE_REACHED = 'quest:milestone_reached'
    ABANDONED = 'quest:abandoned'

class QuestEvent(EventBase):
    """Quest system event."""
    event_type: str
    quest_id: str
    quest_type: str
    entity_id: Optional[str] = None  # Who triggered the quest event
    previous_state: Optional[str] = None
    current_state: str
    milestone_id: Optional[str] = None
    progress: Optional[float] = None  # 0.0 to 1.0
    metadata: Optional[Dict[str, Any]] = None
    
    @validator('event_type')
    def validate_event_type(cls, v):
        if isinstance(v, QuestEventType):
            return v.value
        if any(v == e.value for e in QuestEventType):
            return v
        raise ValueError(f"Invalid quest event type: {v}")

class CombatEventType(Enum):
    """Combat-related event types."""
    STARTED = 'combat:started'
    ENDED = 'combat:ended'
    ATTACK = 'combat:attack'
    DEFEND = 'combat:defend'
    EFFECT_APPLIED = 'combat:effect_applied'
    EFFECT_REMOVED = 'combat:effect_removed'
    DEATH = 'combat:death'

class CombatEvent(EventBase):
    """Combat system event."""
    event_type: str
    combat_id: str
    attacker_id: Optional[str] = None
    defender_id: Optional[str] = None
    effect_id: Optional[str] = None
    damage: Optional[int] = None
    hit_points: Optional[int] = None
    outcome: Optional[str] = None
    position: Optional[Dict[str, float]] = None
    metadata: Optional[Dict[str, Any]] = None
    
    @validator('event_type')
    def validate_event_type(cls, v):
        if isinstance(v, CombatEventType):
            return v.value
        if any(v == e.value for e in CombatEventType):
            return v
        raise ValueError(f"Invalid combat event type: {v}")

class TimeEventType(Enum):
    """Time-related event types."""
    ADVANCED = 'time:advanced'
    DAY_CHANGED = 'time:day_changed'
    MONTH_CHANGED = 'time:month_changed'
    YEAR_CHANGED = 'time:year_changed'
    SEASON_CHANGED = 'time:season_changed'
    SCHEDULED_EVENT = 'time:scheduled_event'

class TimeEvent(EventBase):
    """Time system event."""
    event_type: str
    previous_time: Union[float, str]
    current_time: Union[float, str]
    game_date: Optional[str] = None  # ISO format
    delta: Optional[float] = None  # Time difference in seconds
    season: Optional[str] = None
    scheduled_event_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    @validator('event_type')
    def validate_event_type(cls, v):
        if isinstance(v, TimeEventType):
            return v.value
        if any(v == e.value for e in TimeEventType):
            return v
        raise ValueError(f"Invalid time event type: {v}")

class RelationshipEventType(Enum):
    """Relationship-related event types."""
    CHANGED = 'relationship:changed'
    CREATED = 'relationship:created'
    ENDED = 'relationship:ended'
    AFFINITY_CHANGED = 'relationship:affinity_changed'
    STATUS_CHANGED = 'relationship:status_changed'

class RelationshipEvent(EventBase):
    """Relationship system event."""
    event_type: str
    entity1_id: str
    entity2_id: str
    relationship_type: str
    previous_value: Optional[Any] = None
    current_value: Any
    reason: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    @validator('event_type')
    def validate_event_type(cls, v):
        if isinstance(v, RelationshipEventType):
            return v.value
        if any(v == e.value for e in RelationshipEventType):
            return v
        raise ValueError(f"Invalid relationship event type: {v}")

class StorageEventType(Enum):
    """Storage-related event types."""
    SAVE = 'storage:save'
    LOAD = 'storage:load'
    AUTOSAVE = 'storage:autosave'
    CHECKPOINT = 'storage:checkpoint'
    ERROR = 'storage:error'

class StorageEvent(EventBase):
    """Storage system event."""
    event_type: str
    operation_id: str
    file_path: Optional[str] = None
    success: bool = True
    error_message: Optional[str] = None
    duration_ms: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None
    
    @validator('event_type')
    def validate_event_type(cls, v):
        if isinstance(v, StorageEventType):
            return v.value
        if any(v == e.value for e in StorageEventType):
            return v
        raise ValueError(f"Invalid storage event type: {v}")

class WorldStateEventType(Enum):
    """World state-related event types."""
    CHANGED = 'world_state:changed'
    VARIABLE_SET = 'world_state:variable_set'
    VARIABLE_REMOVED = 'world_state:variable_removed'
    CHECKPOINT = 'world_state:checkpoint'
    ROLLBACK = 'world_state:rollback'

class WorldStateEvent(EventBase):
    """World state system event."""
    event_type: str
    variable_key: Optional[str] = None
    previous_value: Optional[Any] = None
    current_value: Optional[Any] = None
    category: Optional[str] = None
    region_id: Optional[str] = None
    checkpoint_id: Optional[str] = None
    rollback_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    @validator('event_type')
    def validate_event_type(cls, v):
        if isinstance(v, WorldStateEventType):
            return v.value
        if any(v == e.value for e in WorldStateEventType):
            return v
        raise ValueError(f"Invalid world state event type: {v}")

# Export all event types and classes
__all__ = [
    # Event Types
    'SystemEventType',
    'MemoryEventType',
    'RumorEventType',
    'MotifEventType',
    'PopulationEventType',
    'POIEventType',
    'FactionEventType',
    'QuestEventType',
    'CombatEventType',
    'TimeEventType',
    'RelationshipEventType',
    'StorageEventType',
    'WorldStateEventType',
    
    # Event Classes
    'SystemEvent',
    'MemoryEvent',
    'RumorEvent',
    'MotifEvent',
    'PopulationEvent',
    'POIEvent',
    'FactionEvent',
    'QuestEvent',
    'CombatEvent',
    'TimeEvent',
    'RelationshipEvent',
    'StorageEvent',
    'WorldStateEvent',
] 
