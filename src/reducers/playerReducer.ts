import { Position } from '../types/common';
import { PlayerState, MovementState, MovementDirection } from '../types/player';

// Action types
type PlayerAction =
  | { type: 'SET_POSITION'; payload: Position }
  | { type: 'SET_TARGET_POSITION'; payload: Position | null }
  | { type: 'SET_MOVEMENT_STATE'; payload: MovementState }
  | { type: 'SET_FACING'; payload: MovementDirection }
  | { type: 'SET_VISION_RADIUS'; payload: number }
  | { type: 'ADD_DISCOVERED_REGIONS'; payload: string[] }
  | { type: 'ADD_VISITED_POI'; payload: string };

// Initial state
export const initialState: PlayerState = {
  position: { x: 0, y: 0 },
  targetPosition: null,
  movementState: 'idle',
  facing: 'south',
  visionRadius: 3,
  discoveredRegions: new Set<string>(),
  visitedPOIs: new Set<string>(),
};

// Reducer
export const playerReducer = (state: PlayerState, action: PlayerAction): PlayerState => {
  switch (action.type) {
    case 'SET_POSITION':
      return {
        ...state,
        position: action.payload,
      };

    case 'SET_TARGET_POSITION':
      return {
        ...state,
        targetPosition: action.payload,
      };

    case 'SET_MOVEMENT_STATE':
      return {
        ...state,
        movementState: action.payload,
      };

    case 'SET_FACING':
      return {
        ...state,
        facing: action.payload,
      };

    case 'SET_VISION_RADIUS':
      return {
        ...state,
        visionRadius: action.payload,
      };

    case 'ADD_DISCOVERED_REGIONS': {
      const newDiscoveredRegions = new Set(state.discoveredRegions);
      action.payload.forEach(regionId => newDiscoveredRegions.add(regionId));
      return {
        ...state,
        discoveredRegions: newDiscoveredRegions,
      };
    }

    case 'ADD_VISITED_POI': {
      const newVisitedPOIs = new Set(state.visitedPOIs);
      newVisitedPOIs.add(action.payload);
      return {
        ...state,
        visitedPOIs: newVisitedPOIs,
      };
    }

    default:
      return state;
  }
};
