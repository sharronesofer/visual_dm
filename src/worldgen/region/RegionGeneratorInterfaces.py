from typing import Dict, List, Optional, Any, Union
from typing import Union

/**
 * Represents a region's terrain type
 */
TerrainType = Union['water', 'mountain', 'forest', 'desert', 'urban', 'plains']
/**
 * Represents a point of interest in a region
 */
class POI:
    id: str
    templateId: str
    x: float
    y: float
    discovered: bool
/**
 * Represents a resource in a region
 */
class Resource:
    id: str
    templateId: str
    x: float
    y: float
    amount: float
    harvested: bool
/**
 * Represents a cell in the region grid
 */
class RegionCell:
    /** X coordinate (column) */
    x: float
    /** Y coordinate (row) */
    y: float
    /** Terrain type of the cell */
    terrain: TerrainType
    /** Optional elevation value (0-1) */
    elevation?: float
    /** Optional moisture value (0-1) */
    moisture?: float
/**
 * Represents a generated region
 */
class Region:
    /** Unique identifier for the region */
    id: str
    /** Name of the region */
    name: str
    /** Description of the region */
    description: str
    /** Width of the region in cells */
    width: float
    /** Height of the region in cells */
    height: float
    /** Grid of cells in the region */
    cells: List[RegionCell]
    /** Points of interest in the region */
    pointsOfInterest: List[POI]
    /** Resources in the region */
    resources: List[Resource]
    /** Additional metadata about the region */
    metadata: {
        /** Seed used to generate the region */
        seed: float
    /** Generator type used to create the region */
        generatorType: GeneratorType
    /** Parameters used during generation */
        parameters: Dict[str, Any>;
}
/**
 * Configuration for region generation
 */
class RegionGeneratorOptions:
    /** Width of the region in cells */
    width: float
    /** Height of the region in cells */
    height: float
    /** Type of generator to use */
    generatorType: GeneratorType
    /** Optional region name (will be generated if not provided) */
    name?: str
    /** Optional region ID (will be generated if not provided) */
    id?: str
    /** Optional terrain parameters */
    terrain?: {
        /** Threshold for water cells */
        waterThreshold?: float
    /** Threshold for mountain cells */
        mountainThreshold?: float
    /** Threshold for forest cells */
        forestThreshold?: float
    /** Threshold for desert cells */
        desertThreshold?: float
    /** Chance for urban cells */
        urbanChance?: float;
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
interface IRegionGenerator extends IWorldGenerator<RegionGeneratorOptions, Region> {
    /** Get the type of this generator */
    getGeneratorType(): GeneratorType;
    /** Generate a region with the given options */
    generate(options: RegionGeneratorOptions): IGenerationResult<Region>;
}
/**
 * Structure for predefined region templates used by hand-crafted generators
 */
class RegionTemplate:
    /** Template ID */
    id: str
    /** Template name */
    name: str
    /** Template description */
    description: str
    /** Width of the region */
    width: float
    /** Height of the region */
    height: float
    /** Predefined cell data */
    cells: {
        x: float
    y: float
    terrain: TerrainType
    elevation?: float
    moisture?: float[];
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