import { v4 as uuidv4 } from 'uuid';
import {
  Memory,
  MemoryType,
  MemoryLayer,
  MemorySummary,
  NPCKnowledge,
  MemoryConfig,
  MemoryQueryOptions
} from '../types/memory';
import { FactionType } from '../worldgen/faction/types';

const DEFAULT_CONFIG: MemoryConfig = {
  maxMemoriesPerLayer: {
    [MemoryLayer.IMMEDIATE]: 20,
    [MemoryLayer.SHORT_TERM]: 50,
    [MemoryLayer.MEDIUM_TERM]: 100,
    [MemoryLayer.LONG_TERM]: 200,
    [MemoryLayer.PERMANENT]: 50
  },
  decayRates: {
    [MemoryLayer.IMMEDIATE]: 0.1,
    [MemoryLayer.SHORT_TERM]: 0.05,
    [MemoryLayer.MEDIUM_TERM]: 0.02,
    [MemoryLayer.LONG_TERM]: 0.01,
    [MemoryLayer.PERMANENT]: 0
  },
  promotionThresholds: {
    [MemoryLayer.IMMEDIATE]: 24, // hours
    [MemoryLayer.SHORT_TERM]: 72,
    [MemoryLayer.MEDIUM_TERM]: 168,
    [MemoryLayer.LONG_TERM]: 720,
    [MemoryLayer.PERMANENT]: Infinity
  },
  importanceThresholds: {
    low: 0.3,
    medium: 0.6,
    high: 0.8
  },
  compressionRatio: 0.5,
  minClarityThreshold: 0.2
};

export class MemoryManager {
  private knowledge: NPCKnowledge;
  private config: MemoryConfig;

  constructor(npcId: string, config: Partial<MemoryConfig> = {}) {
    this.config = { ...DEFAULT_CONFIG, ...config };
    this.knowledge = {
      npcId,
      backstory: {},
      memories: {
        [MemoryLayer.IMMEDIATE]: [],
        [MemoryLayer.SHORT_TERM]: [],
        [MemoryLayer.MEDIUM_TERM]: [],
        [MemoryLayer.LONG_TERM]: [],
        [MemoryLayer.PERMANENT]: []
      },
      summaries: {
        [MemoryLayer.IMMEDIATE]: [],
        [MemoryLayer.SHORT_TERM]: [],
        [MemoryLayer.MEDIUM_TERM]: [],
        [MemoryLayer.LONG_TERM]: [],
        [MemoryLayer.PERMANENT]: []
      },
      lastUpdate: new Date()
    };
  }

  public addMemory(
    content: string,
    type: MemoryType,
    options: {
      importance?: number;
      emotionalImpact?: number;
      tags?: string[];
      relatedNpcIds?: string[];
      relatedFactions?: FactionType[];
      location?: string;
      context?: Record<string, any>;
    } = {}
  ): Memory {
    const memory: Memory = {
      id: uuidv4(),
      npcId: this.knowledge.npcId,
      type,
      layer: MemoryLayer.IMMEDIATE,
      content,
      timestamp: new Date(),
      lastAccessed: new Date(),
      importance: options.importance ?? this.calculateImportance(content, type, options),
      clarity: 1,
      emotionalImpact: options.emotionalImpact ?? 0,
      tags: options.tags ?? [],
      relatedNpcIds: options.relatedNpcIds,
      relatedFactions: options.relatedFactions,
      location: options.location,
      context: options.context
    };

    this.knowledge.memories[MemoryLayer.IMMEDIATE].push(memory);
    this.enforceLayerLimit(MemoryLayer.IMMEDIATE);
    this.knowledge.lastUpdate = new Date();

    return memory;
  }

  public queryMemories(options: MemoryQueryOptions = {}): Memory[] {
    let memories = this.getAllMemories();

    // Apply filters based on options
    if (options.types?.length) {
      memories = memories.filter(m => options.types!.includes(m.type));
    }
    if (options.layers?.length) {
      memories = memories.filter(m => options.layers!.includes(m.layer));
    }
    if (options.minImportance !== undefined) {
      memories = memories.filter(m => m.importance >= options.minImportance!);
    }
    if (options.minClarity !== undefined) {
      memories = memories.filter(m => m.clarity >= options.minClarity!);
    }
    if (options.tags?.length) {
      memories = memories.filter(m => 
        options.tags!.some(tag => m.tags.includes(tag))
      );
    }
    if (options.relatedNpcIds?.length) {
      memories = memories.filter(m => 
        m.relatedNpcIds?.some(id => options.relatedNpcIds!.includes(id))
      );
    }
    if (options.relatedFactions?.length) {
      memories = memories.filter(m => 
        m.relatedFactions?.some(f => options.relatedFactions!.includes(f))
      );
    }
    if (options.startDate) {
      memories = memories.filter(m => m.timestamp >= options.startDate!);
    }
    if (options.endDate) {
      memories = memories.filter(m => m.timestamp <= options.endDate!);
    }
    if (options.location) {
      memories = memories.filter(m => m.location === options.location);
    }

    // Sort by importance and timestamp
    memories.sort((a, b) => {
      const importanceDiff = b.importance - a.importance;
      if (importanceDiff !== 0) return importanceDiff;
      return b.timestamp.getTime() - a.timestamp.getTime();
    });

    // Apply limit if specified
    if (options.limit) {
      memories = memories.slice(0, options.limit);
    }

    // Update lastAccessed for retrieved memories
    memories.forEach(m => {
      m.lastAccessed = new Date();
    });

    return memories;
  }

  public update(): void {
    this.decayMemories();
    this.promoteMemories();
    this.compressMemories();
    this.knowledge.lastUpdate = new Date();
  }

  private getAllMemories(): Memory[] {
    return Object.values(this.knowledge.memories).flat();
  }

  private calculateImportance(
    content: string,
    type: MemoryType,
    options: {
      emotionalImpact?: number;
      relatedNpcIds?: string[];
      relatedFactions?: FactionType[];
    }
  ): number {
    let importance = 0;

    // Base importance by type
    switch (type) {
      case MemoryType.KEYSTONE:
        importance += 0.8;
        break;
      case MemoryType.BACKSTORY:
        importance += 0.7;
        break;
      case MemoryType.EVENT:
        importance += 0.6;
        break;
      case MemoryType.INTERACTION:
        importance += 0.5;
        break;
      case MemoryType.KNOWLEDGE:
        importance += 0.4;
        break;
      case MemoryType.RUMOR:
        importance += 0.3;
        break;
    }

    // Adjust for emotional impact
    if (options.emotionalImpact) {
      importance += Math.min(0.3, Math.abs(options.emotionalImpact) * 0.3);
    }

    // Adjust for relationships
    if (options.relatedNpcIds?.length) {
      importance += Math.min(0.2, options.relatedNpcIds.length * 0.05);
    }
    if (options.relatedFactions?.length) {
      importance += Math.min(0.2, options.relatedFactions.length * 0.1);
    }

    // Normalize to 0-1 range
    return Math.min(1, Math.max(0, importance));
  }

  private decayMemories(): void {
    for (const layer of Object.values(MemoryLayer)) {
      const decayRate = this.config.decayRates[layer];
      this.knowledge.memories[layer].forEach(memory => {
        const hoursSinceLastAccess = 
          (new Date().getTime() - memory.lastAccessed.getTime()) / (1000 * 60 * 60);
        memory.clarity = Math.max(
          0,
          memory.clarity - (decayRate * hoursSinceLastAccess / 24)
        );
      });
    }
  }

  private promoteMemories(): void {
    for (const layer of [
      MemoryLayer.IMMEDIATE,
      MemoryLayer.SHORT_TERM,
      MemoryLayer.MEDIUM_TERM,
      MemoryLayer.LONG_TERM
    ]) {
      const nextLayer = this.getNextLayer(layer);
      const threshold = this.config.promotionThresholds[layer];
      
      const memoriesToPromote = this.knowledge.memories[layer].filter(memory => {
        const hoursOld = 
          (new Date().getTime() - memory.timestamp.getTime()) / (1000 * 60 * 60);
        return (
          hoursOld >= threshold &&
          memory.importance >= this.config.importanceThresholds.medium
        );
      });

      if (memoriesToPromote.length > 0) {
        // Create summary for promoted memories
        const summary: MemorySummary = {
          id: uuidv4(),
          sourceMemoryIds: memoriesToPromote.map(m => m.id),
          content: this.summarizeMemories(memoriesToPromote),
          layer: nextLayer,
          timestamp: new Date(),
          importance: this.calculateSummaryImportance(memoriesToPromote),
          tags: this.aggregateTags(memoriesToPromote)
        };

        // Move memories to next layer
        this.knowledge.memories[nextLayer].push(...memoriesToPromote);
        this.knowledge.summaries[nextLayer].push(summary);
        this.knowledge.memories[layer] = this.knowledge.memories[layer].filter(
          m => !memoriesToPromote.includes(m)
        );
      }
    }
  }

  private compressMemories(): void {
    for (const layer of Object.values(MemoryLayer)) {
      const memories = this.knowledge.memories[layer];
      const maxMemories = this.config.maxMemoriesPerLayer[layer];
      
      if (memories.length > maxMemories) {
        const numToCompress = Math.floor(
          (memories.length - maxMemories) * this.config.compressionRatio
        );
        
        if (numToCompress > 1) {
          // Find similar memories to compress
          const compressed = this.findAndCompressMemories(
            memories,
            numToCompress
          );
          
          // Update the layer's memories
          this.knowledge.memories[layer] = compressed;
        }
      }
    }
  }

  private enforceLayerLimit(layer: MemoryLayer): void {
    const memories = this.knowledge.memories[layer];
    const maxMemories = this.config.maxMemoriesPerLayer[layer];
    
    if (memories.length > maxMemories) {
      // Sort by importance and keep only the most important ones
      memories.sort((a, b) => b.importance - a.importance);
      this.knowledge.memories[layer] = memories.slice(0, maxMemories);
    }
  }

  private getNextLayer(layer: MemoryLayer): MemoryLayer {
    const layers = Object.values(MemoryLayer);
    const currentIndex = layers.indexOf(layer);
    return layers[currentIndex + 1];
  }

  private summarizeMemories(memories: Memory[]): string {
    // In a real implementation, this would use an LLM to generate a summary
    // For now, we'll just concatenate the contents with a simple format
    return memories
      .sort((a, b) => b.importance - a.importance)
      .map(m => m.content)
      .join(' | ');
  }

  private calculateSummaryImportance(memories: Memory[]): number {
    // Calculate average importance weighted by emotional impact
    const totalWeight = memories.reduce(
      (sum, m) => sum + (1 + Math.abs(m.emotionalImpact)),
      0
    );
    const weightedSum = memories.reduce(
      (sum, m) => sum + m.importance * (1 + Math.abs(m.emotionalImpact)),
      0
    );
    return weightedSum / totalWeight;
  }

  private aggregateTags(memories: Memory[]): string[] {
    // Combine all tags and remove duplicates
    return [...new Set(memories.flatMap(m => m.tags))];
  }

  private findAndCompressMemories(
    memories: Memory[],
    targetReduction: number
  ): Memory[] {
    // Group similar memories by tags and time proximity
    const groups: Memory[][] = [];
    const used = new Set<string>();

    for (const memory of memories) {
      if (used.has(memory.id)) continue;

      const group = [memory];
      used.add(memory.id);

      // Find similar memories
      for (const other of memories) {
        if (used.has(other.id)) continue;

        const isSimilar = this.areMemoriesSimilar(memory, other);
        if (isSimilar) {
          group.push(other);
          used.add(other.id);
        }
      }

      if (group.length > 1) {
        groups.push(group);
      }
    }

    // Compress groups into single memories
    const compressed: Memory[] = [];
    let reductionAchieved = 0;

    // Add isolated memories first
    memories
      .filter(m => !used.has(m.id))
      .forEach(m => compressed.push(m));

    // Process groups by size (largest first) until we achieve target reduction
    groups
      .sort((a, b) => b.length - a.length)
      .forEach(group => {
        if (reductionAchieved < targetReduction) {
          // Compress the group into a single memory
          compressed.push(this.mergeMemories(group));
          reductionAchieved += group.length - 1;
        } else {
          // Add all memories from the group individually
          group.forEach(m => compressed.push(m));
        }
      });

    return compressed;
  }

  private areMemoriesSimilar(a: Memory, b: Memory): boolean {
    // Check if memories are similar based on various criteria
    const timeThreshold = 24 * 60 * 60 * 1000; // 24 hours in milliseconds
    const timeDiff = Math.abs(a.timestamp.getTime() - b.timestamp.getTime());
    
    const hasCommonTags = a.tags.some(tag => b.tags.includes(tag));
    const sameType = a.type === b.type;
    const sameLocation = a.location === b.location;
    
    const hasCommonNPCs = a.relatedNpcIds?.some(
      id => b.relatedNpcIds?.includes(id)
    );
    const hasCommonFactions = a.relatedFactions?.some(
      f => b.relatedFactions?.includes(f)
    );

    return (
      timeDiff <= timeThreshold &&
      sameType &&
      (hasCommonTags || sameLocation || hasCommonNPCs || hasCommonFactions)
    );
  }

  private mergeMemories(memories: Memory[]): Memory {
    // Create a new memory that combines the information from all memories
    const base = memories[0];
    
    return {
      id: uuidv4(),
      npcId: base.npcId,
      type: base.type,
      layer: base.layer,
      content: this.summarizeMemories(memories),
      timestamp: new Date(
        Math.min(...memories.map(m => m.timestamp.getTime()))
      ),
      lastAccessed: new Date(),
      importance: this.calculateSummaryImportance(memories),
      clarity: Math.max(...memories.map(m => m.clarity)),
      emotionalImpact: memories.reduce(
        (sum, m) => sum + m.emotionalImpact,
        0
      ) / memories.length,
      tags: this.aggregateTags(memories),
      relatedNpcIds: [
        ...new Set(memories.flatMap(m => m.relatedNpcIds || []))
      ],
      relatedFactions: [
        ...new Set(memories.flatMap(m => m.relatedFactions || []))
      ],
      location: base.location,
      context: this.mergeContexts(memories)
    };
  }

  private mergeContexts(
    memories: Memory[]
  ): Record<string, any> | undefined {
    const contexts = memories
      .map(m => m.context)
      .filter((c): c is Record<string, any> => c !== undefined);
    
    if (contexts.length === 0) return undefined;

    return contexts.reduce((merged, context) => ({
      ...merged,
      ...context
    }), {});
  }
} 