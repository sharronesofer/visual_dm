import {
  MemoryEvent,
  MemoryEventType,
  NPCMemory,
  MemoryQuery,
  MemoryProcessingResult,
  ImportanceFactors,
  CompressionStrategy,
  MemoryContext,
  MEMORY_CONSTANTS
} from '../../types/npc/memory';
import { MemoryIndex } from './MemoryIndex';

export class MemoryManager {
  private memories: Map<string, NPCMemory>;
  private processingQueue: Set<string>;
  private processingInterval: NodeJS.Timeout | null;
  private memoryIndex: MemoryIndex;
  private batchSize: number = 50;

  constructor() {
    this.memories = new Map();
    this.processingQueue = new Set();
    this.processingInterval = null;
    this.memoryIndex = new MemoryIndex();
    this.startProcessingLoop();
  }

  // Check if NPC exists in memory system
  public hasNPC(npcId: string): boolean {
    return this.memories.has(npcId);
  }

  // Initialize memory system for an NPC
  public initializeNPC(npcId: string): void {
    if (!this.hasNPC(npcId)) {
      this.memories.set(npcId, {
        shortTermMemory: [],
        longTermMemory: [],
        relationships: new Map()
      });
    }
  }

  // Add a new memory for an NPC
  public async addMemory(npcId: string, memory: Omit<MemoryEvent, 'id'>): Promise<void> {
    if (!this.hasNPC(npcId)) {
      this.initializeNPC(npcId);
    }

    const npcMemory = this.memories.get(npcId)!;
    const newMemory: MemoryEvent = {
      ...memory,
      id: crypto.randomUUID(),
      timestamp: Date.now()
    };

    // Add to short-term memory
    npcMemory.shortTermMemory.push(newMemory);

    // Queue for processing
    this.processingQueue.add(npcId);
  }

  // Share memories between NPCs
  public async shareMemories(
    sourceNpcId: string,
    targetNpcId: string,
    memoryIds: string[],
    options?: {
      transformMemory?: (memory: MemoryEvent) => Partial<MemoryEvent>;
    }
  ): Promise<void> {
    if (!this.hasNPC(sourceNpcId) || !this.hasNPC(targetNpcId)) {
      throw new Error('Source or target NPC not found');
    }

    const sourceMemory = this.memories.get(sourceNpcId)!;
    const allSourceMemories = [...sourceMemory.shortTermMemory, ...sourceMemory.longTermMemory];
    
    const memoriesToShare = allSourceMemories.filter(m => memoryIds.includes(m.id));

    for (const memory of memoriesToShare) {
      const transformedMemory = options?.transformMemory
        ? { ...memory, ...options.transformMemory(memory) }
        : { ...memory };

      // Create a new memory ID for the shared copy
      transformedMemory.id = crypto.randomUUID();
      
      // Add to target's short-term memory for processing
      await this.addMemory(targetNpcId, transformedMemory);
    }
  }

  // Initialize memory for a new NPC
  public initializeNPCMemory(npcId: string): void {
    if (!this.memories.has(npcId)) {
      this.memories.set(npcId, {
        npcId,
        shortTermMemory: [],
        longTermMemory: [],
        memoryStats: {
          totalMemories: 0,
          lastProcessed: Date.now(),
          significantEventCount: 0
        },
        relationships: {}
      });
    }
  }

  // Add a new memory event to an NPC's short-term memory
  public addMemoryEvent(event: Omit<MemoryEvent, 'id' | 'importance'>): void {
    const memoryEvent: MemoryEvent = {
      ...event,
      id: this.generateEventId(),
      importance: this.calculateImportance({
        baseImportance: 50,
        emotionalImpact: event.details.emotionalImpact,
        participantCount: event.participants.length,
        relationshipStrength: this.getAverageRelationshipStrength(event.participants[0], event.participants),
        timeRelevance: 1,
        eventType: event.type
      })
    };

    event.participants.forEach(npcId => {
      this.initializeNPCMemory(npcId);
      const memory = this.memories.get(npcId)!;
      
      memory.shortTermMemory.push(memoryEvent);
      memory.memoryStats.totalMemories++;
      
      if (memory.shortTermMemory.length >= MEMORY_CONSTANTS.SHORT_TERM_CAPACITY) {
        this.processingQueue.add(npcId);
      }
    });
  }

  // Process memories in batches for better performance
  private async processBatch(): Promise<void> {
    const batch = Array.from(this.processingQueue).slice(0, this.batchSize);
    if (batch.length === 0) return;

    const results = await Promise.all(
      batch.map(npcId => this.processMemories(npcId))
    );

    // Update memory index for processed memories
    batch.forEach((npcId, index) => {
      const result = results[index];
      result.significantEvents.forEach(event => {
        this.memoryIndex.addMemory(npcId, event);
      });
      result.forgottenEvents.forEach(eventId => {
        this.memoryIndex.removeMemory(eventId);
      });
    });

    // Remove processed NPCs from queue
    batch.forEach(npcId => this.processingQueue.delete(npcId));
  }

  private startProcessingLoop(): void {
    if (this.processingInterval) return;

    this.processingInterval = setInterval(async () => {
      await this.processBatch();
    }, MEMORY_CONSTANTS.PROCESSING_INTERVAL);
  }

  // Process memories for an NPC
  private async processMemories(npcId: string): Promise<MemoryProcessingResult> {
    const memory = this.memories.get(npcId);
    if (!memory) throw new Error(`No memory found for NPC ${npcId}`);

    const now = Date.now();
    const result: MemoryProcessingResult = {
      compressedEvents: [],
      significantEvents: [],
      forgottenEvents: [],
      updatedRelationships: {}
    };

    // Apply memory decay to existing long-term memories
    memory.longTermMemory = memory.longTermMemory.map(event => ({
      ...event,
      importance: this.applyMemoryDecay(event.importance, event.timestamp, now)
    }));

    // Remove old memories that have decayed below threshold
    const [retainedMemories, forgottenMemories] = this.partitionMemories(
      memory.longTermMemory,
      MEMORY_CONSTANTS.IMPORTANCE_THRESHOLD
    );
    memory.longTermMemory = retainedMemories;
    result.forgottenEvents = forgottenMemories.map(m => m.id);

    // Process short-term memories in batches
    const shortTermGroups = this.groupSimilarMemories(memory.shortTermMemory);
    
    for (const group of shortTermGroups) {
      if (group.length >= MEMORY_CONSTANTS.COMPRESSION_THRESHOLD) {
        const compressed = this.compressMemories(group);
        result.compressedEvents.push(compressed);
        if (compressed.importance >= MEMORY_CONSTANTS.IMPORTANCE_THRESHOLD) {
          memory.longTermMemory.push(compressed);
          result.significantEvents.push(compressed);
        }
      } else {
        for (const event of group) {
          if (event.importance >= MEMORY_CONSTANTS.IMPORTANCE_THRESHOLD) {
            memory.longTermMemory.push(event);
            result.significantEvents.push(event);
          }
        }
      }
    }

    // Update relationships based on processed memories
    result.updatedRelationships = this.updateRelationships(memory, result.significantEvents);

    // Clear short-term memory
    memory.shortTermMemory = [];
    memory.memoryStats.lastProcessed = now;
    memory.memoryStats.significantEventCount = memory.longTermMemory.length;

    return result;
  }

  // Enhanced memory retrieval using the index
  public async queryMemories(npcId: string, query: MemoryQuery): Promise<MemoryEvent[]> {
    const memory = this.memories.get(npcId);
    if (!memory) return [];

    let relevantIds = new Set<string>();
    
    // Use memory index for efficient filtering
    if (query.type) {
      const typeMemories = this.memoryIndex.findMemoriesByType(
        query.type,
        query.minImportance
      );
      relevantIds = new Set(typeMemories);
    }

    if (query.participants?.length) {
      const participantMemories = this.memoryIndex.findMemoriesByParticipants(
        query.participants,
        query.requireAllParticipants
      );
      relevantIds = query.type
        ? new Set(
            Array.from(relevantIds).filter(id =>
              participantMemories.includes(id)
            )
          )
        : new Set(participantMemories);
    }

    if (query.tags?.length) {
      const tagMemories = this.memoryIndex.findMemoriesByTags(
        query.tags,
        query.matchAllTags
      );
      relevantIds = relevantIds.size > 0
        ? new Set(
            Array.from(relevantIds).filter(id =>
              tagMemories.includes(id)
            )
          )
        : new Set(tagMemories);
    }

    // If no specific filters, get recent memories
    if (relevantIds.size === 0 && !query.type && !query.participants && !query.tags) {
      const recentIds = this.memoryIndex.findRecentMemories(
        npcId,
        query.limit,
        query.minImportance
      );
      relevantIds = new Set(recentIds);
    }

    // Get full memory objects for the filtered IDs
    const allMemories = [...memory.longTermMemory, ...memory.shortTermMemory];
    return Array.from(relevantIds)
      .map(id => allMemories.find(m => m.id === id))
      .filter((m): m is MemoryEvent => m !== undefined);
  }

  // Calculate memory importance based on various factors
  private calculateImportance(factors: ImportanceFactors): number {
    const {
      baseImportance,
      emotionalImpact,
      participantCount,
      relationshipStrength,
      timeRelevance,
      eventType
    } = factors;

    const emotionalWeight = Math.abs(emotionalImpact) * MEMORY_CONSTANTS.EMOTIONAL_IMPACT_WEIGHT;
    const participantWeight = Math.min(participantCount * 5, 20);
    const relationshipWeight = relationshipStrength * 10;
    const timeWeight = timeRelevance * 5;
    
    // Event type specific weights
    const typeWeights: Record<MemoryEventType, number> = {
      [MemoryEventType.CONFLICT]: 15,
      [MemoryEventType.QUEST]: 12,
      [MemoryEventType.ACHIEVEMENT]: 10,
      [MemoryEventType.RELATIONSHIP_CHANGE]: 8,
      [MemoryEventType.FACTION_EVENT]: 7,
      [MemoryEventType.TRADE]: 5,
      [MemoryEventType.INTERACTION]: 4,
      [MemoryEventType.DECISION]: 4,
      [MemoryEventType.OBSERVATION]: 3,
      [MemoryEventType.WORLD_EVENT]: 6
    };

    const typeWeight = typeWeights[eventType];

    const importance = baseImportance +
      emotionalWeight +
      participantWeight +
      relationshipWeight +
      timeWeight +
      typeWeight;

    return Math.min(Math.max(importance, 0), 100);
  }

  // Apply memory decay based on time
  private applyMemoryDecay(importance: number, timestamp: number, now: number): number {
    const age = now - timestamp;
    const decayFactor = Math.exp(-MEMORY_CONSTANTS.MEMORY_DECAY_RATE * (age / MEMORY_CONSTANTS.MAX_MEMORY_AGE));
    return importance * decayFactor;
  }

  // Group similar memories for compression
  private groupSimilarMemories(memories: MemoryEvent[]): MemoryEvent[][] {
    const groups: Map<string, MemoryEvent[]> = new Map();

    for (const memory of memories) {
      const key = this.getMemoryGroupKey(memory);
      if (!groups.has(key)) {
        groups.set(key, []);
      }
      groups.get(key)!.push(memory);
    }

    return Array.from(groups.values());
  }

  // Compress a group of similar memories into a single memory
  private compressMemories(memories: MemoryEvent[]): MemoryEvent {
    const strategy = this.selectCompressionStrategy(memories);
    
    switch (strategy) {
      case CompressionStrategy.SUMMARIZE:
        return this.summarizeMemories(memories);
      case CompressionStrategy.AGGREGATE:
        return this.aggregateMemories(memories);
      case CompressionStrategy.PRUNE:
        return this.pruneMemoryDetails(memories[0]);
      default:
        return memories[0];
    }
  }

  private selectCompressionStrategy(memories: MemoryEvent[]): CompressionStrategy {
    if (memories.length >= MEMORY_CONSTANTS.COMPRESSION_THRESHOLD * 2) {
      return CompressionStrategy.SUMMARIZE;
    } else if (memories.length >= MEMORY_CONSTANTS.COMPRESSION_THRESHOLD) {
      return CompressionStrategy.AGGREGATE;
    } else {
      return CompressionStrategy.PRUNE;
    }
  }

  // Helper methods
  private generateEventId(): string {
    return `mem_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private getMemoryGroupKey(memory: MemoryEvent): string {
    return `${memory.type}_${memory.participants.sort().join('_')}`;
  }

  private getAverageRelationshipStrength(npcId: string, participants: string[]): number {
    const memory = this.memories.get(npcId);
    if (!memory) return 0;

    const strengths = participants
      .filter(p => p !== npcId)
      .map(p => memory.relationships[p]?.trust || 0);

    return strengths.length > 0
      ? strengths.reduce((a, b) => a + b, 0) / strengths.length
      : 0;
  }

  private summarizeMemories(memories: MemoryEvent[]): MemoryEvent {
    const first = memories[0];
    const last = memories[memories.length - 1];

    return {
      id: this.generateEventId(),
      timestamp: last.timestamp,
      type: first.type,
      importance: Math.max(...memories.map(m => m.importance)),
      participants: Array.from(new Set(memories.flatMap(m => m.participants))),
      location: first.location,
      details: {
        description: `Summary of ${memories.length} similar events from ${new Date(first.timestamp).toLocaleDateString()} to ${new Date(last.timestamp).toLocaleDateString()}`,
        emotionalImpact: memories.reduce((sum, m) => sum + m.details.emotionalImpact, 0) / memories.length,
        originalEvents: memories.map(m => m.id)
      },
      tags: Array.from(new Set(memories.flatMap(m => m.tags))),
      relatedMemories: Array.from(new Set(memories.flatMap(m => m.relatedMemories || [])))
    };
  }

  private aggregateMemories(memories: MemoryEvent[]): MemoryEvent {
    const base = memories[0];
    return {
      ...base,
      id: this.generateEventId(),
      importance: Math.max(...memories.map(m => m.importance)),
      details: {
        ...base.details,
        aggregatedCount: memories.length,
        aggregatedEvents: memories.map(m => m.id)
      }
    };
  }

  private pruneMemoryDetails(memory: MemoryEvent): MemoryEvent {
    const { id, timestamp, type, importance, participants, tags } = memory;
    return {
      id: this.generateEventId(),
      timestamp,
      type,
      importance,
      participants,
      details: {
        description: memory.details.description,
        emotionalImpact: memory.details.emotionalImpact
      },
      tags
    };
  }

  private partitionMemories(
    memories: MemoryEvent[],
    threshold: number
  ): [MemoryEvent[], MemoryEvent[]] {
    return memories.reduce<[MemoryEvent[], MemoryEvent[]]>(
      ([retained, forgotten], memory) => {
        if (memory.importance >= threshold) {
          retained.push(memory);
        } else {
          forgotten.push(memory);
        }
        return [retained, forgotten];
      },
      [[], []]
    );
  }

  private updateRelationships(
    memory: NPCMemory,
    significantEvents: MemoryEvent[]
  ): Record<string, { oldTrust: number; newTrust: number; reason: string }> {
    const updates: Record<string, { oldTrust: number; newTrust: number; reason: string }> = {};

    for (const event of significantEvents) {
      const otherParticipants = event.participants.filter(p => p !== memory.npcId);
      
      for (const participant of otherParticipants) {
        if (!memory.relationships[participant]) {
          memory.relationships[participant] = {
            trust: 0,
            lastInteraction: event.timestamp,
            sharedMemories: []
          };
        }

        const rel = memory.relationships[participant];
        const oldTrust = rel.trust;
        
        // Update trust based on emotional impact and event type
        const trustChange = event.details.emotionalImpact * 0.2;
        rel.trust = Math.max(-10, Math.min(10, rel.trust + trustChange));
        
        // Update shared memories
        rel.sharedMemories.push(event.id);
        rel.lastInteraction = event.timestamp;

        updates[participant] = {
          oldTrust,
          newTrust: rel.trust,
          reason: `${event.type} event with emotional impact of ${event.details.emotionalImpact}`
        };
      }
    }

    return updates;
  }

  public dispose(): void {
    if (this.processingInterval) {
      clearInterval(this.processingInterval);
      this.processingInterval = null;
    }
  }
} 