import { BaseEntity } from './BaseEntity';

/**
 * NPC personality trait enum
 */
export enum PersonalityTrait {
    BRAVE = 'brave',
    COWARDLY = 'cowardly',
    HONEST = 'honest',
    DECEITFUL = 'deceitful',
    FRIENDLY = 'friendly',
    HOSTILE = 'hostile',
    CURIOUS = 'curious',
    CAUTIOUS = 'cautious',
    GREEDY = 'greedy',
    GENEROUS = 'generous',
    PATIENT = 'patient',
    IMPULSIVE = 'impulsive',
    FORGIVING = 'forgiving',
    VENGEFUL = 'vengeful',
    OPTIMISTIC = 'optimistic',
    PESSIMISTIC = 'pessimistic'
}

/**
 * Relationship status between NPCs or NPC and player
 */
export interface Relationship {
    targetId: string | number; // ID of the related character
    opinion: number; // -100 to 100, negative for dislike, positive for like
    trust: number; // -100 to 100, how much this NPC trusts the target
    fear: number; // 0 to 100, how much this NPC fears the target
    respect: number; // 0 to 100, how much this NPC respects the target
    familiarity: number; // 0 to 100, how well this NPC knows the target
    history: RelationshipEvent[]; // History of interactions
}

/**
 * Event in a relationship history
 */
export interface RelationshipEvent {
    date: Date;
    type: string; // e.g., "helped", "betrayed", "met", etc.
    impact: number; // How significant this event was (-100 to 100)
    description: string;
}

/**
 * Schedule entry for NPC daily routines
 */
export interface ScheduleEntry {
    startTime: string; // 24-hour format, e.g., "08:00"
    endTime: string; // 24-hour format, e.g., "12:00"
    activity: string; // What the NPC is doing
    locationId?: string | number; // Where the NPC is during this time
    priority: number; // Higher numbers take precedence if schedules conflict
    conditions?: Record<string, any>; // Conditions that must be met for this schedule entry to be active
}

/**
 * NPC goal for driving behavior
 */
export interface NPCGoal {
    id: string;
    description: string;
    priority: number; // Higher numbers are more important
    conditions: Record<string, any>; // Conditions that must be met to consider this goal completed
    status: 'active' | 'completed' | 'failed' | 'abandoned';
}

/**
 * NPC memory of past events
 */
export interface NPCMemory {
    id: string;
    date: Date;
    description: string;
    importance: number; // 0-100, affects how long the memory lasts
    relatedEntityIds: (string | number)[]; // IDs of entities involved in this memory
    emotions: Record<string, number>; // Emotional response to this memory, e.g., {"anger": 60, "joy": 0}
    expirationDate?: Date; // When this memory will be forgotten, if applicable
}

/**
 * NPC interface representing a non-player character
 */
export interface NPC extends BaseEntity {
    name: string;
    description?: string;

    // Basic properties
    level: number;
    faction?: string | number; // Faction ID the NPC belongs to
    occupation: string;
    isUnique: boolean; // Whether this is a unique NPC or generic/generated

    // Visual attributes
    appearance: {
        race: string;
        gender: string;
        height: number;
        weight: number;
        hairColor?: string;
        eyeColor?: string;
        distinguishingFeatures?: string[];
    };

    // Personality and behavior
    personalityTraits: PersonalityTrait[];
    moodState: Record<string, number>; // Current mood, e.g., {"angry": 60, "happy": 20}
    relationships: Relationship[];

    // Daily schedule and behavior
    schedule: ScheduleEntry[];
    currentActivity?: string;
    currentLocationId?: string | number;

    // Goal-driven behavior
    goals: NPCGoal[];

    // Memory system
    memories: NPCMemory[];
    memoryCapacity: number; // Maximum number of memories this NPC can have

    // Stats
    stats: {
        health: number;
        maxHealth: number;
        combatAbility: number;
        persuasiveness: number;
        intelligence: number;
        [key: string]: number; // Other custom stats
    };
} 