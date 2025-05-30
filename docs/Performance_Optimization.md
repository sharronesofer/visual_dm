# Performance Optimization System

This document outlines the performance optimization systems implemented in the Visual DM application, including both client-side (Unity) and server-side (FastAPI) optimizations.

## Overview

The performance optimization system is designed to improve application performance through several key mechanisms:

1. **Object Pooling**: Reduces garbage collection overhead by reusing objects instead of constantly creating and destroying them
2. **Spatial Partitioning**: Optimizes spatial queries and collision detection through efficient space subdivision
3. **Memory Caching**: Improves performance by caching frequently accessed data
4. **Performance Monitoring**: Provides real-time metrics on system and application performance
5. **Lazy Loading**: Loads resources only when needed to reduce memory usage and startup time

## Client-Side Components (Unity)

### PerformanceManager

The `PerformanceManager` (located at `VDM/Assets/Scripts/Systems/Performance/PerformanceManager.cs`) is a singleton class that centralizes performance optimization functionality:

- **Object Pooling**: Manages pools of reusable objects to minimize garbage collection
- **Spatial Partitioning**: Efficient spatial queries for large worlds
- **Memory Caching**: Client-side caching of frequently accessed data
- **Performance Profiling**: Monitors operation times and logs warnings for slow operations
- **Resource Management**: Handles efficient loading and unloading of resources

Usage example:

```csharp
// Get an object from a pool
var enemyPool = PerformanceManager.Instance.GetObjectPool<Enemy>(enemyPrefab);
var enemy = enemyPool.Get();

// When done with the object, return it to the pool
enemyPool.Return(enemy);

// Spatial queries
PerformanceManager.Instance.RegisterSpatialEntity("player", playerPosition, 1.0f);
var nearbyEntities = PerformanceManager.Instance.QuerySpatialEntities(position, radius);

// Cache frequently accessed data
var cachedData = PerformanceManager.Instance.GetCachedItem<GameData>("gameState");
if (cachedData == null) {
    cachedData = LoadGameData();
    PerformanceManager.Instance.CacheItem("gameState", cachedData);
}

// Profile performance-sensitive code
PerformanceManager.Instance.StartTiming("LoadLevel");
LoadLevel();
PerformanceManager.Instance.EndTiming("LoadLevel");
```

### SpatialPartitionGrid

The `SpatialPartitionGrid` (located at `VDM/Assets/Scripts/Systems/Performance/SpatialPartitionGrid.cs`) implements a spatial partitioning system:

- Divides the world into a grid of cells
- Efficiently tracks entities in the grid
- Supports fast spatial queries (radius, line)
- Handles entity movement with minimal overhead

### PerformanceMonitor

The `PerformanceMonitor` (located at `VDM/Assets/Scripts/Systems/Performance/PerformanceMonitor.cs`) connects to the backend for real-time performance monitoring:

- Connects to the server via WebSockets
- Displays real-time performance metrics
- Includes an optional performance overlay
- Tracks system and application metrics over time

## Server-Side Components (FastAPI)

### Performance Service

The `PerformanceService` (located at `backend/services/performance_service.py`) provides server-side performance optimization:

- **Memory Caching**: Server-side caching system with TTL and LRU eviction
- **Performance Profiling**: Decorator-based profiling for functions
- **Request Throttling**: Prevents server overload
- **Query Optimization**: Suggests optimizations for database queries

Usage example:

```python
from backend.services.performance_service import performance_service, cached, timed, throttled

# Cache function results
@cached(ttl=300, namespace="user_data")
async def get_user_data(user_id: str):
    # Expensive database query...
    return data

# Track function execution time
@timed("process_world_update")
async def process_world_update(world_id: str):
    # Complex processing...
    return result

# Throttle resource-intensive operations
@throttled(category="heavy_operations")
async def generate_large_map(parameters: dict):
    # Resource-intensive operation...
    return map_data
```

### WebSocket Performance Manager

The `WebSocketPerformanceManager` (located at `backend/services/websocket_performance_service.py`) handles real-time performance metrics:

- Maintains WebSocket connections with clients
- Broadcasts system and application metrics
- Supports subscription-based metrics updates
- Tracks system resources (CPU, memory, I/O)

### Performance API Endpoints

The performance API (located at `backend/routers/performance.py`) provides REST endpoints for performance monitoring:

- `/api/performance/stats`: Get performance statistics
- `/api/performance/cache/stats`: Get cache usage statistics
- `/api/performance/cache/invalidate`: Invalidate cached items
- `/api/performance/hotspots`: Get most frequently accessed resources
- `/api/performance/analyze-query`: Analyze and optimize database queries
- `/api/performance/config`: Get/update performance configuration
- `/api/performance/memory/collect`: Trigger garbage collection

## Setting Up Performance Monitoring

1. **Unity Client**:
   - The `PerformanceManager` and `PerformanceMonitor` are automatically added to the `GameLoader` object in the Bootstrap scene
   - Configure server connection in the inspector settings
   - Enable performance overlay for real-time metrics display

2. **FastAPI Server**:
   - Ensure the `psutil` package is installed
   - The performance routes are automatically included in the main FastAPI application
   - Set the `PERFORMANCE_API_KEY` environment variable for API security

## Best Practices

1. **Object Pooling**:
   - Use object pools for frequently created/destroyed objects
   - Return objects to pools when they're no longer needed
   - Pre-populate pools during loading screens

2. **Spatial Queries**:
   - Register all spatially-relevant entities with the spatial partitioning system
   - Use spatial queries instead of distance checks against all entities
   - Update entity positions when they move

3. **Caching**:
   - Cache expensive computations and database queries
   - Set appropriate TTL values based on data volatility
   - Invalidate cache entries when underlying data changes

4. **Performance Profiling**:
   - Wrap performance-sensitive operations with timing calls
   - Monitor the performance dashboard for slowdowns
   - Optimize operations that exceed warning thresholds

5. **Resource Management**:
   - Use lazy loading for non-essential resources
   - Unload unused resources periodically
   - Balance memory usage with load times

## Troubleshooting

Common issues and solutions:

1. **Memory Leaks**:
   - Check if objects are being returned to pools properly
   - Verify all event subscriptions are properly unsubscribed
   - Look for static references keeping objects alive

2. **Slow Performance**:
   - Check the performance dashboard for bottlenecks
   - Analyze which operations are taking the most time
   - Consider optimizing or caching slow operations

3. **High CPU Usage**:
   - Look for tight loops or inefficient algorithms
   - Check if spatial queries are being used correctly
   - Verify physics and collision detection settings

4. **Network Issues**:
   - Check WebSocket connection status
   - Verify server is running and accessible
   - Check for firewall or network configuration issues

## Performance Metrics Reference

Key metrics to monitor:

1. **System Metrics**:
   - CPU Usage: Below 80% for smooth performance
   - Memory Usage: Should not continuously grow
   - Disk/Network I/O: Spikes only during loading

2. **Application Metrics**:
   - Operation Times: Most should be under 16ms (60fps)
   - Cache Hit Rate: Should be above 80% for optimal performance
   - Hot Resources: Identify frequently accessed resources

3. **Unity-Specific**:
   - Garbage Collection: Monitor frequency and duration
   - Object Pool Sizes: Adjust based on usage patterns
   - Spatial Grid Density: Balance between query speed and memory usage

## Future Improvements

Planned enhancements:

1. Advanced occlusion culling for dense scenes
2. Multi-threaded resource loading
3. Level-of-detail (LOD) system for complex objects
4. Predictive resource loading based on player movement
5. Distributed cache with Redis integration 