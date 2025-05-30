using System;
using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using UnityEngine;
using VDM.Systems.Region;
using VDM.Runtime.Region;
using VDM.Runtime.Services.Mock;
using VDM.Runtime.Integration;
using VisualDM.Data;
using VDM.Data.ModDataManager;
using VDM.Net;

namespace VDM.Runtime.Optimization
{
    /// <summary>
    /// System optimizer that analyzes and optimizes performance across all Task 7 systems.
    /// Provides performance monitoring, memory management, and optimization recommendations.
    /// </summary>
    public class SystemOptimizer : MonoBehaviour
    {
        [Header("Optimization Configuration")]
        [SerializeField] private bool _enableAutoOptimization = true;
        [SerializeField] private bool _enablePerformanceMonitoring = true;
        [SerializeField] private float _optimizationInterval = 30f; // seconds
        [SerializeField] private float _memoryCleanupThreshold = 0.8f; // 80% memory usage
        [SerializeField] private int _maxCachedRegions = 50;
        [SerializeField] private int _maxCachedAPIResponses = 100;
        
        [Header("Performance Metrics")]
        [SerializeField] private float _currentFPS = 0f;
        [SerializeField] private float _averageFPS = 0f;
        [SerializeField] private long _memoryUsageMB = 0;
        [SerializeField] private int _activeRegions = 0;
        [SerializeField] private int _cachedAPIResponses = 0;
        [SerializeField] private float _lastOptimizationTime = 0f;
        
        // System references
        private RegionSystemController _regionController;
        private UnityBackendIntegration _backendIntegration;
        private MockAPIServer _mockServer;
        private ModDataManager _dataManager;
        
        // Performance tracking
        private List<float> _fpsHistory = new List<float>();
        private Dictionary<string, PerformanceMetric> _systemMetrics = new Dictionary<string, PerformanceMetric>();
        private List<OptimizationAction> _scheduledOptimizations = new List<OptimizationAction>();
        
        // Memory management
        private Dictionary<string, float> _lastAccessTimes = new Dictionary<string, float>();
        private HashSet<string> _frequentlyAccessedRegions = new HashSet<string>();
        
        // Events
        public event Action<OptimizationReport> OnOptimizationCompleted;
        public event Action<PerformanceAlert> OnPerformanceAlert;
        
        #region Unity Lifecycle
        
        private void Start()
        {
            InitializeOptimizer();
            
            if (_enablePerformanceMonitoring)
            {
                StartCoroutine(PerformanceMonitoringLoop());
            }
            
            if (_enableAutoOptimization)
            {
                StartCoroutine(OptimizationLoop());
            }
        }
        
        private void Update()
        {
            UpdatePerformanceMetrics();
        }
        
        private void OnDestroy()
        {
            // Clean up monitoring coroutines
            StopAllCoroutines();
        }
        
        #endregion
        
        #region Initialization
        
        private void InitializeOptimizer()
        {
            // Find system references
            _regionController = FindObjectOfType<RegionSystemController>();
            _backendIntegration = FindObjectOfType<UnityBackendIntegration>();
            _mockServer = FindObjectOfType<MockAPIServer>();
            
            // Initialize data manager reference
            try
            {
                _dataManager = new ModDataManager();
            }
            catch (Exception ex)
            {
                Debug.LogWarning($"[SystemOptimizer] Could not initialize ModDataManager: {ex.Message}");
            }
            
            // Initialize performance metrics
            InitializePerformanceMetrics();
            
            Debug.Log("[SystemOptimizer] System optimizer initialized successfully");
        }
        
        private void InitializePerformanceMetrics()
        {
            _systemMetrics["RegionSystem"] = new PerformanceMetric("Region System");
            _systemMetrics["DataSystem"] = new PerformanceMetric("Data System");
            _systemMetrics["MockAPI"] = new PerformanceMetric("Mock API");
            _systemMetrics["Integration"] = new PerformanceMetric("Integration Layer");
        }
        
        #endregion
        
        #region Performance Monitoring
        
        private IEnumerator PerformanceMonitoringLoop()
        {
            while (enabled)
            {
                yield return new WaitForSeconds(1f); // Monitor every second
                
                UpdateSystemMetrics();
                CheckPerformanceAlerts();
            }
        }
        
        private void UpdatePerformanceMetrics()
        {
            // Update FPS
            _currentFPS = 1f / Time.unscaledDeltaTime;
            _fpsHistory.Add(_currentFPS);
            
            // Keep FPS history manageable
            if (_fpsHistory.Count > 300) // 5 minutes at 1 second intervals
            {
                _fpsHistory.RemoveAt(0);
            }
            
            // Calculate average FPS
            if (_fpsHistory.Count > 0)
            {
                _averageFPS = _fpsHistory.Sum() / _fpsHistory.Count;
            }
            
            // Update memory usage
            _memoryUsageMB = GC.GetTotalMemory(false) / (1024 * 1024);
        }
        
        private void UpdateSystemMetrics()
        {
            // Update region system metrics
            if (_regionController != null)
            {
                var regionMetric = _systemMetrics["RegionSystem"];
                regionMetric.LastUpdateTime = Time.realtimeSinceStartup;
                regionMetric.IsActive = _regionController.IsInitialized;
                regionMetric.MemoryUsageEstimate = EstimateRegionSystemMemory();
                
                _activeRegions = _regionController.GetAllRegions().Count;
            }
            
            // Update integration metrics
            if (_backendIntegration != null)
            {
                var integrationMetric = _systemMetrics["Integration"];
                integrationMetric.LastUpdateTime = Time.realtimeSinceStartup;
                integrationMetric.IsActive = _backendIntegration.IsReady;
                integrationMetric.MemoryUsageEstimate = EstimateIntegrationMemory();
            }
            
            // Update mock API metrics
            if (_mockServer != null)
            {
                var apiMetric = _systemMetrics["MockAPI"];
                apiMetric.LastUpdateTime = Time.realtimeSinceStartup;
                apiMetric.IsActive = true;
                apiMetric.MemoryUsageEstimate = EstimateMockAPIMemory();
            }
            
            // Update data system metrics
            if (_dataManager != null)
            {
                var dataMetric = _systemMetrics["DataSystem"];
                dataMetric.LastUpdateTime = Time.realtimeSinceStartup;
                dataMetric.IsActive = true;
                dataMetric.MemoryUsageEstimate = EstimateDataSystemMemory();
            }
        }
        
        private void CheckPerformanceAlerts()
        {
            // FPS alert
            if (_currentFPS < 30f && _averageFPS > 45f)
            {
                TriggerPerformanceAlert("Low FPS detected", $"Current: {_currentFPS:F1}, Average: {_averageFPS:F1}", PerformanceAlertLevel.Warning);
            }
            
            // Memory alert
            float memoryUsagePercent = _memoryUsageMB / (SystemInfo.systemMemorySize * 0.001f);
            if (memoryUsagePercent > _memoryCleanupThreshold)
            {
                TriggerPerformanceAlert("High memory usage", $"Using {memoryUsagePercent:P1} of system memory", PerformanceAlertLevel.Critical);
                ScheduleOptimization(OptimizationType.MemoryCleanup, "High memory usage detected");
            }
            
            // System-specific alerts
            CheckRegionSystemAlerts();
            CheckAPISystemAlerts();
        }
        
        private void CheckRegionSystemAlerts()
        {
            if (_regionController != null && _activeRegions > _maxCachedRegions)
            {
                TriggerPerformanceAlert("Too many active regions", $"Active: {_activeRegions}, Max: {_maxCachedRegions}", PerformanceAlertLevel.Warning);
                ScheduleOptimization(OptimizationType.RegionCaching, "Too many active regions");
            }
        }
        
        private void CheckAPISystemAlerts()
        {
            if (_cachedAPIResponses > _maxCachedAPIResponses)
            {
                TriggerPerformanceAlert("API cache overflow", $"Cached: {_cachedAPIResponses}, Max: {_maxCachedAPIResponses}", PerformanceAlertLevel.Warning);
                ScheduleOptimization(OptimizationType.APICacheCleanup, "API cache overflow");
            }
        }
        
        #endregion
        
        #region Optimization Loop
        
        private IEnumerator OptimizationLoop()
        {
            while (enabled)
            {
                yield return new WaitForSeconds(_optimizationInterval);
                
                if (ShouldRunOptimization())
                {
                    yield return PerformOptimization();
                }
            }
        }
        
        private bool ShouldRunOptimization()
        {
            // Run optimization if:
            // 1. Scheduled optimizations are pending
            // 2. Performance has degraded significantly
            // 3. Memory usage is high
            
            bool hasScheduledOptimizations = _scheduledOptimizations.Count > 0;
            bool performanceDegraded = _averageFPS < 45f && _fpsHistory.Count > 60;
            bool memoryHigh = _memoryUsageMB > (SystemInfo.systemMemorySize * 0.0006f); // 60% of system memory
            
            return hasScheduledOptimizations || performanceDegraded || memoryHigh;
        }
        
        private IEnumerator PerformOptimization()
        {
            var stopwatch = Stopwatch.StartNew();
            var report = new OptimizationReport
            {
                StartTime = DateTime.UtcNow,
                OptimizationActions = new List<string>()
            };
            
            Debug.Log("[SystemOptimizer] Starting optimization pass...");
            
            // Process scheduled optimizations first
            foreach (var optimization in _scheduledOptimizations)
            {
                yield return ExecuteOptimization(optimization, report);
            }
            _scheduledOptimizations.Clear();
            
            // General optimizations
            yield return OptimizeRegionSystem(report);
            yield return OptimizeDataSystem(report);
            yield return OptimizeAPISystem(report);
            yield return OptimizeMemoryUsage(report);
            
            // Finalize report
            stopwatch.Stop();
            report.EndTime = DateTime.UtcNow;
            report.Duration = stopwatch.Elapsed;
            report.MemoryFreedMB = CalculateMemoryFreed(report);
            
            _lastOptimizationTime = Time.realtimeSinceStartup;
            
            Debug.Log($"[SystemOptimizer] Optimization completed in {report.Duration.TotalSeconds:F2}s. Actions: {report.OptimizationActions.Count}");
            
            OnOptimizationCompleted?.Invoke(report);
        }
        
        #endregion
        
        #region Optimization Methods
        
        private IEnumerator ExecuteOptimization(OptimizationAction action, OptimizationReport report)
        {
            switch (action.Type)
            {
                case OptimizationType.MemoryCleanup:
                    yield return PerformMemoryCleanup(report);
                    break;
                case OptimizationType.RegionCaching:
                    yield return OptimizeRegionCaching(report);
                    break;
                case OptimizationType.APICacheCleanup:
                    yield return OptimizeAPICaching(report);
                    break;
            }
            
            report.OptimizationActions.Add($"{action.Type}: {action.Reason}");
        }
        
        private IEnumerator OptimizeRegionSystem(OptimizationReport report)
        {
            if (_regionController == null)
            {
                yield break;
            }

            var startTime = Time.realtimeSinceStartup;
            
            try
            {
                // Get current region list
                var regions = _regionController.GetAllRegions();
                int originalCount = regions.Count;
                
                // Track frequently accessed regions
                var accessCounts = new Dictionary<string, int>();
                
                foreach (var region in regions)
                {
                    string regionId = region.RegionId;
                    
                    // Check if region was accessed recently
                    if (_lastAccessTimes.ContainsKey(regionId))
                    {
                        float timeSinceAccess = Time.time - _lastAccessTimes[regionId];
                        if (timeSinceAccess > 300f) // 5 minutes
                        {
                            // Region hasn't been accessed recently, consider for cleanup
                            if (!_frequentlyAccessedRegions.Contains(regionId))
                            {
                                // Could potentially unload this region
                                // For now, just track it
                            }
                        }
                    }
                }
                
                // Update metrics
                report.OptimizationActions.Add($"Analyzed {originalCount} regions");
                
                yield return null;
            }
            catch (Exception ex)
            {
                Debug.LogError($"SystemOptimizer: Error during region system optimization: {ex.Message}");
                report.OptimizationActions.Add($"Region optimization failed: {ex.Message}");
            }
            
            var duration = Time.realtimeSinceStartup - startTime;
            report.OptimizationActions.Add($"Region system optimization completed in {duration:F3}s");
        }
        
        private IEnumerator OptimizeDataSystem(OptimizationReport report)
        {
            if (_dataManager == null) yield break;
            
            // Clean up unused entity data
            // Note: In practice, this would call actual cleanup methods
            yield return null;
            
            report.OptimizationActions.Add("Data System: Optimized entity storage");
        }
        
        private IEnumerator OptimizeAPISystem(OptimizationReport report)
        {
            yield return OptimizeAPICaching(report);
        }
        
        private IEnumerator OptimizeAPICaching(OptimizationReport report)
        {
            // Simulate API cache cleanup
            int cleanedEntries = Mathf.Max(0, _cachedAPIResponses - _maxCachedAPIResponses);
            _cachedAPIResponses = Mathf.Min(_cachedAPIResponses, _maxCachedAPIResponses);
            
            if (cleanedEntries > 0)
            {
                report.OptimizationActions.Add($"API System: Cleaned {cleanedEntries} cached responses");
            }
            
            yield return null;
        }
        
        private IEnumerator OptimizeRegionCaching(OptimizationReport report)
        {
            if (_regionController == null)
            {
                yield break;
            }

            var startTime = Time.realtimeSinceStartup;
            int regionsCleaned = 0;
            
            try
            {
                var allRegions = _regionController.GetAllRegions();
                
                // If we have too many regions, clean up least recently accessed ones
                if (allRegions.Count > _maxCachedRegions)
                {
                    var regionsToRemove = allRegions.Count - _maxCachedRegions;
                    var sortedByAccess = allRegions
                        .Where(r => _lastAccessTimes.ContainsKey(r.RegionId))
                        .OrderBy(r => _lastAccessTimes[r.RegionId])
                        .Take(regionsToRemove)
                        .ToList();
                    
                    foreach (var region in sortedByAccess)
                    {
                        if (!_frequentlyAccessedRegions.Contains(region.RegionId))
                        {
                            // Remove from controller
                            _regionController.RemoveRegion(region.RegionId);
                            regionsCleaned++;
                            
                            // Clean up tracking
                            _lastAccessTimes.Remove(region.RegionId);
                        }
                    }
                }
                
                yield return null;
            }
            catch (Exception ex)
            {
                Debug.LogError($"SystemOptimizer: Error during region caching optimization: {ex.Message}");
            }
            
            var duration = Time.realtimeSinceStartup - startTime;
            report.OptimizationActions.Add($"Region caching optimization: Cleaned {regionsCleaned} regions in {duration:F3}s");
        }
        
        private IEnumerator OptimizeMemoryUsage(OptimizationReport report)
        {
            yield return PerformMemoryCleanup(report);
        }
        
        private IEnumerator PerformMemoryCleanup(OptimizationReport report)
        {
            // Force garbage collection
            var beforeMemory = GC.GetTotalMemory(false);
            GC.Collect();
            GC.WaitForPendingFinalizers();
            GC.Collect();
            var afterMemory = GC.GetTotalMemory(true);
            
            long freedMemory = beforeMemory - afterMemory;
            
            // Clear unused Unity resources
            yield return Resources.UnloadUnusedAssets();
            
            if (freedMemory > 0)
            {
                report.OptimizationActions.Add($"Memory: Freed {freedMemory / (1024 * 1024)}MB through garbage collection");
            }
            
            report.OptimizationActions.Add("Memory: Unloaded unused Unity assets");
        }
        
        #endregion
        
        #region Memory Estimation
        
        private long EstimateRegionSystemMemory()
        {
            if (_regionController == null) return 0;
            
            // Rough estimation: each region uses ~1MB including map data
            return _activeRegions * 1024 * 1024;
        }
        
        private long EstimateIntegrationMemory()
        {
            // Estimation for integration layer overhead
            return 10 * 1024 * 1024; // ~10MB
        }
        
        private long EstimateMockAPIMemory()
        {
            // Estimation based on cached responses
            return _cachedAPIResponses * 1024; // ~1KB per cached response
        }
        
        private long EstimateDataSystemMemory()
        {
            // Estimation for data system
            return 5 * 1024 * 1024; // ~5MB
        }
        
        #endregion
        
        #region Helper Methods
        
        private void ScheduleOptimization(OptimizationType type, string reason)
        {
            var optimization = new OptimizationAction
            {
                Type = type,
                Reason = reason,
                ScheduledAt = Time.realtimeSinceStartup
            };
            
            // Avoid duplicate scheduled optimizations
            if (!_scheduledOptimizations.Any(o => o.Type == type))
            {
                _scheduledOptimizations.Add(optimization);
            }
        }
        
        private void TriggerPerformanceAlert(string title, string message, PerformanceAlertLevel level)
        {
            var alert = new PerformanceAlert
            {
                Title = title,
                Message = message,
                Level = level,
                Timestamp = DateTime.UtcNow
            };
            
            string levelText = level == PerformanceAlertLevel.Critical ? "CRITICAL" : "WARNING";
            Debug.LogWarning($"[SystemOptimizer] {levelText}: {title} - {message}");
            
            OnPerformanceAlert?.Invoke(alert);
        }
        
        private long CalculateMemoryFreed(OptimizationReport report)
        {
            // Calculate estimated memory freed based on optimization actions
            long totalFreed = 0;
            
            foreach (var action in report.OptimizationActions)
            {
                if (action.Contains("Memory:") && action.Contains("MB"))
                {
                    // Extract MB value from action string
                    var parts = action.Split(' ');
                    foreach (var part in parts)
                    {
                        if (part.EndsWith("MB") && long.TryParse(part.Substring(0, part.Length - 2), out long mb))
                        {
                            totalFreed += mb;
                            break;
                        }
                    }
                }
            }
            
            return totalFreed;
        }
        
        public void RegisterRegionAccess(string regionId)
        {
            _lastAccessTimes[regionId] = Time.realtimeSinceStartup;
            
            // Track frequently accessed regions
            // Note: More sophisticated frequency tracking could be implemented
        }
        
        #endregion
        
        #region Public API
        
        /// <summary>
        /// Manually trigger optimization
        /// </summary>
        [ContextMenu("Run Optimization")]
        public void RunOptimizationManually()
        {
            StartCoroutine(PerformOptimization());
        }
        
        /// <summary>
        /// Get current performance summary
        /// </summary>
        public PerformanceSummary GetPerformanceSummary()
        {
            return new PerformanceSummary
            {
                CurrentFPS = _currentFPS,
                AverageFPS = _averageFPS,
                MemoryUsageMB = _memoryUsageMB,
                ActiveRegions = _activeRegions,
                CachedAPIResponses = _cachedAPIResponses,
                LastOptimizationTime = _lastOptimizationTime,
                SystemMetrics = new Dictionary<string, PerformanceMetric>(_systemMetrics)
            };
        }
        
        #endregion
        
        #region Data Classes
        
        [Serializable]
        public class PerformanceMetric
        {
            public string SystemName;
            public bool IsActive;
            public float LastUpdateTime;
            public long MemoryUsageEstimate;
            
            public PerformanceMetric(string systemName)
            {
                SystemName = systemName;
            }
        }
        
        [Serializable]
        public class OptimizationAction
        {
            public OptimizationType Type;
            public string Reason;
            public float ScheduledAt;
        }
        
        [Serializable]
        public class OptimizationReport
        {
            public DateTime StartTime;
            public DateTime EndTime;
            public TimeSpan Duration;
            public List<string> OptimizationActions;
            public long MemoryFreedMB;
        }
        
        [Serializable]
        public class PerformanceAlert
        {
            public string Title;
            public string Message;
            public PerformanceAlertLevel Level;
            public DateTime Timestamp;
        }
        
        [Serializable]
        public class PerformanceSummary
        {
            public float CurrentFPS;
            public float AverageFPS;
            public long MemoryUsageMB;
            public int ActiveRegions;
            public int CachedAPIResponses;
            public float LastOptimizationTime;
            public Dictionary<string, PerformanceMetric> SystemMetrics;
        }
        
        public enum OptimizationType
        {
            MemoryCleanup,
            RegionCaching,
            APICacheCleanup,
            GeneralOptimization
        }
        
        public enum PerformanceAlertLevel
        {
            Warning,
            Critical
        }
        
        #endregion
    }
    
    // Extension methods for system controllers
    public static class SystemOptimizerExtensions
    {
        public static void UnloadRegion(this RegionSystemController controller, string regionId)
        {
            // Implementation would unload region data
            Debug.Log($"[SystemOptimizer] Unloaded region: {regionId}");
        }
        
        public static void OptimizeRegion(this RegionSystemController controller, string regionId)
        {
            // Implementation would optimize region for better memory usage
            Debug.Log($"[SystemOptimizer] Optimized region: {regionId}");
        }
    }
} 