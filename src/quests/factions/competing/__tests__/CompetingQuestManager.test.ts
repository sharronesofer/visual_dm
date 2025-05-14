import { CompetingQuestManager } from '../CompetingQuestManager';
import { FactionQuestSystem } from '../../FactionQuestSystem';
import { ConsequenceSystem } from '../../../consequences/ConsequenceSystem';
import { WorldStateHandler } from '../../../consequences/WorldStateHandler';
import { FactionType, FactionProfile } from '../../../../types/factions/faction';
import { FactionQuestTemplate } from '../../types';
import { CompetingQuestConfig } from '../types';
import { QuestObjective } from '../../../types';

describe('CompetingQuestManager', () => {
  let factionSystem: FactionQuestSystem;
  let consequenceSystem: ConsequenceSystem;
  let worldState: WorldStateHandler;
  let manager: CompetingQuestManager;
  let config: CompetingQuestConfig;
  let mockQuest: FactionQuestTemplate;

  beforeEach(() => {
    factionSystem = new FactionQuestSystem({
      reputationGainRate: 1,
      reputationLossRate: 0.5,
      tierThresholds: [0, 25, 50, 75],
      competingQuestProbability: 0.5,
      mutuallyExclusiveThreshold: 75,
      minimumStandingForSpecialQuests: 50,
      standingGainMultiplier: 1
    }, consequenceSystem);
    
    consequenceSystem = new ConsequenceSystem();
    
    worldState = new WorldStateHandler({
      resources: new Map(),
      territories: new Map(),
      influence: new Map(),
      custom: new Map(),
      customStates: new Map(),
      environmentalConditions: {
        environment: {
          weather: 'clear',
          visibility: 'good'
        }
      },
      economyFactors: {
        inflation: 1.0,
        resourceScarcity: {}
      },
      availableQuests: new Set(),
      activeEffects: []
    });

    config = {
      maxCompetingQuests: 3,
      tensionThreshold: 50,
      tensionDecayRate: 0.1,
      baseTensionDecayRate: 0.05,
      tensionDecayInterval: 60000, // 1 minute
      highTensionThreshold: 75,
      maxDecayTimeThreshold: 3600000, // 1 hour
      questLockoutThreshold: 90,
      questCancellationPenalty: -10,
      questCompletionTensionIncrease: 20
    };

    manager = new CompetingQuestManager(factionSystem, consequenceSystem, worldState, config);

    // Create a mock quest for testing
    mockQuest = {
      id: 'test-quest',
      title: 'Test Quest',
      description: 'A test quest',
      type: 'FACTION',
      requirements: {
        minimumLevel: 1,
        minimumReputation: 0
      },
      rewards: {
        gold: 100,
        experience: 500,
        items: []
      },
      objectives: [
        {
          type: 'diplomacy',
          description: 'Control the market district',
          alternatives: []
        }
      ],
      dialogue: [],
      factionId: FactionType.MERCHANTS,
      factionRequirements: {
        minimumStanding: 0,
        maximumStanding: 100
      },
      factionRewards: {
        standingGain: 10,
        specialRewards: []
      },
      factionObjectives: [
        {
          type: 'diplomacy',
          description: 'Control the market district',
          factionImpact: {
            primary: 10,
            allied: 5,
            opposing: -5
          }
        }
      ]
    };
  });

  describe('checkQuestAvailability', () => {
    it('should return true for non-competing quests', async () => {
      const available = await manager.checkQuestAvailability('non-existing-quest', FactionType.MERCHANTS);
      expect(available).toBe(true);
    });

    it('should return false when tension is too high', async () => {
      const mockFactionProfile: FactionProfile = {
        id: FactionType.THIEVES,
        name: 'Thieves Guild',
        description: 'A guild of thieves',
        values: {
          wealth: 80,
          power: 70,
          knowledge: 40,
          tradition: 30,
          progress: 50,
          honor: 20
        },
        specialResources: [],
        questPreferences: {
          combat: 0.3,
          diplomacy: 0.2,
          stealth: 0.8,
          trade: 0.6,
          exploration: 0.4
        },
        questModifiers: {
          rewardMultipliers: {},
          difficultyModifiers: {},
          objectivePreferences: {}
        },
        relationships: new Map(),
        tier: 0,
        reputation: 0
      };

      const group = await manager.createCompetingQuestGroup(mockQuest, [mockFactionProfile]);

      // Set high tension
      const metrics = manager.getTensionMetrics(FactionType.MERCHANTS, FactionType.THIEVES);
      if (metrics) {
        metrics.currentTension = config.questLockoutThreshold + 10;
      }

      const available = await manager.checkQuestAvailability(mockQuest.id, FactionType.MERCHANTS);
      expect(available).toBe(false);
    });
  });

  describe('cancelCompetingQuests', () => {
    it('should cancel competing quests when one is completed', async () => {
      const mockFactionProfile: FactionProfile = {
        id: FactionType.THIEVES,
        name: 'Thieves Guild',
        description: 'A guild of thieves',
        values: {
          wealth: 80,
          power: 70,
          knowledge: 40,
          tradition: 30,
          progress: 50,
          honor: 20
        },
        specialResources: [],
        questPreferences: {
          combat: 0.3,
          diplomacy: 0.2,
          stealth: 0.8,
          trade: 0.6,
          exploration: 0.4
        },
        questModifiers: {
          rewardMultipliers: {},
          difficultyModifiers: {},
          objectivePreferences: {}
        },
        relationships: new Map(),
        tier: 0,
        reputation: 0
      };

      const group = await manager.createCompetingQuestGroup(mockQuest, [mockFactionProfile]);

      // Add competing quest
      const competingQuest = {
        ...mockQuest,
        id: 'competing-quest',
        factionId: FactionType.THIEVES
      };

      const questMap = new Map();
      questMap.set(mockQuest.id, {
        id: mockQuest.id,
        status: 'active',
        assignedFaction: FactionType.MERCHANTS,
        location: 'market'
      });
      questMap.set(competingQuest.id, {
        id: competingQuest.id,
        status: 'active',
        assignedFaction: FactionType.THIEVES,
        location: 'market'
      });

      group.quests = questMap;

      // Cancel competing quests
      await manager.cancelCompetingQuests(mockQuest.id, FactionType.MERCHANTS);

      // Check that competing quest was cancelled
      const competingQuestInfo = group.quests.get(competingQuest.id);
      expect(competingQuestInfo?.status).toBe('cancelled');
      expect(competingQuestInfo?.completionTime).toBeDefined();
    });
  });

  describe('tension decay', () => {
    it('should decay tension over time', async () => {
      const mockFactionProfile: FactionProfile = {
        id: FactionType.THIEVES,
        name: 'Thieves Guild',
        description: 'A guild of thieves',
        values: {
          wealth: 80,
          power: 70,
          knowledge: 40,
          tradition: 30,
          progress: 50,
          honor: 20
        },
        specialResources: [],
        questPreferences: {
          combat: 0.3,
          diplomacy: 0.2,
          stealth: 0.8,
          trade: 0.6,
          exploration: 0.4
        },
        questModifiers: {
          rewardMultipliers: {},
          difficultyModifiers: {},
          objectivePreferences: {}
        },
        relationships: new Map(),
        tier: 0,
        reputation: 0
      };

      const group = await manager.createCompetingQuestGroup(mockQuest, [mockFactionProfile]);

      // Set initial tension
      const metrics = manager.getTensionMetrics(FactionType.MERCHANTS, FactionType.THIEVES);
      if (metrics) {
        metrics.currentTension = 80;
        metrics.lastConflictTime = Date.now() - config.maxDecayTimeThreshold;
      }

      // Trigger tension decay
      await new Promise(resolve => setTimeout(resolve, config.tensionDecayInterval + 100));

      // Check that tension has decayed
      if (metrics) {
        expect(metrics.currentTension).toBeLessThan(80);
      }
    });
  });
}); 