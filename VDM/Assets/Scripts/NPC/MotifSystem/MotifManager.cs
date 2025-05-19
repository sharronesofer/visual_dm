using System;
using System.Collections.Generic;
using System.IO;
using UnityEngine;

namespace VDM.NPC.MotifSystem
{
    public class MotifManager : MonoBehaviour
    {
        private static MotifManager _instance;
        public static MotifManager Instance
        {
            get
            {
                if (_instance == null)
                {
                    var obj = new GameObject("MotifManager");
                    _instance = obj.AddComponent<MotifManager>();
                    DontDestroyOnLoad(obj);
                }
                return _instance;
            }
        }

        private List<Motif> activeMotifs = new List<Motif>();
        public event Action MotifsChanged;

        public IReadOnlyList<Motif> ActiveMotifs => activeMotifs.AsReadOnly();

        // Event-driven motif change support
        public event Action<string, Motif> MotifEventTriggered; // eventType, motif

        // For propagation/decay
        private float motifUpdateInterval = 1.0f;
        private float motifUpdateTimer = 0f;

        void Update()
        {
            motifUpdateTimer += Time.deltaTime;
            if (motifUpdateTimer >= motifUpdateInterval)
            {
                motifUpdateTimer = 0f;
                ProcessMotifPropagationAndDecay();
            }
        }

        public void AddMotif(Motif motif)
        {
            activeMotifs.Add(motif);
            MotifsChanged?.Invoke();
        }

        public void RemoveMotif(string motifName)
        {
            activeMotifs.RemoveAll(m => m.Name == motifName);
            MotifsChanged?.Invoke();
        }

        public void ModifyMotif(Motif motif)
        {
            for (int i = 0; i < activeMotifs.Count; i++)
            {
                if (activeMotifs[i].Name == motif.Name)
                {
                    activeMotifs[i] = motif;
                    MotifsChanged?.Invoke();
                    return;
                }
            }
        }

        public List<Motif> GetActiveMotifs()
        {
            activeMotifs.RemoveAll(m => !m.IsActive());
            return new List<Motif>(activeMotifs);
        }

        public List<Motif> GetMotifsAffectingLocation(Vector2 location)
        {
            var result = new List<Motif>();
            foreach (var motif in GetActiveMotifs())
            {
                if (motif.IsLocationAffected(location))
                    result.Add(motif);
            }
            return result;
        }

        private string SavePath => Path.Combine(Application.persistentDataPath, "motifs.json");

        [Serializable]
        private class MotifListWrapper { public List<Motif> motifs; }

        public void SaveMotifs()
        {
            var wrapper = new MotifListWrapper { motifs = activeMotifs };
            var json = JsonUtility.ToJson(wrapper);
            File.WriteAllText(SavePath, json);
        }

        public void LoadMotifs()
        {
            if (!File.Exists(SavePath)) return;
            var json = File.ReadAllText(SavePath);
            var wrapper = JsonUtility.FromJson<MotifListWrapper>(json);
            activeMotifs = wrapper?.motifs ?? new List<Motif>();
            MotifsChanged?.Invoke();
        }

        // Event trigger API
        public void TriggerMotifEvent(string eventType, Motif motif)
        {
            switch (eventType)
            {
                case "add":
                    AddMotif(motif);
                    break;
                case "remove":
                    RemoveMotif(motif.Name);
                    break;
                case "modify":
                    ModifyMotif(motif);
                    break;
                default:
                    Debug.LogWarning($"Unknown motif event type: {eventType}");
                    break;
            }
            MotifEventTriggered?.Invoke(eventType, motif);
        }

        // Motif propagation and decay logic
        private void ProcessMotifPropagationAndDecay()
        {
            bool changed = false;
            foreach (var motif in activeMotifs)
            {
                // Propagation: expand radius if motif supports it (e.g., tag "propagate")
                if (motif.Tags != null && motif.Tags.Contains("propagate"))
                {
                    float maxRadius = 100f; // Example max
                    float propagationRate = 1f; // units per interval
                    if (motif.Radius < maxRadius)
                    {
                        motif.GetType().GetProperty("Radius")?.SetValue(motif, Mathf.Min(motif.Radius + propagationRate, maxRadius));
                        changed = true;
                        Debug.Log($"[MotifManager] Propagated motif '{motif.Name}' to radius {motif.Radius}");
                    }
                }
                // Decay: shrink radius or expire motif if tag "decay"
                if (motif.Tags != null && motif.Tags.Contains("decay"))
                {
                    float decayRate = 1f;
                    if (motif.Radius > 0)
                    {
                        motif.GetType().GetProperty("Radius")?.SetValue(motif, Mathf.Max(motif.Radius - decayRate, 0));
                        changed = true;
                        Debug.Log($"[MotifManager] Decayed motif '{motif.Name}' to radius {motif.Radius}");
                    }
                }
            }
            // Remove expired motifs
            int before = activeMotifs.Count;
            activeMotifs.RemoveAll(m => !m.IsActive() || (m.Tags != null && m.Tags.Contains("decay") && m.Radius <= 0));
            if (changed || before != activeMotifs.Count)
                MotifsChanged?.Invoke();
        }

        // Debug/test methods for runtime validation
        public void DebugTriggerMotif(string name, float intensity, MotifScope scope, float duration, int priority, List<string> tags, Vector2 center, float radius)
        {
            var motif = new Motif(name, intensity, scope, duration, priority, tags, DateTime.UtcNow, center, radius);
            TriggerMotifEvent("add", motif);
            Debug.Log($"[MotifManager] Debug motif '{name}' triggered at {center} with radius {radius}");
        }

        public void DebugRemoveMotif(string name)
        {
            TriggerMotifEvent("remove", new Motif(name, 0, MotifScope.Global, 0, 0, null, DateTime.UtcNow, Vector2.zero, 0));
            Debug.Log($"[MotifManager] Debug motif '{name}' removed");
        }
    }
} 