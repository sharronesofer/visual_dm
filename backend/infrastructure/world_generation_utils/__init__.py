"""
World Generation Utilities Infrastructure

Technical utilities for world generation including coordinate mapping,
file operations, and external API calls.
"""

from .world_generation_utils import *

__all__ = [
    # Coordinate utilities
    'generate_continent_region_coordinates',
    'map_region_to_latlon',
    'get_region_latlon',
    'get_continent_boundary',
    
    # Weather utilities
    'fetch_weather_for_region',
    'fetch_weather_for_latlon',
    
    # Region generation utilities
    'walk_region',
    'generate_region',
    'generate_tile',
    
    # POI utilities
    'pick_poi_type',
    'choose_poi_type',
    'pick_valid_tile',
    'generate_settlements',
    'generate_non_settlement_pois',
    'generate_social_poi',
    
    # Population utilities
    'pick_social_size',
    'claim_region_hexes_for_city',
    
    # Game mechanics utilities
    'generate_monsters_for_tile',
    'attempt_rest',
    'log_region_event',
    'refresh_cleared_pois',
]
