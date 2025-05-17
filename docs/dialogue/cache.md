# DialogueCache: Caching System for Dialogue Responses

The `DialogueCache` class provides a robust, thread-safe caching layer for dialogue responses, supporting TTL expiration, LRU eviction, analytics, and pre-warming. It is designed to optimize API usage and response times in dynamic dialogue systems.

## Features
- In-memory cache with configurable size and TTL (time-to-live)
- LRU (Least Recently Used) eviction policy
- Time-based expiration for cache entries
- Manual and pattern-based invalidation
- Analytics for cache hits, misses, and most frequently requested items
- Pre-warming from dictionaries or files
- Thread-safe for concurrent access

## Usage Example
```python
from dialogue.cache import DialogueCache

# Create a cache with a max size of 500 and TTL of 5 minutes
cache = DialogueCache(max_size=500, ttl=300)

# Store a response
cache.set('prompt:user:hello', 'Hi there!')

# Retrieve a response
response = cache.get('prompt:user:hello')

# Invalidate a specific key
cache.invalidate('prompt:user:hello')

# Invalidate all keys matching a pattern
cache.invalidate_pattern('prompt:user:')

# Prewarm cache with a dictionary
cache.prewarm({'prompt:user:bye': 'Goodbye!'})

# Prewarm cache from a JSON file
cache.prewarm_from_file('prewarm.json')

# Get analytics
stats = cache.analytics()
print(stats)
```

## Configuration
- `max_size`: Maximum number of items in the cache (default: 1000)
- `ttl`: Time-to-live for each cache entry in seconds (default: 600)

## Invalidation
- `invalidate(key)`: Remove a specific cache entry
- `invalidate_pattern(pattern)`: Remove all entries whose keys contain the given pattern
- `clear()`: Remove all entries and reset analytics

## Analytics
- `analytics()`: Returns a dictionary with:
  - `hits`, `misses`, `hit_ratio`
  - `most_frequently_requested`: Top 10 most accessed keys
  - `current_size`, `max_size`, `ttl`

## Pre-warming
- `prewarm(items: dict)`: Bulk load key-value pairs into the cache
- `prewarm_from_file(filepath, loader=None)`: Load cache entries from a file (default: JSON)

## Thread Safety
All cache operations are protected by a reentrant lock, making the cache safe for concurrent use in multi-threaded environments.

## Performance Considerations
- For high-throughput systems, tune `max_size` and `ttl` based on memory and expected usage patterns
- Use pre-warming to reduce cold start latency for common dialogue paths
- Monitor analytics to adjust cache parameters for optimal hit rates

## Testing
Unit tests are provided in `tests/dialogue/test_cache.py`.

## Best Practices
- Normalize cache keys to avoid duplication
- Use context and character identity in keys for maximum cache effectiveness
- Regularly review analytics to identify hot paths and optimize pre-warming

## Future Improvements
- Optional persistent storage (e.g., SQLite or file-based)
- Distributed cache support for multi-process or multi-server deployments
- Advanced analytics and reporting 