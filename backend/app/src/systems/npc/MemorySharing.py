from typing import Any, Dict, List


class MemorySharingConfig:
    sharingThreshold: float
    maxSharedMemories: float
    proximityThreshold: float
    sharingProbability: float
const DEFAULT_SHARING_CONFIG: \'MemorySharingConfig\' = {
  sharingThreshold: 2,
  maxSharedMemories: 5,
  proximityThreshold: 10,
  sharingProbability: 0.3
}
class MemorySharing {
  private config: \'MemorySharingConfig\'
  private memoryManager: MemoryManager
  constructor(memoryManager: MemoryManager, config: Partial<MemorySharingConfig> = {}) {
    this.memoryManager = memoryManager
    this.config = { ...DEFAULT_SHARING_CONFIG, ...config }
  }
  public shareMemories(
    sourceNpcId: str,
    targetNpcId: str,
    relationship: NPCRelationship,
    distance: float
  ): MemoryEvent[] {
    if (!this.shouldShareMemories(relationship.value, distance)) {
      return []
    }
    const sourceMemories = this.memoryManager.queryMemories({
      npcId: sourceNpcId,
      importance: Dict[str, Any]
    })
    const memoriesToShare = this.selectMemoriesToShare(sourceMemories)
    const sharedMemories = memoriesToShare.map(memory => this.adaptMemoryForSharing(
      memory,
      sourceNpcId,
      targetNpcId,
      relationship.value
    ))
    sharedMemories.forEach(memory => {
      this.memoryManager.addMemoryEvent({
        ...memory,
        type: MemoryEventType.INTERACTION,
        details: Dict[str, Any]
      })
    })
    return sharedMemories
  }
  private shouldShareMemories(relationshipValue: float, distance: float): bool {
    if (relationshipValue < this.config.sharingThreshold) return false
    if (distance > this.config.proximityThreshold) return false
    const relationshipFactor = (relationshipValue + 10) / 20 
    const distanceFactor = 1 - (distance / this.config.proximityThreshold)
    const probability = this.config.sharingProbability * relationshipFactor * distanceFactor
    return Math.random() < probability
  }
  private selectMemoriesToShare(memories: List[MemoryEvent]): MemoryEvent[] {
    const sortedMemories = [...memories].sort((a, b) => {
      const importanceDiff = b.importance - a.importance
      if (importanceDiff !== 0) return importanceDiff
      return b.timestamp - a.timestamp
    })
    return sortedMemories.slice(0, this.config.maxSharedMemories)
  }
  private adaptMemoryForSharing(
    memory: MemoryEvent,
    sourceNpcId: str,
    targetNpcId: str,
    relationshipValue: float
  ): MemoryEvent {
    const relationshipFactor = (relationshipValue + 10) / 20 
    const adjustedImportance = memory.importance * relationshipFactor
    return {
      ...memory,
      participants: [...memory.participants, targetNpcId],
      importance: adjustedImportance,
      details: Dict[str, Any]
    }
  }
} 