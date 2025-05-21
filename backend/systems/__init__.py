"""
Visual DM Backend Systems

This package contains the core system modules for Visual DM.
"""

from .events import (
    # Re-export core event system
    EventBase, EventDispatcher, 
    
    # Re-export event types
    SystemEvent, SystemEventType,
    MemoryEvent, MemoryEventType,
    RumorEvent, RumorEventType,
    MotifEvent, MotifEventType,
    PopulationEvent, PopulationEventType,
    FactionEvent, FactionEventType,
    QuestEvent, QuestEventType,
    CombatEvent, CombatEventType,
    
    # Re-export utilities
    EventManager,
    
    # Re-export middleware
    logging_middleware,
    error_handling_middleware,
    analytics_middleware
)

# Import other systems as needed
# from .memory import MemorySystem
# from .rumors import RumorSystem
# from .motifs import MotifSystem 