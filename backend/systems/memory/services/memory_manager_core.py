"""
Memory Manager Core Implementation

This module provides the core MemoryManager class that handles memory storage,
retrieval, decay, and summarization for NPCs and other entities.
"""

from typing import Dict, List, Optional, Any, Set, Tuple, TYPE_CHECKING
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import asyncio
import logging
from enum import Enum
import uuid
import json

# Import event types
from backend.infrastructure.events.core.event_dispatcher import EventDispatcher

# Mock database and session imports
from backend.infrastructure.shared.database import get_async_session, mock_db

# Use TYPE_CHECKING to avoid circular imports
if TYPE_CHECKING:
    from backend.systems.memory.services.memory import Memory

from backend.systems.memory.memory_categories import MemoryCategory, get_category_info

logger = logging.getLogger(__name__)


@dataclass
class SummarizationConfig:
    """Configuration for memory summarization."""
    
    max_memories_per_summary: int = 10
    summary_threshold_days: int = 7
    importance_threshold: float = 0.3
    enable_auto_summarization: bool = True


# Default summarization configuration
DEFAULT_SUMMARIZATION_CONFIG = SummarizationConfig()


class VectorDBCollection:
    """Mock vector database collection for storing and retrieving memories."""
    
    def __init__(self, collection_name: str):
        self.collection_name = collection_name
        self.memories = {}
    
    async def add_memory(self, memory: "Memory") -> bool:
        """Add a memory to the collection."""
        self.memories[memory.memory_id] = memory
        return True
    
    async def get_memory(self, memory_id: str) -> Optional["Memory"]:
        """Retrieve a memory by ID."""
        return self.memories.get(memory_id)
    
    async def search_similar(self, query: str, limit: int = 10) -> List["Memory"]:
        """Search for memories similar to the query."""
        # Simple search implementation - in production would use vector embeddings
        results = []
        for memory in self.memories.values():
            if query.lower() in memory.content.lower():
                results.append(memory)
            if len(results) >= limit:
                break
        return results
    
    async def update_memory(self, memory_id: str, memory: "Memory") -> bool:
        """Update a memory in the collection."""
        if memory_id in self.memories:
            self.memories[memory_id] = memory
            return True
        return False
    
    async def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory from the collection."""
        if memory_id in self.memories:
            del self.memories[memory_id]
            return True
        return False
    
    async def get_all_memories(self) -> List["Memory"]:
        """Get all memories in the collection."""
        return list(self.memories.values())


class MockChromaCollection(VectorDBCollection):
    """Mock implementation of ChromaDB collection for testing."""
    
    def __init__(self, collection_name: str):
        super().__init__(collection_name)
        self.embeddings: Dict[str, List[float]] = {}
    
    async def add_with_embedding(self, memory: "Memory", embedding: List[float]) -> bool:
        """Add memory with embedding."""
        await self.add_memory(memory)
        self.embeddings[memory.id] = embedding
        return True
    
    async def search_by_embedding(self, embedding: List[float], limit: int = 10) -> List["Memory"]:
        """Search by embedding similarity."""
        # Simple mock implementation
        return await self.search_similar("", limit)


class MemoryManager:
    """
    Manages memories for an entity (NPC, faction, etc.).
    
    Handles memory storage, retrieval, decay, summarization, and categorization.
    """
    
    def __init__(self, entity_id: str, entity_type: str = "npc", 
                 config: Optional[SummarizationConfig] = None):
        self.entity_id = entity_id
        self.entity_type = entity_type
        self.config = config or DEFAULT_SUMMARIZATION_CONFIG
        self.memories: Dict[str, "Memory"] = {}
        self.vector_collection: Optional[VectorDBCollection] = None
        self.last_cleanup = datetime.now()
        
        # Initialize vector collection
        self._initialize_vector_collection()
    
    def _initialize_vector_collection(self):
        """Initialize the vector database collection."""
        collection_name = f"{self.entity_type}_{self.entity_id}_memories"
        self.vector_collection = MockChromaCollection(collection_name)
    
    async def create_memory(self, content: str, category: Optional[MemoryCategory] = None,
                          importance: Optional[float] = None, metadata: Optional[Dict] = None) -> "Memory":
        """Create a new memory."""
        # Local import to avoid circular dependency
        from backend.systems.memory.services.memory import Memory
        
        if category is None:
            from backend.systems.memory.memory_categories import categorize_memory_content
            category = categorize_memory_content(content)
        
        if importance is None:
            category_info = get_category_info(category)
            importance = category_info.default_importance
        
        memory = Memory(
            npc_id=self.entity_id,
            content=content,
            categories=[category.value] if isinstance(category, MemoryCategory) else [category],
            importance=importance,
            metadata=metadata or {}
        )
        
        await self.add_memory(memory)
        return memory
    
    async def add_memory(self, memory: "Memory") -> bool:
        """Add a memory to the manager."""
        self.memories[memory.memory_id] = memory
        
        # Add to vector collection if available
        if self.vector_collection:
            await self.vector_collection.add_memory(memory)
        
        # Store in mock database
        await mock_db.set(f"memory:{memory.memory_id}", memory.to_dict())
        
        logger.info(f"Added memory {memory.memory_id} for entity {self.entity_id}")
        return True
    
    async def get_memory(self, memory_id: str) -> Optional["Memory"]:
        """Get a memory by ID."""
        return self.memories.get(memory_id)
    
    async def recall_memory(self, query: str, limit: int = 10, 
                          category_filter: Optional[MemoryCategory] = None) -> List["Memory"]:
        """Recall memories based on a query."""
        results = []
        
        if self.vector_collection:
            # Use vector search
            vector_results = await self.vector_collection.search_similar(query, limit * 2)
            results.extend(vector_results)
        
        # Filter by category if specified
        if category_filter:
            results = [m for m in results if m.category == category_filter.value]
        
        # Sort by relevance and importance
        results.sort(key=lambda m: m.importance, reverse=True)
        
        return results[:limit]
    
    async def update_memory_importance(self, memory_id: str, new_importance: float) -> bool:
        """Update the importance of a memory."""
        if memory_id in self.memories:
            self.memories[memory_id].importance = new_importance
            await mock_db.set(f"memory:{memory_id}", self.memories[memory_id].to_dict())
            return True
        return False
    
    async def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory."""
        if memory_id in self.memories:
            del self.memories[memory_id]
            
            if self.vector_collection:
                await self.vector_collection.delete_memory(memory_id)
            
            await mock_db.delete(f"memory:{memory_id}")
            return True
        return False
    
    async def get_memories_by_category(self, category: MemoryCategory) -> List["Memory"]:
        """Get all memories of a specific category."""
        return [m for m in self.memories.values() if category.value in m.categories]
    
    async def get_memories_by_tag(self, tag: str) -> List["Memory"]:
        """Get memories containing a specific tag."""
        return [m for m in self.memories.values() if tag in m.metadata.get('tags', [])]
    
    async def get_memories_involving_entity(self, entity_id: str) -> List["Memory"]:
        """Get memories involving another entity."""
        return [m for m in self.memories.values() 
                if entity_id in m.metadata.get('entities', [])]
    
    async def get_recent_memories(self, days: int = 7) -> List["Memory"]:
        """Get memories from the last N days."""
        cutoff = datetime.now() - timedelta(days=days)
        recent_memories = []
        
        for memory in self.memories.values():
            # Parse the created_at string to datetime for comparison
            try:
                memory_date = datetime.fromisoformat(memory.created_at.replace('Z', '+00:00'))
                if memory_date >= cutoff:
                    recent_memories.append(memory)
            except (ValueError, AttributeError):
                # If parsing fails, include the memory to be safe
                recent_memories.append(memory)
        
        return recent_memories
    
    async def clean_expired_memories(self) -> int:
        """Remove memories that have decayed completely."""
        expired_ids = []
        
        for memory_id, memory in self.memories.items():
            if memory.relevance <= 0.01:  # Very low relevance threshold
                expired_ids.append(memory_id)
        
        for memory_id in expired_ids:
            await self.delete_memory(memory_id)
        
        logger.info(f"Cleaned {len(expired_ids)} expired memories for entity {self.entity_id}")
        return len(expired_ids)
    
    async def update_all_memories(self, current_time: Optional[datetime] = None) -> None:
        """Update all memories (apply decay, etc.)."""
        if current_time is None:
            current_time = datetime.now()
        
        for memory in self.memories.values():
            memory.update_relevance(current_time)
        
        # Periodic cleanup
        if (current_time - self.last_cleanup).days >= 1:
            await self.clean_expired_memories()
            self.last_cleanup = current_time
    
    async def summarize_old_memories(self) -> Optional["Memory"]:
        """Summarize old, low-importance memories."""
        if not self.config.enable_auto_summarization:
            return None
        
        # Get old memories for summarization
        cutoff = datetime.now() - timedelta(days=self.config.summary_threshold_days)
        old_memories = [
            m for m in self.memories.values()
            if (m.created_at < cutoff and 
                m.importance < self.config.importance_threshold and
                m.category != MemoryCategory.SUMMARY.value)
        ]
        
        if len(old_memories) < self.config.max_memories_per_summary:
            return None
        
        # Create summary
        content_parts = [m.content for m in old_memories[:self.config.max_memories_per_summary]]
        summary_content = f"Summary of {len(content_parts)} memories: " + "; ".join(content_parts)
        
        summary_memory = await self.create_memory(
            content=summary_content,
            category=MemoryCategory.SUMMARY,
            importance=0.8,
            metadata={
                'summarized_memory_ids': [m.id for m in old_memories[:self.config.max_memories_per_summary]],
                'summary_type': 'auto_generated'
            }
        )
        
        # Remove summarized memories
        for memory in old_memories[:self.config.max_memories_per_summary]:
            await self.delete_memory(memory.id)
        
        logger.info(f"Created summary memory {summary_memory.id} for entity {self.entity_id}")
        return summary_memory
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get statistics about the memory collection."""
        total_memories = len(self.memories)
        categories = {}
        avg_importance = 0
        
        for memory in self.memories.values():
            category = memory.category
            categories[category] = categories.get(category, 0) + 1
            avg_importance += memory.importance
        
        if total_memories > 0:
            avg_importance /= total_memories
        
        return {
            'total_memories': total_memories,
            'categories': categories,
            'average_importance': avg_importance,
            'entity_id': self.entity_id,
            'entity_type': self.entity_type
        }
