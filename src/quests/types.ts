import { Consequence } from './consequences/ConsequenceSystem';
import { FactionType } from '../types/factions/faction';

/**
 * Represents the current state of a quest, including player's progress
 */
export interface QuestState {
  inventory?: Record<string, number>;
  currentLocation?: string;
  npcInteractions?: Record<string, string[]>;
  combatVictories?: Record<string, number>;
  skills?: Record<string, number>;
  completedStages?: string[];
  currentStageId?: string;
  branchHistory?: { stageId: string; branchId: string }[];
}

/**
 * Represents a condition that must be met to progress in a quest
 */
export interface QuestCondition {
  type: string;
  parameters: Record<string, any>;
  description: string;
  evaluate(state: QuestState): boolean;
}

/**
 * Represents a branch in the quest progression
 */
export interface QuestBranch {
  id: string;
  condition: {
    type: string;
    value: any;
    operator: 'EQUALS' | 'NOT_EQUALS' | 'GREATER_THAN' | 'LESS_THAN' | 'CONTAINS' | 'NOT_CONTAINS';
  };
  nextStageId: string;
  description: string;
  factionRequirements?: Record<FactionType, number>;
  itemRequirements?: string[];
  skillRequirements?: string[];
  tags?: string[];
  involvedNPCs?: string[];
  consequences?: QuestConsequence[];
  emotionalImpact?: number;
}

/**
 * Represents a single stage in a quest
 */
export interface QuestStage {
  id: string;
  title: string;
  description: string;
  branches: QuestBranch[];
  requirements?: {
    items?: string[];
    skills?: string[];
    factions?: Record<FactionType, number>;
  };
  rewards?: {
    items?: string[];
    experience?: number;
    gold?: number;
    factionStanding?: Record<FactionType, number>;
  };
  objectives: QuestObjective[];
  nextStages?: string[];
  completed?: boolean;
}

/**
 * QuestTemplate defines the structure for all quest templates in the system.
 * See ../schemas/quest_template.schema.json for the JSON schema and ../QUEST_TEMPLATE_STRUCTURE.md for documentation.
 */
/**
 * Represents a complete quest template
 */
export interface QuestTemplate {
  id: string;
  title: string;
  description: string;
  type: QuestType;
  questType: QuestType;
  status: 'PENDING' | 'IN_PROGRESS' | 'COMPLETED' | 'FAILED' | 'CANCELLED';
  difficulty: number;
  requirements: QuestRequirements;
  objectives: QuestObjective[];
  dialogue: QuestDialogue[];
  rewards: QuestRewards;
  location?: string | null;
  customData?: Record<string, any>;
}

export type ConsequenceType = 
  | 'ITEM_REWARD'
  | 'ITEM_REMOVE'
  | 'WORLD_STATE'
  | 'FACTION_STANDING'
  | 'NPC_RELATIONSHIP';

export interface QuestConsequence {
  type: 'FACTION_STANDING' | 'ITEM_REWARD' | 'ITEM_REMOVE' | 'NPC_RELATIONSHIP' | 'WORLD_STATE';
  target: string;
  value: number | string | boolean;
  description: string;
}

export interface QuestRequirements {
  minimumLevel: number;
  minimumReputation: number;
  items?: string[];
  abilities?: string[];
}

export interface QuestDialogueResponse {
  text: string;
  nextDialogueId?: string;
  condition?: string;
}

export interface QuestDialogue {
  text: string;
  npcId: string;
  responses: QuestDialogueResponse[];
}

export interface DialogueVariation {
  standingThreshold?: number;
  text: string;
  tone?: string;
}

export interface QuestObjective {
  id: string;
  description: string;
  type: ObjectiveType;
  target?: string;
  amount?: number;
  location?: string;
  customData?: Record<string, any>;
  completed?: boolean;
  conditions?: QuestCondition[];
}

export type QuestType = 
  | 'CUSTOM'
  | 'KILL'
  | 'COLLECT'
  | 'EXPLORE'
  | 'INTERACT'
  | 'DIPLOMATIC'
  | 'RESOURCE_GATHERING'
  | 'TERRITORY_CONTROL';

export type ObjectiveType = 
  | 'CUSTOM'
  | 'KILL'
  | 'COLLECT'
  | 'EXPLORE'
  | 'INTERACT'
  | 'DIPLOMATIC_MEETING'
  | 'RESOURCE_EXCHANGE'
  | 'CONTROL'
  | 'CONTEST';

export interface QuestRewards {
  gold: number;
  experience: number;
  items: string[];
  reputation?: number;
  diplomaticInfluence?: number;
} 