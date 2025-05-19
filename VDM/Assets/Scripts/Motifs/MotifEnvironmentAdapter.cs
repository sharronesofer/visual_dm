using System;

namespace VDM.Motifs
{
    /// <summary>
    /// Adapts motif changes to environment effects (weather, ambient sounds).
    /// </summary>
    public class MotifEnvironmentAdapter : IMotifObserver
    {
        public event Action<string> OnEnvironmentChange; // e.g., "Rain", "Fog", "Clear"

        public MotifEnvironmentAdapter()
        {
            MotifDispatcher.Instance.Register(this);
        }

        /// <summary>
        /// Called when a motif changes. Triggers environment change event.
        /// </summary>
        public void OnMotifChanged(Motif motif)
        {
            // Example: Map motif name or category to environment effect
            if (motif.Name.ToLower().Contains("despair"))
                OnEnvironmentChange?.Invoke("Rain");
            else if (motif.Name.ToLower().Contains("hope"))
                OnEnvironmentChange?.Invoke("Clear");
            // Extend as needed
        }
    }
} 