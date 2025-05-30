from typing import Any, Dict, List



class BranchingOptions:
    maxBranches: float
    minRepRequired: float
    allowParallelPaths: bool
    branchWeightFactors: Dict[str, Any]
class BranchEvaluation:
    branchId: str
    weight: float
    requirements: Dict[str, bool>
class BranchTransition:
    fromStageId: str
    toStageId: str
    conditions: List[str]
    consequences: List[str]
/**
 * QuestBranchingSystem manages dynamic quest branching based on player choices, faction relationships, and world state.
 * - Integrates with FactionQuestSystem for faction standing and requirements
 * - Uses player history and memory for branch weighting
 * - Supports directed graph traversal for quest progression
 * - Designed for extensibility and testability
 */
class QuestBranchingSystem {
  private readonly defaultOptions: \'BranchingOptions\' = {
    maxBranches: 3,
    minRepRequired: 0,
    allowParallelPaths: true,
    branchWeightFactors: Dict[str, Any]
  }
  private branchTransitions: Map<string, BranchTransition[]> = new Map()
  constructor(
    private memoryManager: MemoryManager,
    private factionQuestSystem: FactionQuestSystem,
    private questMemoryIntegrator: QuestMemoryIntegrator,
    private options: Partial<BranchingOptions> = {}
  ) {
    this.options = { ...this.defaultOptions, ...options }
  }
  /**
   * Get player's current reputation score
   */
  private async getPlayerReputation(playerId: str): Promise<number> {
    const reputationMemories = await this.memoryManager.queryMemories(playerId, {
      type: MemoryEventType.FACTION_EVENT,
      limit: 10,
      minImportance: 0.5
    } as MemoryQuery)
    return reputationMemories.reduce((score, memory) => {
      const age = Date.now() - memory.timestamp
      const recencyFactor = Math.exp(-age / (30 * 24 * 60 * 60 * 1000)) 
      return score + (memory.importance * recencyFactor)
    }, 0)
  }
  /**
   * Get faction standing for player
   */
  private async getFactionStanding(
    playerId: str,
    factionRequirements?: Record<FactionType, number>
  ): Promise<number> {
    if (!factionRequirements) {
      return 0
    }
    let totalStanding = 0
    let factionCount = 0
    for (const [faction, _] of Object.entries(factionRequirements)) {
      const standing = await this.factionQuestSystem.getFactionStanding(
        playerId,
        faction as FactionType
      )
      totalStanding += standing
      factionCount++
    }
    return factionCount > 0 ? totalStanding / factionCount : 0
  }
  /**
   * Evaluate available branches for a quest stage
   */
  public async evaluateBranches(
    questId: str,
    currentStage: QuestStage,
    playerId: str,
    options: \'BranchingOptions\'
  ): Promise<QuestBranch[]> {
    const availableBranches = currentStage.branches || []
    const evaluations: List[BranchEvaluation] = []
    for (const branch of availableBranches) {
      const weight = await this.calculateBranchWeight(branch, playerId, options)
      const requirements = await this.checkBranchRequirements(branch, playerId)
      evaluations.push({
        branchId: branch.id,
        weight,
        requirements
      })
    }
    return availableBranches.filter((branch: QuestBranch, index: float) => {
      const evaluation = evaluations[index]
      return evaluation.weight > 0 && 
             this.meetsAllRequirements(evaluation.requirements)
    }).sort((a: QuestBranch, b: QuestBranch) => {
      const weightA = evaluations.find(e => e.branchId === a.id)?.weight || 0
      const weightB = evaluations.find(e => e.branchId === b.id)?.weight || 0
      return weightB - weightA
    })
  }
  /**
   * Calculate weight for a specific branch based on various factors
   */
  private async calculateBranchWeight(
    branch: QuestBranch,
    playerId: str,
    options: \'BranchingOptions\'
  ): Promise<number> {
    const reputation = await this.getPlayerReputation(playerId)
    const factionStanding = await this.getFactionStanding(playerId, branch.factionRequirements)
    const playerHistory = await this.evaluatePlayerHistory(playerId, branch)
    const npcMemoryScore = await this.evaluateNPCMemories(playerId, branch)
    return (
      (reputation * options.branchWeightFactors.reputation) +
      (factionStanding * options.branchWeightFactors.factionStanding) +
      (playerHistory * options.branchWeightFactors.playerHistory) +
      (npcMemoryScore * options.branchWeightFactors.npcMemory)
    )
  }
  /**
   * Check if a branch's requirements are met
   */
  private async checkBranchRequirements(
    branch: QuestBranch,
    playerId: str
  ): Promise<Record<string, boolean>> {
    const requirements: Record<string, boolean> = {}
    if (branch.factionRequirements) {
      for (const [faction, minStanding] of Object.entries(branch.factionRequirements)) {
        const standing = await this.factionQuestSystem.getFactionStanding(
          playerId,
          faction as FactionType
        )
        requirements[`faction_${faction}`] = standing >= minStanding
      }
    }
    if (branch.itemRequirements) {
      requirements.items = true
    }
    if (branch.skillRequirements) {
      requirements.skills = true
    }
    return requirements
  }
  /**
   * Check if all requirements are met
   */
  private meetsAllRequirements(requirements: Record<string, boolean>): bool {
    return Object.values(requirements).every(met => met)
  }
  /**
   * Evaluate player's quest history for branch weighting
   */
  private async evaluatePlayerHistory(
    playerId: str,
    branch: QuestBranch
  ): Promise<number> {
    const relevantMemories = await this.memoryManager.queryMemories(playerId, {
      type: MemoryEventType.QUEST,
      tags: branch.tags || [],
      minImportance: 0.3,
      limit: 20
    } as MemoryQuery)
    let historyScore = 0
    for (const memory of relevantMemories) {
      const age = Date.now() - memory.timestamp
      const recencyFactor = Math.exp(-age / (30 * 24 * 60 * 60 * 1000)) 
      historyScore += (memory.importance * recencyFactor)
    }
    return Math.min(historyScore / 100, 1) 
  }
  /**
   * Evaluate NPC memories related to the branch
   */
  private async evaluateNPCMemories(
    playerId: str,
    branch: QuestBranch
  ): Promise<number> {
    if (!branch.involvedNPCs?.length) {
      return 0
    }
    let totalScore = 0
    for (const npcId of branch.involvedNPCs) {
      const memories = await this.memoryManager.queryMemories(npcId, {
        type: MemoryEventType.INTERACTION,
        participants: [playerId],
        minImportance: 0.3,
        limit: 10
      } as MemoryQuery)
      const npcScore = memories.reduce((score, memory) => {
        const age = Date.now() - memory.timestamp
        const recencyFactor = Math.exp(-age / (7 * 24 * 60 * 60 * 1000)) 
        return score + (memory.details.emotionalImpact * recencyFactor)
      }, 0)
      totalScore += npcScore
    }
    return Math.min(totalScore / (branch.involvedNPCs.length * 10), 1) 
  }
  /**
   * Transition a quest to a new stage based on chosen branch
   */
  public async transitionQuestStage(
    questId: str,
    currentStage: QuestStage,
    chosenBranch: QuestBranch,
    playerId: str
  ): Promise<string> {
    await this.questMemoryIntegrator.recordQuestMemory(
      playerId,
      {
        questId,
        type: QuestType.MAJOR,
        status: QuestStatus.IN_PROGRESS,
        playerId,
        involvedNpcIds: chosenBranch.involvedNPCs || [],
        outcome: QuestStatus.IN_PROGRESS,
        description: `Chose branch ${chosenBranch.id} in stage ${currentStage.id}`,
        tags: chosenBranch.tags || []
      },
      {
        playerChoices: [chosenBranch.id],
        emotionalSignificance: chosenBranch.emotionalImpact || 0
      }
    )
    if (chosenBranch.consequences) {
      for (const consequence of chosenBranch.consequences) {
        await this.applyConsequence(consequence, playerId)
      }
    }
    return chosenBranch.nextStageId
  }
  /**
   * Apply a quest consequence
   */
  private async applyConsequence(
    consequence: QuestConsequence,
    playerId: str
  ): Promise<void> {
    switch (consequence.type) {
      case 'FACTION_STANDING':
        await this.factionQuestSystem.modifyFactionStanding(
          playerId,
          consequence.target as FactionType,
          consequence.value as number
        )
        break
      case 'NPC_RELATIONSHIP':
        await this.questMemoryIntegrator.recordQuestMemory(
          consequence.target,
          {
            questId: 'relationship_change',
            type: QuestType.MINOR,
            status: QuestStatus.COMPLETED,
            playerId,
            involvedNpcIds: [consequence.target],
            outcome: QuestStatus.COMPLETED,
            description: consequence.description,
            tags: ['relationship_change', 'quest_consequence']
          },
          {
            emotionalSignificance: consequence.value as number
          }
        )
        break
      case 'ITEM_REWARD':
        console.warn('Item reward not implemented yet')
        break
      case 'ITEM_REMOVE':
        console.warn('Item removal not implemented yet')
        break
      case 'WORLD_STATE':
        console.warn('World state changes not implemented yet')
        break
      default:
        console.warn(`Unhandled consequence type: ${consequence.type}`)
    }
  }
  /**
   * Get relevant player history for this branch
   */
  private async getRelevantPlayerHistory(playerId: str, branchId: str): Promise<string[]> {
    const relevantMemories = await this.memoryManager.queryMemories(playerId, {
      type: MemoryEventType.QUEST,
      tags: [branchId],
      limit: 5
    })
    return relevantMemories.map(memory => memory.details.description)
  }
  /**
   * Get relevant NPC memories that might affect this branch
   */
  private async getRelevantNPCMemories(
    playerId: str,
    branchId: str,
    involvedNpcIds: List[string]
  ): Promise<string[]> {
    const allMemories: List[string] = []
    for (const npcId of involvedNpcIds) {
      const memories = await this.questMemoryIntegrator.getRelevantQuestMemories(npcId, {
        playerId,
        minImportance: 0.5
      })
      allMemories.push(...memories.map(m => m.details.description))
    }
    return allMemories
  }
  /**
   * Get all possible transitions from a stage
   */
  getBranchTransitions(stageId: str): BranchTransition[] {
    return this.branchTransitions.get(stageId) || []
  }
  /**
   * Record a branch transition for future reference
   */
  recordBranchTransition(
    fromStageId: str,
    toStageId: str,
    conditions: List[string],
    consequences: List[string]
  ): void {
    const transition: \'BranchTransition\' = {
      fromStageId,
      toStageId,
      conditions,
      consequences
    }
    const transitions = this.branchTransitions.get(fromStageId) || []
    transitions.push(transition)
    this.branchTransitions.set(fromStageId, transitions)
  }
} 