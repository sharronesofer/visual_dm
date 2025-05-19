using System;
using System.Collections.Generic;
using System.Text.Json.Serialization;

namespace VDM.Motifs
{
    /// <summary>
    /// Enum for motif scope (global, regional, local)
    /// </summary>
    public enum MotifScope { Global, Regional, Local }

    /// <summary>
    /// Enum for motif lifecycle (introduction, development, resolution)
    /// </summary>
    public enum MotifLifecycle { Introduction, Development, Resolution }

    /// <summary>
    /// Enum for motif category (theme, emotion, event, custom)
    /// </summary>
    public enum MotifCategory { Theme, Emotion, Event, Custom }

    /// <summary>
    /// Data model for a narrative motif, matching backend schema.
    /// </summary>
    public class Motif
    {
        /// <summary>Motif unique ID</summary>
        [JsonPropertyName("id")]
        public int? Id { get; set; }

        /// <summary>Name of the motif</summary>
        [JsonPropertyName("name")]
        public string Name { get; set; }

        /// <summary>Description of the motif</summary>
        [JsonPropertyName("description")]
        public string Description { get; set; }

        /// <summary>Intensity (0-10)</summary>
        [JsonPropertyName("intensity")]
        public float Intensity { get; set; } = 1.0f;

        /// <summary>Prevalence (0-10)</summary>
        [JsonPropertyName("prevalence")]
        public float Prevalence { get; set; } = 1.0f;

        /// <summary>Narrative weight (0-10)</summary>
        [JsonPropertyName("narrative_weight")]
        public float NarrativeWeight { get; set; } = 1.0f;

        /// <summary>Tags for motif</summary>
        [JsonPropertyName("tags")]
        public List<string> Tags { get; set; } = new List<string>();

        /// <summary>Motif category</summary>
        [JsonPropertyName("category")]
        public MotifCategory Category { get; set; } = MotifCategory.Theme;

        /// <summary>Motif scope</summary>
        [JsonPropertyName("scope")]
        public MotifScope Scope { get; set; } = MotifScope.Global;

        /// <summary>Motif lifecycle</summary>
        [JsonPropertyName("lifecycle")]
        public MotifLifecycle Lifecycle { get; set; } = MotifLifecycle.Introduction;

        /// <summary>Parent motif ID</summary>
        [JsonPropertyName("parent_id")]
        public int? ParentId { get; set; }

        /// <summary>Children motif IDs</summary>
        [JsonPropertyName("children")]
        public List<int> Children { get; set; } = new List<int>();

        /// <summary>Arbitrary motif-specific data</summary>
        [JsonPropertyName("data")]
        public Dictionary<string, object> Data { get; set; } = new Dictionary<string, object>();

        /// <summary>Created timestamp (ISO8601)</summary>
        [JsonPropertyName("created_at")]
        public DateTime? CreatedAt { get; set; }

        /// <summary>Updated timestamp (ISO8601)</summary>
        [JsonPropertyName("updated_at")]
        public DateTime? UpdatedAt { get; set; }
    }
} 