using System;
using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using UnityEngine;
using UnityEngine.Profiling;
using Debug = UnityEngine.Debug;

namespace VDM.Runtime.Core.Services
{
    /// <summary>
    /// Comprehensive performance monitoring service for all VDM systems.
    /// Tracks FPS, memory usage, API performance, and system health in real-time.
    /// </summary>
    public class PerformanceMonitor : MonoBehaviour
    {
        [Header("Monitoring Configuration")]
        [SerializeField] private bool _enableMonitoring = true;
        [SerializeField] private float _monitoringInterval = 1f; // seconds
        [SerializeField] private int _maxHistorySize = 300; // 5 minutes at 1Hz
        [SerializeField] private bool _enableDetailedMemoryTracking = true;
        [SerializeField] private bool _enableAPIPerformanceTracking = true;
        
        [Header("Performance Thresholds")]
        [SerializeField] private float _lowFPSThreshold = 30f;
        [SerializeField] private float _criticalFPSThreshold = 15f;
        [SerializeField] private long _highMemoryThresholdMB = 1024; // 1GB
        [SerializeField] private long _criticalMemoryThresholdMB = 2048; // 2GB
        [SerializeField] private float _highAPIResponseTimeMs = 500f;
        [SerializeField] private float _criticalAPIResponseTimeMs = 2000f;
        
        // Performance metrics
        private PerformanceMetrics _currentMetrics = new PerformanceMetrics();
        private List<PerformanceSnapshot> _performanceHistory = new List<PerformanceSnapshot>();
        private Dictionary<string, SystemPerformance> _systemPerformance = new Dictionary<string, SystemPerformance>();
        private Dictionary<string, APICallMetrics> _apiMetrics = new Dictionary<string, APICallMetrics>();
        
        // FPS tracking
        private float _fpsUpdateInterval = 0.5f;
        private float _nextFPSUpdate = 0f;
        private int _frameCount = 0;
        
        // Memory tracking
        private Stopwatch _memoryTrackingStopwatch = new Stopwatch();
        private Dictionary<string, long> _systemMemoryUsage = new Dictionary<string, long>();
        
        // Events
        public event Action<PerformanceAlert> OnPerformanceAlert;
        public event Action<PerformanceMetrics> OnMetricsUpdated;
        public event Action<string, APICallMetrics> OnAPICallCompleted;
        
        #region Unity Lifecycle
        
        private void Awake()
        {
            if (_enableMonitoring)
            {
                InitializeMonitoring();
            }
        }
        
        private void Start()
        {
            if (_enableMonitoring)
            {
                StartCoroutine(MonitoringLoop());
                _memoryTrackingStopwatch.Start();
            }
        }
        
        private void Update()
        {
            if (_enableMonitoring)
            {
                UpdateFPSTracking();
            }
        }
        
        private void OnDestroy()
        {
            StopAllCoroutines();
            _memoryTrackingStopwatch?.Stop();
        }
        
        #endregion
        
        #region Initialization
        
        private void InitializeMonitoring()
        {
            // Initialize system performance tracking for all VDM systems
            var systemNames = new[]
            {
                "Analytics", "Arc", "AuthUser", "Character", "Combat", "Crafting",
                "Data", "Dialogue", "Diplomacy", "Economy", "Equipment", "Events",
                "Faction", "Inventory", "Llm", "Loot", "Magic", "Memory", "Motif",
                "Npc", "Poi", "Population", "Quest", "Region", "Religion", "Rumor",
                "Storage", "Time", "WorldGeneration", "WorldState", "UI", "Core", "Services"
            };
            
            foreach (var systemName in systemNames)
            {
                _systemPerformance[systemName] = new SystemPerformance
                {
                    SystemName = systemName,
                    IsActive = false,
                    MemoryUsageHistory = new List<long>(),
                    ProcessingTimeHistory = new List<float>(),
                    ErrorCount = 0,
                    LastActivity = DateTime.Now
                };
            }
            
            Debug.Log("[PerformanceMonitor] Initialized monitoring for all VDM systems");
        }
        
        #endregion
        
        #region Core Monitoring
        
        private IEnumerator MonitoringLoop()
        {
            while (_enableMonitoring)
            {
                yield return new WaitForSeconds(_monitoringInterval);
                
                try
                {
                    UpdatePerformanceMetrics();
                    CheckPerformanceAlerts();
                    CleanupHistory();
                }
                catch (Exception ex)
                {
                    Debug.LogError($"[PerformanceMonitor] Error in monitoring loop: {ex.Message}");
                }
            }
        }
        
        private void UpdatePerformanceMetrics()
        {
            // Update current metrics
            _currentMetrics.Timestamp = DateTime.Now;
            _currentMetrics.FPS = 1f / Time.deltaTime;
            _currentMetrics.MemoryUsageMB = Profiler.GetTotalAllocatedMemory(false) / (1024 * 1024);
            _currentMetrics.SystemCount = _systemPerformance.Count(s => s.Value.IsActive);
            _currentMetrics.TotalAPIRequests = _apiMetrics.Values.Sum(a => a.TotalCalls);
            _currentMetrics.AverageAPIResponseTime = _apiMetrics.Values.Any() 
                ? _apiMetrics.Values.Average(a => a.AverageResponseTime) : 0f;
            
            // Update Unity-specific metrics
            _currentMetrics.GameObjectCount = FindObjectsOfType<GameObject>().Length;
            _currentMetrics.MonoBehaviourCount = FindObjectsOfType<MonoBehaviour>().Length;
            _currentMetrics.ActiveCameraCount = Camera.allCameras.Length;
            
            // Store snapshot
            var snapshot = new PerformanceSnapshot
            {
                Timestamp = _currentMetrics.Timestamp,
                FPS = _currentMetrics.FPS,
                MemoryUsageMB = _currentMetrics.MemoryUsageMB,
                SystemCount = _currentMetrics.SystemCount,
                GameObjectCount = _currentMetrics.GameObjectCount
            };
            
            _performanceHistory.Add(snapshot);
            
            // Notify listeners
            OnMetricsUpdated?.Invoke(_currentMetrics);
        }
        
        private void UpdateFPSTracking()
        {
            _frameCount++;
            
            if (Time.time >= _nextFPSUpdate)
            {
                _currentMetrics.FPS = _frameCount / _fpsUpdateInterval;
                _frameCount = 0;
                _nextFPSUpdate = Time.time + _fpsUpdateInterval;
            }
        }
        
        #endregion
        
        #region System Performance Tracking
        
        public void TrackSystemActivity(string systemName, float processingTime, long memoryDelta = 0)
        {
            if (!_systemPerformance.ContainsKey(systemName))
            {
                _systemPerformance[systemName] = new SystemPerformance
                {
                    SystemName = systemName,
                    IsActive = true,
                    MemoryUsageHistory = new List<long>(),
                    ProcessingTimeHistory = new List<float>(),
                    ErrorCount = 0,
                    LastActivity = DateTime.Now
                };
            }
            
            var system = _systemPerformance[systemName];
            system.IsActive = true;
            system.LastActivity = DateTime.Now;
            system.ProcessingTimeHistory.Add(processingTime);
            
            if (memoryDelta != 0)
            {
                var currentMemory = system.MemoryUsageHistory.LastOrDefault() + memoryDelta;
                system.MemoryUsageHistory.Add(currentMemory);
            }
            
            // Keep only recent history
            if (system.ProcessingTimeHistory.Count > _maxHistorySize)
            {
                system.ProcessingTimeHistory.RemoveAt(0);
            }
            
            if (system.MemoryUsageHistory.Count > _maxHistorySize)
            {
                system.MemoryUsageHistory.RemoveAt(0);
            }
        }
        
        public void TrackSystemError(string systemName, string errorMessage)
        {
            if (_systemPerformance.ContainsKey(systemName))
            {
                _systemPerformance[systemName].ErrorCount++;
                _systemPerformance[systemName].LastError = errorMessage;
                _systemPerformance[systemName].LastErrorTime = DateTime.Now;
                
                TriggerAlert($"System Error in {systemName}", errorMessage, AlertLevel.Warning);
            }
        }
        
        #endregion
        
        #region API Performance Tracking
        
        public void TrackAPICall(string endpoint, float responseTime, bool success = true)
        {
            if (!_enableAPIPerformanceTracking) return;
            
            if (!_apiMetrics.ContainsKey(endpoint))
            {
                _apiMetrics[endpoint] = new APICallMetrics
                {
                    Endpoint = endpoint,
                    TotalCalls = 0,
                    SuccessfulCalls = 0,
                    AverageResponseTime = 0f,
                    ResponseTimeHistory = new List<float>()
                };
            }
            
            var metrics = _apiMetrics[endpoint];
            metrics.TotalCalls++;
            
            if (success)
            {
                metrics.SuccessfulCalls++;
            }
            
            metrics.ResponseTimeHistory.Add(responseTime);
            metrics.AverageResponseTime = metrics.ResponseTimeHistory.Average();
            metrics.LastCallTime = DateTime.Now;
            
            // Keep only recent history
            if (metrics.ResponseTimeHistory.Count > _maxHistorySize)
            {
                metrics.ResponseTimeHistory.RemoveAt(0);
            }
            
            // Check for performance issues
            if (responseTime > _criticalAPIResponseTimeMs)
            {
                TriggerAlert($"Critical API Performance", 
                    $"API call to {endpoint} took {responseTime:F2}ms", AlertLevel.Critical);
            }
            else if (responseTime > _highAPIResponseTimeMs)
            {
                TriggerAlert($"High API Response Time", 
                    $"API call to {endpoint} took {responseTime:F2}ms", AlertLevel.Warning);
            }
            
            OnAPICallCompleted?.Invoke(endpoint, metrics);
        }
        
        #endregion
        
        #region Memory Monitoring
        
        public void TrackMemoryUsage(string source, long memoryUsage)
        {
            if (!_enableDetailedMemoryTracking) return;
            
            _systemMemoryUsage[source] = memoryUsage;
            
            var totalMemory = _systemMemoryUsage.Values.Sum();
            if (totalMemory > _criticalMemoryThresholdMB * 1024 * 1024)
            {
                TriggerAlert("Critical Memory Usage", 
                    $"Total memory usage: {totalMemory / (1024 * 1024):F2}MB", AlertLevel.Critical);
            }
            else if (totalMemory > _highMemoryThresholdMB * 1024 * 1024)
            {
                TriggerAlert("High Memory Usage", 
                    $"Total memory usage: {totalMemory / (1024 * 1024):F2}MB", AlertLevel.Warning);
            }
        }
        
        public Dictionary<string, long> GetMemoryBreakdown()
        {
            return new Dictionary<string, long>(_systemMemoryUsage);
        }
        
        #endregion
        
        #region Alert System
        
        private void CheckPerformanceAlerts()
        {
            // FPS alerts
            if (_currentMetrics.FPS < _criticalFPSThreshold)
            {
                TriggerAlert("Critical FPS", $"FPS dropped to {_currentMetrics.FPS:F1}", AlertLevel.Critical);
            }
            else if (_currentMetrics.FPS < _lowFPSThreshold)
            {
                TriggerAlert("Low FPS", $"FPS is {_currentMetrics.FPS:F1}", AlertLevel.Warning);
            }
            
            // Memory alerts
            if (_currentMetrics.MemoryUsageMB > _criticalMemoryThresholdMB)
            {
                TriggerAlert("Critical Memory Usage", 
                    $"Memory usage: {_currentMetrics.MemoryUsageMB}MB", AlertLevel.Critical);
            }
            else if (_currentMetrics.MemoryUsageMB > _highMemoryThresholdMB)
            {
                TriggerAlert("High Memory Usage", 
                    $"Memory usage: {_currentMetrics.MemoryUsageMB}MB", AlertLevel.Warning);
            }
        }
        
        private void TriggerAlert(string title, string message, AlertLevel level)
        {
            var alert = new PerformanceAlert
            {
                Title = title,
                Message = message,
                Level = level,
                Timestamp = DateTime.Now,
                SystemSource = "PerformanceMonitor"
            };
            
            string levelText = level == AlertLevel.Critical ? "CRITICAL" : "WARNING";
            Debug.Log($"[PerformanceMonitor] {levelText}: {title} - {message}");
            
            OnPerformanceAlert?.Invoke(alert);
        }
        
        #endregion
        
        #region Public API
        
        public PerformanceMetrics GetCurrentMetrics()
        {
            return _currentMetrics;
        }
        
        public List<PerformanceSnapshot> GetPerformanceHistory(int maxItems = 100)
        {
            return _performanceHistory.TakeLast(maxItems).ToList();
        }
        
        public SystemPerformance GetSystemPerformance(string systemName)
        {
            return _systemPerformance.ContainsKey(systemName) ? _systemPerformance[systemName] : null;
        }
        
        public Dictionary<string, SystemPerformance> GetAllSystemPerformance()
        {
            return new Dictionary<string, SystemPerformance>(_systemPerformance);
        }
        
        public Dictionary<string, APICallMetrics> GetAPIMetrics()
        {
            return new Dictionary<string, APICallMetrics>(_apiMetrics);
        }
        
        public void ResetMetrics()
        {
            _performanceHistory.Clear();
            foreach (var system in _systemPerformance.Values)
            {
                system.MemoryUsageHistory.Clear();
                system.ProcessingTimeHistory.Clear();
                system.ErrorCount = 0;
            }
            foreach (var api in _apiMetrics.Values)
            {
                api.ResponseTimeHistory.Clear();
                api.TotalCalls = 0;
                api.SuccessfulCalls = 0;
            }
            
            Debug.Log("[PerformanceMonitor] Performance metrics reset");
        }
        
        #endregion
        
        #region Cleanup
        
        private void CleanupHistory()
        {
            // Clean up performance history
            while (_performanceHistory.Count > _maxHistorySize)
            {
                _performanceHistory.RemoveAt(0);
            }
            
            // Clean up system performance history
            foreach (var system in _systemPerformance.Values)
            {
                while (system.ProcessingTimeHistory.Count > _maxHistorySize)
                {
                    system.ProcessingTimeHistory.RemoveAt(0);
                }
                while (system.MemoryUsageHistory.Count > _maxHistorySize)
                {
                    system.MemoryUsageHistory.RemoveAt(0);
                }
            }
            
            // Clean up API metrics history
            foreach (var api in _apiMetrics.Values)
            {
                while (api.ResponseTimeHistory.Count > _maxHistorySize)
                {
                    api.ResponseTimeHistory.RemoveAt(0);
                }
            }
        }
        
        #endregion
    }
    
    #region Data Classes
    
    [Serializable]
    public class PerformanceMetrics
    {
        public DateTime Timestamp;
        public float FPS;
        public long MemoryUsageMB;
        public int SystemCount;
        public int TotalAPIRequests;
        public float AverageAPIResponseTime;
        public int GameObjectCount;
        public int MonoBehaviourCount;
        public int ActiveCameraCount;
    }
    
    [Serializable]
    public class PerformanceSnapshot
    {
        public DateTime Timestamp;
        public float FPS;
        public long MemoryUsageMB;
        public int SystemCount;
        public int GameObjectCount;
    }
    
    [Serializable]
    public class SystemPerformance
    {
        public string SystemName;
        public bool IsActive;
        public DateTime LastActivity;
        public List<float> ProcessingTimeHistory;
        public List<long> MemoryUsageHistory;
        public int ErrorCount;
        public string LastError;
        public DateTime LastErrorTime;
        
        public float AverageProcessingTime => ProcessingTimeHistory.Any() ? ProcessingTimeHistory.Average() : 0f;
        public long CurrentMemoryUsage => MemoryUsageHistory.LastOrDefault();
        public float ErrorRate => ProcessingTimeHistory.Count > 0 ? (float)ErrorCount / ProcessingTimeHistory.Count : 0f;
    }
    
    [Serializable]
    public class APICallMetrics
    {
        public string Endpoint;
        public int TotalCalls;
        public int SuccessfulCalls;
        public float AverageResponseTime;
        public List<float> ResponseTimeHistory;
        public DateTime LastCallTime;
        
        public float SuccessRate => TotalCalls > 0 ? (float)SuccessfulCalls / TotalCalls : 0f;
        public float MinResponseTime => ResponseTimeHistory.Any() ? ResponseTimeHistory.Min() : 0f;
        public float MaxResponseTime => ResponseTimeHistory.Any() ? ResponseTimeHistory.Max() : 0f;
    }
    
    [Serializable]
    public class PerformanceAlert
    {
        public string Title;
        public string Message;
        public AlertLevel Level;
        public DateTime Timestamp;
        public string SystemSource;
    }
    
    public enum AlertLevel
    {
        Info,
        Warning,
        Critical
    }
    
    #endregion
} 