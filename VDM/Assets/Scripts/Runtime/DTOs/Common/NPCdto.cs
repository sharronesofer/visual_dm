using System;
using System.Collections.Generic;
using System.Linq;
using VDM.DTOs.Core.Shared;

namespace VDM.DTOs.Social.NPC
{
    // ===========================================
    // ENUMS - NPC and Social System Types
    // ===========================================

    public enum NPCGenderType
    {
        Male,
        Female,
        NonBinary,
        Other,
        Unknown
    }

    public enum NPCProfessionType
    {
        Artisan,
        Merchant,
        Scholar,
        Guard,
        Farmer,
        Noble,
        Soldier,
        Cleric,
        Entertainer,
        Criminal,
        Unemployed,
        Custom
    }

    public enum NPCRaceType
    {
        Human,
        Elf,
        Dwarf,
        Halfling,
        Gnome,
        Orc,
        Tiefling,
        Dragonborn,
        Custom
    }

    public enum NPCClassType
    {
        Fighter,
        Wizard,
        Rogue,
        Cleric,
        Ranger,
        Bard,
        Barbarian,
        Sorcerer,
        Warlock,
        Paladin,
        Commoner,
        Custom
    }

    public enum NPCPersonalityTrait
    {
        Brave,
        Cowardly,
        Loyal,
        Treacherous,
        Honest,
        Deceptive,
        Kind,
        Cruel,
        Wise,
        Foolish,
        Calm,
        Aggressive,
        Generous,
        Greedy,
        Optimistic,
        Pessimistic,
        Patient,
        Impatient,
        Curious,
        Indifferent
    }

    public enum NPCRelationshipType
    {
        Friend,
        Enemy,
        Rival,
        Ally,
        Neutral,
        Family,
        Romantic,
        Professional,
        Mentor,
        Student
    }

    public enum NPCMemoryImportance
    {
        Trivial = 1,
        Minor = 2,
        Moderate = 3,
        Important = 4,
        Significant = 5,
        Major = 6,
        Critical = 7,
        Crucial = 8,
        Vital = 9,
        LifeChanging = 10
    }

    public enum NPCStatusType
    {
        Active,
        Inactive,
        Dead,
        Missing,
        Traveling,
        Imprisoned,
        Retired
    }

    public enum NPCLoyaltyLevel
    {
        Hostile = -10,
        VeryNegative = -5,
        Negative = -3,
        Unfriendly = -1,
        Neutral = 0,
        Friendly = 1,
        Positive = 3,
        VeryPositive = 5,
        Loyal = 10
    }

    public enum RumorCategory
    {
        Personal,
        Political,
        Economic,
        Military,
        Social,
        Religious,
        Criminal,
        Supernatural,
        Historical,
        Gossip
    }

    public enum RumorVeracity
    {
        CompletelyFalse = 0,
        MostlyFalse = 25,
        PartiallyTrue = 50,
        MostlyTrue = 75,
        CompletelyTrue = 100
    }

    // ===========================================
    // CORE NPC DTOs
    // ===========================================

    public class NPCDT0 : MetadataDTO
    {
        public string NpcId { get; set; } = string.Empty;

        public string Name { get; set; } = string.Empty;

        public NPCGenderType? Gender { get; set; }

        public int? Age { get; set; }

        public NPCProfessionType? Profession { get; set; }

        public NPCRaceType? Race { get; set; }

        public NPCClassType? ClassType { get; set; }

        public List<NPCPersonalityTrait> PersonalityTraits { get; set; } = new();

        public string? Backstory { get; set; }

        public string? TravelMotive { get; set; }

        public NPCStatusType Status { get; set; } = NPCStatusType.Active;

        // Location Data
        public string? PoiId { get; set; }

        public string? RegionId { get; set; }

        public CoordinateDTO? Coordinates { get; set; }

        // Faction Data
        public string? FactionId { get; set; }

        public Dictionary<string, int> FactionScores { get; set; } = new();

        public List<string> FactionAffiliations { get; set; } = new();

        public Dictionary<string, string> FactionRoles { get; set; } = new();

        // Stats and Abilities
        public Dictionary<string, object> Stats { get; set; } = new();

        public Dictionary<string, int> Skills { get; set; } = new();

        public List<string> Abilities { get; set; } = new();

        // Social Data
        public Dictionary<string, NPCRelationshipDTO> Relationships { get; set; } = new();

        public Dictionary<string, int> LoyaltyScores { get; set; } = new();

        public Dictionary<string, int> Reputation { get; set; } = new();

        // Computed Properties
        public bool IsActive => Status == NPCStatusType.Active;
        public bool HasFaction => !string.IsNullOrEmpty(FactionId);
        public bool IsStationary => string.IsNullOrEmpty(TravelMotive);
        public int PrimaryFactionLoyalty => !string.IsNullOrEmpty(FactionId) && FactionScores.ContainsKey(FactionId) 
            ? FactionScores[FactionId] : 0;
        public string PersonalityDescription => string.Join(", ", PersonalityTraits);
    }

    public class NPCCreateRequestDTO
    {
        public string Name { get; set; } = string.Empty;

        public NPCGenderType? Gender { get; set; }

        public int? Age { get; set; }

        public NPCProfessionType? Profession { get; set; }

        public NPCRaceType? Race { get; set; }

        public NPCClassType? ClassType { get; set; }

        public List<NPCPersonalityTrait> PersonalityTraits { get; set; } = new();

        public string? Backstory { get; set; }

        public string? TravelMotive { get; set; }

        public string? PoiId { get; set; }

        public string? RegionId { get; set; }

        public string? FactionId { get; set; }

        public Dictionary<string, object> Stats { get; set; } = new();
    }

    public class NPCUpdateRequestDTO
    {
        public string? Name { get; set; }

        public NPCGenderType? Gender { get; set; }

        public int? Age { get; set; }

        public NPCProfessionType? Profession { get; set; }

        public List<NPCPersonalityTrait>? PersonalityTraits { get; set; }

        public string? Backstory { get; set; }

        public string? TravelMotive { get; set; }

        public string? PoiId { get; set; }

        public string? RegionId { get; set; }

        public string? FactionId { get; set; }

        public Dictionary<string, object>? Stats { get; set; }
    }

    public class NPCCreateResponseDTO : SuccessResponseDTO
    {
        public string NpcId { get; set; } = string.Empty;

        public NPCDT0 Npc { get; set; } = new();
    }

    // ===========================================
    // NPC RELATIONSHIP DTOs
    // ===========================================

    public class NPCRelationshipDTO
    {
        public string TargetId { get; set; } = string.Empty;

        public NPCRelationshipType RelationshipType { get; set; }

        public int Strength { get; set; } = 0;

        public string? Description { get; set; }

        public DateTime EstablishedDate { get; set; } = DateTime.UtcNow;

        public DateTime? LastInteraction { get; set; }

        public List<string> InteractionHistory { get; set; } = new();

        // Computed Properties
        public bool IsPositive => Strength > 0;
        public bool IsNegative => Strength < 0;
        public bool IsNeutral => Strength == 0;
        public string StrengthDescription => Strength switch
        {
            >= 80 => "Very Strong",
            >= 60 => "Strong",
            >= 40 => "Moderate",
            >= 20 => "Weak",
            > 0 => "Very Weak",
            0 => "Neutral",
            > -20 => "Slightly Negative",
            > -40 => "Negative",
            > -60 => "Very Negative",
            > -80 => "Hostile",
            _ => "Extremely Hostile"
        };
    }

    // ===========================================
    // NPC MEMORY DTOs
    // ===========================================

    public class NPCMemoryDTO : MetadataDTO
    {
        public string MemoryId { get; set; } = string.Empty;

        public string NpcId { get; set; } = string.Empty;

        public string Content { get; set; } = string.Empty;

        public NPCMemoryImportance Importance { get; set; } = NPCMemoryImportance.Moderate;

        public float DecayRate { get; set; } = 0.1f;

        public float Clarity { get; set; } = 1.0f;

        public List<string> Tags { get; set; } = new();

        public List<string> RelatedNpcs { get; set; } = new();

        public List<string> RelatedFactions { get; set; } = new();

        public List<string> RelatedLocations { get; set; } = new();

        public DateTime MemoryDate { get; set; } = DateTime.UtcNow;

        public int RecallCount { get; set; } = 0;

        public DateTime? LastRecalled { get; set; }

        public Dictionary<string, float> EmotionalImpact { get; set; } = new();

        // Computed Properties
        public bool IsFaded => Clarity < 0.3f;
        public bool IsImportant => Importance >= NPCMemoryImportance.Important;
        public bool IsRecent => MemoryDate > DateTime.UtcNow.AddDays(-7);
        public bool IsOftenRecalled => RecallCount > 10;
        public float EffectiveImportance => (int)Importance * Clarity * (1.0f - DecayRate);
    }

    public class NPCMemoryCreateRequestDTO
    {
        public string Content { get; set; } = string.Empty;

        public NPCMemoryImportance Importance { get; set; } = NPCMemoryImportance.Moderate;

        public List<string> Tags { get; set; } = new();

        public List<string> RelatedNpcs { get; set; } = new();

        public List<string> RelatedFactions { get; set; } = new();

        public List<string> RelatedLocations { get; set; } = new();

        public Dictionary<string, float> EmotionalImpact { get; set; } = new();
    }

    // ===========================================
    // NPC FACTION DTOs
    // ===========================================

    public class NPCFactionStatusDTO
    {
        public string NpcId { get; set; } = string.Empty;

        public string? PrimaryFaction { get; set; }

        public List<string> FactionAffiliations { get; set; } = new();

        public Dictionary<string, int> FactionScores { get; set; } = new();

        public Dictionary<string, string> FactionRoles { get; set; } = new();

        public List<NPCFactionHistoryDTO> FactionHistory { get; set; } = new();

        // Computed Properties
        public bool HasMultipleFactions => FactionAffiliations.Count > 1;
        public int HighestFactionScore => FactionScores.Values.DefaultIfEmpty(0).Max();
        public int LowestFactionScore => FactionScores.Values.DefaultIfEmpty(0).Min();
        public string? MostLoyalFaction => FactionScores.FirstOrDefault(kvp => kvp.Value == HighestFactionScore).Key;
        public string? LeastLoyalFaction => FactionScores.FirstOrDefault(kvp => kvp.Value == LowestFactionScore).Key;
    }

    public class NPCFactionHistoryDTO
    {
        public string FactionId { get; set; } = string.Empty;

        public int OldLoyalty { get; set; }

        public int NewLoyalty { get; set; }

        public DateTime Timestamp { get; set; } = DateTime.UtcNow;

        public string? Reason { get; set; }

        // Computed Properties
        public int LoyaltyChange => NewLoyalty - OldLoyalty;
        public bool IsImprovement => LoyaltyChange > 0;
        public bool IsDeterioration => LoyaltyChange < 0;
        public string ChangeDescription => LoyaltyChange switch
        {
            > 5 => "Major Improvement",
            > 2 => "Improvement",
            > 0 => "Slight Improvement",
            0 => "No Change",
            > -2 => "Slight Decline",
            > -5 => "Decline",
            _ => "Major Decline"
        };
    }

    public class NPCFactionAdjustmentRequestDTO
    {
        public string FactionId { get; set; } = string.Empty;

        public int Adjustment { get; set; }

        public string? Reason { get; set; }
    }

    // ===========================================
    // NPC RUMOR DTOs
    // ===========================================

    public class NPCRumorDTO : MetadataDTO
    {
        public string RumorId { get; set; } = string.Empty;

        public string NpcId { get; set; } = string.Empty;

        public string Content { get; set; } = string.Empty;

        public RumorCategory Category { get; set; } = RumorCategory.Gossip;

        public RumorVeracity Veracity { get; set; } = RumorVeracity.PartiallyTrue;

        public float BeliefStrength { get; set; } = 0.5f;

        public float Credibility { get; set; } = 0.5f;

        public string? SourceNpcId { get; set; }

        public DateTime LearnedDate { get; set; } = DateTime.UtcNow;

        public int SpreadCount { get; set; } = 0;

        public DateTime? LastSpread { get; set; }

        public List<string> Tags { get; set; } = new();

        public List<string> RelatedNpcs { get; set; } = new();

        public List<string> RelatedFactions { get; set; } = new();

        public List<string> RelatedLocations { get; set; } = new();

        // Computed Properties
        public bool IsRecentlyLearned => LearnedDate > DateTime.UtcNow.AddDays(-3);
        public bool IsWidelySpread => SpreadCount > 10;
        public bool IsHighlyBelieved => BeliefStrength > 0.8f;
        public bool IsHighlyCredible => Credibility > 0.8f;
        public bool IsRecentlySpread => LastSpread.HasValue && LastSpread > DateTime.UtcNow.AddDays(-1);
        public float OverallReliability => (BeliefStrength + Credibility + ((int)Veracity / 100.0f)) / 3.0f;
    }

    public class NPCRumorCreateRequestDTO
    {
        public string RumorId { get; set; } = string.Empty;

        public string Version { get; set; } = "1";

        public float BeliefStrength { get; set; } = 0.8f;
    }

    // ===========================================
    // NPC LOYALTY DTOs
    // ===========================================

    public class NPCLoyaltyDTO
    {
        public string NpcId { get; set; } = string.Empty;

        public string CharacterId { get; set; } = string.Empty;

        public NPCLoyaltyLevel LoyaltyScore { get; set; } = NPCLoyaltyLevel.Neutral;

        public List<NPCLoyaltyChangeDTO> LoyaltyHistory { get; set; } = new();

        public DateTime? LastInteraction { get; set; }

        public int InteractionCount { get; set; } = 0;

        public List<string> Reasons { get; set; } = new();

        // Computed Properties
        public bool IsLoyal => LoyaltyScore >= NPCLoyaltyLevel.Positive;
        public bool IsHostile => LoyaltyScore <= NPCLoyaltyLevel.Unfriendly;
        public bool IsNeutral => LoyaltyScore == NPCLoyaltyLevel.Neutral;
        public bool HasRecentInteraction => LastInteraction.HasValue && LastInteraction > DateTime.UtcNow.AddDays(-7);
        public bool IsFrequentlyInteracted => InteractionCount > 20;
        public string LoyaltyDescription => LoyaltyScore.ToString().Replace("Very", "Very ").Replace("Extremely", "Extremely ");
    }

    public class NPCLoyaltyChangeDTO
    {
        public NPCLoyaltyLevel OldLoyalty { get; set; }

        public NPCLoyaltyLevel NewLoyalty { get; set; }

        public int Change { get; set; }

        public string? Reason { get; set; }

        public DateTime Timestamp { get; set; } = DateTime.UtcNow;

        // Computed Properties
        public bool IsImprovement => Change > 0;
        public bool IsDeterioration => Change < 0;
        public string ChangeDescription => Change switch
        {
            > 3 => "Major Improvement",
            > 1 => "Improvement", 
            > 0 => "Slight Improvement",
            0 => "No Change",
            -1 => "Slight Decline",
            < -1 and >= -3 => "Decline",
            _ => "Major Decline"
        };
    }

    public class NPCLoyaltyUpdateRequestDTO
    {
        public string CharacterId { get; set; } = string.Empty;

        public int Change { get; set; }

        public string? Reason { get; set; }
    }

    // ===========================================
    // NPC GENERATION DTOs
    // ===========================================

    public class NPCGenerationRequestDTO
    {
        public string? PoiId { get; set; }

        public string? RegionId { get; set; }

        public int Count { get; set; } = 5;

        public string? FactionId { get; set; }

        public List<NPCProfessionType> Professions { get; set; } = new();

        public int? MinAge { get; set; }

        public int? MaxAge { get; set; }

        public List<NPCPersonalityTrait> RequiredTraits { get; set; } = new();

        public Dictionary<string, float> FactionDistribution { get; set; } = new();
    }

    public class NPCGenerationResponseDTO : SuccessResponseDTO
    {
        public List<NPCDT0> Npcs { get; set; } = new();

        public NPCGenerationStatsDTO GenerationStats { get; set; } = new();
    }

    public class NPCGenerationStatsDTO
    {
        public int RequestedCount { get; set; }

        public int GeneratedCount { get; set; }

        public Dictionary<NPCProfessionType, int> ProfessionDistribution { get; set; } = new();

        public Dictionary<string, int> FactionDistribution { get; set; } = new();

        public Dictionary<NPCGenderType, int> GenderDistribution { get; set; } = new();

        public Dictionary<string, int> AgeDistribution { get; set; } = new();

        public long GenerationTimeMs { get; set; }

        // Computed Properties
        public bool AllGeneratedSuccessfully => GeneratedCount == RequestedCount;
        public float SuccessRate => RequestedCount > 0 ? (float)GeneratedCount / RequestedCount : 0f;
        public string MostCommonProfession => ProfessionDistribution
            .OrderByDescending(kvp => kvp.Value)
            .FirstOrDefault().Key.ToString();
    }

    // ===========================================
    // NPC LOCATION DTOs
    // ===========================================

    public class NPCLocationDTO
    {
        public string NpcId { get; set; } = string.Empty;

        public string? PoiId { get; set; }

        public string? RegionId { get; set; }

        public CoordinateDTO? Coordinates { get; set; }

        public List<NPCTravelHistoryDTO> TravelHistory { get; set; } = new();

        public string? CurrentActivity { get; set; }

        public string TravelStatus { get; set; } = "stationary";

        public DateTime? LastMoved { get; set; }

        // Computed Properties
        public bool IsStationary => TravelStatus == "stationary";
        public bool IsTraveling => TravelStatus == "traveling";
        public bool HasTravelHistory => TravelHistory.Count > 0;
        public bool HasRecentMovement => LastMoved.HasValue && LastMoved > DateTime.UtcNow.AddDays(-1);
    }

    public class NPCTravelHistoryDTO
    {
        public string? FromPoiId { get; set; }

        public string? ToPoiId { get; set; }

        public string? FromRegionId { get; set; }

        public string? ToRegionId { get; set; }

        public DateTime TravelDate { get; set; } = DateTime.UtcNow;

        public string? TravelReason { get; set; }

        public int? DurationDays { get; set; }

        // Computed Properties
        public bool IsRegionChange => FromRegionId != ToRegionId;
        public bool IsRecentTravel => TravelDate > DateTime.UtcNow.AddDays(-7);
    }

    public class NPCLocationUpdateRequestDTO
    {
        public string? PoiId { get; set; }

        public string? RegionId { get; set; }

        public CoordinateDTO? Coordinates { get; set; }

        public string? TravelReason { get; set; }
    }

    // ===========================================
    // RESPONSE DTOs
    // ===========================================

    public class NPCListResponseDTO
    {
        public List<NPCDT0> NPCs { get; set; } = new List<NPCDT0>();
        public PaginationResponseDTO Pagination { get; set; } = new();
        public NPCListStatsDTO Stats { get; set; } = new NPCListStatsDTO();
        public List<string> Warnings { get; set; } = new List<string>();
        public DateTime GeneratedAt { get; set; } = DateTime.UtcNow;
    }

    public class NPCListStatsDTO
    {
        public int TotalNPCs { get; set; }
        public Dictionary<NPCProfessionType, int> ProfessionDistribution { get; set; } = new();
        public Dictionary<NPCGenderType, int> GenderDistribution { get; set; } = new();
        public Dictionary<string, int> FactionDistribution { get; set; } = new();
        public Dictionary<NPCStatusType, int> StatusDistribution { get; set; } = new();
        public float AverageAge { get; set; }
        public int ActiveNPCs { get; set; }
        public int InactiveNPCs { get; set; }
        
        // Computed Properties
        public string MostCommonProfession => ProfessionDistribution
            .OrderByDescending(kvp => kvp.Value)
            .FirstOrDefault().Key.ToString();
        public float ActivePercentage => TotalNPCs > 0 ? (float)ActiveNPCs / TotalNPCs * 100 : 0;
    }

    public class NPCFilterDTO
    {
        public string? PoiId { get; set; }

        public string? RegionId { get; set; }

        public string? FactionId { get; set; }

        public NPCProfessionType? Profession { get; set; }

        public NPCStatusType? Status { get; set; }

        public int? MinAge { get; set; }

        public int? MaxAge { get; set; }
    }

    public class NPCMemoryListResponseDTO : SuccessResponseDTO
    {
        public List<NPCMemoryDTO> Memories { get; set; } = new();

        public NPCMemoryStatsDTO MemoryStats { get; set; } = new();
    }

    public class NPCMemoryStatsDTO
    {
        public int TotalMemories { get; set; }

        public int ImportantMemories { get; set; }

        public int RecentMemories { get; set; }

        public int FadedMemories { get; set; }

        public float AverageImportance { get; set; }

        public float AverageClarity { get; set; }

        // Computed Properties
        public float ImportantMemoryPercentage => TotalMemories > 0 ? (float)ImportantMemories / TotalMemories * 100 : 0;
        public float FadedMemoryPercentage => TotalMemories > 0 ? (float)FadedMemories / TotalMemories * 100 : 0;
        public bool HasGoodMemoryRetention => FadedMemoryPercentage < 20;
    }

    public class NPCRumorListResponseDTO : SuccessResponseDTO
    {
        public List<NPCRumorDTO> Rumors { get; set; } = new();

        public NPCRumorStatsDTO RumorStats { get; set; } = new();
    }

    public class NPCRumorStatsDTO
    {
        public int TotalRumors { get; set; }

        public int HighlyBelievedRumors { get; set; }

        public int WidelySpreadRumors { get; set; }

        public int RecentRumors { get; set; }

        public Dictionary<RumorCategory, int> CategoryDistribution { get; set; } = new();

        public float AverageBeliefStrength { get; set; }

        public float AverageCredibility { get; set; }

        // Computed Properties
        public string MostCommonCategory => CategoryDistribution
            .OrderByDescending(kvp => kvp.Value)
            .FirstOrDefault().Key.ToString();
        public bool IsGullible => AverageBeliefStrength > 0.8f;
        public bool IsSkeptical => AverageBeliefStrength < 0.3f;
    }
} 