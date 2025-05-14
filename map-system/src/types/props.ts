import { ReactNode } from 'react';
import { 
  Position, 
  Dimensions, 
  TerrainType,
  MovementType,
  FactionAffiliation
} from './common';
import {
  TileState,
  ViewportState,
  MovementState,
  POIData,
  RegionState,
  MapState
} from './state';

export interface MapContainerProps {
  children?: ReactNode;
  initialState?: Partial<MapState>;
  onStateChange?: (state: MapState) => void;
  className?: string;
}

export interface ViewportManagerProps {
  children?: ReactNode;
  state: ViewportState;
  onStateChange: (state: ViewportState) => void;
  onDrag?: (offset: Position) => void;
  onZoom?: (zoom: number) => void;
  className?: string;
}

export interface TileLayerProps {
  tiles: Record<string, TileState>;
  viewport: ViewportState;
  onTileClick?: (position: Position) => void;
  onTileHover?: (position: Position | null) => void;
  selectedTile?: Position;
  hoveredTile?: Position;
  className?: string;
}

export interface TileProps {
  state: TileState;
  selected?: boolean;
  hovered?: boolean;
  onClick?: () => void;
  onHover?: () => void;
  className?: string;
}

export interface POILayerProps {
  pois: Record<string, POIData>;
  viewport: ViewportState;
  onPOIClick?: (id: string) => void;
  onPOIHover?: (id: string | null) => void;
  className?: string;
}

export interface MovementSystemProps {
  state: MovementState;
  tiles: Record<string, TileState>;
  onStateChange: (state: MovementState) => void;
  onPathUpdate?: (path: Position[]) => void;
  className?: string;
}

export interface FogOfWarProps {
  tiles: Record<string, TileState>;
  viewport: ViewportState;
  currentPosition: Position;
  visionRadius: number;
  className?: string;
}

export interface RegionBorderProps {
  region: RegionState;
  viewport: ViewportState;
  discovered: boolean;
  className?: string;
}

export interface InfoPanelProps {
  tile?: TileState;
  poi?: POIData;
  region?: RegionState;
  className?: string;
}

// Context Props
export interface MapContextValue {
  state: MapState;
  dispatch: (action: MapAction) => void;
}

// Action Types
export type MapAction = 
  | { type: 'UPDATE_TILE'; payload: { position: Position; tile: Partial<TileState> } }
  | { type: 'SELECT_TILE'; payload: Position | undefined }
  | { type: 'HOVER_TILE'; payload: Position | undefined }
  | { type: 'UPDATE_VIEWPORT'; payload: Partial<ViewportState> }
  | { type: 'UPDATE_MOVEMENT'; payload: Partial<MovementState> }
  | { type: 'UPDATE_POI'; payload: { id: string; poi: Partial<POIData> } }
  | { type: 'UPDATE_REGION'; payload: { id: string; region: Partial<RegionState> } }; 