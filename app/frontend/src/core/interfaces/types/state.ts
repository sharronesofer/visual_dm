import { Position, TerrainType, POIType, Viewport, Dimensions } from './common';

// Base state interfaces
export interface TileState {
  position: Position;
  terrainType: TerrainType;
  visible: boolean;
  discovered: boolean;
  poi: boolean;
}

export interface POIData {
  id: string;
  position: Position;
  type: POIType;
  name: string;
  description: string;
  discovered: boolean;
}

// Viewport state
export interface ViewportState extends Viewport {
  minZoom: number;
  maxZoom: number;
  isDragging: boolean;
}

// Player state
export interface PlayerState {
  position: Position;
  visionRadius: number;
  faction: string;
  discoveredTiles: Set<string>;
  visitedPOIs: Set<string>;
}

// UI state
export interface UIState {
  selectedTile: Position | null;
  hoveredTile: Position | null;
  selectedPOI: string | null;
  hoveredPOI: string | null;
  isContextMenuOpen: boolean;
  contextMenuPosition: Position | null;
}

// Game state
export interface GameState {
  turn: number;
  phase: 'movement' | 'action' | 'end';
  isPlayerTurn: boolean;
  availableMoves: Position[];
  availableActions: string[];
}

// Root state interface
export interface MapState {
  tiles: Record<string, TileState>;
  pois: Record<string, POIData>;
  viewport: ViewportState;
  player: PlayerState;
  ui: UIState;
  game: GameState;
}

// Action types
export type ActionType =
  | { type: 'MOVE_PLAYER'; payload: Position }
  | { type: 'UPDATE_VIEWPORT'; payload: Partial<ViewportState> }
  | { type: 'SELECT_TILE'; payload: Position | null }
  | { type: 'HOVER_TILE'; payload: Position | null }
  | { type: 'SELECT_POI'; payload: string | null }
  | { type: 'HOVER_POI'; payload: string | null }
  | { type: 'DISCOVER_TILE'; payload: Position }
  | { type: 'VISIT_POI'; payload: string }
  | { type: 'SET_GAME_PHASE'; payload: GameState['phase'] }
  | { type: 'CALCULATE_AVAILABLE_MOVES'; payload: Position[] }
  | { type: 'END_TURN' }
  | { type: 'TOGGLE_CONTEXT_MENU'; payload: Position | null };
