from typing import Any, Dict, List, Union



  Group,
  GroupMember,
  GroupRole,
  GroupType,
  GroupDecision,
  GroupDecisionType,
  GROUP_CONSTANTS
} from '../../types/npc/group'
class GroupManager:
    getGroup(groupId: Union[str): Group, None]
    createGroup(members: List[NPCData]): Group
    addMember(groupId: str, member: NPCData): None
    removeMember(groupId: str, memberId: str): None
    getNPC(npcId: Union[str): NPCData, None]
    removeGroup(groupId: str): Awaitable[None>
    updateGroup(group: Group): None
    listGroups(): List[Group]
    getGroupsForNPC(npcId: List[str): Group]
class GroupManager {
  private groups: Map<string, Group>
  private npcToGroups: Map<string, Set<string>> 
  constructor() {
    this.groups = new Map()
    this.npcToGroups = new Map()
  }
  /**
   * Create a new group
   */
  public createGroup(
    name: str,
    type: GroupType,
    description: str,
    leaderId: str
  ): Group {
    const group: Group = {
      id: uuidv4(),
      name,
      type,
      description,
      leaderId,
      members: new Map(),
      createdAt: Date.now(),
      lastActive: Date.now(),
      reputation: GROUP_CONSTANTS.DEFAULT_REPUTATION
    }
    const leaderMember: GroupMember = {
      id: leaderId,
      role: GroupRole.LEADER,
      joinedAt: group.createdAt,
      contribution: 100 
    }
    group.members.set(leaderId, leaderMember)
    this.groups.set(group.id, group)
    return group
  }
  /**
   * Add a member to a group
   */
  public addMember(
    groupId: str,
    memberId: str,
    role: GroupRole = GroupRole.MEMBER
  ): bool {
    const group = this.groups.get(groupId)
    if (!group) return false
    if (group.members.has(memberId)) return false
    if (group.members.size >= GROUP_CONSTANTS.MAX_MEMBERS) return false
    const member: GroupMember = {
      id: memberId,
      role,
      joinedAt: Date.now(),
      contribution: 0
    }
    group.members.set(memberId, member)
    group.lastActive = Date.now()
    return true
  }
  /**
   * Remove a member from a group
   */
  public removeMember(groupId: str, memberId: str): bool {
    const group = this.groups.get(groupId)
    if (!group) return false
    if (memberId === group.leaderId) return false
    const success = group.members.delete(memberId)
    if (success) {
      group.lastActive = Date.now()
      if (group.members.size < GROUP_CONSTANTS.MIN_MEMBERS) {
        this.disbandGroup(groupId)
      }
    }
    return success
  }
  /**
   * Update a member's role in a group
   */
  public updateMemberRole(
    groupId: str,
    memberId: str,
    newRole: GroupRole
  ): bool {
    const group = this.groups.get(groupId)
    if (!group) return false
    const member = group.members.get(memberId)
    if (!member) return false
    if (memberId === group.leaderId && newRole !== GroupRole.LEADER) return false
    member.role = newRole
    group.lastActive = Date.now()
    return true
  }
  /**
   * Update a member's contribution score
   */
  public updateMemberContribution(
    groupId: str,
    memberId: str,
    contributionDelta: float
  ): bool {
    const group = this.groups.get(groupId)
    if (!group) return false
    const member = group.members.get(memberId)
    if (!member) return false
    member.contribution = Math.max(0, Math.min(100, member.contribution + contributionDelta))
    group.lastActive = Date.now()
    return true
  }
  /**
   * Get a group by ID
   */
  public getGroup(groupId: str): Group | undefined {
    return this.groups.get(groupId)
  }
  /**
   * Get all groups a member belongs to
   */
  public getMemberGroups(memberId: str): Group[] {
    return Array.from(this.groups.values())
      .filter(group => group.members.has(memberId))
  }
  /**
   * Disband a group
   */
  public disbandGroup(groupId: str): bool {
    return this.groups.delete(groupId)
  }
  /**
   * Update group reputation
   */
  public updateGroupReputation(groupId: str, delta: float): bool {
    const group = this.groups.get(groupId)
    if (!group) return false
    group.reputation = Math.max(
      GROUP_CONSTANTS.MIN_REPUTATION,
      Math.min(GROUP_CONSTANTS.MAX_REPUTATION, group.reputation + delta)
    )
    group.lastActive = Date.now()
    return true
  }
  /**
   * Check if a group is inactive
   */
  public isGroupInactive(groupId: str): bool {
    const group = this.groups.get(groupId)
    if (!group) return true
    const inactiveTime = Date.now() - group.lastActive
    return inactiveTime > GROUP_CONSTANTS.INACTIVITY_THRESHOLD
  }
  /**
   * Get all groups
   */
  public getAllGroups(): Group[] {
    return Array.from(this.groups.values())
  }
  /**
   * Get groups by type
   */
  public getGroupsByType(type: GroupType): Group[] {
    return Array.from(this.groups.values())
      .filter(group => group.type === type)
  }
  /**
   * Apply contribution decay to all groups
   */
  public applyContributionDecay(): void {
    for (const group of this.groups.values()) {
      for (const member of group.members.values()) {
        if (member.role !== GroupRole.LEADER) {
          member.contribution *= (1 - GROUP_CONSTANTS.CONTRIBUTION_DECAY_RATE)
        }
      }
    }
  }
  /**
   * Propose a new decision for the group
   */
  public proposeDecision(
    groupId: str,
    proposerId: str,
    type: GroupDecisionType,
    description: str,
    options: Dict[str, Any][],
    affectedMembers: List[string] = []
  ): GroupDecision | null {
    const group = this.groups.get(groupId)
    if (!group || !group.members.has(proposerId)) {
      return null
    }
    const decision: GroupDecision = {
      id: uuidv4(),
      type,
      proposerId,
      timestamp: Date.now(),
      description,
      options: options.map(opt => ({
        id: uuidv4(),
        description: opt.description,
        supporters: [],
        opposition: [],
        weight: opt.weight
      })),
      status: 'pending',
      requiredInfluence: this.calculateRequiredInfluence(type, group),
      affectedMembers,
      votingDeadline: Date.now() + GROUP_CONSTANTS.MIN_VOTING_PERIOD
    }
    group.activeDecisions.push(decision)
    group.lastActive = Date.now()
    return decision
  }
  /**
   * Vote on a group decision
   */
  public castVote(
    groupId: str,
    decisionId: str,
    voterId: str,
    optionId: str,
    support: bool
  ): bool {
    const group = this.groups.get(groupId)
    if (!group) return false
    const decision = group.activeDecisions.find(d => d.id === decisionId)
    if (!decision || decision.status !== 'pending') return false
    const voter = group.members.get(voterId)
    if (!voter) return false
    const option = decision.options.find(o => o.id === optionId)
    if (!option) return false
    decision.options.forEach(opt => {
      opt.supporters = opt.supporters.filter(id => id !== voterId)
      opt.opposition = opt.opposition.filter(id => id !== voterId)
    })
    if (support) {
      option.supporters.push(voterId)
    } else {
      option.opposition.push(voterId)
    }
    this.checkDecisionResolution(group, decision)
    group.lastActive = Date.now()
    return true
  }
  /**
   * Update member influence based on activity
   */
  public updateMemberInfluence(
    groupId: str,
    npcId: str,
    amount: float,
    reason: str
  ): bool {
    const group = this.groups.get(groupId)
    if (!group) return false
    const member = group.members.get(npcId)
    if (!member) return false
    member.influence = Math.max(0, Math.min(100, member.influence + amount))
    member.activityLog.push({
      id: uuidv4(),
      timestamp: Date.now(),
      type: MemoryEventType.FACTION_EVENT,
      importance: Math.abs(amount),
      participants: [npcId],
      details: Dict[str, Any],
      tags: ['influence_change', amount > 0 ? 'gain' : 'loss']
    })
    group.lastActive = Date.now()
    return true
  }
  private addNpcToGroupIndex(npcId: str, groupId: str): void {
    if (!this.npcToGroups.has(npcId)) {
      this.npcToGroups.set(npcId, new Set())
    }
    this.npcToGroups.get(npcId)?.add(groupId)
  }
  private removeNpcFromGroupIndex(npcId: str, groupId: str): void {
    const groups = this.npcToGroups.get(npcId)
    if (groups) {
      groups.delete(groupId)
      if (groups.size === 0) {
        this.npcToGroups.delete(npcId)
      }
    }
  }
  private calculateRequiredInfluence(type: GroupDecisionType, group: Group): float {
    switch (type) {
      case GroupDecisionType.LEADERSHIP_CHANGE:
        return 80
      case GroupDecisionType.MEMBER_EXPULSION:
        return 70
      case GroupDecisionType.ALLIANCE_FORMATION:
        return 60
      case GroupDecisionType.GOAL_SETTING:
        return 50
      default:
        return 40
    }
  }
  private checkDecisionResolution(group: Group, decision: GroupDecision): void {
    const totalInfluence = Array.from(group.members.values())
      .reduce((sum, member) => sum + member.influence, 0)
    decision.options.forEach(option => {
      const supportInfluence = option.supporters
        .reduce((sum, id) => sum + (group.members.get(id)?.influence || 0), 0)
      const oppositionInfluence = option.opposition
        .reduce((sum, id) => sum + (group.members.get(id)?.influence || 0), 0)
      if (supportInfluence >= decision.requiredInfluence) {
        decision.status = 'approved'
        decision.outcome = option.description
        this.implementDecision(group, decision, option)
      } else if (oppositionInfluence >= decision.requiredInfluence) {
        decision.status = 'rejected'
      }
    })
    if (decision.status !== 'pending') {
      group.activeDecisions = group.activeDecisions.filter(d => d.id !== decision.id)
      group.decisionHistory.push(decision)
    }
  }
  private implementDecision(group: Group, decision: GroupDecision, selectedOption: Dict[str, Any]): void {
    switch (decision.type) {
      case GroupDecisionType.LEADERSHIP_CHANGE:
        if (decision.affectedMembers.length > 0) {
          const newLeaderId = decision.affectedMembers[0]
          const oldLeaderId = group.leaderId
          const newLeader = group.members.get(newLeaderId)
          const oldLeaderMember = group.members.get(oldLeaderId)
          if (newLeader && oldLeaderMember) {
            newLeader.role = GroupRole.LEADER
            oldLeaderMember.role = GroupRole.ADVISOR
            group.leaderId = newLeaderId
          }
        }
        break
      case GroupDecisionType.MEMBER_EXPULSION:
        decision.affectedMembers.forEach(memberId => {
          this.removeMember(group.id, memberId)
        })
        break
      default:
        console.warn(`Unhandled decision type: ${decision.type}`)
    }
  }
  /**
   * Update relationship scores between group members
   */
  public updateRelationshipScores(groupId: str): void {
    const group = this.groups.get(groupId)
    if (!group) return
    const members = Array.from(group.members.values())
    members.forEach(member => {
      members.forEach(otherMember => {
        if (member.id === otherMember.id) return
        const currentScore = member.relationshipScores.get(otherMember.id) || 0
        const decayedScore = currentScore * (1 - GROUP_CONSTANTS.RELATIONSHIP_DECAY_RATE)
        member.relationshipScores.set(otherMember.id, decayedScore)
      })
    })
    group.lastActive = Date.now()
  }
  /**
   * Process influence decay for inactive members
   */
  public processInfluenceDecay(groupId: str): void {
    const group = this.groups.get(groupId)
    if (!group) return
    const now = Date.now()
    group.members.forEach((member, memberId) => {
      const lastActivity = member.activityLog[member.activityLog.length - 1]?.timestamp || member.joinedAt
      const daysSinceActivity = (now - lastActivity) / (24 * 60 * 60 * 1000)
      if (daysSinceActivity > 1) {
        const decayAmount = member.influence * GROUP_CONSTANTS.INFLUENCE_DECAY_RATE * daysSinceActivity
        this.updateMemberInfluence(
          groupId,
          memberId,
          -decayAmount,
          'Influence decay due to inactivity'
        )
      }
    })
  }
  /**
   * Manage and form subgroups based on member relationships and specializations
   */
  public manageSubgroups(groupId: str): void {
    const group = this.groups.get(groupId)
    if (!group) return
    group.hierarchy.subgroups = []
    const specializationGroups = new Map<string, string[]>()
    group.members.forEach((member, memberId) => {
      member.specializations.forEach(spec => {
        if (!specializationGroups.has(spec)) {
          specializationGroups.set(spec, [])
        }
        specializationGroups.get(spec)?.push(memberId)
      })
    })
    specializationGroups.forEach((members, specialization) => {
      if (members.length >= GROUP_CONSTANTS.MIN_MEMBERS_FOR_SUBGROUP) {
        const leader = members.reduce((bestLeader, memberId) => {
          const member = group.members.get(memberId)
          const bestMember = group.members.get(bestLeader)
          return (member?.influence || 0) > (bestMember?.influence || 0) ? memberId : bestLeader
        }, members[0])
        group.hierarchy.subgroups.push({
          leaderId: leader,
          members: members.filter(id => id !== leader),
          specialization
        })
      }
    })
  }
  /**
   * Update group meeting schedule
   */
  public updateMeetingSchedule(
    groupId: str,
    frequency: 'daily' | 'weekly' | 'monthly',
    location: str
  ): bool {
    const group = this.groups.get(groupId)
    if (!group) return false
    const now = Date.now()
    let nextMeeting: float
    switch (frequency) {
      case 'daily':
        nextMeeting = now + 24 * 60 * 60 * 1000
        break
      case 'weekly':
        nextMeeting = now + 7 * 24 * 60 * 60 * 1000
        break
      case 'monthly':
        nextMeeting = now + 30 * 24 * 60 * 60 * 1000
        break
    }
    group.meetingSchedule = {
      frequency,
      nextMeeting,
      location
    }
    return true
  }
  /**
   * Process group resources and update access permissions
   */
  public manageResources(
    groupId: str,
    updates: Dict[str, Any]
  ): bool {
    const group = this.groups.get(groupId)
    if (!group) return false
    if (updates.wealth !== undefined) {
      group.resources.wealth = Math.max(0, group.resources.wealth + updates.wealth)
    }
    if (updates.territory) {
      group.resources.territory = [...new Set([...group.resources.territory, ...updates.territory])]
    }
    if (updates.assets) {
      updates.assets.forEach(([assetId, amount]) => {
        const current = group.resources.assets.get(assetId) || 0
        group.resources.assets.set(assetId, Math.max(0, current + amount))
      })
    }
    if (updates.inventory) {
      updates.inventory.forEach(([itemId, amount]) => {
        const current = group.resources.sharedInventory.get(itemId) || 0
        group.resources.sharedInventory.set(itemId, Math.max(0, current + amount))
      })
    }
    const rolePermissions = new Map<GroupRole, Set<string>>([
      [GroupRole.LEADER, new Set(['all'])],
      [GroupRole.DEPUTY, new Set(['manage_inventory', 'view_assets', 'use_resources'])],
      [GroupRole.ADVISOR, new Set(['view_assets', 'suggest_allocation'])],
      [GroupRole.MEMBER, new Set(['use_resources'])],
      [GroupRole.RECRUIT, new Set(['view_inventory'])],
      [GroupRole.GUEST, new Set()]
    ])
    group.resources.accessPermissions.clear()
    Array.from(group.resources.assets.keys()).concat(
      Array.from(group.resources.sharedInventory.keys())
    ).forEach(resourceId => {
      group.resources.accessPermissions.set(resourceId, new Set())
      group.members.forEach(member => {
        const permissions = rolePermissions.get(member.role)
        if (permissions?.has('all') || permissions?.has('use_resources')) {
          group.resources.accessPermissions.get(resourceId)?.add(member.id)
        }
      })
    })
    return true
  }
} 