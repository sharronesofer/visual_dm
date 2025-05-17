from typing import List, Dict, Optional, Any, Set, Tuple
from backend.utils.grid import GridManager, GridPosition, GridDimensions, CellType

class QuadTreeBounds:
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

class QuadTreeNode:
    def __init__(self, bounds: QuadTreeBounds, level: int):
        self.bounds = bounds
        self.objects: List[str] = []
        self.nodes: List[QuadTreeNode] = []
        self.level = level

class CollisionSystem:
    """
    CollisionSystem provides spatial partitioning and collision detection
    using a QuadTree data structure.
    """
    
    MAX_OBJECTS = 10
    MAX_LEVELS = 5
    
    def __init__(self, grid_manager: Optional[GridManager] = None):
        """
        Initialize the collision system with an optional grid manager.
        
        Args:
            grid_manager: The grid manager to use for additional collision checks
        """
        self.grid_manager = grid_manager
        
        # Initialize quadtree with grid dimensions or default values
        if grid_manager:
            width = grid_manager.get_width()
            height = grid_manager.get_height()
        else:
            width = 100
            height = 100
            
        bounds = QuadTreeBounds(0, 0, width, height)
        self.quad_tree = QuadTreeNode(bounds, 0)
    
    def clear(self) -> None:
        """Clear all objects from the collision system."""
        self.quad_tree.objects = []
        self.quad_tree.nodes = []
    
    def reset(self) -> None:
        """Reset the collision system (alias for clear)."""
        self.clear()
    
    def insert(self, object_id: str, position: GridPosition, dimensions: GridDimensions) -> None:
        """
        Insert an object into the collision system.
        
        Args:
            object_id: Unique identifier for the object
            position: Position of the object on the grid
            dimensions: Dimensions of the object
        """
        bounds = QuadTreeBounds(
            position.x,
            position.y,
            dimensions.width,
            dimensions.height
        )
        self._insert_into_node(self.quad_tree, object_id, bounds)
    
    def remove(self, object_id: str, position: GridPosition, dimensions: GridDimensions) -> None:
        """
        Remove an object from the collision system.
        
        Args:
            object_id: Unique identifier for the object
            position: Position of the object on the grid
            dimensions: Dimensions of the object
        """
        bounds = QuadTreeBounds(
            position.x,
            position.y,
            dimensions.width,
            dimensions.height
        )
        self._remove_from_node(self.quad_tree, object_id, bounds)
    
    def update(self, object_id: str, old_pos: GridPosition, new_pos: GridPosition, dimensions: GridDimensions) -> None:
        """
        Update an object's position in the collision system.
        
        Args:
            object_id: Unique identifier for the object
            old_pos: Previous position of the object
            new_pos: New position of the object
            dimensions: Dimensions of the object
        """
        self.remove(object_id, old_pos, dimensions)
        self.insert(object_id, new_pos, dimensions)
    
    def find_collisions(self, position: GridPosition, dimensions: GridDimensions) -> List[str]:
        """
        Find all objects that collide with the specified bounds.
        
        Args:
            position: Position to check for collisions
            dimensions: Dimensions of the area to check
            
        Returns:
            List of object IDs that collide with the specified bounds
        """
        bounds = QuadTreeBounds(
            position.x,
            position.y,
            dimensions.width,
            dimensions.height
        )
        
        potential_collisions = self._query_node(self.quad_tree, bounds)
        return [obj_id for obj_id in potential_collisions if self._check_detailed_collision(obj_id, bounds)]
    
    def find_valid_position(
        self,
        object_id: str,
        position: GridPosition,
        dimensions: GridDimensions,
        max_attempts: int = 10
    ) -> Optional[GridPosition]:
        """
        Find a valid position for an object near the specified position.
        
        Args:
            object_id: Unique identifier for the object
            position: Desired position of the object
            dimensions: Dimensions of the object
            max_attempts: Maximum number of positions to try
            
        Returns:
            A valid position, or None if no valid position was found
        """
        # Try original position first
        if self._is_position_valid(position, dimensions, object_id):
            return position
        
        # Try positions in expanding spiral pattern
        spiral_offsets = self._generate_spiral_offsets(max_attempts)
        for offset in spiral_offsets:
            new_pos = GridPosition(
                position.x + offset.x,
                position.y + offset.y
            )
            
            if self._is_position_valid(new_pos, dimensions, object_id):
                return new_pos
        
        return None
    
    def _insert_into_node(self, node: QuadTreeNode, object_id: str, bounds: QuadTreeBounds) -> None:
        """Insert an object into a quadtree node."""
        # If node has subnodes, insert into appropriate subnode
        if node.nodes:
            index = self._get_node_index(node, bounds)
            if index != -1:
                self._insert_into_node(node.nodes[index], object_id, bounds)
                return
        
        # Add object to this node
        node.objects.append(object_id)
        
        # Split if needed
        if len(node.objects) > self.MAX_OBJECTS and node.level < self.MAX_LEVELS:
            if not node.nodes:
                self._split(node)
            
            # Redistribute existing objects
            i = 0
            while i < len(node.objects):
                current_id = node.objects[i]
                current_bounds = self._get_bounds_for_object(current_id)
                index = self._get_node_index(node, current_bounds)
                
                if index != -1:
                    moved_id = node.objects.pop(i)
                    self._insert_into_node(node.nodes[index], moved_id, current_bounds)
                else:
                    i += 1
    
    def _remove_from_node(self, node: QuadTreeNode, object_id: str, bounds: QuadTreeBounds) -> None:
        """Remove an object from a quadtree node."""
        # If node has subnodes, try to remove from appropriate subnode
        if node.nodes:
            index = self._get_node_index(node, bounds)
            if index != -1:
                self._remove_from_node(node.nodes[index], object_id, bounds)
                return
        
        # Remove object from this node
        if object_id in node.objects:
            node.objects.remove(object_id)
    
    def _query_node(self, node: QuadTreeNode, bounds: QuadTreeBounds) -> List[str]:
        """Query a quadtree node for objects that may intersect the given bounds."""
        result = []
        
        # Get index for bounds
        index = self._get_node_index(node, bounds)
        
        # Add objects from this node
        result.extend(node.objects)
        
        # If node has subnodes and bounds fits in a subnode, add from that subnode
        if node.nodes:
            if index != -1:
                result.extend(self._query_node(node.nodes[index], bounds))
            else:
                # Bounds overlaps multiple nodes, check all
                for subnode in node.nodes:
                    if self._bounds_overlap(bounds, subnode.bounds):
                        result.extend(self._query_node(subnode, bounds))
        
        return result
    
    def _split(self, node: QuadTreeNode) -> None:
        """Split a quadtree node into four child nodes."""
        sub_width = node.bounds.width / 2
        sub_height = node.bounds.height / 2
        x = node.bounds.x
        y = node.bounds.y
        level = node.level + 1
        
        # Create the four child nodes (clockwise from top right)
        node.nodes = [
            # Top right
            QuadTreeNode(
                QuadTreeBounds(x + sub_width, y, sub_width, sub_height),
                level
            ),
            # Top left
            QuadTreeNode(
                QuadTreeBounds(x, y, sub_width, sub_height),
                level
            ),
            # Bottom left
            QuadTreeNode(
                QuadTreeBounds(x, y + sub_height, sub_width, sub_height),
                level
            ),
            # Bottom right
            QuadTreeNode(
                QuadTreeBounds(x + sub_width, y + sub_height, sub_width, sub_height),
                level
            )
        ]
    
    def _get_node_index(self, node: QuadTreeNode, bounds: QuadTreeBounds) -> int:
        """Determine which child node the given bounds fits within."""
        vertical_midpoint = node.bounds.x + (node.bounds.width / 2)
        horizontal_midpoint = node.bounds.y + (node.bounds.height / 2)
        
        fits_top = bounds.y < horizontal_midpoint and bounds.y + bounds.height < horizontal_midpoint
        fits_bottom = bounds.y > horizontal_midpoint
        fits_left = bounds.x < vertical_midpoint and bounds.x + bounds.width < vertical_midpoint
        fits_right = bounds.x > vertical_midpoint
        
        if fits_top and fits_right:
            return 0
        if fits_top and fits_left:
            return 1
        if fits_bottom and fits_left:
            return 2
        if fits_bottom and fits_right:
            return 3
        
        return -1
    
    def _bounds_overlap(self, a: QuadTreeBounds, b: QuadTreeBounds) -> bool:
        """Check if two bounding boxes overlap."""
        return (
            a.x < b.x + b.width and
            a.x + a.width > b.x and
            a.y < b.y + b.height and
            a.y + a.height > b.y
        )
    
    def _get_bounds_for_object(self, object_id: str) -> QuadTreeBounds:
        """
        Get the bounds for an object (stub method).
        In a real implementation, this would look up the object's position and dimensions.
        """
        # This is a stub that should be replaced with actual object lookup
        return QuadTreeBounds(0, 0, 1, 1)
    
    def _check_detailed_collision(self, object_id: str, bounds: QuadTreeBounds) -> bool:
        """
        Perform a detailed collision check between an object and bounds.
        In a real implementation, this would perform more precise collision detection.
        """
        # This is a simplified implementation; in a real system we'd use actual object bounds
        return True
    
    def _is_position_valid(
        self,
        position: GridPosition,
        dimensions: GridDimensions,
        exclude_id: Optional[str] = None
    ) -> bool:
        """
        Check if a position is valid for an object with the given dimensions.
        
        Args:
            position: Position to check
            dimensions: Dimensions of the object
            exclude_id: Object ID to exclude from collision checks
            
        Returns:
            True if the position is valid, False otherwise
        """
        # Check if position is within grid bounds
        if self.grid_manager:
            for y in range(position.y, position.y + dimensions.height):
                for x in range(position.x, position.x + dimensions.width):
                    check_pos = GridPosition(x, y)
                    if not self.grid_manager.is_valid_position(check_pos):
                        return False
                    
                    cell = self.grid_manager.get_cell_at(check_pos)
                    if cell and (not cell.walkable or cell.is_occupied):
                        return False
        
        # Check for collisions with other objects
        collisions = self.find_collisions(position, dimensions)
        if exclude_id and exclude_id in collisions:
            collisions.remove(exclude_id)
        
        return len(collisions) == 0
    
    def _generate_spiral_offsets(self, max_attempts: int) -> List[GridPosition]:
        """
        Generate a list of positions in a spiral pattern.
        
        Args:
            max_attempts: Maximum number of positions to generate
            
        Returns:
            List of grid positions in a spiral pattern
        """
        offsets = []
        x, y = 0, 0
        dx, dy = 0, -1
        
        for i in range(1, max_attempts + 1):
            if (-max_attempts // 2 <= x <= max_attempts // 2) and (-max_attempts // 2 <= y <= max_attempts // 2):
                if x != 0 or y != 0:  # Skip the center position (already checked)
                    offsets.append(GridPosition(x, y))
            
            # Turn according to spiral pattern
            if x == y or (x < 0 and x == -y) or (x > 0 and x == 1 - y):
                dx, dy = -dy, dx
            
            x, y = x + dx, y + dy
        
        return offsets 