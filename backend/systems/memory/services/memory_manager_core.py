"""
Memory Manager Core
------------------
Core logic for memory management including forgetting, importance calculation,
LLM integration, and association tracking. Uses JSON configuration for decay.
"""

from typing import Dict, List, Optional, Any, Set, Tuple, TYPE_CHECKING
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import asyncio
import logging
from enum import Enum
import uuid
import json
import os

# Import event system
from backend.infrastructure.events.services.event_dispatcher import EventDispatcher

# Mock database and session imports
from backend.infrastructure.shared.database import get_async_session, mock_db

# Use TYPE_CHECKING to avoid circular imports
if TYPE_CHECKING:
    from backend.systems.memory.services.memory import Memory
    from backend.infrastructure.memory_utils.memory_categorization import MemoryCategory, get_category_info

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
    
    Handles memory storage, retrieval, decay, summarization, and categorization
    using JSON configuration for decay parameters.
    """
    
    def __init__(self, entity_id: str, entity_type: str = "npc", 
                 config: Optional[SummarizationConfig] = None):
        self.entity_id = entity_id
        self.entity_type = entity_type
        self.config = config or DEFAULT_SUMMARIZATION_CONFIG
        self.memories: Dict[str, "Memory"] = {}
        self.vector_collection: Optional[VectorDBCollection] = None
        self.last_cleanup = datetime.now()
        
        # Load decay configuration from JSON
        self.decay_config = self._load_decay_config()
        
        # Initialize vector collection
        self._initialize_vector_collection()
    
    def _load_decay_config(self) -> Dict[str, Any]:
        """Load memory decay configuration from JSON file"""
        try:
            config_path = os.path.join(os.path.dirname(__file__), '../../../data/systems/memory/behavioral_responses.json')
            with open(config_path, 'r') as f:
                data = json.load(f)
                return data.get('memory_decay_factors', {})
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.warning(f"Could not load decay configuration: {e}. Using defaults.")
            return {
                'base_decay_rate': 0.95,
                'importance_preservation_threshold': 0.7,
                'category_decay_modifiers': {
                    'trauma': 0.99,
                    'core_belief': 0.98,
                    'achievement': 0.96,
                    'relationship': 0.97,
                    'mundane': 0.92,
                    'social': 0.94,
                    'combat': 0.93,
                    'economic': 0.93
                },
                'access_frequency_bonus': {
                    'never_accessed': 1.0,
                    'rarely_accessed': 0.98,
                    'occasionally_accessed': 0.95,
                    'frequently_accessed': 0.90,
                    'constantly_accessed': 0.85
                },
                'time_threshold_days': {
                    'recent': 7,
                    'medium_term': 30,
                    'long_term': 365
                },
                'decay_acceleration_factors': {
                    'medium_term_multiplier': 1.2,
                    'long_term_multiplier': 1.5
                },
                'relevance_thresholds': {
                    'deletion_threshold': 0.01,
                    'summarization_threshold': 0.1,
                    'archival_threshold': 0.05
                }
            }
    
    def _initialize_vector_collection(self):
        """Initialize the vector database collection."""
        collection_name = f"{self.entity_type}_{self.entity_id}_memories"
        self.vector_collection = MockChromaCollection(collection_name)
    
    async def create_memory(self, content: str, category: Optional["MemoryCategory"] = None,
                          importance: Optional[float] = None, metadata: Optional[Dict] = None) -> "Memory":
        """Create a new memory."""
        # Local import to avoid circular dependency
        from backend.systems.memory.services.memory import Memory
        
        if category is None:
            from backend.infrastructure.memory_utils.memory_categorization import categorize_memory_content
            category = categorize_memory_content(content)
        
        if importance is None:
            from backend.infrastructure.memory_utils.memory_categorization import get_category_info
            category_info = get_category_info(category)
            importance = category_info.default_importance
        
        # Import MemoryCategory for isinstance check
        from backend.infrastructure.memory_utils.memory_categorization import MemoryCategory
        
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
                          category_filter: Optional["MemoryCategory"] = None) -> List["Memory"]:
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
    
    async def get_memories_by_category(self, category: "MemoryCategory") -> List["Memory"]:
        """Get all memories of a specific category."""
        # Lazy import to avoid circular dependency
        from backend.infrastructure.memory_utils.memory_categorization import MemoryCategory
        
        return [memory for memory in self.memories.values() 
                if category.value in memory.categories]
    
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
        """Remove memories that have decayed completely using JSON configuration."""
        expired_ids = []
        
        # Use JSON configuration for deletion threshold
        deletion_threshold = self.decay_config.get('relevance_thresholds', {}).get('deletion_threshold', 0.01)
        
        for memory_id, memory in self.memories.items():
            if hasattr(memory, 'relevance') and memory.relevance <= deletion_threshold:
                expired_ids.append(memory_id)
        
        for memory_id in expired_ids:
            await self.delete_memory(memory_id)
        
        logger.info(f"Cleaned {len(expired_ids)} expired memories for entity {self.entity_id} using threshold {deletion_threshold}")
        return len(expired_ids)
    
    async def update_all_memories(self, current_time: Optional[datetime] = None) -> None:
        """Update all memories (apply decay, etc.) using JSON configuration."""
        if current_time is None:
            current_time = datetime.now()
        
        for memory in self.memories.values():
            self._apply_memory_decay(memory, current_time)
        
        # Periodic cleanup
        if (current_time - self.last_cleanup).days >= 1:
            await self.clean_expired_memories()
            self.last_cleanup = current_time
    
    def _apply_memory_decay(self, memory: "Memory", current_time: datetime) -> None:
        """Apply memory decay using JSON configuration parameters."""
        if not hasattr(memory, 'relevance'):
            memory.relevance = memory.importance  # Initialize relevance if not set
        
        # Get decay configuration
        base_decay = self.decay_config.get('base_decay_rate', 0.95)
        category_modifiers = self.decay_config.get('category_decay_modifiers', {})
        access_bonuses = self.decay_config.get('access_frequency_bonus', {})
        time_thresholds = self.decay_config.get('time_threshold_days', {})
        acceleration_factors = self.decay_config.get('decay_acceleration_factors', {})
        
        # Calculate memory age
        memory_date = datetime.fromisoformat(memory.created_at) if isinstance(memory.created_at, str) else memory.created_at
        age_days = (current_time - memory_date).days
        
        # Get category-specific decay modifier
        category_modifier = 1.0
        for category in memory.categories:
            if category in category_modifiers:
                category_modifier = max(category_modifier, category_modifiers[category])
        
        # Get access frequency bonus
        access_count = getattr(memory, 'access_count', 0)
        access_modifier = access_bonuses.get('never_accessed', 1.0)
        if access_count > 50:
            access_modifier = access_bonuses.get('constantly_accessed', 0.85)
        elif access_count > 20:
            access_modifier = access_bonuses.get('frequently_accessed', 0.90)
        elif access_count > 5:
            access_modifier = access_bonuses.get('occasionally_accessed', 0.95)
        elif access_count > 0:
            access_modifier = access_bonuses.get('rarely_accessed', 0.98)
        
        # Apply time-based acceleration
        time_modifier = 1.0
        if age_days > time_thresholds.get('long_term', 365):
            time_modifier = acceleration_factors.get('long_term_multiplier', 1.5)
        elif age_days > time_thresholds.get('medium_term', 30):
            time_modifier = acceleration_factors.get('medium_term_multiplier', 1.2)
        
        # Calculate final decay rate
        decay_rate = base_decay * category_modifier * access_modifier / time_modifier
        
        # Apply importance preservation
        importance_threshold = self.decay_config.get('importance_preservation_threshold', 0.7)
        if memory.importance >= importance_threshold:
            decay_rate = max(decay_rate, 0.98)  # Preserve important memories
        
        # Apply decay
        memory.relevance *= decay_rate
        
        # Update access timestamp
        memory.last_accessed = current_time
    
    async def summarize_old_memories(self) -> Optional["Memory"]:
        """Summarize old, low-importance memories using JSON configuration."""
        if not self.config.enable_auto_summarization:
            return None
        
        # Lazy import to avoid circular dependency
        from backend.infrastructure.memory_utils.memory_categorization import MemoryCategory
        
        # Get summarization threshold from config
        summarization_threshold = self.decay_config.get('relevance_thresholds', {}).get('summarization_threshold', 0.1)
        
        # Get old memories for summarization
        cutoff = datetime.now() - timedelta(days=self.config.summary_threshold_days)
        old_memories = [
            m for m in self.memories.values()
            if (m.created_at < cutoff and 
                m.importance < self.config.importance_threshold and
                hasattr(m, 'relevance') and m.relevance < summarization_threshold and
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
        
        logger.info(f"Created summary memory {summary_memory.id} for entity {self.entity_id} using threshold {summarization_threshold}")
        return summary_memory
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get statistics about the memory collection."""
        total_memories = len(self.memories)
        categories = {}
        avg_importance = 0
        avg_relevance = 0
        relevance_count = 0
        
        for memory in self.memories.values():
            category = memory.category
            categories[category] = categories.get(category, 0) + 1
            avg_importance += memory.importance
            if hasattr(memory, 'relevance'):
                avg_relevance += memory.relevance
                relevance_count += 1
        
        if total_memories > 0:
            avg_importance /= total_memories
        
        if relevance_count > 0:
            avg_relevance /= relevance_count
        
        return {
            'total_memories': total_memories,
            'categories': categories,
            'average_importance': avg_importance,
            'average_relevance': avg_relevance,
            'entity_id': self.entity_id,
            'entity_type': self.entity_type,
            'decay_config_loaded': bool(self.decay_config)
        }
