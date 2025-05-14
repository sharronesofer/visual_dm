from typing import Any, Dict


describe('CompetingQuestManager', () => {
  let factionSystem: FactionQuestSystem
  let consequenceSystem: ConsequenceSystem
  let worldState: WorldStateHandler
  let manager: CompetingQuestManager
  let config: CompetingQuestConfig
  let mockQuest: FactionQuestTemplate
  beforeEach(() => {
    factionSystem = new FactionQuestSystem({
      reputationGainRate: 1,
      reputationLossRate: 0.5,
      tierThresholds: [0, 25, 50, 75],
      competingQuestProbability: 0.5,
      mutuallyExclusiveThreshold: 75,
      minimumStandingForSpecialQuests: 50,
      standingGainMultiplier: 1
    }, consequenceSystem)
    consequenceSystem = new ConsequenceSystem()
    worldState = new WorldStateHandler({
      resources: new Map(),
      territories: new Map(),
      influence: new Map(),
      custom: new Map(),
      customStates: new Map(),
      environmentalConditions: Dict[str, Any]
      },
      economyFactors: Dict[str, Any]
      },
      availableQuests: new Set(),
      activeEffects: []
    })
    config = {
      maxCompetingQuests: 3,
      tensionThreshold: 50,
      tensionDecayRate: 0.1,
      baseTensionDecayRate: 0.05,
      tensionDecayInterval: 60000, 
      highTensionThreshold: 75,
      maxDecayTimeThreshold: 3600000, 
      questLockoutThreshold: 90,
      questCancellationPenalty: -10,
      questCompletionTensionIncrease: 20
    }
    manager = new CompetingQuestManager(factionSystem, consequenceSystem, worldState, config)
    mockQuest = {
      id: 'test-quest',
      title: 'Test Quest',
      description: 'A test quest',
      type: 'FACTION',
      requirements: Dict[str, Any],
      rewards: Dict[str, Any],
      objectives: [
        {
          type: 'diplomacy',
          description: 'Control the market district',
          alternatives: []
        }
      ],
      dialogue: [],
      factionId: FactionType.MERCHANTS,
      factionRequirements: Dict[str, Any],
      factionRewards: Dict[str, Any],
      factionObjectives: [
        {
          type: 'diplomacy',
          description: 'Control the market district',
          factionImpact: Dict[str, Any]
        }
      ]
    }
  })
  describe('checkQuestAvailability', () => {
    it('should return true for non-competing quests', async () => {
      const available = await manager.checkQuestAvailability('non-existing-quest', FactionType.MERCHANTS)
      expect(available).toBe(true)
    })
    it('should return false when tension is too high', async () => {
      const mockFactionProfile: FactionProfile = {
        id: FactionType.THIEVES,
        name: 'Thieves Guild',
        description: 'A guild of thieves',
        values: Dict[str, Any],
        specialResources: [],
        questPreferences: Dict[str, Any],
        questModifiers: Dict[str, Any],
          difficultyModifiers: {},
          objectivePreferences: {}
        },
        relationships: new Map(),
        tier: 0,
        reputation: 0
      }
      const group = await manager.createCompetingQuestGroup(mockQuest, [mockFactionProfile])
      const metrics = manager.getTensionMetrics(FactionType.MERCHANTS, FactionType.THIEVES)
      if (metrics) {
        metrics.currentTension = config.questLockoutThreshold + 10
      }
      const available = await manager.checkQuestAvailability(mockQuest.id, FactionType.MERCHANTS)
      expect(available).toBe(false)
    })
  })
  describe('cancelCompetingQuests', () => {
    it('should cancel competing quests when one is completed', async () => {
      const mockFactionProfile: FactionProfile = {
        id: FactionType.THIEVES,
        name: 'Thieves Guild',
        description: 'A guild of thieves',
        values: Dict[str, Any],
        specialResources: [],
        questPreferences: Dict[str, Any],
        questModifiers: Dict[str, Any],
          difficultyModifiers: {},
          objectivePreferences: {}
        },
        relationships: new Map(),
        tier: 0,
        reputation: 0
      }
      const group = await manager.createCompetingQuestGroup(mockQuest, [mockFactionProfile])
      const competingQuest = {
        ...mockQuest,
        id: 'competing-quest',
        factionId: FactionType.THIEVES
      }
      const questMap = new Map()
      questMap.set(mockQuest.id, {
        id: mockQuest.id,
        status: 'active',
        assignedFaction: FactionType.MERCHANTS,
        location: 'market'
      })
      questMap.set(competingQuest.id, {
        id: competingQuest.id,
        status: 'active',
        assignedFaction: FactionType.THIEVES,
        location: 'market'
      })
      group.quests = questMap
      await manager.cancelCompetingQuests(mockQuest.id, FactionType.MERCHANTS)
      const competingQuestInfo = group.quests.get(competingQuest.id)
      expect(competingQuestInfo?.status).toBe('cancelled')
      expect(competingQuestInfo?.completionTime).toBeDefined()
    })
  })
  describe('tension decay', () => {
    it('should decay tension over time', async () => {
      const mockFactionProfile: FactionProfile = {
        id: FactionType.THIEVES,
        name: 'Thieves Guild',
        description: 'A guild of thieves',
        values: Dict[str, Any],
        specialResources: [],
        questPreferences: Dict[str, Any],
        questModifiers: Dict[str, Any],
          difficultyModifiers: {},
          objectivePreferences: {}
        },
        relationships: new Map(),
        tier: 0,
        reputation: 0
      }
      const group = await manager.createCompetingQuestGroup(mockQuest, [mockFactionProfile])
      const metrics = manager.getTensionMetrics(FactionType.MERCHANTS, FactionType.THIEVES)
      if (metrics) {
        metrics.currentTension = 80
        metrics.lastConflictTime = Date.now() - config.maxDecayTimeThreshold
      }
      await new Promise(resolve => setTimeout(resolve, config.tensionDecayInterval + 100))
      if (metrics) {
        expect(metrics.currentTension).toBeLessThan(80)
      }
    })
  })
}) 