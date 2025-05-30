using System.Collections.Generic;
using Newtonsoft.Json;
using System;


namespace VDM.Runtime.Religion.Models
{
    /// <summary>
    /// Religion types as defined in the Development Bible
    /// </summary>
    public enum ReligionType
    {
        Polytheistic = 1,   // Multiple deities, pantheon-based
        Monotheistic = 2,   // Single deity, centralized doctrine
        Animistic = 3,      // Spirits inhabit natural objects/phenomena
        Ancestor = 4,       // Ancestor worship, lineage-based
        Cult = 5,           // Small, secretive, or heretical group
        Syncretic = 6,      // Blends elements from multiple religions
        Custom = 7          // User/system-defined religion type
    }

    /// <summary>
    /// Base DTO for religion data
    /// </summary>
    [Serializable]
    public class ReligionDTO
    {
        [JsonProperty("id")]
        public string Id { get; set; } = string.Empty;

        [JsonProperty("name")]
        public string Name { get; set; } = string.Empty;

        [JsonProperty("description")]
        public string Description { get; set; } = string.Empty;

        [JsonProperty("type")]
        public ReligionType Type { get; set; } = ReligionType.Custom;

        [JsonProperty("tags")]
        public List<string> Tags { get; set; } = new();

        [JsonProperty("tenets")]
        public List<string> Tenets { get; set; } = new();

        [JsonProperty("holy_places")]
        public List<string> HolyPlaces { get; set; } = new();

        [JsonProperty("sacred_texts")]
        public List<string> SacredTexts { get; set; } = new();

        [JsonProperty("region_ids")]
        public List<string> RegionIds { get; set; } = new();

        [JsonProperty("faction_id")]
        public string FactionId { get; set; } = string.Empty;

        [JsonProperty("metadata")]
        public Dictionary<string, object> Metadata { get; set; } = new();

        [JsonProperty("created_at")]
        public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

        [JsonProperty("updated_at")]
        public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;
    }

    /// <summary>
    /// DTO for creating a new religion
    /// </summary>
    [Serializable]
    public class CreateReligionRequestDTO
    {
        [JsonProperty("name")]
        public string Name { get; set; } = string.Empty;

        [JsonProperty("description")]
        public string Description { get; set; } = string.Empty;

        [JsonProperty("type")]
        public ReligionType Type { get; set; } = ReligionType.Custom;

        [JsonProperty("tags")]
        public List<string> Tags { get; set; } = new();

        [JsonProperty("tenets")]
        public List<string> Tenets { get; set; } = new();

        [JsonProperty("holy_places")]
        public List<string> HolyPlaces { get; set; } = new();

        [JsonProperty("sacred_texts")]
        public List<string> SacredTexts { get; set; } = new();

        [JsonProperty("region_ids")]
        public List<string> RegionIds { get; set; } = new();

        [JsonProperty("faction_id")]
        public string FactionId { get; set; } = string.Empty;

        [JsonProperty("metadata")]
        public Dictionary<string, object> Metadata { get; set; } = new();
    }

    /// <summary>
    /// DTO for updating an existing religion
    /// </summary>
    [Serializable]
    public class UpdateReligionRequestDTO
    {
        [JsonProperty("name")]
        public string Name { get; set; } = string.Empty;

        [JsonProperty("description")]
        public string Description { get; set; } = string.Empty;

        [JsonProperty("type")]
        public ReligionType? Type { get; set; }

        [JsonProperty("tags")]
        public List<string> Tags { get; set; } = new();

        [JsonProperty("tenets")]
        public List<string> Tenets { get; set; } = new();

        [JsonProperty("holy_places")]
        public List<string> HolyPlaces { get; set; } = new();

        [JsonProperty("sacred_texts")]
        public List<string> SacredTexts { get; set; } = new();

        [JsonProperty("region_ids")]
        public List<string> RegionIds { get; set; } = new();

        [JsonProperty("faction_id")]
        public string FactionId { get; set; } = string.Empty;

        [JsonProperty("metadata")]
        public Dictionary<string, object> Metadata { get; set; } = new();
    }

    /// <summary>
    /// DTO for religion membership
    /// </summary>
    [Serializable]
    public class ReligionMembershipDTO
    {
        [JsonProperty("id")]
        public string Id { get; set; } = string.Empty;

        [JsonProperty("entity_id")]
        public string EntityId { get; set; } = string.Empty;

        [JsonProperty("religion_id")]
        public string ReligionId { get; set; } = string.Empty;

        [JsonProperty("devotion_level")]
        public float DevotionLevel { get; set; } = 0.5f;

        [JsonProperty("role")]
        public string Role { get; set; } = string.Empty;

        [JsonProperty("joined_at")]
        public DateTime JoinedAt { get; set; } = DateTime.UtcNow;

        [JsonProperty("metadata")]
        public Dictionary<string, object> Metadata { get; set; } = new();
    }

    /// <summary>
    /// Response DTO for religion operations
    /// </summary>
    [Serializable]
    public class ReligionResponseDTO
    {
        [JsonProperty("success")]
        public bool Success { get; set; }

        [JsonProperty("message")]
        public string Message { get; set; } = string.Empty;

        [JsonProperty("religion")]
        public ReligionDTO Religion { get; set; } = new();

        [JsonProperty("errors")]
        public List<string> Errors { get; set; } = new();
    }

    /// <summary>
    /// Response DTO for religion list operations
    /// </summary>
    [Serializable]
    public class ReligionListResponseDTO
    {
        [JsonProperty("success")]
        public bool Success { get; set; }

        [JsonProperty("message")]
        public string Message { get; set; } = string.Empty;

        [JsonProperty("religions")]
        public List<ReligionDTO> Religions { get; set; } = new();

        [JsonProperty("total_count")]
        public int TotalCount { get; set; }

        [JsonProperty("errors")]
        public List<string> Errors { get; set; } = new();
    }
} 