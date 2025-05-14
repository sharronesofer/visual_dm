# Cache Invalidation Strategies

## 1. Overview

This document outlines the cache invalidation strategies implemented across the Visual DM application. Proper cache invalidation is critical to maintaining data consistency while preserving the performance benefits of caching.

## 2. Cache Implementation

Visual DM uses a Redis-based caching system with the following characteristics:

- **Primary Cache Store**: Redis
- **Client Implementation**: Custom `RedisService` wrapper
- **Serialization**: JSON for most objects, MessagePack for binary data
- **Default TTL**: Varies by domain (1 minute to 24 hours)
- **Key Structure**: Domain-specific prefixes (e.g., `character:123`, `quest:456`)

## 3. General Invalidation Principles

### 3.1 Key Cache Patterns

| Pattern | Description | Use Case |
|---------|-------------|----------|
| **Time-based Expiration** | Cache entries expire after a predefined TTL | Data that can tolerate some staleness |
| **Write-through** | Updates to the database are also applied to cache | Critical data requiring immediate consistency |
| **Lazy Loading** | Cache populated on first request, subsequent requests use cache | Non-critical, frequently accessed data |
| **Refresh-ahead** | Cache proactively refreshed before expiration | Predictably accessed, performance-critical data |

### 3.2 Invalidation Triggers

| Trigger Type | Description | Implementation |
|--------------|-------------|----------------|
| **Direct Invalidation** | Explicitly remove cache entries when data changes | `RedisService.delete(key)` |
| **Pattern Invalidation** | Remove multiple related cache entries using patterns | `RedisService.deleteByPattern(pattern)` |
| **Event-based Invalidation** | Subscribe to data change events to trigger invalidation | Event listeners on data operations |
| **Bulk Invalidation** | Clear entire cache domains during major updates | `RedisService.flushDb()` or namespace-specific methods |

## 4. Domain-specific Invalidation Strategies

### 4.1 Character Data Invalidation

| Operation | Invalidation Strategy | Cache Keys Affected |
|-----------|----------------------|---------------------|
| **Character Create** | No invalidation required (new data) | N/A |
| **Character Update** | Tag-based invalidation | `character:${id}`, `character:${id}:*` |
| **Character Stats Update** | Targeted invalidation | `character:${id}:stats` |
| **Character Delete** | Full character invalidation | `character:${id}*` |
| **Bulk Character Update** | Batch invalidation | Multiple character keys based on updated IDs |

**Implementation Example:**

```python
def update_character(character_id, data):
    # Update database
    db.characters.update(character_id, data)
    
    # Invalidate cache entries
    redis_service.delete(f"character:{character_id}")
    redis_service.delete_by_pattern(f"character:{character_id}:*")
    
    # If character is in a faction, invalidate faction member list
    if "faction_id" in data:
        redis_service.delete(f"faction:{data['faction_id']}:members")
```

### 4.2 Faction Data Invalidation

| Operation | Invalidation Strategy | Cache Keys Affected |
|-----------|----------------------|---------------------|
| **Faction Create** | No invalidation required (new data) | N/A |
| **Faction Update** | Tag-based invalidation | `faction:${id}`, `faction:${id}:*` |
| **Member Add/Remove** | Member list invalidation | `faction:${id}:members` |
| **Faction Delete** | Full faction invalidation + member character invalidation | `faction:${id}*` + affected character keys |
| **Faction Relationship Change** | Related factions invalidation | `faction:${id}:relations`, related faction keys |

**Implementation Example:**

```python
def add_character_to_faction(character_id, faction_id):
    # Update database
    db.factions.add_member(faction_id, character_id)
    
    # Invalidate faction member list
    redis_service.delete(f"faction:{faction_id}:members")
    
    # Invalidate character's faction relationship
    redis_service.delete(f"character:{character_id}:faction")
```

### 4.3 Quest Data Invalidation

| Operation | Invalidation Strategy | Cache Keys Affected |
|-----------|----------------------|---------------------|
| **Quest Create** | No invalidation required (new data) | N/A |
| **Quest Update** | Tag-based invalidation | `quest:${id}`, `quest:${id}:*` |
| **Quest Assignment** | Quest and character invalidation | `quest:${id}:assignments`, `character:${character_id}:quests` |
| **Quest Completion** | Quest status and character progress invalidation | `quest:${id}:status`, `character:${character_id}:progress` |
| **Quest Delete** | Full quest invalidation + character quest list invalidation | `quest:${id}*`, affected character quest lists |

**Implementation Example:**

```python
def assign_quest_to_character(quest_id, character_id):
    # Update database
    db.quests.assign(quest_id, character_id)
    
    # Invalidate quest assignments
    redis_service.delete(f"quest:{quest_id}:assignments")
    
    # Invalidate character's quest list
    redis_service.delete(f"character:{character_id}:quests")
```

### 4.4 Spatial Data Invalidation

| Operation | Invalidation Strategy | Cache Keys Affected |
|-----------|----------------------|---------------------|
| **Entity Position Update** | Spatial region invalidation | `spatial:region:${x}:${y}:entities` |
| **Building Addition/Removal** | Full region invalidation | `spatial:region:${x}:${y}:*` |
| **Map Generation** | Full spatial cache invalidation | `spatial:*` |
| **Pathfinding Cache** | Path-specific invalidation | `spatial:path:${start_x}:${start_y}:${end_x}:${end_y}` |
| **Spatial Query Results** | Time-based expiration only (short TTL) | Query-specific cached results |

**Implementation Example:**

```python
def update_entity_position(entity_id, old_position, new_position):
    # Update spatial index
    spatial_index.remove(entity_id, old_position)
    spatial_index.insert(entity_id, new_position)
    
    # Calculate affected regions
    old_region = get_region_for_position(old_position)
    new_region = get_region_for_position(new_position)
    
    # Invalidate affected spatial regions
    redis_service.delete(f"spatial:region:{old_region.x}:{old_region.y}:entities")
    redis_service.delete(f"spatial:region:{new_region.x}:{new_region.y}:entities")
    
    # Invalidate related path caches
    redis_service.delete_by_pattern(f"spatial:path:*:{new_region.x}:{new_region.y}:*")
    redis_service.delete_by_pattern(f"spatial:path:*:{old_region.x}:{old_region.y}:*")
```

### 4.5 Authentication Data Invalidation

| Operation | Invalidation Strategy | Cache Keys Affected |
|-----------|----------------------|---------------------|
| **User Login** | No invalidation required (new session) | N/A |
| **User Logout** | Token invalidation | `auth:token:${token_id}` |
| **Password Change** | All user tokens invalidation | `auth:user:${user_id}:tokens:*` |
| **Permission Change** | Permission cache invalidation | `auth:user:${user_id}:permissions` |
| **Account Suspension** | Full user invalidation + tokens blacklisting | `auth:user:${user_id}:*` + addition to blacklist |

**Implementation Example:**

```python
def change_user_password(user_id, new_password):
    # Update database
    db.users.update_password(user_id, new_password)
    
    # Invalidate all user tokens
    redis_service.delete_by_pattern(f"auth:user:{user_id}:tokens:*")
    
    # Add all existing tokens to blacklist with expiration
    tokens = db.tokens.get_for_user(user_id)
    for token in tokens:
        redis_service.set(f"auth:blacklist:token:{token.id}", "1", expiry=token.expiry)
```

## 5. Advanced Invalidation Techniques

### 5.1 Versioning-based Invalidation

For frequently accessed but occasionally updated data, we use version-based invalidation:

```python
def get_versioned_data(key, fetcher_func):
    # Check for version in cache
    current_version = redis_service.get(f"{key}:version") or 0
    
    # Try to get cached data with correct version
    cached_data = redis_service.get(f"{key}:v{current_version}")
    
    if cached_data:
        return cached_data
    
    # Fetch fresh data
    fresh_data = fetcher_func()
    
    # Store with new version
    new_version = int(current_version) + 1
    redis_service.set(f"{key}:version", new_version)
    redis_service.set(f"{key}:v{new_version}", fresh_data)
    
    return fresh_data
```

### 5.2 Asynchronous Invalidation for High-Volume Operations

For high-volume operations, we use an event-driven asynchronous invalidation pattern:

```python
# Producer side
def bulk_update_entities(entities):
    # Update database
    db.entities.bulk_update(entities)
    
    # Queue invalidation events rather than performing directly
    for entity in entities:
        event_queue.publish('cache_invalidation', {
            'type': entity.type,
            'id': entity.id,
            'operation': 'update'
        })

# Consumer side (runs asynchronously)
def process_invalidation_events():
    while True:
        event = event_queue.consume('cache_invalidation')
        if event:
            entity_type = event['type']
            entity_id = event['id']
            operation = event['operation']
            
            if operation == 'update':
                redis_service.delete(f"{entity_type}:{entity_id}")
                redis_service.delete_by_pattern(f"{entity_type}:{entity_id}:*")
```

### 5.3 Circuit Breaker for Cache Failures

To handle Redis outages gracefully, we implement a circuit breaker pattern:

```python
def cache_with_circuit_breaker(key, ttl, fetcher_func):
    if circuit_breaker.is_open('redis'):
        # Cache is considered unavailable, fetch data directly
        return fetcher_func()
    
    try:
        # Try to get from cache
        cached_data = redis_service.get(key)
        if cached_data:
            return cached_data
        
        # Cache miss, fetch data
        fresh_data = fetcher_func()
        
        # Store in cache if circuit is closed
        redis_service.set(key, fresh_data, ttl=ttl)
        
        return fresh_data
    except RedisException:
        # Failed to interact with Redis, open circuit
        circuit_breaker.open('redis')
        
        # Return fresh data
        return fetcher_func()
```

## 6. Monitoring and Performance

### 6.1 Cache Hit Rate Monitoring

For performance tuning and observability, we monitor cache hit rates:

```python
def get_with_monitoring(key, fetcher_func):
    metrics.increment('cache.requests')
    
    cached_data = redis_service.get(key)
    if cached_data:
        metrics.increment('cache.hits')
        return cached_data
    
    metrics.increment('cache.misses')
    fresh_data = fetcher_func()
    redis_service.set(key, fresh_data)
    
    return fresh_data
```

### 6.2 Invalidation Metrics

We track and report invalidation operations to detect potential over-invalidation:

| Metric | Description | Target |
|--------|-------------|--------|
| **Direct Invalidations/sec** | Rate of specific key invalidations | < 100/sec |
| **Pattern Invalidations/sec** | Rate of wildcard invalidations | < 10/sec |
| **Bulk Invalidations/sec** | Rate of large-scale invalidations | < 1/min |
| **Cache Hit Rate** | Percentage of cache hits vs. total requests | > 80% |
| **Cache Size** | Total memory used by Redis | < 2GB |

## 7. Consistency vs. Performance Tradeoffs

### 7.1 Data Freshness Requirements

| Data Type | Freshness Requirement | Strategy |
|-----------|----------------------|----------|
| **Authentication State** | Real-time (seconds) | Direct invalidation, short TTL (5 min) |
| **Character Core Data** | Near real-time (minutes) | Direct invalidation, medium TTL (15 min) |
| **Quest Status** | Near real-time (minutes) | Direct invalidation, medium TTL (10 min) |
| **Spatial Data** | Real-time (seconds) | Direct invalidation, short TTL (1 min) |
| **Faction Relationships** | Eventually consistent (hours) | Time-based expiration, long TTL (1 hour) |
| **World Data** | Eventually consistent (hours) | Time-based expiration, long TTL (24 hours) |

### 7.2 Cache Warming Strategies

For critical application data, we implement proactive cache warming:

```python
def warm_critical_caches():
    # Warm character cache for online users
    online_user_ids = session_service.get_online_user_ids()
    for user_id in online_user_ids:
        character = db.characters.get_by_user_id(user_id)
        redis_service.set(f"character:{character.id}", character)
        
    # Warm active quest data
    active_quests = db.quests.get_active()
    for quest in active_quests:
        redis_service.set(f"quest:{quest.id}", quest)
        
    # Warm current map regions based on player positions
    active_regions = spatial_service.get_active_regions()
    for region in active_regions:
        entities = spatial_index.query_region(region)
        redis_service.set(f"spatial:region:{region.x}:{region.y}:entities", entities)
```

## 8. Disaster Recovery

### 8.1 Cache Failure Scenarios

| Scenario | Recovery Strategy | Impact |
|----------|------------------|--------|
| **Redis Connection Failure** | Circuit breaker, fallback to direct database access | Temporary performance degradation |
| **Redis Cluster Failover** | Automatic reconnection with exponential backoff | Minimal (seconds of unavailability) |
| **Complete Cache Loss** | Gradual rebuild through normal application operation | Initial performance degradation |
| **Corrupted Cache Data** | Full cache flush and rebuild | Temporary performance degradation |

### 8.2 Recovery Procedures

In case of complete cache failure, the following procedure is implemented:

1. Detect cache unavailability through health checks
2. Switch to circuit breaker mode for all cache operations
3. Apply rate limiting to database access if necessary
4. Once cache is available again:
   - Clear all potentially corrupted data
   - Warm critical caches
   - Gradually restore circuit breakers
   - Monitor performance metrics during recovery

## 9. Cache Configuration Reference

| Parameter | Value | Description |
|-----------|-------|-------------|
| **Redis Connection Timeout** | 200ms | Maximum time to wait for connection |
| **Redis Read Timeout** | 500ms | Maximum time to wait for read operation |
| **Redis Write Timeout** | 500ms | Maximum time to wait for write operation |
| **Circuit Breaker Threshold** | 5 failures | Number of failures before opening circuit |
| **Circuit Breaker Reset Time** | 30 seconds | Time before attempting to reset circuit |
| **Default TTL** | 15 minutes | Default cache expiration time |
| **Maximum Key Size** | 512 bytes | Maximum allowed Redis key size |
| **Maximum Value Size** | 1MB | Maximum allowed Redis value size |

## 10. Maintenance and Best Practices

### 10.1 Cache Maintenance Procedures

- **Daily**: Monitor cache size and hit rates
- **Weekly**: Analyze invalidation patterns for optimization
- **Monthly**: Review TTL settings based on access patterns
- **Quarterly**: Full cache configuration review

### 10.2 Developer Guidelines

1. **Always define TTL**: Never cache without an expiration
2. **Use specific keys**: Avoid overly generic keys
3. **Consistent naming**: Follow the `domain:id:attribute` pattern
4. **Invalidate precisely**: Target specific keys rather than patterns when possible
5. **Handle failures**: Always implement fallbacks for cache misses or failures
6. **Document new caches**: Update this document when adding new cache domains

Version: 1.0  
Last Updated: [Current Date]  
Next Review: [Current Date + 3 months] 