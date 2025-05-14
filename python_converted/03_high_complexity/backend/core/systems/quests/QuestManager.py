from typing import Any, List
from enum import Enum



/**
 * Quest Manager
 * 
 * Manages quest lifecycle, state transitions, and interactions.
 * Provides methods for creating, updating, and tracking quests.
 */
  Quest,
  QuestObjective,
  QuestStatus,
  ObjectiveStatus,
  ObjectiveType,
  RewardType,
  ObjectiveTarget
} from './types'
class QuestEvents(Enum):
    QUEST_CREATED = 'quest:created'
    QUEST_UPDATED = 'quest:updated'
    QUEST_STATUS_CHANGED = 'quest:status_changed'
    OBJECTIVE_COMPLETED = 'quest:objective_completed'
    OBJECTIVE_UPDATED = 'quest:objective_updated'
    QUEST_COMPLETED = 'quest:completed'
    QUEST_FAILED = 'quest:failed'
    QUEST_ABANDONED = 'quest:abandoned'
    QUEST_EXPIRED = 'quest:expired'
    REWARDS_GRANTED = 'quest:rewards_granted'
/**
 * Quest Manager class
 */
class QuestManager {
  private static instance: \'QuestManager\'
  private quests: Map<UUID, Quest> = new Map()
  private activeQuests: Set<UUID> = new Set()
  private eventEmitter: EventEmitter = new EventEmitter()
  /**
   * Private constructor for singleton pattern
   */
  private constructor() {
    this.setupEventListeners()
  }
  /**
   * Get the singleton instance
   */
  public static getInstance(): \'QuestManager\' {
    if (!QuestManager.instance) {
      QuestManager.instance = new QuestManager()
    }
    return QuestManager.instance
  }
  /**
   * Set up event listeners
   */
  private setupEventListeners(): void {
    this.eventEmitter.on(QuestEvents.OBJECTIVE_COMPLETED, (questId: UUID) => {
      this.checkQuestCompletion(questId)
    })
  }
  /**
   * Create a new quest
   */
  public createQuest(quest: Omit<Quest, 'id'>): Quest {
    const id = crypto.randomUUID() as UUID
    const newQuest: Quest = {
      ...quest,
      id,
      status: quest.status || QuestStatus.INACTIVE,
      objectives: quest.objectives || [],
      rewards: quest.rewards || [],
      tags: quest.tags || [],
      isHidden: quest.isHidden || false,
      isMandatory: quest.isMandatory || false,
      hasTimeSensitiveObjectives: quest.hasTimeSensitiveObjectives || false,
      level: quest.level || 1,
      isRepeatable: quest.isRepeatable || false
    }
    this.quests.set(id, newQuest)
    this.eventEmitter.emit(QuestEvents.QUEST_CREATED, newQuest)
    return newQuest
  }
  /**
   * Get a quest by ID
   */
  public getQuest(questId: UUID): Quest | undefined {
    return this.quests.get(questId)
  }
  /**
   * Get all quests
   */
  public getAllQuests(): Quest[] {
    return Array.from(this.quests.values())
  }
  /**
   * Get all quests with a specific status
   */
  public getQuestsByStatus(status: QuestStatus): Quest[] {
    return Array.from(this.quests.values()).filter(quest => quest.status === status)
  }
  /**
   * Get all active quests
   */
  public getActiveQuests(): Quest[] {
    return Array.from(this.activeQuests).map(id => this.quests.get(id)!)
  }
  /**
   * Get quests by tags
   */
  public getQuestsByTags(tags: List[string]): Quest[] {
    return Array.from(this.quests.values()).filter(quest => 
      tags.some(tag => quest.tags.includes(tag))
    )
  }
  /**
   * Add an objective to a quest
   */
  public addObjective(questId: UUID, objective: Omit<QuestObjective, 'id'>): QuestObjective | null {
    const quest = this.quests.get(questId)
    if (!quest) return null
    const id = crypto.randomUUID() as UUID
    const newObjective: QuestObjective = {
      ...objective,
      id,
      status: objective.status || ObjectiveStatus.HIDDEN,
      isOptional: objective.isOptional || false,
      targets: objective.targets || [],
      order: objective.order || quest.objectives.length,
      requiresAllTargets: objective.requiresAllTargets !== undefined ? objective.requiresAllTargets : true
    }
    quest.objectives.push(newObjective)
    this.eventEmitter.emit(QuestEvents.QUEST_UPDATED, quest)
    return newObjective
  }
  /**
   * Update objective progress
   */
  public updateObjectiveProgress(
    questId: UUID, 
    objectiveId: UUID, 
    targetId: UUID, 
    progress: float
  ): bool {
    const quest = this.quests.get(questId)
    if (!quest) return false
    const objective = quest.objectives.find(obj => obj.id === objectiveId)
    if (!objective) return false
    const target = objective.targets.find(t => t.targetId === targetId)
    if (!target) return false
    target.current = Math.min(target.count, target.current + progress)
    const isTargetComplete = target.current >= target.count
    let isObjectiveComplete = false
    if (objective.requiresAllTargets) {
      isObjectiveComplete = objective.targets.every(t => t.current >= t.count)
    } else {
      isObjectiveComplete = objective.targets.some(t => t.current >= t.count)
    }
    if (isObjectiveComplete && objective.status !== ObjectiveStatus.COMPLETED) {
      objective.status = ObjectiveStatus.COMPLETED
      this.eventEmitter.emit(QuestEvents.OBJECTIVE_COMPLETED, questId, objectiveId)
    } else {
      this.eventEmitter.emit(QuestEvents.OBJECTIVE_UPDATED, questId, objectiveId)
    }
    this.eventEmitter.emit(QuestEvents.QUEST_UPDATED, quest)
    return true
  }
  /**
   * Check if a quest is complete
   */
  private checkQuestCompletion(questId: UUID): void {
    const quest = this.quests.get(questId)
    if (!quest || quest.status !== QuestStatus.ACTIVE) return
    const isComplete = quest.objectives
      .filter(obj => !obj.isOptional)
      .every(obj => obj.status === ObjectiveStatus.COMPLETED)
    if (isComplete) {
      this.completeQuest(questId)
    }
  }
  /**
   * Activate a quest
   */
  public activateQuest(questId: UUID): bool {
    const quest = this.quests.get(questId)
    if (!quest || quest.status !== QuestStatus.AVAILABLE) return false
    quest.status = QuestStatus.ACTIVE
    quest.startTime = Date.now()
    quest.objectives.forEach(obj => {
      if (obj.status === ObjectiveStatus.HIDDEN && obj.dependsOn === undefined) {
        obj.status = ObjectiveStatus.VISIBLE
      }
    })
    this.activeQuests.add(questId)
    this.eventEmitter.emit(QuestEvents.QUEST_STATUS_CHANGED, quest, QuestStatus.ACTIVE)
    return true
  }
  /**
   * Complete a quest
   */
  public completeQuest(questId: UUID): bool {
    const quest = this.quests.get(questId)
    if (!quest || quest.status !== QuestStatus.ACTIVE) return false
    quest.status = QuestStatus.COMPLETED
    this.activeQuests.delete(questId)
    this.grantRewards(questId)
    this.eventEmitter.emit(QuestEvents.QUEST_COMPLETED, quest)
    this.eventEmitter.emit(QuestEvents.QUEST_STATUS_CHANGED, quest, QuestStatus.COMPLETED)
    return true
  }
  /**
   * Fail a quest
   */
  public failQuest(questId: UUID): bool {
    const quest = this.quests.get(questId)
    if (!quest || quest.status !== QuestStatus.ACTIVE) return false
    quest.status = QuestStatus.FAILED
    this.activeQuests.delete(questId)
    this.eventEmitter.emit(QuestEvents.QUEST_FAILED, quest)
    this.eventEmitter.emit(QuestEvents.QUEST_STATUS_CHANGED, quest, QuestStatus.FAILED)
    return true
  }
  /**
   * Abandon a quest
   */
  public abandonQuest(questId: UUID): bool {
    const quest = this.quests.get(questId)
    if (!quest || quest.status !== QuestStatus.ACTIVE) return false
    quest.status = QuestStatus.ABANDONED
    this.activeQuests.delete(questId)
    this.eventEmitter.emit(QuestEvents.QUEST_ABANDONED, quest)
    this.eventEmitter.emit(QuestEvents.QUEST_STATUS_CHANGED, quest, QuestStatus.ABANDONED)
    return true
  }
  /**
   * Grant quest rewards
   */
  private grantRewards(questId: UUID): void {
    const quest = this.quests.get(questId)
    if (!quest) return
    this.eventEmitter.emit(QuestEvents.REWARDS_GRANTED, quest)
  }
  /**
   * Make a quest available to the player
   */
  public makeQuestAvailable(questId: UUID): bool {
    const quest = this.quests.get(questId)
    if (!quest || quest.status !== QuestStatus.INACTIVE) return false
    quest.status = QuestStatus.AVAILABLE
    this.eventEmitter.emit(QuestEvents.QUEST_STATUS_CHANGED, quest, QuestStatus.AVAILABLE)
    return true
  }
  /**
   * Check if all dependencies are met for a quest
   */
  public areDependenciesMet(questId: UUID): bool {
    const quest = this.quests.get(questId)
    if (!quest || !quest.dependsOn || quest.dependsOn.length === 0) return true
    return quest.dependsOn.every(depId => {
      const depQuest = this.quests.get(depId)
      return depQuest && depQuest.status === QuestStatus.COMPLETED
    })
  }
  /**
   * Expire a quest due to time limit
   */
  public expireQuest(questId: UUID): bool {
    const quest = this.quests.get(questId)
    if (!quest || quest.status !== QuestStatus.ACTIVE) return false
    quest.status = QuestStatus.EXPIRED
    this.activeQuests.delete(questId)
    this.eventEmitter.emit(QuestEvents.QUEST_EXPIRED, quest)
    this.eventEmitter.emit(QuestEvents.QUEST_STATUS_CHANGED, quest, QuestStatus.EXPIRED)
    return true
  }
  /**
   * Update quests with time limits
   */
  public updateTimeLimitedQuests(): void {
    const now = Date.now()
    this.getActiveQuests().forEach(quest => {
      if (quest.timeLimit && quest.startTime) {
        const expirationTime = quest.startTime + quest.timeLimit * 1000
        if (now >= expirationTime) {
          this.expireQuest(quest.id)
        }
      }
    })
  }
  /**
   * Subscribe to quest events
   */
  public on(event: \'QuestEvents\', listener: (...args: List[any]) => void): void {
    this.eventEmitter.on(event, listener)
  }
  /**
   * Unsubscribe from quest events
   */
  public off(event: \'QuestEvents\', listener: (...args: List[any]) => void): void {
    this.eventEmitter.off(event, listener)
  }
  /**
   * Delete a quest
   */
  public deleteQuest(questId: UUID): bool {
    const quest = this.quests.get(questId)
    if (!quest) return false
    this.quests.delete(questId)
    this.activeQuests.delete(questId)
    return true
  }
  /**
   * Find available quests for a player level
   */
  public getAvailableQuestsForLevel(level: float): Quest[] {
    return this.getQuestsByStatus(QuestStatus.AVAILABLE)
      .filter(quest => !quest.minPlayerLevel || quest.minPlayerLevel <= level)
  }
} 