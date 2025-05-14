import { MapState, TileState, POIData, RegionState } from '../types/state';
import { MapAction } from '../types/props';
import { createTileKey } from '../types/state';

export const mapReducer = (state: MapState, action: MapAction): MapState => {
  switch (action.type) {
    case 'UPDATE_TILE': {
      const key = createTileKey(action.payload.position);
      const existingTile = state.tiles[key];
      const updatedTile = existingTile ? 
        { ...existingTile, ...action.payload.tile } as TileState : 
        action.payload.tile as TileState;
      
      if (!existingTile && !isValidTile(updatedTile)) {
        console.error('Invalid tile data:', action.payload);
        return state;
      }

      return {
        ...state,
        tiles: {
          ...state.tiles,
          [key]: updatedTile
        }
      };
    }

    case 'SELECT_TILE':
      return {
        ...state,
        selectedTile: action.payload
      };

    case 'HOVER_TILE':
      return {
        ...state,
        hoveredTile: action.payload
      };

    case 'UPDATE_VIEWPORT':
      return {
        ...state,
        viewport: {
          ...state.viewport,
          ...action.payload
        }
      };

    case 'UPDATE_MOVEMENT':
      return {
        ...state,
        movement: {
          ...state.movement,
          ...action.payload
        }
      };

    case 'UPDATE_POI': {
      const existingPOI = state.pois[action.payload.id];
      const updatedPOI = existingPOI ?
        { ...existingPOI, ...action.payload.poi } as POIData :
        action.payload.poi as POIData;

      if (!existingPOI && !isValidPOI(updatedPOI)) {
        console.error('Invalid POI data:', action.payload);
        return state;
      }

      return {
        ...state,
        pois: {
          ...state.pois,
          [action.payload.id]: updatedPOI
        }
      };
    }

    case 'UPDATE_REGION': {
      const existingRegion = state.regions[action.payload.id];
      const updatedRegion = existingRegion ?
        { ...existingRegion, ...action.payload.region } as RegionState :
        action.payload.region as RegionState;

      if (!existingRegion && !isValidRegion(updatedRegion)) {
        console.error('Invalid region data:', action.payload);
        return state;
      }

      return {
        ...state,
        regions: {
          ...state.regions,
          [action.payload.id]: updatedRegion
        }
      };
    }

    default:
      return state;
  }
};

// Type guards
function isValidTile(tile: Partial<TileState>): tile is TileState {
  return !!(
    tile.position &&
    tile.terrainType !== undefined &&
    tile.discovered !== undefined &&
    tile.visible !== undefined &&
    tile.selected !== undefined &&
    tile.movementCost !== undefined
  );
}

function isValidPOI(poi: Partial<POIData>): poi is POIData {
  return !!(
    poi.id &&
    poi.position &&
    poi.type &&
    poi.name &&
    poi.discovered !== undefined &&
    poi.interactable !== undefined
  );
}

function isValidRegion(region: Partial<RegionState>): region is RegionState {
  return !!(
    region.id &&
    region.boundaries &&
    region.discovered !== undefined &&
    region.name &&
    region.terrainDistribution
  );
} 