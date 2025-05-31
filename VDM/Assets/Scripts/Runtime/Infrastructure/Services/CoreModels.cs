using System;
using UnityEngine;

namespace VDM.Infrastructure.Core.Core.Models
{
    /// <summary>
    /// Memory summary data transfer object
    /// </summary>
    [Serializable]
    public class MemorySummaryDTO
    {
        public string CharacterId { get; set; }
        public int TotalMemories { get; set; }
        public int RecentMemories { get; set; }
        public DateTime LastUpdated { get; set; } = DateTime.UtcNow;
    }
    
    /// <summary>
    /// Recall memory request
    /// </summary>
    [Serializable]
    public class RecallMemoryRequestDTO
    {
        public string CharacterId { get; set; }
        public string Query { get; set; }
        public int MaxResults { get; set; } = 10;
    }
    
    /// <summary>
    /// Reinforce memory request
    /// </summary>
    [Serializable]
    public class ReinforceMemoryRequestDTO
    {
        public string MemoryId { get; set; }
        public float StrengthIncrease { get; set; } = 0.1f;
    }
    
    /// <summary>
    /// Forget memory request
    /// </summary>
    [Serializable]
    public class ForgetMemoryRequestDTO
    {
        public string MemoryId { get; set; }
        public bool Permanent { get; set; } = false;
    }
} 