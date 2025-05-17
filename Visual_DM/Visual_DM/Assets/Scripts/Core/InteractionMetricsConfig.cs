using UnityEngine;

namespace VisualDM.Core
{
    /// <summary>
    /// Configuration for interaction metrics collection and transmission.
    /// </summary>
    public class InteractionMetricsConfig
    {
        /// <summary>Interval (seconds) between metrics collection samples.</summary>
        public float CollectionInterval = 1f;
        /// <summary>Interval (seconds) between metrics transmission batches.</summary>
        public float TransmissionInterval = 10f;
        /// <summary>Maximum number of snapshots to buffer before dropping oldest.</summary>
        public int MaxBufferSize = 100;
        /// <summary>Base retry delay (seconds) for failed transmissions.</summary>
        public float BaseRetryDelay = 2f;
        /// <summary>Maximum retry delay (seconds) for exponential backoff.</summary>
        public float MaxRetryDelay = 60f;
        /// <summary>Verbosity level for logging (0=silent, 1=info, 2=debug).</summary>
        public int VerbosityLevel = 1;

        /// <summary>
        /// Loads config from persistent storage or returns defaults.
        /// </summary>
        public static InteractionMetricsConfig LoadOrDefault()
        {
            // TODO: Load from file, PlayerPrefs, or ScriptableObject if needed
            return new InteractionMetricsConfig();
        }
    }
}