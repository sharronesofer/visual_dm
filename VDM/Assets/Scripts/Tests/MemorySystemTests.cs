using System;
using UnityEngine;

namespace VisualDM.Tests
{
    public class MemorySystemTests : MonoBehaviour
    {
        private AnimationMemorySystem _memorySystem;

        void Start()
        {
            _memorySystem = new AnimationMemorySystem();
            Debug.Log("[MemorySystemTests] Starting tests...");

            // Test object pool
            var obj = _memorySystem.ObjectPool.Rent();
            _memorySystem.ObjectPool.Return(obj);
            Debug.Log($"[ObjectPool] Count: {_memorySystem.ObjectPool.Count}");

            // Test cache
            _memorySystem.CacheAnimationData("anim1", new object());
            if (_memorySystem.AnimationCache.TryGet("anim1", out var cached))
                Debug.Log("[LRUCache] Cache hit for 'anim1'");

            // Test memory budget
            bool allocated = _memorySystem.BudgetManager.TryAllocate(MemoryBudgetManager.Subsystem.Caches, 1024 * 1024);
            Debug.Log($"[BudgetManager] Allocation success: {allocated}");
            _memorySystem.BudgetManager.Release(MemoryBudgetManager.Subsystem.Caches, 1024 * 1024);

            // Test usage monitor
            _memorySystem.UsageMonitor.OnAlert += (component, usage) =>
                Debug.LogWarning($"[UsageMonitor] Alert: {component} usage high ({usage} bytes)");
            _memorySystem.TrackUsage("TestComponent", 200 * 1024 * 1024); // Should trigger alert

            // Test allocator
            IntPtr ptr = _memorySystem.Allocate(256);
            Debug.Log($"[Allocator] Allocated 256 bytes at {ptr}");
            _memorySystem.Allocator.FreeAll();
            Debug.Log("[Allocator] Freed all blocks");
        }
    }
} 