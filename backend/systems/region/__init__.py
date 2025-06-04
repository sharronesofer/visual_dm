"""
Region System Package

This package provides geographical and territorial management for the Visual DM system.
Business logic and domain models separated from infrastructure dependencies.
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
    ResourceNode,
    RegionStatus,
    RegionListResponse
)

from .services.services import (
    RegionBusinessService,
    ContinentBusinessService,
    RegionData,
    ContinentData,
    CreateRegionData,
    UpdateRegionData,
    create_region_business_service,
    create_continent_business_service
)

from .services.event_service import (
    RegionEventBusinessService,
    get_region_event_service
)

# Note: Technical services (repositories, adapters, etc.) have been moved to backend.infrastructure.systems.region
# Note: World generation utilities have been moved to backend.systems.world_generation
# Note: Tension management has been moved to backend.systems.tension

__version__ = "1.0.0"

__all__ = [
    # Domain Models
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
    "RegionStatus",
    "RegionListResponse",
    
    # Business Services
    "RegionBusinessService",
    "ContinentBusinessService",
    "RegionData",
    "ContinentData",
    "CreateRegionData",
    "UpdateRegionData",
    "create_region_business_service",
    "create_continent_business_service",
    
    # Event Services
    "RegionEventBusinessService",
    "get_region_event_service"
]
