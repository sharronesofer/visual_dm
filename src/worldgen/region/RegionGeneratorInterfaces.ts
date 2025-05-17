import { IGeneratorOptions, IWorldGenerator, IGenerationResult, GeneratorType } from '../core/IWorldGenerator';

/**
 * Represents a region's terrain type
 */
export type TerrainType = 'water' | 'mountain' | 'forest' | 'desert' | 'urban' | 'plains';

/**
 * Represents a point of interest in a region
 */
export interface POI {
    id: string;
    templateId: string;
    x: number;
    y: number;
    discovered: boolean;
}

/**
 * Represents a resource in a region
 */
export interface Resource {
    id: string;
    templateId: string;
    x: number;
    y: number;
    amount: number;
    harvested: boolean;
}

/**
 * Represents a cell in the region grid
 */
export interface RegionCell {
    /** X coordinate (column) */
    x: number;
    /** Y coordinate (row) */
    y: number;
    /** Terrain type of the cell */
    terrain: TerrainType;
    /** Optional elevation value (0-1) */
    elevation?: number;
    /** Optional moisture value (0-1) */
    moisture?: number;
    buildingId?: string;
}

/**
 * Represents a generated region
 */
export interface Region {
    /** Unique identifier for the region */
    id: string;
    /** Name of the region */
    name: string;
    /** Description of the region */
    description: string;
    /** Width of the region in cells */
    width: number;
    /** Height of the region in cells */
    height: number;
    /** Grid of cells in the region */
    cells: RegionCell[];
    /** Points of interest in the region */
    pointsOfInterest: POI[];
    /** Resources in the region */
    resources: Resource[];
    /** Additional metadata about the region */
    metadata: {
        /** Seed used to generate the region */
        seed: number;
        /** Generator type used to create the region */
        generatorType: GeneratorType;
        /** Parameters used during generation */
        parameters: Record<string, any>;
    };
    buildings?: Building[];
    buildingMetadata?: {
        placementRules?: BuildingPlacementRule[];
        materialStyles?: BuildingMaterialStyle[];
    };
}

/**
 * Configuration for region generation
 */
export interface RegionGeneratorOptions extends IGeneratorOptions {
    /** Width of the region in cells */
    width: number;
    /** Height of the region in cells */
    height: number;
    /** Type of generator to use */
    generatorType: GeneratorType;
    /** Optional region name (will be generated if not provided) */
    name?: string;
    /** Optional region ID (will be generated if not provided) */
    id?: string;
    /** Optional terrain parameters */
    terrain?: {
        /** Threshold for water cells */
        waterThreshold?: number;
        /** Threshold for mountain cells */
        mountainThreshold?: number;
        /** Threshold for forest cells */
        forestThreshold?: number;
        /** Threshold for desert cells */
        desertThreshold?: number;
        /** Chance for urban cells */
        urbanChance?: number;
    };
    /** Optional points of interest parameters */
    pointsOfInterest?: {
        /** Maximum number of POIs to generate */
        maxPOIs?: number;
        /** Allow POIs to be placed only on specific terrain types */
        allowedTerrains?: TerrainType[];
    };
    /** Optional resource parameters */
    resources?: {
        /** Maximum number of resources to generate */
        maxResources?: number;
        /** Allow resources to be placed only on specific terrain types */
        allowedTerrains?: TerrainType[];
    };
    buildings?: {
        maxBuildings?: number;
        allowedTypes?: string[];
        placementRules?: BuildingPlacementRule[];
        materialStyles?: BuildingMaterialStyle[];
        customizationHooks?: Record<string, any>;
    };
}

/**
 * Interface for region generators
 */
export interface IRegionGenerator extends IWorldGenerator<RegionGeneratorOptions, Region> {
    /** Get the type of this generator */
    getGeneratorType(): GeneratorType;
    /** Generate a region with the given options */
    generate(options: RegionGeneratorOptions): IGenerationResult<Region>;
}

/**
 * Structure for predefined region templates used by hand-crafted generators
 */
export interface RegionTemplate {
    /** Template ID */
    id: string;
    /** Template name */
    name: string;
    /** Template description */
    description: string;
    /** Width of the region */
    width: number;
    /** Height of the region */
    height: number;
    /** Predefined cell data */
    cells: {
        x: number;
        y: number;
        terrain: TerrainType;
        elevation?: number;
        moisture?: number;
    }[];
    /** Predefined POIs */
    pointsOfInterest: {
        templateId: string;
        x: number;
        y: number;
    }[];
    /** Predefined resources */
    resources: {
        templateId: string;
        x: number;
        y: number;
        amount: number;
    }[];
}

/**
 * Represents a building in a region
 */
export interface Building {
    id: string;
    templateId: string;
    x: number;
    y: number;
    elevation?: number;
    rotation?: number;
    biome?: string;
    terrainType?: TerrainType;
    foundationType?: string;
    material: string;
    style: string;
    integrity: number;
    customization?: Record<string, any>;
}

/**
 * Placement rule for buildings
 */
export interface BuildingPlacementRule {
    allowedTerrains: TerrainType[];
    requiredResources?: string[];
    minDistanceToWater?: number;
    maxSlope?: number;
    minElevation?: number;
    maxElevation?: number;
    populationDensityLimit?: number;
    biomeTypes?: string[];
    customRuleFn?: (cell: RegionCell, context: any) => boolean;
}

/**
 * Material and style definition for buildings
 *
 * - Extensible for modding: add new materials/styles at runtime
 * - Supports biome/region/resource dependencies
 * - Allows for texture/model variants for environmental adaptation
 */
export interface BuildingMaterialStyle {
    material: string;
    style: string;
    biome?: string;
    region?: string;
    resourceDependencies?: string[];
    textureVariant?: string;
    modelVariant?: string;
    // Modding extension point
    [key: string]: any;
}

/**
 * Placement rule for buildings (extended for rule engine)
 */
export interface PlacementRule {
    id: string;
    description?: string;
    allowedBiomes?: string[];
    allowedTerrains?: TerrainType[];
    minDistanceToResource?: { resourceType: string; minDistance: number }[];
    maxDistanceToResource?: { resourceType: string; maxDistance: number }[];
    minPopulationDensity?: number;
    maxPopulationDensity?: number;
    customRuleFn?: (cell: RegionCell, context: PlacementRuleContext) => boolean | PlacementRuleResult;
    priority?: number; // For conflict resolution
    isHardRule?: boolean; // If true, blocks placement
}

export interface PlacementRuleContext {
    cells: RegionCell[];
    buildings: Building[];
    resources: Resource[];
    densityMap?: number[][];
    [key: string]: any;
}

export interface PlacementRuleResult {
    valid: boolean;
    failedRules?: string[];
    reasons?: string[];
    advisory?: string[];
    score?: number;
}

export interface PlacementRuleEngine {
    evaluate(cell: RegionCell, context: PlacementRuleContext, rules: PlacementRule[]): PlacementRuleResult;
    findValidLocations(context: PlacementRuleContext, rules: PlacementRule[]): RegionCell[];
}

/**
 * Hook type for building generation events
 */
export type BuildingGenerationHook = (
    phase: 'pre' | 'post',
    buildingParams: Partial<Building>,
    context: PlacementRuleContext
) => void | Partial<Building>;

/**
 * Serializable configuration object for building customizations
 */
export interface BuildingCustomizationConfig {
    id: string;
    buildingType: string;
    parameters: Record<string, any>;
    version: string;
    createdAt: string;
    updatedAt?: string;
}

/**
 * API for registering custom building generators and modifiers
 */
export interface BuildingCustomizationAPI {
    registerHook(hook: BuildingGenerationHook): void;
    unregisterHook(hook: BuildingGenerationHook): void;
    getHooks(): BuildingGenerationHook[];
    applyCustomization(config: BuildingCustomizationConfig): void;
    getCustomizations(): BuildingCustomizationConfig[];
    registerGenerator(type: string, generator: (...args: any[]) => Building): void;
    registerModifier(type: string, modifier: (building: Building) => Building): void;
    getGenerators(): Record<string, (...args: any[]) => Building>;
    getModifiers(): Record<string, (building: Building) => Building>;
}

/**
 * Plugin type for style/material system (see StyleMaterialSystem.ts)
 */
export type StyleMaterialPlugin = (context: {
    cell: RegionCell;
    resources: Resource[];
    environment: any;
    current: { material: string; style: string; textureVariant?: string; modelVariant?: string };
}) => Partial<{ material: string; style: string; textureVariant: string; modelVariant: string }>; 