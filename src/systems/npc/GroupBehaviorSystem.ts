import { NPCData, NPCGoal } from '../../types/npc/npc';
import { Group, GroupType, GroupRole } from '../../types/npc/group';
import { GroupManager } from './GroupManager';
import { GroupFormationSystem } from './GroupFormationSystem';
import { SpatialGrid } from '../../utils/SpatialGrid';
import { EventBus } from '../../core/interfaces/types/events';

interface GroupDecision {
  id: string;
  type: string;
  description: string;
  options: string[];
  votes: Map<string, string>;
  deadline: number;
  result?: string;
}

export class GroupBehaviorSystem {
  private groupManager: GroupManager;
  private formationSystem: GroupFormationSystem;
  private spatialGrid: SpatialGrid;
  private activeDecisions: Map<string, GroupDecision>;

  constructor(gridSize: number = 100) {
    this.groupManager = new GroupManager();
    this.formationSystem = new GroupFormationSystem(this.groupManager, gridSize);
    this.spatialGrid = new SpatialGrid(gridSize);
    this.activeDecisions = new Map();

    // Subscribe to POI evolution events for NPC integration
    EventBus.getInstance().on('poi:evolved', ({ poiId, poi, trigger, changes, version }) => {
      // Example: Log the event
      console.log(`[NPC Integration] POI evolved: ${poiId}, trigger: ${trigger}, changes:`, changes);
      // TODO: Update NPC routines, spawning, or behaviors based on evolved POI state
      // For example, if a settlement's population increases, spawn more NPCs or adjust routines
    });
  }

  /**
   * Update NPC positions in the spatial grid
   */
  public updateNPCPosition(npcId: string, x: number, y: number): void {
    this.spatialGrid.updateEntity(npcId, { x, y });
    this.formationSystem.updateNPCPosition(npcId, x, y);
  }

  /**
   * Check for potential group formations among NPCs
   */
  public checkGroupFormations(npcs: NPCData[]): void {
    const formationCheck = this.formationSystem.shouldFormGroup(npcs);
    if (formationCheck) {
      const { initiator, candidates } = formationCheck;

      // Determine most appropriate group type based on shared goals
      const groupType = this.determineGroupType(initiator, candidates);

      // Attempt to form the group
      const group = this.formationSystem.formGroup(
        initiator,
        candidates,
        groupType
      );

      if (group) {
        console.log(`New group formed: ${group.name} (${group.type})`);
      }
    }
  }

  /**
   * Determine the most appropriate group type based on NPC goals and traits
   */
  private determineGroupType(initiator: NPCData, candidates: NPCData[]): GroupType {
    const allNPCs = [initiator, ...candidates];
    const goalTypes = new Map<string, number>();

    // Count goal types across all NPCs
    allNPCs.forEach(npc => {
      npc.goals.forEach(goal => {
        goalTypes.set(goal.type, (goalTypes.get(goal.type) || 0) + 1);
      });
    });

    // Map common goal types to group types
    const typeScores = new Map<GroupType, number>();

    goalTypes.forEach((count, goalType) => {
      switch (goalType.toLowerCase()) {
        case 'trade':
        case 'profit':
        case 'business':
          typeScores.set(GroupType.TRADING, (typeScores.get(GroupType.TRADING) || 0) + count);
          break;
        case 'combat':
        case 'protection':
        case 'security':
          typeScores.set(GroupType.MERCENARY, (typeScores.get(GroupType.MERCENARY) || 0) + count);
          break;
        case 'craft':
        case 'create':
        case 'build':
          typeScores.set(GroupType.CRAFTING, (typeScores.get(GroupType.CRAFTING) || 0) + count);
          break;
        case 'explore':
        case 'quest':
        case 'adventure':
          typeScores.set(GroupType.ADVENTURING, (typeScores.get(GroupType.ADVENTURING) || 0) + count);
          break;
        case 'socialize':
        case 'network':
        case 'community':
          typeScores.set(GroupType.SOCIAL, (typeScores.get(GroupType.SOCIAL) || 0) + count);
          break;
        case 'politics':
        case 'influence':
        case 'power':
          typeScores.set(GroupType.FACTION, (typeScores.get(GroupType.FACTION) || 0) + count);
          break;
      }
    });

    // Return the group type with the highest score, defaulting to SOCIAL
    let maxScore = 0;
    let bestType = GroupType.SOCIAL;

    typeScores.forEach((score, type) => {
      if (score > maxScore) {
        maxScore = score;
        bestType = type;
      }
    });

    return bestType;
  }

  /**
   * Initiate a group decision-making process
   */
  public initiateGroupDecision(
    groupId: string,
    type: string,
    description: string,
    options: string[],
    durationMs: number = 5 * 60 * 1000 // 5 minutes default
  ): string {
    const group = this.groupManager.getGroup(groupId);
    if (!group) throw new Error(`Group ${groupId} not found`);

    const decision: GroupDecision = {
      id: `${groupId}_${Date.now()}`,
      type,
      description,
      options,
      votes: new Map(),
      deadline: Date.now() + durationMs
    };

    this.activeDecisions.set(decision.id, decision);
    return decision.id;
  }

  /**
   * Cast a vote in an active group decision
   */
  public castVote(
    decisionId: string,
    memberId: string,
    vote: string
  ): boolean {
    const decision = this.activeDecisions.get(decisionId);
    if (!decision) return false;

    if (decision.deadline < Date.now()) return false;
    if (!decision.options.includes(vote)) return false;

    decision.votes.set(memberId, vote);
    return true;
  }

  /**
   * Resolve a group decision based on votes and member influence
   */
  public resolveDecision(decisionId: string): string | undefined {
    const decision = this.activeDecisions.get(decisionId);
    if (!decision) return undefined;

    if (decision.deadline > Date.now()) return undefined;

    // Count weighted votes based on member roles
    const weightedVotes = new Map<string, number>();

    decision.votes.forEach((vote, memberId) => {
      const weight = this.getMemberWeight(memberId);
      weightedVotes.set(vote, (weightedVotes.get(vote) || 0) + weight);
    });

    // Find option with highest weighted votes
    let maxVotes = 0;
    let result: string | undefined = undefined;

    weightedVotes.forEach((count, option) => {
      if (count > maxVotes) {
        maxVotes = count;
        result = option;
      }
    });

    decision.result = result;
    this.activeDecisions.delete(decisionId);

    return result;
  }

  /**
   * Get the voting weight of a group member based on their role
   */
  private getMemberWeight(memberId: string): number {
    // Find the member's highest role across all groups
    const groups = this.groupManager.getMemberGroups(memberId);
    let maxWeight = 1; // Default weight

    groups.forEach(group => {
      const member = group.members.get(memberId);
      if (!member) return;

      const roleWeight = this.getRoleWeight(member.role);
      maxWeight = Math.max(maxWeight, roleWeight);
    });

    return maxWeight;
  }

  /**
   * Get the weight multiplier for a group role
   */
  private getRoleWeight(role: GroupRole): number {
    switch (role) {
      case GroupRole.LEADER:
        return 3.0;
      case GroupRole.DEPUTY:
        return 2.0;
      case GroupRole.ADVISOR:
        return 1.5;
      case GroupRole.MEMBER:
      default:
        return 1.0;
    }
  }

  /**
   * Update group dynamics periodically
   */
  public update(npcs: NPCData[]): void {
    // Check for potential new group formations
    this.checkGroupFormations(npcs);

    // Resolve completed decisions
    for (const [decisionId] of this.activeDecisions) {
      this.resolveDecision(decisionId);
    }

    // Update group member contributions
    this.groupManager.applyContributionDecay();

    // Check for inactive groups
    const allGroups = this.groupManager.getAllGroups();
    allGroups.forEach(group => {
      if (this.groupManager.isGroupInactive(group.id)) {
        console.log(`Disbanding inactive group: ${group.name}`);
        this.groupManager.disbandGroup(group.id);
      }
    });
  }
} 