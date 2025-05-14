/*
Integration Examples (usage snippets):

// NPC Placement System
function placeNPCs(region) {
  if (region.biome === 'forest') {
    // ...
  }
}

// Quest Generation System
function generateQuests(region) {
  if (region.metadata && region.metadata.dangerLevel > 5) {
    // ...
  }
}

// Environmental System
function applyWeather(region) {
  // Use region.terrain and region.metadata to determine weather effects
  // ...
}
*/

/**
 * RegionContract defines the structure for a world region.
 * @version 1.0.0
 * @example
 * const exampleRegion: RegionContract = {
 *   id: 'region-001',
 *   name: 'Northern Plains',
 *   biome: BiomeType.PLAINS,
 *   cells: 1000,
 *   terrain: TerrainType.FLAT,
 *   metadata: { elevation: 200, climate: 'temperate' },
 *   version: '1.0.0',
 * };
 */
export enum BiomeType {
    PLAINS = 'plains',
    FOREST = 'forest',
    DESERT = 'desert',
    MOUNTAIN = 'mountain',
    SWAMP = 'swamp',
    TUNDRA = 'tundra',
    OCEAN = 'ocean',
}

export enum TerrainType {
    FLAT = 'flat',
    HILLS = 'hills',
    MOUNTAINOUS = 'mountainous',
    VALLEY = 'valley',
    COASTAL = 'coastal',
}

export interface RegionContract {
    /** Unique region identifier */
    readonly id: string;
    /** Human-readable region name */
    readonly name: string;
    /** Biome type for the region */
    readonly biome: BiomeType;
    /** Number of cells in the region */
    readonly cells: number;
    /** Terrain type */
    readonly terrain: TerrainType;
    /** Arbitrary metadata (e.g., elevation, climate) */
    readonly metadata: Record<string, unknown>;
    /** Version of the contract */
    readonly version: string;
}

/**
 * Helper to freeze a RegionContract object for immutability at runtime.
 * @param region The RegionContract object to freeze
 * @returns The frozen RegionContract object
 * @example
 * const frozenRegion = freezeRegionContract(exampleRegion);
 */
export function freezeRegionContract(region: RegionContract): Readonly<RegionContract> {
    return Object.freeze(region);
}

// Note: All fields are readonly for compile-time immutability. Consumers should use freezeRegionContract for runtime immutability.

/**
 * Query parameters for region lookups.
 */
export interface RegionQuery {
    /** Optional biome filter */
    biome?: BiomeType;
    /** Optional terrain filter */
    terrain?: TerrainType;
    /** Optional metadata filter */
    metadata?: Partial<Record<string, unknown>>;
}

/**
 * Interface for region query methods.
 */
export interface RegionQueryAPI {
    /**
     * Find regions matching the query parameters.
     * @param query Query parameters
     * @returns Array of matching RegionContract objects
     */
    findRegions(query: RegionQuery): RegionContract[];
    /**
     * Get a region by its unique ID.
     * @param id Region ID
     * @returns RegionContract or undefined
     */
    getRegionById(id: string): RegionContract | undefined;
}

/**
 * Stub for a spatial index for regions (to be implemented in system code).
 */
export class RegionSpatialIndex {
    // Implementation would use a spatial data structure (e.g., R-tree, quadtree)
    // to optimize location-based queries. This is a placeholder for integration.
}

/**
 * Validate a RegionContract object for required fields, types, and constraints.
 * @param region The object to validate
 * @returns { errors: string[]; value?: RegionContract } - errors array is empty if valid
 * @example
 * const result = validateRegionContract(exampleRegion);
 * if (result.errors.length) { console.error(result.errors); }
 */
export function validateRegionContract(region: any): { errors: string[]; value?: RegionContract } {
    const errors: string[] = [];
    if (!region || typeof region !== 'object') errors.push('Region must be an object');
    if (typeof region.id !== 'string') errors.push('id must be a string');
    if (typeof region.name !== 'string') errors.push('name must be a string');
    if (!Object.values(BiomeType).includes(region.biome)) errors.push('biome must be a valid BiomeType');
    if (typeof region.cells !== 'number' || region.cells < 0) errors.push('cells must be a non-negative number');
    if (!Object.values(TerrainType).includes(region.terrain)) errors.push('terrain must be a valid TerrainType');
    if (typeof region.metadata !== 'object' || region.metadata === null) errors.push('metadata must be an object');
    if (typeof region.version !== 'string') errors.push('version must be a string');
    return errors.length ? { errors } : { errors: [], value: region as RegionContract };
}

/**
 * Get the version of a RegionContract object.
 * @param region The RegionContract object
 * @returns The version string
 */
export function getRegionContractVersion(region: RegionContract): string {
    return region.version;
}

// Versioning notes:
// - The 'version' field should be incremented for breaking changes to the contract.
// - Consumers should check the version before processing data.
// - For backward compatibility, provide migration utilities as needed in future versions. 