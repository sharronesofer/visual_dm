from typing import Any, Dict, List, Union


/**
 * Represents a reward modifier configuration
 */
class RewardModifier:
    type: Union['multiply', 'add', 'set']
    value: float
    condition?: (context: RewardContext) => bool
/**
 * Context used for calculating rewards
 */
class RewardContext:
    playerLevel: float
    questDifficulty: float
    factionStanding: Dict[str, float>
    playerHistory: Dict[str, Any]
  worldState: Dict[str, Any]
}
/**
 * Configuration for reward scaling
 */
class RewardScalingConfig:
    baseMultiplier: float
    levelScaling: Dict[str, Any]
  factionBonuses: Record<string, RewardModifier>
  rarityChances: Record<string, number>
  uniqueRewardCooldown: float 
  antiGrinding: Dict[str, Any]
}
/**
 * Manages the scaling and generation of quest rewards
 */
class RewardScalingSystem {
  private config: \'RewardScalingConfig\'
  private uniqueRewardsGranted: Set<string> = new Set()
  constructor(config: RewardScalingConfig) {
    this.config = config
  }
  /**
   * Calculate scaled rewards for a quest based on context
   */
  calculateRewards(
    baseRewards: QuestTemplate['rewards'],
    context: \'RewardContext\'
  ): QuestTemplate['rewards'] {
    let scaledRewards = { ...baseRewards }
    const baseMultiplier = this.calculateBaseMultiplier(context)
    if (scaledRewards.gold) {
      scaledRewards.gold = Math.floor(
        scaledRewards.gold * baseMultiplier * context.worldState.economyMultiplier
      )
    }
    if (scaledRewards.experience) {
      scaledRewards.experience = Math.floor(
        scaledRewards.experience * this.calculateExperienceMultiplier(context)
      )
    }
    scaledRewards = this.applyFactionBonuses(scaledRewards, context)
    scaledRewards.items = this.processItemRewards(
      scaledRewards.items || [],
      context
    )
    scaledRewards = this.applyAntiGrinding(scaledRewards, context)
    return scaledRewards
  }
  /**
   * Calculate the base multiplier for rewards
   */
  private calculateBaseMultiplier(context: RewardContext): float {
    const { levelScaling, difficultyScaling } = this.config
    const levelFactor = Math.min(
      context.playerLevel * levelScaling.factor,
      levelScaling.cap
    )
    const difficultyFactor = Math.min(
      context.questDifficulty * difficultyScaling.factor,
      difficultyScaling.cap
    )
    return this.config.baseMultiplier * (1 + levelFactor + difficultyFactor)
  }
  /**
   * Calculate experience multiplier based on context
   */
  private calculateExperienceMultiplier(context: RewardContext): float {
    const baseMultiplier = this.calculateBaseMultiplier(context)
    const levelDiff = context.playerLevel - context.questDifficulty
    const levelPenalty = Math.max(0, 1 - (levelDiff * 0.1))
    return baseMultiplier * levelPenalty
  }
  /**
   * Apply faction-based reward bonuses
   */
  private applyFactionBonuses(
    rewards: QuestTemplate['rewards'],
    context: \'RewardContext\'
  ): QuestTemplate['rewards'] {
    const modified = { ...rewards }
    for (const [faction, standing] of Object.entries(context.factionStanding)) {
      const bonus = this.config.factionBonuses[faction]
      if (!bonus || !bonus.condition?.(context)) continue
      switch (bonus.type) {
        case 'multiply':
          if (modified.gold) {
            modified.gold = Math.floor(modified.gold * (1 + standing * bonus.value))
          }
          if (modified.experience) {
            modified.experience = Math.floor(modified.experience * (1 + standing * bonus.value))
          }
          break
        case 'add':
          if (modified.gold) {
            modified.gold += Math.floor(standing * bonus.value)
          }
          if (modified.experience) {
            modified.experience += Math.floor(standing * bonus.value)
          }
          break
        case 'set':
          if (standing >= bonus.value) {
            modified.items = [...(modified.items || []), `${faction}_special_reward`]
          }
          break
      }
    }
    return modified
  }
  /**
   * Process and potentially enhance item rewards
   */
  private processItemRewards(
    items: List[string],
    context: \'RewardContext\'
  ): string[] {
    const processed = [...items]
    const canGrantUnique = this.checkUniqueRewardEligibility(context)
    processed.forEach((item, index) => {
      for (const [rarity, chance] of Object.entries(this.config.rarityChances)) {
        if (Math.random() < chance) {
          processed[index] = `${rarity}_${item}`
          break
        }
      }
    })
    if (canGrantUnique) {
      const uniqueReward = this.selectUniqueReward(context)
      if (uniqueReward) {
        processed.push(uniqueReward)
        this.uniqueRewardsGranted.add(uniqueReward)
      }
    }
    return processed
  }
  /**
   * Check if the player is eligible for unique rewards
   */
  private checkUniqueRewardEligibility(context: RewardContext): bool {
    const recentUnique = context.playerHistory.recentRewards.find(
      reward => reward.type === 'unique' &&
      Date.now() - reward.timestamp.getTime() < this.config.uniqueRewardCooldown
    )
    return !recentUnique && context.playerHistory.questSuccessRate >= 0.7
  }
  /**
   * Select an appropriate unique reward based on context
   */
  private selectUniqueReward(context: RewardContext): str | null {
    return null
  }
  /**
   * Apply anti-grinding measures to prevent reward farming
   */
  private applyAntiGrinding(
    rewards: QuestTemplate['rewards'],
    context: \'RewardContext\'
  ): QuestTemplate['rewards'] {
    const { timeWindow, rewardReduction } = this.config.antiGrinding
    const recentRewards = context.playerHistory.recentRewards.filter(
      reward => Date.now() - reward.timestamp.getTime() < timeWindow
    ).length
    if (recentRewards > 5) { 
      const reduction = Math.min(0.9, rewardReduction * (recentRewards - 5))
      return {
        ...rewards,
        gold: rewards.gold ? Math.floor(rewards.gold * (1 - reduction)) : 0,
        experience: rewards.experience ? Math.floor(rewards.experience * (1 - reduction)) : 0
      }
    }
    return rewards
  }
} 