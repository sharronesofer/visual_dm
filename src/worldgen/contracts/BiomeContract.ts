/**
 * BiomeContract defines the structure for a biome in the world.
 * @version 1.0.0
 * @example
 * const exampleBiome: BiomeContract = {
 *   id: 'biome-001',
 *   name: 'Temperate Forest',
 *   classification: BiomeClassification.FOREST,
 *   parameters: { humidity: 0.7, temperature: 18 },
 *   transitionRules: [BiomeClassification.PLAINS, BiomeClassification.MOUNTAIN],
 *   version: '1.0.0',
 * };
 */
export enum BiomeClassification {
    PLAINS = 'plains',
    FOREST = 'forest',
    DESERT = 'desert',
    MOUNTAIN = 'mountain',
    SWAMP = 'swamp',
    TUNDRA = 'tundra',
    OCEAN = 'ocean',
}

export interface BiomeContract {
    /** Unique biome identifier */
    readonly id: string;
    /** Human-readable biome name */
    readonly name: string;
    /** Biome classification */
    readonly classification: BiomeClassification;
    /** Parameters for the biome (e.g., humidity, temperature) */
    readonly parameters: Record<string, number>;
    /** List of allowed transition biomes */
    readonly transitionRules: readonly BiomeClassification[];
    /** Version of the contract */
    readonly version: string;
}

/**
 * Helper to freeze a BiomeContract object for immutability at runtime.
 * @param biome The BiomeContract object to freeze
 * @returns The frozen BiomeContract object
 * @example
 * const frozenBiome = freezeBiomeContract(exampleBiome);
 */
export function freezeBiomeContract(biome: BiomeContract): Readonly<BiomeContract> {
    return Object.freeze(biome);
}

// Note: All fields are readonly for compile-time immutability. Consumers should use freezeBiomeContract for runtime immutability.

/**
 * Query parameters for biome lookups.
 */
export interface BiomeQuery {
    classification?: BiomeClassification;
    parameters?: Partial<Record<string, number>>;
}

/**
 * Interface for biome query methods.
 */
export interface BiomeQueryAPI {
    /**
     * Find biomes matching the query parameters.
     * @param query Query parameters
     * @returns Array of matching BiomeContract objects
     */
    findBiomes(query: BiomeQuery): BiomeContract[];
    /**
     * Get a biome by its unique ID.
     * @param id Biome ID
     * @returns BiomeContract or undefined
     */
    getBiomeById(id: string): BiomeContract | undefined;
}

/**
 * Stub for a transition rule system (to be implemented in system code).
 */
export class BiomeTransitionRules {
    // Implementation would manage allowed transitions between biomes.
    // This is a placeholder for integration with the worldgen system.
}

/**
 * Validate a BiomeContract object for required fields, types, and constraints.
 * @param biome The object to validate
 * @returns { errors: string[]; value?: BiomeContract } - errors array is empty if valid
 * @example
 * const result = validateBiomeContract(exampleBiome);
 * if (result.errors.length) { console.error(result.errors); }
 */
export function validateBiomeContract(biome: any): { errors: string[]; value?: BiomeContract } {
    const errors: string[] = [];
    if (!biome || typeof biome !== 'object') errors.push('Biome must be an object');
    if (typeof biome.id !== 'string') errors.push('id must be a string');
    if (typeof biome.name !== 'string') errors.push('name must be a string');
    if (!Object.values(BiomeClassification).includes(biome.classification)) errors.push('classification must be a valid BiomeClassification');
    if (typeof biome.parameters !== 'object' || biome.parameters === null) errors.push('parameters must be an object');
    if (!Array.isArray(biome.transitionRules)) errors.push('transitionRules must be an array of BiomeClassification');
    if (typeof biome.version !== 'string') errors.push('version must be a string');
    return errors.length ? { errors } : { errors: [], value: biome as BiomeContract };
}

/**
 * Get the version of a BiomeContract object.
 * @param biome The BiomeContract object
 * @returns The version string
 */
export function getBiomeContractVersion(biome: BiomeContract): string {
    return biome.version;
}

// Versioning notes:
// - The 'version' field should be incremented for breaking changes to the contract.
// - Consumers should check the version before processing data.
// - For backward compatibility, provide migration utilities as needed in future versions.

/*
Integration Examples (usage snippets):

// World Generation System
function assignBiomeToRegion(region, biome) {
  if (biome.classification === 'forest') {
    // ...
  }
}

// Rendering System
function renderBiome(biome) {
  // Use biome.parameters for color/texture selection
  // ...
}

// Simulation System
function simulateBiomeTransition(biome, nextBiome) {
  if (biome.transitionRules && biome.transitionRules.includes(nextBiome.classification)) {
    // ...
  }
}
*/ 