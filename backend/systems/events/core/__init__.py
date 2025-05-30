"""
Core event system components.

This package contains the fundamental building blocks of the event system:
- EventBase: Base class for all events
- EventDispatcher: Singleton event bus
- Canonical event types
"""

from .event_base import EventBase
from .event_dispatcher import EventDispatcher
from .canonical_events import (
    # System
    SystemEvent, SystemEventType,
    
    # Game state
    MemoryEvent, MemoryEventType,
    RumorEvent, RumorEventType,
    MotifEvent, MotifEventType,
    PopulationEvent, PopulationEventType,
    POIEvent, POIEventType,
    FactionEvent, FactionEventType,
    QuestEvent, QuestEventType,
    CombatEvent, CombatEventType,
    TimeEvent, TimeEventType,
    RelationshipEvent, RelationshipEventType,
    StorageEvent, StorageEventType,
    WorldStateEvent, WorldStateEventType,
)

__all__ = [
    'EventBase',
    'EventDispatcher',
    
    # Event types
    'SystemEvent', 'SystemEventType',
    'MemoryEvent', 'MemoryEventType',
    'RumorEvent', 'RumorEventType',
    'MotifEvent', 'MotifEventType',
    'PopulationEvent', 'PopulationEventType',
    'POIEvent', 'POIEventType',
    'FactionEvent', 'FactionEventType',
    'QuestEvent', 'QuestEventType',
    'CombatEvent', 'CombatEventType',
    'TimeEvent', 'TimeEventType',
    'RelationshipEvent', 'RelationshipEventType',
    'StorageEvent', 'StorageEventType',
    'WorldStateEvent', 'WorldStateEventType',
]
