import { QuestTemplate, QuestObjective, QuestType, QuestRequirements } from './types';

/**
 * Main class for generating and managing quests
 */
export class QuestGenerator {
  private templates: Map<string, QuestTemplate> = new Map();

  constructor() {
    this.initializeTemplates();
  }

  private initializeTemplates(): void {
    // Initialize with some basic templates
    this.templates.set('fetch_quest', {
      id: 'fetch_quest',
      title: 'Item Retrieval',
      description: 'A quest to retrieve a valuable item',
      type: 'COLLECT',
      questType: 'COLLECT',
      status: 'PENDING',
      difficulty: 1,
      requirements: {
        minimumLevel: 1,
        minimumReputation: 0,
        items: [],
        abilities: []
      },
      objectives: [
        {
          id: 'talk_to_giver',
          description: 'Speak with the quest giver',
          type: 'INTERACT',
          target: 'questGiver',
          customData: {
            interaction: 'talk'
          },
          completed: false
        },
        {
          id: 'find_location',
          description: 'Search for clues about the item',
          type: 'EXPLORE',
          location: 'searchArea',
          completed: false
        },
        {
          id: 'collect_item',
          description: 'Find and collect the requested item',
          type: 'COLLECT',
          target: 'targetItem',
          amount: 1,
          completed: false
        },
        {
          id: 'return_item',
          description: 'Return the item to the quest giver',
          type: 'INTERACT',
          target: 'questGiver',
          customData: {
            interaction: 'complete',
            requiredItems: ['targetItem']
          },
          completed: false
        }
      ],
      dialogue: [],
      rewards: {
        gold: 100,
        experience: 50,
        items: ['commonReward']
      }
    });
  }

  /**
   * Generate a quest from a template
   */
  generateQuest(templateId: string, difficulty: number): QuestTemplate | null {
    const template = this.templates.get(templateId);
    if (!template) return null;

    // Create a new instance of the template with adjusted difficulty
    const quest: QuestTemplate = {
      ...template,
      difficulty,
      objectives: template.objectives.map(obj => ({
        ...obj,
        completed: false
      }))
    };

    // Adjust rewards based on difficulty
    quest.rewards = {
      gold: template.rewards.gold * difficulty,
      experience: template.rewards.experience * difficulty,
      items: template.rewards.items
    };

    return quest;
  }

  /**
   * Add a new quest template
   */
  addTemplate(template: QuestTemplate): void {
    this.templates.set(template.id, template);
  }

  /**
   * Get all available quest templates
   */
  getTemplates(): QuestTemplate[] {
    return Array.from(this.templates.values());
  }
} 