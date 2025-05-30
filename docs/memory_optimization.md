# Memory System Optimization

This document provides a comprehensive overview of the memory system optimization features, including architecture, performance considerations, and usage guidelines.

## Architecture Overview

The memory optimization system consists of several components working together:

1. **MemoryOptimizer**: Core optimization engine providing memory decay, pruning, and batch operations
2. **MemoryIndex**: Advanced indexing system for fast memory retrieval and queries
3. **MemoryUtils**: Utility functions for efficient memory operations
4. **MemoryWebSocketService**: Real-time notifications for memory operations
5. **optimize_memories.py**: Command-line script for scheduled optimization tasks

### Component Relationships

```
┌─────────────────┐     ┌───────────────────┐     ┌────────────────┐
│  Memory Service │────>│  Memory Optimizer │────>│ Memory Manager │
└────────┬────────┘     └─────────┬─────────┘     └────────────────┘
         │                        │                        ▲
         │                        │                        │
         ▼                        ▼                        │
┌─────────────────┐     ┌───────────────────┐             │
│   Memory Index  │     │   Memory Utils    │─────────────┘
└─────────────────┘     └───────────────────┘
```

## Memory Optimization Features

### 1. Memory Decay

Memory decay is a core feature that gradually reduces the relevance of memories over time to simulate natural forgetting. 

#### How it works:

- **Batch decay**: Process multiple memories in parallel for better performance
- **Selective decay**: Apply decay only to memories above a specified minimum threshold
- **Entity-specific decay**: Optionally target specific entities for decay
- **Core memory protection**: Core memories (relevance = 1.0) are protected from decay

#### Usage:

```python
# Decay memories with default parameters
await memory_service.batch_decay_memories()

# Target specific entity with custom decay
await memory_service.batch_decay_memories(
    entity_id="entity123",
    decay_amount=0.03,
    min_relevance_threshold=0.2
)
```

### 2. Memory Pruning

Memory pruning removes low-relevance memories that are older than a specified age to prevent storage bloat.

#### How it works:

- **Parallel processing**: Uses multiple threads for efficient pruning of large memory sets
- **Age-based filter**: Only prunes memories older than specified age (default: 30 days)
- **Relevance threshold**: Only prunes memories below specified relevance (default: 0.1)
- **Entity targeting**: Optionally targets specific entities

#### Usage:

```python
# Prune with default parameters
await memory_service.prune_low_relevance_memories()

# Customize pruning operation
await memory_service.prune_low_relevance_memories(
    relevance_threshold=0.15,
    age_days=45,
    entity_id="entity456"
)
```

### 3. Memory Reinforcement

Memory reinforcement increases the relevance of important memories to prevent them from being forgotten.

#### How it works:

- **Batch reinforcement**: Process multiple memories at once
- **Flexible input**: Accept memory IDs or complete memory objects
- **Configurable boost**: Adjust the amount of relevance increase

#### Usage:

```python
# Reinforce memories by ID
await memory_service.batch_reinforce_memories(
    memories=[{"id": "mem123"}, {"id": "mem456"}],
    entity_id="entity789",
    boost_amount=0.2
)

# Reinforce with complete memory objects
await memory_service.batch_reinforce_memories(
    memories=[memory1, memory2, memory3],
    boost_amount=0.15
)
```

### 4. Memory Indexing

The memory indexing system provides fast memory retrieval and search capabilities with intelligent caching.

#### Key features:

- **Multi-dimensional indexing**: Index by entity, category, keyword, relevance, recency, creation time
- **Keyword extraction**: Extract and index keywords from memory content
- **Memory caching**: Cache frequently accessed memories to reduce disk I/O
- **Persistent indexes**: Save indexes to disk for faster startup
- **Parallel processing**: Build indexes with multiple threads for performance

#### Usage:

```python
# Build or rebuild the memory index
await memory_service.build_memory_index(force_rebuild=True)

# Search with advanced filtering
memories = await memory_service.search_memories(
    query="important meeting",
    entity_id="entity123",
    category=MemoryCategory.INTERACTION,
    limit=10,
    min_relevance=0.3
)
```

## Performance Optimizations

### 1. Parallel Processing

The optimization system uses parallel processing in several areas:

- **Index building**: Process entity directories in parallel
- **Memory pruning**: Delete files in parallel batches
- **Batch operations**: Process operations in chunks with multiple workers

### 2. Caching Strategy

An intelligent caching system improves performance for frequently accessed memories:

- **LRU Cache**: Automatically manages itself to keep most recently used memories
- **Configurable size**: Adjust cache size based on available memory
- **Automatic updates**: Cache entries are refreshed on memory access/update

### 3. Efficient Storage

Storage optimizations to minimize disk usage:

- **Regular pruning**: Automatically remove low-relevance old memories
- **Memory merging**: Option to merge semantically similar memories
- **Compact storage format**: Efficient JSON structure

## Command-line Optimization Tool

The `optimize_memories.py` script provides a command-line interface for memory optimization tasks.

### Features:

- **Scheduled execution**: Run as a cron job or scheduled task
- **Configurable parameters**: Adjust threshold, age, decay rate
- **Comprehensive reporting**: Generate reports of optimization results
- **Storage statistics**: Track memory usage and reduction

### Usage:

```bash
# Run with default parameters
python optimize_memories.py

# Customize optimization
python optimize_memories.py --threshold=0.15 --age-days=45 --decay-amount=0.03
```

## Real-time Notifications

The WebSocket service provides real-time notifications about memory operations to clients:

- **Optimization events**: Notify when optimization processes start/complete
- **Memory updates**: Notify about individual memory changes
- **Pruning notifications**: Alert when memories are pruned
- **Entity-specific subscriptions**: Allow clients to subscribe to specific entities

## Best Practices

1. **Schedule Regular Optimization**
   - Run `optimize_memories.py` during off-peak hours
   - Recommended frequency: daily or weekly depending on memory volume

2. **Index Performance**
   - Rebuild indexes periodically for optimal performance
   - Consider increasing cache size for large memory sets

3. **Pruning Strategy**
   - Adjust thresholds based on entity needs
   - Consider more aggressive pruning for high-volume entities
   - Preserve important memories with higher relevance scores

4. **Memory Volume Guidelines**
   - <10,000 memories: Default settings work well
   - 10,000-100,000 memories: Increase parallel workers
   - >100,000 memories: Use specialized pruning and optimize storage path

5. **Monitoring and Maintenance**
   - Monitor storage growth over time
   - Review optimization reports regularly
   - Adjust parameters based on usage patterns

## Troubleshooting

### Common Issues and Solutions

1. **Slow index building**
   - Increase `max_workers` parameter
   - Use SSD storage for memory files
   - Consider splitting memory storage across multiple paths

2. **High memory usage**
   - Reduce cache size in MemoryIndex
   - Process larger memory sets in smaller batches
   - Ensure regular pruning is occurring

3. **WebSocket notification delays**
   - Verify WebSocket connections are properly maintained
   - Ensure client subscriptions are correctly registered

4. **Missing or corrupt indexes**
   - Force rebuild with `build_memory_index(force_rebuild=True)`
   - Check for disk space issues
   - Verify permissions on memory directories

## Example Workflow

Here's an example workflow for integrating memory optimization into a production system:

1. **Daily optimization** (runs at 3 AM):
   ```bash
   python optimize_memories.py --decay-amount=0.03 --threshold=0.1 --age-days=30
   ```

2. **Weekly deeper cleanup** (runs on Sundays):
   ```bash
   python optimize_memories.py --decay-amount=0.05 --threshold=0.2 --age-days=60
   ```

3. **Monthly maintenance** (runs first of month):
   ```bash
   # Rebuild indexes
   python -c "import asyncio; from backend.app.core.memory.memory_service import MemoryService; asyncio.run(MemoryService().build_memory_index(force_rebuild=True))"
   ```

## API Reference

See the Python docstrings in relevant modules for detailed API references:

- `memory_optimizer.py`: Core optimization algorithms
- `memory_index.py`: Advanced indexing system
- `memory_utils.py`: Utility functions for memory operations
- `memory_service.py`: High-level service interface
- `memory_ws_service.py`: WebSocket notification service 