using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using VDM.Runtime.Core.Services;

namespace VDM.Runtime.Core.Services
{
    /// <summary>
    /// Intelligent caching system with advanced strategies for performance optimization.
    /// Implements LRU, predictive loading, and smart invalidation policies.
    /// </summary>
    public class CacheManager : MonoBehaviour
    {
        [Header("Cache Configuration")]
        [SerializeField] private int _maxCacheSize = 1000;
        [SerializeField] private long _maxMemoryUsageMB = 512;
        [SerializeField] private float _cacheCleanupInterval = 60f; // seconds
        [SerializeField] private float _defaultTTL = 300f; // 5 minutes default TTL
        [SerializeField] private bool _enablePredictiveLoading = true;
        [SerializeField] private bool _enableCompressionForLargeItems = true;
        
        [Header("Performance Thresholds")]
        [SerializeField] private int _compressionThresholdBytes = 1024; // 1KB
        [SerializeField] private float _accessPatternAnalysisInterval = 120f; // 2 minutes
        [SerializeField] private int _minAccessCountForPrediction = 3;
        [SerializeField] private float _predictionConfidenceThreshold = 0.7f;
        
        // Cache storage
        private Dictionary<string, CacheEntry> _cache = new Dictionary<string, CacheEntry>();
        private Dictionary<string, CacheCategory> _categories = new Dictionary<string, CacheCategory>();
        private LinkedList<string> _accessOrder = new LinkedList<string>(); // For LRU
        private Dictionary<string, LinkedListNode<string>> _accessNodes = new Dictionary<string, LinkedListNode<string>>();
        
        // Access pattern tracking
        private Dictionary<string, AccessPattern> _accessPatterns = new Dictionary<string, AccessPattern>();
        private Dictionary<string, List<string>> _accessSequences = new Dictionary<string, List<string>>();
        
        // Performance monitoring
        private PerformanceMonitor _performanceMonitor;
        private CacheStatistics _statistics = new CacheStatistics();
        
        // Events
        public event Action<string, object> OnCacheHit;
        public event Action<string> OnCacheMiss;
        public event Action<string> OnCacheEvicted;
        public event Action<CacheStatistics> OnStatisticsUpdated;
        
        #region Unity Lifecycle
        
        private void Awake()
        {
            InitializeCache();
        }
        
        private void Start()
        {
            _performanceMonitor = FindObjectOfType<PerformanceMonitor>();
            StartCoroutine(CacheMaintenanceLoop());
            
            if (_enablePredictiveLoading)
            {
                StartCoroutine(AccessPatternAnalysisLoop());
            }
        }
        
        private void OnDestroy()
        {
            StopAllCoroutines();
            ClearCache();
        }
        
        #endregion
        
        #region Initialization
        
        private void InitializeCache()
        {
            // Initialize default cache categories
            _categories["API"] = new CacheCategory
            {
                Name = "API",
                DefaultTTL = 180f, // 3 minutes for API responses
                MaxSize = 300,
                CompressionEnabled = true,
                Priority = CachePriority.High
            };
            
            _categories["GameData"] = new CacheCategory
            {
                Name = "GameData",
                DefaultTTL = 600f, // 10 minutes for game data
                MaxSize = 200,
                CompressionEnabled = false,
                Priority = CachePriority.High
            };
            
            _categories["UI"] = new CacheCategory
            {
                Name = "UI",
                DefaultTTL = 300f, // 5 minutes for UI data
                MaxSize = 150,
                CompressionEnabled = false,
                Priority = CachePriority.Medium
            };
            
            _categories["Temporary"] = new CacheCategory
            {
                Name = "Temporary",
                DefaultTTL = 60f, // 1 minute for temporary data
                MaxSize = 100,
                CompressionEnabled = true,
                Priority = CachePriority.Low
            };
            
            Debug.Log("[CacheManager] Initialized with default categories");
        }
        
        #endregion
        
        #region Core Cache Operations
        
        public T Get<T>(string key, string category = "GameData") where T : class
        {
            if (!_cache.ContainsKey(key))
            {
                _statistics.Misses++;
                OnCacheMiss?.Invoke(key);
                TrackAccessPattern(key, false);
                return null;
            }
            
            var entry = _cache[key];
            
            // Check if expired
            if (IsExpired(entry))
            {
                Remove(key);
                _statistics.Misses++;
                OnCacheMiss?.Invoke(key);
                TrackAccessPattern(key, false);
                return null;
            }
            
            // Update access information
            entry.LastAccessTime = DateTime.Now;
            entry.AccessCount++;
            UpdateAccessOrder(key);
            
            _statistics.Hits++;
            OnCacheHit?.Invoke(key, entry.Data);
            TrackAccessPattern(key, true);
            
            // Try to decompress if needed
            if (entry.IsCompressed && entry.Data is byte[] compressedData)
            {
                return DecompressData<T>(compressedData);
            }
            
            return entry.Data as T;
        }
        
        public void Set<T>(string key, T data, string category = "GameData", float? ttl = null) where T : class
        {
            if (data == null) return;
            
            var categoryConfig = _categories.ContainsKey(category) ? _categories[category] : _categories["GameData"];
            var actualTTL = ttl ?? categoryConfig.DefaultTTL;
            
            // Check if we need to make space
            EnsureSpace(categoryConfig);
            
            // Determine if compression is needed
            bool shouldCompress = ShouldCompress(data, categoryConfig);
            object storeData = data;
            
            if (shouldCompress)
            {
                storeData = CompressData(data);
            }
            
            var entry = new CacheEntry
            {
                Key = key,
                Data = storeData,
                Category = category,
                CreatedTime = DateTime.Now,
                LastAccessTime = DateTime.Now,
                ExpiryTime = DateTime.Now.AddSeconds(actualTTL),
                AccessCount = 1,
                IsCompressed = shouldCompress,
                OriginalSize = GetDataSize(data),
                CompressedSize = shouldCompress ? GetDataSize(storeData) : GetDataSize(data)
            };
            
            // Update or add entry
            if (_cache.ContainsKey(key))
            {
                var oldEntry = _cache[key];
                _statistics.TotalMemoryUsage -= oldEntry.CompressedSize;
                UpdateAccessOrder(key);
            }
            else
            {
                AddToAccessOrder(key);
            }
            
            _cache[key] = entry;
            _statistics.TotalMemoryUsage += entry.CompressedSize;
            _statistics.TotalItems = _cache.Count;
            
            _performanceMonitor?.TrackMemoryUsage($"Cache_{category}", _statistics.TotalMemoryUsage);
            
            Debug.Log($"[CacheManager] Cached {key} in category {category} (TTL: {actualTTL}s, Compressed: {shouldCompress})");
        }
        
        public void Remove(string key)
        {
            if (!_cache.ContainsKey(key)) return;
            
            var entry = _cache[key];
            _cache.Remove(key);
            RemoveFromAccessOrder(key);
            
            _statistics.TotalMemoryUsage -= entry.CompressedSize;
            _statistics.TotalItems = _cache.Count;
            
            OnCacheEvicted?.Invoke(key);
            Debug.Log($"[CacheManager] Removed {key} from cache");
        }
        
        public bool Contains(string key)
        {
            if (!_cache.ContainsKey(key)) return false;
            
            var entry = _cache[key];
            if (IsExpired(entry))
            {
                Remove(key);
                return false;
            }
            
            return true;
        }
        
        public void ClearCategory(string category)
        {
            var keysToRemove = _cache.Where(kvp => kvp.Value.Category == category).Select(kvp => kvp.Key).ToList();
            
            foreach (var key in keysToRemove)
            {
                Remove(key);
            }
            
            Debug.Log($"[CacheManager] Cleared category {category} ({keysToRemove.Count} items)");
        }
        
        public void ClearCache()
        {
            var count = _cache.Count;
            _cache.Clear();
            _accessOrder.Clear();
            _accessNodes.Clear();
            
            _statistics = new CacheStatistics();
            
            Debug.Log($"[CacheManager] Cleared entire cache ({count} items)");
        }
        
        #endregion
        
        #region Cache Maintenance
        
        private IEnumerator CacheMaintenanceLoop()
        {
            while (true)
            {
                yield return new WaitForSeconds(_cacheCleanupInterval);
                
                try
                {
                    PerformMaintenance();
                    UpdateStatistics();
                }
                catch (Exception ex)
                {
                    Debug.LogError($"[CacheManager] Error in maintenance loop: {ex.Message}");
                }
            }
        }
        
        private void PerformMaintenance()
        {
            var expiredKeys = new List<string>();
            var currentTime = DateTime.Now;
            
            // Find expired entries
            foreach (var kvp in _cache)
            {
                if (IsExpired(kvp.Value))
                {
                    expiredKeys.Add(kvp.Key);
                }
            }
            
            // Remove expired entries
            foreach (var key in expiredKeys)
            {
                Remove(key);
            }
            
            // Check memory usage and clean if necessary
            if (_statistics.TotalMemoryUsage > _maxMemoryUsageMB * 1024 * 1024)
            {
                PerformMemoryCleanup();
            }
            
            // Clean up old access patterns
            CleanupAccessPatterns();
            
            Debug.Log($"[CacheManager] Maintenance completed: Removed {expiredKeys.Count} expired items");
        }
        
        private void PerformMemoryCleanup()
        {
            var itemsToRemove = CalculateItemsToRemove();
            
            foreach (var key in itemsToRemove)
            {
                Remove(key);
            }
            
            Debug.Log($"[CacheManager] Memory cleanup: Removed {itemsToRemove.Count} items");
        }
        
        private List<string> CalculateItemsToRemove()
        {
            // LRU + Priority-based removal
            var candidates = _cache.Values
                .OrderBy(e => _categories.ContainsKey(e.Category) ? (int)_categories[e.Category].Priority : 2)
                .ThenBy(e => e.LastAccessTime)
                .ThenBy(e => e.AccessCount)
                .Take(_cache.Count / 4) // Remove up to 25% of items
                .Select(e => e.Key)
                .ToList();
            
            return candidates;
        }
        
        #endregion
        
        #region Predictive Loading
        
        private IEnumerator AccessPatternAnalysisLoop()
        {
            while (_enablePredictiveLoading)
            {
                yield return new WaitForSeconds(_accessPatternAnalysisInterval);
                
                try
                {
                    AnalyzeAccessPatterns();
                    GeneratePredictions();
                }
                catch (Exception ex)
                {
                    Debug.LogError($"[CacheManager] Error in access pattern analysis: {ex.Message}");
                }
            }
        }
        
        private void TrackAccessPattern(string key, bool hit)
        {
            if (!_accessPatterns.ContainsKey(key))
            {
                _accessPatterns[key] = new AccessPattern
                {
                    Key = key,
                    AccessTimes = new List<DateTime>(),
                    HitRate = 0f,
                    PredictedNextAccess = DateTime.MinValue
                };
            }
            
            var pattern = _accessPatterns[key];
            pattern.AccessTimes.Add(DateTime.Now);
            
            // Keep only recent accesses
            var cutoff = DateTime.Now.AddMinutes(-30);
            pattern.AccessTimes = pattern.AccessTimes.Where(t => t > cutoff).ToList();
            
            // Update hit rate
            if (hit)
            {
                pattern.HitCount++;
            }
            pattern.TotalRequests++;
            pattern.HitRate = (float)pattern.HitCount / pattern.TotalRequests;
        }
        
        private void AnalyzeAccessPatterns()
        {
            foreach (var pattern in _accessPatterns.Values)
            {
                if (pattern.AccessTimes.Count >= _minAccessCountForPrediction)
                {
                    // Calculate average time between accesses
                    var intervals = new List<double>();
                    for (int i = 1; i < pattern.AccessTimes.Count; i++)
                    {
                        intervals.Add((pattern.AccessTimes[i] - pattern.AccessTimes[i - 1]).TotalSeconds);
                    }
                    
                    if (intervals.Any())
                    {
                        pattern.AverageInterval = intervals.Average();
                        pattern.PredictedNextAccess = pattern.AccessTimes.Last().AddSeconds(pattern.AverageInterval);
                    }
                }
            }
        }
        
        private void GeneratePredictions()
        {
            var now = DateTime.Now;
            var predictions = _accessPatterns.Values
                .Where(p => p.PredictedNextAccess > now && 
                           p.PredictedNextAccess < now.AddMinutes(5) && 
                           p.HitRate > _predictionConfidenceThreshold)
                .OrderBy(p => p.PredictedNextAccess)
                .Take(10) // Limit predictions
                .ToList();
            
            foreach (var prediction in predictions)
            {
                // Trigger predictive loading event
                Debug.Log($"[CacheManager] Predicted access for {prediction.Key} at {prediction.PredictedNextAccess}");
            }
        }
        
        #endregion
        
        #region Compression
        
        private bool ShouldCompress<T>(T data, CacheCategory category) where T : class
        {
            if (!category.CompressionEnabled || !_enableCompressionForLargeItems)
                return false;
            
            var size = GetDataSize(data);
            return size > _compressionThresholdBytes;
        }
        
        private byte[] CompressData<T>(T data) where T : class
        {
            // Simple compression simulation - in real implementation, use GZip or similar
            var json = JsonUtility.ToJson(data);
            var bytes = System.Text.Encoding.UTF8.GetBytes(json);
            
            // Simulate compression by returning smaller array
            // In real implementation, use System.IO.Compression.GZipStream
            return bytes;
        }
        
        private T DecompressData<T>(byte[] compressedData) where T : class
        {
            // Simple decompression simulation
            var json = System.Text.Encoding.UTF8.GetString(compressedData);
            return JsonUtility.FromJson<T>(json);
        }
        
        private long GetDataSize<T>(T data) where T : class
        {
            if (data == null) return 0;
            
            // Estimate size based on JSON serialization
            try
            {
                var json = JsonUtility.ToJson(data);
                return System.Text.Encoding.UTF8.GetByteCount(json);
            }
            catch
            {
                // Fallback estimate
                return 1024; // 1KB default estimate
            }
        }
        
        #endregion
        
        #region Access Order Management (LRU)
        
        private void UpdateAccessOrder(string key)
        {
            if (_accessNodes.ContainsKey(key))
            {
                var node = _accessNodes[key];
                _accessOrder.Remove(node);
                _accessOrder.AddLast(node);
            }
        }
        
        private void AddToAccessOrder(string key)
        {
            var node = _accessOrder.AddLast(key);
            _accessNodes[key] = node;
        }
        
        private void RemoveFromAccessOrder(string key)
        {
            if (_accessNodes.ContainsKey(key))
            {
                var node = _accessNodes[key];
                _accessOrder.Remove(node);
                _accessNodes.Remove(key);
            }
        }
        
        #endregion
        
        #region Utility Methods
        
        private bool IsExpired(CacheEntry entry)
        {
            return DateTime.Now > entry.ExpiryTime;
        }
        
        private void EnsureSpace(CacheCategory category)
        {
            var categoryItems = _cache.Values.Where(e => e.Category == category.Name).Count();
            
            if (categoryItems >= category.MaxSize)
            {
                // Remove oldest item in this category
                var oldestKey = _cache.Values
                    .Where(e => e.Category == category.Name)
                    .OrderBy(e => e.LastAccessTime)
                    .First().Key;
                
                Remove(oldestKey);
            }
            
            if (_cache.Count >= _maxCacheSize)
            {
                // Remove globally oldest item
                var oldestKey = _accessOrder.First.Value;
                Remove(oldestKey);
            }
        }
        
        private void CleanupAccessPatterns()
        {
            var cutoff = DateTime.Now.AddHours(-1);
            var keysToRemove = _accessPatterns
                .Where(kvp => kvp.Value.AccessTimes.All(t => t < cutoff))
                .Select(kvp => kvp.Key)
                .ToList();
            
            foreach (var key in keysToRemove)
            {
                _accessPatterns.Remove(key);
            }
        }
        
        private void UpdateStatistics()
        {
            _statistics.HitRate = _statistics.TotalRequests > 0 ? 
                (float)_statistics.Hits / _statistics.TotalRequests : 0f;
            _statistics.CompressionRatio = CalculateCompressionRatio();
            _statistics.LastUpdated = DateTime.Now;
            
            OnStatisticsUpdated?.Invoke(_statistics);
        }
        
        private float CalculateCompressionRatio()
        {
            var compressedEntries = _cache.Values.Where(e => e.IsCompressed).ToList();
            if (!compressedEntries.Any()) return 1f;
            
            var originalSize = compressedEntries.Sum(e => e.OriginalSize);
            var compressedSize = compressedEntries.Sum(e => e.CompressedSize);
            
            return originalSize > 0 ? (float)compressedSize / originalSize : 1f;
        }
        
        #endregion
        
        #region Public API
        
        public CacheStatistics GetStatistics()
        {
            UpdateStatistics();
            return _statistics;
        }
        
        public Dictionary<string, CacheCategory> GetCategories()
        {
            return new Dictionary<string, CacheCategory>(_categories);
        }
        
        public List<CacheEntry> GetCacheEntries(string category = null)
        {
            var entries = _cache.Values.AsEnumerable();
            
            if (!string.IsNullOrEmpty(category))
            {
                entries = entries.Where(e => e.Category == category);
            }
            
            return entries.ToList();
        }
        
        public void InvalidatePattern(string pattern)
        {
            var keysToRemove = _cache.Keys.Where(k => k.Contains(pattern)).ToList();
            
            foreach (var key in keysToRemove)
            {
                Remove(key);
            }
            
            Debug.Log($"[CacheManager] Invalidated {keysToRemove.Count} entries matching pattern: {pattern}");
        }
        
        public void SetCategoryConfiguration(string category, CacheCategory config)
        {
            _categories[category] = config;
            Debug.Log($"[CacheManager] Updated configuration for category: {category}");
        }
        
        #endregion
    }
    
    #region Data Classes
    
    [Serializable]
    public class CacheEntry
    {
        public string Key;
        public object Data;
        public string Category;
        public DateTime CreatedTime;
        public DateTime LastAccessTime;
        public DateTime ExpiryTime;
        public int AccessCount;
        public bool IsCompressed;
        public long OriginalSize;
        public long CompressedSize;
    }
    
    [Serializable]
    public class CacheCategory
    {
        public string Name;
        public float DefaultTTL;
        public int MaxSize;
        public bool CompressionEnabled;
        public CachePriority Priority;
    }
    
    [Serializable]
    public class AccessPattern
    {
        public string Key;
        public List<DateTime> AccessTimes;
        public int HitCount;
        public int TotalRequests;
        public float HitRate;
        public double AverageInterval;
        public DateTime PredictedNextAccess;
    }
    
    [Serializable]
    public class CacheStatistics
    {
        public int TotalItems;
        public long TotalMemoryUsage;
        public int Hits;
        public int Misses;
        public float HitRate;
        public float CompressionRatio;
        public DateTime LastUpdated;
        
        public int TotalRequests => Hits + Misses;
    }
    
    public enum CachePriority
    {
        Low = 0,
        Medium = 1,
        High = 2,
        Critical = 3
    }
    
    #endregion
} 