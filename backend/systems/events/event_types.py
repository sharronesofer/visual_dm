"""
Event Types and Classes for Visual DM
------------------------------------
This module provides backward compatibility for old event type imports.
For new code, please import directly from canonical_events.py.

The event system is the backbone of Visual DM's event-driven architecture.
"""

from enum import Enum, auto
from typing import Dict, Any, Optional, List, Union
from uuid import UUID

from .base import EventBase
from .canonical_events import (
    # Import all canonical events for type assignment
    MemoryCreated, MemoryReinforced, MemoryDecayed, MemoryDeleted, MemoryRecalled,
    RumorCreated, RumorSpread, RumorMutated,
    MotifChanged,
    WorldStateChanged,
    RelationshipChanged, RelationshipCreated, RelationshipUpdated, RelationshipRemoved,
    CharacterCreated, CharacterUpdated, CharacterDeleted, CharacterLeveledUp,
    MoodChanged,
    GoalCreated, GoalCompleted, GoalFailed, GoalAbandoned, GoalProgressUpdated,
    PopulationChanged,
    POIStateChanged,
    FactionChanged,
    QuestUpdated,
    CombatEvent, CombatStarted, CombatEnded,
    TimeAdvanced,
    StorageEvent, GameSaved, GameLoaded,
    EventLogged,
)

# System Events
class SystemEventType(Enum):
    """System event types"""
    LOG = "log"
    ERROR = "error"
    DEBUG = "debug"
    STARTUP = "startup"
    SHUTDOWN = "shutdown"

class SystemEvent(EventBase):
    """Legacy system event class - use specific event classes from canonical_events instead"""
    system_type: SystemEventType
    message: str
    details: Optional[Dict[str, Any]] = None

# Memory Events
class MemoryEventType(Enum):
    """Memory event types"""
    CREATED = "created"
    REINFORCED = "reinforced"
    DECAYED = "decayed"
    DELETED = "deleted"
    RECALLED = "recalled"

class MemoryEvent(EventBase):
    """Legacy memory event class - use specific event classes from canonical_events instead"""
    memory_type: MemoryEventType
    entity_id: Union[str, UUID]
    memory_id: Union[str, UUID]
    content: Dict[str, Any]
    importance: Optional[float] = None

# Rumor Events
class RumorEventType(Enum):
    """Rumor event types"""
    CREATED = "created"
    SPREAD = "spread"
    MUTATED = "mutated"

class RumorEvent(EventBase):
    """Legacy rumor event class - use specific event classes from canonical_events instead"""
    rumor_type: RumorEventType
    rumor_id: Union[str, UUID]
    source_id: Optional[Union[str, UUID]] = None
    target_id: Optional[Union[str, UUID]] = None
    content: Dict[str, Any]
    spread_factor: Optional[float] = None

# Motif Events
class MotifEventType(Enum):
    """Motif event types"""
    CHANGED = "changed"

class MotifEvent(EventBase):
    """Legacy motif event class - use specific event classes from canonical_events instead"""
    motif_type: MotifEventType
    motif_id: str
    old_value: Optional[float] = None
    new_value: float
    location_id: Optional[Union[str, UUID]] = None

# Population Events
class PopulationEventType(Enum):
    """Population event types"""
    CHANGED = "changed"

class PopulationEvent(EventBase):
    """Legacy population event class - use specific event classes from canonical_events instead"""
    population_type: PopulationEventType
    location_id: Union[str, UUID]
    old_count: Optional[int] = None
    new_count: int
    change_reason: Optional[str] = None

# POI Events
class POIEventType(Enum):
    """POI event types"""
    STATE_CHANGED = "state_changed"

class POIEvent(EventBase):
    """Legacy POI event class - use specific event classes from canonical_events instead"""
    poi_type: POIEventType
    poi_id: Union[str, UUID]
    old_state: Optional[Dict[str, Any]] = None
    new_state: Dict[str, Any]

# Faction Events
class FactionEventType(Enum):
    """Faction event types"""
    CHANGED = "changed"

class FactionEvent(EventBase):
    """Legacy faction event class - use specific event classes from canonical_events instead"""
    faction_type: FactionEventType
    faction_id: Union[str, UUID]
    changes: Dict[str, Any]

# Quest Events
class QuestEventType(Enum):
    """Quest event types"""
    UPDATED = "updated"

class QuestEvent(EventBase):
    """Legacy quest event class - use specific event classes from canonical_events instead"""
    quest_type: QuestEventType
    quest_id: Union[str, UUID]
    update_type: str
    changes: Dict[str, Any]

# Combat Events
class CombatEventType(Enum):
    """Combat event types"""
    STARTED = "started"
    ENDED = "ended"
    TURN = "turn"
    ACTION = "action"
    DAMAGE = "damage"
    EFFECT = "effect"

# Time Events
class TimeEventType(Enum):
    """Time event types"""
    ADVANCED = "advanced"

class TimeEvent(EventBase):
    """Legacy time event class - use specific event classes from canonical_events instead"""
    time_type: TimeEventType
    old_time: Optional[Dict[str, Any]] = None
    new_time: Dict[str, Any]
    units_passed: Optional[int] = None

# Relationship Events
class RelationshipEventType(Enum):
    """Relationship event types"""
    CREATED = "created"
    UPDATED = "updated"
    REMOVED = "removed"

class RelationshipEvent(EventBase):
    """Legacy relationship event class - use specific event classes from canonical_events instead"""
    relationship_type: RelationshipEventType
    source_id: Union[str, UUID]
    target_id: Union[str, UUID]
    old_value: Optional[float] = None
    new_value: Optional[float] = None
    relationship_kind: Optional[str] = None

# Storage Events
class StorageEventType(Enum):
    """Storage event types"""
    SAVED = "saved"
    LOADED = "loaded"

# World State Events
class WorldStateEventType(Enum):
    """World state event types"""
    CHANGED = "changed"

class WorldStateEvent(EventBase):
    """Legacy world state event class - use specific event classes from canonical_events instead"""
    world_state_type: WorldStateEventType
    changes: Dict[str, Any]
    affected_entities: Optional[List[Union[str, UUID]]] = None 