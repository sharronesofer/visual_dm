import { Position } from './common';

/** Terrain types */
export type TerrainType = 'plains' | 'forest' | 'mountain' | 'water' | 'desert' | 'swamp';

export type Direction = 'north' | 'south' | 'east' | 'west';
export type BorderType = 'normal' | 'difficult' | 'impassable' | 'bridge' | 'gate';

export interface Border {
  type: BorderType;
  direction: Direction;
  connected: boolean;
}

/** Region interface */
export interface Region {
  id: string;
  name: string;
  position: Position;
  width: number;
  height: number;
  terrain: TerrainType;
  borders: Border[];
  metadata?: Record<string, unknown>;
  type: RegionType;
  description?: string;
  boundaries: Array<[number, number]>; // Array of [longitude, latitude] coordinates
}

/** POI (Point of Interest) interface */
export interface POI {
  id: string;
  type: POIType;
  name: string;
  position: Position;
  description?: string;
  icon?: string;
  metadata?: Record<string, unknown>;
}

/** Map chunk interface */
export interface MapChunk {
  position: Position;
  width: number;
  height: number;
  terrain: TerrainType[][];
  pois: POI[];
  regions: Region[];
  lastUpdated: number;
}

/** Map data interface */
export interface MapData {
  id: string;
  name: string;
  width: number;
  height: number;
  chunks: Record<string, MapChunk>;
  regions: Region[];
  metadata?: Record<string, unknown>;
}

/** Map generation state interface */
export interface MapGenerationState {
  isGenerating: boolean;
  progress: number;
  currentChunk?: Position;
  error?: string;
}

/** Map chunk key interface */
export interface MapChunkKey {
  x: number;
  y: number;
  toString(): string;
}

/** POI types */
export type POIType = 'city' | 'dungeon' | 'quest' | 'landmark';

/** Map response types */
export interface MapResponse {
  map: MapData;
  generationId: string;
}

export interface RegionResponse {
  region: Region;
  pois: POI[];
}

export interface ChunkResponse {
  chunk: MapChunk;
  complete: boolean;
}

/** Map generation options */
export interface GenerateMapOptions {
  width: number;
  height: number;
  seed?: string;
  terrainConfig?: Record<TerrainType, number>;
  poiDensity?: number;
}

// Helper functions
export const getChunkKey = (position: Position): string => `${position.x},${position.y}`;
export const getRegionKey = (position: Position): string => `${position.x},${position.y}`;

export const calculateChunkPosition = (position: Position, chunkSize: number): Position => ({
  x: Math.floor(position.x / chunkSize),
  y: Math.floor(position.y / chunkSize),
});

export type RegionType = 'city' | 'dungeon' | 'wilderness' | 'custom';
