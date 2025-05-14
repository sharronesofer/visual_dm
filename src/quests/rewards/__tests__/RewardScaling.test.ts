import { RewardScalingSystem, RewardScalingConfig, RewardContext } from '../RewardScaling';
import { QuestTemplate } from '../../types';

describe('RewardScalingSystem', () => {
  let config: RewardScalingConfig;
  let context: RewardContext;
  let system: RewardScalingSystem;

  beforeEach(() => {
    config = {
      baseMultiplier: 1.0,
      levelScaling: {
        factor: 0.1,
        cap: 2.0
      },
      difficultyScaling: {
        factor: 0.2,
        cap: 3.0
      },
      factionBonuses: {
        merchants: {
          type: 'multiply',
          value: 0.5,
          condition: (ctx) => ctx.factionStanding.merchants > 0
        },
        warriors: {
          type: 'add',
          value: 100,
          condition: (ctx) => ctx.factionStanding.warriors > 5
        }
      },
      rarityChances: {
        rare: 0.2,
        epic: 0.05,
        legendary: 0.01
      },
      uniqueRewardCooldown: 86400000, // 24 hours
      antiGrinding: {
        timeWindow: 3600000, // 1 hour
        rewardReduction: 0.1
      }
    };

    context = {
      playerLevel: 5,
      questDifficulty: 4,
      factionStanding: {
        merchants: 3,
        warriors: 2
      },
      playerHistory: {
        completedQuests: 20,
        questSuccessRate: 0.8,
        recentRewards: []
      },
      worldState: {
        economyMultiplier: 1.0,
        events: []
      }
    };

    system = new RewardScalingSystem(config);
  });

  describe('calculateRewards', () => {
    it('should scale gold rewards based on level and difficulty', () => {
      const baseRewards: QuestTemplate['rewards'] = {
        gold: 100,
        experience: 0,
        items: []
      };

      const scaled = system.calculateRewards(baseRewards, context);
      
      // Base: 100
      // Level factor: 1 + (5 * 0.1) = 1.5
      // Difficulty factor: 1 + (4 * 0.2) = 1.8
      // Base multiplier: 1.0 * (1 + 0.5 + 0.8) = 2.3
      // Merchant faction: 1 + (3 * 0.5) = 2.5
      // Expected: 100 * 2.3 * 2.5 = ~575
      expect(scaled.gold).toBeGreaterThan(500);
      expect(scaled.gold).toBeLessThan(600);
    });

    it('should scale experience rewards with level penalty', () => {
      const baseRewards: QuestTemplate['rewards'] = {
        gold: 0,
        experience: 1000,
        items: []
      };

      // Higher level player on lower difficulty quest
      const highLevelContext = {
        ...context,
        playerLevel: 10,
        questDifficulty: 2
      };

      const scaled = system.calculateRewards(baseRewards, highLevelContext);
      
      // Should apply level penalty due to quest being too easy
      expect(scaled.experience).toBeLessThan(1000);
    });

    it('should apply faction bonuses correctly', () => {
      const baseRewards: QuestTemplate['rewards'] = {
        gold: 100,
        experience: 100,
        items: []
      };

      // High warrior standing
      const warriorContext = {
        ...context,
        factionStanding: {
          merchants: 0,
          warriors: 6 // Above threshold for bonus
        }
      };

      const scaled = system.calculateRewards(baseRewards, warriorContext);
      
      // Should add flat 100 gold for warrior standing
      expect(scaled.gold).toBeGreaterThan(baseRewards.gold + 100);
    });

    it('should handle item rarity upgrades', () => {
      const baseRewards: QuestTemplate['rewards'] = {
        gold: 0,
        experience: 0,
        items: ['sword', 'shield', 'potion']
      };

      // Mock random to always upgrade
      const mockRandom = jest.spyOn(Math, 'random');
      mockRandom.mockReturnValue(0.1); // Will trigger 'rare' upgrade (0.2 threshold)

      const scaled = system.calculateRewards(baseRewards, context);
      
      expect(scaled.items.some(item => item.startsWith('rare_'))).toBe(true);
      
      mockRandom.mockRestore();
    });

    it('should apply anti-grinding measures', () => {
      const baseRewards: QuestTemplate['rewards'] = {
        gold: 100,
        experience: 100,
        items: []
      };

      // Context with many recent rewards
      const grindingContext = {
        ...context,
        playerHistory: {
          ...context.playerHistory,
          recentRewards: Array(10).fill({
            type: 'gold',
            amount: 100,
            timestamp: new Date()
          })
        }
      };

      const scaled = system.calculateRewards(baseRewards, grindingContext);
      
      // Should reduce rewards due to grinding detection
      expect(scaled.gold).toBeLessThan(baseRewards.gold);
      expect(scaled.experience).toBeLessThan(baseRewards.experience);
    });

    it('should handle unique reward cooldowns', () => {
      const baseRewards: QuestTemplate['rewards'] = {
        gold: 0,
        experience: 0,
        items: []
      };

      // Context with recent unique reward
      const recentUniqueContext = {
        ...context,
        playerHistory: {
          ...context.playerHistory,
          recentRewards: [{
            type: 'unique',
            amount: 1,
            timestamp: new Date()
          }]
        }
      };

      const scaled = system.calculateRewards(baseRewards, recentUniqueContext);
      
      // Mock implementation returns null for unique rewards
      expect(scaled.items.length).toBe(0);
    });
  });
}); 