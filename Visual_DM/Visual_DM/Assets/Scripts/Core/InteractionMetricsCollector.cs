using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Threading;
using UnityEngine;

namespace VisualDM.Core
{
    /// <summary>
    /// Collects and reports real-time performance metrics for the Interaction System.
    /// Integrates with MonitoringManager for dashboard and alerting.
    /// </summary>
    public class InteractionMetricsCollector
    {
        private int _activeInteractions = 0;
        private readonly object _statsLock = new object();
        private readonly List<double> _responseTimes = new();
        private readonly List<float> _memoryUsages = new();
        private readonly List<float> _cpuUsages = new();
        private readonly List<float> _bandwidths = new();
        private readonly List<string> _errorTypes = new();
        private readonly List<string> _errorSeverities = new();
        private readonly ConcurrentDictionary<Guid, Stopwatch> _interactionTimers = new();

        /// <summary>
        /// Call when an interaction starts. Returns a unique interaction ID.
        /// </summary>
        public Guid OnInteractionStart()
        {
            Interlocked.Increment(ref _activeInteractions);
            var id = Guid.NewGuid();
            var sw = Stopwatch.StartNew();
            _interactionTimers[id] = sw;
            MonitoringManager.Instance.RecordMetric("active_interactions", _activeInteractions);
            return id;
        }

        /// <summary>
        /// Call when an interaction ends. Records response time and decrements active count.
        /// </summary>
        public void OnInteractionEnd(Guid interactionId)
        {
            if (_interactionTimers.TryRemove(interactionId, out var sw))
            {
                sw.Stop();
                double ms = sw.Elapsed.TotalMilliseconds;
                lock (_statsLock) { _responseTimes.Add(ms); }
                MonitoringManager.Instance.RecordMetric("interaction_response_time_ms", (float)ms);
            }
            Interlocked.Decrement(ref _activeInteractions);
            MonitoringManager.Instance.RecordMetric("active_interactions", _activeInteractions);
        }

        /// <summary>
        /// Record memory usage for an interaction (in MB).
        /// </summary>
        public void RecordMemoryUsage(float mb)
        {
            lock (_statsLock) { _memoryUsages.Add(mb); }
            MonitoringManager.Instance.RecordMetric("interaction_memory_mb", mb);
        }

        /// <summary>
        /// Record CPU usage for an interaction (in percent).
        /// </summary>
        public void RecordCpuUsage(float percent)
        {
            lock (_statsLock) { _cpuUsages.Add(percent); }
            MonitoringManager.Instance.RecordMetric("interaction_cpu_percent", percent);
        }

        /// <summary>
        /// Record bandwidth usage for an interaction (in KB).
        /// </summary>
        public void RecordBandwidth(float kb)
        {
            lock (_statsLock) { _bandwidths.Add(kb); }
            MonitoringManager.Instance.RecordMetric("interaction_bandwidth_kb", kb);
        }

        /// <summary>
        /// Record an error for an interaction.
        /// </summary>
        public void RecordError(string type, string severity)
        {
            lock (_statsLock)
            {
                _errorTypes.Add(type);
                _errorSeverities.Add(severity);
            }
            MonitoringManager.Instance.RecordMetric($"interaction_error_{type}_{severity}", 1);
        }

        /// <summary>
        /// Get current stats for dashboard or reporting.
        /// </summary>
        public InteractionMetricsSnapshot GetSnapshot()
        {
            lock (_statsLock)
            {
                return new InteractionMetricsSnapshot
                {
                    ActiveInteractions = _activeInteractions,
                    ResponseTimes = _responseTimes.ToArray(),
                    MemoryUsages = _memoryUsages.ToArray(),
                    CpuUsages = _cpuUsages.ToArray(),
                    Bandwidths = _bandwidths.ToArray(),
                    ErrorTypes = _errorTypes.ToArray(),
                    ErrorSeverities = _errorSeverities.ToArray(),
                    ResponseTimeStats = ComputeStats(_responseTimes)
                };
            }
        }

        /// <summary>
        /// Compute min, max, avg, p95, p99 for a list of values.
        /// </summary>
        private static ResponseTimeStats ComputeStats(List<double> values)
        {
            if (values.Count == 0) return new ResponseTimeStats();
            var sorted = values.OrderBy(x => x).ToArray();
            double avg = sorted.Average();
            double p95 = sorted[(int)(0.95 * (sorted.Length - 1))];
            double p99 = sorted[(int)(0.99 * (sorted.Length - 1))];
            return new ResponseTimeStats
            {
                Min = sorted.First(),
                Max = sorted.Last(),
                Avg = avg,
                P95 = p95,
                P99 = p99
            };
        }
    }

    /// <summary>
    /// Snapshot of current interaction metrics for reporting.
    /// </summary>
    public class InteractionMetricsSnapshot
    {
        public int ActiveInteractions;
        public double[] ResponseTimes;
        public float[] MemoryUsages;
        public float[] CpuUsages;
        public float[] Bandwidths;
        public string[] ErrorTypes;
        public string[] ErrorSeverities;
        public ResponseTimeStats ResponseTimeStats;
    }

    /// <summary>
    /// Statistical summary for response times.
    /// </summary>
    public class ResponseTimeStats
    {
        public double Min;
        public double Max;
        public double Avg;
        public double P95;
        public double P99;
    }
}