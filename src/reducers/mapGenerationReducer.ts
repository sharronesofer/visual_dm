import { MapGenerationState } from '../contexts/MapGenerationContext';
import { MapData, MapChunk, Position } from '../types/map';

// Action types
type MapGenerationAction =
  | { type: 'SET_MAP_DATA'; payload: MapData }
  | { type: 'SET_GENERATING_MAP'; payload: boolean }
  | {
      type: 'SET_CHUNK_LOADING';
      payload: { position: Position; loading: boolean };
    }
  | { type: 'SET_CHUNK_DATA'; payload: { position: Position; chunk: MapChunk } }
  | { type: 'SET_CHUNK_ERROR'; payload: { position: Position; error: string } }
  | { type: 'SET_REGIONS_DISCOVERED'; payload: string[] }
  | { type: 'SET_ERROR'; payload: string | null };

// Initial state
export const initialState: MapGenerationState = {
  mapData: null,
  loading: false,
  error: null,
  generatingMap: false,
  loadingChunks: {},
};

// Helper function to get chunk key
const getChunkKey = (position: Position): string => `${position.x},${position.y}`;

// Reducer
export const mapGenerationReducer = (
  state: MapGenerationState,
  action: MapGenerationAction
): MapGenerationState => {
  switch (action.type) {
    case 'SET_MAP_DATA':
      return {
        ...state,
        mapData: action.payload,
        error: null,
      };

    case 'SET_GENERATING_MAP':
      return {
        ...state,
        generatingMap: action.payload,
      };

    case 'SET_CHUNK_LOADING': {
      const chunkKey = getChunkKey(action.payload.position);
      return {
        ...state,
        loadingChunks: {
          ...state.loadingChunks,
          [chunkKey]: action.payload.loading,
        },
      };
    }

    case 'SET_CHUNK_DATA': {
      if (!state.mapData) return state;

      const chunkKey = getChunkKey(action.payload.position);
      return {
        ...state,
        mapData: {
          ...state.mapData,
          chunks: {
            ...state.mapData.chunks,
            [chunkKey]: action.payload.chunk,
          },
        },
      };
    }

    case 'SET_CHUNK_ERROR': {
      if (!state.mapData) return state;

      const chunkKey = getChunkKey(action.payload.position);
      return {
        ...state,
        mapData: {
          ...state.mapData,
          chunks: {
            ...state.mapData.chunks,
            [chunkKey]: {
              ...state.mapData.chunks[chunkKey],
              error: action.payload.error,
              loading: false,
            },
          },
        },
      };
    }

    case 'SET_REGIONS_DISCOVERED': {
      if (!state.mapData) return state;

      const updatedChunks = { ...state.mapData.chunks };
      action.payload.forEach(regionId => {
        Object.values(updatedChunks).forEach(chunk => {
          if (chunk.regions[regionId]) {
            chunk.regions[regionId] = {
              ...chunk.regions[regionId],
              discovered: true,
            };
          }
        });
      });

      return {
        ...state,
        mapData: {
          ...state.mapData,
          chunks: updatedChunks,
        },
      };
    }

    case 'SET_ERROR':
      return {
        ...state,
        error: action.payload,
      };

    default:
      return state;
  }
};
