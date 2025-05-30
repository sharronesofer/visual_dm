"""
Utilities for world generation.

This module contains utility functions for generating world components such as continents,
regions, and for mapping between game coordinates and real-world coordinates.
"""
import random
import math
from typing import List, Tuple, Set, Optional, Dict, Any, Union
from uuid import uuid4
from datetime import datetime
from collections import deque

from backend.systems.world_generation.models import CoordinateSchema

# Canonical Sizes & Constants
# Using 2025 update: 50-70 regions per continent
CONTINENT_MIN_REGIONS = 50
CONTINENT_MAX_REGIONS = 70
REGION_HEXES_PER_REGION = 225  # Number of hexes in a region (for internal region detail)

# Lat/Lon Mapping Constants
ORIGIN_LATITUDE = -54.8019  # Ushuaia, Argentina (canonical world origin)
ORIGIN_LONGITUDE = -68.3030
REGION_LATLON_SCALE_DEGREES = 0.5  # Example: 1 grid unit = 0.5 degrees lat/lon

# Region Generation Constants
REGION_HEX_FLAT_TO_FLAT = 4144  # POI hexes (flat-to-flat), ~20,720 ft, ~3.93 miles
POI_HEX_SIZE_FEET = 5           # Each POI hex is 5 feet across
REGION_POPULATION_RANGE = (200, 400)  # Active NPCs per region
METROPOLIS_POPULATION_RANGE = (200, 500)  # Active NPCs in a metropolis
SETTLEMENTS_PER_REGION = 7
NON_SETTLEMENT_POIS_PER_REGION = 14
TOTAL_POIS_PER_REGION = SETTLEMENTS_PER_REGION + NON_SETTLEMENT_POIS_PER_REGION
POI_SPACING_HEXES = 463  # Average spacing between POIs

# POI Placement Terrain Constraints
FORBIDDEN_TERRAINS = {"mountain", "swamp", "tundra"}
LESS_LIKELY_TERRAINS = {"desert", "coast"}
LESS_LIKELY_CHANCE = 0.2  # 20% chance to allow
SETTLEMENT_MIN_POP = 30
SETTLEMENT_MAX_POP = 100
MAX_SETTLEMENTS = 12
NON_SETTLEMENT_MIN_SPACING = 250
SETTLEMENT_MIN_SPACING = 350

# Terrain Types
TERRAIN_TYPES = ["forest", "plains", "mountain", "swamp", "coast", "desert", "tundra"]

# POI Type Weights
POI_TYPE_WEIGHTS = {
    "social": 0.5,
    "dungeon": 0.3,
    "exploration": 0.2
}

TILE_POI_CHANCE = 0.20
TOTAL_REGION_TILES = 225

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
    Determine the size category of a social POI based on population.
    
    Args:
        population: Population count of the POI
        
    Returns:
        Size category string: 'hamlet', 'village', 'town', or 'city'
    """
    if population < 40:
        return "hamlet"
    elif population < 60:
        return "village"
    elif population < 80:
        return "town"
    else:
        return "city"

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
    Generate settlements (social POIs) for a region.
    
    Args:
        region_data: Region data dictionary with tiles
        tiles: Dictionary of tiles keyed by coordinate string
        total_population: Total population to distribute
        min_spacing: Minimum spacing between settlements
        max_settlements: Maximum number of settlements
        
    Returns:
        Tuple of (list of settlement coordinates, remaining population)
    """
    settlements = []
    remaining_npcs = total_population
    
    while remaining_npcs >= SETTLEMENT_MIN_POP and len(settlements) < max_settlements:
        pop = random.randint(SETTLEMENT_MIN_POP, min(SETTLEMENT_MAX_POP, remaining_npcs))
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
        region_data["tiles"][coord_key]["poi_type"] = "social"
        region_data["tiles"][coord_key]["population"] = pop
        region_data["tiles"][coord_key]["size"] = pick_social_size(pop)
        remaining_npcs -= pop
        
    return settlements, remaining_npcs

def generate_non_settlement_pois(region_data: Dict[str, Any], 
                               tiles: Dict[str, Dict[str, Any]], 
                               placed_pois: List[Tuple[int, int]], 
                               num_pois: int, 
                               min_spacing: int = NON_SETTLEMENT_MIN_SPACING) -> List[Tuple[int, int]]:
    """
    Generate non-settlement POIs (dungeons, exploration sites) for a region.
    
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
    
    while len(pois) < num_pois and attempts < max_attempts:
        tile = pick_valid_tile(tiles, placed_pois + pois, min_spacing)
        if tile is not None:
            pois.append(tile)
            coord_key = f"{tile[0]}_{tile[1]}"
            # Determine POI type based on tile danger level
            tile_danger = tiles[coord_key].get("danger_level", 5)
            poi_type = choose_poi_type(tile_danger)
            region_data["tiles"][coord_key]["poi_type"] = poi_type
        attempts += 1
        
    return pois

def generate_region(seed_x: int = 0, seed_y: int = 0) -> Dict[str, Any]:
    """
    Generate a new region with population-driven city/POI creation, unique motif pool, and metropolis type assignment.
    
    Args:
        seed_x: Starting X coordinate
        seed_y: Starting Y coordinate
        
    Returns:
        Complete region data dictionary
    """
    region_id = f"region_{seed_x}_{seed_y}_{uuid4().hex[:6]}"
    print(f"🌎 Generating region: {region_id}")

    # Init region metadata
    total_population = random.randint(*REGION_POPULATION_RANGE)
    region_data = {
        "region_id": region_id,
        "name": region_id.replace("_", " ").title(),
        "created_at": datetime.utcnow().isoformat(),
        "total_population": total_population,
        "tiles": {},
        "poi_list": [],
        "tension_level": random.randint(0, 20),
        "faction_count": random.randint(2, 4),
        "motif_pool": [],  # Will be populated by the motif system
        "memory": [],  # Placeholder for region memory (major events)
        "arc": None,  # Placeholder for arc (meta-quest)
        "metropolis_type": None,  # Placeholder for metropolis type (set during POI generation)
        "coordinates": {
            "x": seed_x,
            "y": seed_y
        }
    }

    # Generate natural tilemap
    region_data["tiles"] = walk_region(seed_x, seed_y, TOTAL_REGION_TILES)
    
    # Generate settlements
    settlements, remaining_npcs = generate_settlements(region_data, region_data["tiles"], total_population)
    
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
        
        # Mark the metropolis
        if metropolis_tile:
            coord_key = f"{metropolis_tile[0]}_{metropolis_tile[1]}"
            region_data["tiles"][coord_key]["is_metropolis"] = True
            metropolis_type = random.choice(["Arcane", "Industrial", "Sacred", "Ruined", "Natural"])
            region_data["tiles"][coord_key]["metropolis_type"] = metropolis_type
            region_data["metropolis_type"] = metropolis_type
            
            # Claim extra hexes for metropolis sprawl
            claimed_hexes = claim_region_hexes_for_city(region_data, metropolis_tile, is_metropolis=True)
            region_data["tiles"][coord_key]["region_hexes"] = claimed_hexes
            
            # Log the creation of a metropolis for narrative purposes
            log_event = {
                "type": "metropolis_assigned",
                "location": coord_key,
                "metropolis_type": metropolis_type,
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
    
    # Combine all POIs and store in region data
    all_pois = settlements + non_settlement_pois
    for x, y in all_pois:
        coord_key = f"{x}_{y}"
        region_data["poi_list"].append({
            "coord_key": coord_key,
            "x": x,
            "y": y,
            "type": region_data["tiles"][coord_key]["poi_type"],
            "is_metropolis": region_data["tiles"][coord_key].get("is_metropolis", False)
        })
    
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