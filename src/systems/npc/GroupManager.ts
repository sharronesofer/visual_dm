import { v4 as uuidv4 } from 'uuid';
import {
  Group,
  GroupMember,
  GroupRole,
  GroupType,
  GroupDecision,
  GroupDecisionType,
  GROUP_CONSTANTS
} from '../../types/npc/group';
import { MemoryEvent, MemoryEventType } from '../../types/npc/memory';
import { NPCData } from '../../types/npc/npc';

export interface GroupManager {
  getGroup(groupId: string): Group | undefined;
  createGroup(members: NPCData[]): Group;
  addMember(groupId: string, member: NPCData): void;
  removeMember(groupId: string, memberId: string): void;
  getNPC(npcId: string): NPCData | undefined;
  removeGroup(groupId: string): Promise<void>;
  updateGroup(group: Group): void;
  listGroups(): Group[];
  getGroupsForNPC(npcId: string): Group[];
}

export class GroupManager {
  private groups: Map<string, Group>;
  private npcToGroups: Map<string, Set<string>>; // npcId -> set of groupIds

  constructor() {
    this.groups = new Map();
    this.npcToGroups = new Map();
  }

  /**
   * Create a new group
   */
  public createGroup(
    name: string,
    type: GroupType,
    description: string,
    leaderId: string
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
    };

    // Add leader as first member
    const leaderMember: GroupMember = {
      id: leaderId,
      role: GroupRole.LEADER,
      joinedAt: group.createdAt,
      contribution: 100 // Leaders start with max contribution
    };

    group.members.set(leaderId, leaderMember);
    this.groups.set(group.id, group);

    return group;
  }

  /**
   * Add a member to a group
   */
  public addMember(
    groupId: string,
    memberId: string,
    role: GroupRole = GroupRole.MEMBER
  ): boolean {
    const group = this.groups.get(groupId);
    if (!group) return false;

    // Check if member already exists
    if (group.members.has(memberId)) return false;

    // Check if group is full
    if (group.members.size >= GROUP_CONSTANTS.MAX_MEMBERS) return false;

    const member: GroupMember = {
      id: memberId,
      role,
      joinedAt: Date.now(),
      contribution: 0
    };

    group.members.set(memberId, member);
    group.lastActive = Date.now();

    return true;
  }

  /**
   * Remove a member from a group
   */
  public removeMember(groupId: string, memberId: string): boolean {
    const group = this.groups.get(groupId);
    if (!group) return false;

    // Can't remove the leader
    if (memberId === group.leaderId) return false;

    const success = group.members.delete(memberId);
    if (success) {
      group.lastActive = Date.now();

      // Disband group if below minimum members
      if (group.members.size < GROUP_CONSTANTS.MIN_MEMBERS) {
        this.disbandGroup(groupId);
      }
    }

    return success;
  }

  /**
   * Update a member's role in a group
   */
  public updateMemberRole(
    groupId: string,
    memberId: string,
    newRole: GroupRole
  ): boolean {
    const group = this.groups.get(groupId);
    if (!group) return false;

    const member = group.members.get(memberId);
    if (!member) return false;

    // Can't change leader's role
    if (memberId === group.leaderId && newRole !== GroupRole.LEADER) return false;

    member.role = newRole;
    group.lastActive = Date.now();
    return true;
  }

  /**
   * Update a member's contribution score
   */
  public updateMemberContribution(
    groupId: string,
    memberId: string,
    contributionDelta: number
  ): boolean {
    const group = this.groups.get(groupId);
    if (!group) return false;

    const member = group.members.get(memberId);
    if (!member) return false;

    member.contribution = Math.max(0, Math.min(100, member.contribution + contributionDelta));
    group.lastActive = Date.now();
    return true;
  }

  /**
   * Get a group by ID
   */
  public getGroup(groupId: string): Group | undefined {
    return this.groups.get(groupId);
  }

  /**
   * Get all groups a member belongs to
   */
  public getMemberGroups(memberId: string): Group[] {
    return Array.from(this.groups.values())
      .filter(group => group.members.has(memberId));
  }

  /**
   * Disband a group
   */
  public disbandGroup(groupId: string): boolean {
    return this.groups.delete(groupId);
  }

  /**
   * Update group reputation
   */
  public updateGroupReputation(groupId: string, delta: number): boolean {
    const group = this.groups.get(groupId);
    if (!group) return false;

    group.reputation = Math.max(
      GROUP_CONSTANTS.MIN_REPUTATION,
      Math.min(GROUP_CONSTANTS.MAX_REPUTATION, group.reputation + delta)
    );
    group.lastActive = Date.now();
    return true;
  }

  /**
   * Check if a group is inactive
   */
  public isGroupInactive(groupId: string): boolean {
    const group = this.groups.get(groupId);
    if (!group) return true;

    const inactiveTime = Date.now() - group.lastActive;
    return inactiveTime > GROUP_CONSTANTS.INACTIVITY_THRESHOLD;
  }

  /**
   * Get all groups
   */
  public getAllGroups(): Group[] {
    return Array.from(this.groups.values());
  }

  /**
   * Get groups by type
   */
  public getGroupsByType(type: GroupType): Group[] {
    return Array.from(this.groups.values())
      .filter(group => group.type === type);
  }

  /**
   * Apply contribution decay to all groups
   */
  public applyContributionDecay(): void {
    for (const group of this.groups.values()) {
      for (const member of group.members.values()) {
        if (member.role !== GroupRole.LEADER) {
          member.contribution *= (1 - GROUP_CONSTANTS.CONTRIBUTION_DECAY_RATE);
        }
      }
    }
  }

  /**
   * Propose a new decision for the group
   */
  public proposeDecision(
    groupId: string,
    proposerId: string,
    type: GroupDecisionType,
    description: string,
    options: { description: string; weight: number }[],
    affectedMembers: string[] = []
  ): GroupDecision | null {
    const group = this.groups.get(groupId);
    if (!group || !group.members.has(proposerId)) {
      return null;
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
    };

    group.activeDecisions.push(decision);
    group.lastActive = Date.now();

    return decision;
  }

  /**
   * Vote on a group decision
   */
  public castVote(
    groupId: string,
    decisionId: string,
    voterId: string,
    optionId: string,
    support: boolean
  ): boolean {
    const group = this.groups.get(groupId);
    if (!group) return false;

    const decision = group.activeDecisions.find(d => d.id === decisionId);
    if (!decision || decision.status !== 'pending') return false;

    const voter = group.members.get(voterId);
    if (!voter) return false;

    const option = decision.options.find(o => o.id === optionId);
    if (!option) return false;

    // Remove any existing votes by this voter
    decision.options.forEach(opt => {
      opt.supporters = opt.supporters.filter(id => id !== voterId);
      opt.opposition = opt.opposition.filter(id => id !== voterId);
    });

    // Add new vote
    if (support) {
      option.supporters.push(voterId);
    } else {
      option.opposition.push(voterId);
    }

    // Check if decision can be resolved
    this.checkDecisionResolution(group, decision);

    group.lastActive = Date.now();
    return true;
  }

  /**
   * Update member influence based on activity
   */
  public updateMemberInfluence(
    groupId: string,
    npcId: string,
    amount: number,
    reason: string
  ): boolean {
    const group = this.groups.get(groupId);
    if (!group) return false;

    const member = group.members.get(npcId);
    if (!member) return false;

    member.influence = Math.max(0, Math.min(100, member.influence + amount));
    member.activityLog.push({
      id: uuidv4(),
      timestamp: Date.now(),
      type: MemoryEventType.FACTION_EVENT,
      importance: Math.abs(amount),
      participants: [npcId],
      details: {
        description: reason,
        emotionalImpact: amount > 0 ? 5 : -5
      },
      tags: ['influence_change', amount > 0 ? 'gain' : 'loss']
    });

    group.lastActive = Date.now();
    return true;
  }

  // Private helper methods

  private addNpcToGroupIndex(npcId: string, groupId: string): void {
    if (!this.npcToGroups.has(npcId)) {
      this.npcToGroups.set(npcId, new Set());
    }
    this.npcToGroups.get(npcId)?.add(groupId);
  }

  private removeNpcFromGroupIndex(npcId: string, groupId: string): void {
    const groups = this.npcToGroups.get(npcId);
    if (groups) {
      groups.delete(groupId);
      if (groups.size === 0) {
        this.npcToGroups.delete(npcId);
      }
    }
  }

  private calculateRequiredInfluence(type: GroupDecisionType, group: Group): number {
    switch (type) {
      case GroupDecisionType.LEADERSHIP_CHANGE:
        return 80;
      case GroupDecisionType.MEMBER_EXPULSION:
        return 70;
      case GroupDecisionType.ALLIANCE_FORMATION:
        return 60;
      case GroupDecisionType.GOAL_SETTING:
        return 50;
      default:
        return 40;
    }
  }

  private checkDecisionResolution(group: Group, decision: GroupDecision): void {
    const totalInfluence = Array.from(group.members.values())
      .reduce((sum, member) => sum + member.influence, 0);

    decision.options.forEach(option => {
      const supportInfluence = option.supporters
        .reduce((sum, id) => sum + (group.members.get(id)?.influence || 0), 0);
      const oppositionInfluence = option.opposition
        .reduce((sum, id) => sum + (group.members.get(id)?.influence || 0), 0);

      if (supportInfluence >= decision.requiredInfluence) {
        decision.status = 'approved';
        decision.outcome = option.description;
        this.implementDecision(group, decision, option);
      } else if (oppositionInfluence >= decision.requiredInfluence) {
        decision.status = 'rejected';
      }
    });

    if (decision.status !== 'pending') {
      group.activeDecisions = group.activeDecisions.filter(d => d.id !== decision.id);
      group.decisionHistory.push(decision);
    }
  }

  private implementDecision(group: Group, decision: GroupDecision, selectedOption: { id: string; description: string }): void {
    switch (decision.type) {
      case GroupDecisionType.LEADERSHIP_CHANGE:
        if (decision.affectedMembers.length > 0) {
          const newLeaderId = decision.affectedMembers[0];
          const oldLeaderId = group.leaderId;
          
          // Update roles
          const newLeader = group.members.get(newLeaderId);
          const oldLeaderMember = group.members.get(oldLeaderId);
          if (newLeader && oldLeaderMember) {
            newLeader.role = GroupRole.LEADER;
            oldLeaderMember.role = GroupRole.ADVISOR;
            
            // Update leader
            group.leaderId = newLeaderId;
          }
        }
        break;

      case GroupDecisionType.MEMBER_EXPULSION:
        decision.affectedMembers.forEach(memberId => {
          this.removeMember(group.id, memberId);
        });
        break;

      // Add more implementation logic for other decision types
      
      default:
        // Log unhandled decision type
        console.warn(`Unhandled decision type: ${decision.type}`);
    }
  }

  /**
   * Update relationship scores between group members
   */
  public updateRelationshipScores(groupId: string): void {
    const group = this.groups.get(groupId);
    if (!group) return;

    const members = Array.from(group.members.values());
    
    members.forEach(member => {
      members.forEach(otherMember => {
        if (member.id === otherMember.id) return;

        const currentScore = member.relationshipScores.get(otherMember.id) || 0;
        const decayedScore = currentScore * (1 - GROUP_CONSTANTS.RELATIONSHIP_DECAY_RATE);
        member.relationshipScores.set(otherMember.id, decayedScore);
      });
    });

    group.lastActive = Date.now();
  }

  /**
   * Process influence decay for inactive members
   */
  public processInfluenceDecay(groupId: string): void {
    const group = this.groups.get(groupId);
    if (!group) return;

    const now = Date.now();
    group.members.forEach((member, memberId) => {
      const lastActivity = member.activityLog[member.activityLog.length - 1]?.timestamp || member.joinedAt;
      const daysSinceActivity = (now - lastActivity) / (24 * 60 * 60 * 1000);
      
      if (daysSinceActivity > 1) {
        const decayAmount = member.influence * GROUP_CONSTANTS.INFLUENCE_DECAY_RATE * daysSinceActivity;
        this.updateMemberInfluence(
          groupId,
          memberId,
          -decayAmount,
          'Influence decay due to inactivity'
        );
      }
    });
  }

  /**
   * Manage and form subgroups based on member relationships and specializations
   */
  public manageSubgroups(groupId: string): void {
    const group = this.groups.get(groupId);
    if (!group) return;

    // Clear existing subgroups
    group.hierarchy.subgroups = [];

    // Group members by specialization
    const specializationGroups = new Map<string, string[]>();
    group.members.forEach((member, memberId) => {
      member.specializations.forEach(spec => {
        if (!specializationGroups.has(spec)) {
          specializationGroups.set(spec, []);
        }
        specializationGroups.get(spec)?.push(memberId);
      });
    });

    // Form subgroups for specializations with enough members
    specializationGroups.forEach((members, specialization) => {
      if (members.length >= GROUP_CONSTANTS.MIN_MEMBERS_FOR_SUBGROUP) {
        // Find member with highest influence as subgroup leader
        const leader = members.reduce((bestLeader, memberId) => {
          const member = group.members.get(memberId);
          const bestMember = group.members.get(bestLeader);
          return (member?.influence || 0) > (bestMember?.influence || 0) ? memberId : bestLeader;
        }, members[0]);

        group.hierarchy.subgroups.push({
          leaderId: leader,
          members: members.filter(id => id !== leader),
          specialization
        });
      }
    });
  }

  /**
   * Update group meeting schedule
   */
  public updateMeetingSchedule(
    groupId: string,
    frequency: 'daily' | 'weekly' | 'monthly',
    location: string
  ): boolean {
    const group = this.groups.get(groupId);
    if (!group) return false;

    const now = Date.now();
    let nextMeeting: number;

    switch (frequency) {
      case 'daily':
        nextMeeting = now + 24 * 60 * 60 * 1000;
        break;
      case 'weekly':
        nextMeeting = now + 7 * 24 * 60 * 60 * 1000;
        break;
      case 'monthly':
        nextMeeting = now + 30 * 24 * 60 * 60 * 1000;
        break;
    }

    group.meetingSchedule = {
      frequency,
      nextMeeting,
      location
    };

    return true;
  }

  /**
   * Process group resources and update access permissions
   */
  public manageResources(
    groupId: string,
    updates: {
      wealth?: number;
      territory?: string[];
      assets?: [string, number][];
      inventory?: [string, number][];
    }
  ): boolean {
    const group = this.groups.get(groupId);
    if (!group) return false;

    if (updates.wealth !== undefined) {
      group.resources.wealth = Math.max(0, group.resources.wealth + updates.wealth);
    }

    if (updates.territory) {
      group.resources.territory = [...new Set([...group.resources.territory, ...updates.territory])];
    }

    if (updates.assets) {
      updates.assets.forEach(([assetId, amount]) => {
        const current = group.resources.assets.get(assetId) || 0;
        group.resources.assets.set(assetId, Math.max(0, current + amount));
      });
    }

    if (updates.inventory) {
      updates.inventory.forEach(([itemId, amount]) => {
        const current = group.resources.sharedInventory.get(itemId) || 0;
        group.resources.sharedInventory.set(itemId, Math.max(0, current + amount));
      });
    }

    // Update access permissions based on roles
    const rolePermissions = new Map<GroupRole, Set<string>>([
      [GroupRole.LEADER, new Set(['all'])],
      [GroupRole.DEPUTY, new Set(['manage_inventory', 'view_assets', 'use_resources'])],
      [GroupRole.ADVISOR, new Set(['view_assets', 'suggest_allocation'])],
      [GroupRole.MEMBER, new Set(['use_resources'])],
      [GroupRole.RECRUIT, new Set(['view_inventory'])],
      [GroupRole.GUEST, new Set()]
    ]);

    group.resources.accessPermissions.clear();
    Array.from(group.resources.assets.keys()).concat(
      Array.from(group.resources.sharedInventory.keys())
    ).forEach(resourceId => {
      group.resources.accessPermissions.set(resourceId, new Set());
      group.members.forEach(member => {
        const permissions = rolePermissions.get(member.role);
        if (permissions?.has('all') || permissions?.has('use_resources')) {
          group.resources.accessPermissions.get(resourceId)?.add(member.id);
        }
      });
    });

    return true;
  }
} 