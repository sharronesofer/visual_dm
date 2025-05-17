using System.Collections.Generic;
using UnityEngine;

namespace VisualDM.World
{
    /// <summary>
    /// Provides methods to distort rumor details based on distance and NPC traits.
    /// </summary>
    public static class InformationDistortionSystem
    {
        /// <summary>
        /// Distorts rumor details based on accuracy and NPC traits.
        /// </summary>
        /// <param name="details">Original rumor details (key: detail name, value: true value)</param>
        /// <param name="accuracy">Accuracy value (0-1), lower means more distortion</param>
        /// <param name="npcTraits">List of NPC traits (e.g., "observant", "gossip-prone")</param>
        /// <returns>Distorted details dictionary</returns>
        public static Dictionary<string, string> DistortRumorDetails(Dictionary<string, string> details, float accuracy, List<string> npcTraits)
        {
            var distorted = new Dictionary<string, string>();
            float traitModifier = 1f;
            if (npcTraits != null)
            {
                if (npcTraits.Contains("observant")) traitModifier += 0.2f;
                if (npcTraits.Contains("gossip-prone")) traitModifier -= 0.2f;
            }
            float effectiveAccuracy = Mathf.Clamp01(accuracy * traitModifier);

            foreach (var kvp in details)
            {
                // Always preserve core truth for event type
                if (kvp.Key == "EventType")
                {
                    distorted[kvp.Key] = kvp.Value;
                    continue;
                }
                // Decide distortion type
                float roll = UnityEngine.Random.value;
                if (roll < effectiveAccuracy)
                {
                    distorted[kvp.Key] = kvp.Value; // True detail
                }
                else if (roll < effectiveAccuracy + 0.3f)
                {
                    distorted[kvp.Key] = Exaggerate(kvp.Value); // Exaggeration
                }
                else if (roll < effectiveAccuracy + 0.6f)
                {
                    distorted[kvp.Key] = Omit(kvp.Value); // Omission
                }
                else
                {
                    distorted[kvp.Key] = Confuse(kvp.Value); // Confusion
                }
            }
            return distorted;
        }

        // Example distortion: Exaggeration
        private static string Exaggerate(string value)
        {
            // Simple example: add "very" or "huge" to the value
            if (string.IsNullOrEmpty(value)) return value;
            return "Very " + value;
        }

        // Example distortion: Omission
        private static string Omit(string value)
        {
            // Omit the detail entirely
            return "(Omitted)";
        }

        // Example distortion: Confusion
        private static string Confuse(string value)
        {
            // Replace with a generic or incorrect value
            if (string.IsNullOrEmpty(value)) return "(Confused)";
            return "Confused " + value;
        }
    }
}