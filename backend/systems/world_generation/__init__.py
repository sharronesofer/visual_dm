"""
World generation module for Visual DM.

This module contains utilities and services for generating and managing
world components such as continents, regions, cities, and POIs.
"""

from backend.systems.world_generation.world_generation_utils import (
    # Continent generation
    generate_continent_region_coordinates,
    get_continent_boundary,
    map_region_to_latlon,
    get_region_latlon,
    fetch_weather_for_region,
    fetch_weather_for_latlon,
    
    # Region generation
    generate_region,
    walk_region,
    pick_poi_type,
    choose_poi_type,
    pick_valid_tile,
    pick_social_size,
    claim_region_hexes_for_city,
    generate_settlements,
    generate_non_settlement_pois,
    log_region_event,
    
    # POI and monster management
    refresh_cleared_pois,
    generate_monsters_for_tile,
    attempt_rest,
    generate_social_poi,
    generate_tile,
    
    # Constants
    CONTINENT_MIN_REGIONS,
    CONTINENT_MAX_REGIONS,
    REGION_HEXES_PER_REGION,
    REGION_POPULATION_RANGE,
    METROPOLIS_POPULATION_RANGE,
    TERRAIN_TYPES,
    POI_TYPE_WEIGHTS
)

from backend.systems.world_generation.models import (
    CoordinateSchema,
    ContinentSchema,
    ContinentBoundarySchema,
    ContinentCreationRequestSchema
)

from backend.systems.world_generation.continent_service import continent_service
from backend.systems.world_generation.continent_repository import continent_repository

# Re-export key components to maintain backwards compatibility after refactoring
from backend.systems.world_generation.models import ContinentSchema, CoordinateSchema, ContinentBoundarySchema, ContinentCreationRequestSchema
from backend.systems.world_generation.continent_service import continent_service, ContinentService
from backend.systems.world_generation.world_generation_utils import (
    generate_continent_region_coordinates,
    map_region_to_latlon,
    get_continent_boundary,
    CONTINENT_MIN_REGIONS,
    CONTINENT_MAX_REGIONS,
    ORIGIN_LATITUDE, 
    ORIGIN_LONGITUDE,
    REGION_LATLON_SCALE_DEGREES
)
from backend.systems.world_generation.continent_repository import continent_repository, ContinentRepository
from backend.systems.world_generation.router import router as world_generation_router 