from typing import Any



/**
 * Quest Generator Tests
 */
  QuestStatus, 
  ObjectiveType
} from '../types'
describe('QuestGenerator', () => {
  let questGenerator: QuestGenerator
  beforeEach(() => {
    (QuestGenerator as any).instance = undefined
    (QuestManager as any).instance = undefined
    (ArcManager as any).instance = undefined
    questGenerator = QuestGenerator.getInstance()
  })
  test('should generate a quest from a template', () => {
    const quest = questGenerator.generateQuestFromTemplate('fetch')
    expect(quest).toBeDefined()
    expect(quest!.id).toBeDefined()
    expect(quest!.title).toContain('Gather')
    expect(quest!.status).toBe(QuestStatus.INACTIVE)
    expect(quest!.objectives.length).toBe(2)
    expect(quest!.rewards.length).toBe(2)
  })
  test('should generate a quest with custom variables', () => {
    const variables = {
      item: 'special herbs',
      location: 'enchanted forest',
      npc: 'wizard',
      count: '7'
    }
    const quest = questGenerator.generateQuestFromTemplate('fetch', variables)
    expect(quest).toBeDefined()
    expect(quest!.title).toBe('Gather special herbs')
    expect(quest!.description).toContain('7 special herbs')
    expect(quest!.description).toContain('enchanted forest')
    expect(quest!.description).toContain('wizard')
  })
  test('should generate a combat quest', () => {
    const quest = questGenerator.generateQuestFromTemplate('combat')
    expect(quest).toBeDefined()
    expect(quest!.id).toBeDefined()
    expect(quest!.title).toContain('Clear the')
    expect(quest!.status).toBe(QuestStatus.INACTIVE)
    expect(quest!.objectives.length).toBe(3)
    expect(quest!.objectives[0].type).toBe(ObjectiveType.KILL)
  })
  test('should generate a quest chain forming a narrative arc', () => {
    const arc = questGenerator.generateQuestChain(
      ['fetch', 'combat', 'fetch'],
      'Test Arc',
      'A test narrative arc',
      false,
      1
    )
    expect(arc).toBeDefined()
    expect(arc!.id).toBeDefined()
    expect(arc!.title).toBe('Test Arc')
    expect(arc!.quests.length).toBe(3)
    expect(arc!.status).toBe(QuestStatus.INACTIVE)
    expect(arc!.isActive).toBe(false)
  })
  test('should generate quests for a player level', () => {
    const quests = questGenerator.generateQuestsForLevel(5, 3, true)
    expect(quests).toBeDefined()
    expect(quests.length).toBe(3)
    expect(quests.every(q => q.level >= 4 && q.level <= 7)).toBe(true)
  })
  test('should get available template names', () => {
    const templates = questGenerator.getAvailableTemplateNames()
    expect(templates).toBeDefined()
    expect(templates.length).toBe(2)
    expect(templates).toContain('fetch')
    expect(templates).toContain('combat')
  })
}) 