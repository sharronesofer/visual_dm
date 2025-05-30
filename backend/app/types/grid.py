from typing import Any, Dict, List
from enum import Enum


class GridPosition:
    x: float
    y: float
class GridDimensions:
    width: float
    height: float
class GridCell:
    position: \'GridPosition\'
    isOccupied: bool
    buildingId?: str
    cellType: \'CellType\'
    walkable: bool
    tags: List[str]
class Grid:
    dimensions: \'GridDimensions\'
    cells: List[List[GridCell]]
    buildings: Dict[str, GridPosition>
class CellType(Enum):
    EMPTY = 'EMPTY'
    BUILDING = 'BUILDING'
    ROAD = 'ROAD'
    WALL = 'WALL'
    ENTRANCE = 'ENTRANCE'
    BLOCKED = 'BLOCKED'
class PathfindingNode:
    position: \'GridPosition\'
    gCost: float
    hCost: float
    parent?: \'PathfindingNode\' 