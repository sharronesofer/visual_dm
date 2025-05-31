using System;
using System.Collections.Generic;
using VDM.DTOs.Core.Shared;

namespace VDM.DTOs.Content.Arc
{
    /// <summary>
    /// Arc types defining scope and influence level
    /// </summary>
    public enum ArcTypeDTO
    {
        Global,     // World-spanning narratives
        Regional,   // Area-specific storylines  
        Character,  // Personal player narratives
        Npc         // NPC-driven storylines
    }

    /// <summary>
    /// Current status of an arc
    /// </summary>
    public enum ArcStatusDTO
    {
        Pending,    // Not yet started
        Active,     // Currently progressing
        Stalled,    // No progress for extended time
        Failed,     // Cannot complete original objective
        Completed,  // Successfully finished
        Abandoned   // Deliberately terminated
    }

    /// <summary>
    /// Priority level for arc progression
    /// </summary>
    public enum ArcPriorityDTO
    {
        Low,
        Medium,
        High,
        Urgent
    }

    /// <summary>
    /// Core Arc model representing a narrative thread
    /// </summary>
    [Serializable]
    public class ArcDTO : MetadataDTO
    {
        // Core Identity
        public string Id { get; set; } = string.Empty;

        public string Title { get; set; } = string.Empty;

        public string Description { get; set; } = string.Empty;

        // Arc Classification
        public ArcTypeDTO ArcType { get; set; } = ArcTypeDTO.Regional;

        public ArcStatusDTO Status { get; set; } = ArcStatusDTO.Pending;

        public ArcPriorityDTO Priority { get; set; } = ArcPriorityDTO.Medium;

        // Narrative Structure
        public string StartingPoint { get; set; } = string.Empty;

        public string PreferredEnding { get; set; } = string.Empty;

        public string CurrentNarrative { get; set; } = string.Empty;

        // Scope and Targeting
        public string? RegionId { get; set; }

        public string? CharacterId { get; set; }

        public string? NpcId { get; set; }

        public List<string> FactionIds { get; set; } = new List<string>();

        // Progression Tracking
        public int CurrentStep { get; set; } = 0;

        public int? TotalSteps { get; set; }

        public float CompletionPercentage { get; set; } = 0.0f;

        // Timeline Management
        public float TimeSensitivity { get; set; } = 0.0f;

        public DateTime? Deadline { get; set; }

        public int StallThresholdDays { get; set; } = 30;

        // Integration Tags
        public Dictionary<string, object> ClassificationTags { get; set; } = new Dictionary<string, object>();

        public List<string> SystemHooks { get; set; } = new List<string>();

        // AI Generation Context
        public Dictionary<string, object> GenerationContext { get; set; } = new Dictionary<string, object>();

        public List<string> PreviousArcHistory { get; set; } = new List<string>();

        // Performance Optimization
        public DateTime LastActivity { get; set; } = DateTime.UtcNow;

        public bool CacheInvalidated { get; set; } = true;

        // Computed Properties (read-only)
        public bool IsTimeSensitive => TimeSensitivity > 0.0f && Deadline.HasValue;

        public bool IsStalled => Status == ArcStatusDTO.Active && 
                                (DateTime.UtcNow - LastActivity).Days >= StallThresholdDays;

        public bool IsOverdue => IsTimeSensitive && DateTime.UtcNow > Deadline;

        public string? ScopeIdentifier => ArcType switch
        {
            ArcTypeDTO.Regional => RegionId,
            ArcTypeDTO.Character => CharacterId,
            ArcTypeDTO.Npc => NpcId,
            _ => null
        };
    }

    /// <summary>
    /// Arc stage representing a step in the narrative progression
    /// </summary>
    [Serializable]
    public class ArcStageDTO
    {
        public string Id { get; set; } = string.Empty;

        public string ArcId { get; set; } = string.Empty;

        public string Name { get; set; } = string.Empty;

        public string Description { get; set; } = string.Empty;

        public int OrderIndex { get; set; } = 0;

        public bool Completed { get; set; } = false;

        public DateTime? CompletionDate { get; set; }

        public Dictionary<string, object> Metadata { get; set; } = new Dictionary<string, object>();

        public List<string> Requirements { get; set; } = new List<string>();

        public List<string> Rewards { get; set; } = new List<string>();
    }

    /// <summary>
    /// Arc relationships defining connections between arcs
    /// </summary>
    [Serializable]
    public class ArcRelationshipsDTO
    {
        public string? ParentArcId { get; set; }

        public List<string> ChildArcIds { get; set; } = new List<string>();

        public List<string> PrerequisiteArcIds { get; set; } = new List<string>();

        public List<string> DependentArcIds { get; set; } = new List<string>();

        public List<string> RelatedArcIds { get; set; } = new List<string>();

        public List<string> ConflictingArcIds { get; set; } = new List<string>();
    }

    /// <summary>
    /// Arc metadata for additional information
    /// </summary>
    [Serializable]
    public class ArcMetadataDTO
    {
        public List<string> Themes { get; set; } = new List<string>();

        public string? Tone { get; set; }

        public int DifficultyLevel { get; set; } = 5;

        public float? EstimatedDurationHours { get; set; }

        public int? PlayerLevelRequirement { get; set; }

        public List<string> Tags { get; set; } = new List<string>();

        public string? Notes { get; set; }
    }

    // ================ Request DTOs ================

    /// <summary>
    /// Request to create a new arc
    /// </summary>
    [Serializable]
    public class CreateArcRequestDTO
    {
        public string Title { get; set; } = string.Empty;

        public string Description { get; set; } = string.Empty;

        public ArcTypeDTO ArcType { get; set; } = ArcTypeDTO.Regional;

        public ArcPriorityDTO Priority { get; set; } = ArcPriorityDTO.Medium;

        public string StartingPoint { get; set; } = string.Empty;

        public string PreferredEnding { get; set; } = string.Empty;

        public string? RegionId { get; set; }

        public string? CharacterId { get; set; }

        public string? NpcId { get; set; }

        public List<string>? FactionIds { get; set; }

        public float TimeSensitivity { get; set; } = 0.0f;

        public DateTime? Deadline { get; set; }

        public Dictionary<string, object>? ClassificationTags { get; set; }

        public List<string>? SystemHooks { get; set; }

        public ArcMetadataDTO? Metadata { get; set; }
    }

    /// <summary>
    /// Request to update an arc
    /// </summary>
    [Serializable]
    public class UpdateArcRequestDTO
    {
        public string? Title { get; set; }

        public string? Description { get; set; }

        public ArcStatusDTO? Status { get; set; }

        public ArcPriorityDTO? Priority { get; set; }

        public string? CurrentNarrative { get; set; }

        public int? CurrentStep { get; set; }

        public float? CompletionPercentage { get; set; }

        public float? TimeSensitivity { get; set; }

        public DateTime? Deadline { get; set; }

        public Dictionary<string, object>? ClassificationTags { get; set; }

        public List<string>? SystemHooks { get; set; }

        public ArcMetadataDTO? Metadata { get; set; }
    }

    /// <summary>
    /// Request to create an arc stage
    /// </summary>
    [Serializable]
    public class CreateArcStageRequestDTO
    {
        public string ArcId { get; set; } = string.Empty;

        public string Name { get; set; } = string.Empty;

        public string Description { get; set; } = string.Empty;

        public int OrderIndex { get; set; } = 0;

        public Dictionary<string, object>? Metadata { get; set; }

        public List<string>? Requirements { get; set; }

        public List<string>? Rewards { get; set; }
    }

    /// <summary>
    /// Request to progress an arc
    /// </summary>
    [Serializable]
    public class ProgressArcRequestDTO
    {
        public string ArcId { get; set; } = string.Empty;

        public string? NarrativeUpdate { get; set; }

        public int StepIncrement { get; set; } = 1;

        public float? CompletionPercentage { get; set; }

        public string? StageId { get; set; }

        public bool CompleteStage { get; set; } = false;

        public Dictionary<string, object>? Context { get; set; }
    }

    /// <summary>
    /// Arc summary for list views
    /// </summary>
    [Serializable]
    public class ArcSummaryDTO
    {
        public string Id { get; set; } = string.Empty;

        public string Title { get; set; } = string.Empty;

        public ArcTypeDTO ArcType { get; set; } = ArcTypeDTO.Regional;

        public ArcStatusDTO Status { get; set; } = ArcStatusDTO.Pending;

        public ArcPriorityDTO Priority { get; set; } = ArcPriorityDTO.Medium;

        public float CompletionPercentage { get; set; } = 0.0f;

        public bool IsTimeSensitive { get; set; } = false;

        public bool IsOverdue { get; set; } = false;

        public DateTime LastActivity { get; set; } = DateTime.UtcNow;
    }
} 