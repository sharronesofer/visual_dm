import { v4 as uuidv4 } from 'uuid';
import {
  Group,
  GroupMember,
  GroupRole,
  GroupType,
  GroupDecision,
  GroupDecisionType,
  GROUP_CONSTANTS
} from '../../core/interfaces/types/npc/group';
import { MemoryEvent, MemoryEventType } from '../../core/interfaces/types/npc/memory';
import { NPCData, StatisticalCrowdModel } from '../../core/interfaces/types/npc/npc';
import { SpatialGrid } from '../../utils/SpatialGrid';
import { EventBus } from '../../core/interfaces/types/events';
import { ResourceMonitor } from '../../core/performance/ResourceMonitor';
import { EmotionSystem } from './EmotionSystem';
import { ReputationSystem } from './ReputationSystem';
import { ReputationAuditLogger } from '../reputation/ReputationAuditLogger';

// export interface GroupManagerInterface {
//   getGroup(groupId: string): Group | undefined;
//   createGroup(name: string, type: GroupType, description: string, leaderId: string, leaderData: NPCData): Group;
//   addMember(groupId: string, member: NPCData): void;
//   removeMember(groupId: string, memberId: string): void;
//   getNPC(npcId: string): NPCData | undefined;
//   removeGroup(groupId: string): Promise<void>;
//   updateGroup(group: Group): void;
//   listGroups(): Group[];
//   getGroupsForNPC(npcId: string): Group[];
// }

export class GroupManager {
  private groups: Map<string, Group>;
  private npcToGroups: Map<string, Set<string>>; // npcId -> set of groupIds
  private crowdModels: Map<string, StatisticalCrowdModel> = new Map();
  private spatialGrid: SpatialGrid = new SpatialGrid(100);
  private lodDistances: [number, number] = [300, 150]; // [toStatistical, toIndividual]

  // --- Event-driven NPC update system ---
  private npcUpdateQueue: Array<{ npcId: string; priority: number }> = [];
  private updating: boolean = false;

  private npcs: Map<string, NPCData> = new Map();

  // --- Dynamic simulation fidelity system ---
  private importantNPCs: Set<string> = new Set();

  private emotionSystem = new EmotionSystem();
  private reputationSystem = new ReputationSystem();

  constructor() {
    this.groups = new Map();
    this.npcToGroups = new Map();
    // Subscribe to player movement events for event-driven LOD updates
    EventBus.getInstance().on('player:move' as any, (event: any) => {
      // TODO: Replace 'player:move' with the actual event type for player movement if different
      const pos = event?.position || event?.newPosition;
      if (pos && typeof pos.x === 'number' && typeof pos.y === 'number') {
        this.updateLODs(pos, this.lodDistances);
      }
    });
    // Periodically process LOD transitions for smooth blending
    setInterval(() => this.processTransitions(), 100);
    // Subscribe to NPC-related events
    EventBus.getInstance().on('npc:needsUpdate' as any, (event: any) => {
      // Schedule with high priority (e.g., 0)
      this.scheduleNPCUpdate(event.npcId, 0);
    });
    EventBus.getInstance().on('npc:proximityChange' as any, (event: any) => {
      // Schedule with priority based on proximity (e.g., event.priority)
      this.scheduleNPCUpdate(event.npcId, event.priority ?? 1);
    });
    EventBus.getInstance().on('npc:interaction' as any, (event: any) => {
      // Schedule with medium priority
      this.scheduleNPCUpdate(event.npcId, 2);
    });
    // Start periodic monitoring for dynamic LOD adjustment
    setInterval(() => {
      this.monitorAndAdjustLOD();
    }, 2000);
  }

  /**
   * Create a new group
   */
  public createGroup(
    name: string,
    type: GroupType,
    description: string,
    leaderId: string,
    leaderData: NPCData
  ): Group {
    const now = Date.now();
    const leaderMember: GroupMember = {
      ...leaderData,
      role: GroupRole.LEADER,
      joinedAt: now,
      contributionScore: 0,
      relationshipScores: new Map(),
      name: leaderData.name || 'Leader',
      faction: leaderData.faction || undefined,
      position: leaderData.position || { x: 0, y: 0 },
      // Add other required fields as needed
    };
    this.npcs.set(leaderId, leaderData);
    const group: Group = {
      id: uuidv4(),
      name,
      type,
      description,
      leaderId,
      members: new Map([[leaderId, leaderMember]]),
      createdAt: now,
      lastActive: now,
      reputation: GROUP_CONSTANTS.DEFAULT_REPUTATION,
      hierarchy: {
        leaderId,
        deputyIds: [],
        advisorIds: [],
        subgroups: [],
      },
      resources: {
        wealth: 0,
        territory: [],
        assets: new Map(),
        sharedInventory: new Map(),
        accessPermissions: new Map(),
      },
      goals: [],
      relationships: new Map(),
      factionAffiliation: undefined,
      activeDecisions: [],
      decisionHistory: [],
      meetingSchedule: undefined,
      disbandConditions: undefined, // Use undefined or provide required object if needed
      decisions: [],
      formationTime: now,
      dissolutionConditions: [],
    };
    this.groups.set(group.id, group);
    this.addNpcToGroupIndex(leaderId, group.id);
    return group;
  }

  /**
   * Add a member to a group
   */
  public addMember(
    groupId: string,
    memberData: NPCData,
    role: GroupRole = GroupRole.MEMBER
  ): boolean {
    const group = this.groups.get(groupId);
    if (!group) return false;
    const now = Date.now();
    const member: GroupMember = {
      ...memberData,
      role,
      joinedAt: now,
      contributionScore: 0,
      relationshipScores: new Map(),
      name: memberData.name || 'Member',
      faction: memberData.faction || undefined,
      position: memberData.position || { x: 0, y: 0 },
      // Add other required fields as needed
    };
    group.members.set(memberData.id, member);
    this.npcs.set(memberData.id, memberData);
    this.addNpcToGroupIndex(memberData.id, groupId);
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

    member.contributionScore = Math.max(0, Math.min(100, member.contributionScore + contributionDelta));
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

    const oldReputation = group.reputation;
    group.reputation = Math.max(
      GROUP_CONSTANTS.MIN_REPUTATION,
      Math.min(GROUP_CONSTANTS.MAX_REPUTATION, group.reputation + delta)
    );
    group.lastActive = Date.now();
    // Audit log
    ReputationAuditLogger.log({
      timestamp: new Date().toISOString(),
      sourceSystem: 'GroupManager',
      targetEntity: groupId,
      valueChange: group.reputation - oldReputation,
      context: `old: ${oldReputation}, new: ${group.reputation}, delta: ${delta}`,
      callingSystem: 'GroupManager.updateGroupReputation'
    });
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
          member.contributionScore *= (1 - GROUP_CONSTANTS.CONTRIBUTION_DECAY_RATE);
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

  /**
   * Create a new statistical crowd model from a set of NPC IDs and a central position
   */
  public createStatisticalCrowdModel(npcIds: string[], position: { x: number; y: number }): StatisticalCrowdModel {
    const id = `crowd_${Date.now()}_${Math.floor(Math.random() * 10000)}`;
    const density = npcIds.length; // For now, 1 NPC per area unit
    const averageMovement = { x: 0, y: 0 }; // Placeholder, can be computed from NPCs
    const dominantBehaviors: string[] = []; // Placeholder, can be computed from NPCs
    const model: StatisticalCrowdModel = {
      id,
      npcIds,
      position,
      density,
      averageMovement,
      dominantBehaviors,
      state: 'active',
      lastUpdate: Date.now(),
    };
    this.crowdModels.set(id, model);
    this.spatialGrid.addEntity(id, position.x, position.y);
    // Emit crowd-level emotion and reputation events
    const emotion = this.emotionSystem.processCrowdEmotion(model);
    const reputation = this.reputationSystem.processCrowdReputation(model, 'world'); // 'world' as placeholder target
    // TODO: Add 'crowd:emotionUpdate' and 'crowd:reputationUpdate' to EventMap for type safety
    // @ts-expect-error: Custom event type not in EventMap yet
    EventBus.getInstance().emit('crowd:emotionUpdate', { crowdId: id, emotion });
    // @ts-expect-error: Custom event type not in EventMap yet
    EventBus.getInstance().emit('crowd:reputationUpdate', { crowdId: id, reputation });
    return model;
  }

  /**
   * Update a statistical crowd model with new data
   */
  public updateStatisticalCrowdModel(crowdId: string, updates: Partial<StatisticalCrowdModel>): void {
    const model = this.crowdModels.get(crowdId);
    if (!model) return;
    Object.assign(model, updates);
    if (updates.position) {
      this.spatialGrid.updateEntity(crowdId, updates.position.x, updates.position.y);
    }
    model.lastUpdate = Date.now();
    // Emit updated crowd-level emotion and reputation events
    const emotion = this.emotionSystem.processCrowdEmotion(model);
    const reputation = this.reputationSystem.processCrowdReputation(model, 'world');
    // TODO: Add 'crowd:emotionUpdate' and 'crowd:reputationUpdate' to EventMap for type safety
    // @ts-expect-error: Custom event type not in EventMap yet
    EventBus.getInstance().emit('crowd:emotionUpdate', { crowdId: crowdId, emotion });
    // @ts-expect-error: Custom event type not in EventMap yet
    EventBus.getInstance().emit('crowd:reputationUpdate', { crowdId: crowdId, reputation });
  }

  /**
   * Dissolve a statistical crowd model and remove it from the system
   */
  public dissolveStatisticalCrowdModel(crowdId: string): boolean {
    const model = this.crowdModels.get(crowdId);
    if (!model) return false;
    this.crowdModels.delete(crowdId);
    this.spatialGrid.removeEntity(crowdId);
    // TODO: Add 'crowd:dissolved' to EventMap for type safety
    // @ts-expect-error: Custom event type not in EventMap yet
    EventBus.getInstance().emit('crowd:dissolved', { crowdId });
    return true;
  }

  /**
   * Get a statistical crowd model by ID
   */
  public getStatisticalCrowdModel(crowdId: string): StatisticalCrowdModel | undefined {
    return this.crowdModels.get(crowdId);
  }

  /**
   * Get all crowd models within a given radius of a center point
   */
  public getCrowdModelsInArea(center: { x: number; y: number }, radius: number): StatisticalCrowdModel[] {
    const ids = this.spatialGrid.getNearbyEntities(center, radius);
    return ids
      .map(id => this.crowdModels.get(id))
      .filter((model): model is StatisticalCrowdModel => !!model);
  }

  /**
   * Convert a set of NPCs to a statistical crowd model (for LOD pooling)
   */
  public convertNPCsToStatisticalModel(npcIds: string[]): StatisticalCrowdModel {
    // Compute central position as average
    const npcs = npcIds
      .map(id => this.getNPC(id))
      .filter((npc): npc is NPCData => !!npc);
    const positions = npcs.map(npc => npc.position);
    const count = positions.length;
    const center = positions.reduce((acc, pos) => ({ x: acc.x + pos.x, y: acc.y + pos.y }), { x: 0, y: 0 });
    const avgPos = count > 0 ? { x: center.x / count, y: center.y / count } : { x: 0, y: 0 };

    // Compute average movement vector
    const movements = npcs.map(npc => (npc as any).movement || { x: 0, y: 0 });
    const avgMovement = movements.length > 0
      ? movements.reduce((acc, m) => ({ x: acc.x + m.x, y: acc.y + m.y }), { x: 0, y: 0 })
      : { x: 0, y: 0 };
    if (movements.length > 0) {
      avgMovement.x /= movements.length;
      avgMovement.y /= movements.length;
    }

    // Compute dominant behaviors (most common currentBehavior string)
    const behaviorCounts: Record<string, number> = {};
    for (const npc of npcs) {
      const behavior = (npc as any).currentBehavior || 'idle';
      behaviorCounts[behavior] = (behaviorCounts[behavior] || 0) + 1;
    }
    const sortedBehaviors = Object.entries(behaviorCounts).sort((a, b) => b[1] - a[1]);
    const dominantBehaviors = sortedBehaviors.slice(0, 3).map(([behavior]) => behavior);

    // Create the statistical crowd model
    const model = this.createStatisticalCrowdModel(npcIds, avgPos);
    model.averageMovement = avgMovement;
    model.dominantBehaviors = dominantBehaviors;
    this.crowdModels.set(model.id, model);
    return model;
  }

  /**
   * Convert a statistical crowd model back to individual NPCs (for LOD unpooling)
   */
  public convertStatisticalModelToNPCs(crowdId: string): string[] {
    const model = this.getStatisticalCrowdModel(crowdId);
    if (!model) return [];
    this.dissolveStatisticalCrowdModel(crowdId);
    return model.npcIds;
  }

  /**
   * Update LODs for all NPCs and crowd models based on player position and LOD distances
   * lodDistances: [individualToStatistical, statisticalToIndividual]
   * - NPCs beyond individualToStatistical are pooled into a statistical model
   * - Statistical models within statisticalToIndividual are dissolved back to individuals
   */
  public updateLODs(playerPosition: { x: number; y: number }, lodDistances: [number, number]): void {
    const [toStatistical, toIndividual] = lodDistances;
    // 1. Pool distant NPCs into statistical models
    const cellSize = this.spatialGrid['cellSize'] || 100;
    const grid = new Map<string, string[]>(); // cellKey -> npcIds
    for (const [npcId, pos] of this.spatialGrid['entityPositions']) {
      const dist = Math.sqrt(
        Math.pow(pos.x - playerPosition.x, 2) +
        Math.pow(pos.y - playerPosition.y, 2)
      );
      if (dist > toStatistical) {
        const cellKey = this.spatialGrid['getCellKey'](pos.x, pos.y);
        if (!grid.has(cellKey)) grid.set(cellKey, []);
        grid.get(cellKey)!.push(npcId);
      }
    }
    for (const npcIds of grid.values()) {
      if (npcIds.length > 2) {
        const model = this.convertNPCsToStatisticalModel(npcIds);
        model.state = 'transitioning';
        (model as any).transitionStart = Date.now();
        npcIds.forEach(id => this.spatialGrid.removeEntity(id));
      }
    }
    // 2. Unpool statistical models that are now close to the player
    for (const [crowdId, model] of this.crowdModels.entries()) {
      const dist = Math.sqrt(
        Math.pow(model.position.x - playerPosition.x, 2) +
        Math.pow(model.position.y - playerPosition.y, 2)
      );
      if (dist < toIndividual && model.state !== 'transitioning') {
        model.state = 'transitioning';
        (model as any).transitionStart = Date.now();
        setTimeout(() => {
          const npcIds = this.convertStatisticalModelToNPCs(crowdId);
          npcIds.forEach(id => {
            const npc = this.getNPC(id);
            if (npc) this.spatialGrid.addEntity(id, npc.position.x, npc.position.y);
          });
        }, 500);
      }
    }
  }

  /**
   * Set the LOD thresholds for statistical pooling and unpooling
   */
  public setLODThresholds(toStatistical: number, toIndividual: number): void {
    this.lodDistances = [toStatistical, toIndividual];
  }

  /**
   * Process smooth transitions for crowd models (e.g., fade in/out, staged updates)
   */
  private processTransitions(): void {
    const now = Date.now();
    for (const [crowdId, model] of this.crowdModels.entries()) {
      if (model.state === 'transitioning' && (now - (model as any).transitionStart < 500)) {
        // Still transitioning, do nothing
        continue;
      }
      if (model.state === 'transitioning' && (now - (model as any).transitionStart >= 500)) {
        // Finalize transition
        model.state = 'active';
        delete (model as any).transitionStart;
      }
    }
  }

  /**
   * Schedule an NPC for update with a given priority (lower = higher priority).
   * If already in the queue, reprioritize.
   */
  public scheduleNPCUpdate(npcId: string, priority: number): void {
    const existing = this.npcUpdateQueue.find(entry => entry.npcId === npcId);
    if (existing) {
      existing.priority = Math.min(existing.priority, priority); // Use the highest priority
    } else {
      this.npcUpdateQueue.push({ npcId, priority });
    }
    // Sort by priority (lowest first)
    this.npcUpdateQueue.sort((a, b) => a.priority - b.priority);
    this.processNPCUpdateQueue();
  }

  /**
   * Process the NPC update queue, updating NPCs in priority order.
   * Ensures only one update loop runs at a time.
   */
  private async processNPCUpdateQueue(): Promise<void> {
    if (this.updating) return;
    this.updating = true;
    while (this.npcUpdateQueue.length > 0) {
      const { npcId } = this.npcUpdateQueue.shift()!;
      const npc = this.getNPC(npcId);
      if (npc) {
        // Call the NPC's update logic here (implement as needed)
        // Example: npc.updateState();
        // TODO: Integrate with actual NPC update logic
      }
      // Optionally: yield to event loop for responsiveness
      await new Promise(res => setTimeout(res, 0));
    }
    this.updating = false;
  }

  public getNPC(npcId: string): NPCData | undefined {
    return this.npcs.get(npcId);
  }

  /**
   * Set the list of important NPCs that should always be simulated at full fidelity.
   */
  public setImportantNPCs(ids: string[]): void {
    this.importantNPCs = new Set(ids);
  }

  /**
   * Monitor system resources and adjust LOD thresholds dynamically.
   * Called periodically (every 2 seconds).
   */
  private async monitorAndAdjustLOD(): Promise<void> {
    const metrics = await ResourceMonitor.getInstance()['gatherResourceMetrics']?.();
    if (!metrics) return;
    let [toStatistical, toIndividual] = this.lodDistances;
    // Adjust LOD distances based on CPU usage
    if (metrics.cpuUsage > 80) {
      // System under heavy load: increase LOD distances (more pooling)
      toStatistical = Math.min(toStatistical + 50, 1000);
      toIndividual = Math.min(toIndividual + 25, 500);
    } else if (metrics.cpuUsage < 50) {
      // System has headroom: decrease LOD distances (more detail)
      toStatistical = Math.max(toStatistical - 50, 100);
      toIndividual = Math.max(toIndividual - 25, 50);
    }
    // Clamp to sensible min/max
    this.lodDistances = [toStatistical, toIndividual];
  }
} 