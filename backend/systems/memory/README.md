# Memory System

## Overview
The Memory System simulates entity-level memory with relevance scoring and decay mechanics. It manages both core memories (permanent) and regular memories (which decay over time).

## Components

### Memory
The `Memory` class represents a single memory entity with the following features:
- Core vs. regular memory types
- Automatic decay mechanics
- Metadata tracking (creation time, last access, etc.)
- Importance scoring
- Tagging system
- Memory graph linking

### MemoryManager
The `MemoryManager` class manages collections of memories for NPCs, integrating:
- Vector database for semantic search and storage
- Summarization capabilities via LLM
- Memory reinforcement and decay mechanics
- Conversation tracking and cleanup logic
- Event system integration
- Singleton instance pattern with async initialization

### Memory Utilities
The `memory_utils.py` file provides utility functions for:
- Storing interactions
- Updating long-term summaries
- Cleaning and summarizing memories
- Managing faction, region, and world memories
- Processing GPT-generated memories

### API Routes
The `memory_routes.py` file provides Flask routes for:
- Viewing memory entries
- Clearing memory
- Storing interactions
- Updating long-term memory
- Evaluating beliefs from memory

## Usage

```python
from backend.systems.memory import Memory, MemoryManager

# Create a memory manager for an NPC
manager = await MemoryManager.get_instance(
    npc_id="npc123",
    short_term_db=short_term_collection, 
    long_term_db=long_term_collection,
    event_dispatcher=event_dispatcher
)

# Add memories
memory = Memory(
    content="Met the player in the tavern",
    importance=0.7,
    associated_entities=["player123"],
    decay_rate=0.1,
    tags=["player", "meeting", "tavern"],
    type_="regular",
    npc_id="npc123"
)
manager.add_memory(memory)

# Store interactions
manager.store_interaction("The player asked about the quest", {"region": "tavern"})

# Retrieve relevant memories
memories = manager.query_memories("player tavern", 5)

# Generate a summary
summary = manager.update_long_term_summary()
```

## Integration
The Memory System integrates with the Event System through:
- `MemoryCreatedEvent`
- `MemoryDecayedEvent`
- `MemoryReinforcedEvent`

These events allow other systems to react to memory changes and maintain loose coupling.

## Features

- Entity-local memory management (memories are never directly shared)
- Core memories that don't decay over time
- Regular memories with decay mechanics
- Memory categorization for analytics
- JSON-based persistence organized by entity
- GPT summarization for narrative generation
- Async API for better performance
- Singleton pattern for centralized management

## Key Components

- Memory objects with metadata, categories, and relevance scores
- Memory decay mechanisms to simulate forgetting
- Contextual relationships between memories (memory graphs)
- Event emission for memory operations
- Vector DB integration for semantic search

## Integration Points

- Provides memory context for dialogue and narrative generation
- Integrates with the Events System for capturing significant events
- Supports NPCs' ability to recall and respond to past interactions
- Firebase integration for persistent storage

Refer to the Development Bible for detailed design documentation.
