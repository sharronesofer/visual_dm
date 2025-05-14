from typing import Any, Dict, List



class Memory:
    id: str
    type: MemoryEventType
    participants: List[str]
    timestamp: float
    details: Any
    importance: float
    tags: List[str]
    relatedMemories?: List[str]
class MemoryQuery:
    type?: MemoryEventType
    participants?: List[str]
    timeRange?: {
    start: float
    end: float
  importance?: {
    min?: float
    max?: float
  }
  tags?: string[]
  limit?: float
}
class MemoryManager {
  private memories: Map<string, Memory>
  private npcMemories: Map<string, Set<string>>
  constructor() {
    this.memories = new Map()
    this.npcMemories = new Map()
  }
  public async createMemory(params: Dict[str, Any]): Promise<Memory> {
    const memory: \'Memory\' = {
      id: this.generateMemoryId(),
      type: params.type,
      participants: params.participants,
      timestamp: Date.now(),
      details: params.details,
      importance: params.importance,
      tags: params.tags || []
    }
    this.memories.set(memory.id, memory)
    params.participants.forEach(participantId => {
      if (!this.npcMemories.has(participantId)) {
        this.npcMemories.set(participantId, new Set())
      }
      this.npcMemories.get(participantId)?.add(memory.id)
    })
    memory.relatedMemories = await this.findRelatedMemories(memory)
    return memory
  }
  public getMemory(id: str): \'Memory\' | undefined {
    return this.memories.get(id)
  }
  public getNPCMemories(npcId: str, query?: MemoryQuery): Memory[] {
    const memoryIds = this.npcMemories.get(npcId) || new Set()
    let memories = Array.from(memoryIds)
      .map(id => this.memories.get(id))
      .filter((memory): memory is Memory => memory !== undefined)
    if (query) {
      memories = this.filterMemories(memories, query)
    }
    return memories
  }
  private filterMemories(memories: List[Memory], query: MemoryQuery): Memory[] {
    return memories.filter(memory => {
      if (query.type && memory.type !== query.type) return false
      if (query.participants && !query.participants.every(p => memory.participants.includes(p))) {
        return false
      }
      if (query.timeRange) {
        if (memory.timestamp < query.timeRange.start || memory.timestamp > query.timeRange.end) {
          return false
        }
      }
      if (query.importance) {
        if (query.importance.min !== undefined && memory.importance < query.importance.min) {
          return false
        }
        if (query.importance.max !== undefined && memory.importance > query.importance.max) {
          return false
        }
      }
      if (query.tags && !query.tags.every(tag => memory.tags.includes(tag))) {
        return false
      }
      return true
    }).slice(0, query.limit)
  }
  private async findRelatedMemories(memory: Memory): Promise<string[]> {
    const relatedMemories = new Set<string>()
    memory.participants.forEach(participantId => {
      const participantMemories = this.npcMemories.get(participantId) || new Set()
      participantMemories.forEach(memoryId => {
        if (memoryId !== memory.id) {
          const otherMemory = this.memories.get(memoryId)
          if (otherMemory && this.areMemoriesRelated(memory, otherMemory)) {
            relatedMemories.add(memoryId)
          }
        }
      })
    })
    return Array.from(relatedMemories)
  }
  private areMemoriesRelated(memory1: \'Memory\', memory2: Memory): bool {
    const timeThreshold = 24 * 60 * 60 * 1000 
    if (Math.abs(memory1.timestamp - memory2.timestamp) > timeThreshold) {
      return false
    }
    const sharedTags = memory1.tags.filter(tag => memory2.tags.includes(tag))
    if (sharedTags.length > 0) {
      return true
    }
    if (memory1.type === memory2.type) {
      return true
    }
    const relatedTypes = this.getRelatedMemoryTypes(memory1.type)
    if (relatedTypes.includes(memory2.type)) {
      return true
    }
    return false
  }
  private getRelatedMemoryTypes(type: MemoryEventType): MemoryEventType[] {
    const relationMap: Dict[str, Any] = {
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
    }
    return relationMap[type] || []
  }
  private generateMemoryId(): str {
    return `mem_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  }
} 