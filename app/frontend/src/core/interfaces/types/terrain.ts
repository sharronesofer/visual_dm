import { GridDimensions } from './grid';
import { POICategory } from './spatial';
import { Coordinates } from '../poi/types/POITypes';

export enum TerrainFeatureType {
  PLAIN = 'PLAIN',
  MOUNTAIN = 'MOUNTAIN',
  WATER = 'WATER',
  FOREST = 'FOREST',
  SWAMP = 'SWAMP'
}

export enum TerrainModificationType {
  LEVEL = 'LEVEL',
  SMOOTH = 'SMOOTH',
  RAMP = 'RAMP',
  FOUNDATION = 'FOUNDATION'
}

export interface TerrainModification {
  position: GridPosition;
  type: TerrainModificationType;
  params: Record<string, any>;
}

export interface TerrainAnalysisResult {
  slope: number;
  buildabilityScore: number;
  nearbyFeatures: TerrainFeatureType[];
  environmentalImpact: number;
}

export interface TerrainFeature {
  type: TerrainFeatureType;
  position: Coordinates;
  size: GridDimensions;
}

export interface BuildableArea {
  position: Coordinates;
  size: GridDimensions;
  slope: number;
  preferredCategories: POICategory[];
}

export interface TerrainData {
  heightMap: number[][];
  features: TerrainFeature[];
  buildableAreas: BuildableArea[];
} 