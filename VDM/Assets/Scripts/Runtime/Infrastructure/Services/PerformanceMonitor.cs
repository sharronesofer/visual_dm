using System;
using System.Collections.Generic;
using UnityEngine;

namespace VDM.Infrastructure.Core
{
    public class PerformanceMonitor : MonoBehaviour
    {
        private static PerformanceMonitor _instance;
        public static PerformanceMonitor Instance
        {
            get
            {
                if (_instance == null)
                {
                    _instance = FindObjectOfType<PerformanceMonitor>();
                    if (_instance == null)
                    {
                        GameObject go = new GameObject("PerformanceMonitor");
                        _instance = go.AddComponent<PerformanceMonitor>();
                        DontDestroyOnLoad(go);
                    }
                }
                return _instance;
            }
        }

        [Header("Performance Metrics")]
        public bool enableMonitoring = true;
        public float updateInterval = 1.0f;
        
        private Dictionary<string, float> metrics = new Dictionary<string, float>();
        private Dictionary<string, List<float>> metricHistory = new Dictionary<string, List<float>>();
        private Dictionary<string, SystemPerformanceData> systemPerformance = new Dictionary<string, SystemPerformanceData>();
        private Dictionary<string, float> apiMetrics = new Dictionary<string, float>();
        private float lastUpdateTime;
        
        // Performance counters
        private int frameCount;
        private float deltaTime;
        private float fps;
        private float memoryUsage;
        
        // Events
        public event Action<PerformanceAlert> OnPerformanceAlert;
        
        void Start()
        {
            if (_instance != null && _instance != this)
            {
                Destroy(gameObject);
                return;
            }
            
            _instance = this;
            DontDestroyOnLoad(gameObject);
            
            InitializeMetrics();
        }
        
        void Update()
        {
            if (!enableMonitoring) return;
            
            frameCount++;
            deltaTime += (Time.unscaledDeltaTime - deltaTime) * 0.1f;
            
            if (Time.time - lastUpdateTime >= updateInterval)
            {
                UpdateMetrics();
                lastUpdateTime = Time.time;
            }
        }
        
        private void InitializeMetrics()
        {
            metrics["FPS"] = 0f;
            metrics["FrameTime"] = 0f;
            metrics["MemoryUsage"] = 0f;
            metrics["DrawCalls"] = 0f;
            metrics["Triangles"] = 0f;
            
            foreach (var key in metrics.Keys)
            {
                metricHistory[key] = new List<float>();
            }
            
            // Initialize API metrics
            apiMetrics["TotalRequests"] = 0f;
            apiMetrics["SuccessfulRequests"] = 0f;
            apiMetrics["FailedRequests"] = 0f;
            apiMetrics["AverageResponseTime"] = 0f;
        }
        
        private void UpdateMetrics()
        {
            // Calculate FPS
            fps = 1.0f / deltaTime;
            UpdateMetric("FPS", fps);
            UpdateMetric("FrameTime", deltaTime * 1000f); // in milliseconds
            
            // Memory usage
            memoryUsage = (float)GC.GetTotalMemory(false) / (1024 * 1024); // MB
            UpdateMetric("MemoryUsage", memoryUsage);
            
            // Unity-specific metrics
            UpdateMetric("DrawCalls", UnityEngine.Rendering.DebugUI.instance != null ? 0 : 0); // Placeholder
            UpdateMetric("Triangles", 0); // Placeholder - would need profiler integration
        }
        
        private void UpdateMetric(string name, float value)
        {
            metrics[name] = value;
            
            if (!metricHistory.ContainsKey(name))
                metricHistory[name] = new List<float>();
                
            metricHistory[name].Add(value);
            
            // Keep only last 100 samples
            if (metricHistory[name].Count > 100)
                metricHistory[name].RemoveAt(0);
        }
        
        public float GetMetric(string name)
        {
            return metrics.ContainsKey(name) ? metrics[name] : 0f;
        }
        
        public List<float> GetMetricHistory(string name)
        {
            return metricHistory.ContainsKey(name) ? new List<float>(metricHistory[name]) : new List<float>();
        }
        
        public Dictionary<string, float> GetAllMetrics()
        {
            return new Dictionary<string, float>(metrics);
        }
        
        public void RecordCustomMetric(string name, float value)
        {
            UpdateMetric(name, value);
        }
        
        public void StartTimer(string name)
        {
            UpdateMetric($"{name}_StartTime", Time.realtimeSinceStartup);
        }
        
        public void EndTimer(string name)
        {
            float startTime = GetMetric($"{name}_StartTime");
            if (startTime > 0)
            {
                float duration = Time.realtimeSinceStartup - startTime;
                UpdateMetric(name, duration * 1000f); // in milliseconds
            }
        }
        
        // New methods for system performance tracking
        public void TrackSystemActivity(string systemName, float executionTime, long memoryUsed)
        {
            if (!systemPerformance.ContainsKey(systemName))
            {
                systemPerformance[systemName] = new SystemPerformanceData
                {
                    SystemName = systemName,
                    TotalExecutionTime = 0f,
                    TotalMemoryUsed = 0L,
                    CallCount = 0,
                    LastUpdated = DateTime.UtcNow
                };
            }
            
            var data = systemPerformance[systemName];
            data.TotalExecutionTime += executionTime;
            data.TotalMemoryUsed += memoryUsed;
            data.CallCount++;
            data.LastUpdated = DateTime.UtcNow;
            data.AverageExecutionTime = data.TotalExecutionTime / data.CallCount;
        }
        
        public void TrackMemoryUsage(string systemName, long memoryBytes)
        {
            float memoryMB = memoryBytes / (1024f * 1024f);
            UpdateMetric($"Memory_{systemName}", memoryMB);
            
            // Check for memory alerts (2GB threshold)
            if (memoryBytes > 2L * 1024 * 1024 * 1024)
            {
                OnPerformanceAlert?.Invoke(new PerformanceAlert
                {
                    AlertType = "HighMemoryUsage",
                    SystemName = systemName,
                    Value = memoryMB,
                    Threshold = 2048f, // 2GB in MB
                    Timestamp = DateTime.UtcNow
                });
            }
        }
        
        public Dictionary<string, SystemPerformanceData> GetAllSystemPerformance()
        {
            return new Dictionary<string, SystemPerformanceData>(systemPerformance);
        }
        
        public Dictionary<string, float> GetAPIMetrics()
        {
            return new Dictionary<string, float>(apiMetrics);
        }
        
        public void LogPerformanceReport()
        {
            Debug.Log("=== Performance Report ===");
            foreach (var metric in metrics)
            {
                Debug.Log($"{metric.Key}: {metric.Value:F2}");
            }
        }
        
        void OnGUI()
        {
            if (!enableMonitoring) return;
            
            GUILayout.BeginArea(new Rect(10, 10, 200, 150));
            GUILayout.BeginVertical("box");
            GUILayout.Label("Performance Monitor");
            
            foreach (var metric in metrics)
            {
                string unit = GetMetricUnit(metric.Key);
                GUILayout.Label($"{metric.Key}: {metric.Value:F1}{unit}");
            }
            
            GUILayout.EndVertical();
            GUILayout.EndArea();
        }
        
        private string GetMetricUnit(string metricName)
        {
            switch (metricName)
            {
                case "FPS": return " fps";
                case "FrameTime": return " ms";
                case "MemoryUsage": return " MB";
                case "DrawCalls": return "";
                case "Triangles": return "";
                default: return "";
            }
        }
    }
    
    [Serializable]
    public class SystemPerformanceData
    {
        public string SystemName;
        public float TotalExecutionTime;
        public long TotalMemoryUsed;
        public int CallCount;
        public float AverageExecutionTime;
        public DateTime LastUpdated;
    }
    
    [Serializable]
    public class PerformanceAlert
    {
        public string AlertType;
        public string SystemName;
        public float Value;
        public float Threshold;
        public DateTime Timestamp;
    }
} 