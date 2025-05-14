import {
  MapState,
  ActionType,
  ViewportState,
  UIState,
  GameState,
  PlayerState,
} from '../types/state';
import { Position } from '../types/common';

// Helper function to calculate tile key
const getTileKey = (position: Position): string => `${position.x},${position.y}`;

// Viewport reducer
const viewportReducer = (state: ViewportState, action: ActionType): ViewportState => {
  switch (action.type) {
    case 'UPDATE_VIEWPORT':
      return { ...state, ...action.payload };
    default:
      return state;
  }
};

// UI reducer
const uiReducer = (state: UIState, action: ActionType): UIState => {
  switch (action.type) {
    case 'SELECT_TILE':
      return { ...state, selectedTile: action.payload };
    case 'HOVER_TILE':
      return { ...state, hoveredTile: action.payload };
    case 'SELECT_POI':
      return { ...state, selectedPOI: action.payload };
    case 'HOVER_POI':
      return { ...state, hoveredPOI: action.payload };
    case 'TOGGLE_CONTEXT_MENU':
      return {
        ...state,
        isContextMenuOpen: action.payload !== null,
        contextMenuPosition: action.payload,
      };
    default:
      return state;
  }
};

// Game reducer
const gameReducer = (state: GameState, action: ActionType): GameState => {
  switch (action.type) {
    case 'SET_GAME_PHASE':
      return { ...state, phase: action.payload };
    case 'CALCULATE_AVAILABLE_MOVES':
      return { ...state, availableMoves: action.payload };
    case 'END_TURN':
      return {
        ...state,
        turn: state.turn + 1,
        phase: 'movement',
        isPlayerTurn: !state.isPlayerTurn,
        availableMoves: [],
        availableActions: [],
      };
    default:
      return state;
  }
};

// Player reducer
const playerReducer = (state: PlayerState, action: ActionType): PlayerState => {
  switch (action.type) {
    case 'MOVE_PLAYER':
      return { ...state, position: action.payload };
    case 'DISCOVER_TILE':
      return {
        ...state,
        discoveredTiles: new Set([...state.discoveredTiles, getTileKey(action.payload)]),
      };
    case 'VISIT_POI':
      return {
        ...state,
        visitedPOIs: new Set([...state.visitedPOIs, action.payload]),
      };
    default:
      return state;
  }
};

// Root reducer
export const mapReducer = (state: MapState, action: ActionType): MapState => {
  // Handle complex state updates that affect multiple slices
  switch (action.type) {
    case 'MOVE_PLAYER': {
      const newPlayer = playerReducer(state.player, action);
      // Calculate new visible tiles and update game state
      const newTiles = { ...state.tiles };
      const visibleTileKeys = calculateVisibleTiles(newPlayer.position, newPlayer.visionRadius);

      visibleTileKeys.forEach(key => {
        if (newTiles[key]) {
          newTiles[key] = { ...newTiles[key], visible: true, discovered: true };
        }
      });

      return {
        ...state,
        tiles: newTiles,
        player: newPlayer,
        game: gameReducer(state.game, {
          type: 'SET_GAME_PHASE',
          payload: 'action',
        }),
      };
    }

    // Handle individual slice updates
    case 'UPDATE_VIEWPORT':
      return { ...state, viewport: viewportReducer(state.viewport, action) };
    case 'SELECT_TILE':
    case 'HOVER_TILE':
    case 'SELECT_POI':
    case 'HOVER_POI':
    case 'TOGGLE_CONTEXT_MENU':
      return { ...state, ui: uiReducer(state.ui, action) };
    case 'SET_GAME_PHASE':
    case 'CALCULATE_AVAILABLE_MOVES':
    case 'END_TURN':
      return { ...state, game: gameReducer(state.game, action) };
    case 'DISCOVER_TILE':
    case 'VISIT_POI':
      return { ...state, player: playerReducer(state.player, action) };
    default:
      return state;
  }
};

// Helper function to calculate visible tiles
const calculateVisibleTiles = (position: Position, radius: number): string[] => {
  const visibleTiles: string[] = [];
  for (let dx = -radius; dx <= radius; dx++) {
    for (let dy = -radius; dy <= radius; dy++) {
      if (Math.sqrt(dx * dx + dy * dy) <= radius) {
        visibleTiles.push(getTileKey({ x: position.x + dx, y: position.y + dy }));
      }
    }
  }
  return visibleTiles;
};
