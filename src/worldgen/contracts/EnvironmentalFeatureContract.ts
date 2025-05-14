/**
 * EnvironmentalFeatureContract defines the structure for an environmental feature (weather, hazard, season, etc.).
 * @version 1.0.0
 * @example
 * const exampleFeature: EnvironmentalFeatureContract = {
 *   id: 'env-001',
 *   type: EnvironmentalFeatureType.WEATHER,
 *   name: 'Thunderstorm',
 *   parameters: { intensity: 0.8, duration: 120 },
 *   metadata: { lightning: true, windSpeed: 30 },
 *   version: '1.0.0',
 * };
 */
export enum EnvironmentalFeatureType {
    WEATHER = 'weather',
    HAZARD = 'hazard',
    SEASON = 'season',
    EVENT = 'event',
}

export interface EnvironmentalFeatureContract {
    /** Unique feature identifier */
    readonly id: string;
    /** Type of environmental feature */
    readonly type: EnvironmentalFeatureType;
    /** Human-readable feature name */
    readonly name: string;
    /** Parameters for the feature (e.g., intensity, duration) */
    readonly parameters: Record<string, number>;
    /** Arbitrary metadata (e.g., lightning, windSpeed) */
    readonly metadata: Record<string, unknown>;
    /** Version of the contract */
    readonly version: string;
}

/**
 * Helper to freeze an EnvironmentalFeatureContract object for immutability at runtime.
 * @param feature The EnvironmentalFeatureContract object to freeze
 * @returns The frozen EnvironmentalFeatureContract object
 * @example
 * const frozenFeature = freezeEnvironmentalFeatureContract(exampleFeature);
 */
export function freezeEnvironmentalFeatureContract(feature: EnvironmentalFeatureContract): Readonly<EnvironmentalFeatureContract> {
    return Object.freeze(feature);
}

// Note: All fields are readonly for compile-time immutability. Consumers should use freezeEnvironmentalFeatureContract for runtime immutability.

/**
 * Query parameters for environmental feature lookups.
 */
export interface EnvironmentalFeatureQuery {
    type?: EnvironmentalFeatureType;
    name?: string;
    parameters?: Partial<Record<string, number>>;
}

/**
 * Interface for environmental feature query methods.
 */
export interface EnvironmentalFeatureQueryAPI {
    /**
     * Find features matching the query parameters.
     * @param query Query parameters
     * @returns Array of matching EnvironmentalFeatureContract objects
     */
    findFeatures(query: EnvironmentalFeatureQuery): EnvironmentalFeatureContract[];
    /**
     * Get a feature by its unique ID.
     * @param id Feature ID
     * @returns EnvironmentalFeatureContract or undefined
     */
    getFeatureById(id: string): EnvironmentalFeatureContract | undefined;
}

/**
 * Stub for a feature index (to be implemented in system code).
 */
export class EnvironmentalFeatureIndex {
    // Implementation would use a data structure to optimize feature queries.
    // This is a placeholder for integration with the worldgen system.
}

/**
 * Validate an EnvironmentalFeatureContract object for required fields, types, and constraints.
 * @param feature The object to validate
 * @returns { errors: string[]; value?: EnvironmentalFeatureContract } - errors array is empty if valid
 * @example
 * const result = validateEnvironmentalFeatureContract(exampleFeature);
 * if (result.errors.length) { console.error(result.errors); }
 */
export function validateEnvironmentalFeatureContract(feature: any): { errors: string[]; value?: EnvironmentalFeatureContract } {
    const errors: string[] = [];
    if (!feature || typeof feature !== 'object') errors.push('Feature must be an object');
    if (typeof feature.id !== 'string') errors.push('id must be a string');
    if (!Object.values(EnvironmentalFeatureType).includes(feature.type)) errors.push('type must be a valid EnvironmentalFeatureType');
    if (typeof feature.name !== 'string') errors.push('name must be a string');
    if (typeof feature.parameters !== 'object' || feature.parameters === null) errors.push('parameters must be an object');
    if (typeof feature.metadata !== 'object' || feature.metadata === null) errors.push('metadata must be an object');
    if (typeof feature.version !== 'string') errors.push('version must be a string');
    return errors.length ? { errors } : { errors: [], value: feature as EnvironmentalFeatureContract };
}

/**
 * Get the version of an EnvironmentalFeatureContract object.
 * @param feature The EnvironmentalFeatureContract object
 * @returns The version string
 */
export function getEnvironmentalFeatureContractVersion(feature: EnvironmentalFeatureContract): string {
    return feature.version;
}

// Versioning notes:
// - The 'version' field should be incremented for breaking changes to the contract.
// - Consumers should check the version before processing data.
// - For backward compatibility, provide migration utilities as needed in future versions.

/*
Integration Examples (usage snippets):

// Weather System
function applyWeatherFeature(feature) {
  if (feature.type === 'weather' && feature.name === 'Thunderstorm') {
    // ...
  }
}

// Hazard System
function handleHazard(feature) {
  if (feature.type === 'hazard') {
    // ...
  }
}

// Event System
function triggerSeasonalEvent(feature) {
  if (feature.type === 'season' && feature.name === 'Winter') {
    // ...
  }
}
*/

/**
 * Discriminated union types for specific environmental feature subtypes.
 */
export type WeatherFeature = EnvironmentalFeatureContract & {
    type: EnvironmentalFeatureType.WEATHER;
    parameters: {
        intensity: number; // 0-1
        duration: number; // minutes
        precipitationType?: 'rain' | 'snow' | 'hail';
        windSpeed?: number;
        [key: string]: unknown;
    };
};

export type HazardFeature = EnvironmentalFeatureContract & {
    type: EnvironmentalFeatureType.HAZARD;
    parameters: {
        severity: number; // 1-10
        affectedArea: string;
        [key: string]: unknown;
    };
};

export type SeasonFeature = EnvironmentalFeatureContract & {
    type: EnvironmentalFeatureType.SEASON;
    parameters: {
        temperature: number;
        daylightHours: number;
        [key: string]: unknown;
    };
};

/**
 * Union type for all environmental feature variants.
 */
export type AnyEnvironmentalFeature = WeatherFeature | HazardFeature | SeasonFeature | EnvironmentalFeatureContract; 