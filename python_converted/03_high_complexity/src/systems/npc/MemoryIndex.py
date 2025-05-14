from typing import Any, List



class MemoryIndexEntry:
    eventId: str
    npcId: str
    timestamp: float
    importance: float
    type: MemoryEventType
    tags: Set[str>
    participants: Set[str>
class MemoryIndexConfig:
    maxIndexSize?: float
    indexUpdateInterval?: float
    enableCache?: bool
/**
 * Optimized memory indexing system for fast retrieval and searching
 * across large NPC populations
 */
class MemoryIndex {
  private index: Map<string, MemoryIndexEntry>
  private typeIndex: Map<MemoryEventType, Set<string>>
  private participantIndex: Map<string, Set<string>>
  private tagIndex: Map<string, Set<string>>
  private importanceIndex: Map<string, number>
  private config: Required<MemoryIndexConfig>
  constructor(config: \'MemoryIndexConfig\' = {}) {
    this.config = {
      maxIndexSize: 100000,
      indexUpdateInterval: 60000, 
      enableCache: true,
      ...config
    }
    this.index = new Map()
    this.typeIndex = new Map()
    this.participantIndex = new Map()
    this.tagIndex = new Map()
    this.importanceIndex = new Map()
  }
  /**
   * Add a memory event to the index
   */
  public addMemory(npcId: str, event: MemoryEvent): void {
    const entry: \'MemoryIndexEntry\' = {
      eventId: event.id,
      npcId,
      timestamp: event.timestamp,
      importance: event.importance,
      type: event.type,
      tags: new Set(event.tags),
      participants: new Set(event.participants)
    }
    this.index.set(event.id, entry)
    this.importanceIndex.set(event.id, event.importance)
    if (!this.typeIndex.has(event.type)) {
      this.typeIndex.set(event.type, new Set())
    }
    this.typeIndex.get(event.type)!.add(event.id)
    event.participants.forEach(participant => {
      if (!this.participantIndex.has(participant)) {
        this.participantIndex.set(participant, new Set())
      }
      this.participantIndex.get(participant)!.add(event.id)
    })
    event.tags.forEach(tag => {
      if (!this.tagIndex.has(tag)) {
        this.tagIndex.set(tag, new Set())
      }
      this.tagIndex.get(tag)!.add(event.id)
    })
    if (this.index.size > this.config.maxIndexSize) {
      this.pruneIndex()
    }
  }
  /**
   * Remove a memory event from the index
   */
  public removeMemory(eventId: str): void {
    const entry = this.index.get(eventId)
    if (!entry) return
    this.typeIndex.get(entry.type)?.delete(eventId)
    entry.participants.forEach(participant => {
      this.participantIndex.get(participant)?.delete(eventId)
    })
    entry.tags.forEach(tag => {
      this.tagIndex.get(tag)?.delete(eventId)
    })
    this.importanceIndex.delete(eventId)
    this.index.delete(eventId)
  }
  /**
   * Find memories by type and importance threshold
   */
  public findMemoriesByType(
    type: MemoryEventType,
    minImportance: float = 0
  ): string[] {
    const typeMemories = this.typeIndex.get(type)
    if (!typeMemories) return []
    return Array.from(typeMemories).filter(
      id => this.importanceIndex.get(id)! >= minImportance
    )
  }
  /**
   * Find memories involving specific participants
   */
  public findMemoriesByParticipants(
    participants: List[string],
    requireAll: bool = false
  ): string[] {
    if (participants.length === 0) return []
    const memorySets = participants
      .map(p => this.participantIndex.get(p))
      .filter((set): set is Set<string> => set !== undefined)
    if (memorySets.length === 0) return []
    if (requireAll) {
      return Array.from(memorySets[0]).filter(id =>
        memorySets.every(set => set.has(id))
      )
    } else {
      const result = new Set<string>()
      memorySets.forEach(set => {
        set.forEach(id => result.add(id))
      })
      return Array.from(result)
    }
  }
  /**
   * Find memories by tags
   */
  public findMemoriesByTags(
    tags: List[string],
    matchAll: bool = false
  ): string[] {
    if (tags.length === 0) return []
    const memorySets = tags
      .map(t => this.tagIndex.get(t))
      .filter((set): set is Set<string> => set !== undefined)
    if (memorySets.length === 0) return []
    if (matchAll) {
      return Array.from(memorySets[0]).filter(id =>
        memorySets.every(set => set.has(id))
      )
    } else {
      const result = new Set<string>()
      memorySets.forEach(set => {
        set.forEach(id => result.add(id))
      })
      return Array.from(result)
    }
  }
  /**
   * Find recent memories for an NPC
   */
  public findRecentMemories(
    npcId: str,
    limit: float = 10,
    minImportance: float = 0
  ): string[] {
    return Array.from(this.index.values())
      .filter(
        entry =>
          entry.npcId === npcId &&
          entry.importance >= minImportance
      )
      .sort((a, b) => b.timestamp - a.timestamp)
      .slice(0, limit)
      .map(entry => entry.eventId)
  }
  /**
   * Remove least important memories when index size exceeds limit
   */
  private pruneIndex(): void {
    const entriesToRemove = Math.floor(this.config.maxIndexSize * 0.2)
    const sortedMemories = Array.from(this.index.values())
      .sort((a, b) => a.importance - b.importance)
      .slice(0, entriesToRemove)
    sortedMemories.forEach(entry => {
      this.removeMemory(entry.eventId)
    })
  }
} 