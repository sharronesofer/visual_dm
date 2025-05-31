using System.Collections.Generic;
using System;
using UnityEngine;
using Newtonsoft.Json;

namespace VDM.Systems.Religion.Models
{
    /// <summary>
    /// Data Transfer Objects and Models for Religion system
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
        public ReligionType Type { get; set; } = ReligionType.Monotheistic;

        [JsonProperty("origin_story")]
        public string OriginStory { get; set; } = string.Empty;

        [JsonProperty("core_beliefs")]
        public List<string> CoreBeliefs { get; set; } = new List<string>();

        [JsonProperty("practices")]
        public List<string> Practices { get; set; } = new List<string>();

        [JsonProperty("clergy_structure")]
        public string ClergyStructure { get; set; } = string.Empty;

        [JsonProperty("holy_texts")]
        public List<string> HolyTexts { get; set; } = new List<string>();

        [JsonProperty("deities")]
        public List<DeityDTO> Deities { get; set; } = new List<DeityDTO>();

        [JsonProperty("followers_count")]
        public int FollowersCount { get; set; } = 0;

        [JsonProperty("influence_regions")]
        public List<string> InfluenceRegions { get; set; } = new List<string>();

        [JsonProperty("status")]
        public string Status { get; set; } = "active";

        [JsonProperty("created_at")]
        public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

        [JsonProperty("updated_at")]
        public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;
    }

    [Serializable]
    public class DeityDTO
    {
        [JsonProperty("id")]
        public string Id { get; set; } = string.Empty;

        [JsonProperty("name")]
        public string Name { get; set; } = string.Empty;

        [JsonProperty("description")]
        public string Description { get; set; } = string.Empty;

        [JsonProperty("domain")]
        public string Domain { get; set; } = string.Empty;

        [JsonProperty("alignment")]
        public string Alignment { get; set; } = string.Empty;

        [JsonProperty("symbols")]
        public List<string> Symbols { get; set; } = new List<string>();

        [JsonProperty("holy_days")]
        public List<string> HolyDays { get; set; } = new List<string>();

        [JsonProperty("powers")]
        public List<string> Powers { get; set; } = new List<string>();

        [JsonProperty("worshiper_count")]
        public int WorshiperCount { get; set; } = 0;

        [JsonProperty("religion_id")]
        public string ReligionId { get; set; } = string.Empty;
    }

    [Serializable]
    public class ReligiousPracticeDTO
    {
        [JsonProperty("id")]
        public string Id { get; set; } = string.Empty;

        [JsonProperty("name")]
        public string Name { get; set; } = string.Empty;

        [JsonProperty("description")]
        public string Description { get; set; } = string.Empty;

        [JsonProperty("frequency")]
        public string Frequency { get; set; } = string.Empty;

        [JsonProperty("participants")]
        public int Participants { get; set; } = 0;

        [JsonProperty("location_type")]
        public string LocationType { get; set; } = string.Empty;

        [JsonProperty("required_items")]
        public List<string> RequiredItems { get; set; } = new List<string>();

        [JsonProperty("religion_id")]
        public string ReligionId { get; set; } = string.Empty;
    }

    [Serializable]
    public class ReligiousEventDTO
    {
        [JsonProperty("id")]
        public string Id { get; set; } = string.Empty;

        [JsonProperty("name")]
        public string Name { get; set; } = string.Empty;

        [JsonProperty("description")]
        public string Description { get; set; } = string.Empty;

        [JsonProperty("event_type")]
        public string EventType { get; set; } = string.Empty;

        [JsonProperty("date")]
        public DateTime Date { get; set; } = DateTime.UtcNow;

        [JsonProperty("duration")]
        public int Duration { get; set; } = 1;

        [JsonProperty("location")]
        public string Location { get; set; } = string.Empty;

        [JsonProperty("participants")]
        public List<string> Participants { get; set; } = new List<string>();

        [JsonProperty("religion_id")]
        public string ReligionId { get; set; } = string.Empty;
    }

    [Serializable]
    public class ReligiousInfluenceDTO
    {
        [JsonProperty("id")]
        public string Id { get; set; } = string.Empty;

        [JsonProperty("religion_id")]
        public string ReligionId { get; set; } = string.Empty;

        [JsonProperty("region_id")]
        public string RegionId { get; set; } = string.Empty;

        [JsonProperty("influence_level")]
        public float InfluenceLevel { get; set; } = 0f;

        [JsonProperty("follower_count")]
        public int FollowerCount { get; set; } = 0;

        [JsonProperty("temples_count")]
        public int TemplesCount { get; set; } = 0;

        [JsonProperty("clergy_count")]
        public int ClergyCount { get; set; } = 0;

        [JsonProperty("last_updated")]
        public DateTime LastUpdated { get; set; } = DateTime.UtcNow;
    }

    // Request DTOs
    [Serializable]
    public class CreateReligiousPracticeRequestDTO
    {
        [JsonProperty("name")]
        public string Name { get; set; } = string.Empty;

        [JsonProperty("description")]
        public string Description { get; set; } = string.Empty;

        [JsonProperty("frequency")]
        public string Frequency { get; set; } = string.Empty;

        [JsonProperty("participants")]
        public int Participants { get; set; } = 0;

        [JsonProperty("location_type")]
        public string LocationType { get; set; } = string.Empty;

        [JsonProperty("required_items")]
        public List<string> RequiredItems { get; set; } = new List<string>();

        [JsonProperty("religion_id")]
        public string ReligionId { get; set; } = string.Empty;
    }

    [Serializable]
    public class CreateDeityRequestDTO
    {
        [JsonProperty("name")]
        public string Name { get; set; } = string.Empty;

        [JsonProperty("description")]
        public string Description { get; set; } = string.Empty;

        [JsonProperty("domain")]
        public string Domain { get; set; } = string.Empty;

        [JsonProperty("alignment")]
        public string Alignment { get; set; } = string.Empty;

        [JsonProperty("symbols")]
        public List<string> Symbols { get; set; } = new List<string>();

        [JsonProperty("holy_days")]
        public List<string> HolyDays { get; set; } = new List<string>();

        [JsonProperty("powers")]
        public List<string> Powers { get; set; } = new List<string>();

        [JsonProperty("religion_id")]
        public string ReligionId { get; set; } = string.Empty;
    }

    [Serializable]
    public class CreateReligiousEventRequestDTO
    {
        [JsonProperty("name")]
        public string Name { get; set; } = string.Empty;

        [JsonProperty("description")]
        public string Description { get; set; } = string.Empty;

        [JsonProperty("event_type")]
        public string EventType { get; set; } = string.Empty;

        [JsonProperty("date")]
        public DateTime Date { get; set; } = DateTime.UtcNow;

        [JsonProperty("duration")]
        public int Duration { get; set; } = 1;

        [JsonProperty("location")]
        public string Location { get; set; } = string.Empty;

        [JsonProperty("participants")]
        public List<string> Participants { get; set; } = new List<string>();

        [JsonProperty("religion_id")]
        public string ReligionId { get; set; } = string.Empty;
    }

    [Serializable]
    public class UpdateReligiousInfluenceRequestDTO
    {
        [JsonProperty("influence_level")]
        public float InfluenceLevel { get; set; } = 0f;

        [JsonProperty("follower_count")]
        public int FollowerCount { get; set; } = 0;

        [JsonProperty("temples_count")]
        public int TemplesCount { get; set; } = 0;

        [JsonProperty("clergy_count")]
        public int ClergyCount { get; set; } = 0;
    }

    // Response DTOs
    [Serializable]
    public class ReligionListResponseDTO
    {
        [JsonProperty("religions")]
        public List<ReligionDTO> Religions { get; set; } = new List<ReligionDTO>();

        [JsonProperty("total_count")]
        public int TotalCount { get; set; } = 0;

        [JsonProperty("page")]
        public int Page { get; set; } = 1;

        [JsonProperty("page_size")]
        public int PageSize { get; set; } = 50;
    }

    /// <summary>
    /// Religion membership data
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
        public string Role { get; set; } = "follower";

        [JsonProperty("joined_date")]
        public DateTime JoinedDate { get; set; } = DateTime.UtcNow;

        [JsonProperty("status")]
        public string Status { get; set; } = "active";
    }

    /// <summary>
    /// Create religion request DTO
    /// </summary>
    [Serializable]
    public class CreateReligionRequestDTO
    {
        [JsonProperty("name")]
        public string Name { get; set; } = string.Empty;

        [JsonProperty("description")]
        public string Description { get; set; } = string.Empty;

        [JsonProperty("type")]
        public ReligionType Type { get; set; } = ReligionType.Monotheistic;

        [JsonProperty("origin_story")]
        public string OriginStory { get; set; } = string.Empty;

        [JsonProperty("core_beliefs")]
        public List<string> CoreBeliefs { get; set; } = new List<string>();

        [JsonProperty("tenets")]
        public List<string> Tenets { get; set; } = new List<string>();

        [JsonProperty("practices")]
        public List<string> Practices { get; set; } = new List<string>();

        [JsonProperty("holy_places")]
        public List<string> HolyPlaces { get; set; } = new List<string>();

        [JsonProperty("sacred_texts")]
        public List<string> SacredTexts { get; set; } = new List<string>();

        [JsonProperty("clergy_structure")]
        public string ClergyStructure { get; set; } = string.Empty;
    }

    /// <summary>
    /// Update religion request DTO
    /// </summary>
    [Serializable]
    public class UpdateReligionRequestDTO
    {
        [JsonProperty("name")]
        public string Name { get; set; } = string.Empty;

        [JsonProperty("description")]
        public string Description { get; set; } = string.Empty;

        [JsonProperty("origin_story")]
        public string OriginStory { get; set; } = string.Empty;

        [JsonProperty("core_beliefs")]
        public List<string> CoreBeliefs { get; set; } = new List<string>();

        [JsonProperty("tenets")]
        public List<string> Tenets { get; set; } = new List<string>();

        [JsonProperty("practices")]
        public List<string> Practices { get; set; } = new List<string>();

        [JsonProperty("holy_places")]
        public List<string> HolyPlaces { get; set; } = new List<string>();

        [JsonProperty("sacred_texts")]
        public List<string> SacredTexts { get; set; } = new List<string>();

        [JsonProperty("clergy_structure")]
        public string ClergyStructure { get; set; } = string.Empty;

        [JsonProperty("status")]
        public string Status { get; set; } = string.Empty;
    }

    /// <summary>
    /// Religion type enumeration
    /// </summary>
    public enum ReligionType
    {
        Monotheistic,
        Polytheistic,
        Pantheistic,
        Atheistic,
        Agnostic,
        Shamanic,
        Ancestral
    }

    /// <summary>
    /// Religion response DTO
    /// </summary>
    [Serializable]
    public class ReligionResponseDTO
    {
        [JsonProperty("religion")]
        public ReligionDTO Religion { get; set; }

        [JsonProperty("success")]
        public bool Success { get; set; } = true;

        [JsonProperty("message")]
        public string Message { get; set; } = string.Empty;
    }
} 