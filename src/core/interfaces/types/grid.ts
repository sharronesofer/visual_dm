export interface GridPosition {
  x: number;
  y: number;
}

export interface GridDimensions {
  width: number;
  height: number;
}

export interface GridCell {
  cellType: CellType;
  walkable: boolean;
  isOccupied: boolean;
  occupiedBy: string | null;
  buildingId?: string | null;
}

export enum CellType {
  EMPTY = 'EMPTY',
  OCCUPIED = 'OCCUPIED',
  BLOCKED = 'BLOCKED',
  PATH = 'PATH',
  WATER = 'WATER',
  MOUNTAIN = 'MOUNTAIN',
  FOREST = 'FOREST',
  WALL = 'WALL',
  ROAD = 'ROAD',
  ROUGH = 'ROUGH'
}

export interface PathfindingNode {
  position: GridPosition;
  gCost: number;
  hCost: number;
  parent?: PathfindingNode;
}

export interface GroupPathfindingOptions {
  groupSize?: number;
  formationWidth?: number;
  formationSpacing?: number;
  predictiveAvoidance?: boolean;
}

export interface PathfindingSystem {
  findPath(start: GridPosition, end: GridPosition): GridPosition[];
  findGroupPath(start: GridPosition, end: GridPosition, options: GroupPathfindingOptions): GridPosition[];
  isPathPossible(start: GridPosition, end: GridPosition): boolean;
  findAccessibleArea(start: GridPosition, maxDistance: number): Set<string>;
} 