"""
World State System

Event-driven world state management system responsible for tracking and
modifying the game world state. Provides interfaces for updating state variables,
handling state-related events, and integrating with game mods.

Core components:
- WorldStateManager: Central manager for all world state operations
- WorldStateLoader: Handles loading and persistence of world state data
- ModSynchronizer: Handles synchronization between game mods and world state
- Event handlers: Manage reactions to world state changes
"""

# Export core components
from backend.systems.world_state.core.manager import WorldStateManager
from backend.systems.world_state.core.loader import WorldStateLoader
from backend.systems.world_state.core.types import (
    WorldState, StateChangeType, WorldRegion, StateCategory, 
    StateVariable, StateChangeRecord, ActiveEffect,
    WorldStateChange, WorldStateChangeCustomData
)
from backend.systems.world_state.core.events import (
    WorldStateEvent, WorldStateCreatedEvent, WorldStateUpdatedEvent,
    WorldStateDeletedEvent, WorldStateCalculatedEvent
)

# Export mod components
from backend.systems.world_state.mods.mod_synchronizer import ModSynchronizer

# Export event handlers
from backend.systems.world_state.events.handlers import WorldStateEventHandler

# Export API router
from backend.systems.world_state.api.router import router as world_state_router

# Export utility functions
from backend.systems.world_state.utils.world_event_utils import (
    create_world_event, inject_chaos_event, get_related_events,
    filter_events_by_category, filter_events_by_location
)
from backend.systems.world_state.utils.tick_utils import (
    validate_world_state, process_world_tick, handle_tick_events
)

# Create singleton instance for easy access
world_state_manager = WorldStateManager()

__all__ = [
    # Core
    'WorldStateManager', 'WorldStateLoader',
    'WorldState', 'StateChangeType', 'WorldRegion', 'StateCategory',
    'StateVariable', 'StateChangeRecord', 'ActiveEffect',
    'WorldStateChange', 'WorldStateChangeCustomData',
    'WorldStateEvent', 'WorldStateCreatedEvent', 'WorldStateUpdatedEvent',
    'WorldStateDeletedEvent', 'WorldStateCalculatedEvent',
    
    # Mods
    'ModSynchronizer',
    
    # Event handlers
    'WorldStateEventHandler',
    
    # API
    'world_state_router',
    
    # Utils
    'create_world_event', 'inject_chaos_event', 'get_related_events',
    'filter_events_by_category', 'filter_events_by_location',
    'validate_world_state', 'process_world_tick', 'handle_tick_events',
    
    # Singleton
    'world_state_manager'
] 