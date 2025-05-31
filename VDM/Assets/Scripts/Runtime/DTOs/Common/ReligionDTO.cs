using System;
using System.Collections.Generic;
using VDM.DTOs.Core.Shared;

namespace VDM.DTOs.Content.Religion
{
    /// <summary>
    /// Religion type enumeration
    /// </summary>
    [Serializable]
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
    /// Base DTO for religion system with common fields
    /// </summary>
    [Serializable]
    public abstract class ReligionBaseDTO : MetadataDTO
    {
        public bool IsActive { get; set; } = true;
    }

    /// <summary>
    /// Deity DTO for religious deities
    /// </summary>
    [Serializable]
    public class DeityDTO : ReligionBaseDTO
    {
        public string Name { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
        public string Domain { get; set; } = string.Empty;
        public string Alignment { get; set; } = string.Empty;
        public List<string> Symbols { get; set; } = new List<string>();
        public List<string> HolyDays { get; set; } = new List<string>();
        public List<string> Powers { get; set; } = new List<string>();
        public int WorshiperCount { get; set; } = 0;
        public string ReligionId { get; set; } = string.Empty;
    }

    /// <summary>
    /// Religious practice DTO
    /// </summary>
    [Serializable]
    public class ReligiousPracticeDTO : ReligionBaseDTO
    {
        public string Name { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
        public string Frequency { get; set; } = string.Empty;
        public int Participants { get; set; } = 0;
        public string LocationType { get; set; } = string.Empty;
        public List<string> RequiredItems { get; set; } = new List<string>();
        public string ReligionId { get; set; } = string.Empty;
    }

    /// <summary>
    /// Religious event DTO
    /// </summary>
    [Serializable]
    public class ReligiousEventDTO : ReligionBaseDTO
    {
        public string Name { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
        public string EventType { get; set; } = string.Empty;
        public DateTime EventDate { get; set; } = DateTime.UtcNow;
        public string Duration { get; set; } = string.Empty;
        public List<string> Participants { get; set; } = new List<string>();
        public string LocationId { get; set; } = string.Empty;
        public string ReligionId { get; set; } = string.Empty;
        public Dictionary<string, object> EventData { get; set; } = new Dictionary<string, object>();
    }

    /// <summary>
    /// Religious influence DTO
    /// </summary>
    [Serializable]
    public class ReligiousInfluenceDTO : ReligionBaseDTO
    {
        public string EntityId { get; set; } = string.Empty;
        public string ReligionId { get; set; } = string.Empty;
        public float DevotionLevel { get; set; } = 0.5f;
        public string Role { get; set; } = "follower";
        public DateTime JoinedDate { get; set; } = DateTime.UtcNow;
        public string Status { get; set; } = "active";
    }

    /// <summary>
    /// Primary DTO for religion system
    /// </summary>
    [Serializable]
    public class ReligionDTO : ReligionBaseDTO
    {
        public string Name { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
        public ReligionType Type { get; set; } = ReligionType.Monotheistic;
        public string OriginStory { get; set; } = string.Empty;
        public List<string> CoreBeliefs { get; set; } = new List<string>();
        public List<string> Practices { get; set; } = new List<string>();
        public string ClergyStructure { get; set; } = string.Empty;
        public List<string> HolyTexts { get; set; } = new List<string>();
        public List<DeityDTO> Deities { get; set; } = new List<DeityDTO>();
        public int FollowersCount { get; set; } = 0;
        public List<string> InfluenceRegions { get; set; } = new List<string>();
        public string Status { get; set; } = "active";
        public Dictionary<string, object> Properties { get; set; } = new Dictionary<string, object>();
    }

    /// <summary>
    /// Request DTO for creating religion
    /// </summary>
    [Serializable]
    public class CreateReligionDTO
    {
        public string Name { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
        public ReligionType Type { get; set; } = ReligionType.Monotheistic;
        public string OriginStory { get; set; } = string.Empty;
        public List<string> CoreBeliefs { get; set; } = new List<string>();
        public List<string> Tenets { get; set; } = new List<string>();
        public List<string> Practices { get; set; } = new List<string>();
        public List<string> HolyPlaces { get; set; } = new List<string>();
        public List<string> SacredTexts { get; set; } = new List<string>();
        public string ClergyStructure { get; set; } = string.Empty;
        public Dictionary<string, object> Properties { get; set; } = new Dictionary<string, object>();
    }

    /// <summary>
    /// Request DTO for updating religion
    /// </summary>
    [Serializable]
    public class UpdateReligionDTO
    {
        public string Name { get; set; }
        public string Description { get; set; }
        public string OriginStory { get; set; }
        public List<string> CoreBeliefs { get; set; }
        public List<string> Tenets { get; set; }
        public List<string> Practices { get; set; }
        public List<string> HolyPlaces { get; set; }
        public List<string> SacredTexts { get; set; }
        public string ClergyStructure { get; set; }
        public string Status { get; set; }
        public Dictionary<string, object> Properties { get; set; }
    }

    /// <summary>
    /// Response DTO for religion
    /// </summary>
    [Serializable]
    public class ReligionResponseDTO : SuccessResponseDTO
    {
        public ReligionDTO Religion { get; set; } = new ReligionDTO();
    }

    /// <summary>
    /// Response DTO for religion lists
    /// </summary>
    [Serializable]
    public class ReligionListResponseDTO : SuccessResponseDTO
    {
        public List<ReligionDTO> Religions { get; set; } = new List<ReligionDTO>();
        public int Total { get; set; }
        public int Page { get; set; }
        public int Size { get; set; }
        public bool HasNext { get; set; }
        public bool HasPrev { get; set; }
    }

    /// <summary>
    /// Request DTO for creating deity
    /// </summary>
    [Serializable]
    public class CreateDeityDTO
    {
        public string Name { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
        public string Domain { get; set; } = string.Empty;
        public string Alignment { get; set; } = string.Empty;
        public List<string> Symbols { get; set; } = new List<string>();
        public List<string> HolyDays { get; set; } = new List<string>();
        public List<string> Powers { get; set; } = new List<string>();
        public string ReligionId { get; set; } = string.Empty;
    }

    /// <summary>
    /// Response DTO for deity
    /// </summary>
    [Serializable]
    public class DeityResponseDTO : SuccessResponseDTO
    {
        public DeityDTO Deity { get; set; } = new DeityDTO();
    }

    /// <summary>
    /// Response DTO for deity lists
    /// </summary>
    [Serializable]
    public class DeityListResponseDTO : SuccessResponseDTO
    {
        public List<DeityDTO> Deities { get; set; } = new List<DeityDTO>();
        public int Total { get; set; }
        public int Page { get; set; }
        public int Size { get; set; }
        public bool HasNext { get; set; }
        public bool HasPrev { get; set; }
    }

    /// <summary>
    /// Request DTO for creating religious practice
    /// </summary>
    [Serializable]
    public class CreateReligiousPracticeDTO
    {
        public string Name { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
        public string Frequency { get; set; } = string.Empty;
        public int Participants { get; set; } = 0;
        public string LocationType { get; set; } = string.Empty;
        public List<string> RequiredItems { get; set; } = new List<string>();
        public string ReligionId { get; set; } = string.Empty;
    }

    /// <summary>
    /// Response DTO for religious practice
    /// </summary>
    [Serializable]
    public class ReligiousPracticeResponseDTO : SuccessResponseDTO
    {
        public ReligiousPracticeDTO Practice { get; set; } = new ReligiousPracticeDTO();
    }

    /// <summary>
    /// Request DTO for creating religious event
    /// </summary>
    [Serializable]
    public class CreateReligiousEventDTO
    {
        public string Name { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
        public string EventType { get; set; } = string.Empty;
        public DateTime EventDate { get; set; } = DateTime.UtcNow;
        public string Duration { get; set; } = string.Empty;
        public List<string> Participants { get; set; } = new List<string>();
        public string LocationId { get; set; } = string.Empty;
        public string ReligionId { get; set; } = string.Empty;
        public Dictionary<string, object> EventData { get; set; } = new Dictionary<string, object>();
    }

    /// <summary>
    /// Response DTO for religious event
    /// </summary>
    [Serializable]
    public class ReligiousEventResponseDTO : SuccessResponseDTO
    {
        public ReligiousEventDTO Event { get; set; } = new ReligiousEventDTO();
    }

    /// <summary>
    /// Request DTO for creating religious influence
    /// </summary>
    [Serializable]
    public class CreateReligiousInfluenceDTO
    {
        public string EntityId { get; set; } = string.Empty;
        public string ReligionId { get; set; } = string.Empty;
        public float DevotionLevel { get; set; } = 0.5f;
        public string Role { get; set; } = "follower";
        public DateTime JoinedDate { get; set; } = DateTime.UtcNow;
        public string Status { get; set; } = "active";
    }

    /// <summary>
    /// Response DTO for religious influence
    /// </summary>
    [Serializable]
    public class ReligiousInfluenceResponseDTO : SuccessResponseDTO
    {
        public ReligiousInfluenceDTO Influence { get; set; } = new ReligiousInfluenceDTO();
    }

    /// <summary>
    /// Pantheon DTO for groups of related religions
    /// </summary>
    [Serializable]
    public class PantheonDTO : ReligionBaseDTO
    {
        public string Name { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
        public List<string> ReligionIds { get; set; } = new List<string>();
        public List<ReligionDTO> Religions { get; set; } = new List<ReligionDTO>();
        public string CulturalOrigin { get; set; } = string.Empty;
        public Dictionary<string, object> Properties { get; set; } = new Dictionary<string, object>();
    }

    /// <summary>
    /// Response DTO for pantheon
    /// </summary>
    [Serializable]
    public class PantheonResponseDTO : SuccessResponseDTO
    {
        public PantheonDTO Pantheon { get; set; } = new PantheonDTO();
    }
} 