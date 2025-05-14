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