export enum RelationshipType {
  STRANGER = 'stranger',
  ACQUAINTANCE = 'acquaintance',
  FRIEND = 'friend',
  CLOSE_FRIEND = 'close_friend',
  RIVAL = 'rival',
  ENEMY = 'enemy',
}

export interface NPCAffinity {
  npcId1: string;
  npcId2: string;
  score: number;
  lastInteraction: Date;
  interactionCount: number;
  relationship: RelationshipType;
} 