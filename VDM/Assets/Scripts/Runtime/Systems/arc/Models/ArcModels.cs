using Newtonsoft.Json;
using System.Collections.Generic;
using System;
using UnityEngine;


namespace VDM.Systems.Arc.Models
{
    /// <summary>
    /// Status of an individual arc step
    /// </summary>
    [Serializable]
    public enum ArcStepStatus
    {
        [JsonProperty("pending")]
        Pending,        // Not yet available
        
        [JsonProperty("available")]
        Available,      // Can be triggered
        
        [JsonProperty("active")]
        Active,         // Currently in progress
        
        [JsonProperty("completed")]
        Completed,      // Successfully finished
        
        [JsonProperty("failed")]
        Failed,         // Failed to complete
        
        [JsonProperty("skipped")]
        Skipped         // Bypassed by other means
    }

    /// <summary>
    /// Type of arc step
    /// </summary>
    [Serializable]
    public enum ArcStepType
    {
        [JsonProperty("narrative")]
        Narrative,      // Story progression
        
        [JsonProperty("challenge")]
        Challenge,      // Combat/skill challenge
        
        [JsonProperty("discovery")]
        Discovery,      // Information gathering
        
        [JsonProperty("interaction")]
        Interaction,    // NPC/faction interaction
        
        [JsonProperty("exploration")]
        Exploration,    // Location-based
        
        [JsonProperty("decision")]
        Decision        // Player choice point
    }

    /// <summary>
    /// Progression method for arc advancement
    /// </summary>
    [Serializable]
    public enum ProgressionMethod
    {
        [JsonProperty("automatic")]
        Automatic,      // Automatic progression
        
        [JsonProperty("manual")]
        Manual,         // Manual progression
        
        [JsonProperty("quest_based")]
        QuestBased,     // Quest-driven progression
        
        [JsonProperty("event_based")]
        EventBased,     // Event-driven progression
        
        [JsonProperty("time_based")]
        TimeBased       // Time-based progression
    }

    /// <summary>
    /// Classification tag for arc step integration
    /// </summary>
    [Serializable]
    public class ArcStepTag
    {
        [JsonProperty("key")]
        public string Key { get; set; }
        
        [JsonProperty("value")]
        public object Value { get; set; }
        
        [JsonProperty("weight")]
        public float Weight { get; set; } = 1.0f;
        
        [JsonProperty("required")]
        public bool Required { get; set; } = false;
    }

    /// <summary>
    /// Core Arc model representing a narrative thread
    /// </summary>
    [Serializable]
    public class ArcModel
    {
        [JsonProperty("id")]
        public string Id { get; set; }
        
        [JsonProperty("title")]
        public string Title { get; set; }
        
        [JsonProperty("description")]
        public string Description { get; set; }
        
        [JsonProperty("arc_type")]
        public ArcType ArcType { get; set; }
        
        [JsonProperty("status")]
        public ArcStatus Status { get; set; }
        
        [JsonProperty("priority")]
        public ArcPriority Priority { get; set; }
        
        [JsonProperty("steps")]
        public List<ArcStepModel> Steps { get; set; } = new List<ArcStepModel>();
        
        [JsonProperty("current_step_index")]
        public int CurrentStepIndex { get; set; } = 0;
        
        [JsonProperty("completion_percentage")]
        public float CompletionPercentage { get; set; } = 0.0f;
        
        [JsonProperty("created_at")]
        public DateTime CreatedAt { get; set; }
        
        [JsonProperty("updated_at")]
        public DateTime UpdatedAt { get; set; }
        
        [JsonProperty("completed_at")]
        public DateTime? CompletedAt { get; set; }
        
        [JsonProperty("metadata")]
        public Dictionary<string, object> Metadata { get; set; } = new Dictionary<string, object>();
        
        [JsonProperty("tags")]
        public List<string> Tags { get; set; } = new List<string>();
        
        [JsonProperty("character_id")]
        public string CharacterId { get; set; }
        
        [JsonProperty("faction_id")]
        public string FactionId { get; set; }
        
        [JsonProperty("region_id")]
        public string RegionId { get; set; }
        
        [JsonProperty("quest_ids")]
        public List<string> QuestIds { get; set; } = new List<string>();
        
        [JsonProperty("prerequisite_arc_ids")]
        public List<string> PrerequisiteArcIds { get; set; } = new List<string>();
        
        [JsonProperty("dependent_arc_ids")]
        public List<string> DependentArcIds { get; set; } = new List<string>();
    }

    /// <summary>
    /// Individual step within arc progression
    /// </summary>
    [Serializable]
    public class ArcStepModel
    {
        [JsonProperty("id")]
        public int Id { get; set; }
        
        [JsonProperty("arc_id")]
        public string ArcId { get; set; }
        
        [JsonProperty("title")]
        public string Title { get; set; }
        
        [JsonProperty("description")]
        public string Description { get; set; }
        
        [JsonProperty("step_type")]
        public ArcStepType StepType { get; set; }
        
        [JsonProperty("status")]
        public ArcStepStatus Status { get; set; }
        
        [JsonProperty("order_index")]
        public int OrderIndex { get; set; }
        
        [JsonProperty("required")]
        public bool Required { get; set; } = true;
        
        [JsonProperty("auto_complete")]
        public bool AutoComplete { get; set; } = false;
        
        [JsonProperty("completion_criteria")]
        public Dictionary<string, object> CompletionCriteria { get; set; } = new Dictionary<string, object>();
        
        [JsonProperty("tags")]
        public List<ArcStepTag> Tags { get; set; } = new List<ArcStepTag>();
        
        [JsonProperty("started_at")]
        public DateTime? StartedAt { get; set; }
        
        [JsonProperty("completed_at")]
        public DateTime? CompletedAt { get; set; }
        
        [JsonProperty("metadata")]
        public Dictionary<string, object> Metadata { get; set; } = new Dictionary<string, object>();
        
        [JsonProperty("quest_integration")]
        public Dictionary<string, object> QuestIntegration { get; set; } = new Dictionary<string, object>();
    }

    /// <summary>
    /// Arc progression tracking data
    /// </summary>
    [Serializable]
    public class ArcProgressionModel
    {
        [JsonProperty("arc_id")]
        public string ArcId { get; set; }
        
        [JsonProperty("character_id")]
        public string CharacterId { get; set; }
        
        [JsonProperty("current_step")]
        public int CurrentStep { get; set; }
        
        [JsonProperty("completion_percentage")]
        public float CompletionPercentage { get; set; }
        
        [JsonProperty("progression_method")]
        public ProgressionMethod ProgressionMethod { get; set; }
        
        [JsonProperty("step_progress")]
        public Dictionary<int, float> StepProgress { get; set; } = new Dictionary<int, float>();
        
        [JsonProperty("milestones_reached")]
        public List<string> MilestonesReached { get; set; } = new List<string>();
        
        [JsonProperty("started_at")]
        public DateTime StartedAt { get; set; }
        
        [JsonProperty("last_updated")]
        public DateTime LastUpdated { get; set; }
        
        [JsonProperty("estimated_completion")]
        public DateTime? EstimatedCompletion { get; set; }
    }

    /// <summary>
    /// Arc creation request DTO
    /// </summary>
    [Serializable]
    public class CreateArcRequestModel
    {
        [JsonProperty("title")]
        public string Title { get; set; }
        
        [JsonProperty("description")]
        public string Description { get; set; }
        
        [JsonProperty("arc_type")]
        public ArcType ArcType { get; set; }
        
        [JsonProperty("priority")]
        public ArcPriority Priority { get; set; }
        
        [JsonProperty("character_id")]
        public string CharacterId { get; set; }
        
        [JsonProperty("faction_id")]
        public string FactionId { get; set; }
        
        [JsonProperty("region_id")]
        public string RegionId { get; set; }
        
        [JsonProperty("tags")]
        public List<string> Tags { get; set; } = new List<string>();
        
        [JsonProperty("metadata")]
        public Dictionary<string, object> Metadata { get; set; } = new Dictionary<string, object>();
    }

    /// <summary>
    /// Arc update request DTO
    /// </summary>
    [Serializable]
    public class UpdateArcRequestModel
    {
        [JsonProperty("status")]
        public ArcStatus? Status { get; set; }
        
        [JsonProperty("priority")]
        public ArcPriority? Priority { get; set; }
        
        [JsonProperty("current_step_index")]
        public int? CurrentStepIndex { get; set; }
        
        [JsonProperty("completion_percentage")]
        public float? CompletionPercentage { get; set; }
        
        [JsonProperty("metadata")]
        public Dictionary<string, object> Metadata { get; set; }
    }

    /// <summary>
    /// Arc generation request DTO
    /// </summary>
    [Serializable]
    public class ArcGenerateRequestModel
    {
        [JsonProperty("arc_type")]
        public ArcType ArcType { get; set; }
        
        [JsonProperty("theme")]
        public string Theme { get; set; }
        
        [JsonProperty("complexity")]
        public int Complexity { get; set; } = 3;
        
        [JsonProperty("character_id")]
        public string CharacterId { get; set; }
        
        [JsonProperty("region_id")]
        public string RegionId { get; set; }
        
        [JsonProperty("faction_id")]
        public string FactionId { get; set; }
        
        [JsonProperty("parameters")]
        public Dictionary<string, object> Parameters { get; set; } = new Dictionary<string, object>();
    }

    /// <summary>
    /// Quest opportunity response from arc system
    /// </summary>
    [Serializable]
    public class QuestOpportunityModel
    {
        [JsonProperty("id")]
        public string Id { get; set; }
        
        [JsonProperty("title")]
        public string Title { get; set; }
        
        [JsonProperty("description")]
        public string Description { get; set; }
        
        [JsonProperty("arc_id")]
        public string ArcId { get; set; }
        
        [JsonProperty("step_id")]
        public int StepId { get; set; }
        
        [JsonProperty("priority")]
        public string Priority { get; set; }
        
        [JsonProperty("estimated_duration")]
        public int EstimatedDuration { get; set; }
        
        [JsonProperty("requirements")]
        public Dictionary<string, object> Requirements { get; set; } = new Dictionary<string, object>();
        
        [JsonProperty("rewards")]
        public Dictionary<string, object> Rewards { get; set; } = new Dictionary<string, object>();
        
        [JsonProperty("integration_data")]
        public Dictionary<string, object> IntegrationData { get; set; } = new Dictionary<string, object>();
    }

    /// <summary>
    /// Arc analytics and reporting data
    /// </summary>
    [Serializable]
    public class ArcAnalyticsModel
    {
        [JsonProperty("arc_id")]
        public string ArcId { get; set; }
        
        [JsonProperty("total_steps")]
        public int TotalSteps { get; set; }
        
        [JsonProperty("completed_steps")]
        public int CompletedSteps { get; set; }
        
        [JsonProperty("active_participants")]
        public int ActiveParticipants { get; set; }
        
        [JsonProperty("average_completion_time")]
        public float AverageCompletionTime { get; set; }
        
        [JsonProperty("engagement_metrics")]
        public Dictionary<string, float> EngagementMetrics { get; set; } = new Dictionary<string, float>();
        
        [JsonProperty("step_analytics")]
        public List<Dictionary<string, object>> StepAnalytics { get; set; } = new List<Dictionary<string, object>>();
    }

    /// <summary>
    /// Arc beat represents a significant story moment within an arc
    /// </summary>
    [Serializable]
    public class ArcBeat
    {
        // Implementation of ArcBeat class
    }

    /// <summary>
    /// Event data for arc quest updates
    /// </summary>
    [Serializable]
    public class ArcQuestUpdateEvent
    {
        [JsonProperty("arc_id")]
        public string ArcId { get; set; } = string.Empty;

        [JsonProperty("quest_id")]
        public string QuestId { get; set; } = string.Empty;

        [JsonProperty("update_type")]
        public string UpdateType { get; set; } = string.Empty;

        [JsonProperty("data")]
        public Dictionary<string, object> Data { get; set; } = new Dictionary<string, object>();

        [JsonProperty("timestamp")]
        public DateTime Timestamp { get; set; } = DateTime.UtcNow;
    }

    /// <summary>
    /// Event data for arc status changes
    /// </summary>
    [Serializable]
    public class ArcStatusChangeEvent
    {
        [JsonProperty("arc_id")]
        public string ArcId { get; set; } = string.Empty;

        [JsonProperty("old_status")]
        public string OldStatus { get; set; } = string.Empty;

        [JsonProperty("new_status")]
        public string NewStatus { get; set; } = string.Empty;

        [JsonProperty("reason")]
        public string Reason { get; set; } = string.Empty;

        [JsonProperty("timestamp")]
        public DateTime Timestamp { get; set; } = DateTime.UtcNow;
    }
} 