/**
 * Quest Generator
 * 
 * Generates quests and narrative arcs based on world state, player history, and motifs.
 */

import {
  Quest,
  QuestObjective,
  QuestStatus,
  ObjectiveStatus,
  ObjectiveType,
  RewardType,
  QuestReward,
  NarrativeArc,
  ArcCompletionRequirementType
} from './types';
import { QuestManager } from './QuestManager';
import { ArcManager } from './ArcManager';
import { UUID } from '../../core/types';

// Template structures for quest generation
export interface QuestTemplate {
  title: string;
  description: string;
  objectiveTemplates: ObjectiveTemplate[];
  level: number;
  tags: string[];
  rewardTemplates: RewardTemplate[];
  isRepeatable: boolean;
  variableReplacements?: Record<string, string[]>;
}

export interface ObjectiveTemplate {
  title: string;
  description: string;
  type: ObjectiveType;
  isOptional: boolean;
  targetCountRange: [number, number];
  order: number;
}

export interface RewardTemplate {
  type: RewardType;
  amountRange: [number, number];
}

/**
 * Quest Generator class
 */
export class QuestGenerator {
  private static instance: QuestGenerator;
  private questManager: QuestManager;
  private arcManager: ArcManager;
  private questTemplates: Map<string, QuestTemplate> = new Map();
  
  /**
   * Private constructor for singleton pattern
   */
  private constructor() {
    this.questManager = QuestManager.getInstance();
    this.arcManager = ArcManager.getInstance();
    this.initializeTemplates();
  }
  
  /**
   * Get singleton instance
   */
  public static getInstance(): QuestGenerator {
    if (!QuestGenerator.instance) {
      QuestGenerator.instance = new QuestGenerator();
    }
    return QuestGenerator.instance;
  }
  
  /**
   * Initialize basic quest templates
   */
  private initializeTemplates(): void {
    // Example template for a basic fetch quest
    const fetchTemplate: QuestTemplate = {
      title: "Gather {item}",
      description: "Collect {count} {item} from {location} for {npc}.",
      objectiveTemplates: [
        {
          title: "Collect {item}",
          description: "Find and collect {count} {item} from {location}.",
          type: ObjectiveType.COLLECT,
          isOptional: false,
          targetCountRange: [3, 10],
          order: 0
        },
        {
          title: "Return to {npc}",
          description: "Bring the collected {item} back to {npc}.",
          type: ObjectiveType.DELIVER,
          isOptional: false,
          targetCountRange: [1, 1],
          order: 1
        }
      ],
      level: 1,
      tags: ["fetch", "collect", "basic"],
      rewardTemplates: [
        {
          type: RewardType.EXPERIENCE,
          amountRange: [50, 200]
        },
        {
          type: RewardType.CURRENCY,
          amountRange: [10, 50]
        }
      ],
      isRepeatable: true,
      variableReplacements: {
        item: ["herbs", "wood", "iron ore", "fruits", "water"],
        location: ["forest", "mine", "valley", "mountain", "riverside"],
        npc: ["village elder", "blacksmith", "alchemist", "merchant", "farmer"],
        count: ["3", "5", "8", "10"]
      }
    };
    
    // Example template for a basic combat quest
    const combatTemplate: QuestTemplate = {
      title: "Clear the {location} of {enemy}",
      description: "{npc} needs your help to clear the {location} of dangerous {enemy} that have been causing trouble.",
      objectiveTemplates: [
        {
          title: "Defeat {enemy}",
          description: "Defeat {count} {enemy} in the {location}.",
          type: ObjectiveType.KILL,
          isOptional: false,
          targetCountRange: [5, 15],
          order: 0
        },
        {
          title: "Collect proof",
          description: "Collect proof of your victories to show {npc}.",
          type: ObjectiveType.COLLECT,
          isOptional: false,
          targetCountRange: [1, 1],
          order: 1
        },
        {
          title: "Return to {npc}",
          description: "Return to {npc} with your proof of victory.",
          type: ObjectiveType.DELIVER,
          isOptional: false,
          targetCountRange: [1, 1],
          order: 2
        }
      ],
      level: 2,
      tags: ["combat", "kill", "basic"],
      rewardTemplates: [
        {
          type: RewardType.EXPERIENCE,
          amountRange: [100, 300]
        },
        {
          type: RewardType.CURRENCY,
          amountRange: [20, 100]
        },
        {
          type: RewardType.ITEM,
          amountRange: [1, 1]
        }
      ],
      isRepeatable: true,
      variableReplacements: {
        enemy: ["wolves", "bandits", "spiders", "undead", "goblins"],
        location: ["forest", "caves", "hills", "ruins", "swamp"],
        npc: ["guard captain", "village elder", "merchant", "survivor", "hunter"],
        count: ["5", "8", "12", "15"]
      }
    };
    
    // Add templates to the map
    this.questTemplates.set("fetch", fetchTemplate);
    this.questTemplates.set("combat", combatTemplate);
    
    // In a real implementation, you would load these from a database or files
  }
  
  /**
   * Generate a quest from a template
   */
  public generateQuestFromTemplate(
    templateName: string,
    variables?: Record<string, string>,
    giverEntityId?: UUID,
    levelOverride?: number
  ): Quest | null {
    const template = this.questTemplates.get(templateName);
    if (!template) return null;
    
    // Prepare variables to replace in the template
    const replacements: Record<string, string> = { ...variables };
    
    // Fill in missing variables with random choices from the template
    if (template.variableReplacements) {
      for (const [key, options] of Object.entries(template.variableReplacements)) {
        if (!replacements[key] && options.length > 0) {
          const randomIndex = Math.floor(Math.random() * options.length);
          replacements[key] = options[randomIndex];
        }
      }
    }
    
    // Apply replacements to strings
    const applyReplacements = (text: string): string => {
      let result = text;
      for (const [key, value] of Object.entries(replacements)) {
        result = result.replace(new RegExp(`\\{${key}\\}`, 'g'), value);
      }
      return result;
    };
    
    // Generate quest title and description
    const title = applyReplacements(template.title);
    const description = applyReplacements(template.description);
    
    // Generate objectives
    const objectives: QuestObjective[] = template.objectiveTemplates.map(objTemplate => {
      const objTitle = applyReplacements(objTemplate.title);
      const objDescription = applyReplacements(objTemplate.description);
      
      // Generate random count within range
      const min = objTemplate.targetCountRange[0];
      const max = objTemplate.targetCountRange[1];
      const count = min + Math.floor(Math.random() * (max - min + 1));
      
      // Create a placeholder target
      const targetId = crypto.randomUUID() as UUID;
      const targetName = objTitle.replace("Collect ", "").replace("Defeat ", "");
      
      return {
        id: crypto.randomUUID() as UUID,
        title: objTitle,
        description: objDescription,
        type: objTemplate.type,
        status: ObjectiveStatus.HIDDEN,
        isOptional: objTemplate.isOptional,
        targets: [{
          targetId,
          targetType: objTemplate.type === ObjectiveType.KILL ? "enemy" : "item",
          targetName,
          count,
          current: 0
        }],
        order: objTemplate.order,
        requiresAllTargets: true
      };
    });
    
    // Generate rewards
    const rewards: QuestReward[] = template.rewardTemplates.map(rewardTemplate => {
      const min = rewardTemplate.amountRange[0];
      const max = rewardTemplate.amountRange[1];
      const amount = min + Math.floor(Math.random() * (max - min + 1));
      
      return {
        type: rewardTemplate.type,
        amount,
        itemId: rewardTemplate.type === RewardType.ITEM ? crypto.randomUUID() as UUID : undefined
      };
    });
    
    // Create the quest
    const quest = this.questManager.createQuest({
      title,
      description,
      status: QuestStatus.INACTIVE,
      objectives,
      rewards,
      giverEntityId,
      level: levelOverride || template.level,
      isRepeatable: template.isRepeatable,
      tags: template.tags,
      isHidden: false,
      isMandatory: false,
      hasTimeSensitiveObjectives: false
    });
    
    return quest;
  }
  
  /**
   * Generate a chain of quests forming a simple narrative arc
   */
  public generateQuestChain(
    templateNames: string[],
    arcTitle: string,
    arcDescription: string,
    isMainStory: boolean = false,
    baseLevel: number = 1
  ): NarrativeArc | null {
    if (templateNames.length === 0) return null;
    
    // Generate all quests in the chain
    const generatedQuests: Quest[] = [];
    const questIds: UUID[] = [];
    
    for (let i = 0; i < templateNames.length; i++) {
      const template = templateNames[i];
      const level = baseLevel + Math.floor(i / 2); // Gradually increase difficulty
      
      const quest = this.generateQuestFromTemplate(template, undefined, undefined, level);
      if (quest) {
        generatedQuests.push(quest);
        questIds.push(quest.id);
        
        // Set dependencies between consecutive quests
        if (i > 0) {
          // In a real implementation, you would update the quest here
          // For now, we'll assume the dependency is set
        }
      }
    }
    
    if (generatedQuests.length === 0) return null;
    
    // Create the narrative arc
    const arc = this.arcManager.createArc({
      title: arcTitle,
      description: arcDescription,
      quests: questIds,
      status: QuestStatus.INACTIVE,
      isActive: false,
      branchingPoints: [],
      completionRequirements: {
        type: ArcCompletionRequirementType.ALL_QUESTS
      },
      isMainStory,
      tags: generatedQuests[0].tags
    });
    
    return arc;
  }
  
  /**
   * Generate quests based on player level
   */
  public generateQuestsForLevel(
    playerLevel: number,
    count: number,
    includeCombat: boolean = true
  ): Quest[] {
    const result: Quest[] = [];
    const templates = Array.from(this.questTemplates.keys());
    
    // Filter out combat templates if not requested
    const availableTemplates = includeCombat 
      ? templates 
      : templates.filter(t => !t.includes("combat"));
    
    for (let i = 0; i < count; i++) {
      if (availableTemplates.length === 0) break;
      
      // Pick a random template
      const randomIndex = Math.floor(Math.random() * availableTemplates.length);
      const templateName = availableTemplates[randomIndex];
      
      // Generate a quest with appropriate level
      const quest = this.generateQuestFromTemplate(
        templateName,
        undefined,
        undefined,
        Math.max(1, playerLevel - 1 + Math.floor(Math.random() * 3))
      );
      
      if (quest) {
        result.push(quest);
      }
    }
    
    return result;
  }
  
  /**
   * Register a new quest template
   */
  public registerQuestTemplate(name: string, template: QuestTemplate): void {
    this.questTemplates.set(name, template);
  }
  
  /**
   * Get all registered template names
   */
  public getAvailableTemplateNames(): string[] {
    return Array.from(this.questTemplates.keys());
  }
} 