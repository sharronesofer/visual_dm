import { BaseEntity } from './BaseEntity';
import { WeatherCondition } from './World';

/**
 * Location type enum
 */
export enum LocationType {
    CITY = 'city',
    TOWN = 'town',
    VILLAGE = 'village',
    DUNGEON = 'dungeon',
    CAVE = 'cave',
    FOREST = 'forest',
    MOUNTAIN = 'mountain',
    LAKE = 'lake',
    RIVER = 'river',
    OCEAN = 'ocean',
    DESERT = 'desert',
    RUIN = 'ruin',
    TEMPLE = 'temple',
    CASTLE = 'castle',
    CAMP = 'camp',
    SHOP = 'shop',
    INN = 'inn',
    HOUSE = 'house',
    CUSTOM = 'custom'
}

/**
 * State of a resource within a location
 */
export interface ResourceState {
    id: string;
    name: string;
    type: string;
    quantity: number;
    maxQuantity: number;
    regenerationRate: number; // Units per game hour
    lastUpdated: Date;
    isDepletable: boolean;
}

/**
 * Encounter table entry for generating random encounters
 */
export interface EncounterTableEntry {
    id: string;
    type: 'npc' | 'event' | 'item' | 'custom';
    targetId: string | number; // ID of the encounter entity
    weight: number; // Relative probability of this encounter
    minLevel?: number; // Minimum player level for this encounter
    maxLevel?: number; // Maximum player level for this encounter
    conditions?: Record<string, any>; // Additional conditions for this encounter
    timeRestrictions?: { // When this encounter can happen
        minTime?: string; // 24-hour format, e.g., "20:00"
        maxTime?: string; // 24-hour format, e.g., "06:00"
        allowedDays?: number[]; // 0-6, where 0 is Sunday
    };
    weatherRestrictions?: WeatherCondition[]; // Allowed weather types
}

/**
 * Access requirement for a location
 */
export interface AccessRequirement {
    type: 'item' | 'quest' | 'faction' | 'skill' | 'stat' | 'time' | 'custom';
    value: any; // Requirement value/threshold
    description: string; // Human-readable description
    isHidden: boolean; // Whether this requirement is initially hidden
}

/**
 * Location event definition
 */
export interface LocationEvent {
    id: string;
    name: string;
    description: string;
    startTime?: Date;
    endTime?: Date;
    recurringSchedule?: {
        frequency: 'daily' | 'weekly' | 'monthly' | 'yearly' | 'custom';
        interval: number; // How many units of frequency between occurrences
        byWeekday?: number[]; // 0-6, where 0 is Sunday
        byMonthDay?: number[]; // 1-31, day of month
        byMonth?: number[]; // 1-12, month of year
        startTime?: string; // 24-hour format
        endTime?: string; // 24-hour format
        customPattern?: string; // For complex patterns
    };
    isActive: boolean;
    probability: number; // 0-100, chance of event occurring when conditions are met
    conditions?: Record<string, any>; // Conditions for this event to occur
    effects: Record<string, any>; // Effects of this event on the location/world
}

/**
 * Location interface representing a place in the game world
 */
export interface Location extends BaseEntity {
    name: string;
    description: string;

    // Basic properties
    type: LocationType;
    subtype?: string; // Further classification
    coordinates: { x: number, y: number, z?: number }; // Position in world

    // State tracking
    currentState: {
        isDiscovered: boolean;
        isAccessible: boolean;
        isActive: boolean;
        customStates: Record<string, any>; // Additional state flags
    };

    // Environmental properties
    localWeather?: WeatherCondition; // Override of world weather
    weatherModifiers?: Record<string, number>; // How this location affects weather probabilities

    // Encounters
    encounterTable: EncounterTableEntry[];
    encounterChance: number; // Base percentage chance per time unit

    // Resources
    resources: ResourceState[];

    // Events
    events: LocationEvent[];

    // Access control
    accessRequirements: AccessRequirement[];

    // Connections to other locations
    connections: {
        locationId: string | number;
        type: 'road' | 'path' | 'river' | 'portal' | 'gate' | 'custom';
        distance: number; // Travel distance/time
        isHidden: boolean;
        accessRequirements?: AccessRequirement[];
    }[];

    // Important entities
    npcs: string[] | number[]; // IDs of NPCs at this location
    items: string[] | number[]; // IDs of items at this location

    // Visual/UI data
    mapIcon?: string;
    minimapVisibility?: 'always' | 'discovered' | 'never';
    zoomLevels?: number[]; // At what map zoom levels this location is visible
} 