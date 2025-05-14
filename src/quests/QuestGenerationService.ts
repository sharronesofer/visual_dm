import { QuestTemplate, QuestStage, QuestObjective, QuestType, QuestRewards, QuestRequirements } from './types';
import { FactionProfile } from './factions/types';
import { getQuestTemplates } from './quest_templates';

/**
 * Service for generating dynamic quests based on templates, parameters, and faction context.
 */
export class QuestGenerationService {
  private factionProfiles: Map<string, FactionProfile>;

  constructor(factionProfiles: Map<string, FactionProfile>) {
    this.factionProfiles = factionProfiles;
  }

  /**
   * Generate a quest for a given player/faction context.
   * @param params Generation parameters (difficulty, faction, tags, etc.)
   */
  public generateQuest(params: QuestGenerationParams): QuestTemplate | null {
    const template = this.selectTemplate(params);
    if (!template) return null;

    // Deep clone to avoid mutating the base template
    const quest: QuestTemplate = JSON.parse(JSON.stringify(template));
    quest.difficulty = params.difficulty;
    quest.objectives = this.generateStages(quest, params);
    quest.rewards = this.generateRewards(quest, params);
    // Optionally inject custom data, tags, etc.
    if (params.customData) quest.customData = { ...quest.customData, ...params.customData };
    return quest;
  }

  /**
   * Select an appropriate quest template based on parameters.
   */
  private selectTemplate(params: QuestGenerationParams): QuestTemplate | null {
    const templates = getQuestTemplates();
    // Example: filter by type, tags, difficulty, faction preferences
    let filtered = templates;
    if (params.type) filtered = filtered.filter(t => t.type === params.type);
    if (params.tags && params.tags.length > 0) {
      filtered = filtered.filter(t => params.tags!.some(tag => t.title.includes(tag) || t.description.includes(tag)));
    }
    if (params.factionId) {
      // Optionally, filter or weight by faction preferences
      // (Assume FactionProfile has quest preferences in real implementation)
    }
    // Sort or randomize for variety
    if (filtered.length === 0) return null;
    return filtered[Math.floor(Math.random() * filtered.length)];
  }

  /**
   * Generate quest stages/objectives, possibly with branching, based on template and params.
   */
  private generateStages(template: QuestTemplate, params: QuestGenerationParams): QuestObjective[] {
    // For now, clone and reset completion; future: inject param-based branches
    return template.objectives.map(obj => ({ ...obj, completed: false }));
  }

  /**
   * Generate quest rewards based on difficulty and parameters.
   */
  private generateRewards(template: QuestTemplate, params: QuestGenerationParams): QuestRewards {
    // Scale rewards by difficulty; extend for faction or tag-based bonuses
    return {
      gold: Math.round(template.rewards.gold * (params.difficulty || 1)),
      experience: Math.round(template.rewards.experience * (params.difficulty || 1)),
      items: template.rewards.items,
      reputation: template.rewards.reputation,
      diplomaticInfluence: template.rewards.diplomaticInfluence,
    };
  }
}

/**
 * Parameters for quest generation.
 */
export interface QuestGenerationParams {
  difficulty: number;
  type?: QuestType;
  tags?: string[];
  factionId?: string;
  customData?: Record<string, any>;
} 