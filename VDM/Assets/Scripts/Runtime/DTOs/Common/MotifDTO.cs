using System;
using System.Collections.Generic;
using VDM.DTOs.Core.Shared;

namespace VDM.DTOs.Content.Motif
{
    /// <summary>
    /// Motif category enumeration
    /// </summary>
    [Serializable]
    public enum MotifCategory
    {
        Ascension,
        Betrayal,
        Chaos,
        Collapse,
        Compulsion,
        Control,
        Death,
        Deception,
        Defiance,
        Desire,
        Despair,
        Destiny,
        Echo,
        Expansion,
        Faith,
        Fear,
        Futility,
        Grief,
        Guilt,
        Hope,
        Hunger,
        Innocence,
        Invention,
        Isolation,
        Justice,
        Loyalty,
        Madness,
        Obsession,
        Paranoia,
        Peace,
        Power,
        Pride,
        Protection,
        Rebirth,
        Redemption,
        Regret,
        Revelation,
        Ruin,
        Sacrifice,
        Silence,
        Shadow,
        Stagnation,
        Temptation,
        Time,
        Transformation,
        Truth,
        Unity,
        Vengeance,
        Worship
    }

    /// <summary>
    /// Motif scope enumeration
    /// </summary>
    [Serializable]
    public enum MotifScope
    {
        Global,
        Regional,
        Local
    }

    /// <summary>
    /// Motif lifecycle enumeration
    /// </summary>
    [Serializable]
    public enum MotifLifecycle
    {
        Emerging,
        Developing,
        Dominant,
        Waning,
        Dormant
    }

    /// <summary>
    /// Location information for motifs
    /// </summary>
    [Serializable]
    public class LocationInfoDTO
    {
        public float X { get; set; }
        public float Y { get; set; }
        public float Radius { get; set; }
        public string RegionId { get; set; } = string.Empty;
    }

    /// <summary>
    /// Motif effect DTO
    /// </summary>
    [Serializable]
    public class MotifEffectDTO
    {
        public string EffectId { get; set; } = string.Empty;
        public string EffectType { get; set; } = string.Empty;
        public string Target { get; set; } = string.Empty;
        public float Magnitude { get; set; }
        public string Duration { get; set; } = string.Empty;
        public Dictionary<string, object> Parameters { get; set; } = new Dictionary<string, object>();
    }

    /// <summary>
    /// Base DTO for motif system with common fields
    /// </summary>
    [Serializable]
    public abstract class MotifBaseDTO : MetadataDTO
    {
        public bool IsActive { get; set; } = true;
    }

    /// <summary>
    /// Primary DTO for motif system
    /// </summary>
    [Serializable]
    public class MotifDTO : MotifBaseDTO
    {
        public string Name { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
        public MotifCategory Category { get; set; } = MotifCategory.Hope;
        public MotifScope Scope { get; set; } = MotifScope.Local;
        public string Theme { get; set; } = "general";
        public MotifLifecycle Lifecycle { get; set; } = MotifLifecycle.Emerging;
        public int Intensity { get; set; } = 5; // 1-10 scale
        
        // Duration and timing
        public DateTime StartTime { get; set; } = DateTime.UtcNow;
        public DateTime EndTime { get; set; } = DateTime.UtcNow.AddDays(14);
        public int DurationDays { get; set; } = 14;
        
        // Location data for regional/local motifs
        public LocationInfoDTO Location { get; set; }
        
        // Effects
        public List<MotifEffectDTO> Effects { get; set; } = new List<MotifEffectDTO>();
        
        // Enhanced narrative integration
        public string Tone { get; set; } = "neutral";
        public string NarrativeDirection { get; set; } = "steady";
        public List<string> Descriptors { get; set; } = new List<string>();
        
        // Optional fields for advanced synthesis
        public List<string> AssociatedElements { get; set; } = new List<string>();
        public List<string> OpposingThemes { get; set; } = new List<string>();
        
        // Context for narrative generation
        public string NarrativeGuidance { get; set; }
        
        // Tags for categorization and filtering
        public List<string> Tags { get; set; } = new List<string>();
    }

    /// <summary>
    /// Request DTO for creating motif
    /// </summary>
    [Serializable]
    public class CreateMotifDTO
    {
        public string Name { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
        public MotifCategory Category { get; set; } = MotifCategory.Hope;
        public MotifScope Scope { get; set; } = MotifScope.Local;
        public string Theme { get; set; } = "general";
        public MotifLifecycle Lifecycle { get; set; } = MotifLifecycle.Emerging;
        public int Intensity { get; set; } = 5;
        public int DurationDays { get; set; } = 14;
        public LocationInfoDTO Location { get; set; }
        public List<MotifEffectDTO> Effects { get; set; } = new List<MotifEffectDTO>();
        public Dictionary<string, object> Metadata { get; set; } = new Dictionary<string, object>();
    }

    /// <summary>
    /// Request DTO for updating motif
    /// </summary>
    [Serializable]
    public class UpdateMotifDTO
    {
        public string Name { get; set; }
        public string Description { get; set; }
        public MotifCategory? Category { get; set; }
        public MotifScope? Scope { get; set; }
        public string Theme { get; set; }
        public MotifLifecycle? Lifecycle { get; set; }
        public int? Intensity { get; set; }
        public int? DurationDays { get; set; }
        public LocationInfoDTO Location { get; set; }
        public List<MotifEffectDTO> Effects { get; set; }
        public Dictionary<string, object> Metadata { get; set; }
    }

    /// <summary>
    /// Response DTO for motif
    /// </summary>
    [Serializable]
    public class MotifResponseDTO : SuccessResponseDTO
    {
        public MotifDTO Motif { get; set; } = new MotifDTO();
    }

    /// <summary>
    /// Response DTO for motif lists
    /// </summary>
    [Serializable]
    public class MotifListResponseDTO : SuccessResponseDTO
    {
        public List<MotifDTO> Motifs { get; set; } = new List<MotifDTO>();
        public int Total { get; set; }
        public int Page { get; set; }
        public int Size { get; set; }
        public bool HasNext { get; set; }
        public bool HasPrev { get; set; }
    }

    /// <summary>
    /// Motif filter DTO for querying motifs
    /// </summary>
    [Serializable]
    public class MotifFilterDTO
    {
        public List<MotifCategory> Categories { get; set; } = new List<MotifCategory>();
        public List<MotifScope> Scopes { get; set; } = new List<MotifScope>();
        public List<MotifLifecycle> Lifecycles { get; set; } = new List<MotifLifecycle>();
        public int? MinIntensity { get; set; }
        public int? MaxIntensity { get; set; }
        public string RegionId { get; set; }
        public string EffectType { get; set; }
        public bool ActiveOnly { get; set; } = true;
        public List<string> Ids { get; set; } = new List<string>();
        public List<string> Themes { get; set; } = new List<string>();
        public List<string> RegionIds { get; set; } = new List<string>();
        public bool? IsGlobal { get; set; }
        public Dictionary<string, object> Metadata { get; set; } = new Dictionary<string, object>();
        public List<string> Tags { get; set; } = new List<string>();
        public DateTime? CreatedAfter { get; set; }
        public DateTime? CreatedBefore { get; set; }
        public DateTime? UpdatedAfter { get; set; }
        public DateTime? UpdatedBefore { get; set; }
        public string SortBy { get; set; }
        public string SortOrder { get; set; } = "asc";
    }

    /// <summary>
    /// Motif synthesis result DTO for combining multiple motifs
    /// </summary>
    [Serializable]
    public class MotifSynthesisDTO
    {
        public string Theme { get; set; } = string.Empty;
        public float Intensity { get; set; }
        public string Tone { get; set; } = "neutral";
        public string NarrativeDirection { get; set; } = "steady";
        public List<string> Descriptors { get; set; } = new List<string>();
        public List<string> ConflictingMotifs { get; set; } = new List<string>();
        public Dictionary<string, float> MotifWeights { get; set; } = new Dictionary<string, float>();
    }

    /// <summary>
    /// Narrative context DTO for motif-driven narrative generation
    /// </summary>
    [Serializable]
    public class MotifNarrativeContextDTO
    {
        public List<MotifDTO> ActiveMotifs { get; set; } = new List<MotifDTO>();
        public string DominantMotif { get; set; }
        public List<string> NarrativeThemes { get; set; } = new List<string>();
        public int MotifCount { get; set; }
        public bool HasMotifs { get; set; }
        public string PromptText { get; set; } = string.Empty;
        public MotifSynthesisDTO Synthesis { get; set; } = new MotifSynthesisDTO();
        public Dictionary<string, object> NarrativeGuidance { get; set; } = new Dictionary<string, object>();
        public string LocationType { get; set; } = string.Empty;
        public string LocationName { get; set; } = string.Empty;
    }

    /// <summary>
    /// Motif context request DTO
    /// </summary>
    [Serializable]
    public class MotifContextRequestDTO
    {
        public float? X { get; set; }
        public float? Y { get; set; }
        public string RegionId { get; set; }
        public string ContextSize { get; set; } = "medium";
    }
} 