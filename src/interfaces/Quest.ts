import { BaseEntity } from './BaseEntity';

/**
 * Quest status enum
 */
export enum QuestStatus {
    AVAILABLE = 'available',
    IN_PROGRESS = 'in_progress',
    COMPLETED = 'completed',
    FAILED = 'failed',
    EXPIRED = 'expired'
}

/**
 * Quest stage condition types enum
 */
export enum ConditionType {
    KILL = 'kill',
    COLLECT = 'collect',
    VISIT = 'visit',
    TALK = 'talk',
    ESCORT = 'escort',
    DEFEND = 'defend',
    DELIVER = 'deliver',
    USE_SKILL = 'use_skill',
    USE_ITEM = 'use_item',
    CUSTOM = 'custom'
}

/**
 * Quest stage completion condition
 */
export interface QuestCondition {
    id: string;
    type: ConditionType;
    target: {
        id?: string | number; // ID of the target entity
        type?: string; // Type of entity (e.g., "npc", "item", "location")
        quantity?: number; // How many needed if applicable
        customData?: Record<string, any>; // Any additional data needed for the condition
    };
    description: string;
    isHidden: boolean; // Whether this condition is initially hidden from the player
    isOptional: boolean; // Whether this condition is optional for completing the stage
    progress: number; // 0-100 percent completion
}

/**
 * Quest stage reward
 */
export interface QuestReward {
    type: 'item' | 'gold' | 'xp' | 'faction_reputation' | 'custom';
    value: number | string; // Amount or item ID
    customData?: Record<string, any>; // Additional data for custom rewards
    isHidden: boolean; // Whether this reward is initially hidden from the player
}

/**
 * Quest stage interface
 */
export interface QuestStage {
    id: string;
    title: string;
    description: string;
    conditions: QuestCondition[];
    rewards: QuestReward[];
    nextStageIds: string[]; // Possible next stages (for branching)
    status: QuestStatus;
    isHidden: boolean; // Whether this stage is initially hidden
    timeLimit?: number; // Time limit in minutes, if applicable
    failureConditions?: QuestCondition[]; // Conditions that cause this stage to fail
}

/**
 * Quest world impact definition
 */
export interface QuestWorldImpact {
    type: 'faction_change' | 'world_flag' | 'npc_state' | 'location_state' | 'custom';
    targetId?: string | number; // ID of the target entity
    value: any; // The impact value (e.g., reputation change amount, new state)
    condition?: string; // Optional condition for when this impact occurs
    description: string; // Human-readable description of the impact
}

/**
 * Quest interface representing a multi-stage quest
 */
export interface Quest extends BaseEntity {
    title: string;
    description: string;

    // Basic properties
    giver: {
        id: string | number;
        type: 'npc' | 'item' | 'location';
    };
    level: number; // Recommended level
    isRepeatable: boolean;
    cooldownTime?: number; // Time in minutes before quest can be taken again

    // Quest structure
    stages: QuestStage[];
    initialStageIds: string[]; // Starting stages (usually just one, but could be multiple for complex quests)
    currentStageIds: string[]; // Currently active stages (can be multiple in parallel)

    // Dependencies and requirements
    prerequisites: {
        questIds?: (string | number)[]; // IDs of quests that must be completed first
        factionRequirements?: { id: string | number, minReputation: number }[]; // Minimum reputation with factions
        levelRequirement?: number; // Minimum level required
        skillRequirements?: { skill: string, level: number }[]; // Minimum skill levels required
        itemRequirements?: { id: string | number, quantity: number }[]; // Items needed to start the quest
        customRequirements?: Record<string, any>; // Any additional requirements
    };

    // Quest properties
    status: QuestStatus;
    expirationDate?: Date; // When the quest will no longer be available
    dateStarted?: Date; // When the quest was started
    dateCompleted?: Date; // When the quest was completed

    // Impact on world
    worldImpacts: QuestWorldImpact[]; // Changes to the world when the quest is completed

    // Hidden objectives & rewards
    hiddenObjectives: QuestCondition[]; // Bonus objectives not revealed to the player
    hiddenRewards: QuestReward[]; // Bonus rewards not revealed to the player
} 