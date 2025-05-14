import { MemoryManager } from './MemoryManager';
import { MemoryEvent, MemoryEventType, MEMORY_CONSTANTS } from '../../types/npc/memory';
import { NPCRelationship } from '../../hooks/useNPCRelationships';

export interface MemorySharingConfig {
  sharingThreshold: number;  // Minimum relationship value for sharing (-10 to 10)
  maxSharedMemories: number; // Maximum memories to share per interaction
  proximityThreshold: number; // Maximum distance for memory sharing (game units)
  sharingProbability: number; // Base probability of sharing a memory (0-1)
}

const DEFAULT_SHARING_CONFIG: MemorySharingConfig = {
  sharingThreshold: 2,
  maxSharedMemories: 5,
  proximityThreshold: 10,
  sharingProbability: 0.3
};

export class MemorySharing {
  private config: MemorySharingConfig;
  private memoryManager: MemoryManager;

  constructor(memoryManager: MemoryManager, config: Partial<MemorySharingConfig> = {}) {
    this.memoryManager = memoryManager;
    this.config = { ...DEFAULT_SHARING_CONFIG, ...config };
  }

  public shareMemories(
    sourceNpcId: string,
    targetNpcId: string,
    relationship: NPCRelationship,
    distance: number
  ): MemoryEvent[] {
    // Check if sharing conditions are met
    if (!this.shouldShareMemories(relationship.value, distance)) {
      return [];
    }

    // Get shareable memories from source NPC
    const sourceMemories = this.memoryManager.queryMemories({
      npcId: sourceNpcId,
      importance: { min: MEMORY_CONSTANTS.MEMORY_SHARING_THRESHOLD, max: 100 }
    });

    // Filter and select memories to share
    const memoriesToShare = this.selectMemoriesToShare(sourceMemories);

    // Process and adapt memories for the target NPC
    const sharedMemories = memoriesToShare.map(memory => this.adaptMemoryForSharing(
      memory,
      sourceNpcId,
      targetNpcId,
      relationship.value
    ));

    // Add shared memories to target NPC's memory system
    sharedMemories.forEach(memory => {
      this.memoryManager.addMemoryEvent({
        ...memory,
        type: MemoryEventType.INTERACTION,
        details: {
          ...memory.details,
          source: sourceNpcId,
          isSharedMemory: true
        }
      });
    });

    return sharedMemories;
  }

  private shouldShareMemories(relationshipValue: number, distance: number): boolean {
    if (relationshipValue < this.config.sharingThreshold) return false;
    if (distance > this.config.proximityThreshold) return false;

    // Calculate sharing probability based on relationship and distance
    const relationshipFactor = (relationshipValue + 10) / 20; // Normalize to 0-1
    const distanceFactor = 1 - (distance / this.config.proximityThreshold);
    const probability = this.config.sharingProbability * relationshipFactor * distanceFactor;

    return Math.random() < probability;
  }

  private selectMemoriesToShare(memories: MemoryEvent[]): MemoryEvent[] {
    // Sort by importance and recency
    const sortedMemories = [...memories].sort((a, b) => {
      const importanceDiff = b.importance - a.importance;
      if (importanceDiff !== 0) return importanceDiff;
      return b.timestamp - a.timestamp;
    });

    // Select memories up to the maximum limit
    return sortedMemories.slice(0, this.config.maxSharedMemories);
  }

  private adaptMemoryForSharing(
    memory: MemoryEvent,
    sourceNpcId: string,
    targetNpcId: string,
    relationshipValue: number
  ): MemoryEvent {
    // Adjust importance based on relationship strength
    const relationshipFactor = (relationshipValue + 10) / 20; // Normalize to 0-1
    const adjustedImportance = memory.importance * relationshipFactor;

    // Create a new memory event with modified details
    return {
      ...memory,
      participants: [...memory.participants, targetNpcId],
      importance: adjustedImportance,
      details: {
        ...memory.details,
        sharedBy: sourceNpcId,
        originalImportance: memory.importance,
        relationshipAtSharing: relationshipValue
      }
    };
  }
} 