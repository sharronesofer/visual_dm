using System;
using System.Collections.Generic;
using UnityEngine;

namespace VDM.NPC.MotifSystem
{
    public class MotifBehaviorModifier : MonoBehaviour
    {
        [Serializable]
        public class MotifBehaviorTemplate
        {
            public string MotifName;
            public string AnimationOverride;
            public string RoutineOverride;
            public string InteractionOverride;
            public float IntensityMultiplier = 1f;
            // Extend as needed for more behavior types
        }

        public List<MotifBehaviorTemplate> BehaviorTemplates = new List<MotifBehaviorTemplate>();
        private Dictionary<string, MotifBehaviorTemplate> templateDict;
        private List<Motif> currentMotifs = new List<Motif>();
        private float motifCheckInterval = 1.0f;
        private float motifCheckTimer = 0f;

        void Awake()
        {
            templateDict = new Dictionary<string, MotifBehaviorTemplate>();
            foreach (var t in BehaviorTemplates)
            {
                if (!string.IsNullOrEmpty(t.MotifName))
                    templateDict[t.MotifName] = t;
            }
            MotifManager.Instance.MotifsChanged += OnMotifsChanged;
        }

        void OnDestroy()
        {
            if (MotifManager.Instance != null)
                MotifManager.Instance.MotifsChanged -= OnMotifsChanged;
        }

        void Update()
        {
            motifCheckTimer += Time.deltaTime;
            if (motifCheckTimer >= motifCheckInterval)
            {
                motifCheckTimer = 0f;
                UpdateMotifEffects();
            }
        }

        void OnMotifsChanged()
        {
            UpdateMotifEffects();
        }

        void UpdateMotifEffects()
        {
            var motifs = MotifManager.Instance.GetMotifsAffectingLocation(transform.position);
            currentMotifs = motifs;
            ApplyMotifBehaviors();
        }

        void ApplyMotifBehaviors()
        {
            if (currentMotifs.Count == 0)
            {
                ResetToBaseBehavior();
                return;
            }

            // Priority resolution: pick highest-priority motif, or blend
            Motif highest = null;
            foreach (var m in currentMotifs)
            {
                if (highest == null || m.Priority > highest.Priority)
                    highest = m;
            }

            if (highest != null && templateDict.TryGetValue(highest.Name, out var template))
            {
                ApplyTemplate(template, highest.Intensity);
            }
            else
            {
                ResetToBaseBehavior();
            }
        }

        void ApplyTemplate(MotifBehaviorTemplate template, float motifIntensity)
        {
            // Example: override animation, routine, interaction
            // Replace with actual calls to your NPC systems
            if (!string.IsNullOrEmpty(template.AnimationOverride))
            {
                // e.g., GetComponent<NPCAnimator>().SetAnimation(template.AnimationOverride);
            }
            if (!string.IsNullOrEmpty(template.RoutineOverride))
            {
                // e.g., GetComponent<NPCRoutine>().SetRoutine(template.RoutineOverride);
            }
            if (!string.IsNullOrEmpty(template.InteractionOverride))
            {
                // e.g., GetComponent<NPCInteraction>().SetInteraction(template.InteractionOverride);
            }
            // Apply intensity multiplier if needed
        }

        void ResetToBaseBehavior()
        {
            // Reset to default NPC behavior (remove motif overrides)
            // e.g., GetComponent<NPCAnimator>().ResetAnimation();
            // e.g., GetComponent<NPCRoutine>().ResetRoutine();
            // e.g., GetComponent<NPCInteraction>().ResetInteraction();
        }
    }
} 