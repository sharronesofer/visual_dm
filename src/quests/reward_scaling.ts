/**
 * Dynamic Reward Scaling System
 * Calculates quest rewards based on difficulty, player level, quest significance, and repetition.
 */

export interface RewardParams {
  baseXP: number;
  baseGold: number;
  difficulty: number;
  playerLevel: number;
  questSignificance: 'main' | 'side' | 'faction' | 'milestone';
  repetitionCount: number;
}

export interface ScaledRewards {
  xp: number;
  gold: number;
  items: string[];
  special?: string[];
}

const SIGNIFICANCE_MULTIPLIER: Record<string, number> = {
  main: 2.0,
  side: 1.0,
  faction: 1.5,
  milestone: 3.0
};

const SPECIAL_REWARDS: Record<string, string[]> = {
  milestone: ['unique_ability', 'legendary_item'],
  main: ['rare_item'],
  faction: ['faction_banner'],
  side: []
};

export function calculateXP({ baseXP, difficulty, playerLevel, questSignificance, repetitionCount }: RewardParams): number {
  const base = baseXP * difficulty * (1 + playerLevel / 10) * (SIGNIFICANCE_MULTIPLIER[questSignificance] || 1);
  return Math.round(applyDiminishingReturns(base, repetitionCount));
}

export function calculateGold({ baseGold, difficulty, playerLevel, questSignificance, repetitionCount }: RewardParams): number {
  const base = baseGold * difficulty * (1 + playerLevel / 20) * (SIGNIFICANCE_MULTIPLIER[questSignificance] || 1);
  return Math.round(applyDiminishingReturns(base, repetitionCount));
}

export function applyDiminishingReturns(value: number, repetitionCount: number): number {
  return value * (1 / (1 + repetitionCount * 0.2));
}

export function getSpecialRewards(questSignificance: string): string[] {
  return SPECIAL_REWARDS[questSignificance] || [];
}

export function scaleRewards(params: RewardParams): ScaledRewards {
  return {
    xp: calculateXP(params),
    gold: calculateGold(params),
    items: [], // Item logic can be extended
    special: getSpecialRewards(params.questSignificance)
  };
} 