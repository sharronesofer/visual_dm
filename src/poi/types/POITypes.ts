/**
 * Enums and types for the POI (Point of Interest) system
 */

/**
 * Primary POI types available in the system
 *
 * - SETTLEMENT: Towns, villages, cities, outposts, etc.
 * - DUNGEON: Caves, ruins, temples, fortresses, etc.
 * - LANDMARK: Natural or constructed points of interest (mountain, lake, monument, etc.)
 * - RESOURCE: Resource locations (mine, quarry, lumber camp, etc.)
 */
export enum POIType {
  SETTLEMENT = 'SETTLEMENT',
  DUNGEON = 'DUNGEON',
  LANDMARK = 'LANDMARK',
  RESOURCE = 'RESOURCE',
  EXPLORATION = 'EXPLORATION',
  SOCIAL = 'SOCIAL'
}

/**
 * POI subtypes for specialized POIs, grouped by main type.
 *
 * - Settlement subtypes: VILLAGE, TOWN, CITY, OUTPOST
 * - Dungeon subtypes: CAVE, RUIN, TEMPLE, FORTRESS
 * - Landmark subtypes: MOUNTAIN, LAKE, FOREST, MONUMENT
 * - Resource subtypes: MINE, QUARRY, LUMBER_CAMP, HUNTING_GROUND
 *
 * Extend this enum as new POI subtypes are introduced.
 */
export enum POISubtype {
  // Settlement subtypes
  VILLAGE = 'VILLAGE',
  TOWN = 'TOWN',
  CITY = 'CITY',
  OUTPOST = 'OUTPOST',

  // Dungeon subtypes
  CAVE = 'CAVE',
  RUIN = 'RUIN',
  TEMPLE = 'TEMPLE',
  FORTRESS = 'FORTRESS',

  // Landmark subtypes
  MOUNTAIN = 'MOUNTAIN',
  LAKE = 'LAKE',
  FOREST = 'FOREST',
  MONUMENT = 'MONUMENT',

  // Resource subtypes
  MINE = 'MINE',
  QUARRY = 'QUARRY',
  LUMBER_CAMP = 'LUMBER_CAMP',
  HUNTING_GROUND = 'HUNTING_GROUND'
}

// Dungeon subtypes
export enum DungeonSubtype {
  CAVE = 'CAVE',
  RUIN = 'RUIN',
  TEMPLE = 'TEMPLE',
  FORTRESS = 'FORTRESS',
  CRYPT = 'CRYPT',
  MINE = 'MINE'
}

// Exploration subtypes
export enum ExplorationSubtype {
  WILDERNESS = 'WILDERNESS',
  LANDMARK = 'LANDMARK',
  MOUNTAIN = 'MOUNTAIN',
  GROVE = 'GROVE'
}

// Social subtypes
export enum SocialSubtype {
  VILLAGE = 'VILLAGE',
  MARKET = 'MARKET',
  GUILD = 'GUILD',
  CASTLE = 'CASTLE'
}

/**
 * Coordinates in 3D space with level information
 */
export interface Coordinates {
  x: number;
  y: number;
  z: number;
  level: number;
}

/**
 * Connection point between POIs
 */
export interface ConnectionPoint {
  id: string;
  sourceCoords: Coordinates;
  targetCoords: Coordinates;
  type: 'door' | 'path' | 'portal' | 'bridge';
  properties: {
    isLocked?: boolean;
    requiredKey?: string;
    isHidden?: boolean;
    isOneWay?: boolean;
  };
}

/**
 * Thematic elements that define the POI's atmosphere and setting
 */
export interface ThematicElements {
  biome: string;
  climate: string;
  era: string;
  culture: string;
  dangerLevel: number; // 0-10
  lighting: 'dark' | 'dim' | 'bright';
  weather?: string;
  ambientSounds?: string[];
  visualEffects?: string[];
  themes: string[];
  difficulty?: number;
  resourceDensity?: number;
  population?: number;
}

/**
 * Change history entry for state tracking
 */
export interface ChangeHistoryEntry {
  timestamp: Date;
  type: 'creation' | 'modification' | 'expansion' | 'deletion';
  details: string;
}

/**
 * State tracking for POI persistence
 */
export interface StateTracking {
  version: number;
  lastModified: Date;
  modifiedBy: string;
  changeHistory: ChangeHistoryEntry[];
  visits: number;
  discoveries: number;
  interactions: number;
  modificationHistory: {
    timestamp: Date;
    details: string;
    type: 'modification' | 'expansion';
  }[];
}

export interface POISize {
  width: number;
  height: number;
  depth?: number;
}

export interface POIBounds {
  position: Coordinates;
  size: POISize;
} 