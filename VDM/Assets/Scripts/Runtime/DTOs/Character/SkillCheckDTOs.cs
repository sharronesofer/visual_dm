using System;
using System.Collections.Generic;

namespace VDM.DTOs.Character
{
    /// <summary>
    /// Request DTO for initiating a skill check with multiple options.
    /// </summary>
    [Serializable]
    public class SkillCheckRequestDTO
    {
        public string CharacterId { get; set; }
        public string Context { get; set; }
        public List<string> EnvironmentalConditions { get; set; } = new List<string>();
        public List<SkillCheckOptionDTO> SkillOptions { get; set; } = new List<SkillCheckOptionDTO>();
    }

    /// <summary>
    /// Individual skill option for a skill check request.
    /// </summary>
    [Serializable]
    public class SkillCheckOptionDTO
    {
        public string SkillName { get; set; }
        public string OptionText { get; set; }
        public int DC { get; set; }
        public string Description { get; set; }
        public List<string> EnvironmentalConditions { get; set; } = new List<string>();
        public List<int> Modifiers { get; set; } = new List<int>();
    }

    /// <summary>
    /// Result DTO for a completed skill check.
    /// </summary>
    [Serializable]
    public class SkillCheckResultDTO
    {
        public string SkillName { get; set; }
        public string CharacterId { get; set; }
        public object BaseRoll { get; set; } // Can be int or int[] for advantage/disadvantage
        public int SkillModifier { get; set; }
        public int FinalModifiers { get; set; }
        public int TotalRoll { get; set; }
        public int? DC { get; set; }
        public bool? Success { get; set; }
        public int DegreeOfSuccess { get; set; }
        public bool CriticalSuccess { get; set; }
        public bool CriticalFailure { get; set; }
        public string AdvantageType { get; set; } = "normal";
        public string Description { get; set; }
        public DateTime Timestamp { get; set; }
    }

    /// <summary>
    /// Result DTO for opposed skill checks.
    /// </summary>
    [Serializable]
    public class OpposedSkillCheckResultDTO
    {
        public SkillCheckResultDTO Character1Result { get; set; }
        public SkillCheckResultDTO Character2Result { get; set; }
        public bool Character1Wins { get; set; }
        public string Description { get; set; }
    }

    /// <summary>
    /// Result DTO for passive skill calculations.
    /// </summary>
    [Serializable]
    public class PassiveSkillResultDTO
    {
        public string SkillName { get; set; }
        public string CharacterId { get; set; }
        public int PassiveScore { get; set; }
        public int SkillModifier { get; set; }
        public int Modifiers { get; set; }
        public int AdvantageBonus { get; set; }
    }

    /// <summary>
    /// DTO for group skill check results.
    /// </summary>
    [Serializable]
    public class GroupSkillCheckResultDTO
    {
        public string SkillName { get; set; }
        public string Description { get; set; }
        public List<SkillCheckResultDTO> IndividualResults { get; set; } = new List<SkillCheckResultDTO>();
        public bool GroupSuccess { get; set; }
        public int SuccessCount { get; set; }
        public int FailureCount { get; set; }
        public float AverageRoll { get; set; }
        public int BestRoll { get; set; }
        public int WorstRoll { get; set; }
    }

    /// <summary>
    /// DTO for perception check results.
    /// </summary>
    [Serializable]
    public class PerceptionResultDTO
    {
        public SkillCheckResultDTO CheckResult { get; set; }
        public string PerceptionType { get; set; }
        public List<DetectedObjectDTO> DetectedObjects { get; set; } = new List<DetectedObjectDTO>();
        public List<DetectedObjectDTO> MissedObjects { get; set; } = new List<DetectedObjectDTO>();
        public Dictionary<string, string> AdditionalInfo { get; set; } = new Dictionary<string, string>();
    }

    /// <summary>
    /// DTO for objects that can be detected via perception.
    /// </summary>
    [Serializable]
    public class DetectedObjectDTO
    {
        public string Id { get; set; }
        public string Name { get; set; }
        public string Description { get; set; }
        public int DC { get; set; }
        public int Modifier { get; set; }
        public string Type { get; set; }
        public string BasicInfo { get; set; }
        public string DetailedInfo { get; set; }
    }

    /// <summary>
    /// DTO for stealth check results.
    /// </summary>
    [Serializable]
    public class StealthResultDTO
    {
        public SkillCheckResultDTO CheckResult { get; set; }
        public string StealthContext { get; set; }
        public List<string> DetectedBy { get; set; } = new List<string>(); // Character UUIDs
        public int StealthLevel { get; set; }
        public int? Duration { get; set; } // Minutes
    }

    /// <summary>
    /// DTO for social interaction results.
    /// </summary>
    [Serializable]
    public class SocialResultDTO
    {
        public SkillCheckResultDTO CheckResult { get; set; }
        public string InteractionType { get; set; }
        public string TargetReaction { get; set; }
        public int AttitudeChange { get; set; }
        public List<string> InformationGained { get; set; } = new List<string>();
        public List<string> Consequences { get; set; } = new List<string>();
    }

    /// <summary>
    /// DTO for investigation check results.
    /// </summary>
    [Serializable]
    public class InvestigationResultDTO
    {
        public SkillCheckResultDTO CheckResult { get; set; }
        public List<ClueDTO> DiscoveredClues { get; set; } = new List<ClueDTO>();
        public int TimeSpentMinutes { get; set; }
        public string InvestigationTarget { get; set; }
    }

    /// <summary>
    /// DTO for clues discovered during investigation.
    /// </summary>
    [Serializable]
    public class ClueDTO
    {
        public string Id { get; set; }
        public string Name { get; set; }
        public string Description { get; set; }
        public string Type { get; set; }
        public int DC { get; set; }
    }

    /// <summary>
    /// DTO for skill check modifiers.
    /// </summary>
    [Serializable]
    public class SkillCheckModifiersDTO
    {
        public int CircumstanceBonus { get; set; } = 0;
        public int EquipmentBonus { get; set; } = 0;
        public int MagicBonus { get; set; } = 0;
        public int EnvironmentalModifier { get; set; } = 0;
        public int SynergyBonus { get; set; } = 0;
        public int TimeModifier { get; set; } = 0;

        public int TotalModifier => CircumstanceBonus + EquipmentBonus + MagicBonus + 
                                   EnvironmentalModifier + SynergyBonus + TimeModifier;
    }

    /// <summary>
    /// DTO for skill check difficulty levels.
    /// </summary>
    [Serializable]
    public class SkillCheckDifficultyDTO
    {
        public string Name { get; set; }
        public int DC { get; set; }
        public string Description { get; set; }
    }

    /// <summary>
    /// DTO for environmental conditions that affect skill checks.
    /// </summary>
    [Serializable]
    public class EnvironmentalConditionDTO
    {
        public string Name { get; set; }
        public string Category { get; set; }
        public int Modifier { get; set; }
        public string Description { get; set; }
    }
} 