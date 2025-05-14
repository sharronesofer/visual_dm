import { FactionType, FactionProfile } from '../../../types/factions/faction';
import { FactionQuestSystem } from '../FactionQuestSystem';
import { FactionQuestTemplate } from '../../factions/types';
import { ConsequenceSystem, WorldStateChange, WorldStateChangeType } from '../../consequences/ConsequenceSystem';
import { WorldStateHandler } from '../../consequences/WorldStateHandler';
import {
  CompetingQuestGroup,
  CompetingQuestConfig,
  FactionTensionMetrics,
  FactionConflict,
  ConflictResolutionState,
  TensionUpdate,
  CompletedQuest,
  FactionQuestBranch
} from './types';
import { QuestType, ObjectiveType, QuestObjective, QuestState } from '../../types';
import { QuestResource } from '../../resources/types';
import { WorldStateChangeEventType } from '../../consequences/types';

/**
 * Manages competing quests between different factions
 */
export class CompetingQuestManager {
  private questGroups: Map<string, CompetingQuestGroup> = new Map();
  private tensionMetrics: Map<string, FactionTensionMetrics> = new Map();
  private historicalConflicts: FactionConflict[] = [];
  private tensionDecayInterval: NodeJS.Timeout | null = null;

  constructor(
    private factionSystem: FactionQuestSystem,
    private consequenceSystem: ConsequenceSystem,
    private worldStateHandler: WorldStateHandler,
    private config: CompetingQuestConfig
  ) {
    this.startTensionDecay();
  }

  /**
   * Create a new competing quest group
   */
  createCompetingQuestGroup(
    originalQuest: FactionQuestTemplate,
    opposingFactions: FactionProfile[]
  ): CompetingQuestGroup {
    const competingQuests = opposingFactions.map(faction =>
      this.factionSystem.createOpposingQuest(originalQuest, faction)
    );

    const allQuests = [originalQuest, ...competingQuests];
    const questsMap = new Map(allQuests.map(quest => [quest.id, quest]));

    const group: CompetingQuestGroup = {
      id: `competing_${originalQuest.id}`,
      originalQuest,
      competingQuests,
      activeQuests: allQuests,
      completedQuests: [],
      winningFaction: null,
      tensionLevel: this.calculateInitialTension(originalQuest.factionId, opposingFactions),
      status: 'active',
      quests: questsMap
    };

    this.questGroups.set(group.id, group);
    return group;
  }

  /**
   * Calculate initial tension between factions
   */
  private calculateInitialTension(
    originalFactionId: FactionType,
    opposingFactions: FactionProfile[]
  ): number {
    const originalFaction = this.factionSystem.getFaction(originalFactionId);
    if (!originalFaction) return this.config.tensionThreshold;

    // Average the negative relationships between original faction and opposing factions
    const totalTension = opposingFactions.reduce((sum, opposing) => {
      const relationship = originalFaction.relationships.get(opposing.id) || 0;
      return sum + Math.abs(Math.min(relationship, 0));
    }, 0);

    return Math.max(
      totalTension / opposingFactions.length,
      this.config.tensionThreshold
    );
  }

  /**
   * Record a conflict between factions
   */
  recordConflict(
    questGroup: CompetingQuestGroup,
    winningFaction: FactionType | null,
    worldStateChanges: WorldStateChange[]
  ): ConflictResolutionState {
    const resolution: ConflictResolutionState = {
      questGroupId: questGroup.id,
      timestamp: Date.now(),
      winningFaction,
      worldStateChanges,
      affectedFactions: [
        questGroup.originalQuest.factionId,
        ...questGroup.competingQuests.map(q => q.factionId)
      ]
    };

    this.historicalConflicts.push(resolution);
    this.updateTensionMetrics(resolution);

    // Apply cascading effects to allied factions
    this.applyCascadingEffects(resolution);

    return resolution;
  }

  /**
   * Apply cascading effects to allied factions
   */
  private applyCascadingEffects(resolution: ConflictResolutionState): void {
    if (!resolution.winningFaction) return;

    const winningProfile = this.factionSystem.getFaction(resolution.winningFaction);
    if (!winningProfile) return;

    // Find allied factions (positive relationship)
    const alliedFactions = Array.from(winningProfile.relationships.entries())
      .filter(([_, standing]) => standing > 30)
      .map(([factionId]) => factionId);

    // Find opposing factions (negative relationship)
    const opposingFactions = resolution.affectedFactions.filter(
      factionId => factionId !== resolution.winningFaction
    );

    // Apply effects to allied factions
    for (const alliedFaction of alliedFactions) {
      // Skip if the allied faction was directly involved
      if (resolution.affectedFactions.includes(alliedFaction)) continue;

      const alliedProfile = this.factionSystem.getFaction(alliedFaction);
      if (!alliedProfile) continue;

      // Create positive world state change for allied faction
      const alliedChange: WorldStateChange = {
        type: 'FACTION_ALLIANCE_BENEFIT' as WorldStateChangeType,
        description: `Benefited from ally ${resolution.winningFaction}'s victory`,
        value: 5, // Small positive effect
        affectedFactions: [alliedFaction],
        location: null,
        customData: {
          type: 'ALLIANCE_VICTORY_BENEFIT' as WorldStateChangeEventType,
          timestamp: Date.now(),
          allyFaction: resolution.winningFaction,
          questGroupId: resolution.questGroupId,
          factions: [alliedFaction, resolution.winningFaction]
        }
      };
      this.worldStateHandler.applyWorldStateChange(alliedChange);

      // Update relationships with opposing factions
      for (const opposingFaction of opposingFactions) {
        const currentStanding = alliedProfile.relationships.get(opposingFaction) || 0;
        alliedProfile.relationships.set(
          opposingFaction,
          Math.max(-100, currentStanding - 5) // Small relationship penalty
        );

        // Get or create tension metrics
        const metrics = this.getTensionMetrics(alliedFaction, opposingFaction);
        
        const tensionIncrease = 5; // Small tension increase
        const update: TensionUpdate = {
          factionA: alliedFaction,
          factionB: opposingFaction,
          oldTension: metrics.currentTension,
          newTension: Math.min(100, metrics.currentTension + tensionIncrease),
          type: 'QUEST_COMPLETION',
          tensionChange: tensionIncrease,
          timestamp: Date.now(),
          reason: `Tension increased due to allied faction ${resolution.winningFaction}'s victory`
        };

        this.updateTensionMetricsWithUpdate(metrics, update);
      }
    }
  }

  /**
   * Create initial tension metrics for a pair of factions
   */
  private createInitialTensionMetrics(factions: FactionType[]): FactionTensionMetrics {
    const now = Date.now();
    return {
      currentTension: this.config.tensionThreshold,
      historicalPeak: this.config.tensionThreshold,
      lastConflictTime: now,
      lastUpdateTimestamp: now,
      involvedFactions: factions,
      conflictHistory: [],
      updates: []
    };
  }

  /**
   * Update tension metrics with a new update
   */
  private updateTensionMetricsWithUpdate(
    metrics: FactionTensionMetrics,
    update: TensionUpdate
  ): void {
    metrics.currentTension = update.newTension;
    metrics.historicalPeak = Math.max(metrics.historicalPeak, update.newTension);
    metrics.lastUpdateTimestamp = update.timestamp;
    
    if (update.type === 'QUEST_COMPLETION') {
      metrics.lastConflictTime = update.timestamp;
    }
    
    metrics.updates.push(update);
    metrics.conflictHistory.push({
      timestamp: update.timestamp,
      type: update.type,
      tensionChange: update.tensionChange
    });
  }

  /**
   * Update tension metrics based on conflict resolution
   */
  private updateTensionMetrics(resolution: ConflictResolutionState): void {
    const { affectedFactions, winningFaction } = resolution;
    const timestamp = Date.now();

    // Update tension for each pair of affected factions
    for (let i = 0; i < affectedFactions.length; i++) {
      for (let j = i + 1; j < affectedFactions.length; j++) {
        const factionA = affectedFactions[i];
        const factionB = affectedFactions[j];
        
        // Get or create tension metrics
        const metrics = this.getTensionMetrics(factionA, factionB);

        const tensionChange = this.calculateTensionChange(
          factionA,
          factionB,
          winningFaction
        );

        const newTension = Math.max(
          0,
          metrics.currentTension + tensionChange
        );

        const update: TensionUpdate = {
          timestamp,
          factionA,
          factionB,
          oldTension: metrics.currentTension,
          newTension,
          tensionChange,
          type: 'QUEST_COMPLETION',
          reason: winningFaction 
            ? `Conflict resolved with ${winningFaction} victorious`
            : 'Unresolved conflict increased tension'
        };

        // Update metrics
        metrics.currentTension = newTension;
        metrics.historicalPeak = Math.max(
          metrics.historicalPeak,
          newTension
        );
        metrics.lastUpdateTimestamp = timestamp;
        metrics.lastConflictTime = timestamp;

        // Record history
        metrics.conflictHistory.push({
          timestamp,
          type: 'QUEST_COMPLETION',
          tensionChange
        });

        metrics.updates.push(update);
      }
    }
  }

  /**
   * Calculate tension change between two factions based on conflict outcome
   */
  private calculateTensionChange(
    factionA: FactionType,
    factionB: FactionType,
    winningFaction: FactionType | null
  ): number {
    if (!winningFaction) {
      return this.config.tensionThreshold * 0.5; // Moderate increase for unresolved conflicts
    }

    if (winningFaction === factionA || winningFaction === factionB) {
      return this.config.tensionThreshold; // Higher increase when one faction wins
    }

    return this.config.tensionThreshold * 0.25; // Small increase for indirect conflict
  }

  /**
   * Get a unique key for a pair of factions
   */
  private getFactionPairKey(factionA: FactionType, factionB: FactionType): string {
    return [factionA, factionB].sort().join('_');
  }

  /**
   * Get tension metrics for a pair of factions
   */
  private getTensionMetrics(factionA: FactionType, factionB: FactionType): FactionTensionMetrics {
    const key = this.getFactionPairKey(factionA, factionB);
    let metrics = this.tensionMetrics.get(key);
    if (!metrics) {
      metrics = this.createInitialTensionMetrics([factionA, factionB]);
      this.tensionMetrics.set(key, metrics);
    }
    return metrics;
  }

  /**
   * Get all historical conflicts
   */
  getHistoricalConflicts(): ConflictResolutionState[] {
    return [...this.historicalConflicts];
  }

  /**
   * Get conflicts filtered by faction
   */
  getFactionConflicts(factionId: FactionType): ConflictResolutionState[] {
    return this.historicalConflicts.filter(conflict =>
      conflict.affectedFactions.includes(factionId)
    ).sort((a, b) => b.timestamp - a.timestamp); // Sort by most recent first
  }

  /**
   * Get a specific quest group
   */
  getQuestGroup(groupId: string): CompetingQuestGroup | undefined {
    return this.questGroups.get(groupId);
  }

  /**
   * Get all quest groups
   */
  getAllQuestGroups(): CompetingQuestGroup[] {
    return Array.from(this.questGroups.values());
  }

  /**
   * Get quest groups involving a specific faction
   */
  getQuestGroupsByFaction(factionId: FactionType): CompetingQuestGroup[] {
    return Array.from(this.questGroups.values()).filter(group =>
      group.activeQuests.some(quest => quest.factionId === factionId)
    );
  }

  /**
   * Update quest group status
   */
  updateQuestGroupStatus(
    groupId: string,
    completedQuest: FactionQuestTemplate,
    worldStateChanges: WorldStateChange[]
  ): void {
    const group = this.questGroups.get(groupId);
    if (!group) return;

    // Move completed quest to completedQuests array
    group.activeQuests = group.activeQuests.filter(q => q.id !== completedQuest.id);
    const completedQuestRecord: CompletedQuest = {
      questId: completedQuest.id,
      factionId: completedQuest.factionId,
      completionTime: Date.now()
    };
    group.completedQuests.push(completedQuestRecord);

    // If this was the first quest completed in the group, it's the winner
    if (group.completedQuests.length === 1) {
      group.winningFaction = completedQuest.factionId;
      
      // Record the conflict resolution
      this.recordConflict(
        group,
        completedQuest.factionId,
        worldStateChanges
      );

      // Apply world state changes
      worldStateChanges.forEach(change => {
        this.worldStateHandler.applyWorldStateChange(change);
      });

      // Cancel remaining active quests as they are now invalid
      group.activeQuests.forEach(quest => {
        const failureChange: WorldStateChange = {
          type: 'QUEST_FAILURE',
          description: `Quest ${quest.id} failed due to competing quest completion`,
          value: -1,
          affectedFactions: [quest.factionId],
          location: null,
          customData: {
            questId: quest.id,
            winningFaction: completedQuest.factionId
          }
        };
        this.worldStateHandler.applyWorldStateChange(failureChange);
      });
      
      // Clear active quests as they're no longer valid
      group.activeQuests = [];
    }

    // Update tension metrics for all involved factions
    const allFactions = [
      group.originalQuest.factionId,
      ...group.competingQuests.map(q => q.factionId)
    ];
    
    for (let i = 0; i < allFactions.length; i++) {
      for (let j = i + 1; j < allFactions.length; j++) {
        const metrics = this.getTensionMetrics(allFactions[i], allFactions[j]);
        if (metrics) {
          metrics.currentTension = Math.max(
            metrics.currentTension,
            this.config.tensionThreshold * 1.5
          );
        }
      }
    }
  }

  /**
   * Start tension decay interval
   */
  private startTensionDecay(): void {
    if (this.tensionDecayInterval) {
      clearInterval(this.tensionDecayInterval);
    }

    this.tensionDecayInterval = setInterval(() => {
      this.updateTensionDecay();
    }, this.config.tensionDecayInterval);
  }

  /**
   * Handle low tension state between factions
   */
  private handleLowTensionState(factionA: FactionType, factionB: FactionType): void {
    const change: WorldStateChange = {
      type: 'TENSION_DECREASE',
      description: `Tension between ${factionA} and ${factionB} has decreased significantly`,
      value: -1,
      affectedFactions: [factionA, factionB],
      location: null,
      customData: {
        type: 'TENSION_STATE_CHANGE',
        oldState: 'HIGH_TENSION',
        newState: 'LOW_TENSION',
        timestamp: Date.now()
      }
    };

    // Apply the world state change
    this.worldStateHandler.applyWorldStateChange(change);

    // Check for potential diplomatic opportunities
    const factionAProfile = this.factionSystem.getFaction(factionA);
    const factionBProfile = this.factionSystem.getFaction(factionB);

    if (factionAProfile && factionBProfile) {
      const diplomaticChange: WorldStateChange = {
        type: 'DIPLOMATIC_OPPORTUNITY',
        description: `Diplomatic opportunity available between ${factionA} and ${factionB}`,
        value: 1,
        affectedFactions: [factionA, factionB],
        location: null,
        customData: {
          type: 'DIPLOMATIC_EVENT',
          eventType: 'OPPORTUNITY',
          factions: [factionA, factionB],
          timestamp: Date.now()
        }
      };

      this.worldStateHandler.applyWorldStateChange(diplomaticChange);

      // Generate diplomatic quests if appropriate
      if (this.shouldGenerateDiplomaticQuests(factionAProfile, factionBProfile)) {
        this.generateDiplomaticQuests(factionA, factionB);
      }
    }
  }

  /**
   * Check if diplomatic quests should be generated
   */
  private shouldGenerateDiplomaticQuests(
    factionA: FactionProfile,
    factionB: FactionProfile
  ): boolean {
    const currentTension = this.getTensionMetrics(factionA.id, factionB.id).currentTension;
    const relationship = factionA.relationships.get(factionB.id) || 0;

    // Check if diplomatic quests are appropriate based on current state
    return currentTension <= this.config.diplomaticSettings.resourceExchangeThreshold &&
           relationship > -50 && // Not completely hostile
           this.isDiplomaticFaction(factionA) && // At least one faction should be diplomatic
           !this.getQuestGroupsByFaction(factionA.id).some(group => 
             group.competingQuests.some(quest => quest.questType === 'DIPLOMATIC')
           );
  }

  private isDiplomaticFaction(faction: FactionProfile): boolean {
    // Implementation would depend on your faction system
    // This is a placeholder that should be replaced with actual faction type checking logic
    return true;
  }

  private isDiplomaticQuest(quest: FactionQuestTemplate): boolean {
    // Implementation would depend on your quest system
    // This is a placeholder that should be replaced with actual quest type checking logic
    return quest.requiredConditions?.some(c => c.type === 'DIPLOMATIC') || false;
  }

  /**
   * Generate diplomatic quests between factions
   */
  private generateDiplomaticQuests(factionA: FactionType, factionB: FactionType): void {
    const baseTemplate: FactionQuestTemplate = {
      id: `diplomatic_${Date.now()}`,
      title: `Diplomatic Relations: ${factionA} and ${factionB}`,
      description: `Improve relations between ${factionA} and ${factionB} through diplomatic means`,
      type: 'DIPLOMATIC',
      questType: 'DIPLOMATIC',
      status: 'PENDING',
      difficulty: 3,
      factionId: factionA,
      requirements: {
        minimumLevel: 5,
        minimumReputation: 0,
        items: [],
        abilities: []
      },
      factionRequirements: {
        minimumStanding: -50,
        maximumStanding: 50,
        minimumReputation: 0,
        minimumTier: 0
      },
      factionRewards: {
        standingGain: 20,
        reputationGain: 100,
        specialRewards: ['DIPLOMATIC_TOKEN']
      },
      objectives: [
        {
          id: `obj_meeting_${Date.now()}`,
          type: 'DIPLOMATIC_MEETING',
          description: 'Arrange a diplomatic meeting between faction representatives',
          target: '1',
          amount: 1,
          completed: false
        },
        {
          id: `obj_exchange_${Date.now()}`,
          type: 'RESOURCE_EXCHANGE',
          description: 'Facilitate resource exchange between factions',
          target: '1',
          amount: 1,
          completed: false
        }
      ],
      factionObjectives: [],
      dialogue: [
        {
          text: `The tension between ${factionA} and ${factionB} has reached a critical point. We need your help to establish diplomatic relations.`,
          npcId: 'FACTION_DIPLOMAT',
          responses: [
            {
              text: 'I will help establish peace.',
              nextDialogueId: 'accepted'
            },
            {
              text: 'I cannot help at this time.',
              nextDialogueId: 'declined'
            }
          ]
        }
      ],
      rewards: {
        gold: 1000,
        experience: 500,
        items: ['PEACE_TREATY_DOCUMENT'],
        reputation: 100
      },
      consequences: [
        {
          type: 'FACTION_TENSION_CHANGE',
          description: `Reduced tension between ${factionA} and ${factionB}`,
          value: -20,
          affectedFactions: [factionA, factionB],
          location: null,
          customData: {
            type: 'TENSION_DECAY',
            factions: [factionA, factionB],
            timestamp: Date.now()
          }
        }
      ]
    };

    // Create the competing quest group with diplomatic focus
    this.createCompetingQuestGroup(
      baseTemplate,
      [this.factionSystem.getFaction(factionB)].filter(Boolean) as FactionProfile[]
    );
  }

  /**
   * Update tension decay for all faction relationships
   */
  private updateTensionDecay(): void {
    const now = Date.now();

    for (const [key, metrics] of this.tensionMetrics.entries()) {
      const [factionA, factionB] = key.split('_') as [FactionType, FactionType];
      
      // Get faction profiles
      const factionAProfile = this.factionSystem.getFaction(factionA);
      const factionBProfile = this.factionSystem.getFaction(factionB);
      
      if (!factionAProfile || !factionBProfile) continue;

      // Calculate time-based decay multiplier
      const timeSinceConflict = now - (metrics.lastConflictTime || now);
      const decayMultiplier = Math.min(1, timeSinceConflict / (24 * 60 * 60 * 1000)); // Max 1 day worth of decay

      // Apply faction-specific modifiers
      const baseDecay = this.config.baseTensionDecayRate * decayMultiplier;
      const factionAModifier = this.getFactionDecayModifier(factionAProfile);
      const factionBModifier = this.getFactionDecayModifier(factionBProfile);

      // Calculate final decay amount
      const decayAmount = baseDecay * (factionAModifier + factionBModifier) / 2;
      
      // Calculate new tension
      const oldTension = metrics.currentTension;
      const newTension = Math.max(0, oldTension - decayAmount);
      
      // Update tension
      metrics.currentTension = newTension;
      
      // Record the update
      const update: TensionUpdate = {
        timestamp: now,
        factionA,
        factionB,
        oldTension,
        newTension,
        tensionChange: newTension - oldTension,
        type: 'NATURAL_DECAY',
        reason: 'Natural tension decay over time',
        decayAmount
      };
      
      metrics.updates.push(update);
      
      // Add to conflict history
      metrics.conflictHistory.push({
        timestamp: now,
        type: 'NATURAL_DECAY',
        tensionChange: newTension - oldTension
      });
      
      // Trigger world state changes if tension drops below threshold
      if (metrics.currentTension < this.config.tensionThreshold) {
        this.handleLowTensionState(factionA, factionB);
      }
    }
  }

  /**
   * Get faction-specific decay modifier based on faction profile
   */
  private getFactionDecayModifier(faction: FactionProfile): number {
    // Higher tier factions have better diplomatic capabilities
    const tierModifier = 1 + (faction.tier * 0.1); // 10% increase per tier
    
    // Factions with more diplomatic quest preferences decay faster
    const diplomaticPreference = faction.questPreferences?.diplomacy || 1;
    const preferenceModifier = 1 + (diplomaticPreference * 0.05); // 5% increase per point
    
    return tierModifier * preferenceModifier;
  }

  /**
   * Check if a quest is available based on tension and other factors
   */
  async checkQuestAvailability(
    questId: string,
    factionId: FactionType
  ): Promise<{ available: boolean; reason?: string }> {
    const group = this.findQuestGroup(questId);
    if (!group) return { available: true }; // If not in a competing group, always available

    // Get the faction profile
    const faction = this.factionSystem.getFaction(factionId);
    if (!faction) return { available: false, reason: 'Invalid faction' };

    // Check cooldown period
    const lastCompletedQuest = group.completedQuests.find(q => q.factionId === factionId);
    if (lastCompletedQuest) {
      const cooldownTime = Date.now() - this.config.questCooldownPeriod;
      if (lastCompletedQuest.completionTime && lastCompletedQuest.completionTime > cooldownTime) {
        return {
          available: false,
          reason: `Quest on cooldown for ${Math.ceil((lastCompletedQuest.completionTime - cooldownTime) / 1000)} seconds`
        };
      }
    }

    // Check faction relationships and tension
    const opposingFactions = group.activeQuests
      .filter(q => q.factionId !== factionId)
      .map(q => q.factionId);

    for (const opposingFaction of opposingFactions) {
      // Check tension metrics
      const metrics = this.getTensionMetrics(factionId, opposingFaction);
      if (metrics && metrics.currentTension >= this.config.questLockoutThreshold) {
        return {
          available: false,
          reason: `Tension too high with ${opposingFaction}`
        };
      }

      // Check faction relationship
      const relationship = faction.relationships.get(opposingFaction) || 0;
      if (relationship <= -this.config.hostilityThreshold) {
        return {
          available: false,
          reason: `Hostile relationship with ${opposingFaction}`
        };
      }
    }

    // Check world state conditions
    const worldStateConditions = this.checkWorldStateConditions(group, factionId);
    if (!worldStateConditions.available) {
      return worldStateConditions;
    }

    // Check if there are active competing quests
    const hasActiveCompeting = group.activeQuests.some(quest => 
      quest.factionId !== factionId
    );

    if (hasActiveCompeting) {
      return {
        available: false,
        reason: 'Competing quest already active'
      };
    }

    return { available: true };
  }

  /**
   * Check world state conditions for quest availability
   */
  private checkWorldStateConditions(
    group: CompetingQuestGroup,
    factionId: FactionType
  ): { available: boolean; reason?: string } {
    // Check territory control
    const territoryControl = this.worldStateHandler.getTerritoryControl();
    const questLocation = group.originalQuest.location;
    
    if (questLocation && territoryControl.has(questLocation)) {
      const controllingFaction = territoryControl.get(questLocation);
      if (controllingFaction && controllingFaction !== factionId) {
        return {
          available: false,
          reason: `Territory controlled by ${controllingFaction}`
        };
      }
    }

    // Check resource requirements
    const requiredResources = group.originalQuest.requiredResources || [];
    for (const resource of requiredResources) {
      const availability = this.worldStateHandler.getResourceAvailability(resource.id);
      if (availability < resource.amount) {
        return {
          available: false,
          reason: `Insufficient ${resource.id} in the region`
        };
      }
    }

    // Check environmental conditions
    const conditions = this.worldStateHandler.getEnvironmentalConditions();
    const questConditions = group.originalQuest.requiredConditions || [];
    
    for (const condition of questConditions) {
      if (!conditions[condition.type] || conditions[condition.type] !== condition.value) {
        return {
          available: false,
          reason: `Required condition not met: ${condition.type}`
        };
      }
    }

    return { available: true };
  }

  /**
   * Cancel competing quests when one is completed
   */
  private async cancelCompetingQuests(group: CompetingQuestGroup, winningFactionId: FactionType): Promise<void> {
    // Filter out quests that belong to the winning faction
    const competingQuests = group.activeQuests.filter(quest => 
      quest.factionId !== winningFactionId
    );

    for (const quest of competingQuests) {
      // Create world state change for quest cancellation
      const change: WorldStateChange = {
        type: 'QUEST_CANCELLED',
        description: `Quest cancelled due to completion of competing quest by ${winningFactionId}`,
        value: this.config.questCancellationPenalty,
        affectedFactions: [quest.factionId],
        location: quest.location || null,
        customData: {
          questId: quest.id,
          groupId: group.id,
          winningFaction: winningFactionId,
          type: 'QUEST_CANCELLATION',
          timestamp: Date.now()
        }
      };

      // Apply the change
      this.worldStateHandler.applyWorldStateChange(change);

      // Remove from active quests
      group.activeQuests = group.activeQuests.filter(q => q.id !== quest.id);
    }

    // Update group status if all quests are handled
    if (group.activeQuests.length === 0) {
      group.status = 'completed';
      group.winningFaction = winningFactionId;
    }

    // Update tension metrics for all affected factions
    const affectedFactions = [
      group.originalQuest.factionId,
      ...group.competingQuests.map(q => q.factionId)
    ];

    for (let i = 0; i < affectedFactions.length; i++) {
      for (let j = i + 1; j < affectedFactions.length; j++) {
        const metrics = this.getTensionMetrics(affectedFactions[i], affectedFactions[j]);
        const tensionIncrease = this.config.questCompletionTensionIncrease;
        
        metrics.currentTension = Math.min(100, metrics.currentTension + tensionIncrease);
        metrics.historicalPeak = Math.max(metrics.historicalPeak, metrics.currentTension);
        metrics.lastConflictTime = Date.now();
        metrics.lastUpdateTimestamp = Date.now();

        // Record the update
        const update: TensionUpdate = {
          timestamp: Date.now(),
          factionA: affectedFactions[i],
          factionB: affectedFactions[j],
          oldTension: metrics.currentTension - tensionIncrease,
          newTension: metrics.currentTension,
          tensionChange: tensionIncrease,
          type: 'QUEST_COMPLETION',
          reason: `Quest completion by ${winningFactionId}`
        };

        metrics.updates.push(update);
        metrics.conflictHistory.push({
          timestamp: Date.now(),
          type: 'QUEST_COMPLETION',
          tensionChange: tensionIncrease
        });
      }
    }
  }

  /**
   * Find the competing quest group for a quest
   */
  private findQuestGroup(questId: string): CompetingQuestGroup | null {
    for (const group of this.questGroups.values()) {
      if (group.quests.has(questId)) {
        return group;
      }
    }
    return null;
  }

  /**
   * Clean up resources when manager is no longer needed
   */
  dispose(): void {
    if (this.tensionDecayInterval) {
      clearInterval(this.tensionDecayInterval);
      this.tensionDecayInterval = null;
    }
  }

  /**
   * Handle quest completion and apply consequences
   */
  private handleQuestCompletion(
    questId: string,
    factionId: FactionType,
    worldStateChanges: WorldStateChange[]
  ): void {
    const group = this.findQuestGroup(questId);
    if (!group) return;

    const completedQuest = group.competingQuests.find(q => q.id === questId);
    if (!completedQuest) return;

    // Create world state change for quest completion
    const questCompletionChange: WorldStateChange = {
      type: 'QUEST_COMPLETION' as WorldStateChangeType,
      description: `Quest ${questId} completed by faction ${factionId}`,
      value: 1,
      affectedFactions: [factionId],
      location: completedQuest.location || null,
      customData: {
        type: 'QUEST_COMPLETION' as WorldStateChangeEventType,
        timestamp: Date.now(),
        questId,
        winningFaction: factionId,
        factions: [factionId]
      }
    };

    worldStateChanges.push(questCompletionChange);
    this.updateQuestGroupStatus(group.id, completedQuest, worldStateChanges);
  }

  private handleQuestFailure(
    questId: string,
    factionId: FactionType
  ): void {
    const group = this.findQuestGroup(questId);
    if (!group) return;

    const failureChange: WorldStateChange = {
      type: 'QUEST_FAILURE',
      description: `Quest ${questId} failed for faction ${factionId}`,
      value: -1,
      affectedFactions: [factionId],
      location: null,
      customData: {
        type: 'QUEST_FAILURE',
        questId,
        timestamp: Date.now()
      }
    };

    this.worldStateHandler.applyWorldStateChange(failureChange);
  }

  /**
   * Initialize a new competing quest group
   */
  private initializeQuestGroup(originalQuest: FactionQuestTemplate): CompetingQuestGroup {
    const questsMap = new Map([[originalQuest.id, originalQuest]]);
    
    return {
      id: `group_${Date.now()}_${originalQuest.id}`,
      originalQuest,
      competingQuests: [],
      completedQuests: [],
      activeQuests: [originalQuest],
      winningFaction: null,
      tensionLevel: 0,
      status: 'active',
      quests: questsMap
    };
  }

  /**
   * Initialize tension metrics for a pair of factions
   */
  private initializeTensionMetrics(factionA: FactionType, factionB: FactionType): FactionTensionMetrics {
    return {
      currentTension: 0,
      historicalPeak: 0,
      lastConflictTime: Date.now(),
      lastUpdateTimestamp: Date.now(),
      involvedFactions: [factionA, factionB],
      conflictHistory: [],
      updates: []
    };
  }

  /**
   * Find allied factions for a given faction
   */
  private findAllyFactions(factionId: FactionType): FactionType[] {
    const allFactions = this.factionSystem.getAllFactions();
    return allFactions
      .filter(faction => 
        faction.id !== factionId && 
        this.factionSystem.getFactionRelationship(factionId, faction.id) >= this.config.allianceThreshold
      )
      .map(faction => faction.id);
  }

  /**
   * Handles a diplomatic meeting objective
   * @param objective The diplomatic meeting objective
   * @param questState Current state of the quest
   * @returns Success status and any state changes
   */
  private async handleDiplomaticMeeting(
    objective: QuestObjective,
    questState: QuestState
  ): Promise<{ success: boolean; stateChanges: WorldStateChange[] }> {
    if (!objective.customData?.targetFaction || !objective.customData?.meetingType) {
      throw new Error('Invalid diplomatic meeting objective: missing required data');
    }

    const { targetFaction, meetingType } = objective.customData;
    const currentTension = await this.getFactionTension(targetFaction);
    const meetingSuccessThreshold = this.config.diplomaticSettings.meetingSuccessThreshold;
    
    // Calculate success chance based on current tension and meeting type
    const baseSuccessChance = 1 - (currentTension / 100);
    const meetingTypeModifier = this.getMeetingTypeModifier(meetingType);
    const finalSuccessChance = Math.min(Math.max(baseSuccessChance * meetingTypeModifier, 0.1), 0.9);

    const success = Math.random() <= finalSuccessChance;
    const stateChanges: WorldStateChange[] = [];

    if (success) {
      stateChanges.push({
        type: 'DIPLOMATIC_AGREEMENT' as WorldStateChangeType,
        value: -this.config.diplomaticSettings.successfulMeetingBonus,
        description: `Successful diplomatic meeting with ${targetFaction}`,
        affectedFactions: [targetFaction as FactionType],
        location: objective.location || null,
        customData: {
          type: 'DIPLOMATIC_MEETING' as WorldStateChangeEventType,
          timestamp: Date.now(),
          factions: [targetFaction as FactionType],
          diplomaticOutcome: 'SUCCESS',
          meetingDetails: {
            location: objective.location || 'Unknown',
            participants: [targetFaction as FactionType],
            agenda: [meetingType],
            outcome: 'Successful diplomatic meeting'
          }
        }
      });

      if (currentTension <= this.config.lowTensionThreshold) {
        stateChanges.push({
          type: 'DIPLOMATIC_OPPORTUNITY' as WorldStateChangeType,
          value: 1,
          description: `New diplomatic opportunity with ${targetFaction}`,
          affectedFactions: [targetFaction as FactionType],
          location: objective.location || null,
          customData: {
            type: 'DIPLOMATIC_EVENT' as WorldStateChangeEventType,
            timestamp: Date.now(),
            eventType: 'OPPORTUNITY',
            factions: [targetFaction as FactionType]
          }
        });
      }
    } else {
      stateChanges.push({
        type: 'DIPLOMATIC_FAILURE' as WorldStateChangeType,
        value: this.config.diplomaticSettings.failedMeetingPenalty,
        description: `Failed diplomatic meeting with ${targetFaction}`,
        affectedFactions: [targetFaction as FactionType],
        location: objective.location || null,
        customData: {
          type: 'DIPLOMATIC_FAILURE' as WorldStateChangeEventType,
          timestamp: Date.now(),
          factions: [targetFaction as FactionType],
          diplomaticOutcome: 'FAILURE',
          meetingDetails: {
            location: objective.location || 'Unknown',
            participants: [targetFaction as FactionType],
            agenda: [meetingType],
            outcome: 'Failed diplomatic meeting'
          }
        }
      });
    }

    return { success, stateChanges };
  }

  /**
   * Handles a resource exchange objective
   * @param objective The resource exchange objective
   * @param questState Current state of the quest
   * @returns Success status and any state changes
   */
  private async handleResourceExchange(
    objective: QuestObjective,
    questState: QuestState
  ): Promise<{ success: boolean; stateChanges: WorldStateChange[] }> {
    if (!objective.customData?.targetFaction || !objective.customData?.resources) {
      throw new Error('Invalid resource exchange objective: missing required data');
    }

    const { targetFaction, resources } = objective.customData;
    const stateChanges: WorldStateChange[] = [];
    let success = true;

    // Verify resource availability
    for (const resource of resources as QuestResource[]) {
      const available = await this.checkResourceAvailability(resource);
      if (!available) {
        success = false;
        break;
      }
    }

    if (success) {
      // Process resource exchange
      for (const resource of resources as QuestResource[]) {
        stateChanges.push({
          type: 'RESOURCE_CHANGE' as WorldStateChangeType,
          value: resource.amount,
          description: `Exchanged ${resource.amount} ${resource.id} with ${targetFaction}`,
          affectedFactions: [targetFaction as FactionType],
          location: objective.location || null,
          customData: {
            type: 'RESOURCE_EXCHANGE' as WorldStateChangeEventType,
            timestamp: Date.now(),
            factions: [targetFaction as FactionType],
            resourceExchange: {
              offeredResources: [{ id: resource.id, amount: resource.amount }],
              requestedResources: []
            }
          }
        });
      }

      // Apply diplomatic benefits
      const tensionReduction = this.config.diplomaticSettings.resourceExchangeBonus;
      stateChanges.push({
        type: 'TENSION_DECREASE' as WorldStateChangeType,
        value: -tensionReduction,
        description: `Reduced tension with ${targetFaction} through resource exchange`,
        affectedFactions: [targetFaction as FactionType],
        location: objective.location || null,
        customData: {
          type: 'TENSION_DECAY' as WorldStateChangeEventType,
          timestamp: Date.now(),
          factions: [targetFaction as FactionType],
          tensionLevel: tensionReduction
        }
      });

      // Check for alliance opportunity
      const currentTension = await this.getFactionTension(targetFaction);
      if (currentTension <= this.config.allianceThreshold) {
        stateChanges.push({
          type: 'FACTION_ALLIANCE_OPPORTUNITY' as WorldStateChangeType,
          value: 1,
          description: `Alliance opportunity available with ${targetFaction}`,
          affectedFactions: [targetFaction as FactionType],
          location: objective.location || null,
          customData: {
            type: 'ALLIANCE_OPPORTUNITY' as WorldStateChangeEventType,
            timestamp: Date.now(),
            factions: [targetFaction as FactionType],
            eventType: 'OPPORTUNITY'
          }
        });
      }
    }

    return { success, stateChanges };
  }

  /**
   * Calculate modifier for different types of diplomatic meetings
   * @param meetingType Type of diplomatic meeting
   * @returns Success chance modifier
   */
  private getMeetingTypeModifier(meetingType: string): number {
    const modifiers = {
      PEACE_TALKS: 1.2,
      TRADE_NEGOTIATION: 1.1,
      ALLIANCE_DISCUSSION: 0.8,
      BORDER_DISPUTE: 0.7,
      CULTURAL_EXCHANGE: 1.3,
    } as const;
    return modifiers[meetingType as keyof typeof modifiers] || 1.0;
  }

  /**
   * Check if required resources are available for exchange
   * @param resource Resource requirement to check
   * @returns Whether the resource is available
   */
  private async checkResourceAvailability(resource: QuestResource): Promise<boolean> {
    // Implementation would depend on your resource management system
    // This is a placeholder that should be replaced with actual resource checking logic
    return true;
  }

  /**
   * Get current tension level with a faction
   * @param factionId Target faction
   * @returns Current tension level (0-100)
   */
  private async getFactionTension(factionId: string): Promise<number> {
    // Implementation would depend on your faction management system
    // This is a placeholder that should be replaced with actual tension checking logic
    return 50;
  }
} 