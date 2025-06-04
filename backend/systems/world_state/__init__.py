"""
World State System - Business Logic

This module contains the core business logic for the world state system.
Technical infrastructure has been moved to backend.infrastructure.world_state.

Business Logic Components:
- Core types and enums
- Business services  
- Event handlers
- Utility functions for business operations
- Regional newspaper system
- World event utilities
- Optimized world generation
- System integrations

Technical Infrastructure (moved to backend.infrastructure.world_state):
- API endpoints and routers
- Database models and repositories
- Schema definitions
- Technical utilities (terrain generation, tick processing)
"""

# Core business logic exports - explicit imports for better clarity
from backend.systems.world_state.world_types import (
    StateChangeType,
    WorldRegion, 
    StateCategory,
    LocationType,
    ResourceType,
    ActiveEffect,
    WorldStateChangeCustomData,
    WorldStateChange,
    WorldState
)

from backend.systems.world_state.services.services import (
    WorldStateService,
    create_world_state_service
)

from backend.systems.world_state.manager import (
    WorldStateManager,
    RegionalSnapshot,
    HistoricalSummary,
    SnapshotLevel,
    WorldStateRepository
)

from backend.systems.world_state.repositories import (
    JSONFileWorldStateRepository
)

from backend.systems.world_state.events import (
    WorldStateEvent,
    WorldStateCreatedEvent,
    WorldStateUpdatedEvent,
    WorldStateDeletedEvent,
    WorldStateCalculatedEvent
)
from backend.systems.world_state.loader import WorldStateLoader

# System integrations
from backend.systems.world_state.integrations import (
    FactionWorldStateIntegration,
    create_faction_world_state_integration
)

# Enhanced utilities - explicit imports
from backend.systems.world_state.utils.newspaper_system import (
    RegionalNewspaperSystem,
    NewspaperType,
    ContentSection,
    PrintingPress,
    NewsArticle,
    NewspaperEdition,
    regional_newspaper_system
)
from backend.systems.world_state.utils.world_event_utils import (
    create_world_event,
    filter_events_by_visibility,
    format_event_for_newspaper,
    aggregate_similar_events
)
from backend.systems.world_state.utils.optimized_worldgen import (
    OptimizedWorldGenerator,
    world_generator
)

__all__ = [
    # Types and enums
    "StateChangeType",
    "WorldRegion", 
    "StateCategory",
    "LocationType",
    "ResourceType",
    "ActiveEffect",
    "WorldStateChangeCustomData",
    "WorldStateChange",
    "WorldState",
    
    # Core business logic components
    "WorldStateManager",
    "RegionalSnapshot",
    "HistoricalSummary", 
    "SnapshotLevel",
    "WorldStateRepository",
    "JSONFileWorldStateRepository",
    "WorldStateEvent",
    "WorldStateCreatedEvent",
    "WorldStateUpdatedEvent", 
    "WorldStateDeletedEvent",
    "WorldStateCalculatedEvent",
    "WorldStateLoader",
    
    # Business services
    "WorldStateService",
    "create_world_state_service",
    
    # System integrations
    "FactionWorldStateIntegration",
    "create_faction_world_state_integration",
    
    # Enhanced newspaper system
    "RegionalNewspaperSystem",
    "NewspaperType", 
    "ContentSection",
    "PrintingPress",
    "NewsArticle",
    "NewspaperEdition",
    "regional_newspaper_system",
    
    # World event utilities
    "create_world_event",
    "filter_events_by_visibility",
    "format_event_for_newspaper",
    "aggregate_similar_events",
    
    # World generation
    "OptimizedWorldGenerator",
    "world_generator",
]
