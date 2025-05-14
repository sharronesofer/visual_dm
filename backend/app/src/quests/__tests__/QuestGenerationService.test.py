from typing import Any, Dict


globalThis.getQuestTemplates = jest.fn(() => [
  {
    id: 'test_quest',
    title: 'Test Quest',
    description: 'A quest for testing',
    type: 'COLLECT',
    questType: 'COLLECT',
    status: 'PENDING',
    difficulty: 1,
    requirements: Dict[str, Any],
    objectives: [
      { id: 'obj1', description: 'Collect item', type: 'COLLECT', completed: false },
      { id: 'obj2', description: 'Return item', type: 'INTERACT', completed: false }
    ],
    dialogue: [],
    rewards: Dict[str, Any]
  }
]) as any
describe('QuestGenerationService', () => {
  const mockFactions = new Map<string, FactionProfile>()
  const service = new QuestGenerationService(mockFactions)
  it('generates a quest with correct difficulty and rewards', () => {
    const params: QuestGenerationParams = { difficulty: 2 }
    const quest = service.generateQuest(params)
    expect(quest).not.toBeNull()
    expect(quest!.difficulty).toBe(2)
    expect(quest!.rewards.gold).toBe(200)
    expect(quest!.rewards.experience).toBe(100)
    expect(quest!.objectives.length).toBe(2)
    quest!.objectives.forEach(obj => expect(obj.completed).toBe(false))
  })
  it('returns null if no template matches', () => {
    (globalThis.getQuestTemplates as jest.Mock).mockReturnValueOnce([])
    const params: QuestGenerationParams = { difficulty: 1, type: 'NON_EXISTENT' as any }
    const quest = service.generateQuest(params)
    expect(quest).toBeNull()
  })
  it('injects customData into quest', () => {
    const params: QuestGenerationParams = { difficulty: 1, customData: Dict[str, Any] }
    const quest = service.generateQuest(params)
    expect(quest!.customData).toHaveProperty('foo', 'bar')
  })
  it('filters by type and tags', () => {
    (globalThis.getQuestTemplates as jest.Mock).mockReturnValueOnce([
      { id: 'a', title: 'Alpha', description: 'desc', type: 'KILL', questType: 'KILL', status: 'PENDING', difficulty: 1, requirements: Dict[str, Any], objectives: [], dialogue: [], rewards: Dict[str, Any] },
      { id: 'b', title: 'Beta', description: 'desc', type: 'COLLECT', questType: 'COLLECT', status: 'PENDING', difficulty: 1, requirements: Dict[str, Any], objectives: [], dialogue: [], rewards: Dict[str, Any] }
    ])
    const params: QuestGenerationParams = { difficulty: 1, type: 'COLLECT', tags: ['Beta'] }
    const quest = service.generateQuest(params)
    expect(quest!.id).toBe('b')
  })
  it('handles missing customData gracefully', () => {
    const params: QuestGenerationParams = { difficulty: 1 }
    const quest = service.generateQuest(params)
    expect(quest!.customData).toBeUndefined()
  })
}) 