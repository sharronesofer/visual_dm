export enum QuestType {
  MAJOR = 'MAJOR',
  MINOR = 'MINOR',
  SIDE = 'SIDE',
  FACTION = 'FACTION',
  DYNAMIC = 'DYNAMIC'
}

export enum QuestStatus {
  PENDING = 'PENDING',
  IN_PROGRESS = 'IN_PROGRESS',
  COMPLETED = 'COMPLETED',
  FAILED = 'FAILED',
  CANCELLED = 'CANCELLED'
}

export interface QuestEvent {
  questId: string;
  type: QuestType;
  status: QuestStatus;
  playerId: string;
  involvedNpcIds: string[];
  outcome: QuestStatus;
  factionId?: string;
  tags?: string[];
  description: string;
} 