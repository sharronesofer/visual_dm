from typing import Any, Dict, List
from enum import Enum


class MemoryType(Enum):
    EVENT = 'event'
    INTERACTION = 'interaction'
    KNOWLEDGE = 'knowledge'
    RUMOR = 'rumor'
    BACKSTORY = 'backstory'
    KEYSTONE = 'keystone'
class MemoryLayer(Enum):
    IMMEDIATE = 'immediate'
    SHORT_TERM = 'short_term'
    MEDIUM_TERM = 'medium_term'
    LONG_TERM = 'long_term'
    PERMANENT = 'permanent'
class Memory:
    id: str
    npcId: str
    type: \'MemoryType\'
    layer: \'MemoryLayer\'
    content: str
    timestamp: Date
    lastAccessed: Date
    importance: float
    clarity: float
    emotionalImpact: float
    tags: List[str]
    relatedNpcIds?: List[str]
    relatedFactions?: List[FactionType]
    location?: str
    context?: Dict[str, Any>
class MemorySummary:
    id: str
    sourceMemoryIds: List[str]
    content: str
    layer: \'MemoryLayer\'
    timestamp: Date
    importance: float
    tags: List[str]
class NPCKnowledge:
    npcId: str
    backstory: Dict[str, Any>
    memories: Dict[MemoryLayer, Memory[]>
    summaries: Dict[MemoryLayer, MemorySummary[]>
    lastUpdate: Date
class MemoryConfig:
    maxMemoriesPerLayer: Dict[MemoryLayer, float>
    decayRates: Dict[MemoryLayer, float>
    promotionThresholds: Dict[MemoryLayer, float>
    importanceThresholds: Dict[str, Any]
class MemoryQueryOptions:
    types?: List[MemoryType]
    layers?: List[MemoryLayer]
    minImportance?: float
    minClarity?: float
    tags?: List[str]
    relatedNpcIds?: List[str]
    relatedFactions?: List[FactionType]
    startDate?: Date
    endDate?: Date
    location?: str
    limit?: float 