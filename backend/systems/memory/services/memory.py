"""
This class defines the core Memory model for the memory system.
It represents a single memory instance with decay mechanics and metadata.
"""

import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional, TypeVar, Type, Set, Union

# Import category system from infrastructure
from backend.infrastructure.memory_utils.memory_categorization import MemoryCategory, categorize_memory_content, apply_category_modifiers
from backend.infrastructure.memory_utils.saliency_scoring import calculate_initial_importance, calculate_memory_saliency

# Import Event-related classes for integration with event system
from backend.infrastructure.events.core.event_base import EventBase

# Define specific memory events
class MemoryCreatedEvent(EventBase):
    memory_id: str
    npc_id: str
    content: str
    memory_type: str # 'core' or 'regular'
    categories: List[str]  # Added categories
    importance: float  # Added importance
    event_type: str = "memory.created"

class MemoryDecayedEvent(EventBase):
    memory_id: str
    npc_id: str
    old_saliency: float
    new_saliency: float
    event_type: str = "memory.decayed"

class MemoryCategorizedEvent(EventBase):
    memory_id: str
    npc_id: str
    categories: List[str]
    event_type: str = "memory.categorized"

class MemoryAccessedEvent(EventBase):
    memory_id: str
    npc_id: str
    context: str  # What context triggered this memory access
    event_type: str = "memory.accessed"

class MemoryReinforcedEvent(EventBase):
    memory_id: str
    npc_id: str
    old_importance: float
    new_importance: float
    context: str  # What context triggered this reinforcement
    event_type: str = "memory.reinforced"

class MemoryGraphLink:
    """Represents a directed link between two memories."""
    def __init__(self, target_memory_id: str, relationship_type: str, strength: float = 1.0):
        self.target_memory_id = target_memory_id
        self.relationship_type = relationship_type # e.g., "follows", "caused_by", "related_to"
        self.strength = strength # 0.0 to 1.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "target_memory_id": self.target_memory_id,
            "relationship_type": self.relationship_type,
            "strength": self.strength
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryGraphLink':
        return cls(
            target_memory_id=data['target_memory_id'],
            relationship_type=data['relationship_type'],
            strength=data.get('strength', 1.0)
        )

class Memory:
    """
    Represents a single memory instance with decay mechanics and metadata.
    """
    def __init__(
        self,
        npc_id: str,
        content: str,
        memory_id: Optional[str] = None,
        memory_type: str = "regular",
        summary: Optional[str] = None,
        created_at: Optional[str] = None,
        categories: Optional[List[str]] = None,
        importance: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
        event_dispatcher = None
    ):
        """
        Initialize a Memory object.
        
        Args:
            npc_id: ID of the NPC this memory belongs to
            content: The actual memory content text
            memory_id: Optional unique ID (generated if not provided)
            memory_type: Type of memory (core or regular)
            summary: Optional short summary of the memory
            created_at: Optional timestamp (current time if not provided)
            categories: Optional list of memory categories
            importance: Optional importance score (calculated if not provided)
            metadata: Optional additional metadata
            event_dispatcher: Optional event dispatcher for emitting events
        """
        self.npc_id = npc_id
        self.content = content
        self.memory_id = memory_id or str(uuid.uuid4())
        self.memory_type = memory_type
        self.summary = summary or ""
        self.created_at = created_at or datetime.now().isoformat()
        self.event_dispatcher = event_dispatcher
        
        # Process categories
        self.categories = categories or []
        if not self.categories:
            # Auto-categorize if no categories provided
            auto_category = categorize_memory_content(content)
            self.categories = [auto_category.value] if hasattr(auto_category, 'value') else [str(auto_category)]
        
        # Calculate importance if not provided
        self.importance = importance
        if self.importance is None:
            self.importance = calculate_initial_importance(
                memory_content=content,
                memory_type=memory_type,
                categories=self.categories
            )
            
        # Initialize access tracking
        self.access_count = 0
        self.last_accessed = None
        
        # Initialize additional metadata
        self.metadata = metadata or {}
        
        # Emit creation event if dispatcher is available
        if self.event_dispatcher:
            self._emit_created_event()
    
    @property
    def id(self) -> str:
        """Backward compatibility property for accessing memory_id as id."""
        return self.memory_id
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the memory to a dictionary representation."""
        return {
            "id": self.memory_id,
            "npc_id": self.npc_id,
            "content": self.content,
            "summary": self.summary,
            "memory_type": self.memory_type,
            "categories": self.categories,
            "importance": self.importance,
            "created_at": self.created_at,
            "access_count": self.access_count,
            "last_accessed": self.last_accessed,
            "saliency": self.get_current_saliency(),
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], event_dispatcher=None) -> 'Memory':
        """Create a Memory object from a dictionary representation."""
        return cls(
            npc_id=data.get("npc_id", ""),
            content=data.get("content", ""),
            memory_id=data.get("id"),
            memory_type=data.get("memory_type", "regular"),
            summary=data.get("summary", ""),
            created_at=data.get("created_at"),
            categories=data.get("categories", []),
            importance=data.get("importance"),
            metadata=data.get("metadata", {}),
            event_dispatcher=event_dispatcher
        )
    
    def get_current_saliency(self) -> float:
        """Calculate the current saliency score for this memory."""
        # Create memory dictionary for saliency calculation without calling to_dict()
        memory_dict = {
            "id": self.memory_id,
            "npc_id": self.npc_id,
            "content": self.content,
            "summary": self.summary,
            "memory_type": self.memory_type,
            "categories": self.categories,
            "importance": self.importance,
            "created_at": self.created_at,
            "access_count": self.access_count,
            "last_accessed": self.last_accessed,
            "metadata": self.metadata
        }
        return calculate_memory_saliency(memory_dict)
    
    def access(self, context: str = "") -> None:
        """
        Record an access to this memory, updating access stats.
        
        Args:
            context: Optional context describing why the memory was accessed
        """
        self.access_count += 1
        self.last_accessed = datetime.now().isoformat()
        
        # Update metadata
        if "access_history" not in self.metadata:
            self.metadata["access_history"] = []
        
        self.metadata["access_history"].append({
            "timestamp": self.last_accessed,
            "context": context
        })
        
        # Emit access event if dispatcher is available
        if self.event_dispatcher:
            self._emit_accessed_event(context)
    
    def update_categories(self, new_categories: List[str]) -> None:
        """
        Update the memory categories.
        
        Args:
            new_categories: New list of categories
        """
        old_categories = self.categories.copy()
        self.categories = new_categories
        
        # Update importance based on category changes
        # For now, just use a simple modifier approach
        # In a full implementation, this would apply category-specific modifiers
        
        # Emit categorization event if dispatcher is available
        if self.event_dispatcher:
            self._emit_categorized_event()
    
    def _emit_created_event(self) -> None:
        """Emit a memory creation event."""
        event = MemoryCreatedEvent(
            memory_id=self.memory_id,
            npc_id=self.npc_id,
            content=self.content,
            memory_type=self.memory_type,
            categories=self.categories,
            importance=self.importance
        )
        self.event_dispatcher.dispatch(event)
    
    def _emit_accessed_event(self, context: str) -> None:
        """Emit a memory access event."""
        event = MemoryAccessedEvent(
            memory_id=self.memory_id,
            npc_id=self.npc_id,
            context=context
        )
        self.event_dispatcher.dispatch(event)
    
    def _emit_categorized_event(self) -> None:
        """Emit a memory categorization event."""
        event = MemoryCategorizedEvent(
            memory_id=self.memory_id,
            npc_id=self.npc_id,
            categories=self.categories
        )
        self.event_dispatcher.dispatch(event)

    def decay(self, delta_seconds: float) -> None:
        """
        Apply decay to the memory's importance over time.
        :param delta_seconds: Time in seconds to decay.
        """
        if self.memory_type == 'core':
            return
        self.importance = max(0, self.importance - self.decay_rate * delta_seconds)
    
    def is_expired(self, threshold: float) -> bool:
        """
        Determine if the memory is expired based on a threshold.
        :param threshold: Importance threshold for expiration.
        :return: True if expired, False otherwise.
        """
        return self.memory_type == 'regular' and self.importance < threshold

    def add_link(self, target_memory_id: str, relationship_type: str, strength: float = 1.0) -> None:
        """
        Add a graph link to another memory.
        :param target_memory_id: ID of the target memory.
        :param relationship_type: Type of relationship (e.g., "follows", "caused_by").
        :param strength: Strength of the relationship (0.0 to 1.0).
        """
        self.links.append(MemoryGraphLink(target_memory_id, relationship_type, strength))

    def has_category(self, category: Union[str, MemoryCategory]) -> bool:
        """
        Check if the memory has a specific category.
        :param category: Category to check (string or MemoryCategory enum).
        :return: True if the memory has the category, False otherwise.
        """
        if isinstance(category, str):
            try:
                return MemoryCategory(category.lower()) in self._categories
            except ValueError:
                return False
        elif isinstance(category, MemoryCategory):
            return category in self._categories
        return False

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the memory to a dictionary for serialization.
        :return: Dictionary representation of the memory.
        """
        return {
            "id": self.memory_id,
            "npc_id": self.npc_id,
            "content": self.content,
            "summary": self.summary,
            "memory_type": self.memory_type,
            "categories": self.categories,
            "importance": self.importance,
            "created_at": self.created_at,
            "access_count": self.access_count,
            "last_accessed": self.last_accessed,
            "saliency": self.get_current_saliency(),
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Memory':
        """
        Create a Memory instance from a dictionary.
        :param data: Dictionary representation of the memory.
        :return: Memory instance.
        """
        from dateutil.parser import parse as parse_iso
        
        memory = cls(
            npc_id=data['npc_id'],
            content=data['content'],
            memory_id=data['id'],
            memory_type=data['memory_type'],
            summary=data.get('summary'),
            created_at=data.get('created_at'),
            categories=data.get('categories', []),
            importance=data.get('importance'),
            metadata=data.get('metadata', {}),
            event_dispatcher=None  # Assuming no event dispatcher is provided in the dictionary
        )
        return memory 