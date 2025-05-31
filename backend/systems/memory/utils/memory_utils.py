"""
Memory utility functions for the memory system.

This module provides utility functions for common memory operations
that are used throughout the system.
"""

from typing import Dict, List, Optional, Any, TYPE_CHECKING
from datetime import datetime, timedelta
import asyncio
import logging

# Use TYPE_CHECKING to avoid circular imports
if TYPE_CHECKING:
    from backend.systems.memory.services.memory import Memory
    from backend.systems.memory.memory_categories import MemoryCategory

from backend.systems.memory.services.memory_manager_core import MemoryManager

logger = logging.getLogger(__name__)


async def store_interaction(entity_id: str, interaction_data: Dict[str, Any]) -> "Memory":
    """Store an interaction as a memory."""
    # Local imports to avoid circular dependency
    from backend.systems.memory.services.memory import Memory
    from backend.systems.memory.memory_categories import MemoryCategory
    
    manager = MemoryManager(entity_id, "npc")
    
    content = f"Interaction with {interaction_data.get('target', 'unknown')}: {interaction_data.get('content', '')}"
    
    memory = await manager.create_memory(
        content=content,
        category=MemoryCategory.INTERACTION,
        importance=interaction_data.get('importance', 0.7),
        metadata={
            'interaction_type': interaction_data.get('type', 'general'),
            'participants': interaction_data.get('participants', []),
            'location': interaction_data.get('location'),
            'timestamp': datetime.now().isoformat()
        }
    )
    
    return memory


async def update_long_term_memory(entity_id: str, memory_data: Dict[str, Any]) -> "Memory":
    """Update or create a long-term memory."""
    # Local imports to avoid circular dependency
    from backend.systems.memory.services.memory import Memory
    from backend.systems.memory.memory_categories import MemoryCategory
    
    manager = MemoryManager(entity_id, "npc")
    
    # Check if this is an update to existing memory
    existing_memories = await manager.recall_memory(memory_data.get('content', ''), limit=1)
    
    if existing_memories:
        # Update existing memory importance
        existing_memory = existing_memories[0]
        new_importance = min(1.0, existing_memory.importance + 0.1)
        await manager.update_memory_importance(existing_memory.id, new_importance)
        return existing_memory
    else:
        # Create new long-term memory
        return await manager.create_memory(
            content=memory_data.get('content', ''),
            category=MemoryCategory.KNOWLEDGE,
            importance=memory_data.get('importance', 0.8),
            metadata=memory_data.get('metadata', {})
        )


async def summarize_and_clean_memory(entity_id: str) -> Optional["Memory"]:
    """Summarize and clean old memories for an entity."""
    # Local import to avoid circular dependency
    from backend.systems.memory.services.memory import Memory
    
    manager = MemoryManager(entity_id, "npc")
    
    # Update all memories first
    await manager.update_all_memories()
    
    # Perform summarization
    summary_memory = await manager.summarize_old_memories()
    
    return summary_memory


async def get_recent_interactions(entity_id: str, days: int = 7) -> List["Memory"]:
    """Get recent interaction memories for an entity."""
    # Local imports to avoid circular dependency
    from backend.systems.memory.services.memory import Memory
    from backend.systems.memory.memory_categories import MemoryCategory
    
    manager = MemoryManager(entity_id, "npc")
    
    recent_memories = await manager.get_recent_memories(days)
    
    # Filter for interactions only
    interactions = [m for m in recent_memories if m.category == MemoryCategory.INTERACTION.value]
    
    return interactions


async def generate_beliefs_from_meta_summary(entity_id: str, summary_data: Dict[str, Any]) -> List["Memory"]:
    """Generate belief memories from meta summary data."""
    # Local imports to avoid circular dependency
    from backend.systems.memory.services.memory import Memory
    from backend.systems.memory.memory_categories import MemoryCategory
    
    manager = MemoryManager(entity_id, "npc")
    
    beliefs = []
    
    # Extract beliefs from summary
    belief_indicators = summary_data.get('beliefs', [])
    
    for belief_text in belief_indicators:
        belief_memory = await manager.create_memory(
            content=f"I believe that {belief_text}",
            category=MemoryCategory.BELIEF,
            importance=0.9,
            metadata={
                'derived_from': 'meta_summary',
                'confidence': summary_data.get('confidence', 0.8)
            }
        )
        beliefs.append(belief_memory)
    
    return beliefs


async def log_permanent_memory(entity_id: str, content: str, category: "MemoryCategory" = None) -> "Memory":
    """Log a permanent memory that won't decay."""
    # Local imports to avoid circular dependency
    from backend.systems.memory.services.memory import Memory
    from backend.systems.memory.memory_categories import MemoryCategory
    
    if category is None:
        category = MemoryCategory.CORE
        
    manager = MemoryManager(entity_id, "npc")
    
    memory = await manager.create_memory(
        content=content,
        category=category,
        importance=1.0,
        metadata={'permanent': True}
    )
    
    return memory


async def update_faction_memory(entity_id: str, faction_id: str, update_data: Dict[str, Any]) -> "Memory":
    """Update memory about a faction."""
    # Local import to avoid circular dependency
    from backend.systems.memory.services.memory import Memory
    
    manager = MemoryManager(entity_id, "npc")
    
    content = f"Faction {faction_id}: {update_data.get('description', '')}"
    
    memory = await manager.create_memory(
        content=content,
        category=MemoryCategory.FACTION,
        importance=update_data.get('importance', 0.7),
        metadata={
            'faction_id': faction_id,
            'relationship': update_data.get('relationship', 'neutral'),
            'last_interaction': datetime.now().isoformat()
        }
    )
    
    return memory


async def update_region_memory(entity_id: str, region_id: str, update_data: Dict[str, Any]) -> "Memory":
    """Update memory about a region."""
    # Local import to avoid circular dependency
    from backend.systems.memory.services.memory import Memory
    
    manager = MemoryManager(entity_id, "npc")
    
    content = f"Region {region_id}: {update_data.get('description', '')}"
    
    memory = await manager.create_memory(
        content=content,
        category=MemoryCategory.LOCATION,
        importance=update_data.get('importance', 0.6),
        metadata={
            'region_id': region_id,
            'visited': update_data.get('visited', False),
            'safety_level': update_data.get('safety_level', 'unknown')
        }
    )
    
    return memory


async def update_world_memory(entity_id: str, world_event: Dict[str, Any]) -> "Memory":
    """Update memory about world events."""
    # Local import to avoid circular dependency
    from backend.systems.memory.services.memory import Memory
    
    manager = MemoryManager(entity_id, "npc")
    
    content = f"World event: {world_event.get('description', '')}"
    
    memory = await manager.create_memory(
        content=content,
        category=MemoryCategory.WORLD_STATE,
        importance=world_event.get('importance', 0.6),
        metadata={
            'event_type': world_event.get('type', 'general'),
            'impact_level': world_event.get('impact', 'minor'),
            'affected_regions': world_event.get('regions', [])
        }
    )
    
    return memory


async def add_touchstone_memory(entity_id: str, content: str, significance: str = "high") -> "Memory":
    """Add a touchstone memory (highly significant)."""
    # Local import to avoid circular dependency
    from backend.systems.memory.services.memory import Memory
    
    manager = MemoryManager(entity_id, "npc")
    
    importance = 1.0 if significance == "high" else 0.9
    
    memory = await manager.create_memory(
        content=content,
        category=MemoryCategory.TOUCHSTONE,
        importance=importance,
        metadata={
            'significance': significance,
            'touchstone': True,
            'created_date': datetime.now().isoformat()
        }
    )
    
    return memory


async def process_gpt_memory_entry(entity_id: str, gpt_response: str, context: Dict[str, Any]) -> "Memory":
    """Process a memory entry generated by GPT."""
    # Local import to avoid circular dependency
    from backend.systems.memory.services.memory import Memory
    
    manager = MemoryManager(entity_id, "npc")
    
    # Determine category and importance from context
    category = MemoryCategory.KNOWLEDGE
    importance = 0.7
    
    if 'emotion' in context:
        importance += 0.1
    
    if 'conflict' in context:
        importance += 0.2
        category = MemoryCategory.EVENT
    
    memory = await manager.create_memory(
        content=gpt_response,
        category=category,
        importance=min(1.0, importance),
        metadata={
            'source': 'gpt_generated',
            'context': context,
            'processing_timestamp': datetime.now().isoformat()
        }
    )
    
    return memory


async def update_poi_memory(entity_id: str, poi_id: str, poi_data: Dict[str, Any]) -> "Memory":
    """Update memory about a point of interest."""
    # Local import to avoid circular dependency
    from backend.systems.memory.services.memory import Memory
    
    manager = MemoryManager(entity_id, "npc")
    
    content = f"Point of Interest {poi_id}: {poi_data.get('name', '')} - {poi_data.get('description', '')}"
    
    memory = await manager.create_memory(
        content=content,
        category=MemoryCategory.LOCATION,
        importance=poi_data.get('importance', 0.6),
        metadata={
            'poi_id': poi_id,
            'poi_type': poi_data.get('type', 'unknown'),
            'coordinates': poi_data.get('coordinates'),
            'discovered': poi_data.get('discovered', False)
        }
    )
    
    return memory
