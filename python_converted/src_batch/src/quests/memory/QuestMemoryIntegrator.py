from typing import Any, Dict, List



class QuestMemoryOptions:
    baseImportance: float
    emotionalImpact: float
    memoryDecayRate: float
    relevanceThreshold: float
class QuestMemoryIntegrator {
  private memoryManager: MemoryManager
  private consequenceSystem: ConsequenceSystem
  private factionQuestSystem: FactionQuestSystem
  private options: \'QuestMemoryOptions\'
  constructor(
    memoryManager: MemoryManager,
    consequenceSystem: ConsequenceSystem,
    factionQuestSystem: FactionQuestSystem,
    options?: Partial<QuestMemoryOptions>
  ) {
    this.memoryManager = memoryManager
    this.consequenceSystem = consequenceSystem
    this.factionQuestSystem = factionQuestSystem
    this.options = {
      baseImportance: 70, 
      emotionalImpact: 0.5, 
      memoryDecayRate: 0.1, 
      relevanceThreshold: 0.4, 
      ...options
    }
  }
  /**
   * Record a quest-related memory for an NPC
   */
  public async recordQuestMemory(
    npcId: str,
    questEvent: QuestEvent,
    context: Dict[str, Any]
  ): Promise<void> {
    const importance = this.calculateMemoryImportance(questEvent, context)
    const emotionalImpact = context.emotionalSignificance || this.options.emotionalImpact
    const memoryEvent: Omit<MemoryEvent, 'id'> = {
      type: MemoryEventType.QUEST,
      timestamp: Date.now(),
      importance,
      details: Dict[str, Any],
        description: questEvent.description
      },
      participants: [questEvent.playerId, ...questEvent.involvedNpcIds],
      tags: this.generateMemoryTags(questEvent),
    }
    await this.memoryManager.addMemory(npcId, memoryEvent)
  }
  /**
   * Retrieve relevant quest memories for an NPC based on context
   */
  public async getRelevantQuestMemories(
    npcId: str,
    context: Dict[str, Any]
  ): Promise<MemoryEvent[]> {
    const query = {
      type: MemoryEventType.QUEST,
      importance: Dict[str, Any],
      tags: context.tags,
      participants: context.playerId ? [context.playerId] : undefined
    }
    const memories = await this.memoryManager.queryMemories(npcId, query)
    return this.filterAndRankMemories(memories, context)
  }
  /**
   * Modify NPC dialogue based on quest memories
   */
  public async modifyDialogueBasedOnMemories(
    npcId: str,
    playerId: str,
    baseDialogue: str
  ): Promise<string> {
    const relevantMemories = await this.getRelevantQuestMemories(npcId, {
      playerId,
      minImportance: this.options.baseImportance * 0.6 
    })
    if (relevantMemories.length === 0) return baseDialogue
    const sortedMemories = this.sortMemoriesByRelevance(relevantMemories)
    const mostRelevantMemory = sortedMemories[0]
    const modifiedDialogue = this.incorporateMemoryIntoDialogue(
      baseDialogue,
      mostRelevantMemory
    )
    return modifiedDialogue
  }
  /**
   * Update NPC behavior based on quest memories
   */
  public async adjustNPCBehavior(
    npcId: str,
    playerId: str
  ): Promise<{
    trustModifier: float
    dispositionChange: float
    questAvailabilityAdjustment: float
  }> {
    const questMemories = await this.getRelevantQuestMemories(npcId, {
      playerId,
      minImportance: this.options.baseImportance * 0.7
    })
    let trustModifier = 0
    let dispositionChange = 0
    let questAvailabilityAdjustment = 0
    for (const memory of questMemories) {
      const impact = this.calculateMemoryImpact(memory)
      trustModifier += impact.trust
      dispositionChange += impact.disposition
      questAvailabilityAdjustment += impact.questAvailability
    }
    return {
      trustModifier: Math.max(-1, Math.min(1, trustModifier / questMemories.length)),
      dispositionChange: Math.max(-10, Math.min(10, dispositionChange)),
      questAvailabilityAdjustment: Math.max(-0.5, Math.min(0.5, questAvailabilityAdjustment))
    }
  }
  private calculateMemoryImportance(
    questEvent: QuestEvent,
    context: Dict[str, Any]
  ): float {
    let importance = this.options.baseImportance
    if (questEvent.type === QuestType.MAJOR) importance *= 1.5
    if (questEvent.status === QuestStatus.FAILED) importance *= 0.8
    if (context.emotionalSignificance) {
      importance *= (1 + context.emotionalSignificance)
    }
    if (context.factionImpact && context.factionImpact.size > 0) {
      const maxImpact = Math.max(...Array.from(context.factionImpact.values()))
      importance *= (1 + Math.abs(maxImpact) * 0.2)
    }
    return Math.min(100, Math.max(1, importance))
  }
  private generateMemoryTags(questEvent: QuestEvent): string[] {
    const tags = [
      `quest_${questEvent.type.toLowerCase()}`,
      `outcome_${questEvent.status.toLowerCase()}`,
      ...questEvent.tags || []
    ]
    if (questEvent.factionId) {
      tags.push(`faction_${questEvent.factionId}`)
    }
    return tags
  }
  private filterAndRankMemories(
    memories: List[MemoryEvent],
    context: Dict[str, Any]
  ): MemoryEvent[] {
    return memories
      .filter(memory => {
        const age = (Date.now() - memory.timestamp) / (1000 * 60 * 60 * 24) 
        const decayedImportance = memory.importance * Math.exp(-this.options.memoryDecayRate * age)
        return decayedImportance >= this.options.baseImportance * this.options.relevanceThreshold
      })
      .sort((a, b) => {
        const scoreA = this.calculateMemoryScore(a, context)
        const scoreB = this.calculateMemoryScore(b, context)
        return scoreB - scoreA
      })
  }
  private calculateMemoryScore(
    memory: MemoryEvent,
    context: Dict[str, Any]
  ): float {
    let score = memory.importance
    const age = (Date.now() - memory.timestamp) / (1000 * 60 * 60 * 24) 
    score *= Math.exp(-this.options.memoryDecayRate * age)
    if (context.questType && memory.details.questType === context.questType) {
      score *= 1.2
    }
    if (context.factions) {
      const factionMatch = context.factions.some(
        faction => memory.details.factionImpact[faction]
      )
      if (factionMatch) score *= 1.1
    }
    if (context.tags) {
      const tagMatch = context.tags.some(tag => memory.tags.includes(tag))
      if (tagMatch) score *= 1.15
    }
    return score
  }
  private sortMemoriesByRelevance(memories: List[MemoryEvent]): MemoryEvent[] {
    return memories.sort((a, b) => {
      const scoreA = a.importance * Math.exp(-this.options.memoryDecayRate * 
        ((Date.now() - a.timestamp) / (1000 * 60 * 60 * 24)))
      const scoreB = b.importance * Math.exp(-this.options.memoryDecayRate * 
        ((Date.now() - b.timestamp) / (1000 * 60 * 60 * 24)))
      return scoreB - scoreA
    })
  }
  private incorporateMemoryIntoDialogue(
    baseDialogue: str,
    memory: MemoryEvent
  ): str {
    const { questType, outcome, playerActions } = memory.details
    const references = []
    if (outcome === QuestStatus.COMPLETED) {
      references.push("like when you successfully completed that task")
    } else if (outcome === QuestStatus.FAILED) {
      references.push("similar to that unfortunate situation before")
    }
    if (playerActions && playerActions.length > 0) {
      references.push(`considering your previous choice to ${playerActions[0]}`)
    }
    if (memory.details.emotionalImpact > 0.7) {
      references.push("which I remember quite clearly")
    }
    if (references.length > 0) {
      const reference = references[Math.floor(Math.random() * references.length)]
      const dialogueParts = baseDialogue.split(/[,.!?]/)
      const insertIndex = Math.floor(dialogueParts.length / 2)
      dialogueParts.splice(insertIndex, 0, `, ${reference},`)
      return dialogueParts.join('')
    }
    return baseDialogue
  }
  private calculateMemoryImpact(memory: MemoryEvent): {
    trust: float
    disposition: float
    questAvailability: float
  } {
    const { outcome, emotionalImpact, factionImpact } = memory.details
    const age = (Date.now() - memory.timestamp) / (1000 * 60 * 60 * 24) 
    const decayFactor = Math.exp(-this.options.memoryDecayRate * age)
    let trust = 0
    let disposition = 0
    let questAvailability = 0
    if (outcome === QuestStatus.COMPLETED) {
      trust += 0.2
      disposition += 2
      questAvailability += 0.1
    } else if (outcome === QuestStatus.FAILED) {
      trust -= 0.3
      disposition -= 3
      questAvailability -= 0.2
    }
    trust += emotionalImpact * 0.1
    disposition += emotionalImpact * 1.5
    if (factionImpact) {
      const values = Object.values(factionImpact) as number[]
      const totalImpact = values.reduce((sum, val) => sum + Math.abs(val), 0)
      questAvailability += totalImpact * 0.05
    }
    return {
      trust: trust * decayFactor,
      disposition: disposition * decayFactor,
      questAvailability: questAvailability * decayFactor
    }
  }
} 