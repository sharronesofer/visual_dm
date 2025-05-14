import { Position } from './common';

export type MaterialType = 'wood' | 'stone' | 'metal' | 'reinforced';
export type BuildingElementType = 'wall' | 'door' | 'window';

export interface BuildingElement {
  id: string;
  type: BuildingElementType;
  position: Position;
  health: number;
  maxHealth: number;
  material: MaterialType;
}

export interface Wall extends BuildingElement {
  type: 'wall';
  thickness: number; // In game units
  height: number; // In game units
  isLoadBearing: boolean;
}

export interface Door extends BuildingElement {
  type: 'door';
  isOpen: boolean;
  isLocked: boolean;
  lockStrength?: number; // Optional lock difficulty
  requiredKey?: string; // Optional key ID
}

export interface Window extends BuildingElement {
  type: 'window';
  isBroken: boolean;
  isBarricaded: boolean;
  barricadeHealth?: number;
}

export interface MaterialProperties {
  weight: number; // Weight per unit
  resistance: {
    impact: number; // 0-1, damage resistance multiplier
    fire: number;
    explosion: number;
  };
  durability: number; // Base durability multiplier
  repairDifficulty: number; // Multiplier for repair time/cost
}

export interface BuildingPhysics {
  gravity: number;
  loadDistribution: number; // How load is distributed to adjacent elements
  windResistance: number;
  materialProperties: {
    [key in MaterialType]: MaterialProperties;
  };
}

export const BUILDING_PHYSICS_DEFAULTS: BuildingPhysics = {
  gravity: 9.81,
  loadDistribution: 0.7,
  windResistance: 0.5,
  materialProperties: {
    wood: {
      weight: 1,
      resistance: {
        impact: 0.3,
        fire: 0.1,
        explosion: 0.2
      },
      durability: 0.6,
      repairDifficulty: 0.5
    },
    stone: {
      weight: 2.5,
      resistance: {
        impact: 0.7,
        fire: 0.8,
        explosion: 0.6
      },
      durability: 0.9,
      repairDifficulty: 0.8
    },
    metal: {
      weight: 2,
      resistance: {
        impact: 0.8,
        fire: 0.6,
        explosion: 0.7
      },
      durability: 0.8,
      repairDifficulty: 0.7
    },
    reinforced: {
      weight: 3,
      resistance: {
        impact: 0.9,
        fire: 0.9,
        explosion: 0.8
      },
      durability: 1,
      repairDifficulty: 1
    }
  }
};

export interface BuildingStructure {
  id: string;
  elements: Map<string, BuildingElement>;
  integrity: number; // Overall structural integrity (0-1)
} 