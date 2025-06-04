"""
World Generation Utilities

Utilities for world generation operations, including coordinate conversion,
region calculations, and configuration management.
"""

import random
import math
from typing import List, Tuple, Set, Optional, Dict, Any, Union
from uuid import uuid4
from datetime import datetime
from collections import deque
from dataclasses import dataclass

from backend.systems.world_generation.models import CoordinateSchema
from backend.systems.region.models import HexCoordinate, BiomeType, ClimateType, ResourceType
from backend.infrastructure.world_generation_config import GenerationConfigManager
from backend.systems.world_generation.config.population_config import (
    POPULATION_CONFIG,
    SETTLEMENT_TYPES,
    BIOME_HABITABILITY,
    TERRAIN_MOVEMENT_COSTS,
    REGION_AREA_KM2,
    get_poi_population_range,
    calculate_region_population_target,
    get_settlement_type_by_population,
    calculate_npc_distribution_for_poi
)

# Initialize configuration manager
_config_manager = GenerationConfigManager()

# Configuration-driven constants (replacing hardcoded values)
def get_total_region_tiles():
    return _config_manager.get_total_region_tiles()

def get_settlements_per_region():
    return _config_manager.get_settlements_per_region()

def get_non_settlement_pois_per_region():
    return _config_manager.get_non_settlement_pois_per_region()

def get_poi_type_weights():
    return _config_manager.get_poi_type_weights()

def get_forbidden_terrains():
    return _config_manager.get_forbidden_terrains()

def get_less_likely_terrains():
    return _config_manager.get_less_likely_terrains()

def get_less_likely_chance():
    return _config_manager.get_less_likely_chance()

def get_settlement_min_spacing():
    return _config_manager.get_settlement_min_spacing()

def get_non_settlement_min_spacing():
    return _config_manager.get_non_settlement_min_spacing()

def get_region_population_range():
    return _config_manager.get_region_population_range()

def get_settlement_population_range():
    return _config_manager.get_settlement_population_range()

def get_metropolis_population_range():
    return _config_manager.get_metropolis_population_range()

def get_metropolis_types():
    return _config_manager.get_metropolis_type_names()

# Canonical Sizes & Constants

# Continental coordinates and sizing
CONTINENT_MIN_REGIONS = _config_manager.get_continent_min_regions()
CONTINENT_MAX_REGIONS = _config_manager.get_continent_max_regions()

# Coordinate mapping constants
ORIGIN_LATITUDE = _config_manager.get_origin_latitude()
ORIGIN_LONGITUDE = _config_manager.get_origin_longitude()
REGION_LATLON_SCALE_DEGREES = _config_manager.get_region_latlon_scale()

# Region Hex Dimensions
REGION_HEXES_PER_REGION = _config_manager.get_region_hexes_per_region()
REGION_HEX_FLAT_TO_FLAT = 4144  # feet
POI_HEX_SIZE_FEET = 5  # feet
REGION_POPULATION_RANGE = POPULATION_CONFIG.REGION_TOTAL_POPULATION_RANGE  # (2000, 5000) instead of (200, 400)
METROPOLIS_POPULATION_RANGE = POPULATION_CONFIG.METROPOLIS_TOTAL_POPULATION_RANGE  # (5000, 15000) instead of (200, 500)
SETTLEMENTS_PER_REGION = POPULATION_CONFIG.SETTLEMENTS_PER_REGION  # 12 instead of 7
NON_SETTLEMENT_POIS_PER_REGION = POPULATION_CONFIG.NON_SETTLEMENT_POIS_PER_REGION  # 25 instead of 14
TOTAL_POIS_PER_REGION = POPULATION_CONFIG.TOTAL_POIS_PER_REGION  # 37 instead of 21
POI_SPACING_HEXES = _config_manager.get_poi_spacing_hexes()  # Average spacing between POIs

# POI Placement Terrain Constraints
FORBIDDEN_TERRAINS = set(get_forbidden_terrains())
LESS_LIKELY_TERRAINS = set(get_less_likely_terrains())
LESS_LIKELY_CHANCE = get_less_likely_chance()  # 20% chance to allow
SETTLEMENT_MIN_POP = 20  # Reduced from 30 for hamlets
SETTLEMENT_MAX_POP = 300  # Increased from 100 for larger settlements
MAX_SETTLEMENTS = _config_manager.get_max_settlements()
NON_SETTLEMENT_MIN_SPACING = get_non_settlement_min_spacing()
SETTLEMENT_MIN_SPACING = get_settlement_min_spacing()

# Terrain Types
TERRAIN_TYPES = _config_manager.get_terrain_types()

# POI Type Weights
POI_TYPE_WEIGHTS = get_poi_type_weights()

TILE_POI_CHANCE = _config_manager.get_tile_poi_chance()
TOTAL_REGION_TILES = get_total_region_tiles()

def generate_continent_region_coordinates(num_regions_target: int) -> List[CoordinateSchema]:
    """
    Generates a list of unique region coordinates for a continent using a random walk.
    Ensures the continent is contiguous.
    
    Args:
        num_regions_target: The target number of regions to generate
        
    Returns:
        List of CoordinateSchema objects representing region coordinates
    """
    if not (CONTINENT_MIN_REGIONS <= num_regions_target <= CONTINENT_MAX_REGIONS):
        num_regions_target = random.randint(CONTINENT_MIN_REGIONS, CONTINENT_MAX_REGIONS)

    coordinates: Set[Tuple[int, int]] = set()
    # Start at origin (0,0) for the first region of the continent
    current_coord = (0, 0)
    coordinates.add(current_coord)
    
    # Keep track of potential next steps from all existing coordinates to ensure contiguity
    frontier: List[Tuple[int, int]] = [current_coord]

    while len(coordinates) < num_regions_target and frontier:
        # Pick a random coordinate from the frontier to expand from
        current_coord_tuple = random.choice(frontier)
        
        possible_next_steps = [
            (current_coord_tuple[0] + 1, current_coord_tuple[1]),
            (current_coord_tuple[0] - 1, current_coord_tuple[1]),
            (current_coord_tuple[0], current_coord_tuple[1] + 1),
            (current_coord_tuple[0], current_coord_tuple[1] - 1),
            # Hex grid neighbors (simplified to cardinal for now, can be expanded for true hex)
            # (current_coord_tuple[0] + 1, current_coord_tuple[1] - 1),  # Example hex neighbor
            # (current_coord_tuple[0] - 1, current_coord_tuple[1] + 1),  # Example hex neighbor
        ]
        random.shuffle(possible_next_steps)

        added_new = False
        for next_coord_tuple in possible_next_steps:
            if next_coord_tuple not in coordinates:
                coordinates.add(next_coord_tuple)
                frontier.append(next_coord_tuple)
                added_new = True
                if len(coordinates) >= num_regions_target:
                    break
        
        if not added_new:
            # If no new coordinate was added from this frontier point (e.g., surrounded), remove it
            frontier.remove(current_coord_tuple)
        
        if len(coordinates) >= num_regions_target:
            break
            
    # If the frontier is exhausted before reaching target, it means we couldn't expand further contiguously with this method.
    # This is a simplified random walk; more sophisticated algorithms might be needed for complex shapes or guarantees.

    return [CoordinateSchema(x=x, y=y) for x, y in coordinates]

def map_region_to_latlon(region_coord: CoordinateSchema) -> Tuple[float, float]:
    """
    Maps region grid coordinates to real-world latitude and longitude.
    
    Args:
        region_coord: Region coordinates to map
        
    Returns:
        Tuple of (latitude, longitude)
    """
    latitude = ORIGIN_LATITUDE + (region_coord.y * REGION_LATLON_SCALE_DEGREES)
    longitude = ORIGIN_LONGITUDE + (region_coord.x * REGION_LATLON_SCALE_DEGREES)
    return latitude, longitude

def get_region_latlon(region_x: int, region_y: int) -> Tuple[float, float]:
    """
    Alias for map_region_to_latlon using raw coordinates.
    
    Args:
        region_x: Region x coordinate
        region_y: Region y coordinate
        
    Returns:
        Tuple of (latitude, longitude)
    """
    return map_region_to_latlon(CoordinateSchema(x=region_x, y=region_y))

def get_continent_boundary(region_coords: List[CoordinateSchema]) -> Optional[Tuple[int, int, int, int]]:
    """
    Calculates the rectangular boundary of a continent from its region coordinates.
    
    Args:
        region_coords: List of region coordinates
        
    Returns:
        Tuple of (min_x, max_x, min_y, max_y) or None if empty
    """
    if not region_coords:
        return None
    min_x = min(rc.x for rc in region_coords)
    max_x = max(rc.x for rc in region_coords)
    min_y = min(rc.y for rc in region_coords)
    max_y = max(rc.y for rc in region_coords)
    return min_x, max_x, min_y, max_y

def fetch_weather_for_region(region_coord: Union[CoordinateSchema, Tuple[int, int]]) -> Dict[str, Any]:
    """
    Fetches weather data for a region based on its real-world latitude and longitude.
    
    Args:
        region_coord: Region coordinates (CoordinateSchema or Tuple)
        
    Returns:
        Dictionary with weather data
    """
    if isinstance(region_coord, tuple):
        lat, lon = get_region_latlon(region_coord[0], region_coord[1])
    else:
        lat, lon = map_region_to_latlon(region_coord)
    return fetch_weather_for_latlon(lat, lon)

def fetch_weather_for_latlon(latitude: float, longitude: float) -> Dict[str, Any]:
    """
    Placeholder for fetching weather from an external API like OpenWeatherMap.
    Actual implementation would use libraries like `requests`.
    
    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate
        
    Returns:
        Dictionary with weather data
    """
    # Simulate API call
    print(f"Simulating weather fetch for Lat: {latitude}, Lon: {longitude}")
    # In a real scenario, you'd make an HTTP request here
    # For now, return mock data
    temp_celsius = random.uniform(5, 25)
    conditions = random.choice(["Sunny", "Cloudy", "Rainy", "Windy"])
    return {
        "temperature_celsius": round(temp_celsius, 1),
        "conditions": conditions,
        "humidity_percent": random.randint(30, 90),
        "wind_kph": random.uniform(0, 30)
    }

# --- Region Generation Functions ---

def walk_region(seed_x: int, seed_y: int, target_count: int = TOTAL_REGION_TILES) -> Dict[str, Dict[str, Any]]:
    """
    Generate a region tilemap using a random walk algorithm.
    
    Args:
        seed_x: Starting X coordinate
        seed_y: Starting Y coordinate
        target_count: Target number of tiles to generate
        
    Returns:
        Dictionary of tiles keyed by coordinate string
    """
    tiles = {}
    visited = set()
    queue = deque([(seed_x, seed_y)])
    
    while queue and len(tiles) < target_count:
        x, y = queue.popleft()
        if (x, y) in visited:
            continue
        
        visited.add((x, y))
        coord_key = f"{x}_{y}"
        
        # Generate terrain data for this tile
        terrain = random.choice(TERRAIN_TYPES)
        danger = min(10, max(1, int(abs(x) + abs(y)) // 10 + random.randint(-1, 1)))
        
        tiles[coord_key] = {
            "x": x,
            "y": y,
            "terrain": terrain,
            "danger_level": danger,
            "original_danger_level": danger,  # Keep original for resets
            "explored": False,
            "poi_type": None,  # Will be set during POI placement
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Add neighbors to queue
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        random.shuffle(directions)
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if (nx, ny) not in visited:
                queue.append((nx, ny))
                
    return tiles

def pick_poi_type() -> str:
    """
    Select a POI type based on predefined weights.
    
    Returns:
        POI type string
    """
    return random.choices(
        list(POI_TYPE_WEIGHTS.keys()),
        weights=list(POI_TYPE_WEIGHTS.values()),
        k=1
    )[0]

def choose_poi_type(tile_danger: int) -> str:
    """
    Biases POI type based on tile danger level.
    
    Args:
        tile_danger: Danger level of the tile (1-10)
        
    Returns:
        'social', 'exploration', or 'dungeon'
    """
    if tile_danger <= 2:
        weights = {"social": 0.7, "exploration": 0.25, "dungeon": 0.05}
    elif tile_danger <= 6:
        weights = {"social": 0.2, "exploration": 0.6, "dungeon": 0.2}
    else:
        weights = {"social": 0.1, "exploration": 0.2, "dungeon": 0.7}

    return random.choices(list(weights.keys()), list(weights.values()))[0]

def pick_valid_tile(tiles: Dict[str, Dict[str, Any]], 
                   placed_pois: List[Tuple[int, int]], 
                   min_spacing: int, 
                   forbidden_terrains: Optional[Set[str]] = None, 
                   less_likely_terrains: Optional[Set[str]] = None, 
                   less_likely_chance: float = 1.0) -> Optional[Tuple[int, int]]:
    """
    Pick a valid tile for POI placement based on spacing and terrain constraints.
    
    Args:
        tiles: Dictionary of tiles keyed by coordinate string
        placed_pois: List of already placed POI coordinates
        min_spacing: Minimum spacing between POIs
        forbidden_terrains: Set of terrain types that cannot have POIs
        less_likely_terrains: Set of terrain types less likely to have POIs
        less_likely_chance: Chance (0-1) to allow POI on less likely terrain
        
    Returns:
        Tuple of (x, y) for valid tile or None if no valid tile found
    """
    attempts = 0
    max_attempts = 1000
    if forbidden_terrains is None:
        forbidden_terrains = FORBIDDEN_TERRAINS
    if less_likely_terrains is None:
        less_likely_terrains = LESS_LIKELY_TERRAINS
        
    while attempts < max_attempts:
        coord_key = random.choice(list(tiles.keys()))
        x, y = map(int, coord_key.split('_'))
        terrain = tiles[coord_key]["terrain"]
        
        # Terrain check
        if terrain in forbidden_terrains:
            attempts += 1
            continue
        if terrain in less_likely_terrains and random.random() > less_likely_chance:
            attempts += 1
            continue
            
        # Spacing check
        if all(abs(x - px) + abs(y - py) >= min_spacing for (px, py) in placed_pois):
            return (x, y)
        attempts += 1
    return None  # fallback if no valid tile found

def pick_social_size(population: int) -> str:
    """
    Determine the size category of a social POI based on population using revolutionary NPC system.
    
    Args:
        population: Population count of the POI
        
    Returns:
        Size category string: 'hamlet', 'village', 'town', 'city', or 'metropolis'
    """
    return get_settlement_type_by_population(population)

def claim_region_hexes_for_city(region_data: Dict[str, Any], 
                              city_tile: Tuple[int, int], 
                              is_metropolis: bool = False) -> List[str]:
    """
    Mark region hexes as claimed by a city/metropolis. For metropolises, claim 2-3 adjacent hexes if available.
    
    Args:
        region_data: Region data dictionary with tiles
        city_tile: Tuple of (x, y) for the city
        is_metropolis: Whether this is a metropolis (claims more hexes)
        
    Returns:
        List of claimed hex coordinates as strings
    """
    x, y = city_tile
    coord_key = f"{x}_{y}"
    claimed_hexes = [coord_key]
    region_data["tiles"][coord_key]["claimed_by_city"] = coord_key
    
    if is_metropolis:
        # Try to claim 1-2 adjacent hexes for visual sprawl
        directions = [(-1,0), (1,0), (0,-1), (0,1), (-1,1), (1,-1)]
        random.shuffle(directions)
        for dx, dy in directions:
            nx, ny = x+dx, y+dy
            nkey = f"{nx}_{ny}"
            if nkey in region_data["tiles"] and "claimed_by_city" not in region_data["tiles"][nkey]:
                region_data["tiles"][nkey]["claimed_by_city"] = coord_key
                claimed_hexes.append(nkey)
                if len(claimed_hexes) >= 3:
                    break
                    
    # Store claimed hexes in the city/metropolis POI data
    region_data["tiles"][coord_key]["region_hexes"] = claimed_hexes
    return claimed_hexes

def generate_settlements(region_data: Dict[str, Any], 
                        tiles: Dict[str, Dict[str, Any]], 
                        total_population: int, 
                        min_spacing: int = SETTLEMENT_MIN_SPACING, 
                        max_settlements: int = MAX_SETTLEMENTS) -> Tuple[List[Tuple[int, int]], int]:
    """
    Generate settlements (social POIs) for a region using the revolutionary NPC system.
    
    Creates a mix of hamlet, village, town, city, and metropolis settlements based on
    population distribution and tier-based NPC management.
    
    Args:
        region_data: Region data dictionary with tiles
        tiles: Dictionary of tiles keyed by coordinate string
        total_population: Total population to distribute across settlements
        min_spacing: Minimum spacing between settlements
        max_settlements: Maximum number of settlements (now uses new config)
        
    Returns:
        Tuple of (list of settlement coordinates, remaining population)
    """
    settlements = []
    remaining_npcs = total_population
    
    # Calculate settlement type distribution for this region
    settlement_distribution = POPULATION_CONFIG.SETTLEMENT_TYPE_DISTRIBUTION
    
    # Create settlements in order of size (largest first to ensure they get good spots)
    settlement_types_ordered = ['metropolis', 'city', 'town', 'village', 'hamlet']
    
    for settlement_type in settlement_types_ordered:
        if remaining_npcs <= 0:
            break
            
        # Calculate how many of this type to create
        target_ratio = settlement_distribution[settlement_type]
        target_count = max(1, int(SETTLEMENTS_PER_REGION * target_ratio))
        
        # Get population range for this settlement type
        min_pop, max_pop = POPULATION_CONFIG.SETTLEMENT_POPULATION_RANGES[settlement_type]
        
        for _ in range(target_count):
            if remaining_npcs < min_pop or len(settlements) >= max_settlements:
                break
                
            # Calculate population for this settlement
            available_pop = min(remaining_npcs, max_pop)
            if available_pop < min_pop:
                break
                
            # For larger settlements, use more population
            if settlement_type in ['metropolis', 'city']:
                pop = random.randint(max(min_pop, available_pop // 2), available_pop)
            else:
                pop = random.randint(min_pop, min(max_pop, available_pop))
            
            # Find a valid location
            tile = pick_valid_tile(
                tiles, settlements, min_spacing,
                forbidden_terrains=FORBIDDEN_TERRAINS,
                less_likely_terrains=LESS_LIKELY_TERRAINS,
                less_likely_chance=LESS_LIKELY_CHANCE
            )
            if tile is None:
                break
                
            settlements.append(tile)
            coord_key = f"{tile[0]}_{tile[1]}"
            
            # Set POI data with tier distribution
            region_data["tiles"][coord_key]["poi_type"] = "social"
            region_data["tiles"][coord_key]["population"] = pop
            region_data["tiles"][coord_key]["size"] = settlement_type
            region_data["tiles"][coord_key]["settlement_type"] = settlement_type
            
            # Add NPC tier distribution data
            tier_distribution = calculate_npc_distribution_for_poi(pop, settlement_type)
            region_data["tiles"][coord_key]["npc_tier_distribution"] = tier_distribution
            
            remaining_npcs -= pop
    
    return settlements, remaining_npcs

def generate_non_settlement_pois(region_data: Dict[str, Any], 
                               tiles: Dict[str, Dict[str, Any]], 
                               placed_pois: List[Tuple[int, int]], 
                               num_pois: int, 
                               min_spacing: int = NON_SETTLEMENT_MIN_SPACING) -> List[Tuple[int, int]]:
    """
    Generate non-settlement POIs (dungeons, exploration sites) for a region using revolutionary NPC system.
    
    Creates a mix of different POI types with appropriate populations and NPC tier distributions.
    
    Args:
        region_data: Region data dictionary with tiles
        tiles: Dictionary of tiles keyed by coordinate string
        placed_pois: List of already placed POI coordinates
        num_pois: Number of POIs to place
        min_spacing: Minimum spacing between POIs
        
    Returns:
        List of non-settlement POI coordinates
    """
    pois = []
    attempts = 0
    max_attempts = 10000
    
    # Get POI type distribution
    poi_distribution = POPULATION_CONFIG.NON_SETTLEMENT_TYPE_DISTRIBUTION
    poi_types = list(poi_distribution.keys())
    poi_weights = list(poi_distribution.values())
    
    while len(pois) < num_pois and attempts < max_attempts:
        tile = pick_valid_tile(tiles, placed_pois + pois, min_spacing)
        if tile is not None:
            pois.append(tile)
            coord_key = f"{tile[0]}_{tile[1]}"
            
            # Select POI type based on distribution weights
            poi_type = random.choices(poi_types, weights=poi_weights)[0]
            
            # Determine POI type based on tile danger level (keeping existing logic)
            tile_danger = tiles[coord_key].get("danger_level", 5)
            if tile_danger > 7:
                # High danger areas favor dungeons and ruins
                poi_type = random.choices(['dungeon', 'ruins', 'wilderness'], weights=[0.5, 0.3, 0.2])[0]
            elif tile_danger < 3:
                # Low danger areas favor temples and settlements
                poi_type = random.choices(['temple', 'mine', 'exploration'], weights=[0.4, 0.4, 0.2])[0]
            
            # Get population for this POI type
            min_pop, max_pop = get_poi_population_range(poi_type)
            population = random.randint(min_pop, max_pop)
            
            # Set POI data
            region_data["tiles"][coord_key]["poi_type"] = poi_type
            region_data["tiles"][coord_key]["population"] = population
            region_data["tiles"][coord_key]["size"] = _determine_poi_size(population, poi_type)
            
            # Add NPC tier distribution data
            if population > 0:
                tier_distribution = calculate_npc_distribution_for_poi(population, poi_type)
                region_data["tiles"][coord_key]["npc_tier_distribution"] = tier_distribution
            
        attempts += 1
        
    return pois

def _determine_poi_size(population: int, poi_type: str) -> str:
    """Determine size category for non-settlement POIs based on population and type."""
    if poi_type == 'fortress':
        if population >= 500:
            return 'major'
        elif population >= 200:
            return 'standard'
        else:
            return 'minor'
    elif poi_type == 'mine':
        if population >= 100:
            return 'major'
        elif population >= 50:
            return 'standard'
        else:
            return 'minor'
    elif poi_type == 'temple':
        if population >= 60:
            return 'cathedral'
        elif population >= 30:
            return 'temple'
        else:
            return 'shrine'
    elif poi_type == 'dungeon':
        if population >= 30:
            return 'major'
        elif population >= 15:
            return 'standard'
        else:
            return 'minor'
    else:
        # Default size categories
        if population >= 20:
            return 'major'
        elif population >= 10:
            return 'standard'
        else:
            return 'minor'

def generate_region(seed_x: int = 0, seed_y: int = 0) -> Dict[str, Any]:
    """
    Generate a new region with revolutionary NPC population system.
    
    Creates a region with proper population distribution across tiers, comprehensive
    POI generation, and metadata for the MMO-scale NPC management system.
    
    Args:
        seed_x: Starting X coordinate
        seed_y: Starting Y coordinate
        
    Returns:
        Complete region data dictionary with tier-based population data
    """
    region_id = f"region_{seed_x}_{seed_y}_{uuid4().hex[:6]}"
    print(f"🌎 Generating region: {region_id}")

    # Calculate total population for this region using new system
    total_population = calculate_region_population_target('standard')
    visible_population = int(total_population * 0.4)  # 40% of total population is visible (Tiers 1-3.5)
    
    print(f"   📊 Population: {total_population:,} total ({visible_population:,} visible)")
    
    region_data = {
        "region_id": region_id,
        "name": region_id.replace("_", " ").title(),
        "created_at": datetime.utcnow().isoformat(),
        
        # Revolutionary population data
        "total_population": total_population,
        "visible_population": visible_population,
        "statistical_population": total_population - visible_population,
        
        # Population distribution by tier (initial)
        "population_tiers": {
            "tier_1_active": 0,      # Start with 0, promoted on interaction
            "tier_2_background": int(visible_population * 0.05),  # 5% background
            "tier_3_dormant": int(visible_population * 0.10),     # 10% dormant
            "tier_3_5_compressed": int(visible_population * 0.85), # 85% compressed
            "tier_4_statistical": total_population - visible_population
        },
        
        # World structure
        "tiles": {},
        "poi_list": [],
        "poi_count": 0,
        "settlement_count": 0,
        
        # Gameplay data
        "tension_level": random.randint(0, 20),
        "faction_count": random.randint(2, 4),
        "motif_pool": [],  # Will be populated by the motif system
        "memory": [],  # Placeholder for region memory (major events)
        "arc": None,  # Placeholder for arc (meta-quest)
        "metropolis_type": None,  # Set during POI generation
        
        # Geographic data
        "coordinates": {
            "x": seed_x,
            "y": seed_y
        },
        
        # Revolutionary NPC system metadata
        "npc_system": {
            "tier_management_enabled": True,
            "last_tier_update": datetime.utcnow().isoformat(),
            "active_player_count": 0,
            "computational_load": 0.0,
            "memory_usage_mb": 0.0
        }
    }

    # Generate natural tilemap
    region_data["tiles"] = walk_region(seed_x, seed_y, TOTAL_REGION_TILES)
    
    # Generate settlements with new population system
    settlements, remaining_settlement_pop = generate_settlements(
        region_data, 
        region_data["tiles"], 
        visible_population  # Use visible population for settlement generation
    )
    
    print(f"   🏘️  Generated {len(settlements)} settlements")
    
    # Find the largest settlement to mark as metropolis
    metropolis_tile = None
    metropolis_type = None
    
    if settlements:
        # Find the largest settlement
        largest_pop = 0
        for tile in settlements:
            coord_key = f"{tile[0]}_{tile[1]}"
            pop = region_data["tiles"][coord_key].get("population", 0)
            if pop > largest_pop:
                largest_pop = pop
                metropolis_tile = tile
        
        # Mark the metropolis if it's large enough
        if metropolis_tile and largest_pop >= 1000:  # Reduced threshold for metropolis
            coord_key = f"{metropolis_tile[0]}_{metropolis_tile[1]}"
            region_data["tiles"][coord_key]["is_metropolis"] = True
            metropolis_type = random.choice(["Arcane", "Industrial", "Sacred", "Ruined", "Natural"])
            region_data["tiles"][coord_key]["metropolis_type"] = metropolis_type
            region_data["metropolis_type"] = metropolis_type
            
            # Claim extra hexes for metropolis sprawl
            claimed_hexes = claim_region_hexes_for_city(region_data, metropolis_tile, is_metropolis=True)
            region_data["tiles"][coord_key]["region_hexes"] = claimed_hexes
            
            print(f"   🏙️  Metropolis: {metropolis_type} ({largest_pop:,} NPCs)")
            
            # Log the creation of a metropolis for narrative purposes
            log_event = {
                "type": "metropolis_assigned",
                "location": coord_key,
                "metropolis_type": metropolis_type,
                "population": largest_pop,
                "region_id": region_id,
                "timestamp": datetime.utcnow().isoformat()
            }
            region_data["memory"].append(log_event)
    
    # Generate non-settlement POIs
    non_settlement_pois = generate_non_settlement_pois(
        region_data, 
        region_data["tiles"], 
        settlements, 
        NON_SETTLEMENT_POIS_PER_REGION
    )
    
    print(f"   🗺️  Generated {len(non_settlement_pois)} non-settlement POIs")
    
    # Combine all POIs and store in region data
    all_pois = settlements + non_settlement_pois
    region_data["poi_list"] = [f"{poi[0]}_{poi[1]}" for poi in all_pois]
    region_data["poi_count"] = len(all_pois)
    region_data["settlement_count"] = len(settlements)
    
    # Calculate actual population distribution across all POIs
    actual_total_pop = 0
    settlement_pop = 0
    non_settlement_pop = 0
    
    for poi_coord in all_pois:
        coord_key = f"{poi_coord[0]}_{poi_coord[1]}"
        poi_pop = region_data["tiles"][coord_key].get("population", 0)
        actual_total_pop += poi_pop
        
        if region_data["tiles"][coord_key].get("poi_type") == "social":
            settlement_pop += poi_pop
        else:
            non_settlement_pop += poi_pop
    
    # Update region metadata with actual populations
    region_data["actual_population_breakdown"] = {
        "total_in_pois": actual_total_pop,
        "settlement_population": settlement_pop,
        "non_settlement_population": non_settlement_pop,
        "population_density_per_poi": actual_total_pop / max(1, len(all_pois))
    }
    
    print(f"   📈 Population breakdown: {settlement_pop:,} in settlements, {non_settlement_pop:,} in other POIs")
    print(f"   ✅ Region generation complete: {len(all_pois)} POIs, {actual_total_pop:,} NPCs")
    
    return region_data

def log_region_event(region_id: str, event_type: str, details: Dict[str, Any]) -> Dict[str, Any]:
    """
    Log an event in a region's memory.
    
    Args:
        region_id: ID of the region
        event_type: Type of event
        details: Event details
        
    Returns:
        The created event object
    """
    event = {
        "type": event_type,
        "details": details,
        "timestamp": datetime.utcnow().isoformat(),
        "event_id": str(uuid4())
    }
    
    # In a real implementation, you'd store this event
    # region_ref = db.reference(f"/regions/{region_id}/memory")
    # region_ref.push(event)
    
    return event

# --- Monster Generation and POI Management Functions ---

def refresh_cleared_pois() -> int:
    """
    Scans all POIs in all regions and resets those marked as 'cleared': true.
    
    Returns:
        Number of POIs refreshed
    """
    # This is a mock implementation since we can't access the database directly
    # In a real implementation, you'd use the database reference
    # root = db.reference("/poi_state")
    # all_regions = root.get() or {}
    
    # For demonstration purposes only:
    print("Refreshing cleared POIs (mock implementation)")
    return 0  # Return the count of refreshed POIs

def generate_monsters_for_tile(region: str, tile_id: str, party_cr: float = 5.0) -> List[Dict[str, Any]]:
    """
    Combines tile danger, regional tension, and party CR to generate appropriate monsters.
    
    Args:
        region: Region identifier
        tile_id: Tile identifier
        party_cr: Challenge rating of the party
        
    Returns:
        List of monster data dictionaries
    """
    # This is a mock implementation since we can't access the database directly
    # In a real implementation, you'd fetch tile data, region data, and monster data
    
    # Example implementation logic:
    # 1. Fetch tile danger level
    # 2. Fetch region tension
    # 3. Calculate appropriate CR range based on danger, tension, and party_cr
    # 4. Select monsters within that CR range
    
    # For demonstration purposes only:
    print(f"Generating monsters for tile {tile_id} in region {region}, party CR: {party_cr}")
    
    # Generate some sample monsters
    sample_monsters = [
        {
            "id": f"monster_{uuid4().hex[:8]}",
            "name": f"Monster {i}",
            "challenge_rating": max(0, min(10, party_cr + random.uniform(-1.5, 1.5))),
            "hp": random.randint(10, 100),
            "armor_class": random.randint(10, 18)
        }
        for i in range(3)
    ]
    
    return sample_monsters

def attempt_rest(region_name: str, poi_id: str, character: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Resolves a long rest attempt at the given POI.
    Rotates motifs, clears status effects, and resets cooldowns if safe.
    
    Args:
        region_name: Region identifier
        poi_id: POI identifier
        character: Character data dictionary (optional)
        
    Returns:
        Dictionary with rest result information
    """
    # This is a mock implementation since we can't access the database directly
    
    # For demonstration purposes only:
    print(f"Attempting rest at POI {poi_id} in region {region_name}")
    
    # Example result
    result = {
        "region": region_name,
        "poi": poi_id,
        "rest_successful": True,
        "character": character["id"] if character and "id" in character else None
    }
    
    return result

def generate_social_poi(region_id: str, x: int, y: int, size: str = "village") -> str:
    """
    Generates a social POI (city, town, etc.) at the specified coordinates.
    
    Args:
        region_id: Region identifier
        x: X coordinate
        y: Y coordinate
        size: Size category of the POI
        
    Returns:
        POI identifier
    """
    # This is a mock implementation since we can't access the database directly
    
    # For demonstration purposes only:
    poi_id = f"poi_{x}_{y}_{uuid4().hex[:6]}"
    print(f"Generating social POI {poi_id} in region {region_id} at ({x}, {y}), size: {size}")
    
    return poi_id

def generate_tile(x: int, y: int, region_id: str) -> Dict[str, Any]:
    """
    Generates a new tile at (x, y) based on neighboring tiles.
    Picks from neighbor terrain types if available, otherwise random.
    
    Args:
        x: X coordinate
        y: Y coordinate
        region_id: Region identifier
        
    Returns:
        Dictionary with tile information
    """
    # This is a mock implementation since we can't access the database directly
    
    # For demonstration purposes only:
    terrain = random.choice(TERRAIN_TYPES)
    coord_str = f"{x}_{y}"
    print(f"Generating tile at {coord_str} in region {region_id}, terrain: {terrain}")
    
    return {
        "message": f"Tile {coord_str} generated.",
        "terrain": terrain,
        "region": region_id,
        "coord_str": coord_str
    } 