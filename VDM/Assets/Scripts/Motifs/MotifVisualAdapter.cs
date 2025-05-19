using UnityEngine;

namespace VDM.Motifs
{
    /// <summary>
    /// Adapts motif changes to visual effects (lighting, fog, weather).
    /// </summary>
    public class MotifVisualAdapter : IMotifObserver
    {
        private Color _baseAmbient = Color.gray;
        private float _baseFogDensity = 0.01f;

        public MotifVisualAdapter()
        {
            MotifDispatcher.Instance.Register(this);
        }

        /// <summary>
        /// Called when a motif changes. Adjusts lighting and fog.
        /// </summary>
        public void OnMotifChanged(Motif motif)
        {
            // Example: Map intensity to ambient light and fog
            float t = Mathf.Clamp01(motif.Intensity / 10f);
            RenderSettings.ambientLight = Color.Lerp(_baseAmbient, Color.white, t);
            RenderSettings.fogDensity = Mathf.Lerp(_baseFogDensity, 0.05f, t);
            // TODO: Add weather system hooks if present
        }
    }
} 