import React from 'react';

/**
 * Represents a geographic coordinate
 */
export type Coordinate = [number, number]; // [longitude, latitude]

/**
 * Represents a bounding box in the format [minLng, minLat, maxLng, maxLat]
 */
export type BoundingBox = [number, number, number, number];

/**
 * Represents a geographic region with boundaries and metadata
 */
export interface Region {
  id: string;
  name: string;
  boundaries: Coordinate[][]; // Array of polygon rings (first is outer, rest are holes)
  properties: {
    population?: number;
    area?: number;
    code?: string;
    color?: string;
    [key: string]: any;
  };
  center?: Coordinate;
  bbox?: BoundingBox;
  style?: RegionStyle;
  state?: RegionState;
}

/**
 * Represents the current state of the map viewport
 */
export interface ViewportState {
  zoom: number;
  center: Coordinate;
  bounds: BoundingBox;
  pitch?: number;
  bearing?: number;
  padding?: { top: number; right: number; bottom: number; left: number };
}

/**
 * POI definition for the map system
 */
export interface POI {
  id: string;
  name: string;
  coordinates: Coordinate;
  type: string;
  metadata?: Record<string, any>;
}

/**
 * Props for the main RegionMap component
 */
export interface RegionMapProps {
  regions: Region[];
  initialViewport?: Partial<ViewportState>;
  onRegionClick?: (region: Region, event: React.MouseEvent) => void;
  onViewportChange?: (viewport: ViewportState) => void;
  selectedRegionId?: string;
  highlightedRegionId?: string;
  style?: React.CSSProperties;
  className?: string;
  mapStyle?: string | object;
  interactive?: boolean;
}

/**
 * Props for the RegionLayer component
 */
export interface RegionLayerProps {
  regions: Region[];
  selectedRegionId?: string;
  highlightedRegionId?: string;
  onRegionClick?: (region: Region, event: React.MouseEvent) => void;
  onRegionHover?: (region: Region | null, event: React.MouseEvent) => void;
  fillOpacity?: number;
  strokeWidth?: number;
  defaultFillColor?: string;
  selectedFillColor?: string;
  highlightedFillColor?: string;
}

/**
 * Props for the ViewportManager component
 */
export interface ViewportManagerProps {
  initialViewport: ViewportState;
  onChange?: (viewport: ViewportState) => void;
  fitBounds?: BoundingBox;
  fitBoundsPadding?: number;
  children: (
    viewport: ViewportState,
    setViewport: (viewport: ViewportState) => void
  ) => React.ReactNode;
}

/**
 * Props for the RegionSystem component
 */
export interface RegionSystemProps {
  regions: Region[];
  children?: React.ReactNode;
  onRegionSelect?: (region: Region | null) => void;
  initialSelectedRegionId?: string;
  mapControls?: {
    zoom?: boolean;
    pan?: boolean;
    rotate?: boolean;
  };
}

/**
 * Type guard to check if a value is a valid Region
 */
export function isRegion(value: any): value is Region {
  return (
    value &&
    typeof value.id === 'string' &&
    typeof value.name === 'string' &&
    Array.isArray(value.boundaries) &&
    typeof value.properties === 'object'
  );
}

/**
 * Utility type for partial region updates
 */
export type RegionUpdate = Pick<Region, 'id'> & Partial<Omit<Region, 'id'>>;

/**
 * Event types for region interactions
 */
export type RegionEvent = {
  region: Region;
  domEvent: React.MouseEvent | React.TouchEvent;
  coordinate: Coordinate;
};

/**
 * Style properties for rendering a region
 */
export interface RegionStyle {
  fillColor?: string;
  strokeColor?: string;
  strokeWidth?: number;
  opacity?: number;
  zIndex?: number;
  [key: string]: any;
}

/**
 * State of a region for rendering/interaction
 */
export type RegionState = 'normal' | 'hover' | 'selected' | 'disabled';

/**
 * Extended Region interface for rendering
 */
export interface RenderableRegion extends Region {
  style?: RegionStyle;
  state?: RegionState;
}

// Utility function for region validation (extended)
export function isRenderableRegion(value: any): value is RenderableRegion {
  return (
    isRegion(value) &&
    (typeof (value as RenderableRegion).style === 'undefined' ||
      typeof (value as RenderableRegion).style === 'object')
  );
}

// Sample usage for type validation
export const sampleStyledRegion: RenderableRegion = {
  id: 'region-2',
  name: 'Styled Region',
  boundaries: [
    [
      [100.0, 0.0],
      [101.0, 0.0],
      [101.0, 1.0],
      [100.0, 1.0],
      [100.0, 0.0],
    ],
  ],
  properties: {
    population: 100000,
    area: 500,
    code: 'SR-02',
    color: '#ffcc00',
  },
  style: {
    fillColor: '#ffcc00',
    strokeColor: '#333',
    strokeWidth: 2,
    opacity: 0.7,
    zIndex: 1,
  },
  state: 'normal',
};

export const sampleRegion: Region = {
  id: 'region-1',
  name: 'Sample Region',
  boundaries: [
    [
      [100.0, 0.0],
      [101.0, 0.0],
      [101.0, 1.0],
      [100.0, 1.0],
      [100.0, 0.0],
    ],
  ],
  properties: {
    population: 500000,
    area: 1234.56,
    code: 'SR-01',
    color: '#3388ff',
  },
  style: {
    fillColor: '#3388ff',
    strokeColor: '#333',
    strokeWidth: 2,
    opacity: 0.7,
    zIndex: 1,
  },
  state: 'normal',
};

export const sampleViewport: ViewportState = {
  zoom: 10,
  center: [100.5, 0.5],
  bounds: [100.0, 0.0, 101.0, 1.0],
};
