"""
Memory System for the DM module.

This module implements entity-level memory with relevance scoring and decay mechanics,
following the repository pattern described in the Development Bible.
"""

from typing import Dict, Any, List, Optional, Union
import logging
from datetime import datetime, timedelta
import json
import math
from uuid import uuid4
# from firebase_admin import db  # TODO: Replace with proper database integration
from pydantic import BaseModel, Field, ConfigDict

# TODO: Replace with proper event integration when dm module is available
# from backend.systems.dm.event_integration import (
#     EventDispatcher, MemoryEvent
# )

# ===== Memory Models =====

class Memory(BaseModel):
    """
    Represents a single memory for an entity.
    """
    id: str = Field(default_factory=lambda: str(uuid4()))
    entity_id: str
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    accessed_at: Optional[datetime] = None
    relevance_score: float = 1.0  # 0.0 to 1.0
    is_core: bool = False
    category: str = "general"
    tags: List[str] = []
    metadata: Dict[str, Any] = {}
    
    model_config = ConfigDict(arbitrary_types_allowed=True)

class MemorySummary(BaseModel):
    """
    Summarized version of entity memories for narrative context.
    """
    entity_id: str
    summary: str
    core_memories: List[str]
    recent_memories: List[str]
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# ===== Memory Manager =====

class MemoryManager:
    """
    Singleton manager for entity memory operations.
    
    Implements the repository pattern with relevance scoring and decay mechanics.
    """
    _instance = None
    
    @classmethod
    def get_instance(cls):
        """Get the singleton instance of the MemoryManager."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        """Initialize the memory manager."""
        if MemoryManager._instance is not None:
            raise Exception("This class is a singleton. Use get_instance() instead.")
        
        MemoryManager._instance = self
        # TODO: Initialize event dispatcher when dm module is available
        # self.event_dispatcher = EventDispatcher.get_instance()
        self.event_dispatcher = None
        
        # Memory decay settings
        self.decay_rate = 0.05  # 5% decay per day
        self.relevance_threshold = 0.2  # Memories below this are candidates for forgetting
        
        # Cache settings
        self.memory_cache = {}
        self.cache_ttl = timedelta(minutes=5)
        self.cache_timestamps = {}
    
    def create_memory(self, entity_id: str, content: str, is_core: bool = False,
                     category: str = "general", tags: List[str] = None,
                     metadata: Dict[str, Any] = None) -> Memory:
        """
        Create a new memory for an entity.
        
        Args:
            entity_id: The ID of the entity
            content: The memory content
            is_core: Whether this is a core memory (doesn't decay)
            category: The memory category
            tags: Optional tags for the memory
            metadata: Optional metadata for the memory
            
        Returns:
            The created Memory object
        """
        memory = Memory(
            entity_id=entity_id,
            content=content,
            is_core=is_core,
            category=category,
            tags=tags or [],
            metadata=metadata or {}
        )
        
        # Store in Firebase
        self._store_memory(memory)
        
        # Clear cache for this entity
        self._clear_entity_cache(entity_id)
        
        # TODO: Emit event when event system is available
        # self.event_dispatcher.publish(MemoryEvent(
        #     event_type="memory.created",
        #     entity_id=entity_id,
        #     memory_id=memory.id,
        #     operation="created",
        #     memory_data=memory.dict()
        # ))
        
        return memory
    
    def get_memory(self, memory_id: str, entity_id: str) -> Optional[Memory]:
        """
        Get a specific memory by ID.
        
        Args:
            memory_id: The ID of the memory
            entity_id: The ID of the entity
            
        Returns:
            The Memory object or None if not found
        """
        # Check cache first
        if self._is_entity_cached(entity_id):
            memory_dict = self._get_memory_from_cache(entity_id, memory_id)
            if memory_dict:
                return Memory(**memory_dict)
        
        # Fetch from Firebase
        memory_ref = db.reference(f"/entity_memory/{entity_id}/memories/{memory_id}")
        memory_data = memory_ref.get()
        
        if not memory_data:
            return None
        
        # Convert string dates to datetime
        memory_data["created_at"] = datetime.fromisoformat(memory_data["created_at"])
        memory_data["updated_at"] = datetime.fromisoformat(memory_data["updated_at"])
        if memory_data.get("accessed_at"):
            memory_data["accessed_at"] = datetime.fromisoformat(memory_data["accessed_at"])
        
        # Update accessed_at
        memory = Memory(**memory_data)
        memory.accessed_at = datetime.utcnow()
        
        # Update in Firebase
        memory_ref.update({"accessed_at": memory.accessed_at.isoformat()})
        
        return memory
    
    def get_all_memories(self, entity_id: str, include_decayed: bool = False) -> List[Memory]:
        """
        Get all memories for an entity.
        
        Args:
            entity_id: The ID of the entity
            include_decayed: Whether to include memories below the relevance threshold
            
        Returns:
            List of Memory objects
        """
        # Check if we need to apply decay
        self._apply_decay_if_needed(entity_id)
        
        # Check cache
        if self._is_entity_cached(entity_id):
            memory_dicts = self._get_all_memories_from_cache(entity_id)
        else:
            # Fetch from Firebase
            memories_ref = db.reference(f"/entity_memory/{entity_id}/memories")
            memory_dicts = memories_ref.get() or {}
            
            # Update cache
            self._cache_entity_memories(entity_id, memory_dicts)
        
        # Convert to Memory objects
        memories = []
        for memory_id, memory_dict in memory_dicts.items():
            # Skip decayed memories if not requested
            if not include_decayed and not memory_dict.get("is_core") and \
               memory_dict.get("relevance_score", 0) < self.relevance_threshold:
                continue
            
            # Convert string dates to datetime
            memory_dict["created_at"] = datetime.fromisoformat(memory_dict["created_at"])
            memory_dict["updated_at"] = datetime.fromisoformat(memory_dict["updated_at"])
            if memory_dict.get("accessed_at"):
                memory_dict["accessed_at"] = datetime.fromisoformat(memory_dict["accessed_at"])
            
            memory_dict["id"] = memory_id
            memories.append(Memory(**memory_dict))
        
        # Sort by relevance (descending)
        memories.sort(key=lambda m: m.relevance_score, reverse=True)
        
        return memories
    
    def get_core_memories(self, entity_id: str) -> List[Memory]:
        """
        Get all core memories for an entity.
        
        Args:
            entity_id: The ID of the entity
            
        Returns:
            List of core Memory objects
        """
        all_memories = self.get_all_memories(entity_id)
        return [m for m in all_memories if m.is_core]
    
    def update_memory(self, memory: Memory) -> Memory:
        """
        Update an existing memory.
        
        Args:
            memory: The Memory object to update
            
        Returns:
            The updated Memory object
        """
        # Save old memory for event
        old_memory = self.get_memory(memory.id, memory.entity_id)
        if not old_memory:
            raise ValueError(f"Memory {memory.id} not found for entity {memory.entity_id}")
        
        # Update timestamp
        memory.updated_at = datetime.utcnow()
        
        # Store in Firebase
        self._store_memory(memory)
        
        # Clear cache for this entity
        self._clear_entity_cache(memory.entity_id)
        
        # Emit event
        self.event_dispatcher.publish(MemoryEvent(
            event_type="memory.updated",
            entity_id=memory.entity_id,
            memory_id=memory.id,
            operation="updated",
            memory_data=memory.dict()
        ))
        
        return memory
    
    def reinforce_memory(self, memory_id: str, entity_id: str, 
                         reinforcement: float = 0.1) -> Memory:
        """
        Reinforce a memory by increasing its relevance score.
        
        Args:
            memory_id: The ID of the memory
            entity_id: The ID of the entity
            reinforcement: The amount to increase the relevance score
            
        Returns:
            The updated Memory object
        """
        memory = self.get_memory(memory_id, entity_id)
        if not memory:
            raise ValueError(f"Memory {memory_id} not found for entity {entity_id}")
        
        # Increase relevance score (max 1.0)
        memory.relevance_score = min(1.0, memory.relevance_score + reinforcement)
        memory.accessed_at = datetime.utcnow()
        memory.updated_at = datetime.utcnow()
        
        # Store in Firebase
        self._store_memory(memory)
        
        # Clear cache for this entity
        self._clear_entity_cache(entity_id)
        
        # Emit event
        self.event_dispatcher.publish(MemoryEvent(
            event_type="memory.reinforced",
            entity_id=entity_id,
            memory_id=memory_id,
            operation="reinforced",
            memory_data=memory.dict()
        ))
        
        return memory
    
    def delete_memory(self, memory_id: str, entity_id: str) -> bool:
        """
        Delete a memory.
        
        Args:
            memory_id: The ID of the memory
            entity_id: The ID of the entity
            
        Returns:
            True if deleted, False otherwise
        """
        # Get memory for event
        memory = self.get_memory(memory_id, entity_id)
        if not memory:
            return False
        
        # Delete from Firebase
        memory_ref = db.reference(f"/entity_memory/{entity_id}/memories/{memory_id}")
        memory_ref.delete()
        
        # Clear cache for this entity
        self._clear_entity_cache(entity_id)
        
        # Emit event
        self.event_dispatcher.publish(MemoryEvent(
            event_type="memory.deleted",
            entity_id=entity_id,
            memory_id=memory_id,
            operation="deleted",
            memory_data=memory.dict()
        ))
        
        return True
    
    def generate_memory_summary(self, entity_id: str, max_recent: int = 5) -> MemorySummary:
        """
        Generate a summary of an entity's memories for narrative context.
        
        Args:
            entity_id: The ID of the entity
            max_recent: Maximum number of recent memories to include
            
        Returns:
            A MemorySummary object
        """
        # Get core and recent memories
        core_memories = self.get_core_memories(entity_id)
        recent_memories = self.get_recent_memories(entity_id, max_recent)
        
        # Extract content
        core_content = [m.content for m in core_memories]
        recent_content = [m.content for m in recent_memories]
        
        # TODO: Use GPT to generate a proper memory summary
        # For now, just concatenate
        summary = "Core memories: " + "; ".join(core_content) if core_content else "No core memories."
        summary += " Recent experiences: " + "; ".join(recent_content) if recent_content else " No recent memories."
        
        return MemorySummary(
            entity_id=entity_id,
            summary=summary,
            core_memories=core_content,
            recent_memories=recent_content
        )
    
    def get_recent_memories(self, entity_id: str, limit: int = 5) -> List[Memory]:
        """
        Get the most recent memories for an entity.
        
        Args:
            entity_id: The ID of the entity
            limit: Maximum number of memories to return
            
        Returns:
            List of Memory objects, sorted by creation date (descending)
        """
        all_memories = self.get_all_memories(entity_id)
        
        # Sort by creation date (descending)
        sorted_memories = sorted(all_memories, key=lambda m: m.created_at, reverse=True)
        
        return sorted_memories[:limit]
    
    def get_memories_by_category(self, entity_id: str, category: str) -> List[Memory]:
        """
        Get all memories for an entity in a specific category.
        
        Args:
            entity_id: The ID of the entity
            category: The category to filter by
            
        Returns:
            List of Memory objects in the specified category
        """
        all_memories = self.get_all_memories(entity_id)
        return [m for m in all_memories if m.category == category]
    
    def get_memories_by_tag(self, entity_id: str, tag: str) -> List[Memory]:
        """
        Get all memories for an entity with a specific tag.
        
        Args:
            entity_id: The ID of the entity
            tag: The tag to filter by
            
        Returns:
            List of Memory objects with the specified tag
        """
        all_memories = self.get_all_memories(entity_id)
        return [m for m in all_memories if tag in m.tags]
    
    def convert_to_core_memory(self, memory_id: str, entity_id: str) -> Memory:
        """
        Convert a regular memory to a core memory.
        
        Args:
            memory_id: The ID of the memory
            entity_id: The ID of the entity
            
        Returns:
            The updated Memory object
        """
        memory = self.get_memory(memory_id, entity_id)
        if not memory:
            raise ValueError(f"Memory {memory_id} not found for entity {entity_id}")
        
        memory.is_core = True
        memory.relevance_score = 1.0  # Core memories always have maximum relevance
        memory.updated_at = datetime.utcnow()
        
        # Store in Firebase
        self._store_memory(memory)
        
        # Clear cache for this entity
        self._clear_entity_cache(entity_id)
        
        # Emit event
        self.event_dispatcher.publish(MemoryEvent(
            event_type="memory.core_converted",
            entity_id=entity_id,
            memory_id=memory_id,
            operation="core_converted",
            memory_data=memory.dict()
        ))
        
        return memory
    
    # ===== Internal Methods =====
    
    def _store_memory(self, memory: Memory):
        """
        Store a memory in Firebase.
        
        Args:
            memory: The Memory object to store
        """
        memory_dict = memory.dict()
        
        # Convert datetime objects to ISO format for Firebase
        memory_dict["created_at"] = memory_dict["created_at"].isoformat()
        memory_dict["updated_at"] = memory_dict["updated_at"].isoformat()
        if memory_dict.get("accessed_at"):
            memory_dict["accessed_at"] = memory_dict["accessed_at"].isoformat()
        
        # Remove id field (it's the key)
        memory_id = memory_dict.pop("id")
        
        # Store in Firebase
        memory_ref = db.reference(f"/entity_memory/{memory.entity_id}/memories/{memory_id}")
        memory_ref.set(memory_dict)
    
    def _apply_decay(self, entity_id: str):
        """
        Apply decay to all non-core memories for an entity.
        
        Args:
            entity_id: The ID of the entity
        """
        # Get last decay time
        last_decay_ref = db.reference(f"/entity_memory/{entity_id}/last_decay")
        last_decay = last_decay_ref.get()
        
        # Calculate days since last decay
        now = datetime.utcnow()
        if last_decay:
            last_decay_time = datetime.fromisoformat(last_decay)
            days_since_decay = (now - last_decay_time).days
        else:
            days_since_decay = 0
        
        # If no decay needed, update timestamp and return
        if days_since_decay < 1:
            return
        
        # Get all memories
        memories_ref = db.reference(f"/entity_memory/{entity_id}/memories")
        memories = memories_ref.get() or {}
        
        # Apply decay to each memory
        for memory_id, memory_data in memories.items():
            # Skip core memories
            if memory_data.get("is_core", False):
                continue
            
            # Calculate new relevance score
            current_score = memory_data.get("relevance_score", 1.0)
            decay_factor = math.pow(1 - self.decay_rate, days_since_decay)
            new_score = current_score * decay_factor
            
            # Update in Firebase
            memory_ref = memories_ref.child(memory_id)
            memory_ref.update({"relevance_score": new_score})
        
        # Update last decay time
        last_decay_ref.set(now.isoformat())
        
        # Clear cache for this entity
        self._clear_entity_cache(entity_id)
    
    def _apply_decay_if_needed(self, entity_id: str):
        """
        Check if decay should be applied and do so if needed.
        
        Args:
            entity_id: The ID of the entity
        """
        # Get last decay time
        last_decay_ref = db.reference(f"/entity_memory/{entity_id}/last_decay")
        last_decay = last_decay_ref.get()
        
        # If never decayed or more than a day since last decay, apply decay
        if not last_decay:
            self._apply_decay(entity_id)
            return
        
        last_decay_time = datetime.fromisoformat(last_decay)
        days_since_decay = (datetime.utcnow() - last_decay_time).days
        
        if days_since_decay >= 1:
            self._apply_decay(entity_id)
    
    def _is_entity_cached(self, entity_id: str) -> bool:
        """
        Check if an entity's memories are cached and not expired.
        
        Args:
            entity_id: The ID of the entity
            
        Returns:
            True if cached and not expired, False otherwise
        """
        if entity_id not in self.cache_timestamps:
            return False
        
        cache_time = self.cache_timestamps[entity_id]
        now = datetime.utcnow()
        
        return now - cache_time < self.cache_ttl
    
    def _cache_entity_memories(self, entity_id: str, memories: Dict[str, Any]):
        """
        Cache an entity's memories.
        
        Args:
            entity_id: The ID of the entity
            memories: Dict of memory_id -> memory_data
        """
        self.memory_cache[entity_id] = memories
        self.cache_timestamps[entity_id] = datetime.utcnow()
    
    def _clear_entity_cache(self, entity_id: str):
        """
        Clear the cache for an entity.
        
        Args:
            entity_id: The ID of the entity
        """
        if entity_id in self.memory_cache:
            del self.memory_cache[entity_id]
        
        if entity_id in self.cache_timestamps:
            del self.cache_timestamps[entity_id]
    
    def _get_memory_from_cache(self, entity_id: str, memory_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a memory from the cache.
        
        Args:
            entity_id: The ID of the entity
            memory_id: The ID of the memory
            
        Returns:
            Memory data dict or None if not found
        """
        if not self._is_entity_cached(entity_id):
            return None
        
        entity_memories = self.memory_cache.get(entity_id, {})
        return entity_memories.get(memory_id)
    
    def _get_all_memories_from_cache(self, entity_id: str) -> Dict[str, Any]:
        """
        Get all memories for an entity from the cache.
        
        Args:
            entity_id: The ID of the entity
            
        Returns:
            Dict of memory_id -> memory_data
        """
        if not self._is_entity_cached(entity_id):
            return {}
        
        return self.memory_cache.get(entity_id, {})

# Initialize the memory manager
memory_manager = MemoryManager.get_instance() 