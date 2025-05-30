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

from .event_base import EventBase

#
# System Events
#
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
        if not v.startswith('system:'):
            raise ValueError(f"SystemEvent event_type must start with 'system:'")
        return v

#
# Memory Events
#
class MemoryEventType(Enum):
    """Memory-related event types."""
    CREATED = 'memory:created'
    REINFORCED = 'memory:reinforced'
    DELETED = 'memory:deleted'
    ACCESSED = 'memory:accessed'
    DECAYED = 'memory:decayed'

class MemoryEvent(EventBase):
    """Memory-related event."""
    event_type: str
    entity_id: str
    memory_id: str
    memory_type: str
    content: Optional[str] = None
    relevance: Optional[float] = None
    is_core: Optional[bool] = False
    
    @validator('event_type')
    def validate_event_type(cls, v):
        if not v.startswith('memory:'):
            raise ValueError(f"MemoryEvent event_type must start with 'memory:'")
        return v

#
# Rumor Events
#
class RumorEventType(Enum):
    """Rumor-related event types."""
    CREATED = 'rumor:created'
    SPREAD = 'rumor:spread'
    MUTATED = 'rumor:mutated'
    FORGOTTEN = 'rumor:forgotten'
    VALIDATED = 'rumor:validated'
    DISPROVEN = 'rumor:disproven'

class RumorEvent(EventBase):
    """Rumor-related event."""
    event_type: str
    rumor_id: str
    source_id: Optional[str] = None
    target_id: Optional[str] = None
    content: Optional[str] = None
    truth_value: Optional[float] = None
    believability: Optional[float] = None
    rumor_type: Optional[str] = None
    
    @validator('event_type')
    def validate_event_type(cls, v):
        if not v.startswith('rumor:'):
            raise ValueError(f"RumorEvent event_type must start with 'rumor:'")
        return v

#
# Motif Events
#
class MotifEventType(Enum):
    """Motif-related event types."""
    CHANGED = 'motif:changed'
    ACTIVATED = 'motif:activated'
    EXPIRED = 'motif:expired'
    REINFORCED = 'motif:reinforced'

class MotifEvent(EventBase):
    """Motif-related event."""
    event_type: str
    motif_id: str
    motif_type: str
    region_id: Optional[str] = None
    intensity: Optional[int] = None
    duration: Optional[int] = None
    is_global: Optional[bool] = False
    
    @validator('event_type')
    def validate_event_type(cls, v):
        if not v.startswith('motif:'):
            raise ValueError(f"MotifEvent event_type must start with 'motif:'")
        return v

#
# Population Events
#
class PopulationEventType(Enum):
    """Population-related event types."""
    CHANGED = 'population:changed'
    MIGRATED = 'population:migrated'
    THRESHOLD_CROSSED = 'population:threshold'
    CRISIS = 'population:crisis'
    GROWTH = 'population:growth'

class PopulationEvent(EventBase):
    """Population-related event."""
    event_type: str
    location_id: str
    previous_value: int
    new_value: int
    delta: int
    cause: Optional[str] = None
    
    @validator('event_type')
    def validate_event_type(cls, v):
        if not v.startswith('population:'):
            raise ValueError(f"PopulationEvent event_type must start with 'population:'")
        return v

#
# POI Events
#
class POIEventType(Enum):
    """POI-related event types."""
    CREATED = 'poi:created'
    STATE_CHANGED = 'poi:state_changed'
    DISCOVERED = 'poi:discovered'
    ABANDONED = 'poi:abandoned'
    REPOPULATED = 'poi:repopulated'

class POIEvent(EventBase):
    """POI-related event."""
    event_type: str
    poi_id: str
    previous_state: Optional[str] = None
    new_state: Optional[str] = None
    poi_type: Optional[str] = None
    region_id: Optional[str] = None
    
    @validator('event_type')
    def validate_event_type(cls, v):
        if not v.startswith('poi:'):
            raise ValueError(f"POIEvent event_type must start with 'poi:'")
        return v

#
# Faction Events
#
class FactionEventType(Enum):
    """Faction-related event types."""
    CREATED = 'faction:created'
    CHANGED = 'faction:changed'
    REPUTATION_CHANGED = 'faction:reputation_changed'
    MEMBER_JOINED = 'faction:member_joined'
    MEMBER_LEFT = 'faction:member_left'
    SCHISM = 'faction:schism'

class FactionEvent(EventBase):
    """Faction-related event."""
    event_type: str
    faction_id: str
    entity_id: Optional[str] = None
    change_type: Optional[str] = None
    previous_value: Optional[Any] = None
    new_value: Optional[Any] = None
    
    @validator('event_type')
    def validate_event_type(cls, v):
        if not v.startswith('faction:'):
            raise ValueError(f"FactionEvent event_type must start with 'faction:'")
        return v

#
# Quest Events
#
class QuestEventType(Enum):
    """Quest-related event types."""
    CREATED = 'quest:created'
    UPDATED = 'quest:updated'
    COMPLETED = 'quest:completed'
    FAILED = 'quest:failed'
    STEP_COMPLETED = 'quest:step_completed'
    OBJECTIVE_COMPLETED = 'quest:objective_completed'

class QuestEvent(EventBase):
    """Quest-related event."""
    event_type: str
    quest_id: str
    character_id: Optional[str] = None
    step_id: Optional[str] = None
    objective_id: Optional[str] = None
    status: Optional[str] = None
    progress: Optional[float] = None
    
    @validator('event_type')
    def validate_event_type(cls, v):
        if not v.startswith('quest:'):
            raise ValueError(f"QuestEvent event_type must start with 'quest:'")
        return v

#
# Combat Events
#
class CombatEventType(Enum):
    """Combat-related event types."""
    STARTED = 'combat:started'
    ENDED = 'combat:ended'
    TURN = 'combat:turn'
    ATTACK = 'combat:attack'
    DAMAGE = 'combat:damage'
    HEAL = 'combat:heal'
    EFFECT_APPLIED = 'combat:effect_applied'
    EFFECT_REMOVED = 'combat:effect_removed'

class CombatEvent(EventBase):
    """Combat-related event."""
    event_type: str
    combat_id: str
    entity_id: Optional[str] = None
    target_id: Optional[str] = None
    ability_id: Optional[str] = None
    damage: Optional[int] = None
    effect_id: Optional[str] = None
    result: Optional[str] = None
    
    @validator('event_type')
    def validate_event_type(cls, v):
        if not v.startswith('combat:'):
            raise ValueError(f"CombatEvent event_type must start with 'combat:'")
        return v

#
# Time Events
#
class TimeEventType(Enum):
    """Time-related event types."""
    ADVANCED = 'time:advanced'
    DAY_CHANGED = 'time:day_changed'
    MONTH_CHANGED = 'time:month_changed'
    YEAR_CHANGED = 'time:year_changed'
    SEASON_CHANGED = 'time:season_changed'
    DAWN = 'time:dawn'
    DUSK = 'time:dusk'

class TimeEvent(EventBase):
    """Time-related event."""
    event_type: str
    game_time: Any  # Could be a custom time object
    real_time: float = Field(default_factory=time.time)
    delta: Optional[float] = None
    
    @validator('event_type')
    def validate_event_type(cls, v):
        if not v.startswith('time:'):
            raise ValueError(f"TimeEvent event_type must start with 'time:'")
        return v

#
# Relationship Events
#
class RelationshipEventType(Enum):
    """Relationship-related event types."""
    CREATED = 'relationship:created'
    CHANGED = 'relationship:changed'
    REMOVED = 'relationship:removed'
    THRESHOLD_CROSSED = 'relationship:threshold_crossed'

class RelationshipEvent(EventBase):
    """Relationship-related event."""
    event_type: str
    source_id: str
    target_id: str
    relationship_type: str
    previous_value: Optional[Any] = None
    new_value: Optional[Any] = None
    
    @validator('event_type')
    def validate_event_type(cls, v):
        if not v.startswith('relationship:'):
            raise ValueError(f"RelationshipEvent event_type must start with 'relationship:'")
        return v

#
# Storage Events
#
class StorageEventType(Enum):
    """Storage-related event types."""
    SAVED = 'storage:saved'
    LOADED = 'storage:loaded'
    AUTOSAVED = 'storage:autosaved'
    CHECKPOINT = 'storage:checkpoint'
    ERROR = 'storage:error'

class StorageEvent(EventBase):
    """Storage-related event."""
    event_type: str
    storage_id: str
    operation: str
    success: bool
    error: Optional[str] = None
    
    @validator('event_type')
    def validate_event_type(cls, v):
        if not v.startswith('storage:'):
            raise ValueError(f"StorageEvent event_type must start with 'storage:'")
        return v

#
# World State Events
#
class WorldStateEventType(Enum):
    """World state-related event types."""
    CREATED = 'world_state:created'
    UPDATED = 'world_state:updated'
    REMOVED = 'world_state:removed'
    THRESHOLD_CROSSED = 'world_state:threshold_crossed'

class WorldStateEvent(EventBase):
    """World state-related event."""
    event_type: str
    key: str
    previous_value: Optional[Any] = None
    new_value: Optional[Any] = None
    category: Optional[str] = None
    region_id: Optional[str] = None
    
    @validator('event_type')
    def validate_event_type(cls, v):
        if not v.startswith('world_state:'):
            raise ValueError(f"WorldStateEvent event_type must start with 'world_state:'")
        return v 