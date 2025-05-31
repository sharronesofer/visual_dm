using System;
using System.Collections.Generic;
using VDM.DTOs.Core.Shared;

namespace VDM.DTOs.Game.Character
{
    /// <summary>
    /// Character mesh slot for swappable components
    /// </summary>
    [Serializable]
    public class MeshSlotDTO
    {
        public string Name { get; set; } = string.Empty;
        public string MeshId { get; set; }
        public List<string> CompatibleTypes { get; set; } = new List<string>();
    }

    /// <summary>
    /// Character blend shape for morphing
    /// </summary>
    [Serializable]
    public class BlendShapeDTO
    {
        public string Name { get; set; } = string.Empty;
        public float Value { get; set; } = 0.0f;
    }

    /// <summary>
    /// Material assignment for character customization
    /// </summary>
    [Serializable]
    public class MaterialAssignmentDTO
    {
        public string Slot { get; set; } = string.Empty;
        public string MaterialId { get; set; } = string.Empty;
        public Dictionary<string, object> Properties { get; set; } = new Dictionary<string, object>();
    }

    /// <summary>
    /// Character visual model configuration
    /// </summary>
    [Serializable]
    public class CharacterModelDTO
    {
        public string Race { get; set; } = "human";
        public string BaseMesh { get; set; } = "base_human";
        public Dictionary<string, MeshSlotDTO> MeshSlots { get; set; } = new Dictionary<string, MeshSlotDTO>();
        public Dictionary<string, BlendShapeDTO> BlendShapes { get; set; } = new Dictionary<string, BlendShapeDTO>();
        public Dictionary<string, MaterialAssignmentDTO> Materials { get; set; } = new Dictionary<string, MaterialAssignmentDTO>();
        public Dictionary<string, float> Scale { get; set; } = new Dictionary<string, float> 
        { 
            { "height", 1.0f }, 
            { "build", 0.5f } 
        };
    }

    /// <summary>
    /// Character attributes (STR, DEX, CON, etc.)
    /// </summary>
    [Serializable]
    public class CharacterAttributesDTO
    {
        public int Strength { get; set; } = 10;
        public int Dexterity { get; set; } = 10;
        public int Constitution { get; set; } = 10;
        public int Intelligence { get; set; } = 10;
        public int Wisdom { get; set; } = 10;
        public int Charisma { get; set; } = 10;
    }

    /// <summary>
    /// Character skill information
    /// </summary>
    [Serializable]
    public class CharacterSkillDTO
    {
        public string Name { get; set; } = string.Empty;
        public int Level { get; set; } = 0;
        public bool Proficient { get; set; } = false;
        public string Attribute { get; set; } = string.Empty;
        public int Modifier { get; set; } = 0;
    }

    /// <summary>
    /// Character progression information
    /// </summary>
    [Serializable]
    public class CharacterProgressionDTO
    {
        public int Level { get; set; } = 1;
        public int Experience { get; set; } = 0;
        public int ExperienceToNextLevel { get; set; } = 1000;
        public string Class { get; set; }
        public string Subclass { get; set; }
    }

    /// <summary>
    /// Character health and status information
    /// </summary>
    [Serializable]
    public class CharacterHealthDTO
    {
        public int HitPoints { get; set; } = 100;
        public int MaxHitPoints { get; set; } = 100;
        public int TemporaryHitPoints { get; set; } = 0;
        public int ArmorClass { get; set; } = 10;
        public List<string> Conditions { get; set; } = new List<string>();
    }

    /// <summary>
    /// Main character DTO
    /// </summary>
    [Serializable]
    public class CharacterDTO : MetadataDTO
    {
        public string Id { get; set; } = string.Empty;
        public string Name { get; set; } = string.Empty;
        public string Description { get; set; }
        public string OwnerId { get; set; } = string.Empty;
        public string Race { get; set; } = "human";
        public string Background { get; set; }
        public string Alignment { get; set; }
        public CharacterAttributesDTO Attributes { get; set; } = new CharacterAttributesDTO();
        public Dictionary<string, CharacterSkillDTO> Skills { get; set; } = new Dictionary<string, CharacterSkillDTO>();
        public CharacterProgressionDTO Progression { get; set; } = new CharacterProgressionDTO();
        public CharacterHealthDTO Health { get; set; } = new CharacterHealthDTO();
        public CharacterModelDTO VisualModel { get; set; }
        public CoordinateDTO Location { get; set; }
        public Dictionary<string, object> Properties { get; set; } = new Dictionary<string, object>();
        public bool IsNpc { get; set; } = false;
        public string Status { get; set; } = "active";
    }

    /// <summary>
    /// Character creation request
    /// </summary>
    [Serializable]
    public class CreateCharacterRequestDTO
    {
        public string Name { get; set; } = string.Empty;
        public string Race { get; set; } = "human";
        public string Class { get; set; }
        public string Background { get; set; }
        public string Alignment { get; set; }
        public CharacterAttributesDTO Attributes { get; set; }
        public string Description { get; set; }
        public CharacterModelDTO VisualModel { get; set; }
    }

    /// <summary>
    /// Character update request
    /// </summary>
    [Serializable]
    public class UpdateCharacterRequestDTO
    {
        public string Name { get; set; }
        public string Description { get; set; }
        public CharacterAttributesDTO Attributes { get; set; }
        public Dictionary<string, CharacterSkillDTO> Skills { get; set; }
        public CharacterProgressionDTO Progression { get; set; }
        public CharacterHealthDTO Health { get; set; }
        public CharacterModelDTO VisualModel { get; set; }
        public CoordinateDTO Location { get; set; }
        public Dictionary<string, object> Properties { get; set; }
        public string Status { get; set; }
    }

    /// <summary>
    /// Character response DTO - main response type used throughout the system
    /// </summary>
    [Serializable]
    public class CharacterResponseDTO : SuccessResponseDTO
    {
        public CharacterDTO Character { get; set; } = new CharacterDTO();
    }

    /// <summary>
    /// Character creation DTO - alias for CreateCharacterRequestDTO
    /// </summary>
    [Serializable]
    public class CharacterCreateDTO : CreateCharacterRequestDTO
    {
    }

    /// <summary>
    /// Character update DTO - alias for UpdateCharacterRequestDTO
    /// </summary>
    [Serializable]
    public class CharacterUpdateDTO : UpdateCharacterRequestDTO
    {
    }

    /// <summary>
    /// Experience grant request DTO
    /// </summary>
    [Serializable]
    public class ExperienceGrantDTO
    {
        public int Amount { get; set; } = 0;
        public string Source { get; set; }
        public string Reason { get; set; }
    }

    /// <summary>
    /// Skill increase request DTO
    /// </summary>
    [Serializable]
    public class SkillIncreaseDTO
    {
        public string SkillName { get; set; } = string.Empty;
        public int IncreaseAmount { get; set; } = 1;
        public string Reason { get; set; }
    }

    /// <summary>
    /// Ability selection request DTO
    /// </summary>
    [Serializable]
    public class AbilitySelectionDTO
    {
        public string AbilityName { get; set; } = string.Empty;
        public string AbilityType { get; set; }
        public string Source { get; set; }
    }

    /// <summary>
    /// Character progression response DTO
    /// </summary>
    [Serializable]
    public class CharacterProgressionResponseDTO : SuccessResponseDTO
    {
        public CharacterProgressionDTO Progression { get; set; } = new CharacterProgressionDTO();
        public List<string> AvailableAbilities { get; set; } = new List<string>();
        public Dictionary<string, object> LevelUpBenefits { get; set; } = new Dictionary<string, object>();
    }

    /// <summary>
    /// Character list response DTO
    /// </summary>
    [Serializable]
    public class CharacterListResponseDTO : SuccessResponseDTO
    {
        public List<CharacterDTO> Characters { get; set; } = new List<CharacterDTO>();
        public int TotalCount { get; set; } = 0;
    }

    /// <summary>
    /// Character model for Unity systems - bridge between DTO and Unity
    /// </summary>
    [Serializable]
    public class CharacterModel
    {
        public string Id { get; set; } = string.Empty;
        public string Name { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
        public string OwnerId { get; set; } = string.Empty;
        public string Race { get; set; } = "human";
        public string Background { get; set; } = string.Empty;
        public string Alignment { get; set; } = string.Empty;
        public CharacterAttributesDTO Attributes { get; set; } = new CharacterAttributesDTO();
        public Dictionary<string, CharacterSkillDTO> Skills { get; set; } = new Dictionary<string, CharacterSkillDTO>();
        public CharacterProgressionDTO Progression { get; set; } = new CharacterProgressionDTO();
        public CharacterHealthDTO Health { get; set; } = new CharacterHealthDTO();
        public CharacterModelDTO VisualModel { get; set; } = new CharacterModelDTO();
        public CoordinateDTO Location { get; set; } = new CoordinateDTO();
        public Dictionary<string, object> Properties { get; set; } = new Dictionary<string, object>();
        public bool IsNpc { get; set; } = false;
        public string Status { get; set; } = "active";
    }
} 