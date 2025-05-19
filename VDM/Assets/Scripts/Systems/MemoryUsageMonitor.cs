using System;
using System.Collections.Concurrent;
using System.Diagnostics;
using System.Threading;

namespace VisualDM.Systems.Animation.Memory
{
    /// <summary>
    /// Real-time memory usage monitor for animation components. Supports alerting and hooks for visualization.
    /// </summary>
    public class MemoryUsageMonitor
    {
        private readonly ConcurrentDictionary<string, long> _componentUsage = new();
        private long _totalUsage;
        private readonly long _alertThresholdBytes;
        public event Action<string, long> OnAlert;

        public MemoryUsageMonitor(long alertThresholdBytes = 128 * 1024 * 1024)
        {
            _alertThresholdBytes = alertThresholdBytes;
        }

        public void Track(string component, long bytes)
        {
            _componentUsage.AddOrUpdate(component, bytes, (k, v) => v + bytes);
            Interlocked.Add(ref _totalUsage, bytes);
            if (_totalUsage > _alertThresholdBytes)
            {
                OnAlert?.Invoke(component, _totalUsage);
            }
        }

        public void Untrack(string component, long bytes)
        {
            _componentUsage.AddOrUpdate(component, 0, (k, v) => Math.Max(0, v - bytes));
            Interlocked.Add(ref _totalUsage, -bytes);
        }

        public long GetComponentUsage(string component)
        {
            return _componentUsage.TryGetValue(component, out var usage) ? usage : 0;
        }

        public long GetTotalUsage() => Interlocked.Read(ref _totalUsage);

        // For visualization: returns a snapshot of all component usages
        public ConcurrentDictionary<string, long> GetAllUsages() => new(_componentUsage);
    }
} 