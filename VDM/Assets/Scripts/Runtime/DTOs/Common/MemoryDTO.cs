using System;
using System.Collections.Generic;
using VDM.DTOs.Core.Shared;

namespace VDM.DTOs.Social.Memory
{
    // ===========================================
    // ENUMS - Memory System Types
    // ===========================================

    public enum MemoryType
    {
        Interaction,    // Memory of interaction with another entity
        Observation,    // Memory of observing something
        Experience,     // Memory of experiencing something directly
        Rumor,          // Memory from hearing about something from others
        Reflection,     // Memory from thinking about other memories
        Decision,       // Memory of making an important decision
        Core           // Special memory that doesn't decay over time
    }

    public enum MemoryEmotionalValence
    {
        HighlyNegative = -2,
        Negative = -1,
        Neutral = 0,
        Positive = 1,
        HighlyPositive = 2
    }

    public enum MemoryCategory
    {
        Personal,       // Personal experience or reflection
        Trauma,         // Negative, impactful experience
        War,           // Conflict or large-scale violence
        Arc,           // Significant narrative moment
        Political,     // Political events or decisions
        Economic,      // Trade, commerce, financial events
        Social,        // Social interactions and relationships
        Combat,        // Combat experiences
        Magic,         // Magical experiences
        Exploration,   // Discovery and exploration
        Achievement,   // Accomplishments and successes
        Failure,       // Failures and mistakes
        Learning,      // Educational or skill-based memories
        Mundane,       // Everyday occurrences
        Important,     // Generally important memories
        Temporary      // Short-term, disposable memories
    }

    public enum MemoryRelationshipType
    {
        Follows,       // This memory follows another
        CausedBy,      // This memory was caused by another
        RelatedTo,     // This memory is related to another
        Contradicts,   // This memory contradicts another
        Reinforces,    // This memory reinforces another
        LeadsTo,       // This memory leads to another
        References,    // This memory references another
        Triggered,     // This memory triggered another
        Supercedes     // This memory supercedes another
    }

    // ===========================================
    // CORE MEMORY DTOs
    // ===========================================

    /// <summary>
    /// Represents a memory graph link between two memories
    /// </summary>
    public class MemoryGraphLinkDTO
    {
        public string TargetMemoryId { get; set; }

        public MemoryRelationshipType RelationshipType { get; set; }

        public float Strength { get; set; } = 1.0f;
    }

    /// <summary>
    /// Core memory data transfer object
    /// </summary>
    public class MemoryDTO : MetadataDTO
    {
        public string Id { get; set; }

        public string OwnerId { get; set; }

        public string Content { get; set; }

        public MemoryType MemoryType { get; set; }

        public float Importance { get; set; }

        public float CurrentStrength { get; set; } = 1.0f;

        public float FormationStrength { get; set; } = 1.0f;

        public MemoryEmotionalValence EmotionalValence { get; set; } = MemoryEmotionalValence.Neutral;

        public List<string> EntitiesInvolved { get; set; } = new List<string>();

        public List<string> Tags { get; set; } = new List<string>();

        public List<MemoryCategory> Categories { get; set; } = new List<MemoryCategory>();

        public string Summary { get; set; }

        public string Location { get; set; }

        public float Timestamp { get; set; }

        public float LastRecalled { get; set; }

        public int RecallCount { get; set; } = 0;

        public int AccessCount { get; set; } = 0;

        public float? LastAccessed { get; set; }

        public Dictionary<string, MemoryGraphLinkDTO> Links { get; set; } = new Dictionary<string, MemoryGraphLinkDTO>();

        public Dictionary<string, object> AdditionalMetadata { get; set; } = new Dictionary<string, object>();

        // Computed properties
        public bool IsCore => MemoryType == MemoryType.Core;
        public bool IsExpired => CurrentStrength < 0.1f && MemoryType != MemoryType.Core;
        public float DaysSinceCreation => (DateTimeOffset.UtcNow.ToUnixTimeSeconds() - Timestamp) / 86400f;
        public float DaysSinceLastRecall => (DateTimeOffset.UtcNow.ToUnixTimeSeconds() - LastRecalled) / 86400f;
    }

    /// <summary>
    /// Memory creation request DTO
    /// </summary>
    public class CreateMemoryRequestDTO
    {
        public string OwnerId { get; set; }

        public string Content { get; set; }

        public MemoryType MemoryType { get; set; } = MemoryType.Experience;

        public float? Importance { get; set; }

        public MemoryEmotionalValence EmotionalValence { get; set; } = MemoryEmotionalValence.Neutral;

        public List<string> EntitiesInvolved { get; set; } = new List<string>();

        public List<string> Tags { get; set; } = new List<string>();

        public List<MemoryCategory> Categories { get; set; } = new List<MemoryCategory>();

        public string Summary { get; set; }

        public string Location { get; set; }

        public Dictionary<string, object> Metadata { get; set; } = new Dictionary<string, object>();
    }

    /// <summary>
    /// Memory update request DTO
    /// </summary>
    public class UpdateMemoryRequestDTO
    {
        public string MemoryId { get; set; }

        public string Content { get; set; }

        public float? Importance { get; set; }

        public MemoryEmotionalValence? EmotionalValence { get; set; }

        public List<string> Tags { get; set; }

        public List<MemoryCategory> Categories { get; set; }

        public string Summary { get; set; }

        public string Location { get; set; }

        public Dictionary<string, object> Metadata { get; set; }
    }

    // ===========================================
    // MEMORY DECAY & SALIENCY DTOs
    // ===========================================

    /// <summary>
    /// Memory decay information DTO
    /// </summary>
    public class MemoryDecayInfoDTO
    {
        public string MemoryId { get; set; }

        public float CurrentStrength { get; set; }

        public float DaysSinceCreation { get; set; }

        public float DaysSinceRecall { get; set; }

        public int RecallCount { get; set; }

        public bool IsCore { get; set; }

        public float EstimatedLifespanDays { get; set; }
    }

    /// <summary>
    /// Memory saliency calculation request DTO
    /// </summary>
    public class CalculateMemorySaliencyRequestDTO
    {
        public MemoryDTO Memory { get; set; }

        public float? CurrentTime { get; set; }

        public float DecayRate { get; set; } = 0.1f;

        public float ImportanceWeight { get; set; } = 2.0f;

        public float RecencyWeight { get; set; } = 1.0f;
    }

    /// <summary>
    /// Memory saliency response DTO
    /// </summary>
    public class MemorySaliencyResponseDTO : SuccessResponseDTO
    {
        public string MemoryId { get; set; }

        public float SaliencyScore { get; set; }

        public float RecencyFactor { get; set; }

        public float ImportanceFactor { get; set; }

        public float DecayFactor { get; set; }
    }

    // ===========================================
    // MEMORY QUERY & RETRIEVAL DTOs
    // ===========================================

    /// <summary>
    /// Memory query request DTO
    /// </summary>
    public class MemoryQueryRequestDTO
    {
        public string OwnerId { get; set; }

        public string QueryContext { get; set; }

        public List<MemoryType> MemoryTypes { get; set; } = new List<MemoryType>();

        public List<MemoryCategory> Categories { get; set; } = new List<MemoryCategory>();

        public List<string> Tags { get; set; } = new List<string>();

        public List<string> EntitiesInvolved { get; set; } = new List<string>();

        public float? MinImportance { get; set; }

        public float? MaxImportance { get; set; }

        public float? MinStrength { get; set; }

        public MemoryEmotionalValence? EmotionalValence { get; set; }

        public string Location { get; set; }

        public float? StartTimestamp { get; set; }

        public float? EndTimestamp { get; set; }

        public int Limit { get; set; } = 50;

        public bool IncludeExpired { get; set; } = false;

        public bool SortByRelevance { get; set; } = true;
    }

    /// <summary>
    /// Memory recall request DTO
    /// </summary>
    public class MemoryRecallRequestDTO
    {
        public string OwnerId { get; set; }

        public string QueryContext { get; set; }

        public int MaxMemories { get; set; } = 10;

        public float RelevanceThreshold { get; set; } = 0.3f;

        public bool UpdateRecallStats { get; set; } = true;
    }

    /// <summary>
    /// Memory query response DTO
    /// </summary>
    public class MemoryQueryResponseDTO : SuccessResponseDTO
    {
        public List<MemoryDTO> Memories { get; set; } = new List<MemoryDTO>();

        public int TotalCount { get; set; }

        public string QueryContext { get; set; }

        public Dictionary<string, float> RelevanceScores { get; set; } = new Dictionary<string, float>();
    }

    // ===========================================
    // MEMORY MANAGEMENT DTOs
    // ===========================================

    /// <summary>
    /// Memory manager state DTO
    /// </summary>
    public class MemoryManagerStateDTO
    {
        public string EntityId { get; set; }

        public int TotalMemories { get; set; }

        public int CoreMemoriesCount { get; set; }

        public int RegularMemoriesCount { get; set; }

        public int ExpiredMemoriesCount { get; set; }

        public float DecayRate { get; set; } = 0.05f;

        public float LastDecayUpdate { get; set; }

        public Dictionary<MemoryCategory, int> MemoryCategoriesDistribution { get; set; } = new Dictionary<MemoryCategory, int>();

        public float AverageImportance { get; set; }

        public float AverageStrength { get; set; }
    }

    /// <summary>
    /// Apply memory decay request DTO
    /// </summary>
    public class ApplyMemoryDecayRequestDTO
    {
        public string EntityId { get; set; }

        public float DecayFactor { get; set; } = 0.1f;

        public float? CurrentTime { get; set; }

        public bool RemoveExpired { get; set; } = true;
    }

    /// <summary>
    /// Memory decay response DTO
    /// </summary>
    public class MemoryDecayResponseDTO : SuccessResponseDTO
    {
        public string EntityId { get; set; }

        public List<string> DecayedMemoryIds { get; set; } = new List<string>();

        public List<string> RemovedMemoryIds { get; set; } = new List<string>();

        public float DecayFactorApplied { get; set; }

        public int MemoriesAffected { get; set; }
    }

    /// <summary>
    /// Reinforce memory request DTO
    /// </summary>
    public class ReinforceMemoryRequestDTO
    {
        public string MemoryId { get; set; }

        public float ReinforcementAmount { get; set; } = 0.2f;

        public string Context { get; set; }
    }

    /// <summary>
    /// Recall memory request DTO
    /// </summary>
    public class RecallMemoryRequestDTO
    {
        public string OwnerId { get; set; }

        public string QueryContext { get; set; }

        public int MaxMemories { get; set; } = 10;

        public float RelevanceThreshold { get; set; } = 0.3f;

        public bool UpdateRecallStats { get; set; } = true;
    }

    /// <summary>
    /// Forget memory request DTO
    /// </summary>
    public class ForgetMemoryRequestDTO
    {
        public string MemoryId { get; set; }

        public string Reason { get; set; } = "manual";

        public bool Permanent { get; set; } = false;
    }

    // ===========================================
    // MEMORY LINK MANAGEMENT DTOs
    // ===========================================

    /// <summary>
    /// Add memory link request DTO
    /// </summary>
    public class AddMemoryLinkRequestDTO
    {
        public string SourceMemoryId { get; set; }

        public string TargetMemoryId { get; set; }

        public MemoryRelationshipType RelationshipType { get; set; }

        public float Strength { get; set; } = 1.0f;
    }

    /// <summary>
    /// Memory network analysis request DTO
    /// </summary>
    public class MemoryNetworkAnalysisRequestDTO
    {
        public string EntityId { get; set; }

        public string StartingMemoryId { get; set; }

        public int MaxDepth { get; set; } = 3;

        public float MinLinkStrength { get; set; } = 0.1f;

        public List<MemoryRelationshipType> IncludeRelationshipTypes { get; set; } = new List<MemoryRelationshipType>();
    }

    /// <summary>
    /// Memory network node DTO
    /// </summary>
    public class MemoryNetworkNodeDTO
    {
        public MemoryDTO Memory { get; set; }

        public int Depth { get; set; }

        public List<MemoryGraphLinkDTO> IncomingLinks { get; set; } = new List<MemoryGraphLinkDTO>();

        public List<MemoryGraphLinkDTO> OutgoingLinks { get; set; } = new List<MemoryGraphLinkDTO>();

        public float CentralityScore { get; set; }
    }

    /// <summary>
    /// Memory network analysis response DTO
    /// </summary>
    public class MemoryNetworkAnalysisResponseDTO : SuccessResponseDTO
    {
        public string EntityId { get; set; }

        public List<MemoryNetworkNodeDTO> NetworkNodes { get; set; } = new List<MemoryNetworkNodeDTO>();

        public int TotalMemoriesInNetwork { get; set; }

        public int TotalLinks { get; set; }

        public int MaxDepthReached { get; set; }

        public string StartingMemoryId { get; set; }
    }

    // ===========================================
    // MEMORY EVENT DTOs
    // ===========================================

    /// <summary>
    /// Memory created event DTO
    /// </summary>
    public class MemoryCreatedEventDTO
    {
        public string MemoryId { get; set; }

        public string EntityId { get; set; }

        public string Content { get; set; }

        public MemoryType MemoryType { get; set; }

        public List<MemoryCategory> Categories { get; set; } = new List<MemoryCategory>();

        public float Importance { get; set; }

        public float Timestamp { get; set; }
    }

    /// <summary>
    /// Memory decayed event DTO
    /// </summary>
    public class MemoryDecayedEventDTO
    {
        public string MemoryId { get; set; }

        public string EntityId { get; set; }

        public float OldSaliency { get; set; }

        public float NewSaliency { get; set; }

        public float Timestamp { get; set; }
    }

    /// <summary>
    /// Memory accessed event DTO
    /// </summary>
    public class MemoryAccessedEventDTO
    {
        public string MemoryId { get; set; }

        public string EntityId { get; set; }

        public string Context { get; set; }

        public float Timestamp { get; set; }
    }

    /// <summary>
    /// Memory recalled event DTO
    /// </summary>
    public class MemoryRecalledEventDTO
    {
        public string MemoryId { get; set; }

        public string EntityId { get; set; }

        public string Context { get; set; }

        public float Timestamp { get; set; }
    }

    /// <summary>
    /// Memory categorized event DTO
    /// </summary>
    public class MemoryCategorizedEventDTO
    {
        public string MemoryId { get; set; }

        public string EntityId { get; set; }

        public List<MemoryCategory> Categories { get; set; } = new List<MemoryCategory>();

        public float Timestamp { get; set; }
    }

    // ===========================================
    // RESPONSES & COMMON DTOs
    // ===========================================

    /// <summary>
    /// Memory operation response DTO
    /// </summary>
    public class MemoryResponseDTO : SuccessResponseDTO
    {
        public MemoryDTO Memory { get; set; }
    }

    /// <summary>
    /// Multiple memories response DTO
    /// </summary>
    public class MemoriesResponseDTO : SuccessResponseDTO
    {
        public List<MemoryDTO> Memories { get; set; } = new List<MemoryDTO>();

        public int TotalCount { get; set; }
    }

    /// <summary>
    /// Memory statistics DTO
    /// </summary>
    public class MemoryStatisticsDTO
    {
        public string EntityId { get; set; }

        public int TotalMemories { get; set; }

        public Dictionary<MemoryType, int> MemoryTypeDistribution { get; set; } = new Dictionary<MemoryType, int>();

        public Dictionary<MemoryCategory, int> CategoryDistribution { get; set; } = new Dictionary<MemoryCategory, int>();

        public Dictionary<MemoryEmotionalValence, int> EmotionalValenceDistribution { get; set; } = new Dictionary<MemoryEmotionalValence, int>();

        public float AverageImportance { get; set; }

        public float AverageStrength { get; set; }

        public float? OldestMemoryTimestamp { get; set; }

        public float? NewestMemoryTimestamp { get; set; }

        public int TotalRecallCount { get; set; }

        public float MemoryNetworkDensity { get; set; }
    }
} 