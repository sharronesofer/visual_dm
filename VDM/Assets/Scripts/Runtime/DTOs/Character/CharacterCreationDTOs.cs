using System;
using System.Collections.Generic;
using UnityEngine;

namespace VDM.DTOs.Character
{
    /// <summary>
    /// Complete character data transfer object for character creation and management
    /// </summary>
    [Serializable]
    public class CharacterDTO
    {
        public string Id { get; set; }
        public string Name { get; set; }
        public string PlayerId { get; set; }
        public RaceDTO Race { get; set; }
        public BackgroundDTO Background { get; set; }
        public AttributesDTO Attributes { get; set; }
        public Dictionary<string, int> Skills { get; set; } = new Dictionary<string, int>();
        public List<string> Proficiencies { get; set; } = new List<string>();
        public string PortraitUrl { get; set; }
        public int Level { get; set; } = 1;
        public int ExperiencePoints { get; set; } = 0;
        public int HitPoints { get; set; }
        public int MaxHitPoints { get; set; }
        public int ArmorClass { get; set; } = 10;
        public string Description { get; set; }
        public string Backstory { get; set; }
        public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
        public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;
        public bool IsActive { get; set; } = true;
    }

    /// <summary>
    /// Race information and bonuses
    /// </summary>
    [Serializable]
    public class RaceDTO
    {
        public string Id { get; set; }
        public string Name { get; set; }
        public string Description { get; set; }
        public string FlavorText { get; set; }
        public AttributeBonusesDTO AttributeBonuses { get; set; } = new AttributeBonusesDTO();
        public List<string> RacialTraits { get; set; } = new List<string>();
        public List<string> SkillProficiencies { get; set; } = new List<string>();
        public List<string> Languages { get; set; } = new List<string>();
        public int Size { get; set; } = 1; // 0=Small, 1=Medium, 2=Large
        public int Speed { get; set; } = 30;
        public string ImageUrl { get; set; }
    }

    /// <summary>
    /// Background information and benefits
    /// </summary>
    [Serializable]
    public class BackgroundDTO
    {
        public string Id { get; set; }
        public string Name { get; set; }
        public string Description { get; set; }
        public string FlavorText { get; set; }
        public List<string> SkillProficiencies { get; set; } = new List<string>();
        public List<string> ToolProficiencies { get; set; } = new List<string>();
        public List<string> Languages { get; set; } = new List<string>();
        public EquipmentPackageDTO StartingEquipment { get; set; } = new EquipmentPackageDTO();
        public string Feature { get; set; }
        public string FeatureDescription { get; set; }
        public List<string> PersonalityTraits { get; set; } = new List<string>();
        public List<string> Ideals { get; set; } = new List<string>();
        public List<string> Bonds { get; set; } = new List<string>();
        public List<string> Flaws { get; set; } = new List<string>();
    }

    /// <summary>
    /// Character attributes (ability scores)
    /// </summary>
    [Serializable]
    public class AttributesDTO
    {
        public int Strength { get; set; } = 10;
        public int Dexterity { get; set; } = 10;
        public int Constitution { get; set; } = 10;
        public int Intelligence { get; set; } = 10;
        public int Wisdom { get; set; } = 10;
        public int Charisma { get; set; } = 10;

        public int GetModifier(int attributeValue)
        {
            return (attributeValue - 10) / 2;
        }

        public int GetStrengthModifier() => GetModifier(Strength);
        public int GetDexterityModifier() => GetModifier(Dexterity);
        public int GetConstitutionModifier() => GetModifier(Constitution);
        public int GetIntelligenceModifier() => GetModifier(Intelligence);
        public int GetWisdomModifier() => GetModifier(Wisdom);
        public int GetCharismaModifier() => GetModifier(Charisma);

        public Dictionary<string, int> ToDictionary()
        {
            return new Dictionary<string, int>
            {
                { "Strength", Strength },
                { "Dexterity", Dexterity },
                { "Constitution", Constitution },
                { "Intelligence", Intelligence },
                { "Wisdom", Wisdom },
                { "Charisma", Charisma }
            };
        }
    }

    /// <summary>
    /// Attribute bonuses from race or other sources
    /// </summary>
    [Serializable]
    public class AttributeBonusesDTO
    {
        public int Strength { get; set; } = 0;
        public int Dexterity { get; set; } = 0;
        public int Constitution { get; set; } = 0;
        public int Intelligence { get; set; } = 0;
        public int Wisdom { get; set; } = 0;
        public int Charisma { get; set; } = 0;

        public AttributesDTO ApplyTo(AttributesDTO baseAttributes)
        {
            return new AttributesDTO
            {
                Strength = baseAttributes.Strength + Strength,
                Dexterity = baseAttributes.Dexterity + Dexterity,
                Constitution = baseAttributes.Constitution + Constitution,
                Intelligence = baseAttributes.Intelligence + Intelligence,
                Wisdom = baseAttributes.Wisdom + Wisdom,
                Charisma = baseAttributes.Charisma + Charisma
            };
        }
    }

    /// <summary>
    /// Starting equipment package
    /// </summary>
    [Serializable]
    public class EquipmentPackageDTO
    {
        public List<EquipmentItemDTO> Items { get; set; } = new List<EquipmentItemDTO>();
        public int StartingGold { get; set; } = 0;
    }

    /// <summary>
    /// Equipment item
    /// </summary>
    [Serializable]
    public class EquipmentItemDTO
    {
        public string Id { get; set; }
        public string Name { get; set; }
        public string Type { get; set; }
        public string Description { get; set; }
        public int Quantity { get; set; } = 1;
        public int Weight { get; set; } = 0;
        public int Value { get; set; } = 0;
    }

    /// <summary>
    /// Character creation request for backend
    /// </summary>
    [Serializable]
    public class CharacterCreationRequestDTO
    {
        public string PlayerId { get; set; }
        public string Name { get; set; }
        public string RaceId { get; set; }
        public string BackgroundId { get; set; }
        public AttributesDTO Attributes { get; set; }
        public string PortraitUrl { get; set; }
        public string Description { get; set; }
        public string Backstory { get; set; }
        public Dictionary<string, string> PersonalityTraits { get; set; } = new Dictionary<string, string>();
    }

    /// <summary>
    /// Character creation response from backend
    /// </summary>
    [Serializable]
    public class CharacterCreationResponseDTO
    {
        public bool Success { get; set; }
        public string Message { get; set; }
        public CharacterDTO Character { get; set; }
        public List<string> Errors { get; set; } = new List<string>();
    }

    /// <summary>
    /// Available races response
    /// </summary>
    [Serializable]
    public class AvailableRacesResponseDTO
    {
        public List<RaceDTO> Races { get; set; } = new List<RaceDTO>();
        public bool Success { get; set; } = true;
        public string Message { get; set; }
    }

    /// <summary>
    /// Available backgrounds response
    /// </summary>
    [Serializable]
    public class AvailableBackgroundsResponseDTO
    {
        public List<BackgroundDTO> Backgrounds { get; set; } = new List<BackgroundDTO>();
        public bool Success { get; set; } = true;
        public string Message { get; set; }
    }

    /// <summary>
    /// Character validation response
    /// </summary>
    [Serializable]
    public class CharacterValidationResponseDTO
    {
        public bool IsValid { get; set; }
        public List<string> Errors { get; set; } = new List<string>();
        public List<string> Warnings { get; set; } = new List<string>();
        public CharacterStatsDTO CalculatedStats { get; set; }
    }

    /// <summary>
    /// Calculated character statistics
    /// </summary>
    [Serializable]
    public class CharacterStatsDTO
    {
        public int HitPoints { get; set; }
        public int ArmorClass { get; set; }
        public int Initiative { get; set; }
        public int Speed { get; set; }
        public Dictionary<string, int> SavingThrows { get; set; } = new Dictionary<string, int>();
        public Dictionary<string, int> Skills { get; set; } = new Dictionary<string, int>();
        public List<string> Proficiencies { get; set; } = new List<string>();
    }

    /// <summary>
    /// Point buy configuration
    /// </summary>
    [Serializable]
    public class PointBuyConfigDTO
    {
        public int TotalPoints { get; set; } = 27;
        public int MinAttribute { get; set; } = 8;
        public int MaxAttribute { get; set; } = 15;
        public Dictionary<int, int> PointCosts { get; set; } = new Dictionary<int, int>
        {
            { 8, 0 }, { 9, 1 }, { 10, 2 }, { 11, 3 }, { 12, 4 }, { 13, 5 }, { 14, 7 }, { 15, 9 }
        };
    }

    /// <summary>
    /// Standard array configuration
    /// </summary>
    [Serializable]
    public class StandardArrayConfigDTO
    {
        public List<int> AttributeValues { get; set; } = new List<int> { 15, 14, 13, 12, 10, 8 };
    }

    /// <summary>
    /// Character creation step tracking
    /// </summary>
    [Serializable]
    public class CharacterCreationProgressDTO
    {
        public int CurrentStep { get; set; } = 0;
        public bool RaceSelected { get; set; } = false;
        public bool AttributesAllocated { get; set; } = false;
        public bool BackgroundSelected { get; set; } = false;
        public bool DetailsCompleted { get; set; } = false;
        public bool ReadyToCreate { get; set; } = false;
        
        public string GetCurrentStepName()
        {
            switch (CurrentStep)
            {
                case 0: return "Race Selection";
                case 1: return "Attribute Allocation";
                case 2: return "Background Selection";
                case 3: return "Character Details";
                case 4: return "Review & Create";
                default: return "Unknown Step";
            }
        }
    }

    /// <summary>
    /// Trait selection for personality
    /// </summary>
    [Serializable]
    public class TraitSelectionDTO
    {
        public string PersonalityTrait { get; set; }
        public string Ideal { get; set; }
        public string Bond { get; set; }
        public string Flaw { get; set; }
    }
} 