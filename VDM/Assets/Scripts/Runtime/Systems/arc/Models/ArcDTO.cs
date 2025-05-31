using Newtonsoft.Json;
using System.Collections.Generic;
using System;
using UnityEngine;


namespace VDM.Systems.Arc.Models
{
    /// <summary>
    /// Arc types defining scope and influence level
    /// </summary>
    public enum ArcType
    {
        Global,      // World-spanning narratives
        Regional,    // Area-specific storylines  
        Character,   // Personal player narratives
        Npc         // NPC-driven storylines
    }
    
    /// <summary>
    /// Current status of an arc
    /// </summary>
    public enum ArcStatus
    {
        Pending,     // Not yet started
        Active,      // Currently progressing
        Stalled,     // No progress for extended time
        Failed,      // Cannot complete original objective
        Completed,   // Successfully finished
        Abandoned    // Deliberately terminated
    }
    
    /// <summary>
    /// Priority level for arc progression
    /// </summary>
    public enum ArcPriority
    {
        Low,
        Medium,
        High,
        Urgent
    }
    
    /// <summary>
    /// Data Transfer Object for Arc API communication matching backend arc models
    /// </summary>
    [Serializable]
    public class ArcDTO
    {
        /// <summary>
        /// Unique arc identifier (UUID)
        /// </summary>
        [JsonProperty("id")]
        public string Id { get; set; }
        
        /// <summary>
        /// Arc title/name
        /// </summary>
        [JsonProperty("title")]
        public string Title { get; set; }
        
        /// <summary>
        /// Brief arc description
        /// </summary>
        [JsonProperty("description")]
        public string Description { get; set; }
        
        /// <summary>
        /// Type of arc (global, regional, character, npc)
        /// </summary>
        [JsonProperty("type")]
        public string Type { get; set; }
        
        /// <summary>
        /// Current status of the arc
        /// </summary>
        [JsonProperty("status")]
        public string Status { get; set; }
        
        /// <summary>
        /// Priority level
        /// </summary>
        [JsonProperty("priority")]
        public string Priority { get; set; }
        
        /// <summary>
        /// Arc steps/stages
        /// </summary>
        [JsonProperty("steps")]
        public List<ArcStepDTO> Steps { get; set; } = new List<ArcStepDTO>();
        
        /// <summary>
        /// Current step index
        /// </summary>
        [JsonProperty("current_step")]
        public int CurrentStep { get; set; } = 0;
        
        /// <summary>
        /// Overall progress percentage (0-100)
        /// </summary>
        [JsonProperty("progress_percentage")]
        public float ProgressPercentage { get; set; } = 0f;
        
        /// <summary>
        /// Arc completion criteria
        /// </summary>
        [JsonProperty("completion_criteria")]
        public Dictionary<string, object> CompletionCriteria { get; set; } = new Dictionary<string, object>();
        
        /// <summary>
        /// Arc triggers and conditions
        /// </summary>
        [JsonProperty("trigger_conditions")]
        public List<Dictionary<string, object>> TriggerConditions { get; set; } = new List<Dictionary<string, object>>();
        
        /// <summary>
        /// Related character IDs for character arcs
        /// </summary>
        [JsonProperty("character_ids")]
        public List<string> CharacterIds { get; set; } = new List<string>();
        
        /// <summary>
        /// Related faction IDs for faction arcs
        /// </summary>
        [JsonProperty("faction_ids")]
        public List<string> FactionIds { get; set; } = new List<string>();
        
        /// <summary>
        /// Related region IDs for regional arcs
        /// </summary>
        [JsonProperty("region_ids")]
        public List<string> RegionIds { get; set; } = new List<string>();
        
        /// <summary>
        /// Related quest IDs that are part of this arc
        /// </summary>
        [JsonProperty("quest_ids")]
        public List<string> QuestIds { get; set; } = new List<string>();
        
        /// <summary>
        /// Arc metadata for additional data
        /// </summary>
        [JsonProperty("metadata")]
        public Dictionary<string, object> Metadata { get; set; } = new Dictionary<string, object>();
        
        /// <summary>
        /// Arc tags for categorization
        /// </summary>
        [JsonProperty("tags")]
        public List<string> Tags { get; set; } = new List<string>();
        
        /// <summary>
        /// Arc outcomes and consequences
        /// </summary>
        [JsonProperty("outcomes")]
        public List<Dictionary<string, object>> Outcomes { get; set; } = new List<Dictionary<string, object>>();
        
        /// <summary>
        /// Arc relationships with other arcs
        /// </summary>
        [JsonProperty("arc_relationships")]
        public Dictionary<string, object> ArcRelationships { get; set; } = new Dictionary<string, object>();
        
        /// <summary>
        /// When the arc was created
        /// </summary>
        [JsonProperty("created_at")]
        public DateTime CreatedAt { get; set; }
        
        /// <summary>
        /// When the arc was last updated
        /// </summary>
        [JsonProperty("updated_at")]
        public DateTime UpdatedAt { get; set; }
        
        /// <summary>
        /// When the arc was started
        /// </summary>
        [JsonProperty("started_at")]
        public DateTime? StartedAt { get; set; }
        
        /// <summary>
        /// When the arc was completed
        /// </summary>
        [JsonProperty("completed_at")]
        public DateTime? CompletedAt { get; set; }
        
        /// <summary>
        /// Estimated completion time
        /// </summary>
        [JsonProperty("estimated_completion_time")]
        public TimeSpan? EstimatedCompletionTime { get; set; }
        
        /// <summary>
        /// Arc difficulty level
        /// </summary>
        [JsonProperty("difficulty_level")]
        public int DifficultyLevel { get; set; } = 1;
        
        /// <summary>
        /// Maximum progression rate per day
        /// </summary>
        [JsonProperty("max_progression_rate")]
        public float MaxProgressionRate { get; set; } = 1.0f;
        
        /// <summary>
        /// Auto-progression enabled
        /// </summary>
        [JsonProperty("auto_progression")]
        public bool AutoProgression { get; set; } = false;
    }
    
    /// <summary>
    /// Data Transfer Object for Arc Step API communication
    /// </summary>
    [Serializable]
    public class ArcStepDTO
    {
        /// <summary>
        /// Step ID within the arc
        /// </summary>
        [JsonProperty("id")]
        public int Id { get; set; }
        
        /// <summary>
        /// Step title
        /// </summary>
        [JsonProperty("title")]
        public string Title { get; set; }
        
        /// <summary>
        /// Step description
        /// </summary>
        [JsonProperty("description")]
        public string Description { get; set; }
        
        /// <summary>
        /// Step type (narrative, action, choice, etc.)
        /// </summary>
        [JsonProperty("type")]
        public string Type { get; set; }
        
        /// <summary>
        /// Whether the step is completed
        /// </summary>
        [JsonProperty("completed")]
        public bool Completed { get; set; } = false;
        
        /// <summary>
        /// Step order within the arc
        /// </summary>
        [JsonProperty("order")]
        public int Order { get; set; }
        
        /// <summary>
        /// Step completion criteria
        /// </summary>
        [JsonProperty("completion_criteria")]
        public Dictionary<string, object> CompletionCriteria { get; set; } = new Dictionary<string, object>();
        
        /// <summary>
        /// Step trigger conditions
        /// </summary>
        [JsonProperty("trigger_conditions")]
        public List<Dictionary<string, object>> TriggerConditions { get; set; } = new List<Dictionary<string, object>>();
        
        /// <summary>
        /// Step outcomes and effects
        /// </summary>
        [JsonProperty("outcomes")]
        public List<Dictionary<string, object>> Outcomes { get; set; } = new List<Dictionary<string, object>>();
        
        /// <summary>
        /// Related quest IDs for this step
        /// </summary>
        [JsonProperty("related_quest_ids")]
        public List<string> RelatedQuestIds { get; set; } = new List<string>();
        
        /// <summary>
        /// Step duration estimate
        /// </summary>
        [JsonProperty("duration_estimate")]
        public TimeSpan? DurationEstimate { get; set; }
        
        /// <summary>
        /// Whether this step is optional
        /// </summary>
        [JsonProperty("is_optional")]
        public bool IsOptional { get; set; } = false;
        
        /// <summary>
        /// Step progress percentage (0-100)
        /// </summary>
        [JsonProperty("progress_percentage")]
        public float ProgressPercentage { get; set; } = 0f;
        
        /// <summary>
        /// Step metadata
        /// </summary>
        [JsonProperty("metadata")]
        public Dictionary<string, object> Metadata { get; set; } = new Dictionary<string, object>();
        
        // UI compatibility properties
        /// <summary>
        /// UI-compatible property for Completed
        /// </summary>
        public bool IsCompleted => Completed;
        
        /// <summary>
        /// UI-compatible property for duration in days
        /// </summary>
        public double? EstimatedDurationDays => DurationEstimate?.TotalDays;
        
        /// <summary>
        /// UI-compatible started timestamp (derived from metadata)
        /// </summary>
        public DateTime? StartedAt 
        {
            get
            {
                if (Metadata?.ContainsKey("started_at") == true && Metadata["started_at"] != null)
                {
                    if (DateTime.TryParse(Metadata["started_at"].ToString(), out var result))
                        return result;
                }
                return null;
            }
        }
    }
    
    /// <summary>
    /// Arc creation request DTO
    /// </summary>
    [Serializable]
    public class CreateArcRequestDTO
    {
        [JsonProperty("title")]
        public string Title { get; set; }
        
        [JsonProperty("description")]
        public string Description { get; set; }
        
        [JsonProperty("type")]
        public string Type { get; set; }
        
        [JsonProperty("priority")]
        public string Priority { get; set; }
        
        [JsonProperty("character_ids")]
        public List<string> CharacterIds { get; set; } = new List<string>();
        
        [JsonProperty("faction_ids")]
        public List<string> FactionIds { get; set; } = new List<string>();
        
        [JsonProperty("region_ids")]
        public List<string> RegionIds { get; set; } = new List<string>();
        
        [JsonProperty("tags")]
        public List<string> Tags { get; set; } = new List<string>();
        
        [JsonProperty("difficulty_level")]
        public int DifficultyLevel { get; set; } = 1;
        
        [JsonProperty("auto_progression")]
        public bool AutoProgression { get; set; } = false;
        
        [JsonProperty("metadata")]
        public Dictionary<string, object> Metadata { get; set; } = new Dictionary<string, object>();
    }
    
    /// <summary>
    /// Arc update request DTO
    /// </summary>
    [Serializable]
    public class UpdateArcRequestDTO
    {
        [JsonProperty("status")]
        public string Status { get; set; }
        
        [JsonProperty("current_step")]
        public int? CurrentStep { get; set; }
        
        [JsonProperty("progress_percentage")]
        public float? ProgressPercentage { get; set; }
        
        [JsonProperty("step_updates")]
        public List<ArcStepUpdateDTO> StepUpdates { get; set; } = new List<ArcStepUpdateDTO>();
        
        [JsonProperty("metadata")]
        public Dictionary<string, object> Metadata { get; set; }
    }
    
    /// <summary>
    /// Arc step update DTO
    /// </summary>
    [Serializable]
    public class ArcStepUpdateDTO
    {
        [JsonProperty("step_id")]
        public int StepId { get; set; }
        
        [JsonProperty("completed")]
        public bool Completed { get; set; }
        
        [JsonProperty("progress_percentage")]
        public float ProgressPercentage { get; set; }
        
        [JsonProperty("metadata")]
        public Dictionary<string, object> Metadata { get; set; }
    }
    
    /// <summary>
    /// Arc progression response DTO
    /// </summary>
    [Serializable]
    public class ArcProgressionResponseDTO
    {
        [JsonProperty("arc_id")]
        public string ArcId { get; set; }
        
        [JsonProperty("previous_step")]
        public int PreviousStep { get; set; }
        
        [JsonProperty("current_step")]
        public int CurrentStep { get; set; }
        
        [JsonProperty("progress_percentage")]
        public float ProgressPercentage { get; set; }
        
        [JsonProperty("completed")]
        public bool Completed { get; set; }
        
        [JsonProperty("triggered_events")]
        public List<Dictionary<string, object>> TriggeredEvents { get; set; } = new List<Dictionary<string, object>>();
        
        [JsonProperty("unlocked_quests")]
        public List<string> UnlockedQuests { get; set; } = new List<string>();
        
        [JsonProperty("narrative_updates")]
        public List<string> NarrativeUpdates { get; set; } = new List<string>();
    }

    /// <summary>
    /// Alias for ArcProgressionResponseDTO to match expected naming
    /// </summary>
    [Serializable]
    public class ArcProgressionDTO : ArcProgressionResponseDTO
    {
        public ArcProgressionDTO() : base() { }
    }
} 