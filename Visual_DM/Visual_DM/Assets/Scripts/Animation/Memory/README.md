# Animation Memory Management Components

This directory contains runtime-only, thread-safe memory management utilities for the animation system. All components are designed for use in Unity 2D projects, with no reliance on UnityEditor, scene references, or drag-and-drop workflows.

## Components

- **ObjectPool.cs**: Generic, thread-safe object pool for animation system objects (transforms, keyframes, interpolators, etc.). Supports pre-allocation and automatic pool sizing.
- **LRUCache.cs**: Thread-safe, generic Least Recently Used (LRU) cache for animation data. Supports predictive caching and cache invalidation.
- **MemoryBudgetManager.cs**: Manages configurable memory budgets for animation subsystems. Supports priority-based allocation and graceful degradation.
- **MemoryUsageMonitor.cs**: Real-time memory usage tracking for animation components. Provides alerting and hooks for visualization tools.
- **AnimationMemoryAllocator.cs**: Custom allocator for animation data, minimizing fragmentation and supporting batch allocations.

## Usage Guidelines
- All classes are safe for use in multi-threaded environments and integrate with the animation thread pool.
- Designed for runtime-only use; no UnityEditor dependencies.
- All memory management is performed programmatically; no scene or prefab references required.
- Integrate with `GameLoader.cs` or animation system entry points as needed.

## Best Practices
- Use `ObjectPool<T>` for frequently created/destroyed animation objects.
- Use `LRUCache<TKey, TValue>` for caching animation data with predictable access patterns.
- Use `MemoryBudgetManager` to enforce memory limits and handle low-memory scenarios gracefully.
- Use `MemoryUsageMonitor` to track and visualize memory usage, and to detect leaks or excessive consumption.
- Use `AnimationMemoryAllocator` for custom allocation patterns where .NET GC is insufficient.

---

*All code in this directory is designed for high-performance, memory-constrained, and parallel animation processing environments.* 