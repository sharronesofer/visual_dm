import { QuestState, QuestTemplate, QuestObjective } from './types';
import { QuestGenerator } from './AdvancedQuestSystem';
import { GroupQuestIntegrator } from './group/GroupQuestIntegrator';
import { GroupManager } from '../systems/npc/GroupManager';
import { GroupResourceSystem } from '../systems/npc/GroupResourceSystem';
import { QuestBranchingSystem } from './QuestBranchingSystem';
import { QuestBranch, QuestStage } from './types';
import type { BranchingOptions } from './QuestBranchingSystem';
import { FactionQuestSystem } from './factions/FactionQuestSystem';
import { FactionQuestGenerator } from './factions/FactionQuestGenerator';

interface ActiveQuest {
  template: QuestTemplate;
  state: QuestState;
  startTime: Date;
  lastUpdated: Date;
}

/**
 * Manages the state and progression of all active quests
 */
export class QuestManager {
  private activeQuests: Map<string, ActiveQuest> = new Map();
  private questGenerator: QuestGenerator;
  private groupQuestIntegrator: GroupQuestIntegrator;
  private questBranchingSystem: QuestBranchingSystem;
  private factionQuestSystem: FactionQuestSystem;
  private factionQuestGenerator: FactionQuestGenerator;

  constructor(
    groupManager: GroupManager,
    groupResourceSystem: GroupResourceSystem,
    questBranchingSystem: QuestBranchingSystem,
    factionQuestSystem: FactionQuestSystem,
    factionQuestGenerator: FactionQuestGenerator
  ) {
    this.questGenerator = new QuestGenerator();
    this.groupQuestIntegrator = new GroupQuestIntegrator(groupManager, groupResourceSystem);
    this.questBranchingSystem = questBranchingSystem;
    this.factionQuestSystem = factionQuestSystem;
    this.factionQuestGenerator = factionQuestGenerator;
  }

  /**
   * Start a new quest for a player
   */
  startQuest(playerId: string, templateId: string, difficulty: number): boolean {
    const template = this.questGenerator.generateQuest(templateId, difficulty);
    if (!template) return false;

    // Set currentStageId to first stage if available
    let currentStageId: string | undefined = undefined;
    if ((template as any).stages && (template as any).stages.length > 0) {
      currentStageId = (template as any).stages[0].id;
    }

    const questState: QuestState = {
      completedStages: [],
      inventory: {},
      npcInteractions: {},
      combatVictories: {},
      skills: {},
      currentStageId,
      branchHistory: []
    };

    const activeQuest: ActiveQuest = {
      template,
      state: questState,
      startTime: new Date(),
      lastUpdated: new Date()
    };

    const questKey = this.getQuestKey(playerId, templateId);
    this.activeQuests.set(questKey, activeQuest);
    return true;
  }

  /**
   * Start a new resource gathering quest
   */
  startResourceGatheringQuest(
    playerId: string,
    resourceType: string,
    quantity: number,
    targetGroupId: string,
    difficulty: number = 1
  ): boolean {
    const template = this.groupQuestIntegrator.createResourceGatheringQuest(
      resourceType,
      quantity,
      targetGroupId,
      difficulty
    );

    return this.startQuest(playerId, template.id, difficulty);
  }

  /**
   * Start a new territory control quest
   */
  startTerritoryControlQuest(
    playerId: string,
    territoryId: string,
    targetGroupId: string,
    difficulty: number = 1
  ): boolean {
    const template = this.groupQuestIntegrator.createTerritoryControlQuest(
      territoryId,
      targetGroupId,
      difficulty
    );

    return this.startQuest(playerId, template.id, difficulty);
  }

  /**
   * Update quest state based on group resource changes
   */
  updateGroupResourceQuests(
    groupId: string,
    resourceType: string,
    quantity: number
  ): void {
    this.activeQuests.forEach((quest, questKey) => {
      if (quest.template.type === 'RESOURCE_GATHERING') {
        const objective = quest.template.objectives.find(obj => 
          obj.type === 'COLLECT' && 
          obj.customData?.groupId === groupId &&
          obj.customData?.resourceType === resourceType
        );

        if (objective && !objective.completed) {
          if (quantity >= (objective.amount || 0)) {
            objective.completed = true;
            this.checkQuestCompletion(questKey);
          }
        }
      }
    });
  }

  /**
   * Update quest state based on territory control changes
   */
  updateTerritoryControlQuests(
    territoryId: string,
    controllingGroupId: string | null,
    contestingGroupIds: string[]
  ): void {
    this.activeQuests.forEach((quest, questKey) => {
      if (quest.template.type === 'TERRITORY_CONTROL') {
        const contestObjective = quest.template.objectives.find(obj =>
          String(obj.type) === 'CONTEST' &&
          typeof obj.customData?.action === 'string' &&
          obj.customData?.action === 'contest' &&
          String(obj.customData?.territoryId) === String(territoryId)
        );

        const controlObjective = quest.template.objectives.find(obj =>
          String(obj.type) === 'CONTROL' &&
          typeof obj.customData?.action === 'string' &&
          obj.customData?.action === 'control' &&
          String(obj.customData?.territoryId) === String(territoryId)
        );

        if (contestObjective && !contestObjective.completed) {
          const groupId = contestObjective.customData?.groupId;
          if (groupId && contestingGroupIds.includes(groupId)) {
            contestObjective.completed = true;
          }
        }

        if (controlObjective && !controlObjective.completed) {
          const groupId = controlObjective.customData?.groupId;
          if (groupId && controllingGroupId === groupId) {
            controlObjective.completed = true;
            this.checkQuestCompletion(questKey);
          }
        }
      }
    });
  }

  /**
   * Check if all objectives in a quest are completed (legacy fallback)
   */
  private checkQuestCompletion(questKey: string): void {
    const quest = this.activeQuests.get(questKey);
    if (!quest) return;
    // If using stages, check if currentStageId is undefined (quest complete)
    if (quest.state.currentStageId === undefined && (quest.template as any).stages) {
      quest.template.status = 'COMPLETED';
      return;
    }
    // Fallback: check objectives
    const allObjectivesCompleted = quest.template.objectives.every(obj => obj.completed);
    if (allObjectivesCompleted) {
      quest.template.status = 'COMPLETED';
      quest.state.completedStages = quest.template.objectives.map(obj => obj.id);
    }
  }

  /**
   * Get all active quests for a player
   */
  getPlayerQuests(playerId: string): ActiveQuest[] {
    return Array.from(this.activeQuests.entries())
      .filter(([key]) => key.startsWith(`${playerId}:`))
      .map(([_, quest]) => quest);
  }

  /**
   * Get detailed progress for a specific quest
   */
  getQuestProgress(
    playerId: string,
    templateId: string
  ): {
    completedObjectives: QuestObjective[];
    progress: number;
  } | null {
    const questKey = this.getQuestKey(playerId, templateId);
    const activeQuest = this.activeQuests.get(questKey);
    if (!activeQuest) return null;

    const { template } = activeQuest;
    const completedObjectives = template.objectives.filter(obj => obj.completed);
    const progress = (completedObjectives.length / template.objectives.length) * 100;

    return {
      completedObjectives,
      progress
    };
  }

  /**
   * Check if a quest is complete
   */
  isQuestComplete(playerId: string, templateId: string): boolean {
    const questKey = this.getQuestKey(playerId, templateId);
    const activeQuest = this.activeQuests.get(questKey);
    if (!activeQuest) return false;

    return activeQuest.template.status === 'COMPLETED';
  }

  /**
   * Generate a unique key for a quest
   */
  private getQuestKey(playerId: string, templateId: string): string {
    return `${playerId}:${templateId}`;
  }

  /**
   * Add a new quest template to the system
   */
  addQuestTemplate(template: QuestTemplate): void {
    this.questGenerator.addTemplate(template);
  }

  /**
   * Get all available quest templates
   */
  getAvailableTemplates(): QuestTemplate[] {
    return this.questGenerator.getTemplates();
  }

  /**
   * Get available branches for the current stage
   */
  async getAvailableBranches(playerId: string, templateId: string): Promise<QuestBranch[]> {
    const questKey = this.getQuestKey(playerId, templateId);
    const activeQuest = this.activeQuests.get(questKey);
    if (!activeQuest) return [];
    const template: any = activeQuest.template;
    const state = activeQuest.state;
    if (!state.currentStageId || !template.stages) return [];
    const currentStage: QuestStage | undefined = template.stages.find((s: QuestStage) => s.id === state.currentStageId);
    if (!currentStage) return [];
    const options: BranchingOptions = (this.questBranchingSystem as any).options;
    return this.questBranchingSystem.evaluateBranches(template.id, currentStage, playerId, options);
  }

  /**
   * Progress quest stage based on player branch choice
   */
  async progressQuestStage(playerId: string, templateId: string, branchId: string): Promise<boolean> {
    const questKey = this.getQuestKey(playerId, templateId);
    const activeQuest = this.activeQuests.get(questKey);
    if (!activeQuest) return false;
    const template: any = activeQuest.template;
    const state = activeQuest.state;
    if (!state.currentStageId || !template.stages) return false;
    const currentStage: QuestStage | undefined = template.stages.find((s: QuestStage) => s.id === state.currentStageId);
    if (!currentStage) return false;
    const chosenBranch = currentStage.branches.find((b: QuestBranch) => b.id === branchId);
    if (!chosenBranch) return false;
    // Transition to next stage using QuestBranchingSystem
    const nextStageId = await this.questBranchingSystem.transitionQuestStage(template.id, currentStage, chosenBranch, playerId);
    // Update quest state
    state.completedStages = [...(state.completedStages || []), state.currentStageId];
    state.branchHistory = [...(state.branchHistory || []), { stageId: state.currentStageId, branchId }];
    state.currentStageId = nextStageId;
    // If no next stage, mark quest as complete
    if (!state.currentStageId) {
      template.status = 'COMPLETED';
    }
    activeQuest.lastUpdated = new Date();
    return true;
  }

  /**
   * Start a new quest for a player, supporting faction context
   */
  startFactionQuest(playerId: string, baseTemplateId: string, factionId: string, difficulty: number): boolean {
    const factionType = this.factionQuestSystem['getFactionById'](factionId);
    const faction = this.factionQuestSystem.getFaction(factionType);
    if (!faction) return false;
    const baseTemplate = this.questGenerator.getTemplates().find(t => t.id === baseTemplateId);
    if (!baseTemplate) return false;
    const factionQuest = this.factionQuestGenerator.generateFactionQuest(baseTemplate, faction);
    // Set up quest state as before
    let currentStageId: string | undefined = undefined;
    if ((factionQuest as any).stages && (factionQuest as any).stages.length > 0) {
      currentStageId = (factionQuest as any).stages[0].id;
    }
    const questState: QuestState = {
      completedStages: [],
      inventory: {},
      npcInteractions: {},
      combatVictories: {},
      skills: {},
      currentStageId,
      branchHistory: []
    };
    const activeQuest: ActiveQuest = {
      template: factionQuest,
      state: questState,
      startTime: new Date(),
      lastUpdated: new Date()
    };
    const questKey = this.getQuestKey(playerId, factionQuest.id);
    this.activeQuests.set(questKey, activeQuest);
    return true;
  }

  /**
   * On quest completion, update faction standing and relationships
   */
  completeFactionQuest(playerId: string, questId: string): void {
    const questKey = Array.from(this.activeQuests.keys()).find(key => key.endsWith(`:${questId}`));
    if (!questKey) return;
    const quest = this.activeQuests.get(questKey);
    if (!quest) return;
    const template = quest.template as any;
    if (template.factionId) {
      this.factionQuestSystem.updateStandings(
        questId,
        template.factionId,
        'success',
        [] // TODO: pass actual choices if tracked
      );
    }
    quest.template.status = 'COMPLETED';
    quest.state.completedStages = quest.template.objectives.map((obj: any) => obj.id);
  }
} 