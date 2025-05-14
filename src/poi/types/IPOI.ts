import { 
  POIType, 
  POISubtype, 
  Coordinates, 
  ConnectionPoint, 
  ThematicElements, 
  StateTracking 
} from './POITypes';

/**
 * Base interface for all Points of Interest (POIs) in the game world
 */
export interface IPOI {
  id: string;
  name: string;
  type: POIType;
  subtype: POISubtype;
  description: string;
  
  // Location and spatial information
  coordinates: Coordinates;
  boundingBox: {
    width: number;
    height: number;
    depth: number;
  };
  
  // Connectivity
  connections: ConnectionPoint[];
  adjacentPOIs: string[]; // IDs of neighboring POIs
  
  // Content and features
  features: {
    id: string;
    type: string;
    properties: Record<string, unknown>;
  }[];
  
  // NPCs, items, and other content
  npcs: string[]; // IDs of NPCs present in the POI
  items: string[]; // IDs of items present in the POI
  quests: string[]; // IDs of available quests
  
  // Thematic and environmental properties
  thematicElements: ThematicElements;
  
  // State and persistence
  stateTracking: StateTracking;
  isActive: boolean;
  isDiscovered: boolean;
  isExplored: boolean;
  
  // Dynamic expansion properties
  canExpand: boolean;
  expansionRules?: {
    direction: 'north' | 'south' | 'east' | 'west' | 'up' | 'down';
    conditions: string[];
    probability: number;
  }[];
  
  // Serialization methods
  serialize(): Record<string, unknown>;
  deserialize(data: Record<string, unknown>): void;
  
  // State management methods
  activate(): void;
  deactivate(): void;
  discover(): void;
  explore(): void;
  
  // Validation methods
  validate(): boolean;
  validateConnections(): boolean;
  validateThematicCoherence(): boolean;
} 