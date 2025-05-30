"""
Memory System for Visual DM

The Memory System simulates entity-level memory with relevance scoring and decay mechanics.
It manages both core memories (permanent) and regular memories (which decay over time).

This module provides the following key components:
- Memory: Represents a single memory instance with decay mechanics
- MemoryManager: Manages a collection of memories for an NPC
- Memory events for the event system
"""

from .memory import (
    Memory,
    MemoryGraphLink,
    MemoryCreatedEvent,
    MemoryDecayedEvent,
    MemoryReinforcedEvent
)

from .memory_manager import (
    MemoryManager,
    VectorDBCollection,
    MockChromaCollection,
    DEFAULT_SUMMARIZATION_CONFIG
)

# Export utility functions
from .memory_utils import (
    store_interaction,
    update_long_term_memory,
    summarize_and_clean_memory,
    get_recent_interactions,
    generate_beliefs_from_meta_summary,
    log_permanent_memory,
    update_faction_memory,
    update_region_memory,
    update_world_memory,
    add_touchstone_memory,
    process_gpt_memory_entry,
    update_poi_memory
)

__all__ = [
    'Memory',
    'MemoryManager',
    'MemoryGraphLink',
    'MemoryCreatedEvent',
    'MemoryDecayedEvent',
    'MemoryReinforcedEvent',
    'VectorDBCollection',
    'MockChromaCollection',
    'DEFAULT_SUMMARIZATION_CONFIG',
    # Utility functions
    'store_interaction',
    'update_long_term_memory',
    'summarize_and_clean_memory',
    'get_recent_interactions',
    'generate_beliefs_from_meta_summary',
    'log_permanent_memory',
    'update_faction_memory',
    'update_region_memory',
    'update_world_memory',
    'add_touchstone_memory',
    'process_gpt_memory_entry',
    'update_poi_memory'
]
