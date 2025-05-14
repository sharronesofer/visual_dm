from typing import Any, Dict, List


describe('ConsequenceService', () => {
  const mockFactions: List[FactionData] = [
    {
      id: FactionType.MERCHANTS,
      name: 'Merchants',
      description: 'Trade-focused',
      relationships: Dict[str, Any],
      values: {},
      resources: {},
      standing: 0,
      tier: 1
    },
    {
      id: FactionType.WARRIORS,
      name: 'Warriors',
      description: 'Combat-focused',
      relationships: Dict[str, Any],
      values: {},
      resources: {},
      standing: 0,
      tier: 1
    }
  ]
  let factionService: FactionService
  let service: ConsequenceService
  beforeEach(() => {
    factionService = new FactionService(mockFactions)
    service = new ConsequenceService(factionService)
  })
  it('records and retrieves player actions', () => {
    const action: PlayerAction = {
      playerId: 'p1',
      actionType: 'QUEST_COMPLETION',
      timestamp: Date.now(),
      questId: 'q1',
      factionId: FactionType.MERCHANTS,
      targetFactionId: FactionType.WARRIORS,
      outcome: 'success'
    }
    service.recordAction(action)
    const history = service.getHistory('p1')
    expect(history.length).toBe(1)
    expect(history[0].actionType).toBe('QUEST_COMPLETION')
  })
  it('applies quest completion and updates relationships', () => {
    const action: PlayerAction = {
      playerId: 'p2',
      actionType: 'QUEST_COMPLETION',
      timestamp: Date.now(),
      questId: 'q2',
      factionId: FactionType.MERCHANTS,
      targetFactionId: FactionType.WARRIORS,
      outcome: 'success'
    }
    service.applyAction(action)
    const merchants = factionService.getFaction(FactionType.MERCHANTS)!
    const warriors = factionService.getFaction(FactionType.WARRIORS)!
    expect(merchants.relationships.get(FactionType.WARRIORS)).toBe(10)
    expect(warriors.relationships.get(FactionType.MERCHANTS)).toBe(10)
  })
  it('applies quest failure and updates relationships', () => {
    const action: PlayerAction = {
      playerId: 'p3',
      actionType: 'QUEST_FAILURE',
      timestamp: Date.now(),
      questId: 'q3',
      factionId: FactionType.MERCHANTS,
      targetFactionId: FactionType.WARRIORS,
      outcome: 'failure'
    }
    service.applyAction(action)
    const merchants = factionService.getFaction(FactionType.MERCHANTS)!
    const warriors = factionService.getFaction(FactionType.WARRIORS)!
    expect(merchants.relationships.get(FactionType.WARRIORS)).toBe(-10)
    expect(warriors.relationships.get(FactionType.MERCHANTS)).toBe(-10)
  })
  it('handles multiple actions and maintains history', () => {
    const actions: List[PlayerAction] = [
      {
        playerId: 'p4',
        actionType: 'QUEST_COMPLETION',
        timestamp: Date.now(),
        questId: 'q4',
        factionId: FactionType.MERCHANTS,
        targetFactionId: FactionType.WARRIORS,
        outcome: 'success'
      },
      {
        playerId: 'p4',
        actionType: 'QUEST_FAILURE',
        timestamp: Date.now(),
        questId: 'q5',
        factionId: FactionType.MERCHANTS,
        targetFactionId: FactionType.WARRIORS,
        outcome: 'failure'
      }
    ]
    actions.forEach(a => service.applyAction(a))
    const history = service.getHistory('p4')
    expect(history.length).toBe(2)
    const merchants = factionService.getFaction(FactionType.MERCHANTS)!
    expect(merchants.relationships.get(FactionType.WARRIORS)).toBe(0)
  })
  it('triggers follow-up events (stub)', () => {
    expect(() => service.triggerFollowUpEvents('p1')).not.toThrow()
  })
}) 