import { Position, Rectangle } from '../common/geometry';

/**
 * Map types used across the application
 */

/** Map region type */
export type RegionType = 'city' | 'dungeon' | 'wilderness' | 'custom';

/** Map region interface */
export interface Region {
  id: string;
  name: string;
  type: RegionType;
  bounds: Rectangle;
  parentId?: string;
  children?: string[];
  metadata?: Record<string, unknown>;
}

/** Point of Interest type */
export type POIType =
  | 'npc'
  | 'quest'
  | 'shop'
  | 'landmark'
  | 'encounter'
  | 'custom';

/** Point of Interest interface */
export interface POI {
  id: string;
  name: string;
  type: POIType;
  position: Position;
  regionId: string;
  description?: string;
  icon?: string;
  metadata?: Record<string, unknown>;
}

/** Map view state interface */
export interface MapViewState {
  center: Position;
  zoom: number;
  rotation: number;
  selectedRegionId?: string;
  selectedPOIId?: string;
  visibleRegionIds: Set<string>;
  visiblePOIIds: Set<string>;
}

/** Map interaction mode */
export type MapInteractionMode = 'pan' | 'select' | 'draw' | 'edit';

/** Map interaction state */
export interface MapInteractionState {
  mode: MapInteractionMode;
  isDragging: boolean;
  isDrawing: boolean;
  isEditing: boolean;
  startPosition?: Position;
  currentPosition?: Position;
}

/** Map data interface */
export interface MapData {
  regions: Record<string, Region>;
  pois: Record<string, POI>;
  metadata?: Record<string, unknown>;
}

/** Helper function to create a region */
export const createRegion = (
  id: string,
  name: string,
  type: RegionType,
  bounds: Rectangle,
  options: Partial<Omit<Region, 'id' | 'name' | 'type' | 'bounds'>> = {}
): Region => ({
  id,
  name,
  type,
  bounds,
  ...options,
});

/** Helper function to create a POI */
export const createPOI = (
  id: string,
  name: string,
  type: POIType,
  position: Position,
  regionId: string,
  options: Partial<
    Omit<POI, 'id' | 'name' | 'type' | 'position' | 'regionId'>
  > = {}
): POI => ({
  id,
  name,
  type,
  position,
  regionId,
  ...options,
});

/** Helper function to create map view state */
export const createMapViewState = (
  center: Position,
  zoom: number = 1,
  rotation: number = 0
): MapViewState => ({
  center,
  zoom,
  rotation,
  visibleRegionIds: new Set(),
  visiblePOIIds: new Set(),
});

/** Helper function to create map interaction state */
export const createMapInteractionState = (
  mode: MapInteractionMode = 'pan'
): MapInteractionState => ({
  mode,
  isDragging: false,
  isDrawing: false,
  isEditing: false,
});

/** Helper function to create map data */
export const createMapData = (
  regions: Record<string, Region> = {},
  pois: Record<string, POI> = {},
  metadata?: Record<string, unknown>
): MapData => ({
  regions,
  pois,
  metadata,
});
