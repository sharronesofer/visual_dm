using Newtonsoft.Json;
using System.Collections.Generic;
using System;
using UnityEngine;


namespace VDM.Runtime.Quest.Models
{
    /// <summary>
    /// Data Transfer Object for Quest API communication matching backend quest models
    /// </summary>
    [Serializable]
    public class QuestDTO
    {
        /// <summary>
        /// Unique identifier for the quest (UUID)
        /// </summary>
        [JsonProperty("id")]
        public string Id { get; set; }
        
        /// <summary>
        /// Display title of the quest
        /// </summary>
        [JsonProperty("title")]
        public string Title { get; set; }
        
        /// <summary>
        /// Brief description of the quest
        /// </summary>
        [JsonProperty("description")]
        public string Description { get; set; }
        
        /// <summary>
        /// Quest type (main, side, faction, character, etc.)
        /// </summary>
        [JsonProperty("type")]
        public string Type { get; set; }
        
        /// <summary>
        /// Current status of the quest
        /// </summary>
        [JsonProperty("status")]
        public string Status { get; set; }
        
        /// <summary>
        /// Priority level (low, medium, high, urgent)
        /// </summary>
        [JsonProperty("priority")]
        public string Priority { get; set; }
        
        /// <summary>
        /// Quest steps/stages
        /// </summary>
        [JsonProperty("steps")]
        public List<QuestStepDTO> Steps { get; set; } = new List<QuestStepDTO>();
        
        /// <summary>
        /// Quest requirements (level, items, etc.)
        /// </summary>
        [JsonProperty("requirements")]
        public Dictionary<string, object> Requirements { get; set; } = new Dictionary<string, object>();
        
        /// <summary>
        /// Quest rewards
        /// </summary>
        [JsonProperty("rewards")]
        public Dictionary<string, object> Rewards { get; set; } = new Dictionary<string, object>();
        
        /// <summary>
        /// IDs of prerequisite quests
        /// </summary>
        [JsonProperty("prerequisite_quest_ids")]
        public List<string> PrerequisiteQuestIds { get; set; } = new List<string>();
        
        /// <summary>
        /// Quest giver NPC ID
        /// </summary>
        [JsonProperty("quest_giver_id")]
        public string QuestGiverId { get; set; }
        
        /// <summary>
        /// Quest turn-in NPC ID
        /// </summary>
        [JsonProperty("quest_turn_in_id")]
        public string QuestTurnInId { get; set; }
        
        /// <summary>
        /// Tags for categorization
        /// </summary>
        [JsonProperty("tags")]
        public List<string> Tags { get; set; } = new List<string>();
        
        /// <summary>
        /// Whether this is a repeatable quest
        /// </summary>
        [JsonProperty("is_repeatable")]
        public bool IsRepeatable { get; set; } = false;
        
        /// <summary>
        /// Minimum level required
        /// </summary>
        [JsonProperty("min_level")]
        public int MinLevel { get; set; } = 1;
        
        /// <summary>
        /// Maximum level for scaling
        /// </summary>
        [JsonProperty("max_level")]
        public int MaxLevel { get; set; } = 100;
        
        /// <summary>
        /// Whether quest auto-completes
        /// </summary>
        [JsonProperty("auto_complete")]
        public bool AutoComplete { get; set; } = false;
        
        /// <summary>
        /// Cooldown time before quest can be repeated (in hours)
        /// </summary>
        [JsonProperty("repeat_cooldown_hours")]
        public float RepeatCooldownHours { get; set; } = 24f;
        
        /// <summary>
        /// When the quest was created
        /// </summary>
        [JsonProperty("created_at")]
        public DateTime CreatedAt { get; set; }
        
        /// <summary>
        /// When the quest was last updated
        /// </summary>
        [JsonProperty("updated_at")]
        public DateTime UpdatedAt { get; set; }
        
        /// <summary>
        /// Quest metadata for additional data
        /// </summary>
        [JsonProperty("metadata")]
        public Dictionary<string, object> Metadata { get; set; } = new Dictionary<string, object>();
        
        /// <summary>
        /// Related arc ID if quest is part of an arc
        /// </summary>
        [JsonProperty("arc_id")]
        public string ArcId { get; set; }
        
        /// <summary>
        /// Related faction ID if this is a faction quest
        /// </summary>
        [JsonProperty("faction_id")]
        public string FactionId { get; set; }
        
        /// <summary>
        /// Related region ID where quest takes place
        /// </summary>
        [JsonProperty("region_id")]
        public string RegionId { get; set; }
        
        /// <summary>
        /// Progress tracking data
        /// </summary>
        [JsonProperty("progress_data")]
        public Dictionary<string, object> ProgressData { get; set; } = new Dictionary<string, object>();
    }
    
    /// <summary>
    /// Data Transfer Object for Quest Step API communication
    /// </summary>
    [Serializable]
    public class QuestStepDTO
    {
        /// <summary>
        /// Step ID within the quest
        /// </summary>
        [JsonProperty("id")]
        public int Id { get; set; }
        
        /// <summary>
        /// Step description
        /// </summary>
        [JsonProperty("description")]
        public string Description { get; set; }
        
        /// <summary>
        /// Step type (dialogue, collect, visit, kill, etc.)
        /// </summary>
        [JsonProperty("type")]
        public string Type { get; set; }
        
        /// <summary>
        /// Whether the step is completed
        /// </summary>
        [JsonProperty("completed")]
        public bool Completed { get; set; } = false;
        
        /// <summary>
        /// Required items for this step
        /// </summary>
        [JsonProperty("required_items")]
        public List<Dictionary<string, object>> RequiredItems { get; set; } = new List<Dictionary<string, object>>();
        
        /// <summary>
        /// Required skills for this step
        /// </summary>
        [JsonProperty("required_skills")]
        public List<Dictionary<string, object>> RequiredSkills { get; set; } = new List<Dictionary<string, object>>();
        
        /// <summary>
        /// Target NPC ID for this step
        /// </summary>
        [JsonProperty("target_npc_id")]
        public string TargetNpcId { get; set; }
        
        /// <summary>
        /// Target location ID for this step
        /// </summary>
        [JsonProperty("target_location_id")]
        public string TargetLocationId { get; set; }
        
        /// <summary>
        /// Target item ID for collection steps
        /// </summary>
        [JsonProperty("target_item_id")]
        public string TargetItemId { get; set; }
        
        /// <summary>
        /// Target enemy ID for combat steps
        /// </summary>
        [JsonProperty("target_enemy_id")]
        public string TargetEnemyId { get; set; }
        
        /// <summary>
        /// Target enemy type for combat steps
        /// </summary>
        [JsonProperty("target_enemy_type")]
        public string TargetEnemyType { get; set; }
        
        /// <summary>
        /// Required quantity for completion
        /// </summary>
        [JsonProperty("quantity")]
        public int Quantity { get; set; } = 1;
        
        /// <summary>
        /// Required count for completion
        /// </summary>
        [JsonProperty("required_count")]
        public int RequiredCount { get; set; } = 1;
        
        /// <summary>
        /// Current progress count
        /// </summary>
        [JsonProperty("current_count")]
        public int CurrentCount { get; set; } = 0;
        
        /// <summary>
        /// Time requirement data
        /// </summary>
        [JsonProperty("time_requirement")]
        public Dictionary<string, object> TimeRequirement { get; set; }
        
        /// <summary>
        /// Step order within the quest
        /// </summary>
        [JsonProperty("order")]
        public int Order { get; set; }
        
        /// <summary>
        /// Whether this step is optional
        /// </summary>
        [JsonProperty("is_optional")]
        public bool IsOptional { get; set; } = false;
    }
    
    /// <summary>
    /// Quest creation request DTO
    /// </summary>
    [Serializable]
    public class CreateQuestRequestDTO
    {
        [JsonProperty("title")]
        public string Title { get; set; }
        
        [JsonProperty("description")]
        public string Description { get; set; }
        
        [JsonProperty("type")]
        public string Type { get; set; }
        
        [JsonProperty("priority")]
        public string Priority { get; set; }
        
        [JsonProperty("quest_giver_id")]
        public string QuestGiverId { get; set; }
        
        [JsonProperty("requirements")]
        public Dictionary<string, object> Requirements { get; set; } = new Dictionary<string, object>();
        
        [JsonProperty("rewards")]
        public Dictionary<string, object> Rewards { get; set; } = new Dictionary<string, object>();
        
        [JsonProperty("tags")]
        public List<string> Tags { get; set; } = new List<string>();
        
        [JsonProperty("arc_id")]
        public string ArcId { get; set; }
        
        [JsonProperty("faction_id")]
        public string FactionId { get; set; }
        
        [JsonProperty("region_id")]
        public string RegionId { get; set; }
    }
    
    /// <summary>
    /// Quest update request DTO
    /// </summary>
    [Serializable]
    public class UpdateQuestRequestDTO
    {
        [JsonProperty("status")]
        public string Status { get; set; }
        
        [JsonProperty("progress_data")]
        public Dictionary<string, object> ProgressData { get; set; }
        
        [JsonProperty("step_updates")]
        public List<QuestStepUpdateDTO> StepUpdates { get; set; } = new List<QuestStepUpdateDTO>();
    }
    
    /// <summary>
    /// Quest step update DTO
    /// </summary>
    [Serializable]
    public class QuestStepUpdateDTO
    {
        [JsonProperty("step_id")]
        public int StepId { get; set; }
        
        [JsonProperty("completed")]
        public bool Completed { get; set; }
        
        [JsonProperty("current_count")]
        public int CurrentCount { get; set; }
    }
} 