from typing import Any, Dict


/**
 * Party Member AI Tests
 */
jest.mock('../PartyManager', () => {
  const mockPartyManager = {
    getParty: jest.fn(),
    getInstance: jest.fn()
  }
  return {
    PartyManager: Dict[str, Any]
  }
})
describe('PartyMemberAI', () => {
  let partyMemberAI: PartyMemberAI
  let entityId: UUID
  let partyId: UUID
  let mockPartyManager: Any
  beforeEach(() => {
    jest.clearAllMocks()
    entityId = crypto.randomUUID() as UUID
    partyId = crypto.randomUUID() as UUID
    mockPartyManager = PartyManager.getInstance()
    mockPartyManager.getParty.mockImplementation((id: str) => {
      if (id === partyId) {
        return {
          id: partyId,
          name: 'Test Party',
          leaderId: 'leader-id',
          members: [
            { entityId: 'leader-id', role: 'leader' },
            { entityId, role: 'member' }
          ]
        }
      }
      return undefined
    })
    partyMemberAI = new PartyMemberAI(entityId, partyId)
  })
  describe('State Management', () => {
    test('should initialize with idle state', () => {
      expect(partyMemberAI.getState()).toBe(AIState.IDLE)
    })
    test('should change state', () => {
      partyMemberAI.setState(AIState.FOLLOWING)
      expect(partyMemberAI.getState()).toBe(AIState.FOLLOWING)
    })
    test('should emit state change event', () => {
      const stateChangeHandler = jest.fn()
      partyMemberAI.on(AIEvents.STATE_CHANGED, stateChangeHandler)
      partyMemberAI.setState(AIState.COMBAT)
      expect(stateChangeHandler).toHaveBeenCalledWith(AIState.IDLE, AIState.COMBAT)
    })
  })
  describe('Behavior Management', () => {
    test('should initialize with default behavior', () => {
      expect(partyMemberAI.getSettings().behavior).toBe(BehaviorType.BALANCED)
    })
    test('should change behavior', () => {
      partyMemberAI.setBehavior(BehaviorType.AGGRESSIVE)
      expect(partyMemberAI.getSettings().behavior).toBe(BehaviorType.AGGRESSIVE)
    })
    test('should emit behavior change event', () => {
      const behaviorChangeHandler = jest.fn()
      partyMemberAI.on(AIEvents.BEHAVIOR_CHANGED, behaviorChangeHandler)
      partyMemberAI.setBehavior(BehaviorType.DEFENSIVE)
      expect(behaviorChangeHandler).toHaveBeenCalledWith(BehaviorType.BALANCED, BehaviorType.DEFENSIVE)
    })
    test('should update AI settings', () => {
      const newSettings = {
        behavior: BehaviorType.SUPPORTIVE,
        combatRole: CombatRole.SUPPORT,
        followBehavior: FollowBehavior.CLOSE,
        fleeThreshold: 10
      }
      partyMemberAI.updateSettings(newSettings)
      const settings = partyMemberAI.getSettings()
      expect(settings.behavior).toBe(BehaviorType.SUPPORTIVE)
      expect(settings.combatRole).toBe(CombatRole.SUPPORT)
      expect(settings.followBehavior).toBe(FollowBehavior.CLOSE)
      expect(settings.fleeThreshold).toBe(10)
      expect(settings.useItems).toBe(true)
      expect(settings.reactToThreats).toBe(true)
    })
  })
  describe('Decision Making', () => {
    test('should not make a decision before decision interval', () => {
      const worldState = {}
      const setStateSpy = jest.spyOn(partyMemberAI, 'setState')
      const currentTime = Date.now()
      partyMemberAI.update(currentTime, worldState)
      partyMemberAI.update(currentTime + 100, worldState)
      expect(setStateSpy).toHaveBeenCalledTimes(0)
    })
    test('should make a decision after decision interval', () => {
      const worldState = {}
      const setStateSpy = jest.spyOn(partyMemberAI, 'setState')
      partyMemberAI.setState(AIState.FOLLOWING)
      setStateSpy.mockClear()
      const currentTime = Date.now()
      partyMemberAI.update(currentTime, worldState)
      partyMemberAI.update(currentTime + 1001, worldState)
      expect(setStateSpy).toHaveBeenCalled()
    })
    test('should transition to IDLE if party is not found', () => {
      mockPartyManager.getParty.mockImplementation(() => undefined)
      const worldState = {}
      const currentTime = Date.now()
      partyMemberAI.update(currentTime + 1001, worldState)
      expect(partyMemberAI.getState()).toBe(AIState.IDLE)
    })
    test('should transition to IDLE if entity is not a party member', () => {
      mockPartyManager.getParty.mockImplementation((id: str) => {
        if (id === partyId) {
          return {
            id: partyId,
            members: [
              { entityId: 'leader-id', role: 'leader' },
              { entityId: 'other-id', role: 'member' }
            ]
          }
        }
        return undefined
      })
      const worldState = {}
      const currentTime = Date.now()
      partyMemberAI.update(currentTime + 1001, worldState)
      expect(partyMemberAI.getState()).toBe(AIState.IDLE)
    })
  })
}) 