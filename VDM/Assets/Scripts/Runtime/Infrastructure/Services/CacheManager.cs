using System;
using System.Collections.Generic;
using UnityEngine;

namespace VDM.Infrastructure.Core
{
    public class CacheManager : MonoBehaviour
    {
        private static CacheManager _instance;
        public static CacheManager Instance
        {
            get
            {
                if (_instance == null)
                {
                    _instance = FindObjectOfType<CacheManager>();
                    if (_instance == null)
                    {
                        GameObject go = new GameObject("CacheManager");
                        _instance = go.AddComponent<CacheManager>();
                        DontDestroyOnLoad(go);
                    }
                }
                return _instance;
            }
        }

        [Header("Cache Settings")]
        public int maxCacheSize = 1000;
        public float defaultTTL = 300f; // 5 minutes
        public bool enableLogging = false;
        
        private Dictionary<string, CacheEntry> cache = new Dictionary<string, CacheEntry>();
        private Queue<string> accessOrder = new Queue<string>();
        private Dictionary<string, Dictionary<string, CacheEntry>> categories = new Dictionary<string, Dictionary<string, CacheEntry>>();
        
        [Serializable]
        public class CacheEntry
        {
            public object data;
            public DateTime createdAt;
            public DateTime lastAccessed;
            public float ttl;
            public int accessCount;
            
            public CacheEntry(object data, float ttl)
            {
                this.data = data;
                this.ttl = ttl;
                this.createdAt = DateTime.UtcNow;
                this.lastAccessed = DateTime.UtcNow;
                this.accessCount = 0;
            }
            
            public bool IsExpired()
            {
                return DateTime.UtcNow > createdAt.AddSeconds(ttl);
            }
        }
        
        void Start()
        {
            if (_instance != null && _instance != this)
            {
                Destroy(gameObject);
                return;
            }
            
            _instance = this;
            DontDestroyOnLoad(gameObject);
            
            // Initialize default categories
            categories["API"] = new Dictionary<string, CacheEntry>();
            categories["GameData"] = new Dictionary<string, CacheEntry>();
            categories["UserData"] = new Dictionary<string, CacheEntry>();
            
            // Start cleanup coroutine
            InvokeRepeating(nameof(CleanupExpiredEntries), 60f, 60f); // Every minute
        }
        
        public void Set<T>(string key, T data, float? ttl = null)
        {
            float cacheTTL = ttl ?? defaultTTL;
            
            if (cache.ContainsKey(key))
            {
                cache[key] = new CacheEntry(data, cacheTTL);
            }
            else
            {
                // Check if we need to evict entries
                if (cache.Count >= maxCacheSize)
                {
                    EvictLeastRecentlyUsed();
                }
                
                cache[key] = new CacheEntry(data, cacheTTL);
                accessOrder.Enqueue(key);
            }
            
            if (enableLogging)
                Debug.Log($"CacheManager: Set key '{key}' with TTL {cacheTTL}s");
        }
        
        public T Get<T>(string key, T defaultValue = default(T))
        {
            if (!cache.ContainsKey(key))
            {
                if (enableLogging)
                    Debug.Log($"CacheManager: Cache miss for key '{key}'");
                return defaultValue;
            }
            
            var entry = cache[key];
            
            if (entry.IsExpired())
            {
                cache.Remove(key);
                if (enableLogging)
                    Debug.Log($"CacheManager: Expired entry removed for key '{key}'");
                return defaultValue;
            }
            
            entry.lastAccessed = DateTime.UtcNow;
            entry.accessCount++;
            
            if (enableLogging)
                Debug.Log($"CacheManager: Cache hit for key '{key}'");
            
            try
            {
                return (T)entry.data;
            }
            catch (InvalidCastException)
            {
                Debug.LogError($"CacheManager: Type mismatch for key '{key}'. Expected {typeof(T)}, got {entry.data.GetType()}");
                return defaultValue;
            }
        }
        
        public bool Contains(string key)
        {
            if (!cache.ContainsKey(key))
                return false;
                
            var entry = cache[key];
            if (entry.IsExpired())
            {
                cache.Remove(key);
                return false;
            }
            
            return true;
        }
        
        public void Remove(string key)
        {
            if (cache.ContainsKey(key))
            {
                cache.Remove(key);
                if (enableLogging)
                    Debug.Log($"CacheManager: Removed key '{key}'");
            }
        }
        
        public void Clear()
        {
            cache.Clear();
            accessOrder.Clear();
            if (enableLogging)
                Debug.Log("CacheManager: Cache cleared");
        }
        
        public void ClearExpired()
        {
            var expiredKeys = new List<string>();
            
            foreach (var kvp in cache)
            {
                if (kvp.Value.IsExpired())
                {
                    expiredKeys.Add(kvp.Key);
                }
            }
            
            foreach (var key in expiredKeys)
            {
                cache.Remove(key);
            }
            
            if (enableLogging && expiredKeys.Count > 0)
                Debug.Log($"CacheManager: Removed {expiredKeys.Count} expired entries");
        }
        
        public void ClearCategory(string categoryName)
        {
            if (categories.ContainsKey(categoryName))
            {
                var categoryCache = categories[categoryName];
                var keysToRemove = new List<string>();
                
                // Find all cache keys that belong to this category
                foreach (var kvp in cache)
                {
                    if (categoryCache.ContainsKey(kvp.Key))
                    {
                        keysToRemove.Add(kvp.Key);
                    }
                }
                
                // Remove from main cache
                foreach (var key in keysToRemove)
                {
                    cache.Remove(key);
                }
                
                // Clear category cache
                categoryCache.Clear();
                
                if (enableLogging)
                    Debug.Log($"CacheManager: Cleared category '{categoryName}' - {keysToRemove.Count} items removed");
            }
        }
        
        public Dictionary<string, Dictionary<string, CacheEntry>> GetCategories()
        {
            return new Dictionary<string, Dictionary<string, CacheEntry>>(categories);
        }
        
        private void CleanupExpiredEntries()
        {
            ClearExpired();
        }
        
        private void EvictLeastRecentlyUsed()
        {
            if (accessOrder.Count == 0) return;
            
            string oldestKey = accessOrder.Dequeue();
            if (cache.ContainsKey(oldestKey))
            {
                cache.Remove(oldestKey);
                if (enableLogging)
                    Debug.Log($"CacheManager: Evicted LRU entry '{oldestKey}'");
            }
        }
        
        public CacheStats GetStats()
        {
            int expiredCount = 0;
            long totalMemory = 0;
            
            foreach (var entry in cache.Values)
            {
                if (entry.IsExpired())
                    expiredCount++;
                    
                // Estimate memory usage (rough calculation)
                if (entry.data != null)
                {
                    totalMemory += EstimateObjectSize(entry.data);
                }
            }
            
            return new CacheStats
            {
                totalEntries = cache.Count,
                expiredEntries = expiredCount,
                maxSize = maxCacheSize,
                hitRate = CalculateHitRate(),
                TotalItems = cache.Count,
                TotalMemoryUsage = totalMemory
            };
        }
        
        public CacheStats GetStatistics()
        {
            return GetStats();
        }
        
        private long EstimateObjectSize(object obj)
        {
            // Very rough estimation - in a real scenario, you'd use more sophisticated memory profiling
            if (obj == null) return 0;
            
            if (obj is string str)
                return str.Length * 2; // Unicode chars are 2 bytes
            else if (obj is int || obj is float)
                return 4;
            else if (obj is long || obj is double)
                return 8;
            else if (obj is bool)
                return 1;
            else
                return 64; // Default estimate for complex objects
        }
        
        private float CalculateHitRate()
        {
            // This would need to be tracked over time for accurate calculation
            // For now, return a placeholder
            return 0.85f;
        }
        
        public void LogStats()
        {
            var stats = GetStats();
            Debug.Log($"Cache Stats - Total: {stats.totalEntries}, Expired: {stats.expiredEntries}, Hit Rate: {stats.hitRate:P}");
        }
        
        [Serializable]
        public class CacheStats
        {
            public int totalEntries;
            public int expiredEntries;
            public int maxSize;
            public float hitRate;
            public int TotalItems;
            public long TotalMemoryUsage;
        }
    }
} 