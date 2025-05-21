"""
Region System Utilities

This module provides re-exports of region utility functions from specialized modules.
"""

# Re-export from worldgen.py
from backend.systems.region.worldgen import (
    WorldGenerator,
    attempt_rest
)

# Re-export from tension.py
from backend.systems.region.tension import (
    TensionManager,
    simulate_revolt_in_poi,
    decay_region_tension,
    check_faction_war_triggers,
    get_regions_by_tension,
    get_region_factions_at_war
)

# Re-export from mapping.py
from backend.systems.region.mapping import (
    map_region_to_latlon,
    fetch_weather_for_latlon
)

__all__ = [
    # From worldgen.py
    'WorldGenerator',
    'attempt_rest',
    
    # From tension.py
    'TensionManager',
    'simulate_revolt_in_poi',
    'decay_region_tension',
    'check_faction_war_triggers',
    'get_regions_by_tension',
    'get_region_factions_at_war',
    
    # From mapping.py
    'map_region_to_latlon',
    'fetch_weather_for_latlon',
] 