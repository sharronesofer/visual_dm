export interface GridPosition {
  x: number;
  y: number;
}

export interface GridDimensions {
  width: number;
  height: number;
}

export interface GridCell {
  position: GridPosition;
  isOccupied: boolean;
  buildingId?: string;
  cellType: CellType;
  walkable: boolean;
  tags: string[];
}

export interface Grid {
  dimensions: GridDimensions;
  cells: GridCell[][];
  buildings: Map<string, GridPosition>;
}

export enum CellType {
  EMPTY = 'EMPTY',
  BUILDING = 'BUILDING',
  ROAD = 'ROAD',
  WALL = 'WALL',
  ENTRANCE = 'ENTRANCE',
  BLOCKED = 'BLOCKED'
}

export interface PathfindingNode {
  position: GridPosition;
  gCost: number;  // Cost from start
  hCost: number;  // Estimated cost to end
  parent?: PathfindingNode;
} 