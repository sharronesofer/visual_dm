using System;
using System.Collections.Concurrent;
using System.Diagnostics;
using System.Threading;

namespace Visual_DM.Animation.Threading
{
    /// <summary>
    /// Provides performance metrics and logging for the animation threading system.
    /// </summary>
    public static class AnimationMetrics
    {
        private static ConcurrentDictionary<int, long> _threadActiveTicks = new ConcurrentDictionary<int, long>();
        private static ConcurrentBag<long> _taskExecutionTimes = new ConcurrentBag<long>();
        private static Stopwatch _globalStopwatch = Stopwatch.StartNew();

        /// <summary>
        /// Records active thread time.
        /// </summary>
        public static void RecordThreadActive(int threadId, long ticks)
        {
            _threadActiveTicks.AddOrUpdate(threadId, ticks, (id, old) => old + ticks);
        }

        /// <summary>
        /// Records task execution time in ticks.
        /// </summary>
        public static void RecordTaskExecution(long ticks)
        {
            _taskExecutionTimes.Add(ticks);
        }

        /// <summary>
        /// Gets the average task execution time in milliseconds.
        /// </summary>
        public static double AverageTaskMs => _taskExecutionTimes.Count == 0 ? 0 : (_taskExecutionTimes.Sum() / (double)_taskExecutionTimes.Count) / TimeSpan.TicksPerMillisecond;

        /// <summary>
        /// Gets the thread utilization as a percentage.
        /// </summary>
        public static double ThreadUtilizationPercent
        {
            get
            {
                long totalActive = 0;
                foreach (var t in _threadActiveTicks.Values) totalActive += t;
                return _globalStopwatch.ElapsedTicks == 0 ? 0 : (totalActive / (double)_globalStopwatch.ElapsedTicks) * 100.0;
            }
        }

        /// <summary>
        /// Logs a performance message.
        /// </summary>
        public static void Log(string message)
        {
            UnityEngine.Debug.Log($"[AnimationMetrics] {message}");
        }
    }
} 