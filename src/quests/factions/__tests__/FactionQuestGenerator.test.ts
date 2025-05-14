import { FactionQuestGenerator } from '../FactionQuestGenerator';
import { FactionQuestSystem } from '../FactionQuestSystem';
import { ConsequenceSystem } from '../../consequences/ConsequenceSystem';
import { FactionType, FactionProfile } from '../../../types/factions/faction';
import { QuestTemplate } from '../../types';

describe('FactionQuestGenerator', () => {
  let generator: FactionQuestGenerator;
  let factionSystem: FactionQuestSystem;
  let consequenceSystem: ConsequenceSystem;
  let mockFaction: FactionProfile;
  let baseTemplate: QuestTemplate;

  beforeEach(() => {
    // Initialize mock systems
    consequenceSystem = new ConsequenceSystem();
    factionSystem = new FactionQuestSystem({
      reputationGainRate: 1,
      reputationLossRate: 1,
      tierThresholds: [100, 200, 300],
      competingQuestProbability: 0.3,
      mutuallyExclusiveThreshold: 50,
      minimumStandingForSpecialQuests: 30
    }, consequenceSystem);

    // Create mock faction
    mockFaction = {
      id: FactionType.MERCHANTS,
      name: 'Test Merchants',
      description: 'A test merchant faction',
      values: {
        wealth: 0.8,
        power: 0.4,
        knowledge: 0.6,
        tradition: 0.3,
        progress: 0.7,
        honor: 0.5
      },
      specialResources: ['rare_goods', 'trade_routes'],
      questPreferences: {
        combat: 0.2,
        diplomacy: 0.8,
        stealth: 0.3,
        trade: 0.9,
        exploration: 0.5
      },
      questModifiers: {
        rewardMultipliers: { gold: 1.2 },
        difficultyModifiers: { trade: 0.8 },
        objectivePreferences: { trade: 1.2 }
      },
      relationships: new Map([
        [FactionType.WARRIORS, -40],
        [FactionType.SCHOLARS, 30]
      ]),
      tier: 2,
      reputation: 75
    };

    // Create base quest template
    baseTemplate = {
      id: 'test_quest',
      title: 'Test Quest',
      description: 'A test quest',
      type: 'trade',
      difficulty: 3,
      requirements: {
        minimumLevel: 5,
        minimumReputation: 20,
        items: ['test_item'],
        abilities: ['test_ability']
      },
      rewards: {
        gold: 100,
        experience: 500,
        items: ['reward_item'],
        reputation: 10
      },
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
    };

    // Initialize generator
    generator = new FactionQuestGenerator(factionSystem, consequenceSystem);
    generator.registerBaseTemplate(baseTemplate);
  });

  describe('generateFactionQuest', () => {
    it('should generate a faction quest with correct basic properties', () => {
      const factionQuest = generator.generateFactionQuest(baseTemplate, mockFaction);

      expect(factionQuest.factionId).toBe(FactionType.MERCHANTS);
      expect(factionQuest.title).toBe(baseTemplate.title);
      expect(factionQuest.description).toBe(baseTemplate.description);
    });

    it('should apply faction-specific requirements', () => {
      const factionQuest = generator.generateFactionQuest(baseTemplate, mockFaction);

      expect(factionQuest.factionRequirements).toBeDefined();
      expect(factionQuest.factionRequirements.minimumStanding).toBeDefined();
      expect(factionQuest.factionRequirements.requiredTier).toBe(1); // tier - 1
    });

    it('should generate appropriate faction rewards', () => {
      const factionQuest = generator.generateFactionQuest(baseTemplate, mockFaction);

      expect(factionQuest.factionRewards).toBeDefined();
      expect(factionQuest.factionRewards.standingGain).toBe(30); // difficulty * 10
    });

    it('should convert objectives to faction objectives', () => {
      const factionQuest = generator.generateFactionQuest(baseTemplate, mockFaction);

      expect(factionQuest.factionObjectives).toHaveLength(baseTemplate.objectives.length);
      expect(factionQuest.factionObjectives[0].type).toBe('trade'); // mapped from 'collect'
      expect(factionQuest.factionObjectives[0].factionImpact).toBeDefined();
    });

    it('should generate competing factions when appropriate', () => {
      // Force competing quest generation by setting probability to 1
      generator = new FactionQuestGenerator(factionSystem, consequenceSystem, {
        competingQuestProbability: 1
      });

      const factionQuest = generator.generateFactionQuest(baseTemplate, mockFaction);

      expect(factionQuest.competingFactions).toBeDefined();
      if (factionQuest.competingFactions) {
        expect(factionQuest.competingFactions[0].factionId).toBe(FactionType.WARRIORS);
        expect(factionQuest.competingFactions[0].standingImpact).toBe(-20);
      }
    });

    it('should apply faction-specific modifiers to quest properties', () => {
      const factionQuest = generator.generateFactionQuest(baseTemplate, mockFaction);

      // Check if merchant-specific modifiers were applied
      expect(factionQuest.difficulty).toBe(baseTemplate.difficulty * 0.8); // merchant difficulty multiplier
      expect(factionQuest.rewards.gold).toBe(baseTemplate.rewards.gold * 1.2); // merchant reward multiplier
    });

    it('should generate appropriate dialogue variations', () => {
      const factionQuest = generator.generateFactionQuest(baseTemplate, mockFaction);

      expect(factionQuest.dialogue[0].variations).toHaveLength(3); // low, medium, high variations
      expect(factionQuest.dialogue[0].variations![0].standingThreshold).toBe(0);
      expect(factionQuest.dialogue[0].variations![1].standingThreshold).toBe(30);
      expect(factionQuest.dialogue[0].variations![2].standingThreshold).toBe(70);
    });
  });

  describe('registerBaseTemplate', () => {
    it('should register a base template correctly', () => {
      const newTemplate: QuestTemplate = {
        ...baseTemplate,
        id: 'new_template'
      };

      generator.registerBaseTemplate(newTemplate);
      const templates = generator.getBaseTemplates();

      expect(templates).toContainEqual(newTemplate);
    });
  });
}); 