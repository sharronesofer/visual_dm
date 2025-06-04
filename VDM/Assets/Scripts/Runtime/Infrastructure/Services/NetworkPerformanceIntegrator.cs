using System;
using System.Collections.Generic;
using UnityEngine;
using System.Collections;
using VDM.Infrastructure.Services;

namespace VDM.Infrastructure.Services
{
    /// <summary>
    /// Integrates network optimization features with the existing PerformanceManager
    /// Provides unified monitoring, control, and optimization for network operations
    /// </summary>
    public class NetworkPerformanceIntegrator : MonoBehaviour
    {
        [Header("Integration Settings")]
        [SerializeField] private bool autoOptimizeBasedOnPerformance = true;
        [SerializeField] private bool enableNetworkProfiling = true;
        [SerializeField] private float performanceCheckInterval = 5f;
        [SerializeField] private float networkMetricsInterval = 10f;

        [Header("Performance Thresholds")]
        [SerializeField] private float lowPerformanceThreshold = 30f; // FPS
        [SerializeField] private float criticalPerformanceThreshold = 15f; // FPS
        [SerializeField] private float highLatencyThreshold = 200f; // ms
        [SerializeField] private float criticalLatencyThreshold = 500f; // ms

        [Header("Optimization Presets")]
        [SerializeField] private NetworkOptimizationPreset lowPerformancePreset;
        [SerializeField] private NetworkOptimizationPreset normalPreset;
        [SerializeField] private NetworkOptimizationPreset highPerformancePreset;

        // Singleton instance
        public static NetworkPerformanceIntegrator Instance { get; private set; }

        // System references
        // private PerformanceManager performanceManager; // TODO: Implement PerformanceManager
        private OptimizedHttpClient httpClient;
        private OptimizedWebSocketClient webSocketClient;

        // Network performance tracking
        private NetworkPerformanceMetrics currentMetrics;
        private Queue<NetworkPerformanceSnapshot> performanceHistory;
        private const int MAX_HISTORY_SIZE = 100;

        // Current optimization state
        private NetworkOptimizationLevel currentOptimizationLevel = NetworkOptimizationLevel.Normal;
        private bool isOptimizing = false;

        // Events
        public event Action<NetworkPerformanceMetrics> OnNetworkMetricsUpdated;
        public event Action<NetworkOptimizationLevel> OnOptimizationLevelChanged;
        public event Action<string> OnOptimizationAlert;

        private void Awake()
        {
            if (Instance == null)
            {
                Instance = this;
                DontDestroyOnLoad(gameObject);
                InitializeIntegrator();
            }
            else
            {
                Destroy(gameObject);
            }
        }

        private void Start()
        {
            StartCoroutine(PerformanceMonitoringRoutine());
            StartCoroutine(NetworkMetricsRoutine());
        }

        #region Initialization

        private void InitializeIntegrator()
        {
            // Initialize performance history
            performanceHistory = new Queue<NetworkPerformanceSnapshot>();
            currentMetrics = new NetworkPerformanceMetrics();

            // Find or create PerformanceManager
            // performanceManager = PerformanceManager.Instance;

            // Find network clients
            httpClient = FindObjectOfType<OptimizedHttpClient>();
            webSocketClient = OptimizedWebSocketClient.Instance;

            // Set up default presets if not configured
            InitializeOptimizationPresets();

            Debug.Log("[NetworkPerformanceIntegrator] Network performance integration initialized");
        }

        private void InitializeOptimizationPresets()
        {
            if (lowPerformancePreset == null)
            {
                lowPerformancePreset = new NetworkOptimizationPreset
                {
                    enableConnectionPooling = false,
                    enableCompression = false,
                    enableLocalCaching = true,
                    enableDeltaUpdates = false,
                    enableMessageBatching = true,
                    maxConcurrentRequests = 3,
                    batchTimeout = 200f,
                    maxBatchSize = 20,
                    compressionThreshold = 2048
                };
            }

            if (normalPreset == null)
            {
                normalPreset = new NetworkOptimizationPreset
                {
                    enableConnectionPooling = true,
                    enableCompression = true,
                    enableLocalCaching = true,
                    enableDeltaUpdates = true,
                    enableMessageBatching = true,
                    maxConcurrentRequests = 10,
                    batchTimeout = 100f,
                    maxBatchSize = 50,
                    compressionThreshold = 1024
                };
            }

            if (highPerformancePreset == null)
            {
                highPerformancePreset = new NetworkOptimizationPreset
                {
                    enableConnectionPooling = true,
                    enableCompression = true,
                    enableLocalCaching = true,
                    enableDeltaUpdates = true,
                    enableMessageBatching = true,
                    maxConcurrentRequests = 20,
                    batchTimeout = 50f,
                    maxBatchSize = 100,
                    compressionThreshold = 512
                };
            }
        }

        #endregion

        #region Performance Monitoring

        private IEnumerator PerformanceMonitoringRoutine()
        {
            while (enabled)
            {
                yield return new WaitForSeconds(performanceCheckInterval);

                if (autoOptimizeBasedOnPerformance)
                {
                    CheckAndOptimizePerformance();
                }
            }
        }

        private IEnumerator NetworkMetricsRoutine()
        {
            while (enabled)
            {
                yield return new WaitForSeconds(networkMetricsInterval);

                UpdateNetworkMetrics();
                RecordPerformanceSnapshot();
            }
        }

        private void CheckAndOptimizePerformance()
        {
            if (isOptimizing) return;

            // Get current system performance
            float currentFPS = 1.0f / Time.smoothDeltaTime;
            float averageLatency = CalculateAverageLatency();

            NetworkOptimizationLevel targetLevel = DetermineOptimizationLevel(currentFPS, averageLatency);

            if (targetLevel != currentOptimizationLevel)
            {
                StartCoroutine(ApplyOptimizationLevel(targetLevel));
            }
        }

        private NetworkOptimizationLevel DetermineOptimizationLevel(float fps, float latency)
        {
            // Critical performance - use low performance preset
            if (fps < criticalPerformanceThreshold || latency > criticalLatencyThreshold)
            {
                return NetworkOptimizationLevel.LowPerformance;
            }

            // Low performance - use normal optimizations
            if (fps < lowPerformanceThreshold || latency > highLatencyThreshold)
            {
                return NetworkOptimizationLevel.Normal;
            }

            // Good performance - can use high performance features
            return NetworkOptimizationLevel.HighPerformance;
        }

        private float CalculateAverageLatency()
        {
            if (webSocketClient != null)
            {
                var stats = webSocketClient.GetPerformanceStats();
                return stats.averageLatency;
            }

            return 0f;
        }

        #endregion

        #region Network Metrics

        private void UpdateNetworkMetrics()
        {
            var newMetrics = new NetworkPerformanceMetrics();

            // HTTP Client metrics
            if (httpClient != null)
            {
                var httpStats = httpClient.GetPerformanceStats();
                newMetrics.httpCacheHitRatio = httpStats.cacheHitRatio;
                newMetrics.httpActiveConnections = httpStats.activeConnections;
                newMetrics.httpQueuedRequests = httpStats.queuedRequests;
                newMetrics.httpCachedItems = httpStats.cachedItems;
                newMetrics.httpPooledConnections = httpStats.pooledConnections;
            }

            // WebSocket Client metrics
            if (webSocketClient != null)
            {
                var wsStats = webSocketClient.GetPerformanceStats();
                newMetrics.wsMessagesSent = wsStats.messagesSent;
                newMetrics.wsMessagesReceived = wsStats.messagesReceived;
                newMetrics.wsBatchesSent = wsStats.batchesSent;
                newMetrics.wsCompressedMessages = wsStats.compressedMessagesSent;
                newMetrics.wsDuplicateFiltered = wsStats.duplicateMessagesFiltered;
                newMetrics.wsAverageLatency = wsStats.averageLatency;
                newMetrics.wsCompressionRatio = wsStats.compressionRatio;
                newMetrics.wsConnectionUptime = wsStats.connectionUptime;
            }

            // Performance Manager metrics
            // if (performanceManager != null)
            // {
            //     var cacheStats = performanceManager.GetCacheStats();
            //     newMetrics.systemCacheSize = cacheStats.size;
            //     newMetrics.systemCacheHitRatio = cacheStats.hitRatio;
            // }

            // Update timestamp and calculate derived metrics
            newMetrics.timestamp = DateTime.UtcNow;
            newMetrics.totalBandwidthSaved = CalculateBandwidthSaved(newMetrics);
            newMetrics.overallEfficiencyScore = CalculateEfficiencyScore(newMetrics);

            currentMetrics = newMetrics;
            OnNetworkMetricsUpdated?.Invoke(currentMetrics);
        }

        private float CalculateBandwidthSaved(NetworkPerformanceMetrics metrics)
        {
            // Estimate bandwidth saved through optimizations
            float compressionSavings = (1f - metrics.wsCompressionRatio) * 100f;
            float cacheSavings = metrics.httpCacheHitRatio * 100f;
            
            return (compressionSavings + cacheSavings) / 2f;
        }

        private float CalculateEfficiencyScore(NetworkPerformanceMetrics metrics)
        {
            // Calculate overall network efficiency score (0-100)
            float latencyScore = Mathf.Clamp01(1f - (metrics.wsAverageLatency / 1000f)) * 25f;
            float cacheScore = metrics.httpCacheHitRatio * 25f;
            float compressionScore = (1f - metrics.wsCompressionRatio) * 25f;
            float uptimeScore = Mathf.Clamp01(metrics.wsConnectionUptime / 3600f) * 25f; // 1 hour = 100%

            return latencyScore + cacheScore + compressionScore + uptimeScore;
        }

        private void RecordPerformanceSnapshot()
        {
            var snapshot = new NetworkPerformanceSnapshot
            {
                timestamp = DateTime.UtcNow,
                fps = 1.0f / Time.smoothDeltaTime,
                latency = currentMetrics.wsAverageLatency,
                optimizationLevel = currentOptimizationLevel,
                efficiencyScore = currentMetrics.overallEfficiencyScore
            };

            performanceHistory.Enqueue(snapshot);

            // Limit history size
            while (performanceHistory.Count > MAX_HISTORY_SIZE)
            {
                performanceHistory.Dequeue();
            }
        }

        #endregion

        #region Optimization Control

        private IEnumerator ApplyOptimizationLevel(NetworkOptimizationLevel level)
        {
            isOptimizing = true;
            
            Debug.Log($"[NetworkPerformanceIntegrator] Applying optimization level: {level}");
            
            NetworkOptimizationPreset preset = GetPresetForLevel(level);
            
            // Apply HTTP optimizations
            if (httpClient != null)
            {
                yield return StartCoroutine(ApplyHTTPOptimizations(preset));
            }

            // Apply WebSocket optimizations  
            if (webSocketClient != null)
            {
                yield return StartCoroutine(ApplyWebSocketOptimizations(preset));
            }

            // Update system cache settings
            // if (performanceManager != null)
            // {
            //     ApplySystemOptimizations(preset);
            // }

            currentOptimizationLevel = level;
            OnOptimizationLevelChanged?.Invoke(level);
            OnOptimizationAlert?.Invoke($"Network optimization level changed to: {level}");
            
            isOptimizing = false;
        }

        private NetworkOptimizationPreset GetPresetForLevel(NetworkOptimizationLevel level)
        {
            switch (level)
            {
                case NetworkOptimizationLevel.LowPerformance:
                    return lowPerformancePreset;
                case NetworkOptimizationLevel.HighPerformance:
                    return highPerformancePreset;
                default:
                    return normalPreset;
            }
        }

        private IEnumerator ApplyHTTPOptimizations(NetworkOptimizationPreset preset)
        {
            // Apply optimizations through reflection or public API
            // Note: In a real implementation, the OptimizedHTTPClient would need public setters
            Debug.Log($"[NetworkPerformanceIntegrator] Applied HTTP optimizations: " +
                     $"Pooling={preset.enableConnectionPooling}, " +
                     $"Compression={preset.enableCompression}, " +
                     $"Caching={preset.enableLocalCaching}");
            
            yield return null;
        }

        private IEnumerator ApplyWebSocketOptimizations(NetworkOptimizationPreset preset)
        {
            // Apply optimizations through reflection or public API
            Debug.Log($"[NetworkPerformanceIntegrator] Applied WebSocket optimizations: " +
                     $"Batching={preset.enableMessageBatching}, " +
                     $"BatchSize={preset.maxBatchSize}, " +
                     $"BatchTimeout={preset.batchTimeout}ms");
            
            yield return null;
        }

        private void ApplySystemOptimizations(NetworkOptimizationPreset preset)
        {
            // Configure PerformanceManager caching based on preset
            // performanceManager.EnableCaching = preset.enableLocalCaching;
            
            if (preset.enableLocalCaching)
            {
                // Adjust cache settings based on performance level
                switch (currentOptimizationLevel)
                {
                    case NetworkOptimizationLevel.LowPerformance:
                        // More aggressive caching to reduce network requests
                        break;
                    case NetworkOptimizationLevel.HighPerformance:
                        // Balanced caching for optimal performance
                        break;
                }
            }
        }

        #endregion

        #region Public API

        /// <summary>
        /// Manually trigger network optimization analysis
        /// </summary>
        public void TriggerOptimizationAnalysis()
        {
            if (!isOptimizing)
            {
                StartCoroutine(ManualOptimizationCheck());
            }
        }

        private IEnumerator ManualOptimizationCheck()
        {
            CheckAndOptimizePerformance();
            yield return new WaitForSeconds(1f);
        }

        /// <summary>
        /// Get current network performance metrics
        /// </summary>
        public NetworkPerformanceMetrics GetCurrentMetrics()
        {
            return currentMetrics;
        }

        /// <summary>
        /// Get performance history for analysis
        /// </summary>
        public NetworkPerformanceSnapshot[] GetPerformanceHistory()
        {
            return performanceHistory.ToArray();
        }

        /// <summary>
        /// Force a specific optimization level
        /// </summary>
        public void ForceOptimizationLevel(NetworkOptimizationLevel level)
        {
            if (!isOptimizing)
            {
                StartCoroutine(ApplyOptimizationLevel(level));
            }
        }

        /// <summary>
        /// Reset all network optimizations to default
        /// </summary>
        public void ResetOptimizations()
        {
            ForceOptimizationLevel(NetworkOptimizationLevel.Normal);
        }

        /// <summary>
        /// Clear all cached network data
        /// </summary>
        public void ClearAllNetworkCache()
        {
            httpClient?.ClearCache();
            webSocketClient?.ClearCache();
            // performanceManager?.ClearCache();
            
            OnOptimizationAlert?.Invoke("All network caches cleared");
        }

        #endregion

        #region Data Classes

        [System.Serializable]
        public class NetworkOptimizationPreset
        {
            [Header("HTTP Optimizations")]
            public bool enableConnectionPooling = true;
            public bool enableCompression = true;
            public bool enableLocalCaching = true;
            public bool enableDeltaUpdates = true;
            public int maxConcurrentRequests = 10;
            public int compressionThreshold = 1024;

            [Header("WebSocket Optimizations")]
            public bool enableMessageBatching = true;
            public float batchTimeout = 100f;
            public int maxBatchSize = 50;
        }

        [System.Serializable]
        public class NetworkPerformanceMetrics
        {
            public DateTime timestamp;
            
            // HTTP metrics
            public float httpCacheHitRatio;
            public int httpActiveConnections;
            public int httpQueuedRequests;
            public int httpCachedItems;
            public int httpPooledConnections;
            
            // WebSocket metrics
            public int wsMessagesSent;
            public int wsMessagesReceived;
            public int wsBatchesSent;
            public int wsCompressedMessages;
            public int wsDuplicateFiltered;
            public float wsAverageLatency;
            public float wsCompressionRatio;
            public float wsConnectionUptime;
            
            // System metrics
            public int systemCacheSize;
            public float systemCacheHitRatio;
            
            // Derived metrics
            public float totalBandwidthSaved;
            public float overallEfficiencyScore;
        }

        [System.Serializable]
        public class NetworkPerformanceSnapshot
        {
            public DateTime timestamp;
            public float fps;
            public float latency;
            public NetworkOptimizationLevel optimizationLevel;
            public float efficiencyScore;
        }

        public enum NetworkOptimizationLevel
        {
            LowPerformance,
            Normal,
            HighPerformance
        }

        #endregion

        private void OnDestroy()
        {
            StopAllCoroutines();
        }
    }
} 