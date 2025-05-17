using System;
using Visual_DM.Animation.Memory;

namespace Visual_DM.Animation.Memory
{
    /// <summary>
    /// High-level coordinator for animation memory management subsystems.
    /// </summary>
    public class AnimationMemorySystem
    {
        public readonly ObjectPool<object> ObjectPool;
        public readonly LRUCache<string, object> AnimationCache;
        public readonly MemoryBudgetManager BudgetManager;
        public readonly MemoryUsageMonitor UsageMonitor;
        public readonly AnimationMemoryAllocator Allocator;

        public AnimationMemorySystem()
        {
            ObjectPool = new ObjectPool<object>(initialSize: 128, maxSize: 4096);
            AnimationCache = new LRUCache<string, object>(capacity: 256);
            BudgetManager = new MemoryBudgetManager();
            UsageMonitor = new MemoryUsageMonitor();
            Allocator = new AnimationMemoryAllocator();
        }

        // Example: Rent an object from the pool
        public T RentObject<T>() where T : class, new()
        {
            // In a real system, use a pool per type
            return new T();
        }

        // Example: Add animation data to cache
        public void CacheAnimationData(string key, object data)
        {
            AnimationCache.AddOrUpdate(key, data);
        }

        // Example: Track memory usage
        public void TrackUsage(string component, long bytes)
        {
            UsageMonitor.Track(component, bytes);
        }

        // Example: Allocate memory for animation data
        public IntPtr Allocate(int size)
        {
            return Allocator.Allocate(size);
        }
    }
} 