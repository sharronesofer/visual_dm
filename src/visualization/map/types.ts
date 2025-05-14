export interface Point {
  x: number;
  y: number;
}

export interface Size {
  width: number;
  height: number;
}

export interface Viewport {
  position: Point;
  size: Size;
  zoom: number;
  rotation: number;
}

export interface Tile {
  id: string;
  type: TerrainType;
  position: Point;
  elevation: number;
  walkable: boolean;
  explored: boolean;
  visible: boolean;
  weather?: string;
}

export enum TerrainType {
  GRASS = 'grass',
  FOREST = 'forest',
  MOUNTAIN = 'mountain',
  WATER = 'water',
  URBAN = 'urban',
}

export interface MapData {
  size: Size;
  tiles: Tile[][];
  objects: MapObject[];
}

export interface MapObject {
  id: string;
  type: string;
  position: Point;
  size: Size;
  elevation: number;
  interactive: boolean;
  data: Record<string, any>;
}

export interface LightSource {
  position: Point;
  intensity: number;
  radius: number;
  color: string;
}

export interface RenderOptions {
  showGrid: boolean;
  showFogOfWar: boolean;
  showLighting: boolean;
  showObjects: boolean;
  levelOfDetail: number;
}

export interface MapInteractionEvent {
  type: 'click' | 'hover' | 'drag';
  position: Point;
  tile?: Tile;
  object?: MapObject;
}

export interface MapUpdateEvent {
  type: 'tile' | 'object' | 'lighting' | 'viewport';
  data: any;
}

export type MapEventListener = (event: MapInteractionEvent | MapUpdateEvent) => void; 