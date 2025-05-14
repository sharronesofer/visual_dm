from typing import Any, Dict, List, Union
from enum import Enum



class MemoryEvent:
    id: str
    timestamp: float
    type: \'MemoryEventType\'
    importance: float
    participants: List[str]
    location?: str
    details: Dict[str, Any]
class MemoryEventType(Enum):
    INTERACTION = 'interaction'
    OBSERVATION = 'observation'
    EXPERIENCE = 'experience'
    INFORMATION = 'information'
    DECISION = 'decision'
    EMOTIONAL = 'emotional'
    ACHIEVEMENT = 'achievement'
    CONFLICT = 'conflict'
    TRADE = 'trade'
    QUEST = 'quest'
    RELATIONSHIP_CHANGE = 'relationship_change'
    FACTION_EVENT = 'faction_event'
    WORLD_EVENT = 'world_event'
    DECEPTION = 'deception'
    COOPERATION = 'cooperation'
    COMPETITION = 'competition'
class NPCMemory:
    npcId: str
    shortTermMemory: List[MemoryEvent]
    longTermMemory: List[MemoryEvent]
    memoryStats: Dict[str, Any]>
}
class MemoryQuery:
    type?: \'MemoryEventType\'
    participants?: List[str]
    requireAllParticipants?: bool
    tags?: List[str]
    matchAllTags?: bool
    minImportance?: float
    limit?: float
class MemoryProcessingResult:
    compressedEvents: List[MemoryEvent]
    significantEvents: List[MemoryEvent]
    forgottenEvents: List[str]
    updatedRelationships: Dict[str, Any]
}
const MEMORY_CONSTANTS = {
  SHORT_TERM_CAPACITY: 50,  
  PROCESSING_INTERVAL: 3600000,  
  IMPORTANCE_THRESHOLD: 70,  
  MEMORY_DECAY_RATE: 0.1,   
  COMPRESSION_THRESHOLD: 3,  
  MAX_MEMORY_AGE: 30 * 24 * 3600000,  
  RELATIONSHIP_DECAY_RATE: 0.05,  
  EMOTIONAL_IMPACT_WEIGHT: 0.3,  
  MEMORY_SHARING_THRESHOLD: 0.7,  
} as const
class ImportanceFactors:
    baseImportance: float
    emotionalImpact: float
    participantCount: float
    relationshipStrength: float
    timeRelevance: float
    eventType: \'MemoryEventType\'
class CompressionStrategy(Enum):
    SUMMARIZE = 'summarize'
    PRUNE = 'prune'
    AGGREGATE = 'aggregate'
class MemoryContext:
    currentLocation?: str
    currentActivity?: str
    emotionalState?: float
    timeOfDay?: float
    recentEvents?: List[str]
    activeFactions?: List[str]
    activeQuests?: List[str]
class Memory:
    id: str
    type: \'MemoryEventType\'
    time: float
    participants: List[str]
    location: str
    details: Dict[str, Any][]
  tags: List[string]
  associatedMemories: List[string]
  lastRecallTime?: float
  recallCount: float
  decayRate: float
}
class MemoryManager:
    getRelevantMemories(
    npcId: str,
    context: str,
    targetId?: str
  ): Awaitable[Memory[]>
    addMemory(
    npcId: Union[str,
    memory: Omit<Memory, 'id', 'recallCount', 'lastRecallTime'>
  ): Awaitable[Memory>]
    updateMemory(
    npcId: str,
    memoryId: str,
    updates: Partial<Memory>
  ): Awaitable[Memory>
    getMemoryById(
    npcId: Union[str,
    memoryId: str
  ): Awaitable[Memory, None>]
    searchMemories(
    npcId: str,
    query: Dict[str, Any]
    }
  ): Promise<Memory[]>
  forgetMemory(
    npcId: str,
    memoryId: str
  ): Promise<boolean>
  calculateMemoryImportance(
    memory: \'Memory\',
    currentContext?: Any
  ): Promise<number>
  associateMemories(
    npcId: str,
    memoryIds: List[string]
  ): Promise<boolean>
} 