from typing import List, Dict, Optional, Any, Set, Tuple, Dict, Union, Callable
from enum import Enum
import time
import math
from backend.utils.grid import GridManager, GridCell
from backend.utils.collision import CollisionSystem

# Data structure stubs
class CellType(Enum):
    EMPTY = 0
    ROAD = 1
    WALL = 2
    BLOCKED = 3
    ROUGH = 4
    WATER = 5

class GridPosition:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
    def __eq__(self, other):
        return isinstance(other, GridPosition) and self.x == other.x and self.y == other.y
    def __hash__(self):
        return hash((self.x, self.y))
    def __repr__(self):
        return f"GridPosition({self.x}, {self.y})"

class PathfindingNode:
    def __init__(self, position: GridPosition, g_cost: float, h_cost: float, parent: Optional['PathfindingNode'] = None):
        self.position = position
        self.g_cost = g_cost
        self.h_cost = h_cost
        self.parent = parent
    
    @property
    def f_cost(self) -> float:
        return self.g_cost + self.h_cost

# POICategory as string alias
POICategory = str

class PathCache:
    def __init__(self, path: List[GridPosition], timestamp: float, category: Optional[POICategory] = None):
        self.path = path
        self.timestamp = timestamp
        self.category = category

class GroupPathfindingOptions:
    def __init__(self, group_size: int = 1, formation_width: int = 1, formation_spacing: int = 2, predictive_avoidance: bool = True):
        self.group_size = group_size
        self.formation_width = formation_width
        self.formation_spacing = formation_spacing
        self.predictive_avoidance = predictive_avoidance

class CategoryPathRules:
    def __init__(self, preferred_types: List[CellType], avoid_types: List[CellType], weight_multiplier: float):
        self.preferred_types = preferred_types
        self.avoid_types = avoid_types
        self.weight_multiplier = weight_multiplier

# Main PathfindingSystem class
class PathfindingSystem:
    """
    PathfindingSystem implements A* pathfinding with support for
    grid-based navigation, collision avoidance, and group movement.
    """
    
    CACHE_DURATION = 5.0  # seconds
    PREDICTIVE_LOOKAHEAD = 3

    def __init__(self, grid_manager: GridManager, collision_system: CollisionSystem):
        """
        Initialize the pathfinding system.
        
        Args:
            grid_manager: The grid manager to provide the navigable grid
            collision_system: The collision system to detect obstacles
        """
        self.grid_manager = grid_manager
        self.collision_system = collision_system
        self.path_cache: Dict[str, PathCache] = {}
        
        # Initialize default category rules
        self.category_rules: Dict[POICategory, CategoryPathRules] = {
            'default': CategoryPathRules(
                preferred_types=[CellType.ROAD],
                avoid_types=[CellType.ROUGH, CellType.WATER],
                weight_multiplier=1.0
            ),
            'npc': CategoryPathRules(
                preferred_types=[CellType.ROAD],
                avoid_types=[CellType.ROUGH, CellType.WATER],
                weight_multiplier=1.0
            ),
            'monster': CategoryPathRules(
                preferred_types=[CellType.ROUGH],
                avoid_types=[CellType.ROAD],
                weight_multiplier=1.2
            ),
            'water_creature': CategoryPathRules(
                preferred_types=[CellType.WATER],
                avoid_types=[CellType.ROAD, CellType.ROUGH],
                weight_multiplier=1.5
            )
        }

    def find_path(self, start: GridPosition, end: GridPosition, character_id: Optional[str] = None, predictive_avoidance: bool = False) -> List[GridPosition]:
        """
        Find a path from start to end position using A* algorithm.
        
        Args:
            start: Starting position
            end: Target position
            character_id: Optional ID of the character finding the path (for collision avoidance)
            predictive_avoidance: Whether to use predictive collision avoidance
            
        Returns:
            List of positions forming the path, or empty list if no path found
        """
        # Try cache first
        cache_key = f"{start.x},{start.y}:{end.x},{end.y}"
        cache_entry = self.path_cache.get(cache_key)
        if cache_entry and (time.time() - cache_entry.timestamp) < self.CACHE_DURATION:
            return cache_entry.path
        
        # Initialize A* algorithm
        open_set: List[PathfindingNode] = []
        closed_set: Set[str] = set()

        start_node = PathfindingNode(position=start, g_cost=0, h_cost=self._calculate_heuristic(start, end))
        open_set.append(start_node)

        while open_set:
            current_node = self._get_lowest_f_cost_node(open_set)
            
            # Check if we've reached the end
            if current_node.position == end:
                path = self._reconstruct_path(current_node)
                # Cache the result
                self.path_cache[cache_key] = PathCache(path, time.time())
                return path

            # Move to closed set
            open_set.remove(current_node)
            closed_set.add(self._position_to_string(current_node.position))

            # Process neighbors
            neighbors = self._get_walkable_neighbors(current_node.position, character_id)
            for neighbor in neighbors:
                # Skip already-evaluated nodes
                if self._position_to_string(neighbor) in closed_set:
                    continue

                # Calculate costs
                new_g_cost = current_node.g_cost + self._get_node_cost(
                    PathfindingNode(position=neighbor, g_cost=0, h_cost=0), 
                    current_node.position
                )
                
                # Add predictive avoidance cost if enabled
                if predictive_avoidance:
                    new_g_cost += self._calculate_predictive_collision_cost(neighbor)

                # Check if this node is already in open set
                neighbor_node = next((node for node in open_set if node.position == neighbor), None)
                
                if neighbor_node is None:
                    # Add new node to open set
                    open_set.append(PathfindingNode(
                        position=neighbor, 
                        g_cost=new_g_cost, 
                        h_cost=self._calculate_heuristic(neighbor, end), 
                        parent=current_node
                    ))
                elif new_g_cost < neighbor_node.g_cost:
                    # Update existing node in open set
                    neighbor_node.g_cost = new_g_cost
                    neighbor_node.parent = current_node

        # No path found
        return []

    def invalidate_cache(self, position: GridPosition, radius: int = 1) -> None:
        """
        Invalidate pathfinding cache entries that pass through the given position.
        
        Args:
            position: The position where the grid has changed
            radius: Radius around the position to invalidate
        """
        # Filter cache entries and keep only those that don't pass through the position
        new_cache = {}
        for key, cache_entry in self.path_cache.items():
            valid = True
            for path_pos in cache_entry.path:
                # Check if path position is close to the invalidated position
                if (abs(path_pos.x - position.x) <= radius and 
                    abs(path_pos.y - position.y) <= radius):
                    valid = False
                    break
            
            if valid:
                new_cache[key] = cache_entry
        
        self.path_cache = new_cache

    def update_path_segment(self, path: List[GridPosition], start_index: int, end_index: int, category: Optional[POICategory] = None) -> List[GridPosition]:
        """
        Update a segment of a path with a more optimal route.
        
        Args:
            path: The original path
            start_index: Index of the start position in the path
            end_index: Index of the end position in the path
            category: Optional POI category to use for path calculation
            
        Returns:
            A new path with the segment updated
        """
        if len(path) < 2 or start_index >= end_index or start_index < 0 or end_index >= len(path):
            return path.copy()
        
        # Find new path for segment
        start_pos = path[start_index]
        end_pos = path[end_index]
        
        # Use active category rules
        old_rules = None
        if category and category in self.category_rules:
            # Temporarily set active category for path calculation
            old_rules = self.category_rules.get('default')
            self.category_rules['default'] = self.category_rules[category]
        
        # Calculate new path segment
        new_segment = self.find_path(start_pos, end_pos)
        
        # Restore original rules if changed
        if old_rules:
            self.category_rules['default'] = old_rules
        
        if not new_segment:
            return path.copy()  # Return original path if segment cannot be found
        
        # Build new combined path
        new_path = path[:start_index]
        new_path.extend(new_segment)
        new_path.extend(path[end_index+1:])
        
        return new_path

    def find_group_path(self, start: GridPosition, end: GridPosition, options: GroupPathfindingOptions, character_id: Optional[str] = None) -> List[GridPosition]:
        """
        Find a path suitable for group movement, ensuring it's wide enough for the group.
        
        Args:
            start: Starting position for the group
            end: Target position for the group
            options: Options for group pathfinding
            character_id: Optional ID of the lead character
            
        Returns:
            A path suitable for group movement, or empty list if no path found
        """
        if options.group_size <= 1:
            # For single entity, use regular pathfinding
            return self.find_path(start, end, character_id, options.predictive_avoidance)
        
        # Find initial path for group leader
        leader_path = self.find_path(start, end, character_id, options.predictive_avoidance)
        if not leader_path:
            return []
        
        # Widen the path for group movement
        widened_path = []
        
        # Process each point in the leader's path
        for i in range(len(leader_path)):
            pos = leader_path[i]
            
            # Skip if we can't determine the direction
            if i == 0 or i == len(leader_path) - 1:
                widened_path.append(pos)
                continue
            
            # Calculate movement direction
            prev = leader_path[i - 1]
            next_pos = leader_path[i + 1]
            
            # Calculate perpendicular direction for formation width
            dx = next_pos.x - prev.x
            dy = next_pos.y - prev.y
            perp_dx = -dy
            perp_dy = dx
            
            if perp_dx == 0 and perp_dy == 0:
                # If we're moving diagonally or not moving, just use current position
                widened_path.append(pos)
                continue
            
            # Normalize perpendicular vector
            magnitude = math.sqrt(perp_dx * perp_dx + perp_dy * perp_dy)
            if magnitude > 0:
                perp_dx /= magnitude
                perp_dy /= magnitude
            
            # Calculate the center of the formation
            center_x = pos.x + (options.formation_width - 1) * options.formation_spacing * perp_dx / 2
            center_y = pos.y + (options.formation_width - 1) * options.formation_spacing * perp_dy / 2
            
            # Check if the formation position is valid
            position_valid = True
            for w in range(options.formation_width):
                offset = (w - (options.formation_width - 1) / 2) * options.formation_spacing
                check_x = round(center_x + offset * perp_dx)
                check_y = round(center_y + offset * perp_dy)
                
                check_pos = GridPosition(check_x, check_y)
                if not self._is_position_valid_for_group(check_pos):
                    position_valid = False
                    break
            
            # If formation position is valid, add it to the path
            if position_valid:
                widened_path.append(pos)
            else:
                # Try to find an alternative position
                found_alternative = False
                for r in range(1, 4):  # Try up to 3 cells radius
                    for dx_alt in range(-r, r + 1):
                        for dy_alt in range(-r, r + 1):
                            if dx_alt == 0 and dy_alt == 0:
                                continue
                            
                            alt_pos = GridPosition(pos.x + dx_alt, pos.y + dy_alt)
                            
                            # Check if all formation positions are valid
                            alt_valid = True
                            for w in range(options.formation_width):
                                offset = (w - (options.formation_width - 1) / 2) * options.formation_spacing
                                check_x = round(alt_pos.x + offset * perp_dx)
                                check_y = round(alt_pos.y + offset * perp_dy)
                                
                                check_pos = GridPosition(check_x, check_y)
                                if not self._is_position_valid_for_group(check_pos):
                                    alt_valid = False
                                    break
                            
                            if alt_valid:
                                widened_path.append(alt_pos)
                                found_alternative = True
                                break
                        
                        if found_alternative:
                            break
                    
                    if found_alternative:
                        break
                
                # If no alternative found, just use original position
                if not found_alternative:
                    widened_path.append(pos)
        
        return widened_path

    # Helper methods for pathfinding
    def _calculate_heuristic(self, start: GridPosition, end: GridPosition) -> float:
        """Calculate the Manhattan distance heuristic for A* algorithm."""
        # Manhattan distance for grid
        return abs(start.x - end.x) + abs(start.y - end.y)

    def _get_lowest_f_cost_node(self, nodes: List[PathfindingNode]) -> PathfindingNode:
        """Find the node with the lowest F cost in the open set."""
        return min(nodes, key=lambda n: n.f_cost)

    def _reconstruct_path(self, end_node: PathfindingNode) -> List[GridPosition]:
        """Reconstruct the path from the end node back to the start."""
        path = []
        current = end_node
        while current:
            path.append(current.position)
            current = current.parent
        return list(reversed(path))

    def _position_to_string(self, pos: GridPosition) -> str:
        """Convert a position to a string key for the closed set."""
        return f"{pos.x},{pos.y}"

    def _get_walkable_neighbors(self, position: GridPosition, character_id: Optional[str] = None) -> List[GridPosition]:
        """
        Get valid, walkable neighbors for a position.
        
        Args:
            position: The position to find neighbors for
            character_id: Optional ID of the character (for collision checks)
            
        Returns:
            List of valid neighbor positions
        """
        # Use grid_manager to get valid, walkable, non-occupied neighbors (8-way)
        neighbors = []
        directions = [
            (-1, 0), (1, 0), (0, -1), (0, 1),  # Cardinal directions
            (-1, -1), (-1, 1), (1, -1), (1, 1)  # Diagonal directions
        ]
        
        for dx, dy in directions:
            nx, ny = position.x + dx, position.y + dy
            neighbor_pos = GridPosition(nx, ny)
            
            if self.grid_manager.is_valid_position(neighbor_pos):
                cell = self.grid_manager.get_cell_at(neighbor_pos)
                if cell and cell.walkable and not cell.is_occupied:
                    # For diagonal movement, check that both adjacent cells are walkable
                    if dx != 0 and dy != 0:
                        # Check that we can walk through both adjacent cells
                        adj1 = self.grid_manager.get_cell_at(GridPosition(position.x + dx, position.y))
                        adj2 = self.grid_manager.get_cell_at(GridPosition(position.x, position.y + dy))
                        
                        if not (adj1 and adj1.walkable and adj2 and adj2.walkable):
                            continue
                    
                    neighbors.append(neighbor_pos)
        
        return neighbors

    def _get_node_cost(self, node: PathfindingNode, from_pos: Optional[GridPosition] = None) -> float:
        """
        Calculate the cost of moving to a node.
        
        Args:
            node: The node to calculate cost for
            from_pos: The position we're moving from (for diagonal check)
            
        Returns:
            The movement cost
        """
        pos = node.position
        cell = self.grid_manager.get_cell_at(pos)
        
        if not cell:
            return float('inf')  # Invalid cell
        
        # Base cost by cell type
        cell_costs = {
            CellType.EMPTY: 1.0,
            CellType.ROAD: 0.8,  # Roads are faster
            CellType.ROUGH: 1.5,  # Rough terrain is slower
            CellType.WATER: 2.0,  # Water is much slower
            CellType.WALL: float('inf'),  # Walls are impassable
            CellType.BLOCKED: float('inf')  # Blocked cells are impassable
        }
        
        cost = cell_costs.get(cell.cell_type, 1.0)
        
        # Apply category rules if available
        rules = self.category_rules.get('default')
        if rules:
            if cell.cell_type in rules.preferred_types:
                cost *= 0.8  # Preferred cells are faster
            if cell.cell_type in rules.avoid_types:
                cost *= 1.5  # Avoided cells are slower
            
            cost *= rules.weight_multiplier
        
        # Diagonal movement costs more (approx. sqrt(2))
        if from_pos and from_pos.x != pos.x and from_pos.y != pos.y:
            cost *= 1.4
        
        return cost

    def _calculate_predictive_collision_cost(self, position: GridPosition) -> float:
        """
        Calculate additional cost for predictive collision avoidance.
        
        Args:
            position: Position to evaluate
            
        Returns:
            Additional cost based on predicted collisions
        """
        # Check for potential collisions with other entities
        collisions = self.collision_system.find_collisions(
            position, 
            GridPosition(1, 1)  # Assuming 1x1 entity size
        )
        
        if collisions:
            # Add cost proportional to number of collisions
            return len(collisions) * 2.0
        
        return 0.0

    def _is_position_valid_for_group(self, position: GridPosition) -> bool:
        """
        Check if a position is valid for group movement.
        
        Args:
            position: Position to check
            
        Returns:
            True if position is valid for group, False otherwise
        """
        if not self.grid_manager.is_valid_position(position):
            return False
        
        cell = self.grid_manager.get_cell_at(position)
        if not cell or not cell.walkable or cell.is_occupied:
            return False
        
        # Check for collisions
        collisions = self.collision_system.find_collisions(
            position,
            GridPosition(1, 1)  # Assuming 1x1 entity size
        )
        
        return len(collisions) == 0

    def set_category_rules(self, category: POICategory, rules: CategoryPathRules) -> None:
        """
        Set path rules for a specific POI category.
        
        Args:
            category: Name of the POI category
            rules: Rules for this category
        """
        self.category_rules[category] = rules

    def clear_cache(self) -> None:
        """Clear the path cache entirely."""
        self.path_cache.clear() 