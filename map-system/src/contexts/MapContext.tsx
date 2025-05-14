import { createContext } from 'react';
import { MapContextValue } from '../types/props';

export const MapContext = createContext<MapContextValue>({
  state: {
    tiles: {},
    regions: {},
    pois: {},
    viewport: {
      offset: { x: 0, y: 0 },
      zoom: 1,
      visibleRange: {
        start: { x: 0, y: 0 },
        end: { x: 0, y: 0 }
      },
      loading: false,
      dimensions: {
        width: 0,
        height: 0
      }
    },
    movement: {
      active: false,
      currentTile: { x: 0, y: 0 },
      movementCost: 0,
      availableMoves: [],
      movementType: 'walk',
      isMoving: false
    }
  },
  dispatch: () => {
    console.warn('MapContext: dispatch not implemented');
  }
}); 