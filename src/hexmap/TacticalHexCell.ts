import { WeatherType } from './HexCell';

export interface TacticalHexCell {
  q: number;
  r: number;
  terrainType: string;
  terrainEffect: string;
  cover: number;
  movementCost: number;
  visibility: number;
  elevation?: number;
  features?: string[];
  environmentalEffects?: Array<{
    type: string;
    magnitude: number;
    duration?: number;
  }>;
} 