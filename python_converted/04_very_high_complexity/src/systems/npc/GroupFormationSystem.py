from typing import Any, Dict, List



  Group, 
  GroupMember, 
  GroupRole, 
  GroupType, 
  GROUP_CONSTANTS,
  PersonalityCompatibility,
  InteractionHistory,
  GroupFormationTrigger,
  GroupDissolutionCondition,
  GroupSizeRecommendation
} from '../../types/npc/group'
class GroupFormationScore:
    npcId: str
    score: float
    affinityScore: float
    proximityScore: float
    goalAlignmentScore: float
    personalityScore: float
    interactionScore: float
class GroupFormationSystem {
  private groupManager: GroupManager
  private spatialGrid: SpatialGrid
  private personalityCompatibility: PersonalityCompatibility
  private gridSize: float
  private eventEmitter: EventEmitter
  private sizeRecommendations: Map<string, GroupSizeRecommendation> = new Map([
    ['combat', {
      min: GROUP_CONSTANTS.MIN_MEMBERS,
      optimal: 4,
      max: GROUP_CONSTANTS.MAX_MEMBERS,
      overhead: 0.3,
      resourceRequirements: [
        { type: 'weapon', amountPerMember: 1 },
        { type: 'armor', amountPerMember: 1 }
      ],
      effectivenessMultiplier: 1.5
    }],
    ['social', {
      min: GROUP_CONSTANTS.MIN_MEMBERS,
      optimal: 6,
      max: GROUP_CONSTANTS.MAX_MEMBERS,
      overhead: 0.5,
      resourceRequirements: [],
      effectivenessMultiplier: 1.2
    }],
    ['economic', {
      min: GROUP_CONSTANTS.MIN_MEMBERS,
      optimal: 3,
      max: 5,
      overhead: 0.2,
      resourceRequirements: [
        { type: 'capital', amountPerMember: 1000 }
      ],
      effectivenessMultiplier: 1.3
    }]
  ])
  constructor(
    groupManager: GroupManager,
    gridSize: float = 100,
    personalityCompatibility?: PersonalityCompatibility
  ) {
    this.groupManager = groupManager
    this.gridSize = gridSize
    this.spatialGrid = new SpatialGrid(gridSize)
    this.eventEmitter = new EventEmitter()
    this.personalityCompatibility = personalityCompatibility || {
      traitWeights: new Map(),
      complementaryTraits: new Map(),
      minCompatibilityScore: 0.5
    }
  }
  private initializePersonalityCompatibility() {
    const traitWeights = new Map<string, number>([
      ['leadership', 1.0],
      ['cooperation', 0.9],
      ['adaptability', 0.8],
      ['reliability', 0.7],
      ['creativity', 0.6]
    ])
    const complementaryTraits = new Map<string, string[]>([
      ['leadership', ['cooperation', 'reliability']],
      ['creativity', ['reliability', 'adaptability']],
      ['cooperation', ['leadership', 'creativity']]
    ])
    this.personalityCompatibility = {
      traitWeights,
      complementaryTraits,
      minCompatibilityScore: GROUP_CONSTANTS.MIN_PERSONALITY_COMPATIBILITY
    }
  }
  /**
   * Calculate personality compatibility score between two NPCs
   */
  private calculatePersonalityScore(npc: NPCData, others: List[NPCData]): float {
    const compatibilities = others.map(other => {
      let score = 0
      let totalWeight = 0
      npc.personality.traits.forEach((value, trait) => {
        const weight = this.personalityCompatibility.traitWeights.get(trait) || 1
        const otherValue = other.personality.traits.get(trait) || 0
        const complementary = this.personalityCompatibility.complementaryTraits.get(trait)
        if (complementary) {
          const complementaryScore = complementary.reduce((max, compTrait) => {
            const compValue = other.personality.traits.get(compTrait) || 0
            return Math.max(max, 1 - Math.abs(value - compValue))
          }, 0)
          score += complementaryScore * weight
        } else {
          score += (1 - Math.abs(value - otherValue)) * weight
        }
        totalWeight += weight
      })
      return totalWeight > 0 ? score / totalWeight : 0
    })
    return compatibilities.length > 0
      ? compatibilities.reduce((sum, score) => sum + score, 0) / compatibilities.length
      : 0
  }
  /**
   * Calculate interaction history score between two NPCs
   */
  private calculateInteractionScore(npc: NPCData, others: List[NPCData]): float {
    const interactionScores = others.map(other => {
      const history = npc.interactionHistory?.individual.get(other.id)
      if (!history) return 0
      const total = history.positive + history.neutral + history.negative
      if (total === 0) return 0
      const successRate = (history.positive + history.neutral * 0.5) / total
      const recency = Math.exp(
        -(Date.now() - history.lastInteraction) / 
        (30 * 24 * 60 * 60 * 1000)  
      )
      return successRate * recency
    })
    return interactionScores.length > 0
      ? interactionScores.reduce((sum, score) => sum + score, 0) / interactionScores.length
      : 0
  }
  /**
   * Enhanced affinity score calculation
   */
  private calculateAffinityScore(npc: NPCData, others: List[NPCData]): float {
    const affinities = others.map(other => {
      const relationshipScore = npc.relationships?.get(other.id)?.score || 0
      const factionAlignment = this.calculateFactionAlignment(npc, other)
      const sharedHistory = this.calculateSharedHistory(npc, other)
      return (
        relationshipScore * 0.5 +
        factionAlignment * 0.3 +
        sharedHistory * 0.2
      )
    })
    return affinities.length > 0 
      ? affinities.reduce((sum, score) => sum + score, 0) / affinities.length
      : 0
  }
  /**
   * Calculate proximity score based on NPCs' positions
   */
  private calculateProximityScore(npc: NPCData, others: List[NPCData]): float {
    const distances = others.map(other => {
      const distance = this.spatialGrid.getDistance(npc.position, other.position)
      return Math.max(0, 1 - (distance / this.gridSize))
    })
    return distances.length > 0
      ? distances.reduce((sum, score) => sum + score, 0) / distances.length
      : 0
  }
  /**
   * Enhanced goal alignment score calculation
   */
  private calculateGoalAlignmentScore(npc: NPCData, others: List[NPCData]): float {
    const alignments = others.map(other => {
      const sharedGoals = npc.goals.filter(goal1 =>
        other.goals.some(goal2 => 
          goal1.type === goal2.type && 
          Math.abs(goal1.priority - goal2.priority) <= 0.2
        )
      )
      return sharedGoals.length / Math.max(npc.goals.length, 1)
    })
    return alignments.length > 0
      ? alignments.reduce((sum, score) => sum + score, 0) / alignments.length
      : 0
  }
  private calculateFactionAlignment(npc1: NPCData, npc2: NPCData): float {
    if (npc1.faction === npc2.faction) return 1
    return 0
  }
  private calculateSharedHistory(npc1: NPCData, npc2: NPCData): float {
    const history1 = npc1.interactionHistory?.individual.get(npc2.id)
    const history2 = npc2.interactionHistory?.individual.get(npc1.id)
    if (!history1 || !history2) return 0
    const total1 = history1.positive + history1.neutral + history1.negative
    const total2 = history2.positive + history2.neutral + history2.negative
    if (total1 === 0 || total2 === 0) return 0
    const score1 = (history1.positive + history1.neutral * 0.5) / total1
    const score2 = (history2.positive + history2.neutral * 0.5) / total2
    return (score1 + score2) / 2
  }
  /**
   * Find potential group members for an NPC
   */
  public findPotentialGroupMembers(
    initiatorNPC: NPCData,
    candidates: List[NPCData],
    minScore: float = 60
  ): GroupFormationScore[] {
    const scores: List[GroupFormationScore] = []
    for (const candidate of candidates) {
      if (candidate.id === initiatorNPC.id) continue
      const affinityScore = this.calculateAffinityScore(initiatorNPC, [candidate])
      const proximityScore = this.calculateProximityScore(initiatorNPC, [candidate])
      const goalAlignmentScore = this.calculateGoalAlignmentScore(initiatorNPC, [candidate])
      const totalScore = (
        affinityScore * 0.4 +
        proximityScore * 0.2 +
        goalAlignmentScore * 0.4
      )
      if (totalScore >= minScore) {
        scores.push({
          npcId: candidate.id,
          score: totalScore,
          affinityScore,
          proximityScore,
          goalAlignmentScore
        })
      }
    }
    return scores.sort((a, b) => b.score - a.score)
  }
  /**
   * Form a new group based on compatible NPCs
   */
  public formGroup(
    initiatorNPC: NPCData,
    candidates: List[NPCData],
    groupType: GroupType,
    minMembers: float = 3,
    maxMembers: float = 10
  ): Group | null {
    const potentialMembers = this.findPotentialGroupMembers(initiatorNPC, candidates)
    if (potentialMembers.length < minMembers - 1) {
      return null
    }
    const selectedMembers = potentialMembers.slice(0, maxMembers - 1)
    const group = this.groupManager.createGroup(
      `${initiatorNPC.name}'s Group`,
      groupType,
      `Group formed by ${initiatorNPC.name} with ${selectedMembers.length} members`,
      initiatorNPC.id
    )
    for (const { npcId, score } of selectedMembers) {
      const role = score >= 80 ? GroupRole.DEPUTY
        : score >= 70 ? GroupRole.ADVISOR
        : GroupRole.MEMBER
      this.groupManager.addMember(group.id, npcId, role)
    }
    return group
  }
  /**
   * Check if a group should be formed based on NPC interactions and compatibility
   */
  public shouldFormGroup(
    npcs: List[NPCData],
    interactionThreshold: float = 5,
    compatibilityThreshold: float = 70
  ): { initiator: NPCData, candidates: List[NPCData] } | null {
    for (const npc of npcs) {
      const interactions = new Map<string, number>()
      npc.recentInteractions.forEach((interaction: NPCInteraction) => {
        const otherId = interaction.participants.find((id: str) => id !== npc.id)
        if (otherId) {
          interactions.set(otherId, (interactions.get(otherId) || 0) + 1)
        }
      })
      const frequentInteractors = Array.from(interactions.entries())
        .filter(([_, count]) => count >= interactionThreshold)
        .map(([id]) => npcs.find(n => n.id === id))
        .filter((n): n is NPCData => n !== undefined)
      if (frequentInteractors.length >= 2) {
        const compatibilityScores = this.findPotentialGroupMembers(
          npc,
          frequentInteractors,
          compatibilityThreshold
        )
        if (compatibilityScores.length >= 2) {
          return {
            initiator: npc,
            candidates: frequentInteractors
          }
        }
      }
    }
    return null
  }
  /**
   * Update NPC positions in the spatial grid
   */
  public updateNPCPosition(npcId: str, x: float, y: float): void {
    this.spatialGrid.updateEntity(npcId, { x, y })
  }
  /**
   * Initiate group formation between two NPCs
   */
  private async initiateGroupFormation(
    npcId: str,
    targetId: str,
    groupType: GroupType
  ): Promise<void> {
    const npc = await this.groupManager.getNPC(npcId)
    const target = await this.groupManager.getNPC(targetId)
    if (!npc || !target) {
      throw new Error('One or both NPCs not found')
    }
    const group = this.formGroup(npc, [target], groupType)
    if (!group) {
      throw new Error('Failed to form group')
    }
  }
  /**
   * Add a member to an existing group
   */
  private async addMemberToGroup(
    groupId: str,
    npcId: str
  ): Promise<void> {
    const npc = await this.groupManager.getNPC(npcId)
    if (!npc) {
      throw new Error('NPC not found')
    }
    const group = this.groupManager.getGroup(groupId)
    if (!group) {
      throw new Error('Group not found')
    }
    const members = Array.from(group.members.values())
    const scores = this.findPotentialGroupMembers(npc, members)
    if (scores.length > 0 && scores[0].score >= 60) {
      this.groupManager.addMember(groupId, npcId, GroupRole.MEMBER)
    } else {
      throw new Error('NPC not compatible with group')
    }
  }
  /**
   * Set up resource sharing between NPCs
   */
  private async setupResourceSharing(
    npcId1: str,
    npcId2: str,
    resources: Any
  ): Promise<void> {
    const npc1 = await this.groupManager.getNPC(npcId1)
    const npc2 = await this.groupManager.getNPC(npcId2)
    if (!npc1 || !npc2) {
      throw new Error('One or both NPCs not found')
    }
    console.log(`Setting up resource sharing between ${npcId1} and ${npcId2}`)
  }
  /**
   * Process a cooperation proposal between NPCs
   */
  public async processCooperation(
    npcId: str,
    targetId: str,
    proposal: Any
  ): Promise<void> {
    try {
      if (proposal.formGroup) {
        await this.initiateGroupFormation(npcId, targetId, proposal.groupType)
      } else if (proposal.joinGroup) {
        await this.addMemberToGroup(proposal.groupId, targetId)
      }
      if (proposal.sharedResources) {
        await this.setupResourceSharing(npcId, targetId, proposal.sharedResources)
      }
    } catch (error) {
      console.error('Error processing cooperation:', error)
      throw error
    }
  }
  /**
   * Calculate optimal group size based on purpose and available resources
   */
  private calculateOptimalGroupSize(
    purpose: str,
    availableResources: Map<string, number>
  ): float {
    const recommendation = this.sizeRecommendations.get(purpose) || {
      min: GROUP_CONSTANTS.MIN_MEMBERS,
      optimal: 4,
      max: GROUP_CONSTANTS.MAX_MEMBERS,
      overhead: GROUP_CONSTANTS.MAX_COMMUNICATION_OVERHEAD,
      resourceRequirements: [],
      effectivenessMultiplier: 1.0
    }
    const maxByResources = recommendation.resourceRequirements.reduce((max, req) => {
      const available = availableResources.get(req.type) || 0
      return Math.min(max, Math.floor(available / req.amountPerMember))
    }, recommendation.max)
    return Math.min(
      maxByResources,
      Math.floor(recommendation.optimal * recommendation.effectivenessMultiplier)
    )
  }
  /**
   * Check if group formation should be triggered
   */
  private checkFormationTriggers(
    npcs: List[NPCData],
    trigger: GroupFormationTrigger
  ): bool {
    const { type, condition, priority } = trigger
    switch (type) {
      case 'emergency':
        return this.evaluateEmergencyCondition(npcs, condition, Date.now())
      case 'resource':
        return this.evaluateResourceCondition(npcs, condition, Date.now())
      case 'goal':
        return this.evaluateGoalCondition(npcs, condition, Date.now())
      case 'periodic':
        return this.evaluatePeriodicCondition(condition, Date.now())
      case 'social':
        return this.evaluateSocialCondition(npcs, condition, Date.now())
      default:
        return false
    }
  }
  private calculateFormationScore(
    npc: NPCData,
    potentialMembers: List[NPCData],
    purpose: str
  ): \'GroupFormationScore\' {
    const affinityScore = this.calculateAffinityScore(npc, potentialMembers)
    const proximityScore = this.calculateProximityScore(npc, potentialMembers)
    const goalAlignmentScore = this.calculateGoalAlignmentScore(npc, potentialMembers)
    const personalityScore = this.calculatePersonalityScore(npc, potentialMembers)
    const interactionScore = this.calculateInteractionScore(npc, potentialMembers)
    const score = (
      affinityScore * GROUP_CONSTANTS.AFFINITY_WEIGHT +
      proximityScore * GROUP_CONSTANTS.PROXIMITY_WEIGHT +
      goalAlignmentScore * GROUP_CONSTANTS.GOAL_ALIGNMENT_WEIGHT +
      personalityScore * GROUP_CONSTANTS.PERSONALITY_WEIGHT +
      interactionScore * GROUP_CONSTANTS.INTERACTION_WEIGHT
    ) / (
      GROUP_CONSTANTS.AFFINITY_WEIGHT +
      GROUP_CONSTANTS.PROXIMITY_WEIGHT +
      GROUP_CONSTANTS.GOAL_ALIGNMENT_WEIGHT +
      GROUP_CONSTANTS.PERSONALITY_WEIGHT +
      GROUP_CONSTANTS.INTERACTION_WEIGHT
    )
    return {
      npcId: npc.id,
      score,
      affinityScore,
      proximityScore,
      goalAlignmentScore,
      personalityScore,
      interactionScore
    }
  }
  private async evaluateGroupFormation(
    initiatorNPC: NPCData,
    candidates: List[NPCData],
    purpose: str,
    currentTime: float
  ): Promise<GroupFormationScore[]> {
    const scores: List[GroupFormationScore] = []
    for (const candidate of candidates) {
      if (candidate.id === initiatorNPC.id) continue
      const score = this.calculateFormationScore(
        initiatorNPC,
        [candidate],
        purpose
      )
      scores.push(score)
    }
    return scores
  }
  private async getNPCsFromMembers(members: List[GroupMember]): Promise<NPCData[]> {
    const npcs: List[NPCData] = []
    for (const member of members) {
      const npc = await this.groupManager.getNPC(member.id)
      if (npc) {
        const relationships = new Map(
          Array.from(member.relationshipScores.entries())
            .map(([id, score]) => [id, { score }])
        )
        npcs.push({
          ...npc,
          id: member.id,
          relationships
        })
      }
    }
    return npcs
  }
  /**
   * Process group lifecycle events
   */
  public async processGroupLifecycle(
    group: Group,
    dissolutionConditions: List[GroupDissolutionCondition]
  ): Promise<void> {
    try {
      for (const condition of dissolutionConditions) {
        if (this.evaluateDissolutionCondition(group, condition)) {
          const gracePeriod = condition.gracePeriod || 0
          const warningThreshold = condition.warningThreshold || condition.threshold
          if (this.evaluateDissolutionCondition(group, {
            ...condition,
            threshold: warningThreshold
          })) {
            this.emitGroupEvent(group.id, 'dissolution_warning', {
              condition: condition.type,
              timeRemaining: gracePeriod
            })
            if (gracePeriod > 0) {
              await new Promise(resolve => setTimeout(resolve, gracePeriod))
              if (this.evaluateDissolutionCondition(group, condition)) {
                await this.dissolveGroup(group.id, condition.type)
              }
            } else {
              await this.dissolveGroup(group.id, condition.type)
            }
          }
        }
      }
    } catch (error) {
      console.error('Error processing group lifecycle:', error)
      throw error
    }
  }
  /**
   * Dissolve a group and handle cleanup
   */
  private async dissolveGroup(
    groupId: str,
    reason: str
  ): Promise<void> {
    try {
      const group = this.groupManager.getGroup(groupId)
      if (!group) {
        throw new Error('Group not found')
      }
      group.members.forEach((member, memberId) => {
        this.emitGroupEvent(groupId, 'group_dissolved', {
          memberId,
          reason,
          groupData: group
        })
      })
      await this.handleResourceDistribution(group)
      await this.archiveGroupData(group)
      await this.groupManager.removeGroup(groupId)
    } catch (error) {
      console.error('Error dissolving group:', error)
      throw error
    }
  }
  private async handleResourceDistribution(group: Group): Promise<void> {
    this.eventEmitter.emit('group:resourceDistribution', {
      groupId: group.id,
      resources: group.resources
    })
  }
  private async archiveGroupData(group: Group): Promise<void> {
    this.eventEmitter.emit('group:archive', {
      groupId: group.id,
      data: group
    })
  }
  private emitGroupEvent(
    groupId: str,
    eventType: str,
    data: Any
  ): void {
    this.eventEmitter.emit(`group:${eventType}`, {
      groupId,
      ...data
    })
  }
  /**
   * Check if a group should be dissolved
   */
  private evaluateDissolutionCondition(
    group: Group,
    condition: GroupDissolutionCondition
  ): bool {
    switch (condition.type) {
      case 'conflict':
        return this.evaluateConflictLevel(group) >= condition.threshold
      case 'goalCompletion':
        return this.evaluateGoalCompletion(group) >= condition.threshold
      case 'resourceDepletion':
        return this.evaluateResourceDepletion(group) >= condition.threshold
      case 'inactivity':
        return this.evaluateInactivity(group) >= condition.threshold
      case 'ineffectiveness':
        return this.evaluateIneffectiveness(group) >= condition.threshold
      default:
        return false
    }
  }
  private evaluateConflictLevel(group: Group): float {
    let conflictScore = 0
    let totalRelationships = 0
    group.members.forEach((member1, id1) => {
      group.members.forEach((member2, id2) => {
        if (id1 < id2) {  
          const score = member1.relationshipScores.get(id2) || 0
          if (score < 0) {
            conflictScore += Math.abs(score)
          }
          totalRelationships++
        }
      })
    })
    return totalRelationships > 0 ? 
      conflictScore / (totalRelationships * 10) : 
      0
  }
  private evaluateGoalCompletion(group: Group): float {
    if (!group.goals.length) return 1  
    const totalProgress = group.goals.reduce(
      (sum, goal) => sum + goal.progress,
      0
    )
    return totalProgress / (group.goals.length * 100)  
  }
  private evaluateResourceDepletion(group: Group): float {
    const { resources } = group
    if (!resources) return 0
    const totalResources = Array.from(resources.assets.values())
      .reduce((sum, amount) => sum + amount, 0)
    const wealthDepletion = 1 - (resources.wealth / GROUP_CONSTANTS.MAX_WEALTH)
    return Math.max(
      wealthDepletion,
      totalResources === 0 ? 1 : 0
    )
  }
  private evaluateInactivity(group: Group): float {
    const now = Date.now()
    const inactivePeriod = now - group.lastActive
    return Math.min(1, 
      inactivePeriod / GROUP_CONSTANTS.INACTIVITY_THRESHOLD
    )
  }
  private evaluateIneffectiveness(group: Group): float {
    const averageContribution = Array.from(group.members.values())
      .reduce((sum, member) => sum + member.contributionScore, 0) / 
      group.members.size
    const recentGoalProgress = group.goals
      .filter(goal => goal.progress > 0)
      .length / Math.max(1, group.goals.length)
    return 1 - ((averageContribution + recentGoalProgress) / 2)
  }
  private evaluateEmergencyCondition(
    npcs: List[NPCData],
    condition: Dict[str, Any],
    currentTime: float
  ): bool {
    return false
  }
  private evaluateResourceCondition(
    npcs: List[NPCData],
    condition: Dict[str, Any],
    currentTime: float
  ): bool {
    const resourceAvailability = npcs.reduce((total, npc) => {
      return total + (npc.economicData?.wealth || 0)
    }, 0) / npcs.length
    return resourceAvailability >= condition.threshold
  }
  private evaluateGoalCondition(
    npcs: List[NPCData],
    condition: Dict[str, Any],
    currentTime: float
  ): bool {
    const goalCounts = new Map<string, number>()
    npcs.forEach(npc => {
      npc.goals.forEach(goal => {
        if (goal.priority >= condition.threshold) {
          goalCounts.set(goal.type, (goalCounts.get(goal.type) || 0) + 1)
        }
      })
    })
    return Array.from(goalCounts.values()).some(count => 
      count >= GROUP_CONSTANTS.MIN_MEMBERS
    )
  }
  private evaluatePeriodicCondition(
    condition: Dict[str, Any],
    currentTime: float
  ): bool {
    if (!condition.timeWindow) return false
    return (currentTime % condition.timeWindow) < condition.threshold
  }
  private evaluateSocialCondition(
    npcs: List[NPCData],
    condition: Dict[str, Any],
    currentTime: float
  ): bool {
    const recentInteractions = npcs.reduce((count, npc) => {
      return count + npc.recentInteractions.length
    }, 0) / npcs.length
    return recentInteractions >= condition.threshold
  }
} 