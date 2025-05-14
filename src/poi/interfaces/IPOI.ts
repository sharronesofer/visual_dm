import { POIType, POISubtype, Coordinates, ThematicElements, StateTracking, POISize } from '../types/POITypes';

/**
 * Interface for all Point of Interest (POI) objects
 *
 * - id: Unique identifier for the POI
 * - type: Main POI category (see POIType enum)
 * - subtype: Specific POI subtype (see POISubtype enum)
 * - position: 3D coordinates in the world
 * - size: Physical size of the POI
 * - name: Human-readable name
 * - description: Optional description
 * - properties: Arbitrary key-value pairs for extensibility
 * - thematicElements: Thematic/environmental attributes
 * - stateTracking: Persistence and change history
 * - connections: List of connected POI IDs
 *
 * Methods provide validation, serialization, state, connection, and property management.
 */
export interface IPOI {
    id: string;
    type: POIType;
    subtype: POISubtype;
    position: Coordinates;
    size: POISize;
    name: string;
    description?: string;
    properties: Record<string, unknown>;
    thematicElements: ThematicElements;
    stateTracking: StateTracking;
    connections: string[];

    // Core methods
    validate(): boolean;
    serialize(): Record<string, unknown>;
    deserialize(data: Record<string, unknown>): void;
    
    // State management
    getStateTracking(): StateTracking;
    updateStateTracking(details: string, type: 'modification' | 'expansion'): void;
    
    // Connection management
    addConnection(poiId: string): void;
    removeConnection(poiId: string): void;
    getConnections(): string[];
    
    // Coordinate management
    setCoordinates(coordinates: Coordinates): void;
    getCoordinates(): Coordinates;
    
    // Thematic elements
    setThematicElements(elements: ThematicElements): void;
    getThematicElements(): ThematicElements;

    // Position methods
    setPosition(position: Coordinates): void;
    getPosition(): Coordinates;

    // Size methods
    setSize(size: POISize): void;
    getSize(): POISize;

    // Type methods
    getType(): POIType;
    getSubtype(): POISubtype;

    // Property methods
    setProperty(key: string, value: unknown): void;
    getProperty<T>(key: string): T | undefined;
    hasProperty(key: string): boolean;
} 