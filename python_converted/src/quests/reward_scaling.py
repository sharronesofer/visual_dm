from typing import Any, List, Union


/**
 * Dynamic Reward Scaling System
 * Calculates quest rewards based on difficulty, player level, quest significance, and repetition.
 */
class RewardParams:
    baseXP: float
    baseGold: float
    difficulty: float
    playerLevel: float
    questSignificance: Union['main', 'side', 'faction', 'milestone']
    repetitionCount: float
class ScaledRewards:
    xp: float
    gold: float
    items: List[str]
    special?: List[str]
const SIGNIFICANCE_MULTIPLIER: Record<string, number> = {
  main: 2.0,
  side: 1.0,
  faction: 1.5,
  milestone: 3.0
}
const SPECIAL_REWARDS: Record<string, string[]> = {
  milestone: ['unique_ability', 'legendary_item'],
  main: ['rare_item'],
  faction: ['faction_banner'],
  side: []
}
function calculateXP({ baseXP, difficulty, playerLevel, questSignificance, repetitionCount }: RewardParams): float {
  const base = baseXP * difficulty * (1 + playerLevel / 10) * (SIGNIFICANCE_MULTIPLIER[questSignificance] || 1)
  return Math.round(applyDiminishingReturns(base, repetitionCount))
}
function calculateGold({ baseGold, difficulty, playerLevel, questSignificance, repetitionCount }: RewardParams): float {
  const base = baseGold * difficulty * (1 + playerLevel / 20) * (SIGNIFICANCE_MULTIPLIER[questSignificance] || 1)
  return Math.round(applyDiminishingReturns(base, repetitionCount))
}
function applyDiminishingReturns(value: float, repetitionCount: float): float {
  return value * (1 / (1 + repetitionCount * 0.2))
}
function getSpecialRewards(questSignificance: str): string[] {
  return SPECIAL_REWARDS[questSignificance] || []
}
function scaleRewards(params: RewardParams): \'ScaledRewards\' {
  return {
    xp: calculateXP(params),
    gold: calculateGold(params),
    items: [], 
    special: getSpecialRewards(params.questSignificance)
  }
} 