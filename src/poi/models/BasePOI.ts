import {
  POIType,
  POISubtype,
  Coordinates,
  ConnectionPoint,
  ThematicElements,
  StateTracking
} from '../types/POITypes';
import { IPOI } from '../interfaces/IPOI';

/**
 * Abstract base class implementing common POI functionality
 */
export abstract class BasePOI implements IPOI {
  id: string;
  name: string;
  type: POIType;
  subtype: POISubtype;
  description: string;
  coordinates: Coordinates;
  boundingBox: { width: number; height: number; depth: number; };
  connections: string[];
  adjacentPOIs: string[];
  features: { id: string; type: string; properties: Record<string, unknown>; }[];
  npcs: string[];
  items: string[];
  quests: string[];
  thematicElements: ThematicElements;
  stateTracking: StateTracking;
  isActive: boolean;
  isDiscovered: boolean;
  isExplored: boolean;
  canExpand: boolean;
  expansionRules?: { direction: 'north' | 'south' | 'east' | 'west' | 'up' | 'down'; conditions: string[]; probability: number; }[];
  position: Coordinates;
  size: { width: number; height: number; depth: number; };
  properties: Record<string, unknown>;

  constructor(
    id: string,
    name: string,
    type: POIType,
    subtype: POISubtype,
    coordinates: Coordinates,
    thematicElements: ThematicElements
  ) {
    this.id = id;
    this.name = name;
    this.type = type;
    this.subtype = subtype;
    this.coordinates = coordinates;
    this.thematicElements = thematicElements;
    this.position = coordinates;
    this.size = this.boundingBox;
    this.properties = {};

    // Initialize default values
    this.description = '';
    this.boundingBox = { width: 1, height: 1, depth: 1 };
    this.connections = [];
    this.adjacentPOIs = [];
    this.features = [];
    this.npcs = [];
    this.items = [];
    this.quests = [];
    this.isActive = false;
    this.isDiscovered = false;
    this.isExplored = false;
    this.canExpand = true;

    // Initialize state tracking
    this.stateTracking = {
      version: 1,
      lastModified: new Date(),
      modifiedBy: 'system',
      changeHistory: [{
        timestamp: new Date(),
        type: 'creation',
        details: 'POI created'
      }],
      visits: 0,
      discoveries: 0,
      interactions: 0,
      modificationHistory: []
    };
  }

  /**
   * Serialize the POI to a plain object for storage or transmission
   */
  serialize(): Record<string, unknown> {
    return {
      id: this.id,
      name: this.name,
      type: this.type,
      subtype: this.subtype,
      description: this.description,
      coordinates: this.coordinates,
      boundingBox: this.boundingBox,
      connections: this.connections,
      adjacentPOIs: this.adjacentPOIs,
      features: this.features,
      npcs: this.npcs,
      items: this.items,
      quests: this.quests,
      thematicElements: this.thematicElements,
      stateTracking: {
        ...this.stateTracking,
        lastModified: this.stateTracking.lastModified.toISOString(),
        changeHistory: this.stateTracking.changeHistory.map(ch => ({
          ...ch,
          timestamp: ch.timestamp.toISOString()
        }))
      },
      isActive: this.isActive,
      isDiscovered: this.isDiscovered,
      isExplored: this.isExplored,
      canExpand: this.canExpand,
      expansionRules: this.expansionRules
    };
  }

  /**
   * Deserialize a plain object into this POI instance
   * @param data - The data to deserialize
   */
  deserialize(data: Record<string, unknown>): void {
    if (typeof data.stateTracking === 'object' && data.stateTracking) {
      const stateData = data.stateTracking as {
        lastModified: string;
        changeHistory: Array<{
          timestamp: string;
          type: 'creation' | 'modification' | 'expansion' | 'deletion';
          details: string;
        }>;
      };

      this.stateTracking = {
        ...data.stateTracking as StateTracking,
        lastModified: new Date(stateData.lastModified),
        changeHistory: stateData.changeHistory.map(ch => ({
          ...ch,
          timestamp: new Date(ch.timestamp)
        }))
      };

      // Remove stateTracking from data to avoid double processing
      const { stateTracking, ...restData } = data;

      // Type assertion for boolean fields
      const typedData = restData as {
        isActive?: boolean | string;
        isDiscovered?: boolean | string;
        isExplored?: boolean | string;
        canExpand?: boolean | string;
      };

      // Helper to coerce string|boolean to boolean
      function toBool(val: boolean | string | undefined): boolean {
        if (typeof val === 'string') return val === 'true';
        return Boolean(val);
      }

      Object.assign(this, {
        ...restData
      });
      this.isActive = toBool(typedData.isActive);
      this.isDiscovered = toBool(typedData.isDiscovered);
      this.isExplored = toBool(typedData.isExplored);
      this.canExpand = toBool(typedData.canExpand);
    } else {
      throw new Error('Invalid state tracking data in POI deserialization');
    }
  }

  // State management methods
  activate(): void {
    this.isActive = true;
    this.trackChange('modification', 'POI activated');
  }

  deactivate(): void {
    this.isActive = false;
    this.trackChange('modification', 'POI deactivated');
  }

  discover(): void {
    this.isDiscovered = true;
    this.trackChange('modification', 'POI discovered');
  }

  explore(): void {
    this.isExplored = true;
    this.trackChange('modification', 'POI explored');
  }

  // Validation methods
  validate(): boolean {
    return (
      this.validateBasicProperties() &&
      this.validateConnections() &&
      this.validateThematicCoherence()
    );
  }

  validateConnections(): boolean {
    // Validate all connections are non-empty strings
    return this.connections.every(id => typeof id === 'string' && id.length > 0);
  }

  validateThematicCoherence(): boolean {
    // Validate thematic elements are consistent with POI type and subtype
    return (
      this.thematicElements.biome &&
      this.thematicElements.climate &&
      this.thematicElements.era &&
      this.thematicElements.culture &&
      this.thematicElements.dangerLevel >= 0 &&
      this.thematicElements.dangerLevel <= 10
    );
  }

  // Protected helper methods
  protected validateBasicProperties(): boolean {
    return (
      !!this.id &&
      !!this.name &&
      !!this.type &&
      !!this.subtype &&
      this.validateCoordinates(this.coordinates)
    );
  }

  protected validateCoordinates(coords: Coordinates): boolean {
    return (
      typeof coords.x === 'number' &&
      typeof coords.y === 'number' &&
      typeof coords.z === 'number' &&
      typeof coords.level === 'number'
    );
  }

  protected trackChange(type: 'creation' | 'modification' | 'expansion' | 'deletion', details: string): void {
    this.stateTracking.version++;
    this.stateTracking.lastModified = new Date();
    this.stateTracking.changeHistory.push({
      timestamp: new Date(),
      type,
      details
    });
  }

  /**
   * Add a connection to another POI by ID
   * @param targetPoiId - The ID of the POI to connect to
   */
  public addConnection(targetPoiId: string): void {
    if (!this.connections.includes(targetPoiId)) {
      this.connections.push(targetPoiId);
    }
  }

  /**
   * Get all connected POI IDs
   * @returns Array of connected POI IDs
   */
  public getConnections(): string[] {
    return [...this.connections];
  }

  /**
   * Returns the coordinates of the POI (for spatial indexing)
   * @returns Coordinates object
   */
  public getPosition(): Coordinates {
    return this.coordinates;
  }

  /**
   * Tracks state changes for auditing and debugging
   * @param details - Description of the change
   * @param type - Type of change (creation, modification, expansion, deletion)
   */
  public updateStateTracking(details: string, type: 'creation' | 'modification' | 'expansion' | 'deletion') {
    if (!this.stateTracking) return;
    this.stateTracking.version++;
    this.stateTracking.lastModified = new Date();
    this.stateTracking.changeHistory.push({
      timestamp: new Date(),
      type,
      details
    });
  }

  // IPOI interface methods
  getStateTracking(): StateTracking {
    return this.stateTracking;
  }

  setCoordinates(coordinates: Coordinates): void {
    this.coordinates = coordinates;
    this.position = coordinates;
  }

  getCoordinates(): Coordinates {
    return this.coordinates;
  }

  setPosition(position: Coordinates): void {
    this.setCoordinates(position);
  }

  setSize(size: { width: number; height: number; depth: number; }): void {
    this.size = size;
    this.boundingBox = size;
  }

  getSize(): { width: number; height: number; depth: number; } {
    return this.size;
  }

  setThematicElements(elements: ThematicElements): void {
    this.thematicElements = elements;
  }

  getThematicElements(): ThematicElements {
    return this.thematicElements;
  }

  setProperty(key: string, value: unknown): void {
    this.properties[key] = value;
  }

  getProperty<T>(key: string): T | undefined {
    return this.properties[key] as T | undefined;
  }

  hasProperty(key: string): boolean {
    return Object.prototype.hasOwnProperty.call(this.properties, key);
  }

  /**
   * Remove a connection to another POI by ID
   * @param targetPoiId - The ID of the POI to disconnect
   */
  public removeConnection(targetPoiId: string): void {
    this.connections = this.connections.filter(id => id !== targetPoiId);
  }

  /**
   * Get the POI type
   */
  public getType(): POIType {
    return this.type;
  }

  /**
   * Get the POI subtype
   */
  public getSubtype(): POISubtype {
    return this.subtype;
  }
} 