using System;
using System.Collections.Generic;
using System.Text;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace VDM.NPC
{
    /// <summary>
    /// Enum for rumor categories.
    /// </summary>
    public enum RumorCategory
    {
        Danger,
        Opportunity,
        Gossip,
        Mystery,
        News
    }

    /// <summary>
    /// Represents a single rumor in the NPC Rumor System.
    /// </summary>
    public class RumorData
    {
        /// <summary>Actual rumor text.</summary>
        public string Content { get; set; }
        /// <summary>ID of the NPC who originated the rumor.</summary>
        public int SourceNpcId { get; set; }
        /// <summary>When the rumor was created.</summary>
        public DateTime Timestamp { get; set; }
        /// <summary>How true the rumor is (0.0-1.0).</summary>
        public float TruthValue { get; set; }
        /// <summary>How far the rumor can spread.</summary>
        public float PropagationRadius { get; set; }
        /// <summary>How much each NPC believes the rumor.</summary>
        public Dictionary<int, float> BelievabilityScores { get; set; }
        /// <summary>Type of rumor (Danger, Opportunity, etc.).</summary>
        public RumorCategory Category { get; set; }

        public RumorData()
        {
            BelievabilityScores = new Dictionary<int, float>();
            Timestamp = DateTime.UtcNow;
        }

        /// <summary>
        /// Serialize this rumor to a JSON string.
        /// </summary>
        public string ToJson()
        {
            return JsonSerializer.Serialize(this);
        }

        /// <summary>
        /// Deserialize a rumor from a JSON string.
        /// </summary>
        public static RumorData FromJson(string json)
        {
            return JsonSerializer.Deserialize<RumorData>(json);
        }

        public override string ToString()
        {
            var sb = new StringBuilder();
            sb.AppendLine($"[Rumor] {Content}");
            sb.AppendLine($"Source: {SourceNpcId}, Truth: {TruthValue}, Category: {Category}");
            sb.AppendLine($"Believability: {BelievabilityScores.Count} NPCs");
            return sb.ToString();
        }
    }
} 