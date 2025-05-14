import { FactionType } from '../../types/factions/faction';

export type WorldStateChangeType =
  | 'QUEST_COMPLETION'
  | 'QUEST_FAILURE'
  | 'QUEST_CANCELLED'
  | 'FACTION_TENSION_CHANGE'
  | 'TENSION_DECREASE'
  | 'DIPLOMATIC_OPPORTUNITY'
  | 'RESOURCE_CHANGE'
  | 'TERRITORY_CHANGE'
  | 'FACTION_ALLIANCE_BENEFIT'
  | 'FACTION_ALLIANCE_OPPORTUNITY'
  | 'DIPLOMATIC_MEETING'
  | 'DIPLOMATIC_AGREEMENT'
  | 'DIPLOMATIC_FAILURE'
  | 'RESOURCE_EXCHANGE';

export type WorldStateChangeEventType =
  | 'QUEST_COMPLETION'
  | 'QUEST_FAILURE'
  | 'QUEST_CANCELLATION'
  | 'TENSION_DECAY'
  | 'TENSION_STATE_CHANGE'
  | 'DIPLOMATIC_EVENT'
  | 'ALLIANCE_VICTORY_BENEFIT'
  | 'ALLIANCE_OPPORTUNITY'
  | 'DIPLOMATIC_MEETING'
  | 'DIPLOMATIC_AGREEMENT'
  | 'DIPLOMATIC_FAILURE'
  | 'RESOURCE_EXCHANGE';

export interface WorldStateChangeCustomData {
  type: WorldStateChangeEventType;
  questId?: string;
  groupId?: string;
  winningFaction?: FactionType;
  factions?: FactionType[];
  timestamp: number;
  oldState?: 'HIGH_TENSION' | 'LOW_TENSION' | 'NEUTRAL' | 'ALLIED';
  newState?: 'HIGH_TENSION' | 'LOW_TENSION' | 'NEUTRAL' | 'ALLIED';
  eventType?: 'OPPORTUNITY' | 'CONFLICT' | 'AGREEMENT' | 'MEETING';
  allyFaction?: FactionType;
  questGroupId?: string;
  tensionLevel?: number;
  diplomaticOutcome?: 'SUCCESS' | 'FAILURE' | 'PARTIAL';
  resourceExchange?: {
    offeredResources: { id: string; amount: number }[];
    requestedResources: { id: string; amount: number }[];
  };
  meetingDetails?: {
    location: string;
    participants: FactionType[];
    agenda: string[];
    outcome: string;
  };
}

export interface WorldStateChange {
  type: WorldStateChangeType;
  description: string;
  value: number;
  affectedFactions: FactionType[];
  location: string | null;
  customData?: WorldStateChangeCustomData;
}

export interface WorldState {
  factionInfluence: Record<FactionType, number>;
  factionTensions: Record<string, number>;
  resources: Map<string, number>;
  territories: Map<FactionType, string[]>;
  customStates: Record<string, any>;
  economyFactors: Record<string, number>;
}

/**
 * Types of player actions that can trigger consequences
 */
export type PlayerActionType =
  | 'QUEST_COMPLETION'
  | 'QUEST_FAILURE'
  | 'QUEST_BRANCH_CHOICE'
  | 'DIALOGUE_CHOICE'
  | 'RESOURCE_EXCHANGE'
  | 'FACTION_INTERACTION'
  | 'WORLD_EVENT';

/**
 * Represents a single player action with context for consequence tracking
 */
export interface PlayerAction {
  playerId: string;
  actionType: PlayerActionType;
  timestamp: number;
  questId?: string;
  factionId?: FactionType;
  targetFactionId?: FactionType;
  choiceId?: string;
  outcome?: string;
  details?: Record<string, any>;
}

/**
 * Tracks the history of player actions for consequence and world state tracking
 */
export interface PlayerActionHistory {
  playerId: string;
  actions: PlayerAction[];
} 