"""
Region System

This module provides functionality for managing regions in the game world.
"""

from backend.systems.region.schemas import (
    RegionSchema,
    RegionCreationSchema,
    RegionUpdateSchema,
    CoordinateSchema,
    HexCoordinateSchema
)
from backend.systems.region.repository import RegionRepository, region_repository
from backend.systems.region.service import RegionService, region_service
from backend.systems.region.router import router as region_router

# Export key utility functions from utils
from backend.systems.region.utils import (
    WorldGenerator,
    TensionManager,
    simulate_revolt_in_poi,
    map_region_to_latlon,
    fetch_weather_for_latlon
)

__all__ = [
    # Schemas
    "RegionSchema",
    "RegionCreationSchema",
    "RegionUpdateSchema",
    "CoordinateSchema",
    "HexCoordinateSchema",
    
    # Repository
    "RegionRepository",
    "region_repository",
    
    # Service
    "RegionService",
    "region_service",
    
    # Router
    "region_router",
    
    # Utils
    "WorldGenerator",
    "TensionManager",
    "simulate_revolt_in_poi",
    "map_region_to_latlon",
    "fetch_weather_for_latlon"
]
