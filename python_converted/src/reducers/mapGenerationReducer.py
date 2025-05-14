from typing import Any, Dict, List, Union


MapGenerationAction = Union[, { type: 'SET_MAP_DATA'] payload: MapData }
  | { type: 'SET_GENERATING_MAP'; payload: bool }
  | {
      type: 'SET_CHUNK_LOADING'
      payload: Dict[str, Any]
    }
  | { type: 'SET_CHUNK_DATA'; payload: Dict[str, Any] }
  | { type: 'SET_CHUNK_ERROR'; payload: Dict[str, Any] }
  | { type: 'SET_REGIONS_DISCOVERED'; payload: List[string] }
  | { type: 'SET_ERROR'; payload: str | null }
const initialState: MapGenerationState = {
  mapData: null,
  loading: false,
  error: null,
  generatingMap: false,
  loadingChunks: {},
}
const getChunkKey = (position: Position): str => `${position.x},${position.y}`
const mapGenerationReducer = (
  state: MapGenerationState,
  action: MapGenerationAction
): MapGenerationState => {
  switch (action.type) {
    case 'SET_MAP_DATA':
      return {
        ...state,
        mapData: action.payload,
        error: null,
      }
    case 'SET_GENERATING_MAP':
      return {
        ...state,
        generatingMap: action.payload,
      }
    case 'SET_CHUNK_LOADING': {
      const chunkKey = getChunkKey(action.payload.position)
      return {
        ...state,
        loadingChunks: Dict[str, Any],
      }
    }
    case 'SET_CHUNK_DATA': {
      if (!state.mapData) return state
      const chunkKey = getChunkKey(action.payload.position)
      return {
        ...state,
        mapData: Dict[str, Any],
        },
      }
    }
    case 'SET_CHUNK_ERROR': {
      if (!state.mapData) return state
      const chunkKey = getChunkKey(action.payload.position)
      return {
        ...state,
        mapData: Dict[str, Any],
          },
        },
      }
    }
    case 'SET_REGIONS_DISCOVERED': {
      if (!state.mapData) return state
      const updatedChunks = { ...state.mapData.chunks }
      action.payload.forEach(regionId => {
        Object.values(updatedChunks).forEach(chunk => {
          if (chunk.regions[regionId]) {
            chunk.regions[regionId] = {
              ...chunk.regions[regionId],
              discovered: true,
            }
          }
        })
      })
      return {
        ...state,
        mapData: Dict[str, Any],
      }
    }
    case 'SET_ERROR':
      return {
        ...state,
        error: action.payload,
      }
    default:
      return state
  }
}