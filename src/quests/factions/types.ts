import type { FactionType } from '../../types/factions/faction';
export { FactionType } from '../../types/factions/faction';
import { QuestTemplate, QuestDialogue, QuestStage, QuestObjective, QuestRewards, QuestBranch } from '../types';
import { WorldStateChange } from '../consequences/ConsequenceSystem';
import { QuestType, ObjectiveType } from '../types';
import { QuestResource, QuestCondition } from '../resources/types';

/**
 * Represents a resource owned or managed by a faction (e.g., gold, territory, influence)
 */
export interface FactionResource {
  type: string;
  amount: number;
}

/**
 * Represents a value or trait of a faction (e.g., honor, aggression, diplomacy)
 */
export interface FactionValue {
  key: string;
  value: number;
}

/**
 * Represents the persistent data for a faction, including relationships, values, and resources
 */
export interface FactionData {
  id: FactionType;
  name: string;
  description: string;
  relationships: Record<FactionType, number>; // -100 (hostile) to 100 (allied)
  values: Record<string, number>;
  resources: Record<string, number>;
  standing: number;
  tier: number;
}

/**
 * Main profile for a faction, used at runtime
 */
export interface FactionProfile {
  id: FactionType;
  name: string;
  description: string;
  relationships: Map<FactionType, number>; // -100 (hostile) to 100 (allied)
  values: Map<string, number>;
  resources: Map<string, number>;
  standing: number;
  tier: number;
}

export interface FactionQuestTemplate extends QuestTemplate {
  factionId: FactionType;
  questType: QuestType;
  factionRequirements: {
    minimumStanding: number;
    maximumStanding: number;
    minimumReputation?: number;
    minimumTier?: number;
    diplomaticStatus?: 'NEUTRAL' | 'FRIENDLY' | 'HOSTILE' | 'ALLIED';
    requiredResources?: QuestResource[];
    requiredConditions?: QuestCondition[];
  };
  factionRewards: {
    standingGain: number;
    reputationGain?: number;
    specialRewards?: string[];
    diplomaticBenefits?: {
      tensionReduction?: number;
      allianceProgress?: number;
      tradeBenefits?: {
        resourceMultiplier: number;
        duration: number;
      };
      territoryAccess?: string[];
    };
  };
  factionObjectives: QuestObjective[];
  consequences?: WorldStateChange[];
  diplomaticOptions?: {
    negotiationApproaches: {
      type: 'AGGRESSIVE' | 'NEUTRAL' | 'FRIENDLY';
      successChance: number;
      standingImpact: number;
      description: string;
    }[];
    resourceExchangeOptions: {
      offered: QuestResource[];
      requested: QuestResource[];
      bonusEffect?: {
        type: string;
        value: number;
      };
    }[];
    meetingLocations: {
      location: string;
      neutralGround: boolean;
      securityLevel: number;
      description: string;
    }[];
    fallbackPlans: {
      condition: string;
      alternativeObjectives: QuestObjective[];
      reducedRewards: Partial<QuestRewards>;
    }[];
  };
}

export interface FactionQuestConfig {
  mutuallyExclusiveThreshold: number;
  standingGainMultiplier: number;
  reputationGainMultiplier: number;
  defaultMinimumStanding: number;
  defaultMaximumStanding: number;
}

/**
 * Represents a faction-specific objective within a quest
 */
export interface FactionObjective {
  type: 'diplomacy' | 'combat' | 'stealth' | 'trade' | 'exploration';
  difficulty: number;
  description: string;
  factionImpact: {
    primary: number;
    allied?: number;
    opposing?: number;
  };
  alternatives?: {
    type: string;
    description: string;
    difficulty: number;
    factionImpact: {
      primary: number;
      allied?: number;
      opposing?: number;
    };
  }[];
}

/**
 * Configuration for the faction quest template generator
 */
export interface FactionQuestGeneratorConfig {
  baseTemplateModifiers: {
    difficultyMultiplier: number;
    rewardMultiplier: number;
    objectiveCount: number;
  };
  factionSpecificModifiers: Record<FactionType, {
    difficultyMultiplier: number;
    rewardMultiplier: number;
    preferredObjectiveTypes: string[];
  }>;
  competingQuestProbability: number;
  specialRewardProbability: number;
}

/**
 * Represents a faction-specific stage in a quest
 */
export interface FactionQuestStage extends QuestStage {
  factionRequirements?: {
    standing: number;
    specialItems?: string[];
    specialAbilities?: string[];
  };
  factionBranches: FactionQuestBranch[];
}

/**
 * Represents a faction-specific branch in quest progression
 */
export interface FactionQuestBranch extends QuestBranch {
  factionRequirements?: {
    minimumStanding: number;
    maximumStanding: number;
    diplomaticStatus?: 'NEUTRAL' | 'FRIENDLY' | 'HOSTILE' | 'ALLIED';
  };
  factionConsequences?: WorldStateChange[];
} 