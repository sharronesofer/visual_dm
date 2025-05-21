"""
Core functionality for the World State system.

This module contains the fundamental components that power the world state
management, including the manager, loader, and type definitions.
"""

from .manager import WorldStateManager
from .loader import WorldStateLoader
from .events import WorldStateEvent
from .types import (
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