import { FactionType } from '../../../types/factions/faction';
import { WorldStateChange } from '../../consequences/ConsequenceSystem';
import { FactionQuestTemplate as BaseFactionQuestTemplate } from '../../factions/types';

export interface QuestResource {
  id: string;
  amount: number;
}

export interface QuestCondition {
  type: string;
  value: any;
}

export interface CompletedQuest {
  questId: string;
  factionId: FactionType;
  completionTime: number;
}

/**
 * Configuration for the competing quest system
 */
export interface CompetingQuestConfig {
  maxActiveGroups: number;
  maxQuestsPerGroup: number;
  questExpirationTime: number;
  tensionDecayInterval: number;
  tensionDecayAmount: number;
  allianceThreshold: number;
  highTensionThreshold: number;
  lowTensionThreshold: number;
  baseTensionDecayRate: number;
  questLockoutThreshold: number;
  hostilityThreshold: number;
  questCooldownPeriod: number;
  questCancellationPenalty: number;
  questCompletionTensionIncrease: number;
  tensionThreshold: number;
  diplomaticSettings: {
    meetingSuccessThreshold: number;
    resourceExchangeBonus: number;
    allianceFormationThreshold: number;
    peaceTreatyDuration: number;
    diplomaticCooldown: number;
    failedMeetingPenalty: number;
    successfulMeetingBonus: number;
    resourceExchangeThreshold: number;
  };
}

/**
 * Extended FactionQuestTemplate interface
 */
export interface CompetingFactionQuestTemplate extends BaseFactionQuestTemplate {
  location?: string | null;
  requiredResources?: QuestResource[];
  requiredConditions?: QuestCondition[];
}

/**
 * Represents a group of competing quests
 */
export interface CompetingQuestGroup {
  id: string;
  originalQuest: CompetingFactionQuestTemplate;
  competingQuests: CompetingFactionQuestTemplate[];
  activeQuests: CompetingFactionQuestTemplate[];
  completedQuests: CompletedQuest[];
  winningFaction: FactionType | null;
  tensionLevel: number;
  status: 'active' | 'completed' | 'failed' | 'expired';
  quests: Map<string, CompetingFactionQuestTemplate>;
  diplomaticState?: {
    meetingScheduled?: boolean;
    meetingLocation?: string;
    resourceExchangeProposed?: boolean;
    proposedResources?: {
      offered: QuestResource[];
      requested: QuestResource[];
    };
    agreementDraft?: {
      terms: string[];
      acceptedBy: FactionType[];
      status: 'DRAFTING' | 'PROPOSED' | 'ACCEPTED' | 'REJECTED';
    };
  };
}

/**
 * Metrics for tracking tension between factions
 */
export interface FactionTensionMetrics {
  currentTension: number;
  historicalPeak: number;
  lastConflictTime: number;
  lastUpdateTimestamp: number;
  involvedFactions: FactionType[];
  conflictHistory: ConflictHistoryEntry[];
  updates: TensionUpdate[];
}

/**
 * Represents a tension update event
 */
export interface TensionUpdate {
  timestamp: number;
  factionA: FactionType;
  factionB: FactionType;
  oldTension: number;
  newTension: number;
  tensionChange: number;
  type: 'QUEST_COMPLETION' | 'NATURAL_DECAY';
  reason: string;
  decayAmount?: number; // Optional field for natural decay updates
}

/**
 * Represents a conflict history entry
 */
export interface ConflictHistoryEntry {
  timestamp: number;
  type: 'QUEST_COMPLETION' | 'NATURAL_DECAY';
  tensionChange: number;
}

/**
 * Represents a conflict between factions
 */
export interface FactionConflict {
  questGroupId: string;
  timestamp: number;
  winningFaction: FactionType | null;
  worldStateChanges: WorldStateChange[];
  affectedFactions: FactionType[];
}

/**
 * State of conflict resolution
 */
export type ConflictResolutionState = FactionConflict;