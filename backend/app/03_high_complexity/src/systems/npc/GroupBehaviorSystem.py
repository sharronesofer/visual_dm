from typing import Any, Dict, List



class GroupDecision:
    id: str
    type: str
    description: str
    options: List[str]
    votes: Dict[str, str>
    deadline: float
    result?: str
class GroupBehaviorSystem {
  private groupManager: GroupManager
  private formationSystem: GroupFormationSystem
  private spatialGrid: SpatialGrid
  private activeDecisions: Map<string, GroupDecision>
  constructor(gridSize: float = 100) {
    this.groupManager = new GroupManager()
    this.formationSystem = new GroupFormationSystem(this.groupManager, gridSize)
    this.spatialGrid = new SpatialGrid(gridSize)
    this.activeDecisions = new Map()
  }
  /**
   * Update NPC positions in the spatial grid
   */
  public updateNPCPosition(npcId: str, x: float, y: float): void {
    this.spatialGrid.updateEntity(npcId, { x, y })
    this.formationSystem.updateNPCPosition(npcId, x, y)
  }
  /**
   * Check for potential group formations among NPCs
   */
  public checkGroupFormations(npcs: List[NPCData]): void {
    const formationCheck = this.formationSystem.shouldFormGroup(npcs)
    if (formationCheck) {
      const { initiator, candidates } = formationCheck
      const groupType = this.determineGroupType(initiator, candidates)
      const group = this.formationSystem.formGroup(
        initiator,
        candidates,
        groupType
      )
      if (group) {
        console.log(`New group formed: ${group.name} (${group.type})`)
      }
    }
  }
  /**
   * Determine the most appropriate group type based on NPC goals and traits
   */
  private determineGroupType(initiator: NPCData, candidates: List[NPCData]): GroupType {
    const allNPCs = [initiator, ...candidates]
    const goalTypes = new Map<string, number>()
    allNPCs.forEach(npc => {
      npc.goals.forEach(goal => {
        goalTypes.set(goal.type, (goalTypes.get(goal.type) || 0) + 1)
      })
    })
    const typeScores = new Map<GroupType, number>()
    goalTypes.forEach((count, goalType) => {
      switch (goalType.toLowerCase()) {
        case 'trade':
        case 'profit':
        case 'business':
          typeScores.set(GroupType.TRADING, (typeScores.get(GroupType.TRADING) || 0) + count)
          break
        case 'combat':
        case 'protection':
        case 'security':
          typeScores.set(GroupType.MERCENARY, (typeScores.get(GroupType.MERCENARY) || 0) + count)
          break
        case 'craft':
        case 'create':
        case 'build':
          typeScores.set(GroupType.CRAFTING, (typeScores.get(GroupType.CRAFTING) || 0) + count)
          break
        case 'explore':
        case 'quest':
        case 'adventure':
          typeScores.set(GroupType.ADVENTURING, (typeScores.get(GroupType.ADVENTURING) || 0) + count)
          break
        case 'socialize':
        case 'network':
        case 'community':
          typeScores.set(GroupType.SOCIAL, (typeScores.get(GroupType.SOCIAL) || 0) + count)
          break
        case 'politics':
        case 'influence':
        case 'power':
          typeScores.set(GroupType.FACTION, (typeScores.get(GroupType.FACTION) || 0) + count)
          break
      }
    })
    let maxScore = 0
    let bestType = GroupType.SOCIAL
    typeScores.forEach((score, type) => {
      if (score > maxScore) {
        maxScore = score
        bestType = type
      }
    })
    return bestType
  }
  /**
   * Initiate a group decision-making process
   */
  public initiateGroupDecision(
    groupId: str,
    type: str,
    description: str,
    options: List[string],
    durationMs: float = 5 * 60 * 1000 
  ): str {
    const group = this.groupManager.getGroup(groupId)
    if (!group) throw new Error(`Group ${groupId} not found`)
    const decision: \'GroupDecision\' = {
      id: `${groupId}_${Date.now()}`,
      type,
      description,
      options,
      votes: new Map(),
      deadline: Date.now() + durationMs
    }
    this.activeDecisions.set(decision.id, decision)
    return decision.id
  }
  /**
   * Cast a vote in an active group decision
   */
  public castVote(
    decisionId: str,
    memberId: str,
    vote: str
  ): bool {
    const decision = this.activeDecisions.get(decisionId)
    if (!decision) return false
    if (decision.deadline < Date.now()) return false
    if (!decision.options.includes(vote)) return false
    decision.votes.set(memberId, vote)
    return true
  }
  /**
   * Resolve a group decision based on votes and member influence
   */
  public resolveDecision(decisionId: str): str | undefined {
    const decision = this.activeDecisions.get(decisionId)
    if (!decision) return undefined
    if (decision.deadline > Date.now()) return undefined
    const weightedVotes = new Map<string, number>()
    decision.votes.forEach((vote, memberId) => {
      const weight = this.getMemberWeight(memberId)
      weightedVotes.set(vote, (weightedVotes.get(vote) || 0) + weight)
    })
    let maxVotes = 0
    let result: str | undefined = undefined
    weightedVotes.forEach((count, option) => {
      if (count > maxVotes) {
        maxVotes = count
        result = option
      }
    })
    decision.result = result
    this.activeDecisions.delete(decisionId)
    return result
  }
  /**
   * Get the voting weight of a group member based on their role
   */
  private getMemberWeight(memberId: str): float {
    const groups = this.groupManager.getMemberGroups(memberId)
    let maxWeight = 1 
    groups.forEach(group => {
      const member = group.members.get(memberId)
      if (!member) return
      const roleWeight = this.getRoleWeight(member.role)
      maxWeight = Math.max(maxWeight, roleWeight)
    })
    return maxWeight
  }
  /**
   * Get the weight multiplier for a group role
   */
  private getRoleWeight(role: GroupRole): float {
    switch (role) {
      case GroupRole.LEADER:
        return 3.0
      case GroupRole.DEPUTY:
        return 2.0
      case GroupRole.ADVISOR:
        return 1.5
      case GroupRole.MEMBER:
      default:
        return 1.0
    }
  }
  /**
   * Update group dynamics periodically
   */
  public update(npcs: List[NPCData]): void {
    this.checkGroupFormations(npcs)
    for (const [decisionId] of this.activeDecisions) {
      this.resolveDecision(decisionId)
    }
    this.groupManager.applyContributionDecay()
    const allGroups = this.groupManager.getAllGroups()
    allGroups.forEach(group => {
      if (this.groupManager.isGroupInactive(group.id)) {
        console.log(`Disbanding inactive group: ${group.name}`)
        this.groupManager.disbandGroup(group.id)
      }
    })
  }
} 