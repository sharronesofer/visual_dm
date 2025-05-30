"""
World-related utility functions.
Provides functions for world generation, management, and interaction.
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import random
from backend.systems.world_state.core.world_models import (
    TerrainType,
    Region,
    PointOfInterest,
    WorldMap
)
from backend.core.utils.firebase_utils import get_firestore_client
from backend.core.utils.error_utils import NotFoundError, ValidationError
from backend.systems.integration.event_bus import integration_event_bus
from backend.systems.integration.state_sync import state_sync_manager
from backend.systems.integration.validation import validation_manager
from backend.systems.integration.monitoring import integration_logger, integration_metrics, integration_alerting
import asyncio
from backend.data.modding.loaders.game_data_registry import GameDataRegistry
from backend.systems.world_state.core.manager import WorldStateManager

# Instantiate registry at module level
registry = GameDataRegistry("backend/data/modding")
registry.load_all()

def generate_terrain_type(name: str) -> TerrainType:
    """Generate a terrain type with appropriate properties."""
    terrain = next((t for t in registry.land_types if t['name'] == name), None)
    if not terrain:
        raise ValueError(f"Unknown terrain type: {name}")
    return TerrainType(
        id=terrain.get('id', name),
        name=terrain['name'],
        description=terrain.get('description', f"A {name} terrain type."),
        movement_cost=terrain.get('movement_cost', 1.0),
        visibility_modifier=terrain.get('visibility_modifier', 1.0),
        resources=terrain.get('resources', []),
        features=terrain.get('features', []),
        metadata=terrain.get('metadata', {})
    )

def generate_region(
    name: str,
    climate: str,
    min_level: int = 1,
    max_level: int = 20
) -> Region:
    """Generate a region with appropriate properties."""
    climates = [c['name'] for c in getattr(registry, 'climates', [])]
    if climate not in climates:
        raise ValueError(f"Unknown climate: {climate}")
    terrain_types = [t['name'] for t in registry.land_types]
    return Region(
        name=name,
        description=f"A {climate} region called {name}.",
        level_range=(min_level, max_level),
        terrain_types=random.sample(terrain_types, random.randint(2, 4)),
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
    # Integration hooks
    asyncio.create_task(integration_event_bus.dispatch('world_map_created', map_id=world_map.id, name=name))
    asyncio.create_task(integration_logger.log(20, f"World map {world_map.id} created: {name}"))
    asyncio.create_task(integration_metrics.record('world_map_create', 1))
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
    # Integration hooks
    asyncio.create_task(integration_event_bus.dispatch('world_map_updated', map_id=map_id, updates=updates))
    asyncio.create_task(integration_logger.log(20, f"World map {map_id} updated: {updates}"))
    asyncio.create_task(integration_metrics.record('world_map_update', 1))
    return world_map

# Note: world_state functions removed in favor of using WorldStateManager
# Use WorldStateManager.get_instance() to access world state functionality

def get_region_at_coordinates(map_id: str, x: int, y: int) -> Optional[str]:
    """Get the region ID at the specified coordinates."""
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
    """Calculate travel time between two points on the map."""
    world_map = get_world_map(map_id)
    distance = world_map.calculate_distance(start_x, start_y, end_x, end_y)
    return distance / (speed * 1000)  # Convert to hours

def validate_world_data(data: Dict[str, Any]) -> bool:
    """
    Validate world data structure.
    
    Args:
        data: The data to validate
    
    Returns:
        True if valid, False otherwise
    """
    # Minimal validation
    required_keys = ["id", "name", "regions", "width", "height"]
    
    if not all(key in data for key in required_keys):
        return False
    
    # More detailed validation could be added here
    
    return True

def process_world_tick(world_state_id: str) -> None:
    """
    Process a world tick using the canonical WorldStateManager.
    
    Args:
        world_state_id: ID of the world state to tick
    """
    world_state_manager = WorldStateManager.get_instance()
    
    try:
        # Call the manager to process the tick
        asyncio.create_task(world_state_manager.process_tick())
        
        # Integration hooks
        asyncio.create_task(integration_event_bus.dispatch('world_tick_processed', world_state_id=world_state_id))
        asyncio.create_task(integration_logger.log(20, f"World tick processed for state {world_state_id}"))
        asyncio.create_task(integration_metrics.record('world_tick', 1))
    except Exception as e:
        asyncio.create_task(integration_logger.log(40, f"Error processing world tick: {str(e)}"))
        asyncio.create_task(integration_alerting.alert("world_tick_failure", f"Failed to process world tick: {str(e)}")) 