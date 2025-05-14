import { ConsequenceSystem, WorldState, Consequence } from '../ConsequenceSystem';
import { QuestConsequence } from '../../types';

describe('ConsequenceSystem', () => {
  let worldState: WorldState;
  let system: ConsequenceSystem;
  const playerId = 'player1';

  beforeEach(() => {
    worldState = {
      factionStandings: { 'test-faction': 0 },
      npcRelationships: {},
      environmentalConditions: {},
      availableQuests: new Set(),
      economyFactors: {
        inflation: 1.0,
        resourceScarcity: {}
      },
      activeEffects: [],
      customState: {}
    };
    system = new ConsequenceSystem(worldState);
  });

  describe('Immediate Consequences', () => {
    it('should apply immediate consequences directly', () => {
      const consequence: Consequence = {
        id: 'test-immediate',
        type: 'faction_reputation',
        severity: 'moderate',
        description: 'Test immediate consequence',
        trigger: { type: 'immediate' },
        effects: {
          immediate: (state: WorldState) => {
            state.factionStandings['test-faction'] += 1;
          }
        }
      };

      system.addConsequence(consequence);
      
      const state = system.getWorldState();
      expect(state.factionStandings['test-faction']).toBe(1);
    });
  });

  describe('Delayed Consequences', () => {
    it('should schedule delayed consequences', () => {
      jest.useFakeTimers();

      const consequence: Consequence = {
        id: 'test-delayed',
        type: 'economy',
        severity: 'minor',
        description: 'Test delayed consequence',
        trigger: { 
          type: 'delayed',
          delay: 1000 // 1 second delay
        },
        effects: {
          immediate: (state: WorldState) => {
            state.economyFactors.inflation *= 1.1;
          }
        }
      };

      system.addConsequence(consequence);
      
      // Consequence shouldn't be applied yet
      expect(system.getWorldState().economyFactors.inflation).toBe(1.0);

      // Advance time
      jest.advanceTimersByTime(1000);
      system.update(1000);

      // Now the consequence should be applied
      expect(system.getWorldState().economyFactors.inflation).toBeCloseTo(1.1);

      jest.useRealTimers();
    });
  });

  describe('Conditional Consequences', () => {
    it('should monitor and apply conditional consequences', () => {
      const consequence: Consequence = {
        id: 'test-conditional',
        type: 'quest_availability',
        severity: 'major',
        description: 'Test conditional consequence',
        trigger: {
          type: 'conditional',
          condition: (state: WorldState) => 
            state.factionStandings['test-faction'] >= 5
        },
        effects: {
          immediate: (state: WorldState) => {
            state.availableQuests.add('special-quest');
          }
        }
      };

      system.addConsequence(consequence);
      
      // Condition not met yet
      system.update(0);
      expect(system.getWorldState().availableQuests.has('special-quest')).toBe(false);

      // Meet the condition
      worldState.factionStandings['test-faction'] = 5;
      system.update(0);

      // Consequence should now be applied
      expect(system.getWorldState().availableQuests.has('special-quest')).toBe(true);
    });
  });

  describe('Ongoing Effects', () => {
    it('should apply ongoing effects during updates', () => {
      const consequence: Consequence = {
        id: 'test-ongoing',
        type: 'environment',
        severity: 'moderate',
        description: 'Test ongoing effect',
        trigger: { type: 'immediate' },
        effects: {
          ongoing: (state: WorldState, deltaTime: number) => {
            if (!state.customState.counter) {
              state.customState.counter = 0;
            }
            state.customState.counter += deltaTime;
          }
        }
      };

      system.addConsequence(consequence);
      
      system.update(100);
      expect(system.getWorldState().customState.counter).toBe(100);
      
      system.update(50);
      expect(system.getWorldState().customState.counter).toBe(150);
    });
  });

  describe('Consequence History', () => {
    it('should track consequence history with filters', () => {
      const consequence1: Consequence = {
        id: 'history-test-1',
        type: 'faction_reputation',
        severity: 'minor',
        description: 'Test history 1',
        trigger: { type: 'immediate' },
        effects: { immediate: () => {} }
      };

      const consequence2: Consequence = {
        id: 'history-test-2',
        type: 'economy',
        severity: 'major',
        description: 'Test history 2',
        trigger: { type: 'immediate' },
        effects: { immediate: () => {} }
      };

      system.addConsequence(consequence1);
      system.addConsequence(consequence2);

      const allHistory = system.getConsequenceHistory();
      expect(allHistory.length).toBe(2);

      const factionHistory = system.getConsequenceHistory({ 
        type: 'faction_reputation' 
      });
      expect(factionHistory.length).toBe(1);
      expect(factionHistory[0].consequence.id).toBe('history-test-1');

      const majorHistory = system.getConsequenceHistory({ 
        severity: 'major' 
      });
      expect(majorHistory.length).toBe(1);
      expect(majorHistory[0].consequence.id).toBe('history-test-2');
    });
  });

  describe('Cleanup', () => {
    it('should properly cleanup consequences', () => {
      const consequence: Consequence = {
        id: 'cleanup-test',
        type: 'environment',
        severity: 'moderate',
        description: 'Test cleanup',
        trigger: { type: 'immediate' },
        effects: {
          immediate: (state: WorldState) => {
            state.activeEffects.push({
              id: 'test-effect',
              type: 'buff',
              duration: 1000,
              strength: 1.5
            });
          },
          cleanup: (state: WorldState) => {
            state.activeEffects = state.activeEffects.filter(
              effect => effect.id !== 'test-effect'
            );
          }
        },
        metadata: {
          source: 'test',
          timestamp: Date.now(),
          expiresAt: Date.now() + 1000
        }
      };

      system.addConsequence(consequence);
      
      // Effect should be added
      expect(system.getWorldState().activeEffects.length).toBe(1);

      // Advance time past expiration
      jest.useFakeTimers();
      jest.advanceTimersByTime(1001);
      system.update(0);
      jest.useRealTimers();

      // Effect should be cleaned up
      expect(system.getWorldState().activeEffects.length).toBe(0);
    });
  });

  describe('Force Resolution', () => {
    it('should force resolve all consequences', () => {
      const consequence1: Consequence = {
        id: 'force-resolve-1',
        type: 'environment',
        severity: 'minor',
        description: 'Test force resolve 1',
        trigger: { type: 'immediate' },
        effects: { ongoing: () => {} }
      };

      const consequence2: Consequence = {
        id: 'force-resolve-2',
        type: 'economy',
        severity: 'minor',
        description: 'Test force resolve 2',
        trigger: { 
          type: 'delayed',
          delay: 1000
        },
        effects: { immediate: () => {} }
      };

      system.addConsequence(consequence1);
      system.addConsequence(consequence2);

      expect(system.getActiveConsequences().length).toBe(1);
      expect(system.getConsequenceHistory().length).toBe(2);

      system.resolveAllConsequences();

      expect(system.getActiveConsequences().length).toBe(0);
      expect(system.getConsequenceHistory().length).toBe(2);
      expect(system.getConsequenceHistory().every(h => h.resolvedAt)).toBe(true);
    });
  });

  describe('Item Consequences', () => {
    it('should handle item rewards', async () => {
      const consequence: QuestConsequence = {
        type: 'ITEM_REWARD',
        target: 'sword',
        value: 1
      };

      await system.processConsequence(playerId, consequence);
      const inventory = system.getPlayerInventory(playerId);
      const item = inventory.items.get('sword');

      expect(item).toBeDefined();
      expect(item?.quantity).toBe(1);
    });

    it('should handle item removal', async () => {
      // First add an item
      await system.processConsequence(playerId, {
        type: 'ITEM_REWARD',
        target: 'potion',
        value: 3
      });

      // Then remove one
      await system.processConsequence(playerId, {
        type: 'ITEM_REMOVE',
        target: 'potion',
        value: 1
      });

      const inventory = system.getPlayerInventory(playerId);
      const item = inventory.items.get('potion');

      expect(item).toBeDefined();
      expect(item?.quantity).toBe(2);
    });

    it('should throw error when removing non-existent item', async () => {
      const consequence: QuestConsequence = {
        type: 'ITEM_REMOVE',
        target: 'nonexistent',
        value: 1
      };

      await expect(system.processConsequence(playerId, consequence))
        .rejects.toThrow('Insufficient quantity of item: nonexistent');
    });
  });

  describe('World State Consequences', () => {
    it('should handle environmental changes', async () => {
      const consequence: QuestConsequence = {
        type: 'WORLD_STATE',
        target: 'environment',
        value: {
          weather: 'stormy',
          visibility: 'low'
        }
      };

      await system.processConsequence(playerId, consequence);
      const worldState = system.getWorldState();

      expect(worldState.environmentalConditions.environment).toEqual({
        weather: 'stormy',
        visibility: 'low'
      });
    });

    it('should handle economy changes', async () => {
      const consequence: QuestConsequence = {
        type: 'WORLD_STATE',
        target: 'economy',
        value: {
          inflation: 1.2,
          resourceScarcity: {
            wood: 1.5,
            iron: 2.0
          }
        }
      };

      await system.processConsequence(playerId, consequence);
      const worldState = system.getWorldState();

      expect(worldState.economyFactors.inflation).toBe(1.2);
      expect(worldState.economyFactors.resourceScarcity).toEqual({
        wood: 1.5,
        iron: 2.0
      });
    });

    it('should handle quest availability changes', async () => {
      const consequence: QuestConsequence = {
        type: 'WORLD_STATE',
        target: 'quest_availability',
        value: {
          add: ['quest1', 'quest2'],
          remove: []
        }
      };

      await system.processConsequence(playerId, consequence);
      const worldState = system.getWorldState();

      expect(worldState.availableQuests.has('quest1')).toBe(true);
      expect(worldState.availableQuests.has('quest2')).toBe(true);
    });

    it('should handle active effects', async () => {
      const effect = {
        id: 'buff1',
        type: 'strength',
        duration: 3600000, // 1 hour
        strength: 1.5
      };

      const consequence: QuestConsequence = {
        type: 'WORLD_STATE',
        target: 'active_effects',
        value: effect
      };

      await system.processConsequence(playerId, consequence);
      const worldState = system.getWorldState();

      expect(worldState.activeEffects).toContainEqual(effect);
    });

    it('should handle timed world state changes', async () => {
      const consequence: QuestConsequence = {
        type: 'WORLD_STATE',
        target: 'environment',
        value: {
          weather: 'stormy',
          duration: 1000 // 1 second
        }
      };

      await system.processConsequence(playerId, consequence);
      
      // Check initial state
      let changes = system.getLocationChanges('environment');
      expect(changes.length).toBe(1);
      expect(changes[0].value.weather).toBe('stormy');

      // Wait for expiration
      await new Promise(resolve => setTimeout(resolve, 1100));
      system.update();

      // Check state after expiration
      changes = system.getLocationChanges('environment');
      expect(changes.length).toBe(0);
    });
  });

  describe('Multiple Consequences', () => {
    it('should process multiple consequences in order', async () => {
      const consequences: QuestConsequence[] = [
        {
          type: 'ITEM_REWARD',
          target: 'gold',
          value: 100
        },
        {
          type: 'WORLD_STATE',
          target: 'economy',
          value: {
            inflation: 1.1
          }
        },
        {
          type: 'ITEM_REWARD',
          target: 'gold',
          value: 50
        }
      ];

      await system.processConsequences(playerId, consequences);

      const inventory = system.getPlayerInventory(playerId);
      const worldState = system.getWorldState();

      expect(inventory.items.get('gold')?.quantity).toBe(150);
      expect(worldState.economyFactors.inflation).toBe(1.1);
    });
  });
}); 