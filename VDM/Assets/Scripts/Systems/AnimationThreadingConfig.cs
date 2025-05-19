using System;

namespace VisualDM.Systems.Animation.Threading
{
    /// <summary>
    /// Configuration for the animation threading system.
    /// </summary>
    public class AnimationThreadingConfig
    {
        /// <summary>
        /// Number of worker threads to use (default: CPU cores - 1).
        /// </summary>
        public int WorkerThreads { get; set; } = Math.Max(2, Environment.ProcessorCount - 1);

        /// <summary>
        /// Enable detailed logging.
        /// </summary>
        public bool EnableLogging { get; set; } = false;

        /// <summary>
        /// Adjusts thread count at runtime.
        /// </summary>
        public void AdjustThreadCount(int newCount)
        {
            WorkerThreads = Math.Max(1, newCount);
            // TODO: Notify thread pool manager if running
        }
    }
} 