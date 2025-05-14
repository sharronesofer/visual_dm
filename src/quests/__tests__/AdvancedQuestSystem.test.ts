import { QuestGenerator, StageCondition, QuestStageImpl } from '../AdvancedQuestSystem';
import { QuestManager } from '../QuestManager';
import { QuestTemplate, QuestState } from '../types';

describe('Advanced Quest System', () => {
  describe('StageCondition', () => {
    it('should evaluate item conditions correctly', () => {
      const condition = new StageCondition(
        'item',
        { itemId: 'sword', quantity: 2 },
        'Have 2 swords'
      );

      const state: Required<Pick<QuestState, 'inventory'>> = {
        inventory: { sword: 1 }
      };
      expect(condition.evaluate(state)).toBe(false);

      state.inventory.sword = 2;
      expect(condition.evaluate(state)).toBe(true);
    });

    it('should evaluate location conditions correctly', () => {
      const condition = new StageCondition(
        'location',
        { locationId: 'cave' },
        'Reach the cave'
      );

      expect(condition.evaluate({ currentLocation: 'forest' })).toBe(false);
      expect(condition.evaluate({ currentLocation: 'cave' })).toBe(true);
    });

    it('should evaluate NPC interaction conditions correctly', () => {
      const condition = new StageCondition(
        'npc',
        { npcId: 'merchant', interaction: 'trade' },
        'Trade with merchant'
      );

      const state: Required<Pick<QuestState, 'npcInteractions'>> = {
        npcInteractions: {
          merchant: ['talk']
        }
      };
      expect(condition.evaluate(state)).toBe(false);

      state.npcInteractions.merchant.push('trade');
      expect(condition.evaluate(state)).toBe(true);
    });
  });

  describe('QuestStageImpl', () => {
    it('should track completion status correctly', () => {
      const stage = new QuestStageImpl(
        'test',
        'Test Stage',
        'A test stage',
        1,
        [
          new StageCondition('item', { itemId: 'key', quantity: 1 }, 'Get key'),
          new StageCondition(
            'location',
            { locationId: 'dungeon' },
            'Enter dungeon'
          )
        ]
      );

      const state: Required<Pick<QuestState, 'inventory' | 'currentLocation'>> = {
        inventory: { key: 1 },
        currentLocation: 'town'
      };
      expect(stage.checkCompletion(state)).toBe(false);

      state.currentLocation = 'dungeon';
      expect(stage.checkCompletion(state)).toBe(true);
    });

    it('should handle branching paths correctly', () => {
      const stage = new QuestStageImpl('choice', 'Choice', 'Make a choice', 1);

      stage.addBranch({
        nextStageId: 'good',
        conditions: [
          new StageCondition(
            'npc',
            { npcId: 'elder', interaction: 'help' },
            'Help the elder'
          )
        ]
      });

      stage.addBranch({
        nextStageId: 'evil',
        conditions: [
          new StageCondition(
            'npc',
            { npcId: 'elder', interaction: 'steal' },
            'Steal from elder'
          )
        ]
      });

      const state: Required<Pick<QuestState, 'npcInteractions'>> = {
        npcInteractions: {
          elder: ['help']
        }
      };

      const nextStages = stage.getNextStages(state);
      expect(nextStages).toContain('good');
      expect(nextStages).not.toContain('evil');
    });
  });

  describe('QuestGenerator', () => {
    let generator: QuestGenerator;

    beforeEach(() => {
      generator = new QuestGenerator();
    });

    it('should generate quests from templates', () => {
      const quest = generator.generateQuest('fetch_quest', 3);
      expect(quest).toBeTruthy();
      expect(quest?.stages.length).toBeGreaterThan(0);
      expect(quest?.rewards.gold).toBeGreaterThan(100); // Should be scaled for level 3
    });

    it('should respect level requirements', () => {
      expect(generator.generateQuest('fetch_quest', 0)).toBeNull();
      expect(generator.generateQuest('fetch_quest', 6)).toBeNull();
    });
  });

  describe('QuestManager', () => {
    let manager: QuestManager;
    const playerId = 'test-player';
    const templateId = 'fetch_quest';

    beforeEach(() => {
      manager = new QuestManager();
    });

    it('should start new quests correctly', () => {
      expect(manager.startQuest(playerId, templateId, 1)).toBe(true);
      const quests = manager.getPlayerQuests(playerId);
      expect(quests.length).toBe(1);
      expect(quests[0].template.id).toBe(templateId);
    });

    it('should track quest progress correctly', () => {
      manager.startQuest(playerId, templateId, 1);

      // Update quest state to complete first stage
      manager.updateQuestState(playerId, templateId, {
        npcInteractions: {
          questGiver: ['talk']
        }
      });

      const progress = manager.getQuestProgress(playerId, templateId);
      expect(progress).toBeTruthy();
      expect(progress?.completedStages.length).toBe(1);
      expect(progress?.progress).toBeGreaterThan(0);
    });

    it('should detect quest completion', () => {
      manager.startQuest(playerId, templateId, 1);

      // Complete all stages
      manager.updateQuestState(playerId, templateId, {
        npcInteractions: {
          questGiver: ['talk', 'complete']
        },
        inventory: {
          targetItem: 1
        },
        currentLocation: 'searchArea'
      });

      expect(manager.isQuestComplete(playerId, templateId)).toBe(true);
    });
  });
}); 