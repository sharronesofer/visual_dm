using System;

namespace VisualDM.Systems
{
    /// <summary>
    /// Types of social skills used in social checks.
    /// </summary>
    public enum SocialSkillType
    {
        Persuasion,
        Deception,
        Intimidation,
        Insight,
        Performance,
        Other
    }

    /// <summary>
    /// Result of a social check, including outcome and details.
    /// </summary>
    public class SocialCheckResult
    {
        public bool Success { get; set; }
        public float Roll { get; set; }
        public float Difficulty { get; set; }
        public SocialSkillType SkillType { get; set; }
        public string InfoType { get; set; } // e.g., Flattery, Warning, etc.
        public string Notes { get; set; } // Additional context or debug info
    }

    /// <summary>
    /// Represents a social check attempt between a player and an NPC.
    /// </summary>
    public class SocialCheck
    {
        public string PlayerId { get; set; }
        public string NpcId { get; set; }
        public SocialSkillType SkillType { get; set; }
        public string InfoType { get; set; }
        public float BaseDifficulty { get; set; }
        public float Modifier { get; set; }
        public DateTime Timestamp { get; set; }
        public SocialCheckResult Result { get; set; }
    }
}