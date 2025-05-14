/**
 * Party Member AI Tests
 */

import { PartyMemberAI, BehaviorType, CombatRole, FollowBehavior, AIState, AIEvents } from '../PartyMemberAI';
import { PartyManager } from '../PartyManager';
import { UUID } from '../../../core/types';

// Mock PartyManager singleton
jest.mock('../PartyManager', () => {
  // Mock implementation of PartyManager
  const mockPartyManager = {
    getParty: jest.fn(),
    getInstance: jest.fn()
  };
  
  return {
    PartyManager: {
      getInstance: jest.fn(() => mockPartyManager)
    }
  };
});

describe('PartyMemberAI', () => {
  let partyMemberAI: PartyMemberAI;
  let entityId: UUID;
  let partyId: UUID;
  let mockPartyManager: any;
  
  beforeEach(() => {
    // Reset all mocks
    jest.clearAllMocks();
    
    // Set up test IDs
    entityId = crypto.randomUUID() as UUID;
    partyId = crypto.randomUUID() as UUID;
    
    // Get mock party manager
    mockPartyManager = PartyManager.getInstance();
    
    // Set up mock party data
    mockPartyManager.getParty.mockImplementation((id: string) => {
      if (id === partyId) {
        return {
          id: partyId,
          name: 'Test Party',
          leaderId: 'leader-id',
          members: [
            { entityId: 'leader-id', role: 'leader' },
            { entityId, role: 'member' }
          ]
        };
      }
      return undefined;
    });
    
    // Create AI instance
    partyMemberAI = new PartyMemberAI(entityId, partyId);
  });
  
  describe('State Management', () => {
    test('should initialize with idle state', () => {
      expect(partyMemberAI.getState()).toBe(AIState.IDLE);
    });
    
    test('should change state', () => {
      partyMemberAI.setState(AIState.FOLLOWING);
      expect(partyMemberAI.getState()).toBe(AIState.FOLLOWING);
    });
    
    test('should emit state change event', () => {
      // Set up event listener
      const stateChangeHandler = jest.fn();
      partyMemberAI.on(AIEvents.STATE_CHANGED, stateChangeHandler);
      
      // Change state
      partyMemberAI.setState(AIState.COMBAT);
      
      // Check that event was emitted
      expect(stateChangeHandler).toHaveBeenCalledWith(AIState.IDLE, AIState.COMBAT);
    });
  });
  
  describe('Behavior Management', () => {
    test('should initialize with default behavior', () => {
      expect(partyMemberAI.getSettings().behavior).toBe(BehaviorType.BALANCED);
    });
    
    test('should change behavior', () => {
      partyMemberAI.setBehavior(BehaviorType.AGGRESSIVE);
      expect(partyMemberAI.getSettings().behavior).toBe(BehaviorType.AGGRESSIVE);
    });
    
    test('should emit behavior change event', () => {
      // Set up event listener
      const behaviorChangeHandler = jest.fn();
      partyMemberAI.on(AIEvents.BEHAVIOR_CHANGED, behaviorChangeHandler);
      
      // Change behavior
      partyMemberAI.setBehavior(BehaviorType.DEFENSIVE);
      
      // Check that event was emitted
      expect(behaviorChangeHandler).toHaveBeenCalledWith(BehaviorType.BALANCED, BehaviorType.DEFENSIVE);
    });
    
    test('should update AI settings', () => {
      const newSettings = {
        behavior: BehaviorType.SUPPORTIVE,
        combatRole: CombatRole.SUPPORT,
        followBehavior: FollowBehavior.CLOSE,
        fleeThreshold: 10
      };
      
      partyMemberAI.updateSettings(newSettings);
      
      const settings = partyMemberAI.getSettings();
      expect(settings.behavior).toBe(BehaviorType.SUPPORTIVE);
      expect(settings.combatRole).toBe(CombatRole.SUPPORT);
      expect(settings.followBehavior).toBe(FollowBehavior.CLOSE);
      expect(settings.fleeThreshold).toBe(10);
      
      // Other settings should remain default
      expect(settings.useItems).toBe(true);
      expect(settings.reactToThreats).toBe(true);
    });
  });
  
  describe('Decision Making', () => {
    test('should not make a decision before decision interval', () => {
      // Create mock world state
      const worldState = {};
      
      // Spy on state changes
      const setStateSpy = jest.spyOn(partyMemberAI, 'setState');
      
      // Update with current time
      const currentTime = Date.now();
      partyMemberAI.update(currentTime, worldState);
      
      // Update again immediately (before decision interval)
      partyMemberAI.update(currentTime + 100, worldState);
      
      // setState should only be called once at most (from the initial update)
      expect(setStateSpy).toHaveBeenCalledTimes(0);
    });
    
    test('should make a decision after decision interval', () => {
      // Create mock world state
      const worldState = {};
      
      // Spy on setState method
      const setStateSpy = jest.spyOn(partyMemberAI, 'setState');
      
      // Set the AI to FOLLOWING state first
      partyMemberAI.setState(AIState.FOLLOWING);
      
      // Reset the spy after initial setup
      setStateSpy.mockClear();
      
      // Update with current time
      const currentTime = Date.now();
      partyMemberAI.update(currentTime, worldState);
      
      // Update after decision interval
      partyMemberAI.update(currentTime + 1001, worldState);
      
      // setState should have been called at least once for the second update
      // (this is checking that a decision was made, not what the decision was)
      expect(setStateSpy).toHaveBeenCalled();
    });
    
    test('should transition to IDLE if party is not found', () => {
      // Mock getParty to return undefined (party not found)
      mockPartyManager.getParty.mockImplementation(() => undefined);
      
      // Create mock world state
      const worldState = {};
      
      // Update with current time
      const currentTime = Date.now();
      partyMemberAI.update(currentTime + 1001, worldState);
      
      // AI should transition to IDLE state
      expect(partyMemberAI.getState()).toBe(AIState.IDLE);
    });
    
    test('should transition to IDLE if entity is not a party member', () => {
      // Mock getParty to return a party without the entity
      mockPartyManager.getParty.mockImplementation((id: string) => {
        if (id === partyId) {
          return {
            id: partyId,
            members: [
              { entityId: 'leader-id', role: 'leader' },
              { entityId: 'other-id', role: 'member' }
            ]
          };
        }
        return undefined;
      });
      
      // Create mock world state
      const worldState = {};
      
      // Update with current time
      const currentTime = Date.now();
      partyMemberAI.update(currentTime + 1001, worldState);
      
      // AI should transition to IDLE state
      expect(partyMemberAI.getState()).toBe(AIState.IDLE);
    });
  });
}); 