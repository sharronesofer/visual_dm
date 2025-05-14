from typing import Any, List, Union
from enum import Enum


class GridPosition:
    x: float
    y: float
class GridDimensions:
    width: float
    height: float
class GridCell:
    cellType: \'CellType\'
    walkable: bool
    isOccupied: bool
    occupiedBy: Union[str, None]
    buildingId?: Union[str, None]
class CellType(Enum):
    EMPTY = 'EMPTY'
    OCCUPIED = 'OCCUPIED'
    BLOCKED = 'BLOCKED'
    PATH = 'PATH'
    WATER = 'WATER'
    MOUNTAIN = 'MOUNTAIN'
    FOREST = 'FOREST'
    WALL = 'WALL'
    ROAD = 'ROAD'
    ROUGH = 'ROUGH'
class PathfindingNode:
    position: \'GridPosition\'
    gCost: float
    hCost: float
    parent?: \'PathfindingNode\'
class GroupPathfindingOptions:
    groupSize?: float
    formationWidth?: float
    formationSpacing?: float
    predictiveAvoidance?: bool
class PathfindingSystem:
    findPath(start: List[GridPosition, end: GridPosition): GridPosition]
    findGroupPath(start: List[GridPosition, end: \'GridPosition\', options: GroupPathfindingOptions): GridPosition]
    isPathPossible(start: \'GridPosition\', end: GridPosition): bool
    findAccessibleArea(start: \'GridPosition\', maxDistance: float): Set[str> 