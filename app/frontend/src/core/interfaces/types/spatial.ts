import { TerrainFeatureType } from './terrain';
import { POIType, POISubtype } from '../poi/types/POITypes';

export enum PlacementPattern {
  GRID = 'GRID',
  ORGANIC = 'ORGANIC',
  CLUSTERED = 'CLUSTERED',
  LINEAR = 'LINEAR',
  RADIAL = 'RADIAL'
}

export enum POICategory {
  SETTLEMENT = 'SETTLEMENT',
  DUNGEON = 'DUNGEON',
  LANDMARK = 'LANDMARK',
  RESOURCE = 'RESOURCE',
  SOCIAL = 'SOCIAL',
  EXPLORATION = 'EXPLORATION'
}

export interface POIPlacementRules {
  minElevation: number;
  maxElevation: number;
  validTerrainTypes: TerrainFeatureType[];
  invalidTerrainTypes: TerrainFeatureType[];
  minDistanceFromType: Map<POIType, number>;
}

export interface CategoryConfig {
  type: POIType;
  subtype: POISubtype;
  count: number;
  rules: POIPlacementRules;
}

export interface SpatialLayoutConfig {
  minDistance: number;
  maxPOIs: number;
  placementPattern: PlacementPattern;
  categories: CategoryConfig[];
}

export interface POIPlacement {
  id: string;
  category: POICategory;
  position: { x: number; y: number };
  groupId?: string;
}

export interface PathSegment {
  /** Start position of the path segment */
  from: { x: number; y: number };
  /** End position of the path segment */
  to: { x: number; y: number };
  /** Path type: 'PRIMARY' (main road) or 'SECONDARY' (side street) */
  type: 'PRIMARY' | 'SECONDARY';
  /** Width of the path in grid cells */
  width: number;
  /** Additional metadata for navigation, decoration, etc. */
  metadata?: Record<string, any>;
}

export interface SpatialLayoutResult {
  placements: POIPlacement[];
  paths: PathSegment[];
  metrics: {
    pathfindingScore: number;
    aestheticScore: number;
    totalScore: number;
  };
} 