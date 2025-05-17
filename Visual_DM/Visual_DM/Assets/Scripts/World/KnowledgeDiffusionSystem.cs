using System;
using System.Collections.Generic;
using UnityEngine;

namespace VisualDM.World
{
    /// <summary>
    /// Represents the result of rumor knowledge for an NPC about a world event.
    /// </summary>
    public class RumorKnowledgeResult
    {
        public float Accuracy; // 0-1, how accurate the knowledge is
        public Dictionary<string, string> Details; // key: detail name, value: known or distorted value
        public RumorKnowledgeResult(float accuracy, Dictionary<string, string> details)
        {
            Accuracy = accuracy;
            Details = details;
        }
    }

    /// <summary>
    /// Provides spatial awareness and knowledge diffusion logic for rumors.
    /// </summary>
    public static class KnowledgeDiffusionSystem
    {
        // Simple cache for rumor knowledge results
        private class CacheEntry
        {
            public RumorKnowledgeResult Result;
            public float ExpiryTime;
        }
        private static Dictionary<(string, WorldEvent), CacheEntry> rumorCache = new Dictionary<(string, WorldEvent), CacheEntry>();
        public static float CacheTTLSeconds { get; set; } = 5f;

        /// <summary>
        /// Returns the distance between an NPC and a world event location.
        /// </summary>
        public static float GetDistanceToEvent(string npcId, WorldEvent worldEvent)
        {
            Vector2 npcPos = NPCPositionRegistry.GetNPCPosition(npcId);
            return Vector2.Distance(npcPos, worldEvent.Location);
        }

        /// <summary>
        /// Returns an accuracy value (0-1) based on distance. Uses exponential decay.
        /// </summary>
        public static float GetAccuracyByDistance(float distance, float maxDistance = 50f)
        {
            // Example: accuracy = e^(-distance / maxDistance)
            return Mathf.Exp(-distance / maxDistance);
        }

        /// <summary>
        /// Determines what details an NPC knows about a world event, based on proximity. Uses cache if available.
        /// </summary>
        public static RumorKnowledgeResult GetRumorKnowledgeForNPC(string npcId, WorldEvent worldEvent)
        {
            var key = (npcId, worldEvent);
            float now = Time.time;
            if (rumorCache.TryGetValue(key, out var entry))
            {
                if (entry.ExpiryTime > now)
                {
                    return entry.Result;
                }
                else
                {
                    rumorCache.Remove(key);
                }
            }
            float distance = GetDistanceToEvent(npcId, worldEvent);
            float accuracy = GetAccuracyByDistance(distance);
            var details = new Dictionary<string, string>();

            // Example: For each involved entity, probabilistically determine knowledge
            foreach (var entity in worldEvent.InvolvedEntities)
            {
                if (UnityEngine.Random.value < accuracy)
                {
                    details[entity] = entity; // Knows the true detail
                }
                else if (UnityEngine.Random.value < 0.5f)
                {
                    details[entity] = "Distorted"; // Knows a distorted version
                }
                else
                {
                    details[entity] = "Unknown"; // Knows nothing
                }
            }
            // Add event type and description similarly
            if (UnityEngine.Random.value < accuracy)
                details["EventType"] = worldEvent.Type.ToString();
            else
                details["EventType"] = "Distorted";

            if (UnityEngine.Random.value < accuracy)
                details["Description"] = worldEvent.Description;
            else
                details["Description"] = "Distorted rumor";

            var result = new RumorKnowledgeResult(accuracy, details);
            rumorCache[key] = new CacheEntry { Result = result, ExpiryTime = now + CacheTTLSeconds };
            return result;
        }
    }

    /// <summary>
    /// Provides runtime access to NPC positions by ID. Should be updated by NPC controllers.
    /// </summary>
    public static class NPCPositionRegistry
    {
        private static Dictionary<string, Vector2> npcPositions = new Dictionary<string, Vector2>();

        /// <summary>
        /// Registers or updates the position of an NPC.
        /// </summary>
        public static void SetNPCPosition(string npcId, Vector2 position)
        {
            npcPositions[npcId] = position;
        }

        /// <summary>
        /// Gets the current position of an NPC by ID.
        /// </summary>
        public static Vector2 GetNPCPosition(string npcId)
        {
            if (npcPositions.TryGetValue(npcId, out var pos))
                return pos;
            return Vector2.zero; // Default if not found
        }
    }
}