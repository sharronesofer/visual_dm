export interface NPCGoal {
  id: string;
  type: GoalType;
  priority: number;
  description: string;
  status: GoalStatus;
  progress: number;
  deadline?: number;
  dependencies: string[];
  subgoals: string[];
  requirements: {
    resources?: {
      type: string;
      amount: number;
    }[];
    skills?: {
      skillId: string;
      minLevel: number;
    }[];
    relationships?: {
      npcId: string;
      minValue: number;
    }[];
    conditions?: {
      type: string;
      value: any;
    }[];
  };
  rewards?: {
    reputation?: number;
    resources?: {
      type: string;
      amount: number;
    }[];
    relationships?: {
      npcId: string;
      change: number;
    }[];
  };
  completion: {
    timeCompleted?: number;
    outcome?: string;
    achievementScore?: number;
  };
}

export enum GoalType {
  PERSONAL = 'personal',
  PROFESSIONAL = 'professional',
  SOCIAL = 'social',
  ECONOMIC = 'economic',
  FACTION = 'faction',
  QUEST = 'quest'
}

export enum GoalStatus {
  ACTIVE = 'active',
  COMPLETED = 'completed',
  FAILED = 'failed',
  ABANDONED = 'abandoned',
  BLOCKED = 'blocked',
  DEFERRED = 'deferred'
} 