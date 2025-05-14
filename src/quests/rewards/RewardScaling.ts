import { QuestTemplate } from '../types';

/**
 * Represents a reward modifier configuration
 */
export interface RewardModifier {
  type: 'multiply' | 'add' | 'set';
  value: number;
  condition?: (context: RewardContext) => boolean;
}

/**
 * Context used for calculating rewards
 */
export interface RewardContext {
  playerLevel: number;
  questDifficulty: number;
  factionStanding: Record<string, number>;
  playerHistory: {
    completedQuests: number;
    questSuccessRate: number;
    recentRewards: Array<{
      type: string;
      amount: number;
      timestamp: Date;
    }>;
  };
  worldState: {
    economyMultiplier: number;
    events: string[];
  };
}

/**
 * Configuration for reward scaling
 */
export interface RewardScalingConfig {
  baseMultiplier: number;
  levelScaling: {
    factor: number;
    cap: number;
  };
  difficultyScaling: {
    factor: number;
    cap: number;
  };
  factionBonuses: Record<string, RewardModifier>;
  rarityChances: Record<string, number>;
  uniqueRewardCooldown: number; // in milliseconds
  antiGrinding: {
    timeWindow: number; // in milliseconds
    rewardReduction: number;
  };
}

/**
 * Manages the scaling and generation of quest rewards
 */
export class RewardScalingSystem {
  private config: RewardScalingConfig;
  private uniqueRewardsGranted: Set<string> = new Set();
  
  constructor(config: RewardScalingConfig) {
    this.config = config;
  }

  /**
   * Calculate scaled rewards for a quest based on context
   */
  calculateRewards(
    baseRewards: QuestTemplate['rewards'],
    context: RewardContext
  ): QuestTemplate['rewards'] {
    let scaledRewards = { ...baseRewards };
    
    // Apply base scaling
    const baseMultiplier = this.calculateBaseMultiplier(context);
    
    // Scale currency rewards
    if (scaledRewards.gold) {
      scaledRewards.gold = Math.floor(
        scaledRewards.gold * baseMultiplier * context.worldState.economyMultiplier
      );
    }

    // Scale experience rewards
    if (scaledRewards.experience) {
      scaledRewards.experience = Math.floor(
        scaledRewards.experience * this.calculateExperienceMultiplier(context)
      );
    }

    // Apply faction bonuses
    scaledRewards = this.applyFactionBonuses(scaledRewards, context);

    // Handle item rewards
    scaledRewards.items = this.processItemRewards(
      scaledRewards.items || [],
      context
    );

    // Apply anti-grinding measures
    scaledRewards = this.applyAntiGrinding(scaledRewards, context);

    return scaledRewards;
  }

  /**
   * Calculate the base multiplier for rewards
   */
  private calculateBaseMultiplier(context: RewardContext): number {
    const { levelScaling, difficultyScaling } = this.config;
    
    // Level-based scaling
    const levelFactor = Math.min(
      context.playerLevel * levelScaling.factor,
      levelScaling.cap
    );
    
    // Difficulty-based scaling
    const difficultyFactor = Math.min(
      context.questDifficulty * difficultyScaling.factor,
      difficultyScaling.cap
    );
    
    return this.config.baseMultiplier * (1 + levelFactor + difficultyFactor);
  }

  /**
   * Calculate experience multiplier based on context
   */
  private calculateExperienceMultiplier(context: RewardContext): number {
    const baseMultiplier = this.calculateBaseMultiplier(context);
    
    // Reduce XP gain for higher level players on easy quests
    const levelDiff = context.playerLevel - context.questDifficulty;
    const levelPenalty = Math.max(0, 1 - (levelDiff * 0.1));
    
    return baseMultiplier * levelPenalty;
  }

  /**
   * Apply faction-based reward bonuses
   */
  private applyFactionBonuses(
    rewards: QuestTemplate['rewards'],
    context: RewardContext
  ): QuestTemplate['rewards'] {
    const modified = { ...rewards };
    
    for (const [faction, standing] of Object.entries(context.factionStanding)) {
      const bonus = this.config.factionBonuses[faction];
      if (!bonus || !bonus.condition?.(context)) continue;
      
      switch (bonus.type) {
        case 'multiply':
          if (modified.gold) {
            modified.gold = Math.floor(modified.gold * (1 + standing * bonus.value));
          }
          if (modified.experience) {
            modified.experience = Math.floor(modified.experience * (1 + standing * bonus.value));
          }
          break;
        case 'add':
          if (modified.gold) {
            modified.gold += Math.floor(standing * bonus.value);
          }
          if (modified.experience) {
            modified.experience += Math.floor(standing * bonus.value);
          }
          break;
        case 'set':
          // Used for specific reward overrides
          if (standing >= bonus.value) {
            modified.items = [...(modified.items || []), `${faction}_special_reward`];
          }
          break;
      }
    }
    
    return modified;
  }

  /**
   * Process and potentially enhance item rewards
   */
  private processItemRewards(
    items: string[],
    context: RewardContext
  ): string[] {
    const processed = [...items];
    
    // Check for unique reward eligibility
    const canGrantUnique = this.checkUniqueRewardEligibility(context);
    
    // Roll for rarity upgrades
    processed.forEach((item, index) => {
      for (const [rarity, chance] of Object.entries(this.config.rarityChances)) {
        if (Math.random() < chance) {
          processed[index] = `${rarity}_${item}`;
          break;
        }
      }
    });
    
    // Add unique rewards if eligible
    if (canGrantUnique) {
      const uniqueReward = this.selectUniqueReward(context);
      if (uniqueReward) {
        processed.push(uniqueReward);
        this.uniqueRewardsGranted.add(uniqueReward);
      }
    }
    
    return processed;
  }

  /**
   * Check if the player is eligible for unique rewards
   */
  private checkUniqueRewardEligibility(context: RewardContext): boolean {
    const recentUnique = context.playerHistory.recentRewards.find(
      reward => reward.type === 'unique' &&
      Date.now() - reward.timestamp.getTime() < this.config.uniqueRewardCooldown
    );
    
    return !recentUnique && context.playerHistory.questSuccessRate >= 0.7;
  }

  /**
   * Select an appropriate unique reward based on context
   */
  private selectUniqueReward(context: RewardContext): string | null {
    // This would integrate with a larger unique item database
    // For now, return null to indicate no unique reward
    return null;
  }

  /**
   * Apply anti-grinding measures to prevent reward farming
   */
  private applyAntiGrinding(
    rewards: QuestTemplate['rewards'],
    context: RewardContext
  ): QuestTemplate['rewards'] {
    const { timeWindow, rewardReduction } = this.config.antiGrinding;
    
    // Count recent rewards
    const recentRewards = context.playerHistory.recentRewards.filter(
      reward => Date.now() - reward.timestamp.getTime() < timeWindow
    ).length;
    
    if (recentRewards > 5) { // Threshold for grinding detection
      const reduction = Math.min(0.9, rewardReduction * (recentRewards - 5));
      
      return {
        ...rewards,
        gold: rewards.gold ? Math.floor(rewards.gold * (1 - reduction)) : 0,
        experience: rewards.experience ? Math.floor(rewards.experience * (1 - reduction)) : 0
      };
    }
    
    return rewards;
  }
} 