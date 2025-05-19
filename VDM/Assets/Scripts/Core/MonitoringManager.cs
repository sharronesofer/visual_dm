using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Threading;
using UnityEngine;
using System.IO;

namespace VisualDM.Core
{
    /// <summary>
    /// Singleton manager for runtime monitoring, metrics collection, and alerting.
    /// Collects FPS, memory, ping, error count, and custom events. Provides alerting and dashboard integration.
    /// Collects and logs runtime performance metrics for the Unity game, including frame time, per-system update time, memory allocations, garbage collection, and event latency.
    /// </summary>
    public class MonitoringManager : MonoBehaviour
    {
        public static MonitoringManager Instance { get; private set; }

        // Metric data structure
        public class Metric
        {
            public string Name;
            public float Value;
            public Dictionary<string, string> Tags;
            public DateTime Timestamp;
        }

        private List<Metric> recentMetrics = new List<Metric>();
        private readonly object metricsLock = new object();
        private float metricInterval = 10f;
        private float metricTimer = 0f;
        private int frameCount = 0;
        private float fpsAccumulator = 0f;
        private float lastFps = 0f;
        private int errorCount = 0;
        private float lastPing = -1f;
        private Thread pingThread;
        private bool running = true;

        // Alert rule configuration
        private float fpsAlertThreshold = 30f;
        private float memoryAlertThresholdMB = 1024f; // Example: 1GB
        private float pingAlertThresholdMs = 200f;
        private int errorCountAlertThreshold = 1;

        /// <summary>
        /// Delegate for alert events.
        /// </summary>
        /// <param name="alertType">Type/category of alert (e.g., Performance, Memory).</param>
        /// <param name="message">Alert message details.</param>
        public delegate void AlertEventHandler(string alertType, string message);
        private event AlertEventHandler AlertEvent;
        private readonly object alertLock = new object();

        /// <summary>
        /// Struct representing alert threshold configuration.
        /// </summary>
        public struct AlertThresholds
        {
            public float Fps;
            public float MemoryMB;
            public float PingMs;
            public int ErrorCount;
        }

        /// <summary>
        /// Get the current alert thresholds.
        /// </summary>
        public AlertThresholds CurrentAlertThresholds
        {
            get
            {
                lock (alertLock)
                {
                    return new AlertThresholds
                    {
                        Fps = fpsAlertThreshold,
                        MemoryMB = memoryAlertThresholdMB,
                        PingMs = pingAlertThresholdMs,
                        ErrorCount = errorCountAlertThreshold
                    };
                }
            }
        }

        private float frameTime;
        private float lastGCCollectTime;
        private int lastFrameCount;
        private List<float> systemUpdateTimes = new List<float>();
        private List<float> memoryAllocations = new List<float>();
        private List<float> eventLatencies = new List<float>();
        private Dictionary<string, float> perSystemUpdateTimes = new Dictionary<string, float>();
        private Dictionary<string, List<float>> eventLatenciesByType = new Dictionary<string, List<float>>();

        void Awake()
        {
            if (Instance != null && Instance != this)
            {
                Destroy(gameObject);
                return;
            }
            Instance = this;
            DontDestroyOnLoad(gameObject);
            StartPingThread();
        }

        void OnDestroy()
        {
            running = false;
            if (pingThread != null && pingThread.IsAlive)
                pingThread.Abort();
        }

        void Update()
        {
            frameTime = Time.deltaTime * 1000f;
            systemUpdateTimes.Add(frameTime);
            memoryAllocations.Add(GC.GetTotalMemory(false) / (1024f * 1024f));
            if (GC.CollectionCount(0) > lastFrameCount)
            {
                lastGCCollectTime = Time.time;
                lastFrameCount = GC.CollectionCount(0);
            }
            // Optionally, measure event latency if event system exposes hooks
            frameCount++;
            fpsAccumulator += Time.unscaledDeltaTime;
            metricTimer += Time.unscaledDeltaTime;
            if (metricTimer >= metricInterval)
            {
                CollectAndSendMetrics();
                metricTimer = 0f;
            }
        }

        private void CollectAndSendMetrics()
        {
            float fps = frameCount / fpsAccumulator;
            lastFps = fps;
            frameCount = 0;
            fpsAccumulator = 0f;
            float memory = (float)(GC.GetTotalMemory(false) / (1024.0 * 1024.0));
            float cpu = -1f; // Not available in Unity runtime, stub for future
            float ping = lastPing;
            int errors = errorCount;
            RecordMetric("fps", fps);
            RecordMetric("memory_mb", memory);
            RecordMetric("cpu_percent", cpu);
            RecordMetric("ping_ms", ping);
            RecordMetric("error_count", errors);
            // Send metrics to backend via WebSocketClient if connected (stub)
            // Example: WebSocketClient.Instance?.SendMetrics(recentMetrics);
            // Integration point for future implementation.
        }

        /// <summary>
        /// Record a custom metric for monitoring and alert evaluation.
        /// </summary>
        /// <param name="name">Metric name.</param>
        /// <param name="value">Metric value.</param>
        public void RecordMetric(string name, float value)
        {
            var metric = new Metric
            {
                Name = name,
                Value = value,
                Tags = new Dictionary<string, string>(),
                Timestamp = DateTime.UtcNow
            };
            lock (metricsLock)
            {
                recentMetrics.Add(metric);
                if (recentMetrics.Count > 1000)
                    recentMetrics.RemoveAt(0);
            }
            EvaluateAlerts();
        }

        /// <summary>
        /// Get a list of recent metrics for dashboard display.
        /// </summary>
        /// <returns>List of recent metrics.</returns>
        public List<Metric> GetRecentMetrics()
        {
            lock (metricsLock)
            {
                return new List<Metric>(recentMetrics);
            }
        }

        /// <summary>
        /// Increment error count (call from error handlers).
        /// </summary>
        public void IncrementErrorCount()
        {
            Interlocked.Increment(ref errorCount);
        }

        /// <summary>
        /// Subscribe to alert events.
        /// </summary>
        /// <param name="handler">Handler to receive alert events.</param>
        public void SubscribeToAlerts(AlertEventHandler handler)
        {
            lock (alertLock)
            {
                AlertEvent += handler;
            }
        }

        /// <summary>
        /// Unsubscribe from alert events.
        /// </summary>
        /// <param name="handler">Handler to remove from alert events.</param>
        public void UnsubscribeFromAlerts(AlertEventHandler handler)
        {
            lock (alertLock)
            {
                AlertEvent -= handler;
            }
        }

        /// <summary>
        /// Called by WebSocketClient when an alert is received from backend.
        /// </summary>
        /// <param name="alertType">Type/category of alert.</param>
        /// <param name="message">Alert message details.</param>
        public void HandleAlert(string alertType, string message)
        {
            AlertEvent?.Invoke(alertType, message);
        }

        private void StartPingThread()
        {
            pingThread = new Thread(() =>
            {
                while (running)
                {
                    try
                    {
                        // Implement ping to backend server (stub)
                        // Example: WebSocketClient.Instance?.SendPing();
                        // lastPing = ... (update with actual ping time)
                        // Integration point for future implementation.
                        Thread.Sleep(5000);
                    }
                    catch { }
                }
            });
            pingThread.IsBackground = true;
            pingThread.Start();
        }

        private void EvaluateAlerts()
        {
            var latest = recentMetrics.Count > 0 ? recentMetrics[recentMetrics.Count - 1] : null;
            if (latest == null) return;
            // FPS
            if (latest.Name == "fps" && latest.Value < fpsAlertThreshold)
                TriggerAlert("Performance", $"Low FPS: {latest.Value:F1}");
            // Memory
            if (latest.Name == "memory_mb" && latest.Value > memoryAlertThresholdMB)
                TriggerAlert("Memory", $"High memory usage: {latest.Value:F1} MB");
            // Ping
            if (latest.Name == "ping_ms" && latest.Value > pingAlertThresholdMs)
                TriggerAlert("Network", $"High ping: {latest.Value:F0} ms");
            // Errors
            if (latest.Name == "error_count" && latest.Value >= errorCountAlertThreshold)
                TriggerAlert("Error", $"Error count: {latest.Value:F0}");
        }

        /// <summary>
        /// Triggers an alert event and stubs for future notification integration.
        /// </summary>
        /// <param name="alertType">Type/category of alert.</param>
        /// <param name="message">Alert message details.</param>
        private void TriggerAlert(string alertType, string message)
        {
            lock (alertLock)
            {
                AlertEvent?.Invoke(alertType, message);
            }
            // Integrate with email, webhook, or other notification systems (stub)
            // Example: NotificationService.SendAlert(alertType, message);
            // Integration point for future implementation.
        }

        /// <summary>
        /// Set the FPS alert threshold.
        /// </summary>
        /// <param name="threshold">Minimum FPS before alert triggers.</param>
        public void SetFpsAlertThreshold(float threshold)
        {
            lock (alertLock)
            {
                fpsAlertThreshold = threshold;
            }
        }

        /// <summary>
        /// Set the memory usage alert threshold in MB.
        /// </summary>
        /// <param name="thresholdMB">Maximum memory usage in MB before alert triggers.</param>
        public void SetMemoryAlertThreshold(float thresholdMB)
        {
            lock (alertLock)
            {
                memoryAlertThresholdMB = thresholdMB;
            }
        }

        /// <summary>
        /// Set the ping alert threshold in milliseconds.
        /// </summary>
        /// <param name="thresholdMs">Maximum ping in ms before alert triggers.</param>
        public void SetPingAlertThreshold(float thresholdMs)
        {
            lock (alertLock)
            {
                pingAlertThresholdMs = thresholdMs;
            }
        }

        /// <summary>
        /// Set the error count alert threshold.
        /// </summary>
        /// <param name="threshold">Minimum error count before alert triggers.</param>
        public void SetErrorCountAlertThreshold(int threshold)
        {
            lock (alertLock)
            {
                errorCountAlertThreshold = threshold;
            }
        }

        /// <summary>
        /// Reset all alert thresholds to their default values.
        /// </summary>
        public void ResetAlertThresholdsToDefault()
        {
            lock (alertLock)
            {
                fpsAlertThreshold = 30f;
                memoryAlertThresholdMB = 1024f;
                pingAlertThresholdMs = 200f;
                errorCountAlertThreshold = 1;
            }
        }

        /// <summary>
        /// Exports collected metrics to a CSV file for analysis.
        /// </summary>
        public void ExportMetrics(string path)
        {
            using (var writer = new StreamWriter(path))
            {
                writer.WriteLine("FrameTimeMs,MemoryMB,EventLatencyMs");
                for (int i = 0; i < systemUpdateTimes.Count; i++)
                {
                    float eventLatency = (i < eventLatencies.Count) ? eventLatencies[i] : 0f;
                    writer.WriteLine($"{systemUpdateTimes[i]},{memoryAllocations[i]},{eventLatency}");
                }
            }
        }

        /// <summary>
        /// Logs a custom event latency metric.
        /// </summary>
        public void LogEventLatency(float latencyMs)
        {
            eventLatencies.Add(latencyMs);
        }

        /// <summary>
        /// Call at the start of a system's update to record the start time.
        /// </summary>
        public void BeginSystemUpdate(string systemName)
        {
            perSystemUpdateTimes[systemName] = Time.realtimeSinceStartup;
        }

        /// <summary>
        /// Call at the end of a system's update to record the elapsed time (ms).
        /// </summary>
        public void EndSystemUpdate(string systemName)
        {
            if (perSystemUpdateTimes.TryGetValue(systemName, out float start))
            {
                float elapsed = (Time.realtimeSinceStartup - start) * 1000f;
                RecordMetric($"system_{systemName}_update_ms", elapsed);
            }
        }

        /// <summary>
        /// Log the latency (ms) for a specific event type.
        /// </summary>
        public void LogEventLatency(string eventType, float latencyMs)
        {
            if (!eventLatenciesByType.ContainsKey(eventType))
                eventLatenciesByType[eventType] = new List<float>(128);
            eventLatenciesByType[eventType].Add(latencyMs);
            if (eventLatenciesByType[eventType].Count > 1000)
                eventLatenciesByType[eventType].RemoveAt(0);
            RecordMetric($"event_{eventType}_latency_ms", latencyMs);
        }

        /// <summary>
        /// Export per-system update times and event latencies to CSV for analysis.
        /// </summary>
        public void ExportPerformanceMetrics(string path)
        {
            using (var writer = new StreamWriter(path))
            {
                writer.WriteLine("system,event_type,latency_ms");
                foreach (var kvp in eventLatenciesByType)
                {
                    foreach (var latency in kvp.Value)
                        writer.WriteLine($"-,{kvp.Key},{latency}");
                }
                // Optionally, export per-system update times if stored historically
            }
        }
    }
} 