using System;
using System.Collections.Generic;
using Newtonsoft.Json;

namespace VDM.Systems.Memory.Models
{
    /// <summary>
    /// Memory response data transfer object
    /// </summary>
    [Serializable]
    public class MemoryResponseDTO
    {
        [JsonProperty("id")]
        public string Id { get; set; } = string.Empty;

        [JsonProperty("character_id")]
        public string CharacterId { get; set; } = string.Empty;

        [JsonProperty("content")]
        public string Content { get; set; } = string.Empty;

        [JsonProperty("importance")]
        public int Importance { get; set; } = 0;

        [JsonProperty("emotional_weight")]
        public float EmotionalWeight { get; set; } = 0f;

        [JsonProperty("category")]
        public string Category { get; set; } = string.Empty;

        [JsonProperty("created_at")]
        public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

        [JsonProperty("last_accessed")]
        public DateTime LastAccessed { get; set; } = DateTime.UtcNow;

        [JsonProperty("access_count")]
        public int AccessCount { get; set; } = 0;

        [JsonProperty("tags")]
        public List<string> Tags { get; set; } = new List<string>();

        [JsonProperty("associated_entities")]
        public List<string> AssociatedEntities { get; set; } = new List<string>();
    }

    /// <summary>
    /// Request DTO for creating a new memory
    /// </summary>
    [Serializable]
    public class CreateMemoryRequestDTO
    {
        [JsonProperty("character_id")]
        public string CharacterId { get; set; } = string.Empty;

        [JsonProperty("content")]
        public string Content { get; set; } = string.Empty;

        [JsonProperty("importance")]
        public int Importance { get; set; } = 5; // Default importance level

        [JsonProperty("emotional_weight")]
        public float EmotionalWeight { get; set; } = 0f;

        [JsonProperty("category")]
        public string Category { get; set; } = "general";

        [JsonProperty("tags")]
        public List<string> Tags { get; set; } = new List<string>();

        [JsonProperty("associated_entities")]
        public List<string> AssociatedEntities { get; set; } = new List<string>();

        [JsonProperty("trigger_event")]
        public string TriggerEvent { get; set; } = string.Empty;

        [JsonProperty("context")]
        public string Context { get; set; } = string.Empty;
    }

    /// <summary>
    /// Request DTO for recalling a memory
    /// </summary>
    [Serializable]
    public class RecallMemoryRequestDTO
    {
        [JsonProperty("character_id")]
        public string CharacterId { get; set; } = string.Empty;

        [JsonProperty("memory_id")]
        public string MemoryId { get; set; } = string.Empty;

        [JsonProperty("recall_context")]
        public string RecallContext { get; set; } = string.Empty;

        [JsonProperty("emotional_state")]
        public string EmotionalState { get; set; } = string.Empty;

        [JsonProperty("trigger_event")]
        public string TriggerEvent { get; set; } = string.Empty;
    }

    /// <summary>
    /// Request DTO for reinforcing a memory
    /// </summary>
    [Serializable]
    public class ReinforceMemoryRequestDTO
    {
        [JsonProperty("character_id")]
        public string CharacterId { get; set; } = string.Empty;

        [JsonProperty("memory_id")]
        public string MemoryId { get; set; } = string.Empty;

        [JsonProperty("reinforcement_strength")]
        public float ReinforcementStrength { get; set; } = 1.0f;

        [JsonProperty("emotional_context")]
        public string EmotionalContext { get; set; } = string.Empty;

        [JsonProperty("additional_details")]
        public string AdditionalDetails { get; set; } = string.Empty;
    }

    /// <summary>
    /// Request DTO for forgetting a memory
    /// </summary>
    [Serializable]
    public class ForgetMemoryRequestDTO
    {
        [JsonProperty("character_id")]
        public string CharacterId { get; set; } = string.Empty;

        [JsonProperty("memory_id")]
        public string MemoryId { get; set; } = string.Empty;

        [JsonProperty("forget_method")]
        public string ForgetMethod { get; set; } = "natural"; // natural, forced, modified

        [JsonProperty("preserve_core_details")]
        public bool PreserveCoreDetails { get; set; } = false;

        [JsonProperty("reason")]
        public string Reason { get; set; } = string.Empty;
    }

    /// <summary>
    /// Memory summary response DTO
    /// </summary>
    [Serializable]
    public class MemorySummaryResponseDTO
    {
        [JsonProperty("character_id")]
        public string CharacterId { get; set; } = string.Empty;

        [JsonProperty("total_memories")]
        public int TotalMemories { get; set; } = 0;

        [JsonProperty("recent_memories")]
        public int RecentMemories { get; set; } = 0;

        [JsonProperty("important_memories")]
        public int ImportantMemories { get; set; } = 0;

        [JsonProperty("summary")]
        public MemorySummaryDTO Summary { get; set; } = new MemorySummaryDTO();

        [JsonProperty("categories")]
        public Dictionary<string, int> Categories { get; set; } = new Dictionary<string, int>();

        [JsonProperty("recent_activity")]
        public List<MemoryActivityDTO> RecentActivity { get; set; } = new List<MemoryActivityDTO>();
    }

    /// <summary>
    /// Memory list response DTO
    /// </summary>
    [Serializable]
    public class MemoryListResponseDTO
    {
        [JsonProperty("character_id")]
        public string CharacterId { get; set; } = string.Empty;

        [JsonProperty("memories")]
        public List<MemoryResponseDTO> Memories { get; set; } = new List<MemoryResponseDTO>();

        [JsonProperty("total_count")]
        public int TotalCount { get; set; } = 0;

        [JsonProperty("page")]
        public int Page { get; set; } = 1;

        [JsonProperty("page_size")]
        public int PageSize { get; set; } = 20;

        [JsonProperty("filters_applied")]
        public Dictionary<string, object> FiltersApplied { get; set; } = new Dictionary<string, object>();
    }

    /// <summary>
    /// Memory activity DTO for tracking recent memory interactions
    /// </summary>
    [Serializable]
    public class MemoryActivityDTO
    {
        [JsonProperty("memory_id")]
        public string MemoryId { get; set; } = string.Empty;

        [JsonProperty("activity_type")]
        public string ActivityType { get; set; } = string.Empty; // created, accessed, modified, reinforced, forgotten

        [JsonProperty("timestamp")]
        public DateTime Timestamp { get; set; } = DateTime.UtcNow;

        [JsonProperty("details")]
        public string Details { get; set; } = string.Empty;
    }
} 