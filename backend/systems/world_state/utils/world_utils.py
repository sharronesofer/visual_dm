"""
World-related utility functions.
Provides functions for world generation, management, and interaction.
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import random

# Mock classes for missing models
class TerrainType:
    def __init__(self, id, name, description, movement_cost=1.0, visibility_modifier=1.0, resources=None, features=None, metadata=None):
        self.id = id
        self.name = name
        self.description = description
        self.movement_cost = movement_cost
        self.visibility_modifier = visibility_modifier
        self.resources = resources or []
        self.features = features or []
        self.metadata = metadata or {}

class Region:
    def __init__(self, name, description, level_range, terrain_types, points_of_interest, factions, climate):
        self.name = name
        self.description = description
        self.level_range = level_range
        self.terrain_types = terrain_types
        self.points_of_interest = points_of_interest
        self.factions = factions
        self.climate = climate

class PointOfInterest:
    def __init__(self, name, description, type, region_id, coordinates, level, npcs, quests, resources):
        self.name = name
        self.description = description
        self.type = type
        self.region_id = region_id
        self.coordinates = coordinates
        self.level = level
        self.npcs = npcs
        self.quests = quests
        self.resources = resources

class WorldMap:
    def __init__(self, name, description, width, height, scale=1.0):
        self.id = f"map_{name.lower().replace(' ', '_')}"
        self.name = name
        self.description = description
        self.width = width
        self.height = height
        self.scale = scale
        self.updated_at = datetime.utcnow()
    
    def dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'width': self.width,
            'height': self.height,
            'scale': self.scale,
            'updated_at': self.updated_at.isoformat()
        }
    
    def get_region_at(self, x, y):
        return f"region_{x}_{y}"
    
    def get_pois_in_region(self, region_id):
        return [f"poi_{region_id}_1", f"poi_{region_id}_2"]
    
    def calculate_distance(self, start_x, start_y, end_x, end_y):
        return ((end_x - start_x) ** 2 + (end_y - start_y) ** 2) ** 0.5

import asyncio

# HACK: GameDataRegistry doesn't exist - using placeholder
# TODO: Implement proper GameDataRegistry or remove dependency
class GameDataRegistryPlaceholder:
    """Placeholder for missing GameDataRegistry"""
    def __init__(self, path):
        self.path = path
        self.land_types = [
            {'name': 'forest', 'id': 'forest', 'movement_cost': 1.0, 'visibility_modifier': 0.8},
            {'name': 'grassland', 'id': 'grassland', 'movement_cost': 0.8, 'visibility_modifier': 1.2},
            {'name': 'mountain', 'id': 'mountain', 'movement_cost': 2.0, 'visibility_modifier': 1.5},
        ]
        self.climates = [
            {'name': 'temperate'},
            {'name': 'tropical'},
            {'name': 'arctic'},
        ]
    
    def load_all(self):
        """Placeholder load method"""
        pass

# HACK: Lazy loading to avoid circular import
# TODO: Refactor to eliminate circular dependency
def get_world_state_manager():
    """Lazy loading for WorldStateManager to avoid circular imports"""
    try:
        from backend.systems.world_state.manager import WorldStateManager
        return WorldStateManager
    except ImportError:
        # Return a placeholder class for now
        class WorldStateManagerPlaceholder:
            @classmethod
            def get_instance(cls):
                class InstancePlaceholder:
                    async def process_tick(self):
                        pass
                return InstancePlaceholder()
        return WorldStateManagerPlaceholder

# Instantiate registry at module level
registry = GameDataRegistryPlaceholder("data/builders")

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
    return world_map

def get_world_map(map_id: str) -> Optional[WorldMap]:
    """Retrieve a world map by ID - placeholder implementation."""
    # This would need to be implemented with proper data access
    return None

def update_world_map(map_id: str, updates: Dict[str, Any]) -> Optional[WorldMap]:
    """Update a world map's properties - placeholder implementation."""
    # This would need to be implemented with proper data access
    return None

# Note: world_state functions removed in favor of using WorldStateManager
# Use WorldStateManager.get_instance() to access world state functionality

def get_region_at_coordinates(map_id: str, x: int, y: int) -> Optional[str]:
    """Get the region ID at the specified coordinates."""
    # This would need proper map data access
    return f"region_{x}_{y}"

def get_pois_in_region(map_id: str, region_id: str) -> List[str]:
    """Get all POIs in a specific region."""
    # This would need proper POI data access
    return [f"poi_{region_id}_1", f"poi_{region_id}_2"]

def calculate_travel_time(
    map_id: str,
    start_x: int,
    start_y: int,
    end_x: int,
    end_y: int,
    speed: float = 5.0  # km/h
) -> float:
    """Calculate travel time between two points on the map."""
    # Simple distance calculation
    distance = ((end_x - start_x) ** 2 + (end_y - start_y) ** 2) ** 0.5
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
    world_state_manager = get_world_state_manager().get_instance()
    
    try:
        # Call the manager to process the tick
        asyncio.create_task(world_state_manager.process_tick())
    except Exception as e:
        # Log error without integration dependencies
        print(f"Error processing world tick: {str(e)}") 