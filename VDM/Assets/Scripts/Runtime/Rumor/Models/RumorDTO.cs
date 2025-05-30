using System.Collections.Generic;
using Newtonsoft.Json;
using System;


namespace VDM.Runtime.Rumor.Models
{
    /// <summary>
    /// Categories for rumor classification, aligned with Development Bible
    /// </summary>
    public enum RumorCategory
    {
        Scandal,        // Gossip about personal or political misdeeds
        Secret,         // Hidden information, often with high stakes
        Prophecy,       // Predictions about future events
        Discovery,      // News of new lands, resources, or inventions
        Catastrophe,    // Warnings of disaster, war, or plague
        Miracle,        // Reports of supernatural or miraculous events
        Betrayal,       // Accusations of treachery or broken trust
        Romance,        // Tales of love affairs or forbidden relationships
        Treasure,       // Hints of hidden wealth or valuable items
        Monster,        // Sightings or rumors of dangerous creatures
        Political,      // Shifts in power, alliances, or intrigue
        Economic,       // Market crashes, booms, or trade opportunities
        Invention,      // New technologies or magical discoveries
        Disappearance,  // Missing persons or unexplained vanishings
        Uprising,       // Rebellions, revolts, or civil unrest
        Other           // Fallback for unclassified rumors
    }

    /// <summary>
    /// Severity levels for rumors
    /// </summary>
    public enum RumorSeverity
    {
        Trivial,    // Minor gossip
        Minor,      // Interesting but not consequential
        Moderate,   // Could affect reputation
        Major,      // Could affect relationships/alliances
        Critical    // Could trigger major events
    }

    /// <summary>
    /// Represents a specific variant/mutation of a rumor
    /// </summary>
    [Serializable]
    public class RumorVariantDTO
    {
        [JsonProperty("id")]
        public string Id { get; set; } = string.Empty;

        [JsonProperty("content")]
        public string Content { get; set; } = string.Empty;

        [JsonProperty("created_at")]
        public string CreatedAt { get; set; } = string.Empty;

        [JsonProperty("parent_variant_id")]
        public string ParentVariantId { get; set; } = string.Empty;

        [JsonProperty("entity_id")]
        public string EntityId { get; set; } = string.Empty;

        [JsonProperty("mutation_metadata")]
        public Dictionary<string, object> MutationMetadata { get; set; } = new Dictionary<string, object>();
    }

    /// <summary>
    /// Tracks the spread of a rumor to an entity
    /// </summary>
    [Serializable]
    public class RumorSpreadDTO
    {
        [JsonProperty("entity_id")]
        public string EntityId { get; set; } = string.Empty;

        [JsonProperty("variant_id")]
        public string VariantId { get; set; } = string.Empty;

        [JsonProperty("heard_from_entity_id")]
        public string HeardFromEntityId { get; set; } = string.Empty;

        [JsonProperty("believability")]
        public float Believability { get; set; } = 0.5f;

        [JsonProperty("heard_at")]
        public string HeardAt { get; set; } = string.Empty;

        [JsonProperty("last_reinforced_at")]
        public string LastReinforcedAt { get; set; } = string.Empty;
    }

    /// <summary>
    /// Main rumor data transfer object
    /// </summary>
    [Serializable]
    public class RumorDTO
    {
        [JsonProperty("id")]
        public string Id { get; set; } = string.Empty;

        [JsonProperty("created_at")]
        public string CreatedAt { get; set; } = string.Empty;

        [JsonProperty("originator_id")]
        public string OriginatorId { get; set; } = string.Empty;

        [JsonProperty("original_content")]
        public string OriginalContent { get; set; } = string.Empty;

        [JsonProperty("categories")]
        public List<string> Categories { get; set; } = new List<string>();

        [JsonProperty("severity")]
        public string Severity { get; set; } = "minor";

        [JsonProperty("truth_value")]
        public float TruthValue { get; set; } = 0.5f;

        [JsonProperty("variants")]
        public List<RumorVariantDTO> Variants { get; set; } = new List<RumorVariantDTO>();

        [JsonProperty("spread")]
        public List<RumorSpreadDTO> Spread { get; set; } = new List<RumorSpreadDTO>();
    }

    /// <summary>
    /// Request for creating a new rumor
    /// </summary>
    [Serializable]
    public class CreateRumorRequestDTO
    {
        [JsonProperty("originator_id")]
        public string OriginatorId { get; set; } = string.Empty;

        [JsonProperty("content")]
        public string Content { get; set; } = string.Empty;

        [JsonProperty("categories")]
        public List<string> Categories { get; set; } = new List<string>();

        [JsonProperty("severity")]
        public string Severity { get; set; } = "minor";

        [JsonProperty("truth_value")]
        public float TruthValue { get; set; } = 0.5f;
    }

    /// <summary>
    /// Request for spreading a rumor
    /// </summary>
    [Serializable]
    public class SpreadRumorRequestDTO
    {
        [JsonProperty("rumor_id")]
        public string RumorId { get; set; } = string.Empty;

        [JsonProperty("from_entity_id")]
        public string FromEntityId { get; set; } = string.Empty;

        [JsonProperty("to_entity_id")]
        public string ToEntityId { get; set; } = string.Empty;

        [JsonProperty("mutation_probability")]
        public float MutationProbability { get; set; } = 0.2f;

        [JsonProperty("relationship_factor")]
        public float? RelationshipFactor { get; set; }

        [JsonProperty("receiver_bias_factor")]
        public float? ReceiverBiasFactor { get; set; }
    }

    /// <summary>
    /// Response for rumor operations
    /// </summary>
    [Serializable]
    public class RumorOperationResponseDTO
    {
        [JsonProperty("success")]
        public bool Success { get; set; }

        [JsonProperty("message")]
        public string Message { get; set; } = string.Empty;

        [JsonProperty("rumor_id")]
        public string RumorId { get; set; } = string.Empty;

        [JsonProperty("data")]
        public Dictionary<string, object> Data { get; set; } = new Dictionary<string, object>();
    }

    /// <summary>
    /// Response for listing rumors
    /// </summary>
    [Serializable]
    public class RumorListResponseDTO
    {
        [JsonProperty("rumors")]
        public List<RumorDTO> Rumors { get; set; } = new List<RumorDTO>();

        [JsonProperty("count")]
        public int Count { get; set; }

        [JsonProperty("total")]
        public int? Total { get; set; }
    }

    /// <summary>
    /// Response for entity-specific rumors
    /// </summary>
    [Serializable]
    public class EntityRumorsResponseDTO
    {
        [JsonProperty("entity_id")]
        public string EntityId { get; set; } = string.Empty;

        [JsonProperty("rumors")]
        public List<RumorDTO> Rumors { get; set; } = new List<RumorDTO>();

        [JsonProperty("count")]
        public int Count { get; set; }
    }

    /// <summary>
    /// Summary view of a rumor
    /// </summary>
    [Serializable]
    public class RumorSummaryDTO
    {
        [JsonProperty("id")]
        public string Id { get; set; } = string.Empty;

        [JsonProperty("content")]
        public string Content { get; set; } = string.Empty;

        [JsonProperty("categories")]
        public List<string> Categories { get; set; } = new List<string>();

        [JsonProperty("severity")]
        public string Severity { get; set; } = string.Empty;

        [JsonProperty("believability")]
        public float? Believability { get; set; }

        [JsonProperty("variant_count")]
        public int VariantCount { get; set; }

        [JsonProperty("spread_count")]
        public int SpreadCount { get; set; }
    }
} 