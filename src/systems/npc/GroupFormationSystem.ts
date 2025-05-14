import { 
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
} from '../../types/npc/group';
import { NPCData, NPCGoal, NPCInteraction } from '../../types/npc/npc';
import { GroupManager } from './GroupManager';
import { SpatialGrid } from '../../utils/SpatialGrid';
import { EventEmitter } from 'events';

interface GroupFormationScore {
  npcId: string;
  score: number;
  affinityScore: number;
  proximityScore: number;
  goalAlignmentScore: number;
  personalityScore: number;
  interactionScore: number;
}

export class GroupFormationSystem {
  private groupManager: GroupManager;
  private spatialGrid: SpatialGrid;
  private personalityCompatibility: PersonalityCompatibility;
  private gridSize: number;
  private eventEmitter: EventEmitter;
  
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
  ]);

  constructor(
    groupManager: GroupManager,
    gridSize: number = 100,
    personalityCompatibility?: PersonalityCompatibility
  ) {
    this.groupManager = groupManager;
    this.gridSize = gridSize;
    this.spatialGrid = new SpatialGrid(gridSize);
    this.eventEmitter = new EventEmitter();
    this.personalityCompatibility = personalityCompatibility || {
      traitWeights: new Map(),
      complementaryTraits: new Map(),
      minCompatibilityScore: 0.5
    };
  }

  private initializePersonalityCompatibility() {
    // Initialize trait weights and complementary traits
    const traitWeights = new Map<string, number>([
      ['leadership', 1.0],
      ['cooperation', 0.9],
      ['adaptability', 0.8],
      ['reliability', 0.7],
      ['creativity', 0.6]
    ]);

    const complementaryTraits = new Map<string, string[]>([
      ['leadership', ['cooperation', 'reliability']],
      ['creativity', ['reliability', 'adaptability']],
      ['cooperation', ['leadership', 'creativity']]
    ]);

    this.personalityCompatibility = {
      traitWeights,
      complementaryTraits,
      minCompatibilityScore: GROUP_CONSTANTS.MIN_PERSONALITY_COMPATIBILITY
    };
  }

  /**
   * Calculate personality compatibility score between two NPCs
   */
  private calculatePersonalityScore(npc: NPCData, others: NPCData[]): number {
    // Calculate personality compatibility with other members
    const compatibilities = others.map(other => {
      let score = 0;
      let totalWeight = 0;

      npc.personality.traits.forEach((value, trait) => {
        const weight = this.personalityCompatibility.traitWeights.get(trait) || 1;
        const otherValue = other.personality.traits.get(trait) || 0;
        
        // Check for complementary traits
        const complementary = this.personalityCompatibility.complementaryTraits.get(trait);
        if (complementary) {
          const complementaryScore = complementary.reduce((max, compTrait) => {
            const compValue = other.personality.traits.get(compTrait) || 0;
            return Math.max(max, 1 - Math.abs(value - compValue));
          }, 0);
          score += complementaryScore * weight;
        } else {
          // Direct trait comparison
          score += (1 - Math.abs(value - otherValue)) * weight;
        }
        
        totalWeight += weight;
      });

      return totalWeight > 0 ? score / totalWeight : 0;
    });

    return compatibilities.length > 0
      ? compatibilities.reduce((sum, score) => sum + score, 0) / compatibilities.length
      : 0;
  }

  /**
   * Calculate interaction history score between two NPCs
   */
  private calculateInteractionScore(npc: NPCData, others: NPCData[]): number {
    // Calculate interaction success rate with other members
    const interactionScores = others.map(other => {
      const history = npc.interactionHistory?.individual.get(other.id);
      if (!history) return 0;

      const total = history.positive + history.neutral + history.negative;
      if (total === 0) return 0;

      const successRate = (history.positive + history.neutral * 0.5) / total;
      const recency = Math.exp(
        -(Date.now() - history.lastInteraction) / 
        (30 * 24 * 60 * 60 * 1000)  // 30 days decay
      );

      return successRate * recency;
    });

    return interactionScores.length > 0
      ? interactionScores.reduce((sum, score) => sum + score, 0) / interactionScores.length
      : 0;
  }

  /**
   * Enhanced affinity score calculation
   */
  private calculateAffinityScore(npc: NPCData, others: NPCData[]): number {
    // Calculate average affinity with other members
    const affinities = others.map(other => {
      const relationshipScore = npc.relationships?.get(other.id)?.score || 0;
      const factionAlignment = this.calculateFactionAlignment(npc, other);
      const sharedHistory = this.calculateSharedHistory(npc, other);
      
      return (
        relationshipScore * 0.5 +
        factionAlignment * 0.3 +
        sharedHistory * 0.2
      );
    });

    return affinities.length > 0 
      ? affinities.reduce((sum, score) => sum + score, 0) / affinities.length
      : 0;
  }

  /**
   * Calculate proximity score based on NPCs' positions
   */
  private calculateProximityScore(npc: NPCData, others: NPCData[]): number {
    // Calculate average proximity score with other members
    const distances = others.map(other => {
      const distance = this.spatialGrid.getDistance(npc.position, other.position);
      return Math.max(0, 1 - (distance / this.gridSize));
    });

    return distances.length > 0
      ? distances.reduce((sum, score) => sum + score, 0) / distances.length
      : 0;
  }

  /**
   * Enhanced goal alignment score calculation
   */
  private calculateGoalAlignmentScore(npc: NPCData, others: NPCData[]): number {
    // Calculate goal alignment with other members
    const alignments = others.map(other => {
      const sharedGoals = npc.goals.filter(goal1 =>
        other.goals.some(goal2 => 
          goal1.type === goal2.type && 
          Math.abs(goal1.priority - goal2.priority) <= 0.2
        )
      );

      return sharedGoals.length / Math.max(npc.goals.length, 1);
    });

    return alignments.length > 0
      ? alignments.reduce((sum, score) => sum + score, 0) / alignments.length
      : 0;
  }

  private calculateFactionAlignment(npc1: NPCData, npc2: NPCData): number {
    if (npc1.faction === npc2.faction) return 1;
    // Additional faction relationship logic would go here
    return 0;
  }

  private calculateSharedHistory(npc1: NPCData, npc2: NPCData): number {
    const history1 = npc1.interactionHistory?.individual.get(npc2.id);
    const history2 = npc2.interactionHistory?.individual.get(npc1.id);
    
    if (!history1 || !history2) return 0;

    const total1 = history1.positive + history1.neutral + history1.negative;
    const total2 = history2.positive + history2.neutral + history2.negative;
    
    if (total1 === 0 || total2 === 0) return 0;

    const score1 = (history1.positive + history1.neutral * 0.5) / total1;
    const score2 = (history2.positive + history2.neutral * 0.5) / total2;

    return (score1 + score2) / 2;
  }

  /**
   * Find potential group members for an NPC
   */
  public findPotentialGroupMembers(
    initiatorNPC: NPCData,
    candidates: NPCData[],
    minScore: number = 60
  ): GroupFormationScore[] {
    const scores: GroupFormationScore[] = [];

    for (const candidate of candidates) {
      if (candidate.id === initiatorNPC.id) continue;

      const affinityScore = this.calculateAffinityScore(initiatorNPC, [candidate]);
      const proximityScore = this.calculateProximityScore(initiatorNPC, [candidate]);
      const goalAlignmentScore = this.calculateGoalAlignmentScore(initiatorNPC, [candidate]);

      // Weighted average of scores
      const totalScore = (
        affinityScore * 0.4 +
        proximityScore * 0.2 +
        goalAlignmentScore * 0.4
      );

      if (totalScore >= minScore) {
        scores.push({
          npcId: candidate.id,
          score: totalScore,
          affinityScore,
          proximityScore,
          goalAlignmentScore
        });
      }
    }

    // Sort by score in descending order
    return scores.sort((a, b) => b.score - a.score);
  }

  /**
   * Form a new group based on compatible NPCs
   */
  public formGroup(
    initiatorNPC: NPCData,
    candidates: NPCData[],
    groupType: GroupType,
    minMembers: number = 3,
    maxMembers: number = 10
  ): Group | null {
    // Find potential members
    const potentialMembers = this.findPotentialGroupMembers(initiatorNPC, candidates);
    
    // If we don't have enough compatible members, don't form the group
    if (potentialMembers.length < minMembers - 1) {
      return null;
    }

    // Select members (limited to maxMembers - 1 to account for initiator)
    const selectedMembers = potentialMembers.slice(0, maxMembers - 1);

    // Create the group
    const group = this.groupManager.createGroup(
      `${initiatorNPC.name}'s Group`,
      groupType,
      `Group formed by ${initiatorNPC.name} with ${selectedMembers.length} members`,
      initiatorNPC.id
    );

    // Add selected members
    for (const { npcId, score } of selectedMembers) {
      // Assign roles based on compatibility score
      const role = score >= 80 ? GroupRole.DEPUTY
        : score >= 70 ? GroupRole.ADVISOR
        : GroupRole.MEMBER;
      
      this.groupManager.addMember(group.id, npcId, role);
    }

    return group;
  }

  /**
   * Check if a group should be formed based on NPC interactions and compatibility
   */
  public shouldFormGroup(
    npcs: NPCData[],
    interactionThreshold: number = 5,
    compatibilityThreshold: number = 70
  ): { initiator: NPCData, candidates: NPCData[] } | null {
    for (const npc of npcs) {
      // Count recent interactions with other NPCs
      const interactions = new Map<string, number>();
      
      npc.recentInteractions.forEach((interaction: NPCInteraction) => {
        const otherId = interaction.participants.find((id: string) => id !== npc.id);
        if (otherId) {
          interactions.set(otherId, (interactions.get(otherId) || 0) + 1);
        }
      });

      // Filter NPCs with sufficient interactions
      const frequentInteractors = Array.from(interactions.entries())
        .filter(([_, count]) => count >= interactionThreshold)
        .map(([id]) => npcs.find(n => n.id === id))
        .filter((n): n is NPCData => n !== undefined);

      if (frequentInteractors.length >= 2) {
        // Check compatibility with frequent interactors
        const compatibilityScores = this.findPotentialGroupMembers(
          npc,
          frequentInteractors,
          compatibilityThreshold
        );

        if (compatibilityScores.length >= 2) {
          return {
            initiator: npc,
            candidates: frequentInteractors
          };
        }
      }
    }

    return null;
  }

  /**
   * Update NPC positions in the spatial grid
   */
  public updateNPCPosition(npcId: string, x: number, y: number): void {
    this.spatialGrid.updateEntity(npcId, { x, y });
  }

  /**
   * Initiate group formation between two NPCs
   */
  private async initiateGroupFormation(
    npcId: string,
    targetId: string,
    groupType: GroupType
  ): Promise<void> {
    const npc = await this.groupManager.getNPC(npcId);
    const target = await this.groupManager.getNPC(targetId);
    
    if (!npc || !target) {
      throw new Error('One or both NPCs not found');
    }

    const group = this.formGroup(npc, [target], groupType);
    if (!group) {
      throw new Error('Failed to form group');
    }
  }

  /**
   * Add a member to an existing group
   */
  private async addMemberToGroup(
    groupId: string,
    npcId: string
  ): Promise<void> {
    const npc = await this.groupManager.getNPC(npcId);
    if (!npc) {
      throw new Error('NPC not found');
    }

    const group = this.groupManager.getGroup(groupId);
    if (!group) {
      throw new Error('Group not found');
    }

    // Calculate compatibility with current members
    const members = Array.from(group.members.values());
    const scores = this.findPotentialGroupMembers(npc, members);

    if (scores.length > 0 && scores[0].score >= 60) {
      this.groupManager.addMember(groupId, npcId, GroupRole.MEMBER);
    } else {
      throw new Error('NPC not compatible with group');
    }
  }

  /**
   * Set up resource sharing between NPCs
   */
  private async setupResourceSharing(
    npcId1: string,
    npcId2: string,
    resources: any
  ): Promise<void> {
    const npc1 = await this.groupManager.getNPC(npcId1);
    const npc2 = await this.groupManager.getNPC(npcId2);
    
    if (!npc1 || !npc2) {
      throw new Error('One or both NPCs not found');
    }

    // Implementation would depend on the resource system
    // This is a placeholder for the actual resource sharing logic
    console.log(`Setting up resource sharing between ${npcId1} and ${npcId2}`);
  }

  /**
   * Process a cooperation proposal between NPCs
   */
  public async processCooperation(
    npcId: string,
    targetId: string,
    proposal: any
  ): Promise<void> {
    try {
      // Update or create group relationships based on the cooperation proposal
      if (proposal.formGroup) {
        await this.initiateGroupFormation(npcId, targetId, proposal.groupType);
      } else if (proposal.joinGroup) {
        await this.addMemberToGroup(proposal.groupId, targetId);
      }

      // Process any additional cooperation effects
      if (proposal.sharedResources) {
        await this.setupResourceSharing(npcId, targetId, proposal.sharedResources);
      }
    } catch (error) {
      console.error('Error processing cooperation:', error);
      throw error;
    }
  }

  /**
   * Calculate optimal group size based on purpose and available resources
   */
  private calculateOptimalGroupSize(
    purpose: string,
    availableResources: Map<string, number>
  ): number {
    const recommendation = this.sizeRecommendations.get(purpose) || {
      min: GROUP_CONSTANTS.MIN_MEMBERS,
      optimal: 4,
      max: GROUP_CONSTANTS.MAX_MEMBERS,
      overhead: GROUP_CONSTANTS.MAX_COMMUNICATION_OVERHEAD,
      resourceRequirements: [],
      effectivenessMultiplier: 1.0
    };

    // Check resource constraints
    const maxByResources = recommendation.resourceRequirements.reduce((max, req) => {
      const available = availableResources.get(req.type) || 0;
      return Math.min(max, Math.floor(available / req.amountPerMember));
    }, recommendation.max);

    // Balance between optimal size and resource constraints
    return Math.min(
      maxByResources,
      Math.floor(recommendation.optimal * recommendation.effectivenessMultiplier)
    );
  }

  /**
   * Check if group formation should be triggered
   */
  private checkFormationTriggers(
    npcs: NPCData[],
    trigger: GroupFormationTrigger
  ): boolean {
    const { type, condition, priority } = trigger;

    switch (type) {
      case 'emergency':
        // Check for emergency conditions (e.g., threats, critical resource shortages)
        return this.evaluateEmergencyCondition(npcs, condition, Date.now());

      case 'resource':
        // Check for resource-based triggers (e.g., valuable resource discovery)
        return this.evaluateResourceCondition(npcs, condition, Date.now());

      case 'goal':
        // Check for shared goal opportunities
        return this.evaluateGoalCondition(npcs, condition, Date.now());

      case 'periodic':
        // Check for time-based triggers
        return this.evaluatePeriodicCondition(condition, Date.now());

      case 'social':
        // Check for social interaction patterns
        return this.evaluateSocialCondition(npcs, condition, Date.now());

      default:
        return false;
    }
  }

  private calculateFormationScore(
    npc: NPCData,
    potentialMembers: NPCData[],
    purpose: string
  ): GroupFormationScore {
    const affinityScore = this.calculateAffinityScore(npc, potentialMembers);
    const proximityScore = this.calculateProximityScore(npc, potentialMembers);
    const goalAlignmentScore = this.calculateGoalAlignmentScore(npc, potentialMembers);
    const personalityScore = this.calculatePersonalityScore(npc, potentialMembers);
    const interactionScore = this.calculateInteractionScore(npc, potentialMembers);

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
    );

    return {
      npcId: npc.id,
      score,
      affinityScore,
      proximityScore,
      goalAlignmentScore,
      personalityScore,
      interactionScore
    };
  }

  private async evaluateGroupFormation(
    initiatorNPC: NPCData,
    candidates: NPCData[],
    purpose: string,
    currentTime: number
  ): Promise<GroupFormationScore[]> {
    const scores: GroupFormationScore[] = [];

    for (const candidate of candidates) {
      if (candidate.id === initiatorNPC.id) continue;

      const score = this.calculateFormationScore(
        initiatorNPC,
        [candidate],
        purpose
      );
      scores.push(score);
    }

    return scores;
  }

  private async getNPCsFromMembers(members: GroupMember[]): Promise<NPCData[]> {
    const npcs: NPCData[] = [];
    for (const member of members) {
      const npc = await this.groupManager.getNPC(member.id);
      if (npc) {
        // Convert GroupMember to NPCData
        const relationships = new Map(
          Array.from(member.relationshipScores.entries())
            .map(([id, score]) => [id, { score }])
        );

        npcs.push({
          ...npc,
          id: member.id,
          relationships
        });
      }
    }
    return npcs;
  }

  /**
   * Process group lifecycle events
   */
  public async processGroupLifecycle(
    group: Group,
    dissolutionConditions: GroupDissolutionCondition[]
  ): Promise<void> {
    try {
      // Check each dissolution condition
      for (const condition of dissolutionConditions) {
        if (this.evaluateDissolutionCondition(group, condition)) {
          // Check if we're in grace period
          const gracePeriod = condition.gracePeriod || 0;
          const warningThreshold = condition.warningThreshold || condition.threshold;
          
          if (this.evaluateDissolutionCondition(group, {
            ...condition,
            threshold: warningThreshold
          })) {
            // Emit warning event
            this.emitGroupEvent(group.id, 'dissolution_warning', {
              condition: condition.type,
              timeRemaining: gracePeriod
            });

            // Wait for grace period
            if (gracePeriod > 0) {
              await new Promise(resolve => setTimeout(resolve, gracePeriod));
              
              // Re-check condition after grace period
              if (this.evaluateDissolutionCondition(group, condition)) {
                await this.dissolveGroup(group.id, condition.type);
              }
            } else {
              await this.dissolveGroup(group.id, condition.type);
            }
          }
        }
      }
    } catch (error) {
      console.error('Error processing group lifecycle:', error);
      throw error;
    }
  }

  /**
   * Dissolve a group and handle cleanup
   */
  private async dissolveGroup(
    groupId: string,
    reason: string
  ): Promise<void> {
    try {
      const group = this.groupManager.getGroup(groupId);
      if (!group) {
        throw new Error('Group not found');
      }

      // Notify all members
      group.members.forEach((member, memberId) => {
        this.emitGroupEvent(groupId, 'group_dissolved', {
          memberId,
          reason,
          groupData: group
        });
      });

      // Clean up resources
      await this.handleResourceDistribution(group);

      // Archive group data
      await this.archiveGroupData(group);

      // Remove group
      await this.groupManager.removeGroup(groupId);
    } catch (error) {
      console.error('Error dissolving group:', error);
      throw error;
    }
  }

  private async handleResourceDistribution(group: Group): Promise<void> {
    // Implementation would depend on the resource system
    // This is a placeholder for the actual resource distribution logic
    this.eventEmitter.emit('group:resourceDistribution', {
      groupId: group.id,
      resources: group.resources
    });
  }

  private async archiveGroupData(group: Group): Promise<void> {
    // Implementation would depend on the data persistence system
    // This is a placeholder for the actual archiving logic
    this.eventEmitter.emit('group:archive', {
      groupId: group.id,
      data: group
    });
  }

  private emitGroupEvent(
    groupId: string,
    eventType: string,
    data: any
  ): void {
    this.eventEmitter.emit(`group:${eventType}`, {
      groupId,
      ...data
    });
  }

  /**
   * Check if a group should be dissolved
   */
  private evaluateDissolutionCondition(
    group: Group,
    condition: GroupDissolutionCondition
  ): boolean {
    switch (condition.type) {
      case 'conflict':
        return this.evaluateConflictLevel(group) >= condition.threshold;

      case 'goalCompletion':
        return this.evaluateGoalCompletion(group) >= condition.threshold;

      case 'resourceDepletion':
        return this.evaluateResourceDepletion(group) >= condition.threshold;

      case 'inactivity':
        return this.evaluateInactivity(group) >= condition.threshold;

      case 'ineffectiveness':
        return this.evaluateIneffectiveness(group) >= condition.threshold;

      default:
        return false;
    }
  }

  private evaluateConflictLevel(group: Group): number {
    let conflictScore = 0;
    let totalRelationships = 0;

    // Calculate average negative relationship score
    group.members.forEach((member1, id1) => {
      group.members.forEach((member2, id2) => {
        if (id1 < id2) {  // Avoid counting relationships twice
          const score = member1.relationshipScores.get(id2) || 0;
          if (score < 0) {
            conflictScore += Math.abs(score);
          }
          totalRelationships++;
        }
      });
    });

    return totalRelationships > 0 ? 
      conflictScore / (totalRelationships * 10) : // Normalize to 0-1
      0;
  }

  private evaluateGoalCompletion(group: Group): number {
    if (!group.goals.length) return 1;  // No goals = complete

    const totalProgress = group.goals.reduce(
      (sum, goal) => sum + goal.progress,
      0
    );

    return totalProgress / (group.goals.length * 100);  // Normalize to 0-1
  }

  private evaluateResourceDepletion(group: Group): number {
    const { resources } = group;
    if (!resources) return 0;

    // Calculate resource depletion level
    const totalResources = Array.from(resources.assets.values())
      .reduce((sum, amount) => sum + amount, 0);
    const wealthDepletion = 1 - (resources.wealth / GROUP_CONSTANTS.MAX_WEALTH);
    
    return Math.max(
      wealthDepletion,
      totalResources === 0 ? 1 : 0
    );
  }

  private evaluateInactivity(group: Group): number {
    const now = Date.now();
    const inactivePeriod = now - group.lastActive;
    
    return Math.min(1, 
      inactivePeriod / GROUP_CONSTANTS.INACTIVITY_THRESHOLD
    );
  }

  private evaluateIneffectiveness(group: Group): number {
    // Calculate effectiveness based on goal progress rate and member contribution
    const averageContribution = Array.from(group.members.values())
      .reduce((sum, member) => sum + member.contributionScore, 0) / 
      group.members.size;

    const recentGoalProgress = group.goals
      .filter(goal => goal.progress > 0)
      .length / Math.max(1, group.goals.length);

    return 1 - ((averageContribution + recentGoalProgress) / 2);
  }

  private evaluateEmergencyCondition(
    npcs: NPCData[],
    condition: { type: string; threshold: number; timeWindow?: number },
    currentTime: number
  ): boolean {
    // Implementation would depend on threat detection system
    // This is a placeholder that always returns false
    return false;
  }

  private evaluateResourceCondition(
    npcs: NPCData[],
    condition: { type: string; threshold: number; timeWindow?: number },
    currentTime: number
  ): boolean {
    const resourceAvailability = npcs.reduce((total, npc) => {
      return total + (npc.economicData?.wealth || 0);
    }, 0) / npcs.length;

    return resourceAvailability >= condition.threshold;
  }

  private evaluateGoalCondition(
    npcs: NPCData[],
    condition: { type: string; threshold: number; timeWindow?: number },
    currentTime: number
  ): boolean {
    // Count NPCs with matching high-priority goals
    const goalCounts = new Map<string, number>();
    
    npcs.forEach(npc => {
      npc.goals.forEach(goal => {
        if (goal.priority >= condition.threshold) {
          goalCounts.set(goal.type, (goalCounts.get(goal.type) || 0) + 1);
        }
      });
    });

    // Check if any goal type has enough interested NPCs
    return Array.from(goalCounts.values()).some(count => 
      count >= GROUP_CONSTANTS.MIN_MEMBERS
    );
  }

  private evaluatePeriodicCondition(
    condition: { type: string; threshold: number; timeWindow?: number },
    currentTime: number
  ): boolean {
    if (!condition.timeWindow) return false;
    
    return (currentTime % condition.timeWindow) < condition.threshold;
  }

  private evaluateSocialCondition(
    npcs: NPCData[],
    condition: { type: string; threshold: number; timeWindow?: number },
    currentTime: number
  ): boolean {
    // Check recent social interactions
    const recentInteractions = npcs.reduce((count, npc) => {
      return count + npc.recentInteractions.length;
    }, 0) / npcs.length;

    return recentInteractions >= condition.threshold;
  }
} 