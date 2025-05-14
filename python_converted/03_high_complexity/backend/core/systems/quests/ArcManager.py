from typing import Any, List
from enum import Enum



/**
 * Arc Manager
 * 
 * Manages narrative arcs, quest chains, and branching storylines.
 * Provides methods for creating, updating, and tracking narrative arcs.
 */
  NarrativeArc,
  QuestStatus,
  ArcCompletionRequirementType,
  BranchingPoint,
  Branch,
  BranchingCondition
} from './types'
class ArcEvents(Enum):
    ARC_CREATED = 'arc:created'
    ARC_UPDATED = 'arc:updated'
    ARC_ACTIVATED = 'arc:activated'
    ARC_COMPLETED = 'arc:completed'
    ARC_BRANCHED = 'arc:branched'
    BRANCH_SELECTED = 'arc:branch_selected'
/**
 * Arc Manager class
 */
class ArcManager {
  private static instance: \'ArcManager\'
  private arcs: Map<UUID, NarrativeArc> = new Map()
  private activeArcs: Set<UUID> = new Set()
  private questManager: QuestManager
  private eventEmitter: EventEmitter = new EventEmitter()
  /**
   * Private constructor for singleton pattern
   */
  private constructor() {
    this.questManager = QuestManager.getInstance()
    this.setupEventListeners()
  }
  /**
   * Get the singleton instance
   */
  public static getInstance(): \'ArcManager\' {
    if (!ArcManager.instance) {
      ArcManager.instance = new ArcManager()
    }
    return ArcManager.instance
  }
  /**
   * Set up event listeners
   */
  private setupEventListeners(): void {
    this.questManager.on(
      QuestManager.prototype.constructor.name === 'QuestEvents' 
        ? (this.questManager.constructor as any).QUEST_COMPLETED 
        : 'quest:completed',
      (quest: Any) => {
        this.updateArcsForCompletedQuest(quest.id)
      }
    )
  }
  /**
   * Create a new narrative arc
   */
  public createArc(arc: Omit<NarrativeArc, 'id'>): NarrativeArc {
    const id = crypto.randomUUID() as UUID
    const newArc: NarrativeArc = {
      ...arc,
      id,
      quests: arc.quests || [],
      status: arc.status || QuestStatus.INACTIVE,
      isActive: arc.isActive || false,
      branchingPoints: arc.branchingPoints || [],
      isMainStory: arc.isMainStory || false,
      tags: arc.tags || []
    }
    this.arcs.set(id, newArc)
    this.eventEmitter.emit(ArcEvents.ARC_CREATED, newArc)
    return newArc
  }
  /**
   * Get a narrative arc by ID
   */
  public getArc(arcId: UUID): NarrativeArc | undefined {
    return this.arcs.get(arcId)
  }
  /**
   * Get all narrative arcs
   */
  public getAllArcs(): NarrativeArc[] {
    return Array.from(this.arcs.values())
  }
  /**
   * Get active narrative arcs
   */
  public getActiveArcs(): NarrativeArc[] {
    return Array.from(this.activeArcs).map(id => this.arcs.get(id)!)
  }
  /**
   * Get all main story arcs
   */
  public getMainStoryArcs(): NarrativeArc[] {
    return this.getAllArcs().filter(arc => arc.isMainStory)
  }
  /**
   * Get arcs by tags
   */
  public getArcsByTags(tags: List[string]): NarrativeArc[] {
    return this.getAllArcs().filter(arc => 
      tags.some(tag => arc.tags.includes(tag))
    )
  }
  /**
   * Update arcs when a quest is completed
   */
  private updateArcsForCompletedQuest(questId: UUID): void {
    this.getActiveArcs().forEach(arc => {
      if (arc.quests.includes(questId)) {
        this.checkArcCompletion(arc.id)
        this.checkBranchingPoints(arc.id, questId)
      }
    })
  }
  /**
   * Check if an arc is complete
   */
  private checkArcCompletion(arcId: UUID): void {
    const arc = this.arcs.get(arcId)
    if (!arc || !arc.isActive) return
    let isComplete = false
    switch (arc.completionRequirements.type) {
      case ArcCompletionRequirementType.ALL_QUESTS:
        isComplete = arc.quests.every(questId => {
          const quest = this.questManager.getQuest(questId)
          return quest && quest.status === QuestStatus.COMPLETED
        })
        break
      case ArcCompletionRequirementType.SPECIFIC_QUESTS:
        if (arc.completionRequirements.specificQuestIds) {
          isComplete = arc.completionRequirements.specificQuestIds.every(questId => {
            const quest = this.questManager.getQuest(questId)
            return quest && quest.status === QuestStatus.COMPLETED
          })
        }
        break
      case ArcCompletionRequirementType.PERCENTAGE:
        if (arc.completionRequirements.percentage) {
          const completedCount = arc.quests.filter(questId => {
            const quest = this.questManager.getQuest(questId)
            return quest && quest.status === QuestStatus.COMPLETED
          }).length
          const percentage = (completedCount / arc.quests.length) * 100
          isComplete = percentage >= (arc.completionRequirements.percentage || 0)
        }
        break
      case ArcCompletionRequirementType.ANY_BRANCH:
        isComplete = arc.quests.some(questId => {
          const quest = this.questManager.getQuest(questId)
          return quest && quest.status === QuestStatus.COMPLETED
        })
        break
    }
    if (isComplete) {
      this.completeArc(arcId)
    }
  }
  /**
   * Check for branching points triggered by a completed quest
   */
  private checkBranchingPoints(arcId: UUID, completedQuestId: UUID): void {
    const arc = this.arcs.get(arcId)
    if (!arc) return
    const branchingPoints = arc.branchingPoints.filter(bp => 
      bp.sourceQuestId === completedQuestId
    )
    branchingPoints.forEach(bp => {
      this.evaluateBranchingPoint(arcId, bp)
    })
  }
  /**
   * Evaluate a branching point to determine which branch to take
   */
  private evaluateBranchingPoint(arcId: UUID, branchingPoint: BranchingPoint): void {
    const selectedBranchId = branchingPoint.defaultBranchId
    this.selectBranch(arcId, branchingPoint.id, selectedBranchId)
  }
  /**
   * Select a branch at a branching point
   */
  public selectBranch(arcId: UUID, branchingPointId: UUID, branchId: UUID): bool {
    const arc = this.arcs.get(arcId)
    if (!arc) return false
    const branchingPoint = arc.branchingPoints.find(bp => bp.id === branchingPointId)
    if (!branchingPoint) return false
    const branch = branchingPoint.branches.find(b => b.id === branchId)
    if (!branch) return false
    this.updateArcWithBranch(arcId, branch)
    this.eventEmitter.emit(ArcEvents.BRANCH_SELECTED, arc, branchingPoint, branch)
    return true
  }
  /**
   * Update arc with selected branch
   */
  private updateArcWithBranch(arcId: UUID, branch: Branch): void {
    const arc = this.arcs.get(arcId)
    if (!arc) return
    branch.questIds.forEach(questId => {
      if (!arc.quests.includes(questId)) {
        arc.quests.push(questId)
      }
    })
    this.eventEmitter.emit(ArcEvents.ARC_UPDATED, arc)
    if (branch.leadsToArcId) {
      this.activateArc(branch.leadsToArcId)
    }
  }
  /**
   * Activate a narrative arc
   */
  public activateArc(arcId: UUID): bool {
    const arc = this.arcs.get(arcId)
    if (!arc) return false
    if (arc.prerequisiteArcs && arc.prerequisiteArcs.length > 0) {
      const allPrerequisitesMet = arc.prerequisiteArcs.every(preArcId => {
        const preArc = this.arcs.get(preArcId)
        return preArc && preArc.status === QuestStatus.COMPLETED
      })
      if (!allPrerequisitesMet) {
        return false
      }
    }
    arc.isActive = true
    arc.status = QuestStatus.ACTIVE
    this.activeArcs.add(arcId)
    arc.quests.forEach(questId => {
      const quest = this.questManager.getQuest(questId)
      if (quest && quest.status === QuestStatus.INACTIVE) {
        this.questManager.makeQuestAvailable(questId)
      }
    })
    this.eventEmitter.emit(ArcEvents.ARC_ACTIVATED, arc)
    return true
  }
  /**
   * Complete a narrative arc
   */
  private completeArc(arcId: UUID): void {
    const arc = this.arcs.get(arcId)
    if (!arc) return
    arc.status = QuestStatus.COMPLETED
    arc.isActive = false
    this.activeArcs.delete(arcId)
    this.eventEmitter.emit(ArcEvents.ARC_COMPLETED, arc)
  }
  /**
   * Add a branching point to an arc
   */
  public addBranchingPoint(
    arcId: UUID, 
    sourceQuestId: UUID,
    branches: List[Branch],
    defaultBranchId: UUID,
    conditions: List[BranchingCondition] = []
  ): BranchingPoint | null {
    const arc = this.arcs.get(arcId)
    if (!arc) return null
    const id = crypto.randomUUID() as UUID
    const branchingPoint: BranchingPoint = {
      id,
      sourceQuestId,
      branches,
      defaultBranchId,
      conditions
    }
    arc.branchingPoints.push(branchingPoint)
    this.eventEmitter.emit(ArcEvents.ARC_UPDATED, arc)
    return branchingPoint
  }
  /**
   * Add a quest to an arc
   */
  public addQuestToArc(arcId: UUID, questId: UUID): bool {
    const arc = this.arcs.get(arcId)
    if (!arc) return false
    if (!arc.quests.includes(questId)) {
      arc.quests.push(questId)
      const quest = this.questManager.getQuest(questId)
      if (quest) {
      }
      this.eventEmitter.emit(ArcEvents.ARC_UPDATED, arc)
    }
    return true
  }
  /**
   * Remove a quest from an arc
   */
  public removeQuestFromArc(arcId: UUID, questId: UUID): bool {
    const arc = this.arcs.get(arcId)
    if (!arc) return false
    const index = arc.quests.indexOf(questId)
    if (index >= 0) {
      arc.quests.splice(index, 1)
      const quest = this.questManager.getQuest(questId)
      if (quest) {
      }
      this.eventEmitter.emit(ArcEvents.ARC_UPDATED, arc)
      return true
    }
    return false
  }
  /**
   * Subscribe to arc events
   */
  public on(event: \'ArcEvents\', listener: (...args: List[any]) => void): void {
    this.eventEmitter.on(event, listener)
  }
  /**
   * Unsubscribe from arc events
   */
  public off(event: \'ArcEvents\', listener: (...args: List[any]) => void): void {
    this.eventEmitter.off(event, listener)
  }
  /**
   * Delete an arc
   */
  public deleteArc(arcId: UUID): bool {
    const arc = this.arcs.get(arcId)
    if (!arc) return false
    this.arcs.delete(arcId)
    this.activeArcs.delete(arcId)
    return true
  }
} 