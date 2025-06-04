"""
Region System Package

This package provides geographical and territorial management for the Visual DM system.
Fixed: Removed references to moved utilities (worldgen -> world_generation, tension -> tension system).
"""

from .models import (
    RegionMetadata,
    ContinentMetadata,
    RegionProfile,
    CreateRegionRequest,
    UpdateRegionRequest,
    RegionResponse,
    RegionType,
    BiomeType,
    ClimateType,
    DangerLevel,
    POIType,
    HexCoordinate,
    ResourceNode
)

from .services.services import (
    RegionService,
    ContinentService,
    create_region_service,
    create_continent_service
)

from .services.event_service import (
    RegionEventService,
    create_region_event_service
)

# Note: World generation utilities have been moved to backend.world_generation
# Note: Tension management has been moved to backend.systems.tension

__version__ = "1.0.0"

__all__ = [
    # Models
    "RegionMetadata",
    "ContinentMetadata", 
    "RegionProfile",
    "CreateRegionRequest",
    "UpdateRegionRequest",
    "RegionResponse",
    "RegionType",
    "BiomeType",
    "ClimateType",
    "DangerLevel",
    "POIType",
    "HexCoordinate",
    "ResourceNode",
    
    # Services
    "RegionService",
    "ContinentService",
    "create_region_service",
    "create_continent_service",
    "RegionEventService",
    "create_region_event_service"
]
