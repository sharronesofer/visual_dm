import { Position, TerrainType, VisibilityState, MovementType, FactionAffiliation, Range } from './common';

export interface TileState {
  position: Position;
  terrainType: TerrainType;
  discovered: boolean;
  visible: boolean;
  selected: boolean;
  movementCost: number;
  faction?: FactionAffiliation;
  poi?: POIData;
}

export interface ViewportState {
  offset: Position;
  zoom: number;
  visibleRange: Range;
  loading: boolean;
  dimensions: {
    width: number;
    height: number;
  };
}

export interface MovementState {
  active: boolean;
  path?: Position[];
  startTile?: Position;
  endTile?: Position;
  currentTile: Position;
  movementCost: number;
  availableMoves: Position[];
  movementType: MovementType;
  isMoving: boolean;
}

export interface POIData {
  id: string;
  position: Position;
  type: string;
  name: string;
  description?: string;
  faction?: FactionAffiliation;
  discovered: boolean;
  interactable: boolean;
}

export interface RegionState {
  id: string;
  boundaries: Position[];
  discovered: boolean;
  name: string;
  faction?: FactionAffiliation;
  terrainDistribution: Record<TerrainType, number>;
}

export interface MapState {
  tiles: Record<string, TileState>;
  regions: Record<string, RegionState>;
  pois: Record<string, POIData>;
  viewport: ViewportState;
  movement: MovementState;
  selectedTile?: Position;
  hoveredTile?: Position;
}

// Helper type for tile coordinate string
export type TileKey = `${number},${number}`;

// Helper functions
export const createTileKey = (position: Position): TileKey => 
  `${position.x},${position.y}`;

export const parseTileKey = (key: TileKey): Position => {
  const [xStr, yStr] = key.split(',');
  const x = Number(xStr);
  const y = Number(yStr);
  
  if (isNaN(x) || isNaN(y)) {
    throw new Error(`Invalid tile key: ${key}`);
  }
  
  return { x, y };
}; 