import { MemoryEventType } from '../../types/npc/memory';
import { EventBus as CoreEventBus } from '../../core/interfaces/types/events';
import { POIEvents } from '../../poi/types/POIEvents';
import { TypedEventEmitter } from '../../utils/TypedEventEmitter';

export interface Memory {
  id: string;
  type: MemoryEventType;
  participants: string[];
  timestamp: number;
  details: any;
  importance: number;
  tags: string[];
  relatedMemories?: string[];
}

export interface MemoryQuery {
  type?: MemoryEventType;
  participants?: string[];
  timeRange?: {
    start: number;
    end: number;
  };
  importance?: {
    min?: number;
    max?: number;
  };
  tags?: string[];
  limit?: number;
}

// Use a typed EventBus for POI events
const POIEventBus = CoreEventBus.getInstance() as TypedEventEmitter<POIEvents>;

// Subscribe to POI evolution events for Memory system integration
POIEventBus.on('poi:evolved', ({ poiId, poi, trigger, changes, version }) => {
  // Example: Log the event
  console.log(`[Memory Integration] Recording POI evolution event for POI ${poiId}, trigger: ${trigger}`);
  // TODO: Record this as a MemoryEvent for historical tracking
  // For example, create a new memory entry with details of the evolution
});

export class MemoryManager {
  private memories: Map<string, Memory>;
  private npcMemories: Map<string, Set<string>>;

  constructor() {
    this.memories = new Map();
    this.npcMemories = new Map();
  }

  public async createMemory(params: {
    type: MemoryEventType;
    participants: string[];
    details: any;
    importance: number;
    tags?: string[];
  }): Promise<Memory> {
    const memory: Memory = {
      id: this.generateMemoryId(),
      type: params.type,
      participants: params.participants,
      timestamp: Date.now(),
      details: params.details,
      importance: params.importance,
      tags: params.tags || []
    };

    // Store the memory
    this.memories.set(memory.id, memory);

    // Index by participants
    params.participants.forEach(participantId => {
      if (!this.npcMemories.has(participantId)) {
        this.npcMemories.set(participantId, new Set());
      }
      this.npcMemories.get(participantId)?.add(memory.id);
    });

    // Find and link related memories
    memory.relatedMemories = await this.findRelatedMemories(memory);

    return memory;
  }

  public getMemory(id: string): Memory | undefined {
    return this.memories.get(id);
  }

  public getNPCMemories(npcId: string, query?: MemoryQuery): Memory[] {
    const memoryIds = this.npcMemories.get(npcId) || new Set();
    let memories = Array.from(memoryIds)
      .map(id => this.memories.get(id))
      .filter((memory): memory is Memory => memory !== undefined);

    if (query) {
      memories = this.filterMemories(memories, query);
    }

    return memories;
  }

  private filterMemories(memories: Memory[], query: MemoryQuery): Memory[] {
    return memories.filter(memory => {
      // Filter by type
      if (query.type && memory.type !== query.type) return false;

      // Filter by participants
      if (query.participants && !query.participants.every(p => memory.participants.includes(p))) {
        return false;
      }

      // Filter by time range
      if (query.timeRange) {
        if (memory.timestamp < query.timeRange.start || memory.timestamp > query.timeRange.end) {
          return false;
        }
      }

      // Filter by importance
      if (query.importance) {
        if (query.importance.min !== undefined && memory.importance < query.importance.min) {
          return false;
        }
        if (query.importance.max !== undefined && memory.importance > query.importance.max) {
          return false;
        }
      }

      // Filter by tags
      if (query.tags && !query.tags.every(tag => memory.tags.includes(tag))) {
        return false;
      }

      return true;
    }).slice(0, query.limit);
  }

  private async findRelatedMemories(memory: Memory): Promise<string[]> {
    const relatedMemories = new Set<string>();

    // Find memories with same participants
    memory.participants.forEach(participantId => {
      const participantMemories = this.npcMemories.get(participantId) || new Set();
      participantMemories.forEach(memoryId => {
        if (memoryId !== memory.id) {
          const otherMemory = this.memories.get(memoryId);
          if (otherMemory && this.areMemoriesRelated(memory, otherMemory)) {
            relatedMemories.add(memoryId);
          }
        }
      });
    });

    return Array.from(relatedMemories);
  }

  private areMemoriesRelated(memory1: Memory, memory2: Memory): boolean {
    // Check if memories are within 24 hours of each other
    const timeThreshold = 24 * 60 * 60 * 1000; // 24 hours in milliseconds
    if (Math.abs(memory1.timestamp - memory2.timestamp) > timeThreshold) {
      return false;
    }

    // Check for shared tags
    const sharedTags = memory1.tags.filter(tag => memory2.tags.includes(tag));
    if (sharedTags.length > 0) {
      return true;
    }

    // Check for same type
    if (memory1.type === memory2.type) {
      return true;
    }

    // Check for related types
    const relatedTypes = this.getRelatedMemoryTypes(memory1.type);
    if (relatedTypes.includes(memory2.type)) {
      return true;
    }

    return false;
  }

  private getRelatedMemoryTypes(type: MemoryEventType): MemoryEventType[] {
    // Define related memory types
    const relationMap: { [key in MemoryEventType]?: MemoryEventType[] } = {
      [MemoryEventType.INTERACTION]: [
        MemoryEventType.RELATIONSHIP_CHANGE,
        MemoryEventType.DECEPTION,
        MemoryEventType.COOPERATION,
        MemoryEventType.COMPETITION
      ],
      [MemoryEventType.TRADE]: [
        MemoryEventType.INTERACTION,
        MemoryEventType.RELATIONSHIP_CHANGE
      ],
      [MemoryEventType.DECEPTION]: [
        MemoryEventType.INTERACTION,
        MemoryEventType.RELATIONSHIP_CHANGE
      ],
      [MemoryEventType.COOPERATION]: [
        MemoryEventType.INTERACTION,
        MemoryEventType.RELATIONSHIP_CHANGE,
        MemoryEventType.FACTION_EVENT
      ],
      [MemoryEventType.COMPETITION]: [
        MemoryEventType.INTERACTION,
        MemoryEventType.RELATIONSHIP_CHANGE,
        MemoryEventType.CONFLICT
      ]
    };

    return relationMap[type] || [];
  }

  private generateMemoryId(): string {
    return `mem_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
} 