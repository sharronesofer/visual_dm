using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Threading;
using VisualDM.Systems.Metrics;
using UnityEngine;
using System.Collections;
using VisualDM.Core.Network;

namespace VisualDM.Core
{
    /// <summary>
    /// Configuration for metrics collection and transmission.
    /// </summary>
    public class InteractionMetricsConfig
    {
        public float TransmissionInterval = 5f; // seconds
        public int MaxBufferSize = 100;
        public float BaseRetryDelay = 2f; // seconds
        public float MaxRetryDelay = 60f; // seconds

        // Loads config from file, PlayerPrefs, or returns defaults
        public static InteractionMetricsConfig LoadOrDefault()
        {
            // TODO: Load from file or PlayerPrefs if available
            return new InteractionMetricsConfig();
        }
    }

    /// <summary>
    /// Thin integration layer for collecting and reporting real-time performance metrics for the Interaction System.
    /// Delegates all metrics collection and aggregation to MetricsCollector.
    /// </summary>
    public class InteractionMetricsCollector : MonoBehaviour
    {
        private readonly MetricsCollector _metricsCollector;
        private readonly Dictionary<Guid, Stopwatch> _interactionTimers = new();
        private float _lastSampleTime = 0f;
        private float _sampleInterval = 5f; // seconds
        private int _errorCount = 0;
        private int _totalInteractions = 0;
        private readonly List<InteractionMetricsSnapshot> _buffer = new();
        private InteractionMetricsConfig _config;
        private bool _transmitting = false;
        private int _retryCount = 0;
        private float _nextRetryTime = 0f;
        private readonly object _statsLock = new object();
        private long _lastBytesSent = 0;
        private long _lastBytesReceived = 0;

        public InteractionMetricsCollector(MetricsCollector metricsCollector)
        {
            _metricsCollector = metricsCollector;
        }

        void Awake()
        {
            _config = InteractionMetricsConfig.LoadOrDefault();
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
                    _nextRetryTime = Time.time + Mathf.Min(_config.BaseRetryDelay * Mathf.Pow(2, _retryCount), _config.MaxRetryDelay);
                }
                _transmitting = false;
            }
        }

        /// <summary>
        /// Serialize the buffer to JSON or agreed format.
        /// </summary>
        private string SerializeBuffer()
        {
            // Replace with actual serialization as needed
            return JsonUtility.ToJson(new { metrics = _buffer });
        }
    }
}