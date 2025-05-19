using System;
using System.Collections.Generic;
using UnityEngine;

namespace VDM.NPC
{
    /// <summary>
    /// Handles rumor propagation, mutation, merging, and event notification between NPCs.
    /// </summary>
    public class RumorPropagationSystem : MonoBehaviour
    {
        public float ShareDistance = 5f; // Distance threshold for sharing
        public float MutationRate = 0.1f; // Chance for mutation per share

        // Event: Called when a rumor is propagated
        public event Action<RumorData, int, int> OnRumorPropagated; // (rumor, fromNpcId, toNpcId)

        /// <summary>
        /// Attempt to share a rumor between two NPCs.
        /// </summary>
        public void TryShareRumor(RumorData rumor, int fromNpcId, int toNpcId, Vector2 fromPos, Vector2 toPos)
        {
            if (Vector2.Distance(fromPos, toPos) > ShareDistance)
                return;

            float probability = CalculateShareProbability(rumor, fromNpcId, toNpcId);
            if (UnityEngine.Random.value > probability)
                return;

            var sharedRumor = MaybeMutateRumor(rumor);
            RumorManager.Instance.AddRumor(sharedRumor);
            OnRumorPropagated?.Invoke(sharedRumor, fromNpcId, toNpcId);
        }

        /// <summary>
        /// Calculate the probability of sharing a rumor based on importance and personality (stub).
        /// </summary>
        private float CalculateShareProbability(RumorData rumor, int fromNpcId, int toNpcId)
        {
            // TODO: Use NPC personality and rumor importance
            float baseProb = 0.5f;
            if (rumor.Category == RumorCategory.Danger) baseProb += 0.2f;
            baseProb *= rumor.TruthValue;
            return Mathf.Clamp01(baseProb);
        }

        /// <summary>
        /// Possibly mutate a rumor during propagation.
        /// </summary>
        private RumorData MaybeMutateRumor(RumorData rumor)
        {
            if (UnityEngine.Random.value > MutationRate)
                return rumor;
            // Simple mutation: add "(exaggerated)" to content
            var mutated = new RumorData
            {
                Content = rumor.Content + " (exaggerated)",
                SourceNpcId = rumor.SourceNpcId,
                Timestamp = DateTime.UtcNow,
                TruthValue = Mathf.Clamp01(rumor.TruthValue - 0.1f),
                PropagationRadius = rumor.PropagationRadius,
                BelievabilityScores = new Dictionary<int, float>(rumor.BelievabilityScores),
                Category = rumor.Category
            };
            return mutated;
        }

        /// <summary>
        /// Merge two similar rumors into one.
        /// </summary>
        public RumorData MergeRumors(RumorData a, RumorData b)
        {
            // Simple heuristic: if content is similar, merge
            if (StringSimilarity(a.Content, b.Content) < 0.7f)
                return null;
            var merged = new RumorData
            {
                Content = a.Content, // Prefer a's content
                SourceNpcId = a.SourceNpcId, // Prefer a's source
                Timestamp = DateTime.UtcNow,
                TruthValue = (a.TruthValue + b.TruthValue) / 2f,
                PropagationRadius = Mathf.Max(a.PropagationRadius, b.PropagationRadius),
                BelievabilityScores = new Dictionary<int, float>(a.BelievabilityScores),
                Category = a.Category
            };
            // Merge believability scores
            foreach (var kv in b.BelievabilityScores)
                if (!merged.BelievabilityScores.ContainsKey(kv.Key))
                    merged.BelievabilityScores[kv.Key] = kv.Value;
            return merged;
        }

        /// <summary>
        /// Simple string similarity (Jaccard index on words).
        /// </summary>
        private float StringSimilarity(string a, string b)
        {
            var setA = new HashSet<string>(a.Split(' '));
            var setB = new HashSet<string>(b.Split(' '));
            int intersection = 0;
            foreach (var word in setA)
                if (setB.Contains(word)) intersection++;
            int union = setA.Count + setB.Count - intersection;
            return union == 0 ? 1f : (float)intersection / union;
        }
    }
} 