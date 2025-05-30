from typing import Any, Dict



describe('FactionQuestGenerator', () => {
  let generator: FactionQuestGenerator
  let factionSystem: FactionQuestSystem
  let consequenceSystem: ConsequenceSystem
  let mockFaction: FactionProfile
  let baseTemplate: QuestTemplate
  beforeEach(() => {
    consequenceSystem = new ConsequenceSystem()
    factionSystem = new FactionQuestSystem({
      reputationGainRate: 1,
      reputationLossRate: 1,
      tierThresholds: [100, 200, 300],
      competingQuestProbability: 0.3,
      mutuallyExclusiveThreshold: 50,
      minimumStandingForSpecialQuests: 30
    }, consequenceSystem)
    mockFaction = {
      id: FactionType.MERCHANTS,
      name: 'Test Merchants',
      description: 'A test merchant faction',
      values: Dict[str, Any],
      specialResources: ['rare_goods', 'trade_routes'],
      questPreferences: Dict[str, Any],
      questModifiers: Dict[str, Any],
        difficultyModifiers: Dict[str, Any],
        objectivePreferences: Dict[str, Any]
      },
      relationships: new Map([
        [FactionType.WARRIORS, -40],
        [FactionType.SCHOLARS, 30]
      ]),
      tier: 2,
      reputation: 75
    }
    baseTemplate = {
      id: 'test_quest',
      title: 'Test Quest',
      description: 'A test quest',
      type: 'trade',
      difficulty: 3,
      requirements: Dict[str, Any],
      rewards: Dict[str, Any],
      objectives: [
        {
          type: 'collect',
          description: 'Collect test items',
          difficulty: 2,
          alternatives: [
            {
              type: 'trade',
              description: 'Trade for items instead',
              difficulty: 1
            }
          ]
        }
      ],
      dialogue: [
        {
          npcId: 'test_npc',
          text: 'Base dialogue text',
          variations: []
        }
      ]
    }
    generator = new FactionQuestGenerator(factionSystem, consequenceSystem)
    generator.registerBaseTemplate(baseTemplate)
  })
  describe('generateFactionQuest', () => {
    it('should generate a faction quest with correct basic properties', () => {
      const factionQuest = generator.generateFactionQuest(baseTemplate, mockFaction)
      expect(factionQuest.factionId).toBe(FactionType.MERCHANTS)
      expect(factionQuest.title).toBe(baseTemplate.title)
      expect(factionQuest.description).toBe(baseTemplate.description)
    })
    it('should apply faction-specific requirements', () => {
      const factionQuest = generator.generateFactionQuest(baseTemplate, mockFaction)
      expect(factionQuest.factionRequirements).toBeDefined()
      expect(factionQuest.factionRequirements.minimumStanding).toBeDefined()
      expect(factionQuest.factionRequirements.requiredTier).toBe(1) 
    })
    it('should generate appropriate faction rewards', () => {
      const factionQuest = generator.generateFactionQuest(baseTemplate, mockFaction)
      expect(factionQuest.factionRewards).toBeDefined()
      expect(factionQuest.factionRewards.standingGain).toBe(30) 
    })
    it('should convert objectives to faction objectives', () => {
      const factionQuest = generator.generateFactionQuest(baseTemplate, mockFaction)
      expect(factionQuest.factionObjectives).toHaveLength(baseTemplate.objectives.length)
      expect(factionQuest.factionObjectives[0].type).toBe('trade') 
      expect(factionQuest.factionObjectives[0].factionImpact).toBeDefined()
    })
    it('should generate competing factions when appropriate', () => {
      generator = new FactionQuestGenerator(factionSystem, consequenceSystem, {
        competingQuestProbability: 1
      })
      const factionQuest = generator.generateFactionQuest(baseTemplate, mockFaction)
      expect(factionQuest.competingFactions).toBeDefined()
      if (factionQuest.competingFactions) {
        expect(factionQuest.competingFactions[0].factionId).toBe(FactionType.WARRIORS)
        expect(factionQuest.competingFactions[0].standingImpact).toBe(-20)
      }
    })
    it('should apply faction-specific modifiers to quest properties', () => {
      const factionQuest = generator.generateFactionQuest(baseTemplate, mockFaction)
      expect(factionQuest.difficulty).toBe(baseTemplate.difficulty * 0.8) 
      expect(factionQuest.rewards.gold).toBe(baseTemplate.rewards.gold * 1.2) 
    })
    it('should generate appropriate dialogue variations', () => {
      const factionQuest = generator.generateFactionQuest(baseTemplate, mockFaction)
      expect(factionQuest.dialogue[0].variations).toHaveLength(3) 
      expect(factionQuest.dialogue[0].variations![0].standingThreshold).toBe(0)
      expect(factionQuest.dialogue[0].variations![1].standingThreshold).toBe(30)
      expect(factionQuest.dialogue[0].variations![2].standingThreshold).toBe(70)
    })
  })
  describe('registerBaseTemplate', () => {
    it('should register a base template correctly', () => {
      const newTemplate: QuestTemplate = {
        ...baseTemplate,
        id: 'new_template'
      }
      generator.registerBaseTemplate(newTemplate)
      const templates = generator.getBaseTemplates()
      expect(templates).toContainEqual(newTemplate)
    })
  })
}) 