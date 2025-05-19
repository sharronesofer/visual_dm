using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using VisualDM.NPC;

namespace VisualDM.AI
{
    public static class RumorAnalytics
    {
        // Returns a list of NPCs who know a given rumor (not forgotten)
        public static List<NPCBase> GetNPCsKnowingRumor(string rumorId, IEnumerable<NPCBase> allNpcs)
        {
            return allNpcs.Where(npc => npc.KnowsRumor(rumorId)).ToList();
        }

        // Calculates the average distortion for a rumor for a given NPC
        public static float GetRumorDistortionForNPC(string rumorId, NPCBase npc)
        {
            if (!npc.RumorMemories.TryGetValue(rumorId, out var memory)) return 0f;
            if (memory.Transformations == null || memory.Transformations.Count == 0) return 0f;
            return memory.Transformations.Average(t => t.DistortionLevel);
        }

        // Returns the number and percentage of NPCs who know a rumor
        public static (int count, float percent) GetRumorSpread(string rumorId, IEnumerable<NPCBase> allNpcs)
        {
            var total = allNpcs.Count();
            var known = GetNPCsKnowingRumor(rumorId, allNpcs).Count;
            float percent = total > 0 ? (float)known / total : 0f;
            return (known, percent);
        }

        // Logs a summary of rumor spread and distortion for debugging/playtesting
        public static void LogRumorSpread(string rumorId, IEnumerable<NPCBase> allNpcs)
        {
            var npcs = GetNPCsKnowingRumor(rumorId, allNpcs);
            var (count, percent) = GetRumorSpread(rumorId, allNpcs);
            Debug.Log($"Rumor {rumorId}: Known by {count}/{allNpcs.Count()} NPCs ({percent:P1})");
            foreach (var npc in npcs)
            {
                float distortion = GetRumorDistortionForNPC(rumorId, npc);
                Debug.Log($"  NPC {npc.NPCName}: Distortion {distortion:F2}");
            }
        }

        /// <summary>
        /// Approximates the old global rumor state based on distributed NPC knowledge.
        /// States: "new", "spreading", "widespread", "fading", "forgotten"
        /// </summary>
        public static string GetLegacyRumorState(string rumorId, IEnumerable<NPCBase> allNpcs)
        {
            var npcs = allNpcs.ToList();
            var knownNpcs = GetNPCsKnowingRumor(rumorId, npcs);
            int total = npcs.Count;
            int known = knownNpcs.Count;
            float percent = total > 0 ? (float)known / total : 0f;
            float avgMemory = knownNpcs.Count > 0 ? knownNpcs.Average(npc => npc.RumorMemories[rumorId].MemoryStrength) : 0f;
            // Mapping logic:
            // - "new": <10% know it
            // - "spreading": 10-40% know it
            // - "widespread": >40% know it and avgMemory > 0.5
            // - "fading": >40% know it and avgMemory <= 0.5
            // - "forgotten": <5% know it or all memories are forgotten
            if (percent < 0.05f || known == 0) return "forgotten";
            if (percent < 0.10f) return "new";
            if (percent < 0.40f) return "spreading";
            if (percent >= 0.40f && avgMemory > 0.5f) return "widespread";
            if (percent >= 0.40f && avgMemory <= 0.5f) return "fading";
            return "unknown";
        }
    }
}