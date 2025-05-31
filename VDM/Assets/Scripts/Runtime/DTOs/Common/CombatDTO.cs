using System;
using System.Collections.Generic;
using VDM.DTOs.Core.Shared;

namespace VDM.DTOs.Game.Combat
{
    /// <summary>
    /// Types of damage that can be inflicted
    /// </summary>
    public enum DamageTypeDTO
    {
        Physical,
        Magical,
        Fire,
        Ice,
        Lightning,
        Poison,
        Psychic,
        Necrotic,
        Radiant,
        Force,
        Acid,
        Thunder,
        True // Bypasses resistances
    }

    /// <summary>
    /// Combat phases
    /// </summary>
    public enum CombatPhaseDTO
    {
        NotStarted,
        Initialization,
        Active,
        PostCombat,
        Ended
    }

    /// <summary>
    /// Types of combat encounters
    /// </summary>
    public enum CombatEncounterTypeDTO
    {
        Normal,
        Boss,
        Ambush,
        Quest,
        Arena,
        Tutorial
    }

    /// <summary>
    /// Types of combat actions
    /// </summary>
    public enum ActionTypeDTO
    {
        Standard,
        Bonus,
        Reaction,
        Movement,
        Free,
        Attack
    }

    /// <summary>
    /// Target types for actions
    /// </summary>
    public enum ActionTargetDTO
    {
        Self,
        Single,
        Multi,
        Area,
        Global
    }

    /// <summary>
    /// Types of combat effects
    /// </summary>
    public enum EffectTypeDTO
    {
        Buff,
        Debuff,
        Condition,
        DamageOverTime,
        HealOverTime,
        Resistance,
        Vulnerability,
        Immunity,
        Trigger,
        Passive,
        Shield,
        Aura,
        Stance,
        Counter
    }

    /// <summary>
    /// Effect stacking behavior
    /// </summary>
    public enum EffectStackingTypeDTO
    {
        Stack,
        Replace,
        Extend,
        Intensify,
        TakeHighest,
        TakeLowest
    }

    /// <summary>
    /// Effect application priority
    /// </summary>
    public enum EffectPriorityDTO
    {
        VeryLow = 0,
        Low = 25,
        Normal = 50,
        High = 75,
        VeryHigh = 100
    }

    /// <summary>
    /// Status effect types
    /// </summary>
    public enum StatusEffectTypeDTO
    {
        Buff,
        Debuff,
        Neutral
    }

    /// <summary>
    /// Status effect targets
    /// </summary>
    public enum StatusEffectTargetDTO
    {
        Self,
        Ally,
        Enemy,
        AllAllies,
        AllEnemies,
        All
    }

    /// <summary>
    /// Effect duration types
    /// </summary>
    public enum EffectDurationDTO
    {
        Instant,
        Temporary,
        Permanent
    }

    /// <summary>
    /// Combat statistics for a character
    /// </summary>
    [Serializable]
    public class CombatStatsDTO
    {
        public int Hp { get; set; } = 100;

        public int MaxHp { get; set; } = 100;

        public int Mp { get; set; } = 50;

        public int MaxMp { get; set; } = 50;

        public int Strength { get; set; } = 10;

        public int Dexterity { get; set; } = 10;

        public int Constitution { get; set; } = 10;

        public int Intelligence { get; set; } = 10;

        public int Wisdom { get; set; } = 10;

        public int Charisma { get; set; } = 10;

        public float Accuracy { get; set; } = 0.8f;

        public float Evasion { get; set; } = 0.1f;

        public int ArmorClass { get; set; } = 10;

        public int Armor { get; set; } = 5;

        public float MagicResistance { get; set; } = 0.0f;

        public float CriticalChance { get; set; } = 0.05f;

        public float CriticalMultiplier { get; set; } = 2.0f;

        public int Initiative { get; set; } = 10;

        public int Speed { get; set; } = 10;
    }

    /// <summary>
    /// State of a combatant in combat
    /// </summary>
    [Serializable]
    public class CombatantStateDTO
    {
        public string Id { get; set; } = string.Empty;

        public string Name { get; set; } = string.Empty;

        public string Team { get; set; } = string.Empty;

        public CoordinateDTO? Position { get; set; }

        public CombatStatsDTO Stats { get; set; } = new CombatStatsDTO();

        public List<StatusEffectDTO> StatusEffects { get; set; } = new List<StatusEffectDTO>();

        public List<string> ActiveAbilities { get; set; } = new List<string>();

        public Dictionary<string, int> TurnActionsUsed { get; set; } = new Dictionary<string, int>();

        public bool IsActive { get; set; } = true;

        public bool IsDefeated { get; set; } = false;
    }

    /// <summary>
    /// Current state of a combat encounter
    /// </summary>
    [Serializable]
    public class CombatStateDTO : MetadataDTO
    {
        public string Id { get; set; } = string.Empty;

        public CombatPhaseDTO Phase { get; set; } = CombatPhaseDTO.NotStarted;

        public CombatEncounterTypeDTO EncounterType { get; set; } = CombatEncounterTypeDTO.Normal;

        public int CurrentTurn { get; set; } = 0;

        public int CurrentRound { get; set; } = 1;

        public string? CurrentCombatantId { get; set; }

        public List<string> TurnOrder { get; set; } = new List<string>();

        public Dictionary<string, CombatantStateDTO> Combatants { get; set; } = new Dictionary<string, CombatantStateDTO>();

        public List<EnvironmentEffectDTO> EnvironmentEffects { get; set; } = new List<EnvironmentEffectDTO>();

        public List<CombatLogEntryDTO> CombatLog { get; set; } = new List<CombatLogEntryDTO>();

        public string? Victor { get; set; }

        public CoordinateDTO AreaSize { get; set; } = new CoordinateDTO { X = 20.0f, Y = 20.0f };

        public DateTime StartTime { get; set; } = DateTime.UtcNow;

        public DateTime? EndTime { get; set; }

        public Dictionary<string, object> CombatMetadata { get; set; } = new Dictionary<string, object>();
    }

    /// <summary>
    /// A combat effect applied to a character
    /// </summary>
    [Serializable]
    public class CombatEffectDTO
    {
        public string Id { get; set; } = Guid.NewGuid().ToString();

        public string Name { get; set; } = string.Empty;

        public string? Description { get; set; }

        public EffectTypeDTO EffectType { get; set; } = EffectTypeDTO.Buff;

        public EffectStackingTypeDTO StackingType { get; set; } = EffectStackingTypeDTO.Stack;

        public EffectPriorityDTO Priority { get; set; } = EffectPriorityDTO.Normal;

        public int Duration { get; set; } = 1; // Turns

        public EffectDurationDTO DurationType { get; set; } = EffectDurationDTO.Temporary;

        public int RemainingDuration { get; set; } = 1;

        public int Stacks { get; set; } = 1;

        public string? CasterId { get; set; }

        public string TargetId { get; set; } = string.Empty;

        public Dictionary<string, float> StatModifiers { get; set; } = new Dictionary<string, float>();

        public float? DamagePerTurn { get; set; }

        public float? HealPerTurn { get; set; }

        public DamageTypeDTO? DamageType { get; set; }

        public string? Condition { get; set; }

        public List<DamageTypeDTO> ResistanceTypes { get; set; } = new List<DamageTypeDTO>();

        public float? ResistanceMultiplier { get; set; }

        public List<DamageTypeDTO> VulnerabilityTypes { get; set; } = new List<DamageTypeDTO>();

        public float? VulnerabilityMultiplier { get; set; }

        public List<DamageTypeDTO> ImmunityTypes { get; set; } = new List<DamageTypeDTO>();

        public List<string> ImmuneEffects { get; set; } = new List<string>();

        public Dictionary<string, object>? TickEffect { get; set; }

        public List<string> TriggerConditions { get; set; } = new List<string>();

        public Dictionary<string, object> Metadata { get; set; } = new Dictionary<string, object>();
    }

    /// <summary>
    /// Status effect applied to a combatant
    /// </summary>
    [Serializable]
    public class StatusEffectDTO : CombatEffectDTO
    {
        public StatusEffectTypeDTO StatusType { get; set; } = StatusEffectTypeDTO.Neutral;

        public bool IsVisible { get; set; } = true;

        public bool IsDispellable { get; set; } = true;

        public string? SourceAbilityId { get; set; }
    }

    /// <summary>
    /// Environment effect in combat area
    /// </summary>
    [Serializable]
    public class EnvironmentEffectDTO : CombatEffectDTO
    {
        public CoordinateDTO? Area { get; set; }

        public float? Radius { get; set; }

        public List<string> AffectsTeams { get; set; } = new List<string>();
    }

    /// <summary>
    /// A combat action
    /// </summary>
    [Serializable]
    public class CombatActionDTO
    {
        public string Id { get; set; } = Guid.NewGuid().ToString();

        public ActionTypeDTO ActionType { get; set; } = ActionTypeDTO.Standard;

        public string Name { get; set; } = string.Empty;

        public string? Description { get; set; }

        public string SourceId { get; set; } = string.Empty;

        public ActionTargetDTO TargetType { get; set; } = ActionTargetDTO.Single;

        public List<string> TargetIds { get; set; } = new List<string>();

        public CoordinateDTO? TargetPosition { get; set; }

        public int Priority { get; set; } = 50;

        public DateTime Timestamp { get; set; } = DateTime.UtcNow;

        public bool IsExecuted { get; set; } = false;

        public DateTime? ExecutionTime { get; set; }

        public Dictionary<string, object> Payload { get; set; } = new Dictionary<string, object>();
    }

    /// <summary>
    /// Result of executing a combat action
    /// </summary>
    [Serializable]
    public class ActionResultDTO
    {
        public bool Success { get; set; } = true;

        public string Message { get; set; } = string.Empty;

        public float DamageDealt { get; set; } = 0.0f;

        public float HealingDone { get; set; } = 0.0f;

        public DamageTypeDTO? DamageType { get; set; }

        public bool IsCritical { get; set; } = false;

        public List<CombatEffectDTO> EffectsApplied { get; set; } = new List<CombatEffectDTO>();

        public List<string> EffectsRemoved { get; set; } = new List<string>();

        public List<string> TargetsAffected { get; set; } = new List<string>();

        public string? NarrativeText { get; set; }

        public Dictionary<string, object> Metadata { get; set; } = new Dictionary<string, object>();
    }

    /// <summary>
    /// Damage calculation details
    /// </summary>
    [Serializable]
    public class DamageCalculationDTO
    {
        public float BaseDamage { get; set; } = 0.0f;

        public DamageTypeDTO DamageType { get; set; } = DamageTypeDTO.Physical;

        public bool IsCritical { get; set; } = false;

        public float CriticalMultiplier { get; set; } = 2.0f;

        public float ArmorMitigation { get; set; } = 0.0f;

        public float ResistanceMitigation { get; set; } = 0.0f;

        public float VulnerabilityAmplification { get; set; } = 1.0f;

        public float FinalDamage { get; set; } = 0.0f;

        public bool WasBlocked { get; set; } = false;

        public bool WasDodged { get; set; } = false;

        public List<string> CalculationSteps { get; set; } = new List<string>();
    }

    /// <summary>
    /// Combat log entry
    /// </summary>
    [Serializable]
    public class CombatLogEntryDTO
    {
        public string Id { get; set; } = Guid.NewGuid().ToString();

        public DateTime Timestamp { get; set; } = DateTime.UtcNow;

        public int Turn { get; set; } = 0;

        public int Round { get; set; } = 1;

        public string? ActionId { get; set; }

        public string? SourceId { get; set; }

        public List<string> TargetIds { get; set; } = new List<string>();

        public string Message { get; set; } = string.Empty;

        public string EventType { get; set; } = string.Empty;

        public Dictionary<string, object> Data { get; set; } = new Dictionary<string, object>();
    }

    /// <summary>
    /// Request to start a combat encounter
    /// </summary>
    [Serializable]
    public class StartCombatRequestDTO
    {
        public CombatEncounterTypeDTO EncounterType { get; set; } = CombatEncounterTypeDTO.Normal;

        public List<CombatantStateDTO> PlayerCombatants { get; set; } = new List<CombatantStateDTO>();

        public List<CombatantStateDTO> EnemyCombatants { get; set; } = new List<CombatantStateDTO>();

        public List<EnvironmentEffectDTO> EnvironmentEffects { get; set; } = new List<EnvironmentEffectDTO>();

        public CoordinateDTO? AreaSize { get; set; }

        public Dictionary<string, object> Metadata { get; set; } = new Dictionary<string, object>();
    }

    /// <summary>
    /// Request to execute a combat action
    /// </summary>
    [Serializable]
    public class ExecuteActionRequestDTO
    {
        public string CombatId { get; set; } = string.Empty;

        public CombatActionDTO Action { get; set; } = new CombatActionDTO();

        public bool ValidateOnly { get; set; } = false;
    }

    /// <summary>
    /// Response for executing a combat action
    /// </summary>
    [Serializable]
    public class ExecuteActionResponseDTO : SuccessResponseDTO
    {
        public ActionResultDTO? ActionResult { get; set; }

        public CombatStateDTO? UpdatedCombatState { get; set; }

        public string? NextCombatantId { get; set; }

        public bool IsCombatOver { get; set; } = false;
    }

    /// <summary>
    /// Request to apply damage to a combatant
    /// </summary>
    [Serializable]
    public class ApplyDamageRequestDTO
    {
        public string CombatId { get; set; } = string.Empty;

        public string? SourceId { get; set; }

        public string TargetId { get; set; } = string.Empty;

        public float Damage { get; set; } = 0.0f;

        public DamageTypeDTO DamageType { get; set; } = DamageTypeDTO.Physical;

        public bool CanCritical { get; set; } = true;

        public bool IgnoreArmor { get; set; } = false;

        public bool IgnoreResistance { get; set; } = false;
    }

    /// <summary>
    /// Request to apply a status effect
    /// </summary>
    [Serializable]
    public class ApplyEffectRequestDTO
    {
        public string CombatId { get; set; } = string.Empty;

        public StatusEffectDTO Effect { get; set; } = new StatusEffectDTO();

        public bool ForceApplication { get; set; } = false;
    }

    /// <summary>
    /// Response for applying damage
    /// </summary>
    [Serializable]
    public class ApplyDamageResponseDTO : SuccessResponseDTO
    {
        public DamageCalculationDTO? DamageCalculation { get; set; }

        public bool TargetDefeated { get; set; } = false;

        public CombatantStateDTO? UpdatedTargetState { get; set; }
    }

    /// <summary>
    /// Combat encounter summary
    /// </summary>
    [Serializable]
    public class CombatSummaryDTO
    {
        public string CombatId { get; set; } = string.Empty;

        public CombatEncounterTypeDTO EncounterType { get; set; } = CombatEncounterTypeDTO.Normal;

        public string? Victor { get; set; }

        public TimeSpan Duration { get; set; } = TimeSpan.Zero;

        public int TotalTurns { get; set; } = 0;

        public int TotalRounds { get; set; } = 1;

        public float TotalDamageDealt { get; set; } = 0.0f;

        public float TotalHealingDone { get; set; } = 0.0f;

        public List<CombatantStateDTO> Participants { get; set; } = new List<CombatantStateDTO>();

        public List<string> DefeatedCombatants { get; set; } = new List<string>();

        public string? NarrativeSummary { get; set; }

        public Dictionary<string, object> Rewards { get; set; } = new Dictionary<string, object>();
    }
} 