using System;

namespace VDM.Motifs
{
    /// <summary>
    /// Adapts motif changes to NPC behavior (e.g., aggression, dialogue mood).
    /// </summary>
    public class MotifNpcBehaviorAdapter : IMotifObserver
    {
        public event Action<float, string> OnNpcBehaviorChanged; // (aggression, mood)

        public MotifNpcBehaviorAdapter()
        {
            MotifDispatcher.Instance.Register(this);
        }

        /// <summary>
        /// Called when a motif changes. Updates NPC behavior parameters.
        /// </summary>
        public void OnMotifChanged(Motif motif)
        {
            // Example: Map motif intensity to aggression, name to mood
            float aggression = motif.Intensity / 10f;
            string mood = motif.Name;
            OnNpcBehaviorChanged?.Invoke(aggression, mood);
        }
    }
} 