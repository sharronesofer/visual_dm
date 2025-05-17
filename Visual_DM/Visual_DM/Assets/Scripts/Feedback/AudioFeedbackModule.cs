using System.Collections.Generic;
using UnityEngine;

namespace VisualDM.Feedback
{
    public class AudioFeedbackModule : MonoBehaviour, IFeedbackModule
    {
        private readonly Dictionary<ActionType, List<AudioClip>> soundBank = new Dictionary<ActionType, List<AudioClip>>();
        private readonly List<AudioSource> audioSources = new List<AudioSource>();
        private int maxSimultaneousSounds = 8;
        private int sourceIndex = 0;

        private void Awake()
        {
            // Create audio sources at runtime
            for (int i = 0; i < maxSimultaneousSounds; i++)
            {
                var go = new GameObject($"AudioSource_{i}");
                go.transform.parent = this.transform;
                var src = go.AddComponent<AudioSource>();
                src.spatialBlend = 0f; // 2D by default, can be set to 1f for 3D
                audioSources.Add(src);
            }
            // TODO: Load AudioClips for each ActionType at runtime (from Resources or AssetBundles)
        }

        public void TriggerFeedback(ActionType type, int importance, Vector2 position, FeedbackContext context = null)
        {
            var config = FeedbackManager.Instance?.config;
            if (config != null && !config.AudioEnabled) return;
            var clip = GetRandomClip(type);
            if (clip == null) return;
            var src = audioSources[sourceIndex];
            sourceIndex = (sourceIndex + 1) % maxSimultaneousSounds;
            src.clip = clip;
            src.transform.position = position;
            float baseVolume = Mathf.Lerp(0.5f, 1f, Mathf.Clamp01(importance / 10f));
            if (config != null && !config.AllowLoudSounds)
                baseVolume = Mathf.Min(baseVolume, 0.6f);
            src.volume = baseVolume;
            src.pitch = 1f + Random.Range(-0.1f, 0.1f); // Variation
            src.spatialBlend = 0.5f; // Semi-2D/3D for spatialization
            src.Play();
        }

        private AudioClip GetRandomClip(ActionType type)
        {
            if (!soundBank.TryGetValue(type, out var clips) || clips.Count == 0)
                return null;
            int idx = Random.Range(0, clips.Count);
            return clips[idx];
        }

        // API for loading clips at runtime
        public void RegisterClips(ActionType type, List<AudioClip> clips)
        {
            if (!soundBank.ContainsKey(type))
                soundBank[type] = new List<AudioClip>();
            soundBank[type].AddRange(clips);
        }
    }
} 