"""
Base hex grid implementation.
"""

from typing import Dict, List, Optional, Tuple, Any
from .hex_cell import HexCell, TerrainType

# Axial coordinate directions for neighboring hexes
AXIAL_DIRECTIONS = [
    (1, 0), (1, -1), (0, -1),
    (-1, 0), (-1, 1), (0, 1)
]

class HexGrid:
    """Base class for hex grid systems."""
    
    def __init__(self, width: float, height: float):
        """
        Initialize a hex grid.
        
        Args:
            width: Width of the grid in hex units
            height: Height of the grid in hex units
        """
        self.width = width
        self.height = height
        self.cells: Dict[Tuple[int, int], HexCell] = {}
    
    def get(self, q: int, r: int) -> Optional[HexCell]:
        """Get the cell at the given coordinates."""
        return self.cells.get((q, r))
    
    def set(self, q: int, r: int, cell: HexCell) -> None:
        """Set the cell at the given coordinates."""
        self.cells[(q, r)] = cell
    
    def remove(self, q: int, r: int) -> None:
        """Remove the cell at the given coordinates."""
        if (q, r) in self.cells:
            del self.cells[(q, r)]
    
    def get_all_cells(self) -> List[HexCell]:
        """Get all cells in the grid."""
        return list(self.cells.values())
    
    def clear(self) -> None:
        """Remove all cells from the grid."""
        self.cells.clear()
    
    def is_valid_position(self, q: int, r: int) -> bool:
        """Check if the given coordinates are within the grid bounds."""
        return -self.width/2 <= q <= self.width/2 and -self.height/2 <= r <= self.height/2
    
    def serialize(self) -> Dict[str, Any]:
        """Convert the grid to a dictionary."""
        return {
            'width': self.width,
            'height': self.height,
            'cells': {
                f"{q},{r}": cell.serialize()
                for (q, r), cell in self.cells.items()
            }
        }
    
    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> 'HexGrid':
        """Create a HexGrid from serialized data."""
        grid = cls(
            width=data['width'],
            height=data['height']
        )
        
        for coord_str, cell_data in data['cells'].items():
            q, r = map(int, coord_str.split(','))
            grid.cells[(q, r)] = HexCell.deserialize(cell_data)
        
        return grid

    def initialize_cells(self):
        """Initialize the grid with basic hex cells."""
        for x in range(self.width):
            for y in range(self.height):
                self.cells[(x, y)] = HexCell(x=x, y=y)

    def get_neighbors(self, x: int, y: int) -> List[HexCell]:
        """Get all neighboring cells for the given coordinates."""
        # Axial coordinate neighbor offsets
        neighbors = []
        directions = [
            (1, 0), (1, -1), (0, -1),
            (-1, 0), (-1, 1), (0, 1)
        ]
        
        for dx, dy in directions:
            new_x, new_y = x + dx, y + dy
            if 0 <= new_x < self.width and 0 <= new_y < self.height:
                if cell := self.get_cell(new_x, new_y):
                    neighbors.append(cell)
        
        return neighbors

    def distance(self, x1: int, y1: int, x2: int, y2: int) -> int:
        """Calculate the distance between two hex cells."""
        # In axial coordinates, distance is max absolute value of the differences
        return max(abs(x2 - x1), abs(y2 - y1), abs((x2 + y2) - (x1 + y1)))

    def set_terrain(self, q: int, r: int, terrain: TerrainType) -> None:
        """Set the terrain type for a cell."""
        cell = self.get_cell(q, r)
        if cell:
            cell.terrain = terrain

    def get_cell(self, x: int, y: int) -> Optional[HexCell]:
        """Get the hex cell at the specified coordinates."""
        return self.cells.get((x, y))

    def is_valid_coordinate(self, x: int, y: int) -> bool:
        """Check if the given coordinates are within the grid bounds."""
        return 0 <= x < self.width and 0 <= y < self.height

    def get_neighbors(self, x: int, y: int) -> List[HexCell]:
        """Get all neighboring cells for the given coordinates."""
        # Axial coordinate neighbor offsets
        neighbors = []
        directions = [
            (1, 0), (1, -1), (0, -1),
            (-1, 0), (-1, 1), (0, 1)
        ]
        
        for dx, dy in directions:
            new_x, new_y = x + dx, y + dy
            if 0 <= new_x < self.width and 0 <= new_y < self.height:
                if cell := self.get_cell(new_x, new_y):
                    neighbors.append(cell)
        
        return neighbors 