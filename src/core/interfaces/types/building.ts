import { Position } from './common';

/*
 * Advanced Material System Extensions
 * ----------------------------------
 * This file now supports advanced material properties for:
 * - Weather resistance (heat, cold, moisture, UV, wind)
 * - Weathering rate and history (for time-based degradation)
 * - Advanced properties (density, flexibility, conductivity)
 * - Upgrade paths and material combinations (for crafting and progression)
 * - Visual degradation states and special effects (for rendering/feedback)
 *
 * See MaterialProperties interface for field-level documentation.
 *
 * TODO: Extend MaterialType and BUILDING_PHYSICS_DEFAULTS as new materials, upgrades, and combinations are added.
 */

export type MaterialType =
  | 'wood'
  | 'stone'
  | 'metal'
  | 'reinforced'
  | 'composite' // New: for advanced combinations
  | 'upgraded'  // New: for upgrade paths
  // TODO: Add more as needed
  ;

export type BuildingElementType =
  | 'wall'
  | 'door'
  | 'window'
  | 'floor'
  | 'roof'
  | 'column'
  | 'beam'
  | 'stair'
  | 'furniture'
  | 'partition'
  | 'foundation';

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
  accessPermissions?: Record<string, { type: 'owner' | 'resident' | 'key' | 'custom', expiresAt?: number }>; // Permissions per character
}

export interface Window extends BuildingElement {
  type: 'window';
  isBroken: boolean;
  isBarricaded: boolean;
  barricadeHealth?: number;
}

export interface Floor extends BuildingElement {
  type: 'floor';
  thickness: number; // In game units
  area: number; // Square units
  material: MaterialType;
  supportColumns?: string[]; // IDs of supporting columns
}

export interface Roof extends BuildingElement {
  type: 'roof';
  thickness: number;
  area: number;
  material: MaterialType;
  slope: number; // Slope in degrees
  supportBeams?: string[];
}

export interface Column extends BuildingElement {
  type: 'column';
  height: number;
  radius: number;
  material: MaterialType;
  loadCapacity: number; // Max load in game units
}

export interface Beam extends BuildingElement {
  type: 'beam';
  length: number;
  crossSection: number; // Area of cross-section
  material: MaterialType;
  loadCapacity: number;
}

export interface Stair extends BuildingElement {
  type: 'stair';
  width: number;
  height: number;
  steps: number;
  material: MaterialType;
  connects: [string, string]; // IDs of connected floors
}

export interface Furniture extends BuildingElement {
  type: 'furniture';
  furnitureType: string; // e.g., 'chair', 'table', etc.
  dimensions: { width: number; height: number; depth: number };
  material: MaterialType;
  isMovable: boolean;
}

export interface Partition extends BuildingElement {
  type: 'partition';
  thickness: number;
  height: number;
  material: MaterialType;
  isMovable: boolean;
}

export interface MaterialProperties {
  weight: number; // Weight per unit
  resistance: {
    impact: number; // 0-1, damage resistance multiplier
    fire: number;
    explosion: number;
    // --- Advanced Weather Resistance ---
    heat?: number;      // 0-100, resistance to heat (sun, fire, etc.)
    cold?: number;      // 0-100, resistance to cold (snow, frost, etc.)
    moisture?: number;  // 0-100, resistance to water/rain/humidity
    uv?: number;        // 0-100, resistance to UV/sunlight
    wind?: number;      // 0-100, resistance to wind/air erosion
  };
  durability: number; // Base durability multiplier
  repairDifficulty: number; // Multiplier for repair time/cost
  // --- Advanced Properties ---
  density?: number;        // kg/m^3 or normalized (affects weight, physics)
  flexibility?: number;    // 0-1 (affects physics, damage, upgrades)
  conductivity?: number;   // 0-1 (thermal/electrical, affects special effects)
  // --- Weathering ---
  weatheringRate?: number; // 0-1 per time unit (higher = faster degradation)
  weatheringHistory?: Array<{ timestamp: number; value: number; reason?: string }>; // Log of weathering events
  // --- Upgrade/Combination ---
  upgradePath?: string[]; // List of material types this can upgrade to
  combinationKey?: string; // Key for combination matrix (for advanced crafting)
  synergyBonus?: number;   // Bonus for optimal combinations (0-1)
  // --- Visual/Effect ---
  visualDegradationStates?: string[]; // Asset keys for visual states (pristine, worn, damaged)
  specialEffects?: string[]; // Keys for special effects (e.g., sound, particles)
  // TODO: Add more fields as needed for future expansion
}

export interface BuildingPhysics {
  gravity: number;
  loadDistribution: number; // How load is distributed to adjacent elements
  windResistance: number;
  materialProperties: {
    [key in MaterialType]: MaterialProperties;
  };
  minSupportPoints: number; // Minimum required support points for stability
  maxIntegrity: number; // Maximum possible integrity value
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
        explosion: 0.2,
        heat: 40,
        cold: 60,
        moisture: 30,
        uv: 20,
        wind: 50
      },
      durability: 0.6,
      repairDifficulty: 0.5,
      density: 600,
      flexibility: 0.7,
      conductivity: 0.2,
      weatheringRate: 0.02,
      upgradePath: ['reinforced'],
      visualDegradationStates: ['wood_pristine', 'wood_worn', 'wood_damaged'],
      specialEffects: ['creak']
    },
    stone: {
      weight: 2.5,
      resistance: {
        impact: 0.7,
        fire: 0.8,
        explosion: 0.6,
        heat: 80,
        cold: 90,
        moisture: 70,
        uv: 90,
        wind: 80
      },
      durability: 0.9,
      repairDifficulty: 0.8,
      density: 2500,
      flexibility: 0.1,
      conductivity: 0.05,
      weatheringRate: 0.01,
      upgradePath: ['reinforced'],
      visualDegradationStates: ['stone_pristine', 'stone_worn', 'stone_cracked'],
      specialEffects: ['dust']
    },
    metal: {
      weight: 2,
      resistance: {
        impact: 0.8,
        fire: 0.6,
        explosion: 0.7,
        heat: 90,
        cold: 80,
        moisture: 40,
        uv: 100,
        wind: 90
      },
      durability: 0.8,
      repairDifficulty: 0.7,
      density: 7800,
      flexibility: 0.3,
      conductivity: 0.9,
      weatheringRate: 0.015,
      upgradePath: ['reinforced'],
      visualDegradationStates: ['metal_pristine', 'metal_rusty', 'metal_damaged'],
      specialEffects: ['clang']
    },
    reinforced: {
      weight: 3,
      resistance: {
        impact: 0.9,
        fire: 0.9,
        explosion: 0.8,
        heat: 95,
        cold: 95,
        moisture: 90,
        uv: 100,
        wind: 95
      },
      durability: 1,
      repairDifficulty: 1,
      density: 8200,
      flexibility: 0.2,
      conductivity: 0.7,
      weatheringRate: 0.008,
      upgradePath: [],
      visualDegradationStates: ['reinforced_pristine', 'reinforced_worn', 'reinforced_damaged'],
      specialEffects: ['thud']
    },
    composite: {
      weight: 2.2,
      resistance: {
        impact: 0.85,
        fire: 0.7,
        explosion: 0.75,
        heat: 85,
        cold: 90,
        moisture: 80,
        uv: 95,
        wind: 90
      },
      durability: 0.95,
      repairDifficulty: 0.9,
      density: 3000,
      flexibility: 0.5,
      conductivity: 0.5,
      weatheringRate: 0.009,
      upgradePath: ['upgraded'],
      visualDegradationStates: ['composite_pristine', 'composite_worn', 'composite_damaged'],
      specialEffects: ['resonance']
      // TODO: Tune composite properties and effects
    },
    upgraded: {
      weight: 2.8,
      resistance: {
        impact: 0.92,
        fire: 0.95,
        explosion: 0.85,
        heat: 98,
        cold: 98,
        moisture: 95,
        uv: 100,
        wind: 97
      },
      durability: 1,
      repairDifficulty: 1,
      density: 8500,
      flexibility: 0.25,
      conductivity: 0.8,
      weatheringRate: 0.006,
      upgradePath: [],
      visualDegradationStates: ['upgraded_pristine', 'upgraded_worn', 'upgraded_damaged'],
      specialEffects: ['pulse']
      // TODO: Tune upgraded properties and effects
    }
  },
  minSupportPoints: 2, // Reasonable default for minimum support points
  maxIntegrity: 1 // Integrity is normalized between 0 and 1
};

export interface BuildingStructure {
  id: string;
  elements: Map<string, BuildingElement>;
  integrity: number; // Overall structural integrity (0-1)
  supportPoints: Position[]; // List of support points for the structure
  ownerId?: string; // Owner of the building
  buildingType?: string; // Type of building (residential, industrial, etc.)
  /**
   * Two-axis damage tracking:
   * - battleDamage: Damage from combat (1-10)
   * - deterioration: Damage from time/environment (1-10)
   * Both axes are independent and capped at 10.
   */
  battleDamage: number;
  deterioration: number;
}

/**
 * Serialize a BuildingStructure to a plain object (for persistence)
 */
export function serializeBuildingStructure(structure: BuildingStructure): any {
  return {
    ...structure,
    elements: Array.from(structure.elements.entries()),
  };
}

/**
 * Deserialize a plain object to a BuildingStructure
 */
export function deserializeBuildingStructure(data: any): BuildingStructure {
  return {
    ...data,
    elements: new Map(data.elements),
  };
}

// Unified material and resource system for all building elements
// TODO: Extend MaterialType and MaterialProperties for advanced elements as needed
// TODO: Add resource cost and tracking logic for advanced elements in construction/repair systems 