from typing import Any



/**
 * Quest Manager Tests
 */
  Quest, 
  QuestStatus, 
  ObjectiveType, 
  ObjectiveStatus, 
  QuestObjective
} from '../types'
describe('QuestManager', () => {
  let questManager: QuestManager
  beforeEach(() => {
    (QuestManager as any).instance = undefined
    questManager = QuestManager.getInstance()
  })
  test('should create a quest with required fields', () => {
    const quest = questManager.createQuest({
      title: 'Test Quest',
      description: 'A quest for testing',
      status: QuestStatus.INACTIVE,
      objectives: [],
      rewards: [],
      level: 1,
      isRepeatable: false,
      tags: ['test'],
      isHidden: false,
      isMandatory: false,
      hasTimeSensitiveObjectives: false
    })
    expect(quest).toBeDefined()
    expect(quest.id).toBeDefined()
    expect(quest.title).toBe('Test Quest')
    expect(quest.status).toBe(QuestStatus.INACTIVE)
  })
  test('should retrieve a quest by ID', () => {
    const quest = questManager.createQuest({
      title: 'Test Quest',
      description: 'A quest for testing',
      status: QuestStatus.INACTIVE,
      objectives: [],
      rewards: [],
      level: 1,
      isRepeatable: false,
      tags: ['test'],
      isHidden: false,
      isMandatory: false,
      hasTimeSensitiveObjectives: false
    })
    const retrievedQuest = questManager.getQuest(quest.id)
    expect(retrievedQuest).toBeDefined()
    expect(retrievedQuest?.id).toBe(quest.id)
  })
  test('should make a quest available', () => {
    const quest = questManager.createQuest({
      title: 'Test Quest',
      description: 'A quest for testing',
      status: QuestStatus.INACTIVE,
      objectives: [],
      rewards: [],
      level: 1,
      isRepeatable: false,
      tags: ['test'],
      isHidden: false,
      isMandatory: false,
      hasTimeSensitiveObjectives: false
    })
    const result = questManager.makeQuestAvailable(quest.id)
    expect(result).toBe(true)
    const updatedQuest = questManager.getQuest(quest.id)
    expect(updatedQuest?.status).toBe(QuestStatus.AVAILABLE)
  })
  test('should activate a quest', () => {
    const quest = questManager.createQuest({
      title: 'Test Quest',
      description: 'A quest for testing',
      status: QuestStatus.AVAILABLE,
      objectives: [],
      rewards: [],
      level: 1,
      isRepeatable: false,
      tags: ['test'],
      isHidden: false,
      isMandatory: false,
      hasTimeSensitiveObjectives: false
    })
    const result = questManager.activateQuest(quest.id)
    expect(result).toBe(true)
    const updatedQuest = questManager.getQuest(quest.id)
    expect(updatedQuest?.status).toBe(QuestStatus.ACTIVE)
  })
  test('should add an objective to a quest', () => {
    const quest = questManager.createQuest({
      title: 'Test Quest',
      description: 'A quest for testing',
      status: QuestStatus.INACTIVE,
      objectives: [],
      rewards: [],
      level: 1,
      isRepeatable: false,
      tags: ['test'],
      isHidden: false,
      isMandatory: false,
      hasTimeSensitiveObjectives: false
    })
    const objective = questManager.addObjective(quest.id, {
      title: 'Test Objective',
      description: 'An objective for testing',
      type: ObjectiveType.KILL,
      status: ObjectiveStatus.HIDDEN,
      isOptional: false,
      targets: [{
        targetId: '123' as UUID,
        targetType: 'enemy',
        targetName: 'Test Enemy',
        count: 5,
        current: 0
      }],
      order: 0,
      requiresAllTargets: true
    })
    expect(objective).toBeDefined()
    const updatedQuest = questManager.getQuest(quest.id)
    expect(updatedQuest?.objectives.length).toBe(1)
    expect(updatedQuest?.objectives[0].title).toBe('Test Objective')
  })
  test('should complete an objective and quest', () => {
    const quest = questManager.createQuest({
      title: 'Test Quest',
      description: 'A quest for testing',
      status: QuestStatus.ACTIVE,
      objectives: [],
      rewards: [],
      level: 1,
      isRepeatable: false,
      tags: ['test'],
      isHidden: false,
      isMandatory: false,
      hasTimeSensitiveObjectives: false
    })
    const objective = questManager.addObjective(quest.id, {
      title: 'Test Objective',
      description: 'An objective for testing',
      type: ObjectiveType.KILL,
      status: ObjectiveStatus.VISIBLE,
      isOptional: false,
      targets: [{
        targetId: '123' as UUID,
        targetType: 'enemy',
        targetName: 'Test Enemy',
        count: 5,
        current: 0
      }],
      order: 0,
      requiresAllTargets: true
    })
    const completionListener = jest.fn()
    questManager.on('quest:completed', completionListener)
    const result = questManager.updateObjectiveProgress(
      quest.id,
      objective!.id,
      '123' as UUID,
      5
    )
    expect(result).toBe(true)
    const updatedQuest = questManager.getQuest(quest.id)
    expect(updatedQuest?.status).toBe(QuestStatus.COMPLETED)
    expect(completionListener).toHaveBeenCalled()
  })
  test('should filter quests by status', () => {
    questManager.createQuest({
      title: 'Inactive Quest',
      description: 'A quest that is inactive',
      status: QuestStatus.INACTIVE,
      objectives: [],
      rewards: [],
      level: 1,
      isRepeatable: false,
      tags: ['test'],
      isHidden: false,
      isMandatory: false,
      hasTimeSensitiveObjectives: false
    })
    questManager.createQuest({
      title: 'Active Quest',
      description: 'A quest that is active',
      status: QuestStatus.ACTIVE,
      objectives: [],
      rewards: [],
      level: 1,
      isRepeatable: false,
      tags: ['test'],
      isHidden: false,
      isMandatory: false,
      hasTimeSensitiveObjectives: false
    })
    questManager.createQuest({
      title: 'Available Quest',
      description: 'A quest that is available',
      status: QuestStatus.AVAILABLE,
      objectives: [],
      rewards: [],
      level: 1,
      isRepeatable: false,
      tags: ['test'],
      isHidden: false,
      isMandatory: false,
      hasTimeSensitiveObjectives: false
    })
    const inactiveQuests = questManager.getQuestsByStatus(QuestStatus.INACTIVE)
    const activeQuests = questManager.getQuestsByStatus(QuestStatus.ACTIVE)
    const availableQuests = questManager.getQuestsByStatus(QuestStatus.AVAILABLE)
    expect(inactiveQuests.length).toBe(1)
    expect(activeQuests.length).toBe(1)
    expect(availableQuests.length).toBe(1)
    expect(inactiveQuests[0].title).toBe('Inactive Quest')
    expect(activeQuests[0].title).toBe('Active Quest')
    expect(availableQuests[0].title).toBe('Available Quest')
  })
}) 