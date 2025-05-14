// Monster siege and attack types

export type MonsterAttackDirection =
  | 'north'
  | 'northeast'
  | 'southeast'
  | 'south'
  | 'southwest'
  | 'northwest';

export type MonsterAttackOutcome =
  | 'defended'
  | 'close_defeat'
  | 'decisive_defeat';

export interface MonsterAttack {
  id: string;
  poiId: string;
  direction: MonsterAttackDirection;
  strength: number;
  monsterTypes: string[];
  timestamp: Date;
  resolved: boolean;
  outcome?: MonsterAttackOutcome;
} 