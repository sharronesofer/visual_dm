namespace Systems.Integration
{
    /// <summary>
    /// Interface for the Chaos Engine, enabling bidirectional integration with motif and other systems.
    /// </summary>
    public interface IChaosEngine
    {
        /// <summary>
        /// Called when a motif event occurs.
        /// </summary>
        /// <param name="eventData">Details about the motif event.</param>
        void OnMotifEvent(MotifEventData eventData);
        /// <summary>
        /// Gets the current chaos state.
        /// </summary>
        /// <returns>The current chaos state.</returns>
        ChaosState GetChaosState();
        /// <summary>
        /// Synchronizes the chaos state from an external source.
        /// </summary>
        /// <param name="state">The new chaos state.</param>
        void SyncChaosState(ChaosState state);
        // Extend as needed for bidirectional integration
    }

    /// <summary>
    /// Represents the current state of chaos in the system.
    /// </summary>
    public class ChaosState
    {
        public float ChaosLevel { get; set; }
        public string Description { get; set; }
        // Add more fields as needed
    }

    /// <summary>
    /// Data contract for motif-related events sent to the Chaos Engine.
    /// </summary>
    public class MotifEventData
    {
        public string MotifTheme { get; set; }
        public bool IsChaosSource { get; set; }
        public string EventType { get; set; }
        public string Context { get; set; }
        // Add more fields as needed
    }
}