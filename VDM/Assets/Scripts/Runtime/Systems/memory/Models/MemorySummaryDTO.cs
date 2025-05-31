using System;
using System.Collections.Generic;
using Newtonsoft.Json;

namespace VDM.Systems.Memory.Models
{
    /// <summary>
    /// Memory summary data transfer object for Unity frontend
    /// </summary>
    [Serializable]
    public class MemorySummaryDTO
    {
        [JsonProperty("character_id")]
        public string CharacterId { get; set; } = string.Empty;

        [JsonProperty("total_memories")]
        public int TotalMemories { get; set; } = 0;

        [JsonProperty("recent_memories")]
        public int RecentMemories { get; set; } = 0;

        [JsonProperty("important_memories")]
        public int ImportantMemories { get; set; } = 0;

        [JsonProperty("memory_categories")]
        public Dictionary<string, int> MemoryCategories { get; set; } = new Dictionary<string, int>();

        [JsonProperty("last_memory_created")]
        public DateTime LastMemoryCreated { get; set; } = DateTime.MinValue;

        [JsonProperty("memory_strength_average")]
        public float MemoryStrengthAverage { get; set; } = 0.5f;

        [JsonProperty("emotional_context_summary")]
        public Dictionary<string, int> EmotionalContextSummary { get; set; } = new Dictionary<string, int>();

        [JsonProperty("relationship_memories")]
        public int RelationshipMemories { get; set; } = 0;

        [JsonProperty("event_memories")]
        public int EventMemories { get; set; } = 0;

        [JsonProperty("knowledge_memories")]
        public int KnowledgeMemories { get; set; } = 0;
    }
} 