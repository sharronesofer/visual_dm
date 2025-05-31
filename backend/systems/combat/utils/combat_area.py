"""
CombatArea module for the Visual DM combat system.

This module implements a system for managing battlefield positions, terrain,
and movement during combat. It provides spatial awareness and positioning
for combat entities.

Following the design principles from the Development Bible, this implementation:
1. Uses a grid-based positioning system
2. Supports terrain features with gameplay effects
3. Manages line of sight and cover calculations
4. Is entirely runtime-generated with no scene dependencies
"""

import logging
import math
import random
from typing import Dict, List, Any, Optional, Tuple, Set, Union
import uuid

# Set up logging
logger = logging.getLogger(__name__)

# Type definitions
Position = Tuple[float, float, float]  # x, y, z
GridCoord = Tuple[int, int]  # grid_x, grid_y

class TerrainFeature:
    """Represents a terrain feature on the battlefield."""
    
    def __init__(
        self,
        feature_id: str,
        name: str,
        position: Position,
        size: Tuple[float, float],
        feature_type: str,
        properties: Dict[str, Any] = None
    ):
        """
        Initialize a terrain feature.
        
        Args:
            feature_id: Unique identifier
            name: Display name
            position: Center position (x, y, z)
            size: Width and height (x, z)
            feature_type: Type of feature (wall, water, etc.)
            properties: Additional properties for this feature
        """
        self.feature_id = feature_id
        self.name = name
        self.position = position
        self.size = size
        self.feature_type = feature_type
        self.properties = properties or {}
    
    def is_point_inside(self, point: Position) -> bool:
        """
        Check if a point is inside this feature.
        
        Args:
            point: Position to check (x, y, z)
            
        Returns:
            True if the point is inside the feature
        """
        # Extract feature boundaries
        feature_x, _, feature_z = self.position
        width, height = self.size
        half_width = width / 2
        half_height = height / 2
        
        # Extract point coordinates
        point_x, _, point_z = point
        
        # Check if point is within boundaries
        return (
            point_x >= feature_x - half_width and
            point_x <= feature_x + half_width and
            point_z >= feature_z - half_height and
            point_z <= feature_z + half_height
        )
    
    def get_movement_modifier(self) -> float:
        """
        Get movement speed modifier for this terrain.
        
        Returns:
            Movement multiplier (1.0 = normal speed)
        """
        return self.properties.get("movement_modifier", 1.0)
    
    def provides_cover(self) -> bool:
        """
        Check if this feature provides cover.
        
        Returns:
            True if the feature provides cover
        """
        return self.properties.get("provides_cover", False)
    
    def is_passable(self) -> bool:
        """
        Check if entities can move through this feature.
        
        Returns:
            True if the feature is passable
        """
        return self.properties.get("passable", True)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.feature_id,
            "name": self.name,
            "position": self.position,
            "size": self.size,
            "type": self.feature_type,
            "properties": self.properties
        }

class CombatArea:
    """
    Manages the combat battlefield including positions and terrain.
    
    This class handles entity positioning, movement validation, and
    terrain effects during combat.
    """
    
    def __init__(
        self,
        area_id: str = None,
        name: str = "Battlefield",
        size: Tuple[float, float] = (20.0, 20.0),
        grid_size: float = 1.0
    ):
        """
        Initialize a new combat area.
        
        Args:
            area_id: Unique identifier (generated if None)
            name: Display name for this area
            size: Width and height of the area (x, z)
            grid_size: Size of each grid cell
        """
        self.area_id = area_id or f"area_{uuid.uuid4().hex[:8]}"
        self.name = name
        self.size = size
        self.grid_size = grid_size
        
        # Calculate grid dimensions
        self.grid_width = int(size[0] / grid_size)
        self.grid_height = int(size[1] / grid_size)
        
        # Entity positions (entity_id -> position)
        self.entity_positions: Dict[str, Position] = {}
        
        # Terrain features
        self.terrain_features: Dict[str, TerrainFeature] = {}
        
        # Grid cell occupancy for quick lookups
        self.grid_occupancy: Dict[GridCoord, Set[str]] = {}
        
        logger.info(f"CombatArea initialized: {name} ({size[0]}x{size[1]})")
    
    def _position_to_grid(self, position: Position) -> GridCoord:
        """
        Convert a world position to grid coordinates.
        
        Args:
            position: World position (x, y, z)
            
        Returns:
            Grid coordinates (grid_x, grid_y)
        """
        x, _, z = position
        grid_x = int(x / self.grid_size)
        grid_y = int(z / self.grid_size)
        
        # Clamp to grid boundaries
        grid_x = max(0, min(grid_x, self.grid_width - 1))
        grid_y = max(0, min(grid_y, self.grid_height - 1))
        
        return (grid_x, grid_y)
    
    def _grid_to_position(self, grid_coord: GridCoord) -> Position:
        """
        Convert grid coordinates to world position.
        
        Args:
            grid_coord: Grid coordinates (grid_x, grid_y)
            
        Returns:
            World position (x, y, z) at grid cell center
        """
        grid_x, grid_y = grid_coord
        x = (grid_x + 0.5) * self.grid_size
        z = (grid_y + 0.5) * self.grid_size
        
        return (x, 0.0, z)
    
    def add_entity(self, entity_id: str, position: Position) -> bool:
        """
        Add an entity to the combat area.
        
        Args:
            entity_id: Unique identifier for the entity
            position: Initial position (x, y, z)
            
        Returns:
            True if entity was added successfully
        """
        # Validate position is within bounds
        if not self.is_position_valid(position):
            logger.warning(f"Cannot add entity {entity_id}: Position out of bounds")
            return False
        
        # Add to position dictionary
        self.entity_positions[entity_id] = position
        
        # Add to grid occupancy
        grid_coord = self._position_to_grid(position)
        if grid_coord not in self.grid_occupancy:
            self.grid_occupancy[grid_coord] = set()
        self.grid_occupancy[grid_coord].add(entity_id)
        
        logger.debug(f"Added entity {entity_id} at position {position}")
        return True
    
    def remove_entity(self, entity_id: str) -> bool:
        """
        Remove an entity from the combat area.
        
        Args:
            entity_id: ID of the entity to remove
            
        Returns:
            True if entity was found and removed
        """
        if entity_id not in self.entity_positions:
            return False
        
        # Remove from grid occupancy
        position = self.entity_positions[entity_id]
        grid_coord = self._position_to_grid(position)
        
        if grid_coord in self.grid_occupancy:
            self.grid_occupancy[grid_coord].discard(entity_id)
            
            # Clean up empty sets
            if not self.grid_occupancy[grid_coord]:
                del self.grid_occupancy[grid_coord]
        
        # Remove from positions dictionary
        del self.entity_positions[entity_id]
        
        logger.debug(f"Removed entity {entity_id} from combat area")
        return True
    
    def move_entity(self, entity_id: str, new_position: Position) -> bool:
        """
        Move an entity to a new position.
        
        Args:
            entity_id: ID of the entity to move
            new_position: New position (x, y, z)
            
        Returns:
            True if move was successful
        """
        if entity_id not in self.entity_positions:
            logger.warning(f"Cannot move entity {entity_id}: Not in combat area")
            return False
        
        # Validate position is within bounds
        if not self.is_position_valid(new_position):
            logger.warning(f"Cannot move entity {entity_id}: Position out of bounds")
            return False
        
        # Check if move is valid (terrain, etc.)
        if not self.can_move_to(entity_id, new_position):
            logger.warning(f"Cannot move entity {entity_id}: Invalid move")
            return False
        
        # Remove from old grid cell
        old_position = self.entity_positions[entity_id]
        old_grid = self._position_to_grid(old_position)
        
        if old_grid in self.grid_occupancy:
            self.grid_occupancy[old_grid].discard(entity_id)
            
            # Clean up empty sets
            if not self.grid_occupancy[old_grid]:
                del self.grid_occupancy[old_grid]
        
        # Add to new grid cell
        new_grid = self._position_to_grid(new_position)
        if new_grid not in self.grid_occupancy:
            self.grid_occupancy[new_grid] = set()
        self.grid_occupancy[new_grid].add(entity_id)
        
        # Update position
        self.entity_positions[entity_id] = new_position
        
        logger.debug(f"Moved entity {entity_id} to position {new_position}")
        return True
    
    def get_entity_position(self, entity_id: str) -> Optional[Position]:
        """
        Get the current position of an entity.
        
        Args:
            entity_id: ID of the entity
            
        Returns:
            Current position, or None if entity not found
        """
        return self.entity_positions.get(entity_id)
    
    def get_entities_at_position(self, position: Position, radius: float = 0.0) -> List[str]:
        """
        Get all entities at or near a specific position.
        
        Args:
            position: Position to check (x, y, z)
            radius: Search radius (0 for exact position)
            
        Returns:
            List of entity IDs at the position
        """
        if radius <= 0:
            # Just check the exact grid cell
            grid_coord = self._position_to_grid(position)
            return list(self.grid_occupancy.get(grid_coord, set()))
        
        # Check cells within radius
        x, y, z = position
        entities = set()
        grid_radius = math.ceil(radius / self.grid_size)
        
        for dx in range(-grid_radius, grid_radius + 1):
            for dz in range(-grid_radius, grid_radius + 1):
                check_x = x + dx * self.grid_size
                check_z = z + dz * self.grid_size
                
                check_position = (check_x, y, check_z)
                
                # Skip if outside area bounds
                if not self.is_position_valid(check_position):
                    continue
                
                # Check distance to original position
                dist = math.sqrt((check_x - x) ** 2 + (check_z - z) ** 2)
                if dist <= radius:
                    grid_coord = self._position_to_grid(check_position)
                    if grid_coord in self.grid_occupancy:
                        entities.update(self.grid_occupancy[grid_coord])
        
        return list(entities)
    
    def is_position_valid(self, position: Position) -> bool:
        """
        Check if a position is within the combat area bounds.
        
        Args:
            position: Position to check (x, y, z)
            
        Returns:
            True if position is valid
        """
        x, _, z = position
        width, height = self.size
        
        return 0 <= x < width and 0 <= z < height
    
    def can_move_to(self, entity_id: str, position: Position) -> bool:
        """
        Check if an entity can move to a specific position.
        
        Args:
            entity_id: ID of the entity trying to move
            position: Target position (x, y, z)
            
        Returns:
            True if the move is valid
        """
        # Check if position is within bounds
        if not self.is_position_valid(position):
            return False
        
        # Check terrain features
        for feature in self.terrain_features.values():
            if feature.is_point_inside(position) and not feature.is_passable():
                return False
        
        return True
    
    def calculate_path(
        self, 
        entity_id: str, 
        target_position: Position,
        avoid_entities: bool = True
    ) -> List[Position]:
        """
        Calculate a path from entity's current position to target.
        
        Args:
            entity_id: ID of the entity to move
            target_position: Target position (x, y, z)
            avoid_entities: Whether to avoid other entities
            
        Returns:
            List of positions forming the path (empty if no path)
        """
        # This is a simplified implementation using a basic A* algorithm
        # A production-ready system would use a more sophisticated pathfinding approach
        
        start_position = self.get_entity_position(entity_id)
        if not start_position:
            return []
            
        # If already at target, return empty path
        if start_position == target_position:
            return []
            
        # For now, just return a straight-line path if target is reachable
        if self.can_move_to(entity_id, target_position):
            # For simplicity, just return start and end points
            # A real implementation would include intermediate points
            return [start_position, target_position]
        
        # No path found
        return []
    
    def add_terrain_feature(self, feature: TerrainFeature) -> str:
        """
        Add a terrain feature to the combat area.
        
        Args:
            feature: TerrainFeature to add
            
        Returns:
            ID of the added feature
        """
        # Validate position is within bounds
        if not self.is_position_valid(feature.position):
            logger.warning(f"Cannot add terrain feature: Position out of bounds")
            return None
        
        # Add to features dictionary
        self.terrain_features[feature.feature_id] = feature
        
        logger.debug(f"Added terrain feature {feature.name} ({feature.feature_id})")
        return feature.feature_id
    
    def remove_terrain_feature(self, feature_id: str) -> bool:
        """
        Remove a terrain feature from the combat area.
        
        Args:
            feature_id: ID of the feature to remove
            
        Returns:
            True if feature was found and removed
        """
        if feature_id not in self.terrain_features:
            return False
        
        # Remove from features dictionary
        del self.terrain_features[feature_id]
        
        logger.debug(f"Removed terrain feature {feature_id}")
        return True
    
    def get_terrain_at_position(self, position: Position) -> List[TerrainFeature]:
        """
        Get all terrain features at a specific position.
        
        Args:
            position: Position to check (x, y, z)
            
        Returns:
            List of terrain features at the position
        """
        features = []
        
        for feature in self.terrain_features.values():
            if feature.is_point_inside(position):
                features.append(feature)
        
        return features
    
    def is_line_of_sight_clear(self, start: Position, end: Position) -> bool:
        """
        Check if there is clear line of sight between two positions.
        
        Args:
            start: Starting position (x, y, z)
            end: Ending position (x, y, z)
            
        Returns:
            True if line of sight is clear
        """
        # This is a simplified implementation using a raycasting approach
        # A production-ready system would use more sophisticated techniques
        
        # Extract coordinates
        start_x, start_y, start_z = start
        end_x, end_y, end_z = end
        
        # Calculate direction vector
        dir_x = end_x - start_x
        dir_z = end_z - start_z
        
        # Normalize direction
        length = math.sqrt(dir_x ** 2 + dir_z ** 2)
        if length < 0.0001:
            return True  # Points are basically the same
            
        dir_x /= length
        dir_z /= length
        
        # Step along the line and check for blocking terrain
        steps = int(length / (self.grid_size * 0.5))
        steps = max(5, steps)  # Use at least 5 steps for short distances
        
        for i in range(1, steps):
            t = i / steps
            check_x = start_x + dir_x * length * t
            check_z = start_z + dir_z * length * t
            
            check_position = (check_x, 0.0, check_z)
            
            # Check terrain features
            for feature in self.terrain_features.values():
                if feature.is_point_inside(check_position) and not feature.is_passable():
                    return False
        
        return True
    
    def get_movement_cost(self, start: Position, end: Position) -> float:
        """
        Calculate the movement cost between two positions.
        
        Args:
            start: Starting position (x, y, z)
            end: Ending position (x, y, z)
            
        Returns:
            Movement cost (1.0 = normal cost)
        """
        # Calculate base distance
        start_x, _, start_z = start
        end_x, _, end_z = end
        
        distance = math.sqrt((end_x - start_x) ** 2 + (end_z - start_z) ** 2)
        
        # Check for terrain modifiers
        midpoint = (
            (start_x + end_x) / 2,
            0.0,
            (start_z + end_z) / 2
        )
        
        # Get terrain at midpoint
        terrain_features = self.get_terrain_at_position(midpoint)
        
        # Apply terrain modifiers
        cost_multiplier = 1.0
        for feature in terrain_features:
            cost_multiplier *= feature.get_movement_modifier()
        
        return distance * cost_multiplier
    
    def get_nearest_position(self, target: Position, max_distance: float = 5.0) -> Position:
        """
        Find the nearest valid position to a target.
        
        Args:
            target: Target position (x, y, z)
            max_distance: Maximum search distance
            
        Returns:
            Valid position closest to target, or original target if already valid
        """
        # If target is already valid, return it
        if self.is_position_valid(target) and not any(
            feature.is_point_inside(target) and not feature.is_passable()
            for feature in self.terrain_features.values()
        ):
            return target
        
        # Extract coordinates
        target_x, target_y, target_z = target
        
        # Search in expanding rings
        best_position = None
        best_distance = float('inf')
        
        search_radius = max(1, int(max_distance / self.grid_size))
        
        for dx in range(-search_radius, search_radius + 1):
            for dz in range(-search_radius, search_radius + 1):
                # Skip corners to prioritize closer positions
                if abs(dx) == search_radius and abs(dz) == search_radius:
                    continue
                
                check_x = target_x + dx * self.grid_size
                check_z = target_z + dz * self.grid_size
                
                check_position = (check_x, target_y, check_z)
                
                # Check if position is valid
                if not self.is_position_valid(check_position):
                    continue
                
                # Check terrain features
                if any(
                    feature.is_point_inside(check_position) and not feature.is_passable()
                    for feature in self.terrain_features.values()
                ):
                    continue
                
                # Calculate distance to target
                distance = math.sqrt((check_x - target_x) ** 2 + (check_z - target_z) ** 2)
                
                # Update best position if closer
                if distance < best_distance:
                    best_distance = distance
                    best_position = check_position
        
        return best_position if best_position else target
    
    def create_default_terrain(self) -> None:
        """Create default terrain features for a standard combat area."""
        # Add some sample terrain features
        
        # Center obstacle
        center_x = self.size[0] / 2
        center_z = self.size[1] / 2
        
        center_obstacle = TerrainFeature(
            feature_id=f"terrain_{uuid.uuid4().hex[:8]}",
            name="Center Pillar",
            position=(center_x, 0, center_z),
            size=(2.0, 2.0),
            feature_type="obstacle",
            properties={
                "passable": False,
                "provides_cover": True,
                "description": "A large stone pillar in the center of the area"
            }
        )
        self.add_terrain_feature(center_obstacle)
        
        # Some scattered rocks
        for i in range(3):
            rock_x = random.uniform(2.0, self.size[0] - 2.0)
            rock_z = random.uniform(2.0, self.size[1] - 2.0)
            
            rock = TerrainFeature(
                feature_id=f"terrain_{uuid.uuid4().hex[:8]}",
                name=f"Rock {i+1}",
                position=(rock_x, 0, rock_z),
                size=(1.0, 1.0),
                feature_type="obstacle",
                properties={
                    "passable": False,
                    "provides_cover": True,
                    "description": "A large boulder"
                }
            )
            self.add_terrain_feature(rock)
        
        # Difficult terrain patch
        mud_x = random.uniform(3.0, self.size[0] - 3.0)
        mud_z = random.uniform(3.0, self.size[1] - 3.0)
        
        mud = TerrainFeature(
            feature_id=f"terrain_{uuid.uuid4().hex[:8]}",
            name="Mud Patch",
            position=(mud_x, 0, mud_z),
            size=(4.0, 4.0),
            feature_type="difficult_terrain",
            properties={
                "passable": True,
                "movement_modifier": 2.0,
                "description": "A patch of thick mud that slows movement"
            }
        )
        self.add_terrain_feature(mud)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.area_id,
            "name": self.name,
            "size": self.size,
            "grid_size": self.grid_size,
            "grid_dimensions": (self.grid_width, self.grid_height),
            "entities": {
                entity_id: list(position)
                for entity_id, position in self.entity_positions.items()
            },
            "terrain_features": {
                feature_id: feature.to_dict()
                for feature_id, feature in self.terrain_features.items()
            },
        }

# Create a factory function to get a combat area
def create_combat_area(
    name: str = "Battlefield",
    size: Tuple[float, float] = (20.0, 20.0),
    add_default_terrain: bool = True
) -> CombatArea:
    """
    Create and initialize a new combat area.
    
    Args:
        name: Display name
        size: Area dimensions (width, height)
        add_default_terrain: Whether to add default terrain features
        
    Returns:
        Initialized CombatArea instance
    """
    area = CombatArea(name=name, size=size)
    
    if add_default_terrain:
        area.create_default_terrain()
    
    return area 