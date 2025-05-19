using System;
using System.Collections.Generic;

namespace VDM.NPC
{
    /// <summary>
    /// Provides static methods for calculating and updating believability scores for rumors.
    /// </summary>
    public static class BeliefCalculator
    {
        // Cache: (npcId, rumorId) -> believability
        private static Dictionary<(int, string), float> _cache = new();
        private static float _decayRate = 0.01f; // Decay per hour (configurable)

        /// <summary>
        /// Calculate believability score for a given NPC and rumor.
        /// </summary>
        public static float CalculateBelievability(int npcId, RumorData rumor, float hoursSinceHeard)
        {
            var key = (npcId, rumor.Content); // Use Content as unique ID for now
            if (_cache.TryGetValue(key, out float cached))
                return cached;

            float relationship = GetRelationshipWithSource(npcId, rumor.SourceNpcId); // Stub
            float accuracy = GetHistoricalAccuracy(npcId, rumor.SourceNpcId); // Stub
            float valueAlignment = GetValueAlignment(npcId, rumor); // Stub

            // Weighted sum (tune weights as needed)
            float baseScore = 0.5f * relationship + 0.3f * accuracy + 0.2f * valueAlignment;
            float decayed = ApplyDecay(baseScore, hoursSinceHeard);
            _cache[key] = decayed;
            return decayed;
        }

        /// <summary>
        /// Apply exponential decay to believability over time.
        /// </summary>
        public static float ApplyDecay(float score, float hours)
        {
            return score * (float)Math.Exp(-_decayRate * hours);
        }

        /// <summary>
        /// Invalidate cache for a given rumor and NPC.
        /// </summary>
        public static void InvalidateCache(int npcId, string rumorId)
        {
            _cache.Remove((npcId, rumorId));
        }

        /// <summary>
        /// Stub: Get relationship score between two NPCs (0.0-1.0).
        /// </summary>
        private static float GetRelationshipWithSource(int npcId, int sourceNpcId)
        {
            // TODO: Integrate with Character Relationship System (Task #740)
            return 0.5f; // Placeholder
        }

        /// <summary>
        /// Stub: Get historical accuracy of source's rumors for this NPC (0.0-1.0).
        /// </summary>
        private static float GetHistoricalAccuracy(int npcId, int sourceNpcId)
        {
            // TODO: Track and calculate based on past rumors
            return 0.5f; // Placeholder
        }

        /// <summary>
        /// Stub: Get value alignment between NPC and rumor (0.0-1.0).
        /// </summary>
        private static float GetValueAlignment(int npcId, RumorData rumor)
        {
            // TODO: Integrate with Motif system (Task #741)
            return 0.5f; // Placeholder
        }
    }
} 