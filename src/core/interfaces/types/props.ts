import { Position, Viewport } from './common';
import { TileState, POIData } from './state';

export interface MapContainerProps {
  className?: string;
}

export interface ViewportManagerProps {
  viewport: Viewport;
  onViewportChange: (viewport: Viewport) => void;
  children: React.ReactNode;
  className?: string;
}

export interface TileLayerProps {
  tiles: Record<string, TileState>;
  viewport: Viewport;
  selectedTile: Position | null;
  hoveredTile: Position | null;
  onTileClick?: (position: Position) => void;
  onTileHover?: (position: Position) => void;
  className?: string;
}

export interface TileProps {
  state: TileState;
  selected: boolean;
  hovered: boolean;
  onClick?: () => void;
  onHover?: () => void;
  className?: string;
}

export interface POILayerProps {
  pois: Record<string, POIData>;
  viewport: Viewport;
  onPOIClick?: (id: string) => void;
  onPOIHover?: (id: string | null) => void;
  className?: string;
}

export interface FogOfWarProps {
  tiles: Record<string, TileState>;
  viewport: Viewport;
  currentPosition: Position;
  visionRadius: number;
  className?: string;
}
