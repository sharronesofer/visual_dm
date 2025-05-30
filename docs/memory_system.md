# Memory System Documentation

## Overview

The memory system provides a way for entities in the game to store, retrieve, and manage memories with relevance scoring, categorization, and contextual relationships. The optimized memory system adds batch operations, automatic decay, pruning, and indexing for improved performance and memory management.

## Core Components

### Memory Model

The `Memory` class represents a single memory entity and includes the following key properties:

- `id`: Unique identifier for the memory
- `entity_id`: Entity that owns this memory
- `summary`: Short text summary of the memory
- `categories`: List of categories the memory belongs to
- `details`: Additional structured details about the memory
- `relevance`: Floating-point score (0.0-1.0) indicating the memory's importance
- `is_core`: Boolean flag for core (permanent) memories that don't decay
- `context_ids`: Set of related memory IDs providing context
- `created_at`: Timestamp when the memory was created

### Memory Manager

The `MemoryManager` class handles basic memory operations:

- Creating memories for entities
- Retrieving memories by ID or entity
- Updating memory relevance
- Decaying individual memories
- Marking memories as core (permanent)
- Adding contextual relationships between memories
- Generating textual summaries of entity memories

### Memory Optimizer

The `MemoryOptimizer` class extends the memory system with performance optimizations:

- **Batch Decay**: Apply decay to multiple memories at once
- **Pruning**: Remove low-relevance memories based on age and relevance threshold
- **Memory Indexing**: Build and maintain indexes for faster memory retrieval
- **Batch Operations**: Perform bulk operations with reduced I/O overhead
- **Storage Statistics**: Track and report memory system usage metrics
- **Related Memory Retrieval**: Find memories connected through context relationships

### Memory Service

The `MemoryService` provides a simplified interface to both the `MemoryManager` and `MemoryOptimizer` functionality, making it easier to use memory operations from other parts of the application.

### Memory Scheduler

The `MemoryScheduler` provides automatic scheduled maintenance for the memory system:

- **Hourly Decay**: Small, frequent relevance decay to all non-core memories
- **Daily Optimization**: Complete memory system optimization run
- **Weekly Pruning**: More aggressive cleanup of old, low-relevance memories

## Usage Examples

### Creating a Memory

```python
memory_service = MemoryService()

memory = await memory_service.create_memory(
    entity_id="npc_123",
    summary="Witnessed the fall of Kingdom X",
    categories=[MemoryCategory.WAR, MemoryCategory.CATASTROPHE],
    details={"location": "Capital City", "witnesses": ["npc_456", "npc_789"]},
    relevance=0.8,
    is_core=True
)
```

### Retrieving Entity Memories

```python
# Get all memories for an entity
memories = await memory_service.get_entity_memories(
    entity_id="npc_123",
    limit=50,
    min_relevance=0.3
)

# Get only core memories
core_memories = await memory_service.get_entity_memories(
    entity_id="npc_123",
    include_core_only=True
)

# Get memories of a specific category
war_memories = await memory_service.get_entity_memories(
    entity_id="npc_123",
    categories=[MemoryCategory.WAR]
)
```

### Memory Decay and Update

```python
# Manually decay a memory
await memory_service.decay_memory_relevance(
    memory_id="mem_123",
    decay_amount=0.1
)

# Update memory relevance
await memory_service.update_memory_relevance(
    memory_id="mem_123",
    new_relevance=0.9
)
```

### Batch Operations and Optimization

```python
# Batch decay all memories
await memory_service.batch_decay_memories(
    decay_amount=0.05,
    min_relevance_threshold=0.1
)

# Prune low-relevance memories
await memory_service.prune_low_relevance_memories(
    relevance_threshold=0.2,
    age_days=30
)

# Full optimization
results = await memory_service.optimize_memory_system()
```

## API Endpoints

The memory system exposes the following API endpoints:

### Memory Operations

- `POST /api/v1/memory/create`: Create a new memory
- `GET /api/v1/memory/{memory_id}`: Get a specific memory
- `GET /api/v1/memory/entity/{entity_id}`: Get memories for an entity
- `PUT /api/v1/memory/{memory_id}/relevance`: Update memory relevance
- `PUT /api/v1/memory/{memory_id}/core`: Mark memory as core/non-core
- `PUT /api/v1/memory/{memory_id}/decay`: Decay memory relevance
- `PUT /api/v1/memory/{memory_id}/context/{context_memory_id}`: Add context relationship
- `DELETE /api/v1/memory/{memory_id}`: Delete a memory
- `GET /api/v1/memory/{memory_id}/related`: Get related memories
- `GET /api/v1/memory/entity/{entity_id}/summary`: Generate text summary of memories

### Optimization Operations

- `POST /api/v1/memory/optimize/batch-decay`: Perform batch decay
- `POST /api/v1/memory/optimize/prune`: Prune low-relevance memories
- `POST /api/v1/memory/optimize/full`: Perform full memory system optimization
- `GET /api/v1/memory/stats`: Get memory system statistics
- `POST /api/v1/memory/index/build`: Build memory index

### Scheduler Operations

- `GET /api/v1/scheduler/status`: Get scheduler status
- `POST /api/v1/scheduler/optimize`: Run immediate optimization

## Optimization Details

### Memory Decay

Memory decay reduces the relevance of memories over time, simulating the natural forgetting process. Core memories (marked with `is_core=True`) are exempt from decay.

- **Individual Decay**: Applied when the memory is accessed or manually called
- **Batch Decay**: Applied to multiple memories at once on a schedule
- **Decay Formula**: `new_relevance = max(min_threshold, old_relevance - decay_amount)`

### Memory Pruning

Pruning removes low-relevance memories that have aged beyond a certain threshold, preventing unlimited memory accumulation.

- **Relevance Threshold**: Memories below this relevance score are candidates for pruning
- **Age Threshold**: Only memories older than this number of days will be pruned
- **Entity Filtering**: Can be limited to a specific entity's memories
- **Core Protection**: Core memories are never pruned, regardless of relevance or age

### Memory Indexing

The memory indexing system accelerates memory retrieval by maintaining cached indexes:

- **Entity Index**: Maps entity IDs to their memory IDs
- **Category Index**: Maps memory categories to memory IDs
- **Lazy Loading**: Memories are loaded on demand and cached for future access
- **Index Rebuilding**: Index is automatically rebuilt after pruning operations

### Scheduled Optimization

The scheduler performs the following tasks automatically:

- **Hourly Decay** (interval: 1 hour):
  - Small decay amount (0.02) to all non-core memories
  - Prevents memories from staying at maximum relevance indefinitely

- **Daily Optimization** (interval: 24 hours):
  - Full memory system optimization
  - Index rebuilding
  - Statistics collection

- **Weekly Pruning** (interval: 7 days):
  - More aggressive pruning of old, low-relevance memories
  - Threshold: 0.15 relevance, 14 days age
  - Complete index rebuild

## Performance Considerations

For optimal performance:

1. Use batch operations whenever possible instead of individual operations
2. Use the `memory_service.optimize_memory_system()` method periodically
3. Consider the tradeoff between memory retention and system performance
4. Use core memory flag for important memories that should never decay or be pruned
5. Implement custom decay rates based on memory importance and game mechanics 