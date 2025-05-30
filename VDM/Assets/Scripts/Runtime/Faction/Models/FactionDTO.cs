using System.Collections.Generic;
using Newtonsoft.Json;
using System;


namespace VDM.Runtime.Faction.Models
{
    /// <summary>
    /// Faction type enumeration
    /// Maps to backend FactionType enum
    /// </summary>
    public enum FactionType
    {
        Guild,
        Political,
        Religious,
        Mercenary,
        Criminal,
        Noble,
        Merchant,
        Military,
        Academic,
        Cult,
        Other
    }

    /// <summary>
    /// Faction alignment enumeration
    /// Maps to backend FactionAlignment enum
    /// </summary>
    public enum FactionAlignment
    {
        LawfulGood,
        LawfulNeutral,
        LawfulEvil,
        NeutralGood,
        TrueNeutral,
        NeutralEvil,
        ChaoticGood,
        ChaoticNeutral,
        ChaoticEvil
    }

    /// <summary>
    /// Diplomatic stance enumeration
    /// Maps to backend DiplomaticStance enum
    /// </summary>
    public enum DiplomaticStance
    {
        Allied,
        Friendly,
        Neutral,
        Unfriendly,
        Hostile,
        AtWar
    }

    /// <summary>
    /// Faction resources DTO
    /// Represents faction financial and material resources
    /// </summary>
    [Serializable]
    public class FactionResourcesDTO
    {
        [JsonProperty("gold")]
        public float Gold { get; set; } = 1000;

        [JsonProperty("materials")]
        public Dictionary<string, float> Materials { get; set; } = new Dictionary<string, float>();

        [JsonProperty("special_resources")]
        public Dictionary<string, float> SpecialResources { get; set; } = new Dictionary<string, float>();

        [JsonProperty("income_sources")]
        public List<string> IncomeSources { get; set; } = new List<string>();

        [JsonProperty("expenses")]
        public List<string> Expenses { get; set; } = new List<string>();
    }

    /// <summary>
    /// Faction relationships DTO
    /// Tracks relationships with other factions
    /// </summary>
    [Serializable]
    public class FactionRelationshipsDTO
    {
        [JsonProperty("allies")]
        public List<string> Allies { get; set; } = new List<string>();

        [JsonProperty("enemies")]
        public List<string> Enemies { get; set; } = new List<string>();

        [JsonProperty("neutral")]
        public List<string> Neutral { get; set; } = new List<string>();

        [JsonProperty("trade_partners")]
        public List<string> TradePartners { get; set; } = new List<string>();
    }

    /// <summary>
    /// Faction goals DTO
    /// Tracks current, completed, and failed goals
    /// </summary>
    [Serializable]
    public class FactionGoalsDTO
    {
        [JsonProperty("current")]
        public List<string> Current { get; set; } = new List<string>();

        [JsonProperty("completed")]
        public List<string> Completed { get; set; } = new List<string>();

        [JsonProperty("failed")]
        public List<string> Failed { get; set; } = new List<string>();
    }

    /// <summary>
    /// Faction diplomatic policies DTO
    /// </summary>
    [Serializable]
    public class FactionDiplomaticPoliciesDTO
    {
        [JsonProperty("aggression")]
        public int Aggression { get; set; } = 0;

        [JsonProperty("trade_focus")]
        public int TradeFocus { get; set; } = 0;

        [JsonProperty("expansion")]
        public int Expansion { get; set; } = 0;
    }

    /// <summary>
    /// Faction economic policies DTO
    /// </summary>
    [Serializable]
    public class FactionEconomicPoliciesDTO
    {
        [JsonProperty("tax_rate")]
        public int TaxRate { get; set; } = 10;

        [JsonProperty("trade_tariffs")]
        public int TradeTariffs { get; set; } = 5;

        [JsonProperty("investment_focus")]
        public List<string> InvestmentFocus { get; set; } = new List<string>();
    }

    /// <summary>
    /// Faction military policies DTO
    /// </summary>
    [Serializable]
    public class FactionMilitaryPoliciesDTO
    {
        [JsonProperty("stance")]
        public string Stance { get; set; } = "defensive";

        [JsonProperty("recruitment_rate")]
        public string RecruitmentRate { get; set; } = "normal";

        [JsonProperty("training_focus")]
        public List<string> TrainingFocus { get; set; } = new List<string>();
    }

    /// <summary>
    /// Faction policies DTO
    /// Comprehensive faction policy configuration
    /// </summary>
    [Serializable]
    public class FactionPoliciesDTO
    {
        [JsonProperty("diplomatic")]
        public FactionDiplomaticPoliciesDTO Diplomatic { get; set; } = new FactionDiplomaticPoliciesDTO();

        [JsonProperty("economic")]
        public FactionEconomicPoliciesDTO Economic { get; set; } = new FactionEconomicPoliciesDTO();

        [JsonProperty("military")]
        public FactionMilitaryPoliciesDTO Military { get; set; } = new FactionMilitaryPoliciesDTO();
    }

    /// <summary>
    /// Faction statistics DTO
    /// </summary>
    [Serializable]
    public class FactionStatisticsDTO
    {
        [JsonProperty("members_count")]
        public int MembersCount { get; set; } = 0;

        [JsonProperty("territory_count")]
        public int TerritoryCount { get; set; } = 0;

        [JsonProperty("quest_success_rate")]
        public float QuestSuccessRate { get; set; } = 0;
    }

    /// <summary>
    /// Faction state DTO
    /// Current state and activities of the faction
    /// </summary>
    [Serializable]
    public class FactionStateDTO
    {
        [JsonProperty("active_wars")]
        public List<string> ActiveWars { get; set; } = new List<string>();

        [JsonProperty("current_projects")]
        public List<string> CurrentProjects { get; set; } = new List<string>();

        [JsonProperty("recent_events")]
        public List<string> RecentEvents { get; set; } = new List<string>();

        [JsonProperty("statistics")]
        public FactionStatisticsDTO Statistics { get; set; } = new FactionStatisticsDTO();
    }

    /// <summary>
    /// Main faction response DTO from backend
    /// Comprehensive faction data matching backend faction model
    /// </summary>
    [Serializable]
    public class FactionResponseDTO
    {
        [JsonProperty("id")]
        public int Id { get; set; }

        [JsonProperty("name")]
        public string Name { get; set; } = "";

        [JsonProperty("description")]
        public string Description { get; set; } = "";

        [JsonProperty("type")]
        public string Type { get; set; } = "other";

        [JsonProperty("alignment")]
        public string Alignment { get; set; } = "";

        [JsonProperty("influence")]
        public float Influence { get; set; } = 50.0f;

        [JsonProperty("reputation")]
        public float Reputation { get; set; } = 0.0f;

        [JsonProperty("resources")]
        public FactionResourcesDTO Resources { get; set; } = new FactionResourcesDTO();

        [JsonProperty("territory")]
        public Dictionary<string, object> Territory { get; set; } = new Dictionary<string, object>();

        [JsonProperty("relationships")]
        public FactionRelationshipsDTO Relationships { get; set; } = new FactionRelationshipsDTO();

        [JsonProperty("history")]
        public string History { get; set; } = "";

        [JsonProperty("is_active")]
        public bool IsActive { get; set; } = true;

        [JsonProperty("leader_id")]
        public int? LeaderId { get; set; }

        [JsonProperty("headquarters_id")]
        public int? HeadquartersId { get; set; }

        [JsonProperty("parent_faction_id")]
        public int? ParentFactionId { get; set; }

        [JsonProperty("power")]
        public float Power { get; set; } = 1.0f;

        [JsonProperty("wealth")]
        public float Wealth { get; set; } = 1000.0f;

        [JsonProperty("goals")]
        public FactionGoalsDTO Goals { get; set; } = new FactionGoalsDTO();

        [JsonProperty("policies")]
        public FactionPoliciesDTO Policies { get; set; } = new FactionPoliciesDTO();

        [JsonProperty("state")]
        public FactionStateDTO State { get; set; } = new FactionStateDTO();

        [JsonProperty("world_id")]
        public int? WorldId { get; set; }

        [JsonProperty("created_at")]
        public string CreatedAt { get; set; } = DateTime.UtcNow.ToString("O");

        [JsonProperty("updated_at")]
        public string UpdatedAt { get; set; } = DateTime.UtcNow.ToString("O");

        // Computed properties for Unity compatibility
        public FactionType FactionType => Enum.TryParse<FactionType>(Type, true, out var result) ? result : FactionType.Other;
        public FactionAlignment? FactionAlignment => !string.IsNullOrEmpty(Alignment) && Enum.TryParse<FactionAlignment>(Alignment, true, out var result) ? result : null;
        public DateTime? CreatedAtDateTime => DateTime.TryParse(CreatedAt, out var result) ? result : null;
        public DateTime? UpdatedAtDateTime => DateTime.TryParse(UpdatedAt, out var result) ? result : null;
    }

    /// <summary>
    /// Faction creation request DTO
    /// Used when creating new factions
    /// </summary>
    [Serializable]
    public class FactionCreateDTO
    {
        [JsonProperty("name")]
        public string Name { get; set; } = "";

        [JsonProperty("description")]
        public string Description { get; set; } = "";

        [JsonProperty("type")]
        public string Type { get; set; } = "other";

        [JsonProperty("alignment")]
        public string Alignment { get; set; } = "";

        [JsonProperty("influence")]
        public float Influence { get; set; } = 50.0f;

        [JsonProperty("leader_id")]
        public int? LeaderId { get; set; }

        [JsonProperty("headquarters_id")]
        public int? HeadquartersId { get; set; }

        [JsonProperty("parent_faction_id")]
        public int? ParentFactionId { get; set; }

        [JsonProperty("resources")]
        public FactionResourcesDTO Resources { get; set; } = new FactionResourcesDTO();

        [JsonProperty("goals")]
        public FactionGoalsDTO Goals { get; set; } = new FactionGoalsDTO();

        [JsonProperty("policies")]
        public FactionPoliciesDTO Policies { get; set; } = new FactionPoliciesDTO();

        [JsonProperty("world_id")]
        public int? WorldId { get; set; }
    }

    /// <summary>
    /// Faction update request DTO
    /// Used for partial faction updates
    /// </summary>
    [Serializable]
    public class FactionUpdateDTO
    {
        [JsonProperty("name")]
        public string Name { get; set; }

        [JsonProperty("description")]
        public string Description { get; set; }

        [JsonProperty("type")]
        public string Type { get; set; }

        [JsonProperty("alignment")]
        public string Alignment { get; set; }

        [JsonProperty("influence")]
        public float? Influence { get; set; }

        [JsonProperty("reputation")]
        public float? Reputation { get; set; }

        [JsonProperty("resources")]
        public FactionResourcesDTO Resources { get; set; }

        [JsonProperty("relationships")]
        public FactionRelationshipsDTO Relationships { get; set; }

        [JsonProperty("history")]
        public string History { get; set; }

        [JsonProperty("is_active")]
        public bool? IsActive { get; set; }

        [JsonProperty("leader_id")]
        public int? LeaderId { get; set; }

        [JsonProperty("headquarters_id")]
        public int? HeadquartersId { get; set; }

        [JsonProperty("power")]
        public float? Power { get; set; }

        [JsonProperty("wealth")]
        public float? Wealth { get; set; }

        [JsonProperty("goals")]
        public FactionGoalsDTO Goals { get; set; }

        [JsonProperty("policies")]
        public FactionPoliciesDTO Policies { get; set; }

        [JsonProperty("state")]
        public FactionStateDTO State { get; set; }
    }

    /// <summary>
    /// Faction list response DTO
    /// Used for paginated faction lists
    /// </summary>
    [Serializable]
    public class FactionListResponseDTO
    {
        [JsonProperty("factions")]
        public List<FactionResponseDTO> Factions { get; set; } = new List<FactionResponseDTO>();

        [JsonProperty("total_count")]
        public int TotalCount { get; set; } = 0;

        [JsonProperty("page")]
        public int Page { get; set; } = 1;

        [JsonProperty("page_size")]
        public int PageSize { get; set; } = 10;
    }

    /// <summary>
    /// Faction relationship response DTO
    /// Represents diplomatic relationships between factions
    /// </summary>
    [Serializable]
    public class FactionRelationshipResponseDTO
    {
        [JsonProperty("id")]
        public int Id { get; set; }

        [JsonProperty("faction_id")]
        public int FactionId { get; set; }

        [JsonProperty("other_faction_id")]
        public int OtherFactionId { get; set; }

        [JsonProperty("diplomatic_stance")]
        public string DiplomaticStance { get; set; } = "neutral";

        [JsonProperty("tension")]
        public float Tension { get; set; } = 0.0f;

        [JsonProperty("treaties")]
        public List<Dictionary<string, object>> Treaties { get; set; } = new List<Dictionary<string, object>>();

        [JsonProperty("war_state")]
        public Dictionary<string, object> WarState { get; set; } = new Dictionary<string, object>();

        [JsonProperty("history")]
        public List<Dictionary<string, object>> History { get; set; } = new List<Dictionary<string, object>>();

        [JsonProperty("metadata")]
        public Dictionary<string, object> Metadata { get; set; } = new Dictionary<string, object>();

        [JsonProperty("created_at")]
        public string CreatedAt { get; set; } = DateTime.UtcNow.ToString("O");

        [JsonProperty("updated_at")]
        public string UpdatedAt { get; set; } = DateTime.UtcNow.ToString("O");

        // Computed properties
        public DiplomaticStance Stance => Enum.TryParse<DiplomaticStance>(DiplomaticStance, true, out var result) ? result : Models.DiplomaticStance.Neutral;
        public bool IsAtWar => WarState.ContainsKey("at_war") && WarState["at_war"] is bool atWar && atWar;
        public DateTime? CreatedAtDateTime => DateTime.TryParse(CreatedAt, out var result) ? result : null;
        public DateTime? UpdatedAtDateTime => DateTime.TryParse(UpdatedAt, out var result) ? result : null;
    }

    /// <summary>
    /// Faction membership response DTO
    /// Represents character membership in factions
    /// </summary>
    [Serializable]
    public class FactionMembershipResponseDTO
    {
        [JsonProperty("id")]
        public int Id { get; set; }

        [JsonProperty("faction_id")]
        public int FactionId { get; set; }

        [JsonProperty("character_id")]
        public int CharacterId { get; set; }

        [JsonProperty("role")]
        public string Role { get; set; } = "";

        [JsonProperty("rank")]
        public int Rank { get; set; } = 0;

        [JsonProperty("reputation")]
        public float Reputation { get; set; } = 0.0f;

        [JsonProperty("joined_at")]
        public string JoinedAt { get; set; } = DateTime.UtcNow.ToString("O");

        [JsonProperty("is_active")]
        public bool IsActive { get; set; } = true;

        [JsonProperty("status")]
        public string Status { get; set; } = "active";

        [JsonProperty("achievements")]
        public List<Dictionary<string, object>> Achievements { get; set; } = new List<Dictionary<string, object>>();

        [JsonProperty("history")]
        public List<Dictionary<string, object>> History { get; set; } = new List<Dictionary<string, object>>();

        [JsonProperty("metadata")]
        public Dictionary<string, object> Metadata { get; set; } = new Dictionary<string, object>();

        [JsonProperty("created_at")]
        public string CreatedAt { get; set; } = DateTime.UtcNow.ToString("O");

        [JsonProperty("updated_at")]
        public string UpdatedAt { get; set; } = DateTime.UtcNow.ToString("O");

        // Computed properties
        public DateTime? JoinedAtDateTime => DateTime.TryParse(JoinedAt, out var result) ? result : null;
        public DateTime? CreatedAtDateTime => DateTime.TryParse(CreatedAt, out var result) ? result : null;
        public DateTime? UpdatedAtDateTime => DateTime.TryParse(UpdatedAt, out var result) ? result : null;
    }

    /// <summary>
    /// Diplomatic stance change request DTO
    /// Used for updating diplomatic relationships
    /// </summary>
    [Serializable]
    public class DiplomaticStanceChangeDTO
    {
        [JsonProperty("stance")]
        public string Stance { get; set; } = "neutral";

        [JsonProperty("tension")]
        public float? Tension { get; set; }

        [JsonProperty("reason")]
        public string Reason { get; set; } = "";

        [JsonProperty("treaties")]
        public List<Dictionary<string, object>> Treaties { get; set; } = new List<Dictionary<string, object>>();

        [JsonProperty("metadata")]
        public Dictionary<string, object> Metadata { get; set; } = new Dictionary<string, object>();
    }

    /// <summary>
    /// Faction membership change request DTO
    /// Used for updating character faction memberships
    /// </summary>
    [Serializable]
    public class FactionMembershipChangeDTO
    {
        [JsonProperty("character_id")]
        public int CharacterId { get; set; }

        [JsonProperty("role")]
        public string Role { get; set; } = "";

        [JsonProperty("rank")]
        public int? Rank { get; set; }

        [JsonProperty("reputation")]
        public float? Reputation { get; set; }

        [JsonProperty("status")]
        public string Status { get; set; } = "active";

        [JsonProperty("is_active")]
        public bool? IsActive { get; set; }
    }
} 