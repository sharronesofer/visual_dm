import { BaseEntity } from './BaseEntity';

/**
 * Faction alignment enum
 */
export enum FactionAlignment {
    LAWFUL_GOOD = 'lawful_good',
    NEUTRAL_GOOD = 'neutral_good',
    CHAOTIC_GOOD = 'chaotic_good',
    LAWFUL_NEUTRAL = 'lawful_neutral',
    TRUE_NEUTRAL = 'true_neutral',
    CHAOTIC_NEUTRAL = 'chaotic_neutral',
    LAWFUL_EVIL = 'lawful_evil',
    NEUTRAL_EVIL = 'neutral_evil',
    CHAOTIC_EVIL = 'chaotic_evil'
}

/**
 * Faction relationship status
 */
export interface FactionRelationship {
    targetFactionId: string | number;
    stance: 'allied' | 'friendly' | 'neutral' | 'unfriendly' | 'hostile';
    value: number; // -100 to 100 numerical value
    reasonText?: string; // Explanation of relationship
    tradeAgreement?: boolean; // Whether there's a trade agreement
    nonAggressionPact?: boolean; // Whether there's a non-aggression pact
    alliance?: boolean; // Whether there's a formal alliance
    warState?: {
        isAtWar: boolean;
        startDate?: Date;
        casualties?: { [factionId: string]: number };
        territoryControl?: Record<string, any>;
    };
}

/**
 * Resource controlled by a faction
 */
export interface FactionResource {
    id: string;
    type: string;
    name: string;
    amount: number;
    maxAmount: number;
    location?: string | number; // Location ID where resource is based
    generationRate: number; // Units per game hour
    consumptionRate: number; // Units per game hour
    lastUpdated: Date;
}

/**
 * A territory controlled by a faction
 */
export interface Territory {
    id: string;
    name: string;
    locationIds: (string | number)[]; // Locations in this territory
    controlLevel: number; // 0-100 how much control the faction has
    contestedBy?: (string | number)[]; // Faction IDs contesting this territory
    taxRate?: number; // Taxation level in this territory
    resources?: FactionResource[]; // Resources in this territory
    populationCount?: number; // Population in this territory
}

/**
 * Faction interface representing a group or organization
 */
export interface Faction extends BaseEntity {
    name: string;
    description: string;

    // Basic properties
    alignment: FactionAlignment;
    type: string; // Type of faction (e.g., "guild", "kingdom", "tribe", etc.)

    // Leadership and hierarchy
    leaderId?: string | number; // ID of leader character
    leadership: { // Leadership structure
        characterId: string | number;
        role: string;
        influence: number; // 0-100
    }[];
    parentFactionId?: string | number; // Parent faction if this is a subfaction
    subFactions?: (string | number)[]; // IDs of subfactions

    // Relationships
    relationships: FactionRelationship[];

    // Territory and resources
    headquarters?: string | number; // Location ID of headquarters
    territories: Territory[];
    resources: FactionResource[];

    // Members
    memberIds: (string | number)[]; // IDs of member characters
    requiredReputationJoin: number; // Reputation required to join

    // Reputation levels (thresholds and names)
    reputationLevels: {
        value: number; // Threshold value
        name: string; // Name of this reputation level
        benefits: string[]; // Benefits at this level
    }[];

    // Economic data
    economy: {
        wealth: number;
        income: number; // Per game day
        expenses: number; // Per game day
        taxRate: number; // Base tax rate
        tradeProficiency: number; // 0-100, affects trade prices
    };

    // Military strength
    military?: {
        strength: number; // Overall military power
        troops: { type: string, count: number }[];
        equipmentQuality: number; // 0-100
        trainingLevel: number; // 0-100
        strategy: string; // Preferred strategy
    };

    // Faction goals and behavior
    goals: {
        id: string;
        description: string;
        priority: number;
        progress: number; // 0-100
        targetIds?: (string | number)[]; // Related entity IDs
    }[];

    // Cultural aspects
    culture: {
        values: string[];
        traditions: string[];
        language?: string;
        symbols?: string[];
    };

    // Current state
    isActive: boolean;
    influence: number; // 0-100, overall world influence

    // Historical data
    foundingDate?: Date;
    majorEvents?: {
        date: Date;
        description: string;
        impact: number; // -100 to 100, how it affected the faction
    }[];
} 