from typing import Any, Dict, List


  CompetingQuestGroup,
  CompetingQuestConfig,
  FactionTensionMetrics,
  FactionConflict,
  ConflictResolutionState,
  TensionUpdate,
  CompletedQuest,
  FactionQuestBranch
} from './types'
/**
 * Manages competing quests between different factions
 */
class CompetingQuestManager {
  private questGroups: Map<string, CompetingQuestGroup> = new Map()
  private tensionMetrics: Map<string, FactionTensionMetrics> = new Map()
  private historicalConflicts: List[FactionConflict] = []
  private tensionDecayInterval: NodeJS.Timeout | null = null
  constructor(
    private factionSystem: FactionQuestSystem,
    private consequenceSystem: ConsequenceSystem,
    private worldStateHandler: WorldStateHandler,
    private config: CompetingQuestConfig
  ) {
    this.startTensionDecay()
  }
  /**
   * Create a new competing quest group
   */
  createCompetingQuestGroup(
    originalQuest: FactionQuestTemplate,
    opposingFactions: List[FactionProfile]
  ): CompetingQuestGroup {
    const competingQuests = opposingFactions.map(faction =>
      this.factionSystem.createOpposingQuest(originalQuest, faction)
    )
    const allQuests = [originalQuest, ...competingQuests]
    const questsMap = new Map(allQuests.map(quest => [quest.id, quest]))
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
    }
    this.questGroups.set(group.id, group)
    return group
  }
  /**
   * Calculate initial tension between factions
   */
  private calculateInitialTension(
    originalFactionId: FactionType,
    opposingFactions: List[FactionProfile]
  ): float {
    const originalFaction = this.factionSystem.getFaction(originalFactionId)
    if (!originalFaction) return this.config.tensionThreshold
    const totalTension = opposingFactions.reduce((sum, opposing) => {
      const relationship = originalFaction.relationships.get(opposing.id) || 0
      return sum + Math.abs(Math.min(relationship, 0))
    }, 0)
    return Math.max(
      totalTension / opposingFactions.length,
      this.config.tensionThreshold
    )
  }
  /**
   * Record a conflict between factions
   */
  recordConflict(
    questGroup: CompetingQuestGroup,
    winningFaction: FactionType | null,
    worldStateChanges: List[WorldStateChange]
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
    }
    this.historicalConflicts.push(resolution)
    this.updateTensionMetrics(resolution)
    this.applyCascadingEffects(resolution)
    return resolution
  }
  /**
   * Apply cascading effects to allied factions
   */
  private applyCascadingEffects(resolution: ConflictResolutionState): void {
    if (!resolution.winningFaction) return
    const winningProfile = this.factionSystem.getFaction(resolution.winningFaction)
    if (!winningProfile) return
    const alliedFactions = Array.from(winningProfile.relationships.entries())
      .filter(([_, standing]) => standing > 30)
      .map(([factionId]) => factionId)
    const opposingFactions = resolution.affectedFactions.filter(
      factionId => factionId !== resolution.winningFaction
    )
    for (const alliedFaction of alliedFactions) {
      if (resolution.affectedFactions.includes(alliedFaction)) continue
      const alliedProfile = this.factionSystem.getFaction(alliedFaction)
      if (!alliedProfile) continue
      const alliedChange: WorldStateChange = {
        type: 'FACTION_ALLIANCE_BENEFIT' as WorldStateChangeType,
        description: `Benefited from ally ${resolution.winningFaction}'s victory`,
        value: 5, 
        affectedFactions: [alliedFaction],
        location: null,
        customData: Dict[str, Any]
      }
      this.worldStateHandler.applyWorldStateChange(alliedChange)
      for (const opposingFaction of opposingFactions) {
        const currentStanding = alliedProfile.relationships.get(opposingFaction) || 0
        alliedProfile.relationships.set(
          opposingFaction,
          Math.max(-100, currentStanding - 5) 
        )
        const metrics = this.getTensionMetrics(alliedFaction, opposingFaction)
        const tensionIncrease = 5 
        const update: TensionUpdate = {
          factionA: alliedFaction,
          factionB: opposingFaction,
          oldTension: metrics.currentTension,
          newTension: Math.min(100, metrics.currentTension + tensionIncrease),
          type: 'QUEST_COMPLETION',
          tensionChange: tensionIncrease,
          timestamp: Date.now(),
          reason: `Tension increased due to allied faction ${resolution.winningFaction}'s victory`
        }
        this.updateTensionMetricsWithUpdate(metrics, update)
      }
    }
  }
  /**
   * Create initial tension metrics for a pair of factions
   */
  private createInitialTensionMetrics(factions: List[FactionType]): FactionTensionMetrics {
    const now = Date.now()
    return {
      currentTension: this.config.tensionThreshold,
      historicalPeak: this.config.tensionThreshold,
      lastConflictTime: now,
      lastUpdateTimestamp: now,
      involvedFactions: factions,
      conflictHistory: [],
      updates: []
    }
  }
  /**
   * Update tension metrics with a new update
   */
  private updateTensionMetricsWithUpdate(
    metrics: FactionTensionMetrics,
    update: TensionUpdate
  ): void {
    metrics.currentTension = update.newTension
    metrics.historicalPeak = Math.max(metrics.historicalPeak, update.newTension)
    metrics.lastUpdateTimestamp = update.timestamp
    if (update.type === 'QUEST_COMPLETION') {
      metrics.lastConflictTime = update.timestamp
    }
    metrics.updates.push(update)
    metrics.conflictHistory.push({
      timestamp: update.timestamp,
      type: update.type,
      tensionChange: update.tensionChange
    })
  }
  /**
   * Update tension metrics based on conflict resolution
   */
  private updateTensionMetrics(resolution: ConflictResolutionState): void {
    const { affectedFactions, winningFaction } = resolution
    const timestamp = Date.now()
    for (let i = 0; i < affectedFactions.length; i++) {
      for (let j = i + 1; j < affectedFactions.length; j++) {
        const factionA = affectedFactions[i]
        const factionB = affectedFactions[j]
        const metrics = this.getTensionMetrics(factionA, factionB)
        const tensionChange = this.calculateTensionChange(
          factionA,
          factionB,
          winningFaction
        )
        const newTension = Math.max(
          0,
          metrics.currentTension + tensionChange
        )
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
        }
        metrics.currentTension = newTension
        metrics.historicalPeak = Math.max(
          metrics.historicalPeak,
          newTension
        )
        metrics.lastUpdateTimestamp = timestamp
        metrics.lastConflictTime = timestamp
        metrics.conflictHistory.push({
          timestamp,
          type: 'QUEST_COMPLETION',
          tensionChange
        })
        metrics.updates.push(update)
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
  ): float {
    if (!winningFaction) {
      return this.config.tensionThreshold * 0.5 
    }
    if (winningFaction === factionA || winningFaction === factionB) {
      return this.config.tensionThreshold 
    }
    return this.config.tensionThreshold * 0.25 
  }
  /**
   * Get a unique key for a pair of factions
   */
  private getFactionPairKey(factionA: FactionType, factionB: FactionType): str {
    return [factionA, factionB].sort().join('_')
  }
  /**
   * Get tension metrics for a pair of factions
   */
  private getTensionMetrics(factionA: FactionType, factionB: FactionType): FactionTensionMetrics {
    const key = this.getFactionPairKey(factionA, factionB)
    let metrics = this.tensionMetrics.get(key)
    if (!metrics) {
      metrics = this.createInitialTensionMetrics([factionA, factionB])
      this.tensionMetrics.set(key, metrics)
    }
    return metrics
  }
  /**
   * Get all historical conflicts
   */
  getHistoricalConflicts(): ConflictResolutionState[] {
    return [...this.historicalConflicts]
  }
  /**
   * Get conflicts filtered by faction
   */
  getFactionConflicts(factionId: FactionType): ConflictResolutionState[] {
    return this.historicalConflicts.filter(conflict =>
      conflict.affectedFactions.includes(factionId)
    ).sort((a, b) => b.timestamp - a.timestamp) 
  }
  /**
   * Get a specific quest group
   */
  getQuestGroup(groupId: str): CompetingQuestGroup | undefined {
    return this.questGroups.get(groupId)
  }
  /**
   * Get all quest groups
   */
  getAllQuestGroups(): CompetingQuestGroup[] {
    return Array.from(this.questGroups.values())
  }
  /**
   * Get quest groups involving a specific faction
   */
  getQuestGroupsByFaction(factionId: FactionType): CompetingQuestGroup[] {
    return Array.from(this.questGroups.values()).filter(group =>
      group.activeQuests.some(quest => quest.factionId === factionId)
    )
  }
  /**
   * Update quest group status
   */
  updateQuestGroupStatus(
    groupId: str,
    completedQuest: FactionQuestTemplate,
    worldStateChanges: List[WorldStateChange]
  ): void {
    const group = this.questGroups.get(groupId)
    if (!group) return
    group.activeQuests = group.activeQuests.filter(q => q.id !== completedQuest.id)
    const completedQuestRecord: CompletedQuest = {
      questId: completedQuest.id,
      factionId: completedQuest.factionId,
      completionTime: Date.now()
    }
    group.completedQuests.push(completedQuestRecord)
    if (group.completedQuests.length === 1) {
      group.winningFaction = completedQuest.factionId
      this.recordConflict(
        group,
        completedQuest.factionId,
        worldStateChanges
      )
      worldStateChanges.forEach(change => {
        this.worldStateHandler.applyWorldStateChange(change)
      })
      group.activeQuests.forEach(quest => {
        const failureChange: WorldStateChange = {
          type: 'QUEST_FAILURE',
          description: `Quest ${quest.id} failed due to competing quest completion`,
          value: -1,
          affectedFactions: [quest.factionId],
          location: null,
          customData: Dict[str, Any]
        }
        this.worldStateHandler.applyWorldStateChange(failureChange)
      })
      group.activeQuests = []
    }
    const allFactions = [
      group.originalQuest.factionId,
      ...group.competingQuests.map(q => q.factionId)
    ]
    for (let i = 0; i < allFactions.length; i++) {
      for (let j = i + 1; j < allFactions.length; j++) {
        const metrics = this.getTensionMetrics(allFactions[i], allFactions[j])
        if (metrics) {
          metrics.currentTension = Math.max(
            metrics.currentTension,
            this.config.tensionThreshold * 1.5
          )
        }
      }
    }
  }
  /**
   * Start tension decay interval
   */
  private startTensionDecay(): void {
    if (this.tensionDecayInterval) {
      clearInterval(this.tensionDecayInterval)
    }
    this.tensionDecayInterval = setInterval(() => {
      this.updateTensionDecay()
    }, this.config.tensionDecayInterval)
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
      customData: Dict[str, Any]
    }
    this.worldStateHandler.applyWorldStateChange(change)
    const factionAProfile = this.factionSystem.getFaction(factionA)
    const factionBProfile = this.factionSystem.getFaction(factionB)
    if (factionAProfile && factionBProfile) {
      const diplomaticChange: WorldStateChange = {
        type: 'DIPLOMATIC_OPPORTUNITY',
        description: `Diplomatic opportunity available between ${factionA} and ${factionB}`,
        value: 1,
        affectedFactions: [factionA, factionB],
        location: null,
        customData: Dict[str, Any]
      }
      this.worldStateHandler.applyWorldStateChange(diplomaticChange)
      if (this.shouldGenerateDiplomaticQuests(factionAProfile, factionBProfile)) {
        this.generateDiplomaticQuests(factionA, factionB)
      }
    }
  }
  /**
   * Check if diplomatic quests should be generated
   */
  private shouldGenerateDiplomaticQuests(
    factionA: FactionProfile,
    factionB: FactionProfile
  ): bool {
    const currentTension = this.getTensionMetrics(factionA.id, factionB.id).currentTension
    const relationship = factionA.relationships.get(factionB.id) || 0
    return currentTension <= this.config.diplomaticSettings.resourceExchangeThreshold &&
           relationship > -50 && 
           this.isDiplomaticFaction(factionA) && 
           !this.getQuestGroupsByFaction(factionA.id).some(group => 
             group.competingQuests.some(quest => quest.questType === 'DIPLOMATIC')
           )
  }
  private isDiplomaticFaction(faction: FactionProfile): bool {
    return true
  }
  private isDiplomaticQuest(quest: FactionQuestTemplate): bool {
    return quest.requiredConditions?.some(c => c.type === 'DIPLOMATIC') || false
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
      requirements: Dict[str, Any],
      factionRequirements: Dict[str, Any],
      factionRewards: Dict[str, Any],
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
      rewards: Dict[str, Any],
      consequences: [
        {
          type: 'FACTION_TENSION_CHANGE',
          description: `Reduced tension between ${factionA} and ${factionB}`,
          value: -20,
          affectedFactions: [factionA, factionB],
          location: null,
          customData: Dict[str, Any]
        }
      ]
    }
    this.createCompetingQuestGroup(
      baseTemplate,
      [this.factionSystem.getFaction(factionB)].filter(Boolean) as FactionProfile[]
    )
  }
  /**
   * Update tension decay for all faction relationships
   */
  private updateTensionDecay(): void {
    const now = Date.now()
    for (const [key, metrics] of this.tensionMetrics.entries()) {
      const [factionA, factionB] = key.split('_') as [FactionType, FactionType]
      const factionAProfile = this.factionSystem.getFaction(factionA)
      const factionBProfile = this.factionSystem.getFaction(factionB)
      if (!factionAProfile || !factionBProfile) continue
      const timeSinceConflict = now - (metrics.lastConflictTime || now)
      const decayMultiplier = Math.min(1, timeSinceConflict / (24 * 60 * 60 * 1000)) 
      const baseDecay = this.config.baseTensionDecayRate * decayMultiplier
      const factionAModifier = this.getFactionDecayModifier(factionAProfile)
      const factionBModifier = this.getFactionDecayModifier(factionBProfile)
      const decayAmount = baseDecay * (factionAModifier + factionBModifier) / 2
      const oldTension = metrics.currentTension
      const newTension = Math.max(0, oldTension - decayAmount)
      metrics.currentTension = newTension
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
      }
      metrics.updates.push(update)
      metrics.conflictHistory.push({
        timestamp: now,
        type: 'NATURAL_DECAY',
        tensionChange: newTension - oldTension
      })
      if (metrics.currentTension < this.config.tensionThreshold) {
        this.handleLowTensionState(factionA, factionB)
      }
    }
  }
  /**
   * Get faction-specific decay modifier based on faction profile
   */
  private getFactionDecayModifier(faction: FactionProfile): float {
    const tierModifier = 1 + (faction.tier * 0.1) 
    const diplomaticPreference = faction.questPreferences?.diplomacy || 1
    const preferenceModifier = 1 + (diplomaticPreference * 0.05) 
    return tierModifier * preferenceModifier
  }
  /**
   * Check if a quest is available based on tension and other factors
   */
  async checkQuestAvailability(
    questId: str,
    factionId: FactionType
  ): Promise<{ available: bool; reason?: str }> {
    const group = this.findQuestGroup(questId)
    if (!group) return { available: true } 
    const faction = this.factionSystem.getFaction(factionId)
    if (!faction) return { available: false, reason: 'Invalid faction' }
    const lastCompletedQuest = group.completedQuests.find(q => q.factionId === factionId)
    if (lastCompletedQuest) {
      const cooldownTime = Date.now() - this.config.questCooldownPeriod
      if (lastCompletedQuest.completionTime && lastCompletedQuest.completionTime > cooldownTime) {
        return {
          available: false,
          reason: `Quest on cooldown for ${Math.ceil((lastCompletedQuest.completionTime - cooldownTime) / 1000)} seconds`
        }
      }
    }
    const opposingFactions = group.activeQuests
      .filter(q => q.factionId !== factionId)
      .map(q => q.factionId)
    for (const opposingFaction of opposingFactions) {
      const metrics = this.getTensionMetrics(factionId, opposingFaction)
      if (metrics && metrics.currentTension >= this.config.questLockoutThreshold) {
        return {
          available: false,
          reason: `Tension too high with ${opposingFaction}`
        }
      }
      const relationship = faction.relationships.get(opposingFaction) || 0
      if (relationship <= -this.config.hostilityThreshold) {
        return {
          available: false,
          reason: `Hostile relationship with ${opposingFaction}`
        }
      }
    }
    const worldStateConditions = this.checkWorldStateConditions(group, factionId)
    if (!worldStateConditions.available) {
      return worldStateConditions
    }
    const hasActiveCompeting = group.activeQuests.some(quest => 
      quest.factionId !== factionId
    )
    if (hasActiveCompeting) {
      return {
        available: false,
        reason: 'Competing quest already active'
      }
    }
    return { available: true }
  }
  /**
   * Check world state conditions for quest availability
   */
  private checkWorldStateConditions(
    group: CompetingQuestGroup,
    factionId: FactionType
  ): { available: bool; reason?: str } {
    const territoryControl = this.worldStateHandler.getTerritoryControl()
    const questLocation = group.originalQuest.location
    if (questLocation && territoryControl.has(questLocation)) {
      const controllingFaction = territoryControl.get(questLocation)
      if (controllingFaction && controllingFaction !== factionId) {
        return {
          available: false,
          reason: `Territory controlled by ${controllingFaction}`
        }
      }
    }
    const requiredResources = group.originalQuest.requiredResources || []
    for (const resource of requiredResources) {
      const availability = this.worldStateHandler.getResourceAvailability(resource.id)
      if (availability < resource.amount) {
        return {
          available: false,
          reason: `Insufficient ${resource.id} in the region`
        }
      }
    }
    const conditions = this.worldStateHandler.getEnvironmentalConditions()
    const questConditions = group.originalQuest.requiredConditions || []
    for (const condition of questConditions) {
      if (!conditions[condition.type] || conditions[condition.type] !== condition.value) {
        return {
          available: false,
          reason: `Required condition not met: ${condition.type}`
        }
      }
    }
    return { available: true }
  }
  /**
   * Cancel competing quests when one is completed
   */
  private async cancelCompetingQuests(group: CompetingQuestGroup, winningFactionId: FactionType): Promise<void> {
    const competingQuests = group.activeQuests.filter(quest => 
      quest.factionId !== winningFactionId
    )
    for (const quest of competingQuests) {
      const change: WorldStateChange = {
        type: 'QUEST_CANCELLED',
        description: `Quest cancelled due to completion of competing quest by ${winningFactionId}`,
        value: this.config.questCancellationPenalty,
        affectedFactions: [quest.factionId],
        location: quest.location || null,
        customData: Dict[str, Any]
      }
      this.worldStateHandler.applyWorldStateChange(change)
      group.activeQuests = group.activeQuests.filter(q => q.id !== quest.id)
    }
    if (group.activeQuests.length === 0) {
      group.status = 'completed'
      group.winningFaction = winningFactionId
    }
    const affectedFactions = [
      group.originalQuest.factionId,
      ...group.competingQuests.map(q => q.factionId)
    ]
    for (let i = 0; i < affectedFactions.length; i++) {
      for (let j = i + 1; j < affectedFactions.length; j++) {
        const metrics = this.getTensionMetrics(affectedFactions[i], affectedFactions[j])
        const tensionIncrease = this.config.questCompletionTensionIncrease
        metrics.currentTension = Math.min(100, metrics.currentTension + tensionIncrease)
        metrics.historicalPeak = Math.max(metrics.historicalPeak, metrics.currentTension)
        metrics.lastConflictTime = Date.now()
        metrics.lastUpdateTimestamp = Date.now()
        const update: TensionUpdate = {
          timestamp: Date.now(),
          factionA: affectedFactions[i],
          factionB: affectedFactions[j],
          oldTension: metrics.currentTension - tensionIncrease,
          newTension: metrics.currentTension,
          tensionChange: tensionIncrease,
          type: 'QUEST_COMPLETION',
          reason: `Quest completion by ${winningFactionId}`
        }
        metrics.updates.push(update)
        metrics.conflictHistory.push({
          timestamp: Date.now(),
          type: 'QUEST_COMPLETION',
          tensionChange: tensionIncrease
        })
      }
    }
  }
  /**
   * Find the competing quest group for a quest
   */
  private findQuestGroup(questId: str): CompetingQuestGroup | null {
    for (const group of this.questGroups.values()) {
      if (group.quests.has(questId)) {
        return group
      }
    }
    return null
  }
  /**
   * Clean up resources when manager is no longer needed
   */
  dispose(): void {
    if (this.tensionDecayInterval) {
      clearInterval(this.tensionDecayInterval)
      this.tensionDecayInterval = null
    }
  }
  /**
   * Handle quest completion and apply consequences
   */
  private handleQuestCompletion(
    questId: str,
    factionId: FactionType,
    worldStateChanges: List[WorldStateChange]
  ): void {
    const group = this.findQuestGroup(questId)
    if (!group) return
    const completedQuest = group.competingQuests.find(q => q.id === questId)
    if (!completedQuest) return
    const questCompletionChange: WorldStateChange = {
      type: 'QUEST_COMPLETION' as WorldStateChangeType,
      description: `Quest ${questId} completed by faction ${factionId}`,
      value: 1,
      affectedFactions: [factionId],
      location: completedQuest.location || null,
      customData: Dict[str, Any]
    }
    worldStateChanges.push(questCompletionChange)
    this.updateQuestGroupStatus(group.id, completedQuest, worldStateChanges)
  }
  private handleQuestFailure(
    questId: str,
    factionId: FactionType
  ): void {
    const group = this.findQuestGroup(questId)
    if (!group) return
    const failureChange: WorldStateChange = {
      type: 'QUEST_FAILURE',
      description: `Quest ${questId} failed for faction ${factionId}`,
      value: -1,
      affectedFactions: [factionId],
      location: null,
      customData: Dict[str, Any]
    }
    this.worldStateHandler.applyWorldStateChange(failureChange)
  }
  /**
   * Initialize a new competing quest group
   */
  private initializeQuestGroup(originalQuest: FactionQuestTemplate): CompetingQuestGroup {
    const questsMap = new Map([[originalQuest.id, originalQuest]])
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
    }
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
    }
  }
  /**
   * Find allied factions for a given faction
   */
  private findAllyFactions(factionId: FactionType): FactionType[] {
    const allFactions = this.factionSystem.getAllFactions()
    return allFactions
      .filter(faction => 
        faction.id !== factionId && 
        this.factionSystem.getFactionRelationship(factionId, faction.id) >= this.config.allianceThreshold
      )
      .map(faction => faction.id)
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
  ): Promise<{ success: bool; stateChanges: List[WorldStateChange] }> {
    if (!objective.customData?.targetFaction || !objective.customData?.meetingType) {
      throw new Error('Invalid diplomatic meeting objective: missing required data')
    }
    const { targetFaction, meetingType } = objective.customData
    const currentTension = await this.getFactionTension(targetFaction)
    const meetingSuccessThreshold = this.config.diplomaticSettings.meetingSuccessThreshold
    const baseSuccessChance = 1 - (currentTension / 100)
    const meetingTypeModifier = this.getMeetingTypeModifier(meetingType)
    const finalSuccessChance = Math.min(Math.max(baseSuccessChance * meetingTypeModifier, 0.1), 0.9)
    const success = Math.random() <= finalSuccessChance
    const stateChanges: List[WorldStateChange] = []
    if (success) {
      stateChanges.push({
        type: 'DIPLOMATIC_AGREEMENT' as WorldStateChangeType,
        value: -this.config.diplomaticSettings.successfulMeetingBonus,
        description: `Successful diplomatic meeting with ${targetFaction}`,
        affectedFactions: [targetFaction as FactionType],
        location: objective.location || null,
        customData: Dict[str, Any]
        }
      })
      if (currentTension <= this.config.lowTensionThreshold) {
        stateChanges.push({
          type: 'DIPLOMATIC_OPPORTUNITY' as WorldStateChangeType,
          value: 1,
          description: `New diplomatic opportunity with ${targetFaction}`,
          affectedFactions: [targetFaction as FactionType],
          location: objective.location || null,
          customData: Dict[str, Any]
        })
      }
    } else {
      stateChanges.push({
        type: 'DIPLOMATIC_FAILURE' as WorldStateChangeType,
        value: this.config.diplomaticSettings.failedMeetingPenalty,
        description: `Failed diplomatic meeting with ${targetFaction}`,
        affectedFactions: [targetFaction as FactionType],
        location: objective.location || null,
        customData: Dict[str, Any]
        }
      })
    }
    return { success, stateChanges }
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
  ): Promise<{ success: bool; stateChanges: List[WorldStateChange] }> {
    if (!objective.customData?.targetFaction || !objective.customData?.resources) {
      throw new Error('Invalid resource exchange objective: missing required data')
    }
    const { targetFaction, resources } = objective.customData
    const stateChanges: List[WorldStateChange] = []
    let success = true
    for (const resource of resources as QuestResource[]) {
      const available = await this.checkResourceAvailability(resource)
      if (!available) {
        success = false
        break
      }
    }
    if (success) {
      for (const resource of resources as QuestResource[]) {
        stateChanges.push({
          type: 'RESOURCE_CHANGE' as WorldStateChangeType,
          value: resource.amount,
          description: `Exchanged ${resource.amount} ${resource.id} with ${targetFaction}`,
          affectedFactions: [targetFaction as FactionType],
          location: objective.location || null,
          customData: Dict[str, Any]],
              requestedResources: []
            }
          }
        })
      }
      const tensionReduction = this.config.diplomaticSettings.resourceExchangeBonus
      stateChanges.push({
        type: 'TENSION_DECREASE' as WorldStateChangeType,
        value: -tensionReduction,
        description: `Reduced tension with ${targetFaction} through resource exchange`,
        affectedFactions: [targetFaction as FactionType],
        location: objective.location || null,
        customData: Dict[str, Any]
      })
      const currentTension = await this.getFactionTension(targetFaction)
      if (currentTension <= this.config.allianceThreshold) {
        stateChanges.push({
          type: 'FACTION_ALLIANCE_OPPORTUNITY' as WorldStateChangeType,
          value: 1,
          description: `Alliance opportunity available with ${targetFaction}`,
          affectedFactions: [targetFaction as FactionType],
          location: objective.location || null,
          customData: Dict[str, Any]
        })
      }
    }
    return { success, stateChanges }
  }
  /**
   * Calculate modifier for different types of diplomatic meetings
   * @param meetingType Type of diplomatic meeting
   * @returns Success chance modifier
   */
  private getMeetingTypeModifier(meetingType: str): float {
    const modifiers = {
      PEACE_TALKS: 1.2,
      TRADE_NEGOTIATION: 1.1,
      ALLIANCE_DISCUSSION: 0.8,
      BORDER_DISPUTE: 0.7,
      CULTURAL_EXCHANGE: 1.3,
    } as const
    return modifiers[meetingType as keyof typeof modifiers] || 1.0
  }
  /**
   * Check if required resources are available for exchange
   * @param resource Resource requirement to check
   * @returns Whether the resource is available
   */
  private async checkResourceAvailability(resource: QuestResource): Promise<boolean> {
    return true
  }
  /**
   * Get current tension level with a faction
   * @param factionId Target faction
   * @returns Current tension level (0-100)
   */
  private async getFactionTension(factionId: str): Promise<number> {
    return 50
  }
} 