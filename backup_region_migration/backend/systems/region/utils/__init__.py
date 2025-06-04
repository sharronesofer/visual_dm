"""
Region System Utilities - Business Logic

Game mechanics and business logic utilities for the region system.
Technical mapping utilities have been moved to backend.infrastructure.region.utils
"""

# Business logic utilities
from .tension import *
from .worldgen import *

__all__ = [
    # Tension management (game mechanics)
    'TensionManager',
    'TensionConfig',
    'decay_region_tension',
    'check_faction_war_triggers',
    'get_regions_by_tension',
    'get_region_factions_at_war',
    'simulate_revolt_in_poi',
    
    # World generation (business rules)
    'EnhancedWorldGenerator',
    'BiomeConfig',
    'ContinentGenerationConfig',
    'WorldGenerationResult',
    'validate_biome_adjacency',
    'generate_continent_with_validation',
    'attempt_rest'
]
