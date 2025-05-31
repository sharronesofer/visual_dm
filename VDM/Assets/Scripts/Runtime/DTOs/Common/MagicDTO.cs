using System;
using System.Collections.Generic;
using VDM.DTOs.Core.Shared;

namespace VDM.DTOs.Game.Magic
{
    /// <summary>
    /// Magic school enumeration for spell classification
    /// </summary>
    public enum MagicSchoolDTO
    {
        Abjuration,
        Conjuration,
        Divination,
        Enchantment,
        Evocation,
        Illusion,
        Necromancy,
        Transmutation
    }

    /// <summary>
    /// Magic domain enumeration representing the source or tradition of magic
    /// </summary>
    public enum MagicDomainDTO
    {
        Arcane,     // Traditional wizardry and academic magic study
        Divine,     // Magic granted by deities and higher powers
        Nature,     // Magic drawn from natural forces and elements
        Occult      // Forbidden knowledge and pacts with otherworldly entities
    }

    /// <summary>
    /// Types of magical effects for narrative context
    /// </summary>
    public enum EffectTypeDTO
    {
        Influence,      // Subtle influence on environment/people
        Manifestation,  // Visible magical presence
        Alteration,     // Changes to physical properties
        Enhancement,    // Enhances existing properties
        Diminishment    // Reduces existing properties
    }

    /// <summary>
    /// Spell model for magical knowledge in the world
    /// </summary>
    [Serializable]
    public class SpellDTO : MetadataDTO
    {
        public string Id { get; set; } = string.Empty;

        public string Name { get; set; } = string.Empty;

        public string? Description { get; set; }

        public MagicSchoolDTO School { get; set; } = MagicSchoolDTO.Evocation;

        public MagicDomainDTO Domain { get; set; } = MagicDomainDTO.Arcane;

        public float NarrativePower { get; set; } = 5.0f;

        public Dictionary<string, object> NarrativeEffects { get; set; } = new Dictionary<string, object>();
    }

    /// <summary>
    /// Spellbook model for tracking magical knowledge
    /// </summary>
    [Serializable]
    public class SpellbookDTO : MetadataDTO
    {
        public string Id { get; set; } = string.Empty;

        public string OwnerId { get; set; } = string.Empty;

        public string OwnerType { get; set; } = "character"; // 'character', 'npc'

        public Dictionary<string, object> Spells { get; set; } = new Dictionary<string, object>();
    }

    /// <summary>
    /// Spell effect model for tracking magical influences
    /// </summary>
    [Serializable]
    public class SpellEffectDTO : MetadataDTO
    {
        public string Id { get; set; } = string.Empty;

        public string SpellId { get; set; } = string.Empty;

        public string TargetId { get; set; } = string.Empty;

        public string TargetType { get; set; } = string.Empty; // character, location, etc.

        public int Duration { get; set; } = 0; // in narrative time units

        public int RemainingDuration { get; set; } = 0;

        public Dictionary<string, object> Effects { get; set; } = new Dictionary<string, object>();

        public bool IsExpired { get; set; } = false;
    }

    /// <summary>
    /// Magical influence model for tracking background magic in locations
    /// </summary>
    [Serializable]
    public class MagicalInfluenceDTO : MetadataDTO
    {
        public string Id { get; set; } = string.Empty;

        public string LocationId { get; set; } = string.Empty;

        public MagicSchoolDTO School { get; set; } = MagicSchoolDTO.Evocation;

        public float Strength { get; set; } = 1.0f;

        public string? Description { get; set; }

        public Dictionary<string, object> Effects { get; set; } = new Dictionary<string, object>();
    }

    /// <summary>
    /// Magic ability for characters
    /// </summary>
    [Serializable]
    public class MagicAbilityDTO
    {
        public string Name { get; set; } = string.Empty;

        public MagicSchoolDTO School { get; set; } = MagicSchoolDTO.Evocation;

        public MagicDomainDTO Domain { get; set; } = MagicDomainDTO.Arcane;

        public int Level { get; set; } = 0;

        public bool Known { get; set; } = false;

        public bool Prepared { get; set; } = false;

        public int UsesRemaining { get; set; } = 0;

        public int MaxUses { get; set; } = 0;
    }

    // ================ Request/Response DTOs ================

    /// <summary>
    /// Request to create a new spell
    /// </summary>
    [Serializable]
    public class CreateSpellRequestDTO
    {
        public string Name { get; set; } = string.Empty;

        public string? Description { get; set; }

        public MagicSchoolDTO School { get; set; } = MagicSchoolDTO.Evocation;

        public MagicDomainDTO Domain { get; set; } = MagicDomainDTO.Arcane;

        public float NarrativePower { get; set; } = 5.0f;

        public Dictionary<string, object>? NarrativeEffects { get; set; }
    }

    /// <summary>
    /// Request to update a spell
    /// </summary>
    [Serializable]
    public class UpdateSpellRequestDTO
    {
        public string? Name { get; set; }

        public string? Description { get; set; }

        public MagicSchoolDTO? School { get; set; }

        public MagicDomainDTO? Domain { get; set; }

        public float? NarrativePower { get; set; }

        public Dictionary<string, object>? NarrativeEffects { get; set; }
    }

    /// <summary>
    /// Request to create a spellbook
    /// </summary>
    [Serializable]
    public class CreateSpellbookRequestDTO
    {
        public string OwnerId { get; set; } = string.Empty;

        public string OwnerType { get; set; } = "character";

        public Dictionary<string, object>? Spells { get; set; }
    }

    /// <summary>
    /// Request to cast a spell
    /// </summary>
    [Serializable]
    public class CastSpellRequestDTO
    {
        public string SpellId { get; set; } = string.Empty;

        public string CasterId { get; set; } = string.Empty;

        public string? TargetId { get; set; }

        public string? TargetType { get; set; }

        public int? Duration { get; set; }

        public Dictionary<string, object>? Effects { get; set; }
    }

    /// <summary>
    /// Request to create a magic ability
    /// </summary>
    [Serializable]
    public class CreateMagicAbilityRequestDTO
    {
        public string Name { get; set; } = string.Empty;

        public MagicSchoolDTO School { get; set; } = MagicSchoolDTO.Evocation;

        public MagicDomainDTO Domain { get; set; } = MagicDomainDTO.Arcane;

        public int Level { get; set; } = 0;

        public int MaxUses { get; set; } = 0;
    }

    /// <summary>
    /// Request to update a magic ability
    /// </summary>
    [Serializable]
    public class UpdateMagicAbilityRequestDTO
    {
        public bool? Known { get; set; }

        public bool? Prepared { get; set; }

        public int? UsesRemaining { get; set; }

        public int? MaxUses { get; set; }
    }
} 