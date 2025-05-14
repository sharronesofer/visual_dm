"""
Memory system models for NPCs and world state.
"""

from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from enum import Enum

class MemoryType(str, Enum):
    """Types of memories that can be stored."""
    EVENT = "event"
    INTERACTION = "interaction"
    KNOWLEDGE = "knowledge"
    RUMOR = "rumor"
    BACKSTORY = "backstory"
    KEYSTONE = "keystone"

class MemoryLayer(str, Enum):
    """Layers of memory storage."""
    IMMEDIATE = "immediate"  # 1 day
    SHORT_TERM = "short_term"  # 7 days
    MEDIUM_TERM = "medium_term"  # 4 weeks
    LONG_TERM = "long_term"  # 12 months
    PERMANENT = "permanent"

class Memory(BaseModel):
    """Base memory model."""
    id: str
    type: MemoryType
    content: Dict
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source: str
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    layer: MemoryLayer = Field(default=MemoryLayer.IMMEDIATE)
    is_keystone: bool = Field(default=False)
    tags: List[str] = Field(default_factory=list)
    metadata: Dict = Field(default_factory=dict)

    def should_promote(self) -> bool:
        """Determine if this memory should be promoted to the next layer."""
        if self.layer == MemoryLayer.PERMANENT or self.is_keystone:
            return False
            
        age = datetime.utcnow() - self.timestamp
        if self.layer == MemoryLayer.IMMEDIATE and age >= timedelta(days=1):
            return True
        elif self.layer == MemoryLayer.SHORT_TERM and age >= timedelta(days=7):
            return True
        elif self.layer == MemoryLayer.MEDIUM_TERM and age >= timedelta(days=28):
            return True
        elif self.layer == MemoryLayer.LONG_TERM and age >= timedelta(days=365):
            return True
        return False

class MemorySummary(BaseModel):
    """Summary of multiple memories for promotion to next layer."""
    id: str
    source_memory_ids: List[str]
    content: Dict
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    layer: MemoryLayer
    tags: List[str] = Field(default_factory=list)
    metadata: Dict = Field(default_factory=dict)

class NPCKnowledge(BaseModel):
    """NPC's knowledge base including memories and backstory."""
    npc_id: str
    backstory: Dict
    memories: Dict[MemoryLayer, List[Memory]] = Field(default_factory=lambda: {
        layer: [] for layer in MemoryLayer
    })
    summaries: Dict[MemoryLayer, List[MemorySummary]] = Field(default_factory=lambda: {
        layer: [] for layer in MemoryLayer
    })
    last_update: datetime = Field(default_factory=datetime.utcnow)

    def add_memory(self, memory: Memory):
        """Add a new memory to the appropriate layer."""
        self.memories[memory.layer].append(memory)
        self.last_update = datetime.utcnow()

    def promote_memories(self):
        """Promote memories that have aged enough to the next layer."""
        for layer in [MemoryLayer.IMMEDIATE, MemoryLayer.SHORT_TERM, 
                     MemoryLayer.MEDIUM_TERM, MemoryLayer.LONG_TERM]:
            memories_to_promote = [m for m in self.memories[layer] if m.should_promote()]
            if memories_to_promote:
                # Create summary and move to next layer
                summary = MemorySummary(
                    id=f"summary_{datetime.utcnow().timestamp()}",
                    source_memory_ids=[m.id for m in memories_to_promote],
                    content=self._summarize_memories(memories_to_promote),
                    layer=MemoryLayer(layer.value)
                )
                next_layer = MemoryLayer(list(MemoryLayer).index(layer) + 1)
                self.summaries[next_layer].append(summary)
                # Remove promoted memories
                self.memories[layer] = [m for m in self.memories[layer] 
                                      if m not in memories_to_promote]

    def _summarize_memories(self, memories: List[Memory]) -> Dict:
        """Create a summary of multiple memories."""
        # This would be where we call GPT to summarize the memories
        # For now, return a simple summary
        return {
            "summary": f"Summary of {len(memories)} memories",
            "key_points": [m.content.get("key_point", "") for m in memories],
            "timestamp": datetime.utcnow().isoformat()
        } 