/**
 * Building location in 3D space
 */
export interface Location {
  x: number;
  y: number;
  z: number;
}

/**
 * Building dimensions
 */
export interface Dimensions {
  width: number;
  height: number;
  length: number;
}

/**
 * Building room data
 */
export interface Room {
  id: string;
  name: string;
  type: string;
  floor: number;
  dimensions: Dimensions;
  position: Location;
}

/**
 * Room connection data
 */
export interface Connection {
  from: string;
  to: string;
  type: string;
}

/**
 * Building interior data
 */
export interface BuildingInterior {
  floors: number;
  rooms: Room[];
  connections: Connection[];
}

/**
 * Building state information
 */
export interface BuildingState {
  condition: number;
  occupancy: number;
  power: {
    connected: boolean;
    consumption: number;
  };
  temperature: number;
  lastMaintenance?: Date;
  customProperties?: Record<string, any>;
}

/**
 * Building metadata
 */
export interface BuildingMetadata {
  description?: string;
  owner?: string;
  constructionDate?: Date;
  lastRenovation?: Date;
  customFields?: Record<string, any>;
}

/**
 * Main building data structure
 */
export interface Building {
  id: string;
  name: string;
  type: string;
  position: Location;
  dimensions: Dimensions;
  interior?: BuildingInterior;
  state?: BuildingState;
  metadata?: BuildingMetadata;
  createdAt?: Date;
  updatedAt?: Date;
} 