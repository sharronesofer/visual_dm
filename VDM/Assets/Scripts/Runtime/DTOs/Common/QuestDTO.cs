using System;
using System.Collections.Generic;
using VDM.DTOs.Core.Shared;

namespace VDM.DTOs.Content.Quest
{
    /// <summary>
    /// Base DTO for quest system with common fields
    /// </summary>
    [Serializable]
    public abstract class QuestBaseDTO : MetadataDTO
    {
        public bool IsActive { get; set; } = true;
    }

    /// <summary>
    /// Primary DTO for quest system
    /// </summary>
    [Serializable]
    public class QuestDTO : QuestBaseDTO
    {
        public string Name { get; set; } = string.Empty;
        public string Description { get; set; }
        public string Status { get; set; } = "available";
        public Dictionary<string, object> Properties { get; set; } = new Dictionary<string, object>();
        public string QuestType { get; set; } = "main";
        public int LevelRequirement { get; set; } = 1;
        public List<string> Prerequisites { get; set; } = new List<string>();
        public List<QuestObjectiveDTO> Objectives { get; set; } = new List<QuestObjectiveDTO>();
        public List<QuestRewardDTO> Rewards { get; set; } = new List<QuestRewardDTO>();
        public string GiverId { get; set; }
        public string LocationId { get; set; }
        public TimeSpan? TimeLimit { get; set; }
        public bool IsRepeatable { get; set; } = false;
        public int CompletionCount { get; set; } = 0;
    }

    /// <summary>
    /// Request DTO for creating quest
    /// </summary>
    [Serializable]
    public class CreateQuestRequestDTO
    {
        public string Name { get; set; } = string.Empty;
        public string Description { get; set; }
        public Dictionary<string, object> Properties { get; set; } = new Dictionary<string, object>();
        public string QuestType { get; set; } = "main";
        public int LevelRequirement { get; set; } = 1;
        public List<string> Prerequisites { get; set; } = new List<string>();
        public string GiverId { get; set; }
        public string LocationId { get; set; }
        public TimeSpan? TimeLimit { get; set; }
        public bool IsRepeatable { get; set; } = false;
    }

    /// <summary>
    /// Request DTO for updating quest
    /// </summary>
    [Serializable]
    public class UpdateQuestRequestDTO
    {
        public string Name { get; set; }
        public string Description { get; set; }
        public string Status { get; set; }
        public Dictionary<string, object> Properties { get; set; }
        public string QuestType { get; set; }
        public int? LevelRequirement { get; set; }
        public string GiverId { get; set; }
        public string LocationId { get; set; }
        public TimeSpan? TimeLimit { get; set; }
        public bool? IsRepeatable { get; set; }
    }

    /// <summary>
    /// Response DTO for quest
    /// </summary>
    [Serializable]
    public class QuestResponseDTO : SuccessResponseDTO
    {
        public QuestDTO Quest { get; set; } = new QuestDTO();
    }

    /// <summary>
    /// Response DTO for quest lists
    /// </summary>
    [Serializable]
    public class QuestListResponseDTO : SuccessResponseDTO
    {
        public List<QuestDTO> Quests { get; set; } = new List<QuestDTO>();
        public int Total { get; set; }
        public int Page { get; set; }
        public int Size { get; set; }
        public bool HasNext { get; set; }
        public bool HasPrev { get; set; }
    }

    /// <summary>
    /// Quest objective DTO for quest objectives
    /// </summary>
    [Serializable]
    public class QuestObjectiveDTO : QuestBaseDTO
    {
        public string ObjectiveId { get; set; } = string.Empty;
        public string QuestId { get; set; } = string.Empty;
        public string Title { get; set; } = string.Empty;
        public string Description { get; set; }
        public string ObjectiveType { get; set; } = "kill";
        public string TargetId { get; set; }
        public string TargetType { get; set; }
        public int TargetCount { get; set; } = 1;
        public int CurrentCount { get; set; } = 0;
        public bool IsCompleted { get; set; } = false;
        public DateTime? CompletionDate { get; set; }
        public int OrderIndex { get; set; } = 0;
        public bool IsOptional { get; set; } = false;
    }

    /// <summary>
    /// Quest reward DTO for quest rewards
    /// </summary>
    [Serializable]
    public class QuestRewardDTO : QuestBaseDTO
    {
        public string RewardId { get; set; } = string.Empty;
        public string QuestId { get; set; } = string.Empty;
        public string RewardType { get; set; } = "experience";
        public string ItemId { get; set; }
        public int Quantity { get; set; } = 1;
        public int ExperiencePoints { get; set; } = 0;
        public int GoldAmount { get; set; } = 0;
        public bool IsOptional { get; set; } = false;
        public Dictionary<string, object> Conditions { get; set; } = new Dictionary<string, object>();
    }

    /// <summary>
    /// Quest progress DTO for tracking quest progress
    /// </summary>
    [Serializable]
    public class QuestProgressDTO : QuestBaseDTO
    {
        public string CharacterId { get; set; } = string.Empty;
        public string QuestId { get; set; } = string.Empty;
        public string Status { get; set; } = "in_progress";
        public DateTime StartDate { get; set; } = DateTime.UtcNow;
        public DateTime? CompletionDate { get; set; }
        public List<ObjectiveProgressDTO> ObjectiveProgress { get; set; } = new List<ObjectiveProgressDTO>();
        public string Notes { get; set; }
        public int CurrentStep { get; set; } = 0;
        public float CompletionPercentage { get; set; } = 0f;
    }

    /// <summary>
    /// Objective progress DTO for tracking individual objective progress
    /// </summary>
    [Serializable]
    public class ObjectiveProgressDTO : MetadataDTO
    {
        public string ObjectiveId { get; set; } = string.Empty;
        public int CurrentCount { get; set; } = 0;
        public bool IsCompleted { get; set; } = false;
        public DateTime? CompletionDate { get; set; }
        public string Notes { get; set; }
    }
} 