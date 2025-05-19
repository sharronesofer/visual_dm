using System;

namespace VDM.Motifs
{
    /// <summary>
    /// Adapts motif changes to music system (intensity, theme).
    /// </summary>
    public class MotifMusicAdapter : IMotifObserver
    {
        /// <summary>
        /// Event triggered when music parameters should change.
        /// </summary>
        public event Action<float, string> OnMusicChange; // (intensity, theme)

        public MotifMusicAdapter()
        {
            MotifDispatcher.Instance.Register(this);
        }

        /// <summary>
        /// Called when a motif changes. Triggers music change event.
        /// </summary>
        public void OnMotifChanged(Motif motif)
        {
            OnMusicChange?.Invoke(motif.Intensity, motif.Name);
        }
    }
} 