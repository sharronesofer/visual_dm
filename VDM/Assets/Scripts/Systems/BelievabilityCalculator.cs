using System;
using VisualDM.Entities;

namespace VisualDM.AI
{
    /// <summary>
    /// Calculates how believable a rumor is to a given NPC, factoring in traits, relationships, and prior knowledge.
    /// </summary>
    public static class BelievabilityCalculator
    {
        /// <summary>
        /// Calculates believability score (0.0-1.0) for a rumor for a specific NPC.
        /// </summary>
        public static float CalculateBelievability(NPCBase npc, Rumor rumor)
        {
            if (npc == null || rumor == null) return 0f;
            // Base: rumor truth value (if known)
            float baseScore = rumor.TruthValue ?? 0.5f;
            // Memory: if NPC already knows rumor, reinforce
            if (npc.RumorMemories.TryGetValue(rumor.CoreContent.GetHashCode().ToString(), out var memory))
            {
                baseScore += memory.MemoryStrength * 0.2f;
                if (memory.IsForgotten) baseScore -= 0.2f;
            }
            // Personality: gullibility, curiosity, skepticism
            float personalityMod = 0f;
            if (npc.Personality != null)
            {
                personalityMod += npc.Personality.Gullibility * 0.3f;
                personalityMod += npc.Personality.Curiosity * 0.1f;
                personalityMod -= npc.Personality.Skepticism * 0.3f;
            }
            // Faction bias: if rumor source is from allied/hostile faction, adjust
            // (Assume rumor.Origin.OriginNpcId is available and NPC has a Faction property)
            float factionMod = 0f;
            if (npc.Faction != null && rumor.Origin != null)
            {
                var sourceNpc = FindNpcById(rumor.Origin.OriginNpcId);
                if (sourceNpc != null && sourceNpc.Faction != null)
                {
                    var rel = VisualDM.Systems.FactionRelationshipManager.Instance.GetRelationship(npc.Faction, sourceNpc.Faction);
                    if (rel == VisualDM.Systems.FactionRelationshipType.Allied) factionMod += 0.1f;
                    if (rel == VisualDM.Systems.FactionRelationshipType.Hostile) factionMod -= 0.2f;
                }
            }
            // Clamp and return
            float score = baseScore + personalityMod + factionMod;
            return Math.Clamp(score, 0f, 1f);
        }

        // Helper to find NPC by ID (assumes NPCName is unique)
        private static NPCBase FindNpcById(string npcId)
        {
            foreach (var npc in UnityEngine.GameObject.FindObjectsOfType<NPCBase>())
            {
                if (npc.NPCName == npcId)
                    return npc;
            }
            return null;
        }
    }
} 