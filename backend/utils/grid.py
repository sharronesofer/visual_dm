from typing import List, Optional, Any
from backend.utils.pathfinding import CellType, GridPosition

class GridCell:
    def __init__(self, cell_type: CellType = CellType.EMPTY, walkable: bool = True, is_occupied: bool = False, occupied_by: Optional[Any] = None):
        self.cell_type = cell_type
        self.walkable = walkable
        self.is_occupied = is_occupied
        self.occupied_by = occupied_by

class GridDimensions:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height

class GridManager:
    def __init__(self, dimensions: GridDimensions):
        self.dimensions = dimensions
        self.cells: List[List[GridCell]] = [
            [GridCell() for _ in range(dimensions.width)]
            for _ in range(dimensions.height)
        ]

    def get_cell_at(self, position: GridPosition) -> Optional[GridCell]:
        if not self.is_valid_position(position):
            return None
        return self.cells[position.y][position.x]

    def set_cell_type(self, position: GridPosition, cell_type: CellType) -> None:
        if not self.is_valid_position(position):
            return
        cell = self.cells[position.y][position.x]
        cell.cell_type = cell_type
        cell.walkable = cell_type not in (CellType.WALL, CellType.BLOCKED)

    def set_occupied(self, position: GridPosition, occupied: bool) -> None:
        if not self.is_valid_position(position):
            return
        self.cells[position.y][position.x].is_occupied = occupied

    def is_valid_position(self, position: GridPosition) -> bool:
        return 0 <= position.x < self.dimensions.width and 0 <= position.y < self.dimensions.height

    def get_width(self) -> int:
        return self.dimensions.width

    def get_height(self) -> int:
        return self.dimensions.height

    def clear(self) -> None:
        self.cells = [
            [GridCell() for _ in range(self.dimensions.width)]
            for _ in range(self.dimensions.height)
        ]

    def to_serialized_data(self) -> dict:
        return {
            'dimensions': {'width': self.dimensions.width, 'height': self.dimensions.height},
            'cells': [
                [
                    {
                        'cell_type': cell.cell_type.name,
                        'is_occupied': cell.is_occupied,
                        'occupied_by': cell.occupied_by
                    } for cell in row
                ] for row in self.cells
            ]
        }

    @staticmethod
    def from_serialized_data(data: dict) -> 'GridManager':
        dims = GridDimensions(data['dimensions']['width'], data['dimensions']['height'])
        manager = GridManager(dims)
        manager.cells = [
            [
                GridCell(
                    cell_type=CellType[cell['cell_type']],
                    is_occupied=cell['is_occupied'],
                    occupied_by=cell['occupied_by']
                ) for cell in row
            ] for row in data['cells']
        ]
        return manager

    def get_building_by_id(self, building_id: str) -> Any:
        # TODO: Implement actual building lookup
        return None

    def get_room_by_id(self, room_id: str) -> Any:
        # TODO: Implement actual room lookup
        return None

    def get_door_by_id(self, door_id: str) -> Any:
        # TODO: Implement actual door lookup
        return None 