"""
Visual DM Events System
-----------------------
A consolidated, event-driven architecture for the Visual DM game.

This module exports the canonical event system components, including
the EventDispatcher, EventBase, and predefined event types.

Importing this module gives access to all event-related functionality:
- EventDispatcher: Singleton event bus with publish-subscribe pattern
- EventBase: Base class for all event types
- Predefined event types (MemoryEvent, RumorEvent, etc.)
- Middleware for logging, error handling, and analytics
"""

# Core components
from .base import EventBase, T
from .event_dispatcher import EventDispatcher, EventMiddleware, LoggingMiddleware, AnalyticsMiddleware, get_dispatcher

# Event types
from .canonical_events import (
    # Memory events
    MemoryCreated, MemoryReinforced, MemoryDecayed, MemoryDeleted, MemoryRecalled,
    # Rumor events
    RumorCreated, RumorSpread, RumorMutated,
    # Motif events
    MotifChanged,
    # World state events
    WorldStateChanged,
    # Relationship events
    RelationshipChanged, RelationshipCreated, RelationshipUpdated, RelationshipRemoved,
    # Character events
    CharacterCreated, CharacterUpdated, CharacterDeleted, CharacterLeveledUp,
    # Mood events
    MoodChanged,
    # Goal events
    GoalCreated, GoalCompleted, GoalFailed, GoalAbandoned, GoalProgressUpdated,
    # Population events
    PopulationChanged,
    # POI events
    POIStateChanged,
    # Faction events
    FactionChanged,
    # Quest events
    QuestUpdated,
    # Combat events
    CombatEvent, CombatStarted, CombatEnded,
    # Time events
    TimeAdvanced,
    # Storage events
    StorageEvent, GameSaved, GameLoaded,
    # System events
    EventLogged,
)

# For backward compatibility with separate event_types imports
from .event_types import (
    SystemEvent, SystemEventType,
    MemoryEvent, MemoryEventType,
    RumorEvent, RumorEventType,
    MotifEvent, MotifEventType,
    PopulationEvent, PopulationEventType,
    POIEvent, POIEventType,
    FactionEvent, FactionEventType,
    QuestEvent, QuestEventType,
    CombatEventType,
    TimeEvent, TimeEventType,
    RelationshipEvent, RelationshipEventType,
    StorageEventType,
    WorldStateEvent, WorldStateEventType,
)

# Import middleware for backward compatibility
try:
    from .middleware.logging import logging_middleware
    from .middleware.error_handler import error_handling_middleware
    from .middleware.analytics import analytics_middleware
    from .middleware.debugging import debug_middleware
except ImportError:
    # Define fallbacks if middleware modules don't exist
    logging_middleware = LoggingMiddleware()
    error_handling_middleware = None
    analytics_middleware = None
    debug_middleware = None

# Import utility for backward compatibility
try:
    from .utils.manager import EventManager
except ImportError:
    # EventManager is optional
    EventManager = None

__all__ = [
    # Core
    'EventBase',
    'EventDispatcher',
    'EventMiddleware',
    'LoggingMiddleware',
    'AnalyticsMiddleware',
    'get_dispatcher',
    'T',
    
    # Memory events
    'MemoryCreated', 'MemoryReinforced', 'MemoryDecayed', 'MemoryDeleted', 'MemoryRecalled',
    
    # Rumor events
    'RumorCreated', 'RumorSpread', 'RumorMutated',
    
    # Motif events
    'MotifChanged',
    
    # World state events
    'WorldStateChanged',
    
    # Relationship events
    'RelationshipChanged', 'RelationshipCreated', 'RelationshipUpdated', 'RelationshipRemoved',
    
    # Character events
    'CharacterCreated', 'CharacterUpdated', 'CharacterDeleted', 'CharacterLeveledUp',
    
    # Mood events
    'MoodChanged',
    
    # Goal events
    'GoalCreated', 'GoalCompleted', 'GoalFailed', 'GoalAbandoned', 'GoalProgressUpdated',
    
    # Population events
    'PopulationChanged',
    
    # POI events
    'POIStateChanged',
    
    # Faction events
    'FactionChanged',
    
    # Quest events
    'QuestUpdated',
    
    # Combat events
    'CombatEvent', 'CombatStarted', 'CombatEnded',
    
    # Time events
    'TimeAdvanced',
    
    # Storage events
    'StorageEvent', 'GameSaved', 'GameLoaded',
    
    # System events
    'EventLogged',
    
    # Legacy event types (for backward compatibility)
    'SystemEvent', 'SystemEventType',
    'MemoryEvent', 'MemoryEventType',
    'RumorEvent', 'RumorEventType',
    'MotifEvent', 'MotifEventType',
    'PopulationEvent', 'PopulationEventType',
    'POIEvent', 'POIEventType',
    'FactionEvent', 'FactionEventType',
    'QuestEvent', 'QuestEventType',
    'CombatEventType',
    'TimeEvent', 'TimeEventType',
    'RelationshipEvent', 'RelationshipEventType',
    'StorageEventType',
    'WorldStateEvent', 'WorldStateEventType',
    
    # Middleware
    'logging_middleware',
    'error_handling_middleware',
    'analytics_middleware',
    'debug_middleware',
    
    # Utilities
    'EventManager',
]

# Backward compatibility for old import paths
import sys
sys.modules['backend.systems.event.event_dispatcher'] = sys.modules['backend.systems.events.event_dispatcher']
sys.modules['backend.systems.event.canonical_events'] = sys.modules['backend.systems.events.canonical_events']
