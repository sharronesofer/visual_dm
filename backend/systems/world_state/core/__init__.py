"""
Core functionality for the World State system.

This module contains the fundamental components that power the world state
management, including the manager, loader, and type definitions.
"""

from backend.systems.world_state.manager import WorldStateManager
from backend.systems.world_state.loader import WorldStateLoader
from backend.systems.world_state.events import WorldStateEvent
from backend.systems.world_state.types import (
    StateChangeType,
    WorldRegion,
    StateCategory,
    WorldState,
    WorldStateChange,
    WorldStateChangeCustomData,
    ActiveEffect,
    LocationType,
    ResourceType,
)

__all__ = [
    # Classes
    'WorldStateManager',
    'WorldStateLoader',
    'WorldStateEvent',
    
    # Types and enums
    'StateChangeType',
    'WorldRegion',
    'StateCategory',
    'WorldState',
    'WorldStateChange',
    'WorldStateChangeCustomData',
    'ActiveEffect',
    'LocationType',
    'ResourceType',
] 