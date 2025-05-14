import { BuildingType } from '../../types/buildings/base';

export { BuildingType };

export interface InteriorParams {
  buildingType: BuildingType;
  width: number;
  length: number;
  height: number;
  entryPoints: { x: number; y: number }[];
  region?: string;
  culture?: string;
}

export interface InteriorLayout {
  rooms: Room[];
  doors: Door[];
  furniture: FurniturePlacement[];
  decorations: DecorationPlacement[];
}

export interface Room {
  id: string;
  type: string;
  x: number;
  y: number;
  width: number;
  length: number;
}

export interface Door {
  fromRoom: string;
  toRoom: string;
  x: number;
  y: number;
}

export interface FurniturePlacement {
  roomId: string;
  type: string;
  x: number;
  y: number;
  rotation: number;
}

export interface DecorationPlacement {
  roomId: string;
  type: string;
  x: number;
  y: number;
  rotation: number;
  colorPalette: string[];
}

export interface InteriorMesh {
  vertices: number[][];
  faces: number[][];
  lod: number;
}

export interface VariationParams {
  region: string;
  culture: string;
  style: string;
} 