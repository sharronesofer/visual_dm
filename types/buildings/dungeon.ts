import { BuildingBase, BuildingType, POICategory } from './base';

export interface DungeonStructure extends BuildingBase {
  category: POICategory.DUNGEON;
  difficulty: DifficultyRating;
  requiredLevel: number;
  rewards: RewardType[];
}

export interface EnemyLair extends DungeonStructure {
  type: BuildingType.ENEMY_LAIR;
  enemyTypes: string[];
  enemyCount: number;
  bossPresent: boolean;
}

export interface PuzzleRoom extends DungeonStructure {
  type: BuildingType.PUZZLE_ROOM;
  puzzleType: PuzzleType;
  solutionSteps: number;
  timeLimit?: number;
}

export interface TreasureChamber extends DungeonStructure {
  type: BuildingType.TREASURE_CHAMBER;
  treasureLevel: number;
  guardianType?: string;
  trapsCount: number;
}

export interface TrapRoom extends DungeonStructure {
  type: BuildingType.TRAP_ROOM;
  trapTypes: TrapType[];
  damageTypes: DamageType[];
  difficultyClass: number;
}

export enum DifficultyRating {
  EASY = 'EASY',
  MEDIUM = 'MEDIUM',
  HARD = 'HARD',
  DEADLY = 'DEADLY'
}

export enum PuzzleType {
  RIDDLE = 'RIDDLE',
  MECHANICAL = 'MECHANICAL',
  MAGICAL = 'MAGICAL',
  ENVIRONMENTAL = 'ENVIRONMENTAL',
  COMBINATION = 'COMBINATION'
}

export enum TrapType {
  PIT = 'PIT',
  ARROW = 'ARROW',
  POISON_GAS = 'POISON_GAS',
  MAGICAL = 'MAGICAL',
  CRUSHING = 'CRUSHING',
  FALLING = 'FALLING'
}

export enum DamageType {
  PHYSICAL = 'PHYSICAL',
  FIRE = 'FIRE',
  COLD = 'COLD',
  LIGHTNING = 'LIGHTNING',
  POISON = 'POISON',
  NECROTIC = 'NECROTIC'
}

export enum RewardType {
  GOLD = 'GOLD',
  ITEMS = 'ITEMS',
  EXPERIENCE = 'EXPERIENCE',
  RESOURCES = 'RESOURCES',
  REPUTATION = 'REPUTATION'
} 