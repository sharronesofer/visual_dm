using System.Collections.Generic;
using UnityEngine;

namespace VisualDM.World
{
    /// <summary>
    /// Minimal interface for NPC Memory System.
    /// </summary>
    public interface INPCMemory
    {
        void AddRumor(string npcId, Dictionary<string, string> rumorDetails);
        List<Dictionary<string, string>> GetRumors(string npcId);
    }

    /// <summary>
    /// Minimal interface for NPC Conversation System.
    /// </summary>
    public interface INPCConversation
    {
        void AddRumorToConversation(string npcId, Dictionary<string, string> rumorDetails);
        List<string> GetRumorLines(string npcId);
    }

    /// <summary>
    /// Minimal interface for Social Check System.
    /// </summary>
    public interface ISocialCheck
    {
        bool CheckRumorKnowledge(string npcId, string rumorKey);
    }

    /// <summary>
    /// Integrates world event/rumor system with NPC Memory, Conversation, and Social Check systems.
    /// </summary>
    public static class WorldRumorIntegration
    {
        public static INPCMemory NpcMemorySystem;
        public static INPCConversation NpcConversationSystem;
        public static ISocialCheck SocialCheckSystem;

        /// <summary>
        /// Pushes a new rumor into the NPC Memory System.
        /// </summary>
        public static void PushRumorToMemory(string npcId, Dictionary<string, string> rumorDetails)
        {
            NpcMemorySystem?.AddRumor(npcId, rumorDetails);
        }

        /// <summary>
        /// Retrieves rumors for use in NPC conversations.
        /// </summary>
        public static List<string> GetRumorsForConversation(string npcId)
        {
            var rumors = NpcMemorySystem?.GetRumors(npcId) ?? new List<Dictionary<string, string>>();
            var lines = new List<string>();
            foreach (var rumor in rumors)
            {
                if (NpcConversationSystem != null)
                {
                    NpcConversationSystem.AddRumorToConversation(npcId, rumor);
                    lines.AddRange(NpcConversationSystem.GetRumorLines(npcId));
                }
                else
                {
                    // Fallback: simple stringification
                    lines.Add(RumorToString(rumor));
                }
            }
            return lines;
        }

        /// <summary>
        /// Interface for social checks to query rumor knowledge.
        /// </summary>
        public static bool HasRumorKnowledge(string npcId, string rumorKey)
        {
            return SocialCheckSystem?.CheckRumorKnowledge(npcId, rumorKey) ?? false;
        }

        private static string RumorToString(Dictionary<string, string> rumor)
        {
            if (rumor == null) return "";
            var parts = new List<string>();
            foreach (var kvp in rumor)
            {
                parts.Add($"{kvp.Key}: {kvp.Value}");
            }
            return string.Join(", ", parts);
        }
    }
}