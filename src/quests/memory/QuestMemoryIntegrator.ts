import { MemoryManager } from '../../systems/npc/MemoryManager';
import { MemoryEvent, MemoryEventType, NPCMemory } from '../../types/npc/memory';
import { QuestEvent, QuestStatus, QuestType } from '../../types/quests/quest';
import { FactionType } from '../../types/factions/faction';
import { ConsequenceSystem } from '../consequences/ConsequenceSystem';
import { FactionQuestSystem } from '../factions/FactionQuestSystem';

interface QuestMemoryOptions {
  baseImportance: number;
  emotionalImpact: number;
  memoryDecayRate: number;
  relevanceThreshold: number;
}

export class QuestMemoryIntegrator {
  private memoryManager: MemoryManager;
  private consequenceSystem: ConsequenceSystem;
  private factionQuestSystem: FactionQuestSystem;
  private options: QuestMemoryOptions;

  constructor(
    memoryManager: MemoryManager,
    consequenceSystem: ConsequenceSystem,
    factionQuestSystem: FactionQuestSystem,
    options?: Partial<QuestMemoryOptions>
  ) {
    this.memoryManager = memoryManager;
    this.consequenceSystem = consequenceSystem;
    this.factionQuestSystem = factionQuestSystem;
    this.options = {
      baseImportance: 70, // Base importance for quest memories
      emotionalImpact: 0.5, // Default emotional impact multiplier
      memoryDecayRate: 0.1, // Rate at which memory importance decays
      relevanceThreshold: 0.4, // Minimum relevance score for memory recall
      ...options
    };
  }

  /**
   * Record a quest-related memory for an NPC
   */
  public async recordQuestMemory(
    npcId: string,
    questEvent: QuestEvent,
    context: {
      playerChoices?: string[];
      factionImpact?: Map<FactionType, number>;
      emotionalSignificance?: number;
    }
  ): Promise<void> {
    const importance = this.calculateMemoryImportance(questEvent, context);
    const emotionalImpact = context.emotionalSignificance || this.options.emotionalImpact;

    const memoryEvent: Omit<MemoryEvent, 'id'> = {
      type: MemoryEventType.QUEST,
      timestamp: Date.now(),
      importance,
      details: {
        questId: questEvent.questId,
        questType: questEvent.type,
        playerActions: context.playerChoices || [],
        outcome: questEvent.outcome,
        emotionalImpact,
        factionImpact: context.factionImpact ? Object.fromEntries(context.factionImpact) : {},
        description: questEvent.description
      },
      participants: [questEvent.playerId, ...questEvent.involvedNpcIds],
      tags: this.generateMemoryTags(questEvent),
    };

    await this.memoryManager.addMemory(npcId, memoryEvent);
  }

  /**
   * Retrieve relevant quest memories for an NPC based on context
   */
  public async getRelevantQuestMemories(
    npcId: string,
    context: {
      questType?: QuestType;
      playerId?: string;
      factions?: FactionType[];
      tags?: string[];
      minImportance?: number;
    }
  ): Promise<MemoryEvent[]> {
    const query = {
      type: MemoryEventType.QUEST,
      importance: {
        min: context.minImportance || this.options.baseImportance * this.options.relevanceThreshold
      },
      tags: context.tags,
      participants: context.playerId ? [context.playerId] : undefined
    };

    const memories = await this.memoryManager.queryMemories(npcId, query);
    return this.filterAndRankMemories(memories, context);
  }

  /**
   * Modify NPC dialogue based on quest memories
   */
  public async modifyDialogueBasedOnMemories(
    npcId: string,
    playerId: string,
    baseDialogue: string
  ): Promise<string> {
    const relevantMemories = await this.getRelevantQuestMemories(npcId, {
      playerId,
      minImportance: this.options.baseImportance * 0.6 // Lower threshold for dialogue modification
    });

    if (relevantMemories.length === 0) return baseDialogue;

    // Sort memories by importance and recency
    const sortedMemories = this.sortMemoriesByRelevance(relevantMemories);
    const mostRelevantMemory = sortedMemories[0];

    // Modify dialogue based on the most relevant memory
    const modifiedDialogue = this.incorporateMemoryIntoDialogue(
      baseDialogue,
      mostRelevantMemory
    );

    return modifiedDialogue;
  }

  /**
   * Update NPC behavior based on quest memories
   */
  public async adjustNPCBehavior(
    npcId: string,
    playerId: string
  ): Promise<{
    trustModifier: number;
    dispositionChange: number;
    questAvailabilityAdjustment: number;
  }> {
    const questMemories = await this.getRelevantQuestMemories(npcId, {
      playerId,
      minImportance: this.options.baseImportance * 0.7
    });

    let trustModifier = 0;
    let dispositionChange = 0;
    let questAvailabilityAdjustment = 0;

    for (const memory of questMemories) {
      const impact = this.calculateMemoryImpact(memory);
      trustModifier += impact.trust;
      dispositionChange += impact.disposition;
      questAvailabilityAdjustment += impact.questAvailability;
    }

    // Normalize the values
    return {
      trustModifier: Math.max(-1, Math.min(1, trustModifier / questMemories.length)),
      dispositionChange: Math.max(-10, Math.min(10, dispositionChange)),
      questAvailabilityAdjustment: Math.max(-0.5, Math.min(0.5, questAvailabilityAdjustment))
    };
  }

  private calculateMemoryImportance(
    questEvent: QuestEvent,
    context: {
      playerChoices?: string[];
      factionImpact?: Map<FactionType, number>;
      emotionalSignificance?: number;
    }
  ): number {
    let importance = this.options.baseImportance;

    // Adjust based on quest type and outcome
    if (questEvent.type === QuestType.MAJOR) importance *= 1.5;
    if (questEvent.status === QuestStatus.FAILED) importance *= 0.8;

    // Factor in emotional significance
    if (context.emotionalSignificance) {
      importance *= (1 + context.emotionalSignificance);
    }

    // Consider faction impact
    if (context.factionImpact && context.factionImpact.size > 0) {
      const maxImpact = Math.max(...Array.from(context.factionImpact.values()));
      importance *= (1 + Math.abs(maxImpact) * 0.2);
    }

    return Math.min(100, Math.max(1, importance));
  }

  private generateMemoryTags(questEvent: QuestEvent): string[] {
    const tags = [
      `quest_${questEvent.type.toLowerCase()}`,
      `outcome_${questEvent.status.toLowerCase()}`,
      ...questEvent.tags || []
    ];

    if (questEvent.factionId) {
      tags.push(`faction_${questEvent.factionId}`);
    }

    return tags;
  }

  private filterAndRankMemories(
    memories: MemoryEvent[],
    context: {
      questType?: QuestType;
      factions?: FactionType[];
      tags?: string[];
    }
  ): MemoryEvent[] {
    return memories
      .filter(memory => {
        // Apply decay based on time
        const age = (Date.now() - memory.timestamp) / (1000 * 60 * 60 * 24); // Age in days
        const decayedImportance = memory.importance * Math.exp(-this.options.memoryDecayRate * age);
        return decayedImportance >= this.options.baseImportance * this.options.relevanceThreshold;
      })
      .sort((a, b) => {
        // Score based on importance and recency
        const scoreA = this.calculateMemoryScore(a, context);
        const scoreB = this.calculateMemoryScore(b, context);
        return scoreB - scoreA;
      });
  }

  private calculateMemoryScore(
    memory: MemoryEvent,
    context: {
      questType?: QuestType;
      factions?: FactionType[];
      tags?: string[];
    }
  ): number {
    let score = memory.importance;

    // Factor in recency
    const age = (Date.now() - memory.timestamp) / (1000 * 60 * 60 * 24); // Age in days
    score *= Math.exp(-this.options.memoryDecayRate * age);

    // Boost score based on context matches
    if (context.questType && memory.details.questType === context.questType) {
      score *= 1.2;
    }

    if (context.factions) {
      const factionMatch = context.factions.some(
        faction => memory.details.factionImpact[faction]
      );
      if (factionMatch) score *= 1.1;
    }

    if (context.tags) {
      const tagMatch = context.tags.some(tag => memory.tags.includes(tag));
      if (tagMatch) score *= 1.15;
    }

    return score;
  }

  private sortMemoriesByRelevance(memories: MemoryEvent[]): MemoryEvent[] {
    return memories.sort((a, b) => {
      const scoreA = a.importance * Math.exp(-this.options.memoryDecayRate * 
        ((Date.now() - a.timestamp) / (1000 * 60 * 60 * 24)));
      const scoreB = b.importance * Math.exp(-this.options.memoryDecayRate * 
        ((Date.now() - b.timestamp) / (1000 * 60 * 60 * 24)));
      return scoreB - scoreA;
    });
  }

  private incorporateMemoryIntoDialogue(
    baseDialogue: string,
    memory: MemoryEvent
  ): string {
    // Extract key details from the memory
    const { questType, outcome, playerActions } = memory.details;
    
    // Generate reference phrases based on the memory
    const references = [];
    
    if (outcome === QuestStatus.COMPLETED) {
      references.push("like when you successfully completed that task");
    } else if (outcome === QuestStatus.FAILED) {
      references.push("similar to that unfortunate situation before");
    }

    if (playerActions && playerActions.length > 0) {
      references.push(`considering your previous choice to ${playerActions[0]}`);
    }

    if (memory.details.emotionalImpact > 0.7) {
      references.push("which I remember quite clearly");
    }

    // Insert memory references naturally into the dialogue
    if (references.length > 0) {
      const reference = references[Math.floor(Math.random() * references.length)];
      const dialogueParts = baseDialogue.split(/[,.!?]/);
      const insertIndex = Math.floor(dialogueParts.length / 2);
      dialogueParts.splice(insertIndex, 0, `, ${reference},`);
      return dialogueParts.join('');
    }

    return baseDialogue;
  }

  private calculateMemoryImpact(memory: MemoryEvent): {
    trust: number;
    disposition: number;
    questAvailability: number;
  } {
    const { outcome, emotionalImpact, factionImpact } = memory.details;
    const age = (Date.now() - memory.timestamp) / (1000 * 60 * 60 * 24); // Age in days
    const decayFactor = Math.exp(-this.options.memoryDecayRate * age);

    let trust = 0;
    let disposition = 0;
    let questAvailability = 0;

    // Calculate base impact
    if (outcome === QuestStatus.COMPLETED) {
      trust += 0.2;
      disposition += 2;
      questAvailability += 0.1;
    } else if (outcome === QuestStatus.FAILED) {
      trust -= 0.3;
      disposition -= 3;
      questAvailability -= 0.2;
    }

    // Factor in emotional impact
    trust += emotionalImpact * 0.1;
    disposition += emotionalImpact * 1.5;

    // Consider faction impact
    if (factionImpact) {
      const values = Object.values(factionImpact) as number[];
      const totalImpact = values.reduce((sum, val) => sum + Math.abs(val), 0);
      questAvailability += totalImpact * 0.05;
    }

    // Apply decay
    return {
      trust: trust * decayFactor,
      disposition: disposition * decayFactor,
      questAvailability: questAvailability * decayFactor
    };
  }
} 