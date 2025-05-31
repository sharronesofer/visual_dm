using System.Collections.Generic;
using Newtonsoft.Json;
using System;


namespace VDM.Systems.Character.Models
{
    /// <summary>
    /// Character attributes (STR, DEX, CON, etc.) DTO
    /// Maps to backend character attributes structure
    /// </summary>
    [Serializable]
    public class CharacterAttributesDTO
    {
        [JsonProperty("strength")]
        public int Strength { get; set; } = 10;

        [JsonProperty("dexterity")]
        public int Dexterity { get; set; } = 10;

        [JsonProperty("constitution")]
        public int Constitution { get; set; } = 10;

        [JsonProperty("intelligence")]
        public int Intelligence { get; set; } = 10;

        [JsonProperty("wisdom")]
        public int Wisdom { get; set; } = 10;

        [JsonProperty("charisma")]
        public int Charisma { get; set; } = 10;
    }

    /// <summary>
    /// Character derived stats DTO
    /// Computed stats based on attributes and level
    /// </summary>
    [Serializable]
    public class CharacterDerivedStatsDTO
    {
        [JsonProperty("hit_points")]
        public int HitPoints { get; set; } = 100;

        [JsonProperty("max_hit_points")]
        public int MaxHitPoints { get; set; } = 100;

        [JsonProperty("armor_class")]
        public int ArmorClass { get; set; } = 10;

        [JsonProperty("initiative")]
        public int Initiative { get; set; } = 0;

        [JsonProperty("speed")]
        public int Speed { get; set; } = 30;

        [JsonProperty("proficiency_bonus")]
        public int ProficiencyBonus { get; set; } = 2;
    }

    /// <summary>
    /// Character personality traits DTO
    /// </summary>
    [Serializable]
    public class CharacterPersonalityDTO
    {
        [JsonProperty("traits")]
        public List<string> Traits { get; set; } = new List<string>();

        [JsonProperty("ideals")]
        public List<string> Ideals { get; set; } = new List<string>();

        [JsonProperty("bonds")]
        public List<string> Bonds { get; set; } = new List<string>();

        [JsonProperty("flaws")]
        public List<string> Flaws { get; set; } = new List<string>();
    }

    /// <summary>
    /// Character game state DTO
    /// Includes current game-related state like gold, reputation, etc.
    /// </summary>
    [Serializable]
    public class CharacterGameStateDTO
    {
        [JsonProperty("gold")]
        public int Gold { get; set; } = 0;

        [JsonProperty("reputation")]
        public Dictionary<string, int> Reputation { get; set; } = new Dictionary<string, int>();

        [JsonProperty("faction_affiliations")]
        public List<string> FactionAffiliations { get; set; } = new List<string>();

        [JsonProperty("status_effects")]
        public List<string> StatusEffects { get; set; } = new List<string>();

        [JsonProperty("conditions")]
        public List<string> Conditions { get; set; } = new List<string>();
    }

    /// <summary>
    /// Character narrative data DTO
    /// Story-related information
    /// </summary>
    [Serializable]
    public class CharacterNarrativeDTO
    {
        [JsonProperty("backstory")]
        public string Backstory { get; set; } = "";

        [JsonProperty("current_goal")]
        public string CurrentGoal { get; set; } = "";

        [JsonProperty("motivations")]
        public List<string> Motivations { get; set; } = new List<string>();

        [JsonProperty("fears")]
        public List<string> Fears { get; set; } = new List<string>();

        [JsonProperty("secrets")]
        public List<string> Secrets { get; set; } = new List<string>();
    }

    /// <summary>
    /// Character metadata DTO
    /// System-level metadata
    /// </summary>
    [Serializable]
    public class CharacterMetadataDTO
    {
        [JsonProperty("created_at")]
        public string CreatedAt { get; set; } = DateTime.UtcNow.ToString("O");

        [JsonProperty("updated_at")]
        public string UpdatedAt { get; set; } = DateTime.UtcNow.ToString("O");

        [JsonProperty("version")]
        public int Version { get; set; } = 1;

        [JsonProperty("owner_id")]
        public string OwnerId { get; set; } = "";
    }

    /// <summary>
    /// Main character response DTO from backend
    /// Comprehensive character data matching backend character model
    /// </summary>
    [Serializable]
    public class CharacterResponseDTO
    {
        [JsonProperty("id")]
        public string Id { get; set; } = "";

        [JsonProperty("character_id")]
        public string CharacterId { get; set; } = "";

        [JsonProperty("character_name")]
        public string CharacterName { get; set; } = "";

        [JsonProperty("race")]
        public string Race { get; set; } = "human";

        [JsonProperty("character_class")]
        public string CharacterClass { get; set; } = "";

        [JsonProperty("level")]
        public int Level { get; set; } = 1;

        [JsonProperty("experience")]
        public int Experience { get; set; } = 0;

        [JsonProperty("background")]
        public string Background { get; set; } = "";

        [JsonProperty("alignment")]
        public string Alignment { get; set; } = "";

        [JsonProperty("attributes")]
        public CharacterAttributesDTO Attributes { get; set; } = new CharacterAttributesDTO();

        [JsonProperty("derived_stats")]
        public CharacterDerivedStatsDTO DerivedStats { get; set; } = new CharacterDerivedStatsDTO();

        [JsonProperty("skills")]
        public Dictionary<string, int> Skills { get; set; } = new Dictionary<string, int>();

        [JsonProperty("abilities")]
        public List<string> Abilities { get; set; } = new List<string>();

        [JsonProperty("languages")]
        public List<string> Languages { get; set; } = new List<string>();

        [JsonProperty("personality")]
        public CharacterPersonalityDTO Personality { get; set; } = new CharacterPersonalityDTO();

        [JsonProperty("game_state")]
        public CharacterGameStateDTO GameState { get; set; } = new CharacterGameStateDTO();

        [JsonProperty("narrative")]
        public CharacterNarrativeDTO Narrative { get; set; } = new CharacterNarrativeDTO();

        [JsonProperty("metadata")]
        public CharacterMetadataDTO Metadata { get; set; } = new CharacterMetadataDTO();

        [JsonProperty("is_active")]
        public bool IsActive { get; set; } = true;

        [JsonProperty("is_npc")]
        public bool IsNpc { get; set; } = false;

        // Computed properties for Unity compatibility
        public int HitPoints => DerivedStats?.HitPoints ?? 100;
        public int MaxHitPoints => DerivedStats?.MaxHitPoints ?? 100;
        public int ArmorClass => DerivedStats?.ArmorClass ?? 10;
        public DateTime? CreatedAt => DateTime.TryParse(Metadata?.CreatedAt, out var result) ? result : null;
        public DateTime? UpdatedAt => DateTime.TryParse(Metadata?.UpdatedAt, out var result) ? result : null;
    }

    /// <summary>
    /// Character creation request DTO
    /// Used when creating new characters
    /// </summary>
    [Serializable]
    public class CharacterCreateDTO
    {
        [JsonProperty("character_name")]
        public string CharacterName { get; set; } = "";

        [JsonProperty("race")]
        public string Race { get; set; } = "human";

        [JsonProperty("character_class")]
        public string CharacterClass { get; set; } = "";

        [JsonProperty("background")]
        public string Background { get; set; } = "";

        [JsonProperty("alignment")]
        public string Alignment { get; set; } = "";

        [JsonProperty("attributes")]
        public CharacterAttributesDTO Attributes { get; set; } = new CharacterAttributesDTO();

        [JsonProperty("personality")]
        public CharacterPersonalityDTO Personality { get; set; } = new CharacterPersonalityDTO();

        [JsonProperty("narrative")]
        public CharacterNarrativeDTO Narrative { get; set; } = new CharacterNarrativeDTO();

        [JsonProperty("is_npc")]
        public bool IsNpc { get; set; } = false;
    }

    /// <summary>
    /// Character update request DTO
    /// Used for partial character updates
    /// </summary>
    [Serializable]
    public class CharacterUpdateDTO
    {
        [JsonProperty("character_name")]
        public string CharacterName { get; set; }

        [JsonProperty("background")]
        public string Background { get; set; }

        [JsonProperty("alignment")]
        public string Alignment { get; set; }

        [JsonProperty("attributes")]
        public CharacterAttributesDTO Attributes { get; set; }

        [JsonProperty("personality")]
        public CharacterPersonalityDTO Personality { get; set; }

        [JsonProperty("narrative")]
        public CharacterNarrativeDTO Narrative { get; set; }

        [JsonProperty("game_state")]
        public CharacterGameStateDTO GameState { get; set; }

        [JsonProperty("is_active")]
        public bool? IsActive { get; set; }
    }

    /// <summary>
    /// Character list response DTO
    /// Used for paginated character lists
    /// </summary>
    [Serializable]
    public class CharacterListResponseDTO
    {
        [JsonProperty("characters")]
        public List<CharacterResponseDTO> Characters { get; set; } = new List<CharacterResponseDTO>();

        [JsonProperty("total_count")]
        public int TotalCount { get; set; } = 0;

        [JsonProperty("page")]
        public int Page { get; set; } = 1;

        [JsonProperty("page_size")]
        public int PageSize { get; set; } = 10;
    }

    /// <summary>
    /// Experience grant DTO
    /// Used for granting experience to characters
    /// </summary>
    [Serializable]
    public class ExperienceGrantDTO
    {
        [JsonProperty("amount")]
        public int Amount { get; set; }

        [JsonProperty("source")]
        public string Source { get; set; } = "Unknown";

        [JsonProperty("notes")]
        public string Notes { get; set; } = "";
    }

    /// <summary>
    /// Skill increase DTO
    /// Used for increasing character skills
    /// </summary>
    [Serializable]
    public class SkillIncreaseDTO
    {
        [JsonProperty("skill_name")]
        public string SkillName { get; set; } = "";

        [JsonProperty("increase_amount")]
        public int IncreaseAmount { get; set; } = 1;
    }

    /// <summary>
    /// Ability selection DTO
    /// Used for adding abilities to characters
    /// </summary>
    [Serializable]
    public class AbilitySelectionDTO
    {
        [JsonProperty("ability_name")]
        public string AbilityName { get; set; } = "";

        [JsonProperty("prerequisites_met")]
        public bool PrerequisitesMet { get; set; } = true;
    }

    /// <summary>
    /// Character progression response DTO
    /// Used for tracking character progression history
    /// </summary>
    [Serializable]
    public class CharacterProgressionResponseDTO
    {
        [JsonProperty("id")]
        public string Id { get; set; } = "";

        [JsonProperty("character_id")]
        public string CharacterId { get; set; } = "";

        [JsonProperty("progression_type")]
        public string ProgressionType { get; set; } = "";

        [JsonProperty("details")]
        public Dictionary<string, object> Details { get; set; } = new Dictionary<string, object>();

        [JsonProperty("timestamp")]
        public string Timestamp { get; set; } = DateTime.UtcNow.ToString("O");
    }
} 