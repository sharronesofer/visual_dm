using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Threading;
using UnityEngine;
using System.Collections;

namespace VisualDM.Core
{
    /// <summary>
    /// Manages collection and aggregation of performance metrics.
    /// </summary>
    public class MetricsCollector
    {
        private Dictionary<string, double> _memoryPerInteraction = new();
        private Dictionary<string, double> _cpuPerThread = new();
        private double _memoryTotalMb = 0;
        private double _cpuTotalPercent = 0;
        private double _bandwidthKbps = 0;
        private double _errorRate = 0;
        private double _averageResponseTimeMs = 0;
        private int _responseTimeCount = 0;
        private double _responseTimeSum = 0;
        private int _activeInteractions = 0;
        private Dictionary<string, string> _activeInteractionStatuses = new();

        public void IncrementActiveInteractions(string id, string status)
        {
            _activeInteractions++;
            _activeInteractionStatuses[id] = status;
        }

        public void DecrementActiveInteractions(string id)
        {
            _activeInteractions = Math.Max(0, _activeInteractions - 1);
            _activeInteractionStatuses.Remove(id);
        }

        public void RecordResponseTime(double ms)
        {
            _responseTimeSum += ms;
            _responseTimeCount++;
            _averageResponseTimeMs = _responseTimeCount > 0 ? _responseTimeSum / _responseTimeCount : 0;
        }

        public void RecordError(string type, string severity)
        {
            // Log the error
        }

        public void SetErrorRate(double rate)
        {
            _errorRate = rate;
        }

        public void SetMemoryUsage(double totalMb, Dictionary<string, double> perInteraction)
        {
            _memoryTotalMb = totalMb;
            _memoryPerInteraction = perInteraction;
        }

        public void SetCpuUsage(double totalPercent, Dictionary<string, double> perThread)
        {
            _cpuTotalPercent = totalPercent;
            _cpuPerThread = perThread;
        }

        public void SetBandwidth(double kbps)
        {
            _bandwidthKbps = kbps;
        }

        public double GetMemoryTotalMb() => _memoryTotalMb;
        public Dictionary<string, double> GetMemoryPerInteraction() => _memoryPerInteraction;
        public double GetCpuTotalPercent() => _cpuTotalPercent;
        public Dictionary<string, double> GetCpuPerThread() => _cpuPerThread;
        public double GetBandwidth() => _bandwidthKbps;
        public double GetErrorRate() => _errorRate;
        public double GetAverageResponseTimeMs() => _averageResponseTimeMs;
        public int GetActiveInteractions() => _activeInteractions;
    }

    /// <summary>
    /// Configuration for metrics collection and transmission.
    /// </summary>
    public class InteractionMetricsConfig
    {
        /// <summary>Interval (seconds) between each metrics collection/sample.</summary>
        public float CollectionInterval = 5f;
        /// <summary>Interval (seconds) between each metrics transmission attempt.</summary>
        public float TransmissionInterval = 5f;
        /// <summary>Maximum number of metrics snapshots to buffer before sending.</summary>
        public int MaxBufferSize = 100;
        /// <summary>Base delay (seconds) for retrying failed transmissions (exponential backoff).</summary>
        public float BaseRetryDelay = 2f;
        /// <summary>Maximum delay (seconds) for retrying failed transmissions.</summary>
        public float MaxRetryDelay = 60f;

        /// <summary>
        /// Loads config from PlayerPrefs, file, or returns defaults. Extend as needed for remote config.
        /// </summary>
        public static InteractionMetricsConfig LoadOrDefault()
        {
            var config = new InteractionMetricsConfig();
            // Example: Load from PlayerPrefs (extend for file/remote config as needed)
            if (PlayerPrefs.HasKey("Metrics_CollectionInterval"))
                config.CollectionInterval = PlayerPrefs.GetFloat("Metrics_CollectionInterval");
            if (PlayerPrefs.HasKey("Metrics_TransmissionInterval"))
                config.TransmissionInterval = PlayerPrefs.GetFloat("Metrics_TransmissionInterval");
            if (PlayerPrefs.HasKey("Metrics_MaxBufferSize"))
                config.MaxBufferSize = PlayerPrefs.GetInt("Metrics_MaxBufferSize");
            if (PlayerPrefs.HasKey("Metrics_BaseRetryDelay"))
                config.BaseRetryDelay = PlayerPrefs.GetFloat("Metrics_BaseRetryDelay");
            if (PlayerPrefs.HasKey("Metrics_MaxRetryDelay"))
                config.MaxRetryDelay = PlayerPrefs.GetFloat("Metrics_MaxRetryDelay");
            return config;
        }

        /// <summary>
        /// Save current config to PlayerPrefs (extend for file/remote config as needed).
        /// </summary>
        public void Save()
        {
            PlayerPrefs.SetFloat("Metrics_CollectionInterval", CollectionInterval);
            PlayerPrefs.SetFloat("Metrics_TransmissionInterval", TransmissionInterval);
            PlayerPrefs.SetInt("Metrics_MaxBufferSize", MaxBufferSize);
            PlayerPrefs.SetFloat("Metrics_BaseRetryDelay", BaseRetryDelay);
            PlayerPrefs.SetFloat("Metrics_MaxRetryDelay", MaxRetryDelay);
            PlayerPrefs.Save();
        }
    }

    /// <summary>
    /// Thin integration layer for collecting and reporting real-time performance metrics for the Interaction System.
    /// Delegates all metrics collection and aggregation to MetricsCollector.
    /// </summary>
    public class InteractionMetricsCollector : MonoBehaviour
    {
        private MetricsCollector _metricsCollector;
        private readonly Dictionary<Guid, Stopwatch> _interactionTimers = new();
        private float _lastSampleTime = 0f;
        private float _sampleInterval = 5f; // seconds
        private int _errorCount = 0;
        private int _totalInteractions = 0;
        private readonly List<InteractionMetricsSnapshot> _buffer = new();
        private InteractionMetricsSettings _config;
        private bool _transmitting = false;
        private int _retryCount = 0;
        private float _nextRetryTime = 0f;
        private readonly object _statsLock = new object();
        private long _lastBytesSent = 0;
        private long _lastBytesReceived = 0;

        void Awake()
        {
            _config = InteractionMetricsSettings.LoadOrDefault();
            _metricsCollector = new MetricsCollector();
            StartCoroutine(TransmissionCoroutine());
        }

        void Start()
        {
            InvokeRepeating(nameof(SampleBandwidth), 0f, _config.CollectionInterval);
        }

        /// <summary>
        /// Call when an interaction starts. Returns a unique interaction ID.
        /// </summary>
        public Guid OnInteractionStart(string status = "active")
        {
            var id = Guid.NewGuid();
            var sw = Stopwatch.StartNew();
            _interactionTimers[id] = sw;
            _metricsCollector.IncrementActiveInteractions(id.ToString(), status);
            _totalInteractions++;
            return id;
        }

        /// <summary>
        /// Call when an interaction ends. Records response time and decrements active count.
        /// </summary>
        public void OnInteractionEnd(Guid interactionId)
        {
            if (_interactionTimers.TryGetValue(interactionId, out var sw))
            {
                sw.Stop();
                double ms = sw.Elapsed.TotalMilliseconds;
                _metricsCollector.RecordResponseTime(ms);
                _interactionTimers.Remove(interactionId);
            }
            _metricsCollector.DecrementActiveInteractions(interactionId.ToString());
        }

        /// <summary>
        /// Record memory usage for an interaction (in MB).
        /// </summary>
        public void RecordMemoryUsage(string interactionId, double mb)
        {
            var perInteraction = _metricsCollector.GetMemoryPerInteraction();
            perInteraction[interactionId] = mb;
            _metricsCollector.SetMemoryUsage(_metricsCollector.GetMemoryTotalMb(), perInteraction);
        }

        /// <summary>
        /// Record CPU usage for an interaction (in percent).
        /// </summary>
        public void RecordCpuUsage(string interactionId, double percent)
        {
            var perThread = _metricsCollector.GetCpuPerThread();
            perThread[interactionId] = percent;
            _metricsCollector.SetCpuUsage(_metricsCollector.GetCpuTotalPercent(), perThread);
        }

        /// <summary>
        /// Record bandwidth usage for an interaction (in kbps).
        /// </summary>
        public void RecordBandwidth(double kbps)
        {
            _metricsCollector.SetBandwidth(kbps);
        }

        /// <summary>
        /// Record an error for an interaction.
        /// </summary>
        public void RecordError(string type, string severity)
        {
            _metricsCollector.RecordError(type, severity);
            _errorCount++;
        }

        /// <summary>
        /// Set the overall error rate (errors per total interactions).
        /// </summary>
        public void UpdateErrorRate()
        {
            double rate = _totalInteractions > 0 ? (double)_errorCount / _totalInteractions : 0.0;
            _metricsCollector.SetErrorRate(rate);
        }

        /// <summary>
        /// Periodically sample memory, CPU, and bandwidth using Unity/.NET APIs.
        /// Call this from a MonoBehaviour's Update() or a coroutine.
        /// </summary>
        public void SampleSystemMetrics()
        {
            if (Time.unscaledTime - _lastSampleTime < _sampleInterval) return;
            _lastSampleTime = Time.unscaledTime;

            // Memory usage (MB)
            double totalMemoryMb = GC.GetTotalMemory(false) / (1024.0 * 1024.0);
            _metricsCollector.SetMemoryUsage(totalMemoryMb, _metricsCollector.GetMemoryPerInteraction());

            // CPU usage (stub: Unity does not provide direct CPU usage, so this is a placeholder)
            // In production, use platform-specific APIs or plugins for accurate CPU metrics.
            double cpuPercent = -1; // Not available in Unity by default
            _metricsCollector.SetCpuUsage(cpuPercent, _metricsCollector.GetCpuPerThread());

            // Bandwidth (stub: requires integration with network layer)
            double bandwidthKbps = -1; // Placeholder, update with real value if available
            _metricsCollector.SetBandwidth(bandwidthKbps);

            // Update error rate
            UpdateErrorRate();
        }

        /// <summary>
        /// Sample bandwidth usage from WebSocketClient and record as metric.
        /// </summary>
        private void SampleBandwidth()
        {
            var ws = WebSocketClient.Instance;
            if (ws == null) return;
            long sent = ws.TotalBytesSent;
            long received = ws.TotalBytesReceived;
            float deltaSentKB = (sent - _lastBytesSent) / 1024f;
            float deltaReceivedKB = (received - _lastBytesReceived) / 1024f;
            RecordBandwidth(deltaSentKB + deltaReceivedKB);
            _lastBytesSent = sent;
            _lastBytesReceived = received;
        }

        /// <summary>
        /// Get a snapshot of all current metrics for reporting or dashboard.
        /// </summary>
        public MetricsCollector Metrics => _metricsCollector;

        /// <summary>
        /// Buffer the current snapshot for transmission.
        /// </summary>
        public void BufferSnapshot()
        {
            lock (_statsLock)
            {
                _buffer.Add(GetSnapshot());
                if (_buffer.Count > _config.MaxBufferSize)
                    _buffer.RemoveAt(0);
            }
        }

        /// <summary>
        /// Coroutine for periodic metrics transmission.
        /// </summary>
        private IEnumerator TransmissionCoroutine()
        {
            while (true)
            {
                yield return new WaitForSeconds(_config.TransmissionInterval);
                if (Time.time < _nextRetryTime) continue;
                if (_buffer.Count == 0) continue;
                if (_transmitting) continue;
                _transmitting = true;
                var payload = SerializeBuffer();
                bool success = false;
                try
                {
                    success = WebSocketClient.Instance?.SendMetrics(payload) ?? false;
                }
                catch { success = false; }
                if (success)
                {
                    lock (_statsLock) { _buffer.Clear(); }
                    _retryCount = 0;
                }
                else
                {
                    _retryCount++;
                    float delay = Math.Min(
                        _config.BaseRetryDelay * (float)Math.Pow(2, _retryCount - 1),
                        _config.MaxRetryDelay
                    );
                    _nextRetryTime = Time.time + delay;
                }
                _transmitting = false;
            }
        }

        /// <summary>
        /// Serializes the current buffer of metrics to a JSON string.
        /// </summary>
        private string SerializeBuffer()
        {
            // Simplified stub implementation
            return JsonUtility.ToJson(new { snapshots = _buffer, timestamp = DateTime.UtcNow });
        }

        /// <summary>
        /// Get the current snapshot of metrics.
        /// </summary>
        private InteractionMetricsSnapshot GetSnapshot()
        {
            var snapshot = new InteractionMetricsSnapshot
            {
                Timestamp = DateTime.UtcNow,
                MemoryUsageMb = _metricsCollector.GetMemoryTotalMb(),
                CpuUsagePercent = _metricsCollector.GetCpuTotalPercent(),
                BandwidthKbps = _metricsCollector.GetBandwidth(),
                ActiveInteractions = _metricsCollector.GetActiveInteractions(),
                AverageResponseTimeMs = _metricsCollector.GetAverageResponseTimeMs(),
                ErrorRate = _metricsCollector.GetErrorRate(),
                MemoryPerInteraction = _metricsCollector.GetMemoryPerInteraction(),
                CpuPerThread = _metricsCollector.GetCpuPerThread()
            };
            return snapshot;
        }
    }

    /// <summary>
    /// Represents a snapshot of interaction metrics at a point in time.
    /// </summary>
    public class InteractionMetricsSnapshot
    {
        public DateTime Timestamp { get; set; }
        public double MemoryUsageMb { get; set; }
        public double CpuUsagePercent { get; set; }
        public double BandwidthKbps { get; set; }
        public int ActiveInteractions { get; set; }
        public double AverageResponseTimeMs { get; set; }
        public double ErrorRate { get; set; }
        public Dictionary<string, double> MemoryPerInteraction { get; set; }
        public Dictionary<string, double> CpuPerThread { get; set; }
        
        public InteractionMetricsSnapshot()
        {
            Timestamp = DateTime.UtcNow;
            MemoryPerInteraction = new Dictionary<string, double>();
            CpuPerThread = new Dictionary<string, double>();
        }
    }
}