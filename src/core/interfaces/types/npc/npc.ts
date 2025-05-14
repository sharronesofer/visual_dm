import { Faction } from '../factions/faction';
import { Position } from '../world/position';
import { Memory, MemoryEventType } from './memory';

export interface NPCPosition {
  x: number;
  y: number;
}

export interface NPCGoal {
  id: string;
  type: string;
  priority: number;
  progress: number;
  deadline?: number;
  dependencies?: string[];
  conflicts?: string[];
  requirements?: {
    resources?: string[];
    relationships?: { [key: string]: number };
    skills?: string[];
  };
}

export interface NPCInteraction {
  timestamp: number;
  type: string;
  targetId: string;
  outcome: 'positive' | 'neutral' | 'negative';
}

export interface NPCStats {
  strength: number;
  dexterity: number;
  constitution: number;
  intelligence: number;
  wisdom: number;
  charisma: number;
  perception: number;
  leadership: number;
}

export interface NPCPersonality {
  aggressiveness: number;
  cautiousness: number;
  friendliness: number;
  ambition: number;
  loyalty: number;
  leadership: number;
  adaptability: number;
  curiosity: number;
  empathy: number;
  integrity: number;
  openness: number;
  trustworthiness: number;
  conformity: number;
  diplomacy: number;
  extraversion: number;
}

export interface NPCData {
  id: string;
  name: string;
  faction: Faction;
  position: Position;
  traits: string[];
  values: string[];
  goals: NPCGoal[];
  stats: NPCStats;
  personality: {
    traits: Map<string, number>;  // trait -> strength (0-1)
    compatibilityProfile: {
      preferredTraits: string[];
      avoidedTraits: string[];
      adaptability: number;  // 0-1
    };
    socialPreferences: {
      groupSize: {
        min: number;
        optimal: number;
        max: number;
      };
      leadershipStyle: 'dominant' | 'collaborative' | 'supportive';
      conflictResolution: 'aggressive' | 'diplomatic' | 'avoidant';
    };
  };
  skills: Map<string, number>;
  inventory: any[];
  relationships: Map<string, { score: number }>;
  memories: Memory[];
  location: string;
  groupAffiliations: {
    groupId: string;
    role: string;
    joinDate: number;
  }[];
  economicData?: {
    wealth: number;
    income: number;
    expenses: number;
    marketPreferences: {
      riskTolerance: number;
      priceThreshold: number;
      qualityPreference: number;
    };
  };
  socialStatus: {
    reputation: number;
    influence: number;
    trustworthiness: number;
    lastInteractionTime: number;
    recentInteractions: {
      npcId: string;
      type: string;
      time: number;
      outcome: string;
    }[];
  };
  learningProgress: Map<string, {
    skillId: string;
    currentLevel: number;
    experience: number;
    teachingAbility: number;
  }>;
  recentInteractions: {
    timestamp: number;
    type: string;
    targetId: string;
    outcome: 'positive' | 'neutral' | 'negative';
  }[];
  interactionHistory: {
    individual: Map<string, {
      positive: number;
      neutral: number;
      negative: number;
      lastInteraction: number;
      averageImpact: number;
    }>;
    group: Map<string, {
      role: string;
      contribution: number;
      conflicts: number;
      lastActive: number;
      satisfaction: number;
    }>;
  };
  groupFormationPreferences: {
    triggers: {
      emergency: number;  // 0-1 threshold
      resource: number;
      goal: number;
      social: number;
    };
    rolePreferences: string[];
    purposeWeights: Map<string, number>;
    minTrustThreshold: number;
  };
} 