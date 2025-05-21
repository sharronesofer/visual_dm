"""
MemoryManager
--------------
Implements the core Memory System as described in the Development Bible.
Provides entity-level memory with relevance scoring and decay mechanics.
Uses a repository pattern for managing both "core memories" (permanent) and 
regular memories (decaying over time).
"""

import os
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
import json
import logging

# Event dispatcher for emitting memory events
from backend.systems.events.event_dispatcher import EventDispatcher
from backend.systems.events.canonical_events import MemoryCreated, MemoryReinforced, MemoryDeleted

# Constants for memory system
DEFAULT_MEMORY_DECAY_RATE = 0.1  # Per day
DEFAULT_MEMORY_RELEVANCE_THRESHOLD = 0.3  # Minimum relevance to retain
MAX_REGULAR_MEMORIES = 100  # Maximum number of regular memories per entity
MAX_CORE_MEMORIES = 20  # Maximum number of core memories per entity

class Memory:
    """
    Represents a single memory instance with metadata, relevance, and decay.
    """
    def __init__(
        self,
        content: str,
        entity_id: Union[str, uuid.UUID],
        relevance: float = 1.0,
        is_core: bool = False,
        metadata: Optional[Dict[str, Any]] = None,
        categories: Optional[List[str]] = None,
        decay_rate: Optional[float] = None,
        memory_id: Optional[Union[str, uuid.UUID]] = None
    ):
        """
        Initialize a new memory.
        
        Args:
            content: The memory content text
            entity_id: ID of the entity this memory belongs to
            relevance: Initial relevance score (0.0-1.0)
            is_core: Whether this is a core memory (doesn't decay)
            metadata: Additional metadata about the memory
            categories: Categories for easier querying/analytics
            decay_rate: Custom decay rate (per day), if None uses default
            memory_id: Optional memory ID, generates one if not provided
        """
        self.id = str(memory_id) if memory_id else str(uuid.uuid4())
        self.content = content
        self.entity_id = str(entity_id)
        self.relevance = max(0.0, min(1.0, relevance))  # Clamp between 0 and 1
        self.is_core = is_core
        self.created_at = datetime.utcnow()
        self.last_accessed = self.created_at
        self.metadata = metadata or {}
        self.categories = categories or []
        self.decay_rate = decay_rate or DEFAULT_MEMORY_DECAY_RATE
    
    def access(self) -> None:
        """Mark the memory as accessed, updating its last access timestamp."""
        self.last_accessed = datetime.utcnow()
    
    def decay(self, days: float) -> float:
        """
        Apply decay to the memory's relevance based on time passed.
        Core memories don't decay.
        
        Args:
            days: Number of days since last decay
            
        Returns:
            New relevance value
        """
        if self.is_core:
            return self.relevance
            
        decay_amount = self.decay_rate * days
        self.relevance = max(0.0, self.relevance - decay_amount)
        return self.relevance
    
    def reinforce(self, amount: float = 0.2) -> float:
        """
        Reinforce the memory, increasing its relevance.
        
        Args:
            amount: Amount to increase relevance by
            
        Returns:
            New relevance value
        """
        self.relevance = min(1.0, self.relevance + amount)
        self.access()  # Update last accessed time
        return self.relevance
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert memory to dictionary for serialization."""
        return {
            "id": self.id,
            "content": self.content,
            "entity_id": self.entity_id,
            "relevance": self.relevance,
            "is_core": self.is_core,
            "created_at": self.created_at.isoformat(),
            "last_accessed": self.last_accessed.isoformat(),
            "metadata": self.metadata,
            "categories": self.categories,
            "decay_rate": self.decay_rate
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Memory':
        """Create memory instance from dictionary."""
        memory = cls(
            content=data["content"],
            entity_id=data["entity_id"],
            relevance=data["relevance"],
            is_core=data["is_core"],
            metadata=data["metadata"],
            categories=data["categories"],
            decay_rate=data["decay_rate"],
            memory_id=data["id"]
        )
        memory.created_at = datetime.fromisoformat(data["created_at"])
        memory.last_accessed = datetime.fromisoformat(data["last_accessed"])
        return memory


class MemoryManager:
    """
    Manager for entity-level memories with repository pattern, decay mechanics, 
    and event emission.
    """
    def __init__(self, entity_id: Union[str, uuid.UUID], storage_dir: Optional[str] = None):
        """
        Initialize memory manager for an entity.
        
        Args:
            entity_id: The entity ID to manage memories for
            storage_dir: Directory to store serialized memories
        """
        self.entity_id = str(entity_id)
        self.storage_dir = storage_dir or os.path.join("data", "memories")
        self.memories: Dict[str, Memory] = {}
        self.event_dispatcher = EventDispatcher.get_instance()
        
        # Create storage directory if it doesn't exist
        os.makedirs(self.storage_dir, exist_ok=True)
        
        # Load existing memories
        self._load_memories()
    
    def _load_memories(self) -> None:
        """Load memories from storage."""
        file_path = os.path.join(self.storage_dir, f"{self.entity_id}_memories.json")
        if not os.path.exists(file_path):
            return
            
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
                
            for memory_data in data:
                memory = Memory.from_dict(memory_data)
                self.memories[memory.id] = memory
        except Exception as e:
            logging.error(f"Error loading memories for entity {self.entity_id}: {e}")
    
    def _save_memories(self) -> None:
        """Save memories to storage."""
        file_path = os.path.join(self.storage_dir, f"{self.entity_id}_memories.json")
        
        try:
            memory_data = [memory.to_dict() for memory in self.memories.values()]
            with open(file_path, "w") as f:
                json.dump(memory_data, f, indent=2)
        except Exception as e:
            logging.error(f"Error saving memories for entity {self.entity_id}: {e}")
    
    def add_memory(self, content: str, relevance: float = 1.0, 
                   is_core: bool = False, metadata: Optional[Dict[str, Any]] = None,
                   categories: Optional[List[str]] = None, commit: bool = True) -> Memory:
        """
        Add a new memory for the entity.
        
        Args:
            content: Memory content text
            relevance: Initial relevance score (0.0-1.0)
            is_core: Whether this is a core memory
            metadata: Additional memory metadata
            categories: Categories for analytics and querying
            commit: Whether to save to storage immediately
            
        Returns:
            The created Memory instance
        """
        # Create memory
        memory = Memory(
            content=content,
            entity_id=self.entity_id,
            relevance=relevance,
            is_core=is_core,
            metadata=metadata,
            categories=categories
        )
        
        # Enforce memory limits
        self._enforce_memory_limits(is_core)
        
        # Add to collection
        self.memories[memory.id] = memory
        
        # Emit creation event
        self.event_dispatcher.publish_sync(MemoryCreated(
            entity_id=self.entity_id,
            memory_id=memory.id,
            is_core=is_core,
            content=content,
            categories=categories or []
        ))
        
        # Save if requested
        if commit:
            self._save_memories()
            
        return memory
    
    def _enforce_memory_limits(self, is_core: bool) -> None:
        """
        Enforce memory limits by removing lowest-relevance memories.
        
        Args:
            is_core: Whether enforcing core memory limits
        """
        if is_core:
            # Count core memories
            core_memories = [m for m in self.memories.values() if m.is_core]
            if len(core_memories) >= MAX_CORE_MEMORIES:
                # We don't remove core memories, but log a warning
                logging.warning(f"Entity {self.entity_id} has reached maximum core memories ({MAX_CORE_MEMORIES})")
        else:
            # Count regular memories
            regular_memories = [m for m in self.memories.values() if not m.is_core]
            if len(regular_memories) >= MAX_REGULAR_MEMORIES:
                # Remove lowest relevance memory
                regular_memories.sort(key=lambda m: m.relevance)
                to_remove = regular_memories[0]
                self.remove_memory(to_remove.id)
    
    def get_memory(self, memory_id: Union[str, uuid.UUID]) -> Optional[Memory]:
        """
        Retrieve a memory by ID.
        
        Args:
            memory_id: Memory ID to retrieve
            
        Returns:
            Memory instance or None if not found
        """
        memory_id_str = str(memory_id)
        memory = self.memories.get(memory_id_str)
        if memory:
            memory.access()  # Update last accessed time
        return memory
    
    def reinforce_memory(self, memory_id: Union[str, uuid.UUID], 
                         amount: float = 0.2, commit: bool = True) -> Optional[Memory]:
        """
        Reinforce a memory, increasing its relevance.
        
        Args:
            memory_id: Memory ID to reinforce
            amount: Amount to increase relevance by
            commit: Whether to save to storage immediately
            
        Returns:
            Updated Memory instance or None if not found
        """
        memory_id_str = str(memory_id)
        memory = self.memories.get(memory_id_str)
        if not memory:
            return None
            
        memory.reinforce(amount)
        
        # Emit reinforcement event
        self.event_dispatcher.publish_sync(MemoryReinforced(
            entity_id=self.entity_id,
            memory_id=memory_id_str,
            reinforcement_amount=amount,
            new_relevance=memory.relevance
        ))
        
        if commit:
            self._save_memories()
            
        return memory
    
    def remove_memory(self, memory_id: Union[str, uuid.UUID], commit: bool = True) -> bool:
        """
        Remove a memory.
        
        Args:
            memory_id: Memory ID to remove
            commit: Whether to save to storage immediately
            
        Returns:
            True if removed, False if not found
        """
        memory_id_str = str(memory_id)
        memory = self.memories.get(memory_id_str)
        if not memory:
            return False
            
        # Remove from collection
        del self.memories[memory_id_str]
        
        # Emit deletion event
        self.event_dispatcher.publish_sync(MemoryDeleted(
            entity_id=self.entity_id,
            memory_id=memory_id_str,
            was_core=memory.is_core
        ))
        
        if commit:
            self._save_memories()
            
        return True
    
    def decay_all_memories(self, days: Optional[float] = None, 
                          commit: bool = True) -> List[str]:
        """
        Apply decay to all memories based on time passed.
        
        Args:
            days: Days since last decay (if None, calculates from last accessed)
            commit: Whether to save to storage immediately
            
        Returns:
            List of IDs of memories that fell below threshold and were removed
        """
        now = datetime.utcnow()
        removed_ids = []
        
        for memory_id, memory in list(self.memories.items()):
            if memory.is_core:
                continue  # Core memories don't decay
                
            # Calculate days since last access if not provided
            memory_days = days
            if memory_days is None:
                memory_days = (now - memory.last_accessed).total_seconds() / 86400  # Convert to days
                
            # Apply decay
            new_relevance = memory.decay(memory_days)
            
            # Check if below threshold
            if new_relevance < DEFAULT_MEMORY_RELEVANCE_THRESHOLD:
                self.remove_memory(memory_id, commit=False)
                removed_ids.append(memory_id)
        
        if commit and (removed_ids or days is not None):
            self._save_memories()
            
        return removed_ids
    
    def query_memories(self, 
                      categories: Optional[List[str]] = None,
                      min_relevance: float = 0.0,
                      core_only: bool = False,
                      limit: Optional[int] = None,
                      order_by_relevance: bool = True) -> List[Memory]:
        """
        Query memories based on criteria.
        
        Args:
            categories: Filter by categories (OR logic)
            min_relevance: Minimum relevance to include
            core_only: Only include core memories
            limit: Maximum number of results
            order_by_relevance: Order by relevance (high to low)
            
        Returns:
            List of matching Memory instances
        """
        results = []
        
        for memory in self.memories.values():
            # Apply filters
            if core_only and not memory.is_core:
                continue
                
            if memory.relevance < min_relevance:
                continue
                
            if categories and not any(cat in memory.categories for cat in categories):
                continue
                
            # Add to results
            results.append(memory)
            
        # Sort by relevance
        if order_by_relevance:
            results.sort(key=lambda m: m.relevance, reverse=True)
            
        # Apply limit
        if limit is not None:
            results = results[:limit]
            
        # Update last accessed
        for memory in results:
            memory.access()
            
        # Save access timestamps if we returned results
        if results:
            self._save_memories()
            
        return results
    
    def generate_memory_summary(self, categories: Optional[List[str]] = None,
                              min_relevance: float = 0.5,
                              max_memories: int = 10) -> str:
        """
        Generate a summary of memories for GPT context.
        
        Args:
            categories: Filter by categories
            min_relevance: Minimum relevance to include
            max_memories: Maximum number of memories to include
            
        Returns:
            Formatted summary string
        """
        # Query memories with filters
        memories = self.query_memories(
            categories=categories,
            min_relevance=min_relevance,
            limit=max_memories,
            order_by_relevance=True
        )
        
        if not memories:
            return "No significant memories."
            
        # Format core memories first
        core_summaries = []
        regular_summaries = []
        
        for memory in memories:
            summary = f"- {memory.content}"
            if memory.metadata:
                if "date" in memory.metadata:
                    summary += f" ({memory.metadata['date']})"
            
            if memory.is_core:
                core_summaries.append(summary)
            else:
                regular_summaries.append(summary)
        
        # Combine summaries
        result = ""
        if core_summaries:
            result += "Core Memories:\n" + "\n".join(core_summaries) + "\n\n"
        if regular_summaries:
            result += "Recent Memories:\n" + "\n".join(regular_summaries)
            
        return result 