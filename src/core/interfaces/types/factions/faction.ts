export enum FactionType {
  MERCHANTS = 'MERCHANTS',
  WARRIORS = 'WARRIORS',
  SCHOLARS = 'SCHOLARS',
  NOBLES = 'NOBLES',
  OUTLAWS = 'OUTLAWS',
  RELIGIOUS = 'RELIGIOUS',
  NEUTRAL = 'NEUTRAL'
}

export interface FactionRelationship {
  faction: FactionType;
  attitude: number; // -100 to 100
  lastInteraction: number;
}

export interface Faction {
  type: FactionType;
  name: string;
  description: string;
  influence: number; // 0 to 100
  territory: string[];
  relationships: Map<FactionType, FactionRelationship>;
  resources: Map<string, number>;
  goals: string[];
  activeMembers: Set<string>;
}

export interface FactionProfile {
  id: FactionType;
  name: string;
  description: string;
  values: {
    wealth: number;
    power: number;
    knowledge: number;
    tradition: number;
    progress: number;
    honor: number;
  };
  specialResources: string[];
  questPreferences: Record<QuestType, number>;
  questModifiers: {
    rewardMultipliers: Record<string, number>;
    difficultyModifiers: Record<string, number>;
    objectivePreferences: Record<string, number>;
  };
  relationships: Map<FactionType, number>;
  tier: number;
  reputation: number;
}

export interface FactionStanding {
  reputation: number;
  tier: number;
  completedQuests: number;
  failedQuests: number;
  specialActions: Array<{
    type: string;
    impact: number;
    timestamp: number;
  }>;
}

export type QuestType = 'combat' | 'diplomacy' | 'stealth' | 'trade' | 'exploration'; 