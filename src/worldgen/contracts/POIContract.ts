/**
 * POIContract defines the structure for a Point of Interest in the world.
 * @version 1.0.0
 * @example
 * const examplePOI: POIContract = {
 *   id: 'poi-001',
 *   name: 'Ancient Ruins',
 *   type: POIType.RUINS,
 *   state: POIState.DISCOVERED,
 *   modifiers: ['haunted', 'collapsed'],
 *   metadata: { discoveredBy: 'player-123', dangerLevel: 5 },
 *   version: '1.0.0',
 * };
 */
export enum POIType {
    RUINS = 'ruins',
    VILLAGE = 'village',
    CITY = 'city',
    DUNGEON = 'dungeon',
    LANDMARK = 'landmark',
    SHRINE = 'shrine',
    CAVE = 'cave',
}

export enum POIState {
    UNDISCOVERED = 'undiscovered',
    DISCOVERED = 'discovered',
    CLEARED = 'cleared',
    DESTROYED = 'destroyed',
}

export interface POIContract {
    /** Unique POI identifier */
    readonly id: string;
    /** Human-readable POI name */
    readonly name: string;
    /** Type of POI */
    readonly type: POIType;
    /** Current state of the POI */
    readonly state: POIState;
    /** List of modifiers (e.g., haunted, collapsed) */
    readonly modifiers: readonly string[];
    /** Arbitrary metadata (e.g., discoveredBy, dangerLevel) */
    readonly metadata: Record<string, unknown>;
    /** Version of the contract */
    readonly version: string;
}

/**
 * Helper to freeze a POIContract object for immutability at runtime.
 * @param poi The POIContract object to freeze
 * @returns The frozen POIContract object
 * @example
 * const frozenPOI = freezePOIContract(examplePOI);
 */
export function freezePOIContract(poi: POIContract): Readonly<POIContract> {
    return Object.freeze(poi);
}

// Note: All fields are readonly for compile-time immutability. Consumers should use freezePOIContract for runtime immutability.

/**
 * Query parameters for POI lookups.
 */
export interface POIQuery {
    type?: POIType;
    state?: POIState;
    modifiers?: string[];
    metadata?: Partial<Record<string, unknown>>;
}

/**
 * Interface for POI query methods.
 */
export interface POIQueryAPI {
    /**
     * Find POIs matching the query parameters.
     * @param query Query parameters
     * @returns Array of matching POIContract objects
     */
    findPOIs(query: POIQuery): POIContract[];
    /**
     * Get a POI by its unique ID.
     * @param id POI ID
     * @returns POIContract or undefined
     */
    getPOIById(id: string): POIContract | undefined;
}

/**
 * Stub for a spatial index for POIs (to be implemented in system code).
 */
export class POISpatialIndex {
    // Implementation would use a spatial data structure (e.g., R-tree, quadtree)
    // to optimize location-based queries. This is a placeholder for integration.
}

/**
 * Validate a POIContract object for required fields, types, and constraints.
 * @param poi The object to validate
 * @returns { errors: string[]; value?: POIContract } - errors array is empty if valid
 * @example
 * const result = validatePOIContract(examplePOI);
 * if (result.errors.length) { console.error(result.errors); }
 */
export function validatePOIContract(poi: any): { errors: string[]; value?: POIContract } {
    const errors: string[] = [];
    if (!poi || typeof poi !== 'object') errors.push('POI must be an object');
    if (typeof poi.id !== 'string') errors.push('id must be a string');
    if (typeof poi.name !== 'string') errors.push('name must be a string');
    if (!Object.values(POIType).includes(poi.type)) errors.push('type must be a valid POIType');
    if (!Object.values(POIState).includes(poi.state)) errors.push('state must be a valid POIState');
    if (!Array.isArray(poi.modifiers)) errors.push('modifiers must be an array of strings');
    if (typeof poi.metadata !== 'object' || poi.metadata === null) errors.push('metadata must be an object');
    if (typeof poi.version !== 'string') errors.push('version must be a string');
    return errors.length ? { errors } : { errors: [], value: poi as POIContract };
}

/**
 * Get the version of a POIContract object.
 * @param poi The POIContract object
 * @returns The version string
 */
export function getPOIContractVersion(poi: POIContract): string {
    return poi.version;
}

// Versioning notes:
// - The 'version' field should be incremented for breaking changes to the contract.
// - Consumers should check the version before processing data.
// - For backward compatibility, provide migration utilities as needed in future versions.

/*
Integration Examples (usage snippets):

// Quest System
function assignQuestToPOI(poi) {
  if (poi.type === 'ruins' && poi.state === 'undiscovered') {
    // ...
  }
}

// Event System
function triggerEventAtPOI(poi) {
  if (poi.modifiers && poi.modifiers.includes('haunted')) {
    // ...
  }
}

// Map System
function highlightPOI(poi) {
  // Use poi.state and poi.type to determine map icon
  // ...
}
*/ 