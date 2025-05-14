import {
  POIType,
  POISubtype,
  Coordinates,
  ConnectionPoint,
  ThematicElements,
  StateTracking
} from '../types/POITypes';
import { IPOI } from '../types/IPOI';

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
  connections: ConnectionPoint[];
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
      }]
    };
  }

  // Serialization methods
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
        isActive: boolean;
        isDiscovered: boolean;
        isExplored: boolean;
        canExpand: boolean;
      };

      Object.assign(this, {
        ...restData,
        isActive: Boolean(typedData.isActive),
        isDiscovered: Boolean(typedData.isDiscovered),
        isExplored: Boolean(typedData.isExplored),
        canExpand: Boolean(typedData.canExpand)
      });
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
    // Validate all connections have valid source and target coordinates
    return this.connections.every(connection => 
      this.validateCoordinates(connection.sourceCoords) &&
      this.validateCoordinates(connection.targetCoords)
    );
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
} 