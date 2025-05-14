"""
Tactical hex grid implementation for combat scenarios.
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from .hex_cell import HexCell, TerrainType, WeatherType
from .hex_grid import HexGrid
import math

@dataclass
class TacticalHexCell(HexCell):
    """A hex cell with additional tactical properties."""
    
    cover: float = 0.0  # 0-1, amount of cover provided
    movement_cost: int = 1  # Movement points required to enter
    terrain_effect: str = ''  # Special terrain effect (e.g., 'concealment')
    unit_occupants: List[str] = field(default_factory=list)  # List of unit IDs
    elevation: float = 0.0
    is_occupied: bool = False
    occupant_id: Optional[str] = None

    def serialize(self) -> Dict[str, Any]:
        """Convert the tactical cell to a dictionary."""
        base_data = super().serialize()
        base_data.update({
            'cover': self.cover,
            'movement_cost': self.movement_cost,
            'terrain_effect': self.terrain_effect,
            'unit_occupants': self.unit_occupants,
            'elevation': self.elevation,
            'is_occupied': self.is_occupied,
            'occupant_id': self.occupant_id
        })
        return base_data

    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> 'TacticalHexCell':
        """Create a TacticalHexCell from serialized data."""
        cell = cls(
            q=data['q'],
            r=data['r'],
            terrain=data['terrain'],
            elevation=data['elevation'],
            discovered=data['discovered'],
            weather=data.get('weather'),
            cover=data.get('cover', 0.0),
            movement_cost=data.get('movement_cost', 1),
            terrain_effect=data.get('terrain_effect', ''),
            unit_occupants=data.get('unit_occupants', []),
            is_occupied=data.get('is_occupied', False),
            occupant_id=data.get('occupant_id')
        )
        return cell

    def get_cube_coords(self) -> Tuple[int, int, int]:
        """Convert axial to cube coordinates."""
        x = self.q
        z = self.r
        y = -x - z
        return (x, y, z)

class TacticalHexGrid(HexGrid):
    """
    A specialized hex grid for tactical combat scenarios.
    Extends the base HexGrid with combat-specific functionality.
    """
    
    def __init__(self, radius: int = 10):
        """
        Initialize the tactical hex grid.
        
        Args:
            radius: Radius of the hex grid from center
        """
        super().__init__(radius * 2, radius * math.sqrt(3))
        self.cells: Dict[Tuple[int, int], TacticalHexCell] = {}
        self._initialize_grid()

    def _initialize_grid(self) -> None:
        """Initialize the hex grid with empty cells."""
        for q in range(-self.width // 2, self.width // 2 + 1):
            r1 = max(-self.width // 2, -q - self.width // 2)
            r2 = min(self.width // 2, -q + self.width // 2)
            for r in range(r1, r2 + 1):
                self.cells[(q, r)] = TacticalHexCell(q=q, r=r)

    def get_cell(self, q: int, r: int) -> Optional[TacticalHexCell]:
        """Get the tactical hex cell at the specified coordinates."""
        return self.cells.get((q, r))

    def set_elevation(self, x: int, y: int, elevation: float):
        """Set the elevation of a cell."""
        if cell := self.get_cell(x, y):
            cell.elevation = elevation

    def set_cover(self, x: int, y: int, cover: float):
        """Set the cover value of a cell."""
        if cell := self.get_cell(x, y):
            cell.cover = cover

    def set_movement_cost(self, x: int, y: int, cost: float):
        """Set the movement cost of a cell."""
        if cell := self.get_cell(x, y):
            cell.movement_cost = cost

    def occupy_cell(self, x: int, y: int, occupant_id: str):
        """Mark a cell as occupied by an entity."""
        if cell := self.get_cell(x, y):
            cell.is_occupied = True
            cell.occupant_id = occupant_id

    def clear_cell(self, x: int, y: int):
        """Clear the occupant from a cell."""
        if cell := self.get_cell(x, y):
            cell.is_occupied = False
            cell.occupant_id = None

    def get(self, q: int, r: int) -> Optional[TacticalHexCell]:
        """Get the tactical cell at the given coordinates."""
        return self.cells.get((q, r))

    def set_combat_props(self, q: int, r: int, props: Dict[str, Any]) -> None:
        """Set combat-related properties for a cell."""
        cell = self.get(q, r)
        if cell:
            if 'cover' in props:
                cell.cover = props['cover']
            if 'movement_cost' in props:
                cell.movement_cost = props['movement_cost']
            if 'terrain_effect' in props:
                cell.terrain_effect = props['terrain_effect']
            if 'unit_occupants' in props:
                cell.unit_occupants = props['unit_occupants']

    def add_unit(self, q: int, r: int, unit_id: str) -> None:
        """Add a unit to a cell."""
        cell = self.get(q, r)
        if cell and unit_id not in cell.unit_occupants:
            cell.unit_occupants.append(unit_id)

    def remove_unit(self, q: int, r: int, unit_id: str) -> None:
        """Remove a unit from a cell."""
        cell = self.get(q, r)
        if cell:
            cell.unit_occupants = [uid for uid in cell.unit_occupants if uid != unit_id]

    @classmethod
    def from_region_grid(cls, region_grid: HexGrid) -> 'TacticalHexGrid':
        """Create a tactical grid from a region grid, with appropriate combat properties."""
        grid = cls(region_grid.width // 2)
        
        for r in range(region_grid.height):
            for q in range(region_grid.width):
                region_cell = region_grid.get(q, r)
                tactical_cell = grid.get(q, r)
                
                if region_cell and tactical_cell:
                    tactical_cell.terrain = region_cell.terrain
                    tactical_cell.elevation = region_cell.elevation
                    tactical_cell.weather = region_cell.weather
                    
                    # Set combat props based on terrain
                    props = {
                        'forest': {
                            'cover': 0.7,
                            'movement_cost': 2,
                            'terrain_effect': 'concealment'
                        },
                        'mountain': {
                            'cover': 0.5,
                            'movement_cost': 3,
                            'terrain_effect': 'highground'
                        },
                        'urban': {
                            'cover': 0.9,
                            'movement_cost': 1,
                            'terrain_effect': 'hardcover'
                        },
                        'water': {
                            'cover': 0.0,
                            'movement_cost': 99,
                            'terrain_effect': 'impassable'
                        },
                        'desert': {
                            'cover': 0.1,
                            'movement_cost': 2,
                            'terrain_effect': 'exposure'
                        }
                    }
                    
                    terrain_props = props.get(region_cell.terrain, {
                        'cover': 0.2,
                        'movement_cost': 1,
                        'terrain_effect': ''
                    })
                    
                    grid.set_combat_props(q, r, terrain_props)
        
        return grid

    def get_neighbors_in_range(self, q: int, r: int, range_val: int) -> List[TacticalHexCell]:
        """Get all cells within a certain range of a position."""
        neighbors = []
        for dq in range(-range_val, range_val + 1):
            for dr in range(-range_val, range_val + 1):
                if abs(dq + dr) <= range_val:
                    cell = self.get(q + dq, r + dr)
                    if cell:
                        neighbors.append(cell)
        return neighbors

    def get_neighbors(self, q: int, r: int) -> List[TacticalHexCell]:
        """Get all neighboring cells for the given coordinates"""
        directions = [
            (1, 0), (1, -1), (0, -1),
            (-1, 0), (-1, 1), (0, 1)
        ]
        
        neighbors = []
        for dq, dr in directions:
            neighbor = self.get(q + dq, r + dr)
            if neighbor:
                neighbors.append(neighbor)
        return neighbors

    def get_distance(self, q1: int, r1: int, q2: int, r2: int) -> int:
        """Calculate the distance between two hexes using cube coordinates"""
        x1, y1, z1 = self.get_cell(q1, r1).get_cube_coords()
        x2, y2, z2 = self.get_cell(q2, r2).get_cube_coords()
        return max(abs(x1 - x2), abs(y1 - y2), abs(z1 - z2))

    def is_valid_position(self, x: int, y: int) -> bool:
        """Check if the given coordinates are within the grid bounds"""
        return 0 <= x < self.width and 0 <= y < self.height

    def clear_cell(self, x: int, y: int):
        """Clear all units and effects from a cell"""
        if (x, y) in self.cells:
            self.cells[(x, y)].unit_occupants.clear()
            self.cells[(x, y)].effects.clear()

    def get_line(self, q1: int, r1: int, q2: int, r2: int) -> List[TacticalHexCell]:
        """Get all cells in a line between two points."""
        N = self.get_distance(q1, r1, q2, r2)
        if N == 0:
            return [self.get_cell(q1, r1)]
            
        cells = []
        for i in range(N + 1):
            t = 1.0 * i / N
            q = round(q1 * (1-t) + q2 * t)
            r = round(r1 * (1-t) + r2 * t)
            cell = self.get_cell(q, r)
            if cell:
                cells.append(cell)
        return cells

    def get_ring(self, center_q: int, center_r: int, radius: int) -> List[TacticalHexCell]:
        """Get all cells at a certain distance from the center."""
        if radius == 0:
            cell = self.get_cell(center_q, center_r)
            return [cell] if cell else []
            
        results = []
        # Start at the top-right and work around
        q = center_q + radius
        r = center_r - radius
        
        directions = [
            (0, 1), (-1, 1), (-1, 0),
            (0, -1), (1, -1), (1, 0)
        ]
        
        for direction in directions:
            for _ in range(radius):
                cell = self.get_cell(q, r)
                if cell:
                    results.append(cell)
                q += direction[0]
                r += direction[1]
                
        return results

    def get_area(self, center_q: int, center_r: int, radius: int) -> List[TacticalHexCell]:
        """Get all cells within a certain distance of the center."""
        results = []
        for r in range(radius + 1):
            results.extend(self.get_ring(center_q, center_r, r))
        return results

    def find_path(self, start_q: int, start_r: int, end_q: int, end_r: int,
                  movement_cost_fn=None) -> Optional[List[TacticalHexCell]]:
        """
        Find a path between two cells using A* pathfinding.
        
        Args:
            start_q: Starting q coordinate
            start_r: Starting r coordinate
            end_q: Ending q coordinate
            end_r: Ending r coordinate
            movement_cost_fn: Optional function to calculate movement cost between cells
            
        Returns:
            List of cells forming the path, or None if no path exists
        """
        if movement_cost_fn is None:
            movement_cost_fn = lambda c1, c2: c2.movement_cost
            
        start_cell = self.get_cell(start_q, start_r)
        end_cell = self.get_cell(end_q, end_r)
        
        if not (start_cell and end_cell):
            return None
            
        # A* implementation
        from heapq import heappush, heappop
        
        frontier = []
        heappush(frontier, (0, start_cell))
        came_from = {start_cell: None}
        cost_so_far = {start_cell: 0}
        
        while frontier:
            current = heappop(frontier)[1]
            
            if current == end_cell:
                break
                
            for next_cell in self.get_neighbors(current.q, current.r):
                new_cost = cost_so_far[current] + movement_cost_fn(current, next_cell)
                
                if next_cell not in cost_so_far or new_cost < cost_so_far[next_cell]:
                    cost_so_far[next_cell] = new_cost
                    priority = new_cost + self.get_distance(next_cell.q, next_cell.r, end_q, end_r)
                    heappush(frontier, (priority, next_cell))
                    came_from[next_cell] = current
                    
        if end_cell not in came_from:
            return None
            
        # Reconstruct path
        current = end_cell
        path = []
        while current:
            path.append(current)
            current = came_from[current]
        path.reverse()
        
        return path 