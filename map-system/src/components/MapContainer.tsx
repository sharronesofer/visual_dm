import React, { useReducer, useCallback } from 'react';
import styled from 'styled-components';
import { MapContainerProps } from '../types/props';
import { MapState } from '../types/state';
import { MapContext } from '../contexts/MapContext';
import { mapReducer } from '../reducers/mapReducer';
import ViewportManager from './ViewportManager';
import TileLayer from './TileLayer';
import POILayer from './POILayer';
import MovementSystem from './MovementSystem';
import FogOfWar from './FogOfWar';
import RegionBorders from './RegionBorders';
import InfoPanel from './InfoPanel';

const initialState: MapState = {
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
};

const Container = styled.div`
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden;
  background: #2c3e50;
  touch-action: none;
`;

const MapContainer: React.FC<MapContainerProps> = ({
  children,
  initialState: propInitialState,
  onStateChange,
  className
}) => {
  const [state, dispatch] = useReducer(
    mapReducer,
    { ...initialState, ...propInitialState }
  );

  const handleStateChange = useCallback((newState: MapState) => {
    onStateChange?.(newState);
  }, [onStateChange]);

  return (
    <MapContext.Provider value={{ state, dispatch }}>
      <Container className={className}>
        <ViewportManager
          state={state.viewport}
          onStateChange={(viewport) => {
            dispatch({ type: 'UPDATE_VIEWPORT', payload: viewport });
            handleStateChange({ ...state, viewport });
          }}
        >
          <TileLayer
            tiles={state.tiles}
            viewport={state.viewport}
            selectedTile={state.selectedTile}
            hoveredTile={state.hoveredTile}
            onTileClick={(position) => 
              dispatch({ type: 'SELECT_TILE', payload: position })}
            onTileHover={(position) => 
              dispatch({ type: 'HOVER_TILE', payload: position })}
          />
          <RegionBorders
            regions={state.regions}
            viewport={state.viewport}
          />
          <POILayer
            pois={state.pois}
            viewport={state.viewport}
          />
          <MovementSystem
            state={state.movement}
            tiles={state.tiles}
            onStateChange={(movement) => {
              dispatch({ type: 'UPDATE_MOVEMENT', payload: movement });
              handleStateChange({ ...state, movement });
            }}
          />
          <FogOfWar
            tiles={state.tiles}
            viewport={state.viewport}
            currentPosition={state.movement.currentTile}
            visionRadius={2}
          />
        </ViewportManager>
        <InfoPanel
          tile={state.selectedTile ? state.tiles[`${state.selectedTile.x},${state.selectedTile.y}`] : undefined}
          poi={state.selectedTile ? state.pois[`${state.selectedTile.x},${state.selectedTile.y}`] : undefined}
          region={state.selectedTile ? 
            Object.values(state.regions).find(r => 
              r.boundaries.some(b => b.x === state.selectedTile?.x && b.y === state.selectedTile?.y)
            ) : undefined}
        />
        {children}
      </Container>
    </MapContext.Provider>
  );
};

export default MapContainer; 