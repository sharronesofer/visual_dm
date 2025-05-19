using System;
using System.Collections.Generic;
using System.Diagnostics;

namespace Systems.Integration
{
    public static class IntegrationLogger
    {
        public static event Action<LogEntry> OnLog;
        public static Action<string, LogLevel> LogHandler = (msg, level) => { };

        public static void Log(string message, LogLevel level = LogLevel.Info, string source = null, string target = null, string operation = null, string status = null)
        {
            var entry = new LogEntry
            {
                Timestamp = DateTime.UtcNow,
                Message = message,
                Level = level,
                SourceSystem = source,
                TargetSystem = target,
                Operation = operation,
                Status = status
            };
            OnLog?.Invoke(entry);
            LogHandler?.Invoke(message, level);
        }
    }

    public class LogEntry
    {
        public DateTime Timestamp;
        public string Message;
        public LogLevel Level;
        public string SourceSystem;
        public string TargetSystem;
        public string Operation;
        public string Status;
    }

    public enum LogLevel { Debug, Info, Warn, Error, Critical }

    public static class IntegrationMetrics
    {
        public static event Action<MetricEntry> OnMetric;
        private static readonly Dictionary<string, double> _metrics = new Dictionary<string, double>();
        private static readonly Random _rand = new Random();
        public static double SamplingRate = 1.0; // 1.0 = 100%, 0.1 = 10%

        public static void Record(string metric, double value)
        {
            if (_rand.NextDouble() > SamplingRate) return;
            _metrics[metric] = value;
            OnMetric?.Invoke(new MetricEntry { Name = metric, Value = value, Timestamp = DateTime.UtcNow });
        }

        public static double Get(string metric)
        {
            return _metrics.TryGetValue(metric, out var value) ? value : 0;
        }
    }

    public class MetricEntry
    {
        public string Name;
        public double Value;
        public DateTime Timestamp;
    }

    public static class IntegrationDiagnostics
    {
        public static event Action<TraceEntry> OnTrace;
        public static void Trace(string operation, string details, string source = null, string target = null)
        {
            var entry = new TraceEntry
            {
                Operation = operation,
                Details = details,
                SourceSystem = source,
                TargetSystem = target,
                Timestamp = DateTime.UtcNow
            };
            OnTrace?.Invoke(entry);
            IntegrationLogger.Log($"[TRACE] {operation}: {details}", LogLevel.Debug, source, target, operation, "trace");
        }
    }

    public class TraceEntry
    {
        public string Operation;
        public string Details;
        public string SourceSystem;
        public string TargetSystem;
        public DateTime Timestamp;
    }

    public static class IntegrationAlerting
    {
        public static event Action<AlertEntry> OnAlert;
        public static Action<string, LogLevel> AlertHandler = (msg, level) => { };

        public static void Alert(string message, LogLevel level = LogLevel.Error, string source = null, string target = null, string operation = null)
        {
            var entry = new AlertEntry
            {
                Timestamp = DateTime.UtcNow,
                Message = message,
                Level = level,
                SourceSystem = source,
                TargetSystem = target,
                Operation = operation
            };
            OnAlert?.Invoke(entry);
            AlertHandler?.Invoke(message, level);
        }
    }

    public class AlertEntry
    {
        public DateTime Timestamp;
        public string Message;
        public LogLevel Level;
        public string SourceSystem;
        public string TargetSystem;
        public string Operation;
    }

    // Dashboard hooks can be implemented by UI systems subscribing to metrics/logs
} 