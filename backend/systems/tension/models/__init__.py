"""
Tension System Domain Models

This module contains the domain models and data structures for the tension system
following Development Bible standards for pure business logic separation.
"""

from .tension_state import (
    TensionState,
    TensionModifier,
    TensionConfig,
    ConflictTrigger,
    RevoltConfig,
    CalculationConstants
)

from .tension_events import (
    TensionEvent,
    TensionEventType,
    TensionEventBuilder,
    TensionEventFilter,
    EventSeverity,
    # Factory functions
    create_player_combat_event,
    create_npc_death_event,
    create_environmental_disaster_event,
    create_political_change_event,
    create_festival_event
)

__all__ = [
    'TensionState',
    'TensionModifier', 
    'TensionConfig',
    'ConflictTrigger',
    'RevoltConfig',
    'CalculationConstants',
    'TensionEvent',
    'TensionEventType',
    "TensionEventBuilder",
    "TensionEventFilter",
    "EventSeverity",
    "create_player_combat_event",
    "create_npc_death_event",
    "create_environmental_disaster_event",
    "create_political_change_event",
    "create_festival_event"
] 