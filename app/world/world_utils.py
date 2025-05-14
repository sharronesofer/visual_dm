"""
World-related utility functions.
Provides functions for world generation, management, and interaction.
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import random
from .world_models import (
    TerrainType,
    Region,
    PointOfInterest,
    WorldMap,
    WorldState
)
from ..core.utils.firebase_utils import get_firestore_client
from ..core.utils.error_utils import NotFoundError, ValidationError

# Constants for world generation
TERRAIN_TYPES = [
    "plains", "forest", "mountains", "desert", "swamp",
    "tundra", "coast", "ocean", "river", "lake"
]

CLIMATES = [
    "temperate", "tropical", "arid", "polar", "continental"
]

WEATHER_TYPES = [
    "clear", "cloudy", "rainy", "stormy", "snowy", "foggy"
]

def generate_terrain_type(name: str) -> TerrainType:
    """Generate a terrain type with appropriate properties."""
    return TerrainType(
        name=name,
        description=f"A {name} terrain type.",
        movement_cost=random.uniform(1.0, 3.0),
        visibility_modifier=random.uniform(0.3, 1.0),
        resources=[],
        features=[]
    )

def generate_region(
    name: str,
    climate: str,
    min_level: int = 1,
    max_level: int = 20
) -> Region:
    """Generate a region with appropriate properties."""
    return Region(
        name=name,
        description=f"A {climate} region called {name}.",
        level_range=(min_level, max_level),
        terrain_types=random.sample(TERRAIN_TYPES, random.randint(2, 4)),
        points_of_interest=[],
        factions=[],
        climate=climate
    )

def generate_point_of_interest(
    name: str,
    poi_type: str,
    region_id: str,
    coordinates: Tuple[float, float],
    level: int
) -> PointOfInterest:
    """Generate a point of interest with appropriate properties."""
    return PointOfInterest(
        name=name,
        description=f"A {poi_type} called {name}.",
        type=poi_type,
        region_id=region_id,
        coordinates=coordinates,
        level=level,
        npcs=[],
        quests=[],
        resources=[]
    )

def create_world_map(
    name: str,
    width: int,
    height: int,
    scale: float = 1.0
) -> WorldMap:
    """Create a new world map."""
    world_map = WorldMap(
        name=name,
        description=f"A world map called {name}.",
        width=width,
        height=height,
        scale=scale
    )

    # Save to Firebase
    db = get_firestore_client()
    db.collection("world_maps").document(world_map.id).set(world_map.dict())
    return world_map

def get_world_map(map_id: str) -> WorldMap:
    """Retrieve a world map by ID."""
    db = get_firestore_client()
    doc = db.collection("world_maps").document(map_id).get()
    
    if not doc.exists:
        raise NotFoundError(f"World map with ID {map_id} not found")
    
    return WorldMap(**doc.to_dict())

def update_world_map(map_id: str, updates: Dict[str, Any]) -> WorldMap:
    """Update a world map's properties."""
    world_map = get_world_map(map_id)
    
    # Update map properties
    for key, value in updates.items():
        if hasattr(world_map, key):
            setattr(world_map, key, value)
    
    world_map.updated_at = datetime.utcnow()
    
    # Save to Firebase
    db = get_firestore_client()
    db.collection("world_maps").document(map_id).update(world_map.dict())
    return world_map

def create_world_state() -> WorldState:
    """Create a new world state."""
    world_state = WorldState(
        weather=random.choice(WEATHER_TYPES),
        season=random.choice(["spring", "summer", "autumn", "winter"]),
        active_events=[],
        active_quests=[],
        active_npcs=[]
    )

    # Save to Firebase
    db = get_firestore_client()
    db.collection("world_states").document(world_state.id).set(world_state.dict())
    return world_state

def get_world_state(state_id: str) -> WorldState:
    """Retrieve a world state by ID."""
    db = get_firestore_client()
    doc = db.collection("world_states").document(state_id).get()
    
    if not doc.exists:
        raise NotFoundError(f"World state with ID {state_id} not found")
    
    return WorldState(**doc.to_dict())

def update_world_state(state_id: str, updates: Dict[str, Any]) -> WorldState:
    """Update a world state's properties."""
    world_state = get_world_state(state_id)
    
    # Update state properties
    for key, value in updates.items():
        if hasattr(world_state, key):
            setattr(world_state, key, value)
    
    world_state.updated_at = datetime.utcnow()
    
    # Save to Firebase
    db = get_firestore_client()
    db.collection("world_states").document(state_id).update(world_state.dict())
    return world_state

def advance_world_time(state_id: str, hours: int = 1) -> WorldState:
    """Advance the world time by the specified number of hours."""
    world_state = get_world_state(state_id)
    world_state.advance_time(hours)
    
    # Update weather based on time of day and season
    current_hour = world_state.current_time.hour
    if 6 <= current_hour < 18:  # Daytime
        if random.random() < 0.3:  # 30% chance of weather change
            world_state.update_weather(random.choice(WEATHER_TYPES))
    
    # Save updates
    return update_world_state(state_id, world_state.dict())

def get_region_at_coordinates(map_id: str, x: int, y: int) -> Optional[str]:
    """Get the region ID at the specified coordinates on the map."""
    world_map = get_world_map(map_id)
    return world_map.get_region_at(x, y)

def get_pois_in_region(map_id: str, region_id: str) -> List[str]:
    """Get all POIs in a specific region."""
    world_map = get_world_map(map_id)
    return world_map.get_pois_in_region(region_id)

def calculate_travel_time(
    map_id: str,
    start_x: int,
    start_y: int,
    end_x: int,
    end_y: int,
    speed: float = 5.0  # km/h
) -> float:
    """Calculate the travel time between two points on the map."""
    world_map = get_world_map(map_id)
    distance = world_map.calculate_distance(start_x, start_y, end_x, end_y)
    return distance / (speed * 1000)  # Convert to hours

def validate_world_data(data: Dict[str, Any]) -> bool:
    """Validate world creation/update data."""
    if "map" in data:
        map_data = data["map"]
        if "width" in map_data and map_data["width"] < 1:
            raise ValidationError("Map width must be at least 1")
        if "height" in map_data and map_data["height"] < 1:
            raise ValidationError("Map height must be at least 1")
        if "scale" in map_data and map_data["scale"] <= 0:
            raise ValidationError("Map scale must be greater than 0")
    
    if "region" in data:
        region_data = data["region"]
        if "level_range" in region_data:
            min_level, max_level = region_data["level_range"]
            if min_level > max_level:
                raise ValidationError("Minimum level cannot be greater than maximum level")
    
    return True 

def process_world_tick(world_state_id: str) -> None:
    """Process a world tick, updating various world state elements."""
    world_state = get_world_state(world_state_id)
    
    # Update time
    advance_world_time(world_state_id)
    
    # Process active events
    for event in world_state.active_events:
        if event.should_end():
            world_state.active_events.remove(event)
    
    # Process active quests
    for quest in world_state.active_quests:
        if quest.is_completed() or quest.is_failed():
            world_state.active_quests.remove(quest)
    
    # Update NPCs
    for npc in world_state.active_npcs:
        if npc.needs_update():
            npc.update_state()
    
    # Save state changes
    update_world_state(world_state_id, world_state.dict())

def cleanup_old_events(world_state_id: str, max_age_hours: int = 24) -> None:
    """Remove events older than the specified age."""
    world_state = get_world_state(world_state_id)
    current_time = datetime.utcnow()
    
    # Filter out old events
    world_state.active_events = [
        event for event in world_state.active_events
        if (current_time - event.created_at) < timedelta(hours=max_age_hours)
    ]
    
    # Save state changes
    update_world_state(world_state_id, world_state.dict()) 