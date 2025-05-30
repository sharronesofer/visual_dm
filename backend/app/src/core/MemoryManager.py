from typing import Any, Dict, List


  Memory,
  MemoryType,
  MemoryLayer,
  MemorySummary,
  NPCKnowledge,
  MemoryConfig,
  MemoryQueryOptions
} from '../types/memory'
const DEFAULT_CONFIG: MemoryConfig = {
  maxMemoriesPerLayer: Dict[str, Any],
  decayRates: Dict[str, Any],
  promotionThresholds: Dict[str, Any],
  importanceThresholds: Dict[str, Any],
  compressionRatio: 0.5,
  minClarityThreshold: 0.2
}
class MemoryManager {
  private knowledge: NPCKnowledge
  private config: MemoryConfig
  constructor(npcId: str, config: Partial<MemoryConfig> = {}) {
    this.config = { ...DEFAULT_CONFIG, ...config }
    this.knowledge = {
      npcId,
      backstory: {},
      memories: Dict[str, Any],
      summaries: Dict[str, Any],
      lastUpdate: new Date()
    }
  }
  public addMemory(
    content: str,
    type: MemoryType,
    options: Dict[str, Any] = {}
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
    }
    this.knowledge.memories[MemoryLayer.IMMEDIATE].push(memory)
    this.enforceLayerLimit(MemoryLayer.IMMEDIATE)
    this.knowledge.lastUpdate = new Date()
    return memory
  }
  public queryMemories(options: MemoryQueryOptions = {}): Memory[] {
    let memories = this.getAllMemories()
    if (options.types?.length) {
      memories = memories.filter(m => options.types!.includes(m.type))
    }
    if (options.layers?.length) {
      memories = memories.filter(m => options.layers!.includes(m.layer))
    }
    if (options.minImportance !== undefined) {
      memories = memories.filter(m => m.importance >= options.minImportance!)
    }
    if (options.minClarity !== undefined) {
      memories = memories.filter(m => m.clarity >= options.minClarity!)
    }
    if (options.tags?.length) {
      memories = memories.filter(m => 
        options.tags!.some(tag => m.tags.includes(tag))
      )
    }
    if (options.relatedNpcIds?.length) {
      memories = memories.filter(m => 
        m.relatedNpcIds?.some(id => options.relatedNpcIds!.includes(id))
      )
    }
    if (options.relatedFactions?.length) {
      memories = memories.filter(m => 
        m.relatedFactions?.some(f => options.relatedFactions!.includes(f))
      )
    }
    if (options.startDate) {
      memories = memories.filter(m => m.timestamp >= options.startDate!)
    }
    if (options.endDate) {
      memories = memories.filter(m => m.timestamp <= options.endDate!)
    }
    if (options.location) {
      memories = memories.filter(m => m.location === options.location)
    }
    memories.sort((a, b) => {
      const importanceDiff = b.importance - a.importance
      if (importanceDiff !== 0) return importanceDiff
      return b.timestamp.getTime() - a.timestamp.getTime()
    })
    if (options.limit) {
      memories = memories.slice(0, options.limit)
    }
    memories.forEach(m => {
      m.lastAccessed = new Date()
    })
    return memories
  }
  public update(): void {
    this.decayMemories()
    this.promoteMemories()
    this.compressMemories()
    this.knowledge.lastUpdate = new Date()
  }
  private getAllMemories(): Memory[] {
    return Object.values(this.knowledge.memories).flat()
  }
  private calculateImportance(
    content: str,
    type: MemoryType,
    options: Dict[str, Any]
  ): float {
    let importance = 0
    switch (type) {
      case MemoryType.KEYSTONE:
        importance += 0.8
        break
      case MemoryType.BACKSTORY:
        importance += 0.7
        break
      case MemoryType.EVENT:
        importance += 0.6
        break
      case MemoryType.INTERACTION:
        importance += 0.5
        break
      case MemoryType.KNOWLEDGE:
        importance += 0.4
        break
      case MemoryType.RUMOR:
        importance += 0.3
        break
    }
    if (options.emotionalImpact) {
      importance += Math.min(0.3, Math.abs(options.emotionalImpact) * 0.3)
    }
    if (options.relatedNpcIds?.length) {
      importance += Math.min(0.2, options.relatedNpcIds.length * 0.05)
    }
    if (options.relatedFactions?.length) {
      importance += Math.min(0.2, options.relatedFactions.length * 0.1)
    }
    return Math.min(1, Math.max(0, importance))
  }
  private decayMemories(): void {
    for (const layer of Object.values(MemoryLayer)) {
      const decayRate = this.config.decayRates[layer]
      this.knowledge.memories[layer].forEach(memory => {
        const hoursSinceLastAccess = 
          (new Date().getTime() - memory.lastAccessed.getTime()) / (1000 * 60 * 60)
        memory.clarity = Math.max(
          0,
          memory.clarity - (decayRate * hoursSinceLastAccess / 24)
        )
      })
    }
  }
  private promoteMemories(): void {
    for (const layer of [
      MemoryLayer.IMMEDIATE,
      MemoryLayer.SHORT_TERM,
      MemoryLayer.MEDIUM_TERM,
      MemoryLayer.LONG_TERM
    ]) {
      const nextLayer = this.getNextLayer(layer)
      const threshold = this.config.promotionThresholds[layer]
      const memoriesToPromote = this.knowledge.memories[layer].filter(memory => {
        const hoursOld = 
          (new Date().getTime() - memory.timestamp.getTime()) / (1000 * 60 * 60)
        return (
          hoursOld >= threshold &&
          memory.importance >= this.config.importanceThresholds.medium
        )
      })
      if (memoriesToPromote.length > 0) {
        const summary: MemorySummary = {
          id: uuidv4(),
          sourceMemoryIds: memoriesToPromote.map(m => m.id),
          content: this.summarizeMemories(memoriesToPromote),
          layer: nextLayer,
          timestamp: new Date(),
          importance: this.calculateSummaryImportance(memoriesToPromote),
          tags: this.aggregateTags(memoriesToPromote)
        }
        this.knowledge.memories[nextLayer].push(...memoriesToPromote)
        this.knowledge.summaries[nextLayer].push(summary)
        this.knowledge.memories[layer] = this.knowledge.memories[layer].filter(
          m => !memoriesToPromote.includes(m)
        )
      }
    }
  }
  private compressMemories(): void {
    for (const layer of Object.values(MemoryLayer)) {
      const memories = this.knowledge.memories[layer]
      const maxMemories = this.config.maxMemoriesPerLayer[layer]
      if (memories.length > maxMemories) {
        const numToCompress = Math.floor(
          (memories.length - maxMemories) * this.config.compressionRatio
        )
        if (numToCompress > 1) {
          const compressed = this.findAndCompressMemories(
            memories,
            numToCompress
          )
          this.knowledge.memories[layer] = compressed
        }
      }
    }
  }
  private enforceLayerLimit(layer: MemoryLayer): void {
    const memories = this.knowledge.memories[layer]
    const maxMemories = this.config.maxMemoriesPerLayer[layer]
    if (memories.length > maxMemories) {
      memories.sort((a, b) => b.importance - a.importance)
      this.knowledge.memories[layer] = memories.slice(0, maxMemories)
    }
  }
  private getNextLayer(layer: MemoryLayer): MemoryLayer {
    const layers = Object.values(MemoryLayer)
    const currentIndex = layers.indexOf(layer)
    return layers[currentIndex + 1]
  }
  private summarizeMemories(memories: List[Memory]): str {
    return memories
      .sort((a, b) => b.importance - a.importance)
      .map(m => m.content)
      .join(' | ')
  }
  private calculateSummaryImportance(memories: List[Memory]): float {
    const totalWeight = memories.reduce(
      (sum, m) => sum + (1 + Math.abs(m.emotionalImpact)),
      0
    )
    const weightedSum = memories.reduce(
      (sum, m) => sum + m.importance * (1 + Math.abs(m.emotionalImpact)),
      0
    )
    return weightedSum / totalWeight
  }
  private aggregateTags(memories: List[Memory]): string[] {
    return [...new Set(memories.flatMap(m => m.tags))]
  }
  private findAndCompressMemories(
    memories: List[Memory],
    targetReduction: float
  ): Memory[] {
    const groups: List[Memory][] = []
    const used = new Set<string>()
    for (const memory of memories) {
      if (used.has(memory.id)) continue
      const group = [memory]
      used.add(memory.id)
      for (const other of memories) {
        if (used.has(other.id)) continue
        const isSimilar = this.areMemoriesSimilar(memory, other)
        if (isSimilar) {
          group.push(other)
          used.add(other.id)
        }
      }
      if (group.length > 1) {
        groups.push(group)
      }
    }
    const compressed: List[Memory] = []
    let reductionAchieved = 0
    memories
      .filter(m => !used.has(m.id))
      .forEach(m => compressed.push(m))
    groups
      .sort((a, b) => b.length - a.length)
      .forEach(group => {
        if (reductionAchieved < targetReduction) {
          compressed.push(this.mergeMemories(group))
          reductionAchieved += group.length - 1
        } else {
          group.forEach(m => compressed.push(m))
        }
      })
    return compressed
  }
  private areMemoriesSimilar(a: Memory, b: Memory): bool {
    const timeThreshold = 24 * 60 * 60 * 1000 
    const timeDiff = Math.abs(a.timestamp.getTime() - b.timestamp.getTime())
    const hasCommonTags = a.tags.some(tag => b.tags.includes(tag))
    const sameType = a.type === b.type
    const sameLocation = a.location === b.location
    const hasCommonNPCs = a.relatedNpcIds?.some(
      id => b.relatedNpcIds?.includes(id)
    )
    const hasCommonFactions = a.relatedFactions?.some(
      f => b.relatedFactions?.includes(f)
    )
    return (
      timeDiff <= timeThreshold &&
      sameType &&
      (hasCommonTags || sameLocation || hasCommonNPCs || hasCommonFactions)
    )
  }
  private mergeMemories(memories: List[Memory]): Memory {
    const base = memories[0]
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
    }
  }
  private mergeContexts(
    memories: List[Memory]
  ): Record<string, any> | undefined {
    const contexts = memories
      .map(m => m.context)
      .filter((c): c is Record<string, any> => c !== undefined)
    if (contexts.length === 0) return undefined
    return contexts.reduce((merged, context) => ({
      ...merged,
      ...context
    }), {})
  }
} 