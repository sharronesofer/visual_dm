using System;
using System.Collections.Generic;
using UnityEngine;

namespace VDM.DTOs.Character
{
    [Serializable]
    public class CharacterResponseDTO
    {
        public string id;
        public string name;
        public int level;
        public int experience;
        public int health;
        public int maxHealth;
        public int mana;
        public int maxMana;
        public Dictionary<string, int> attributes;
        public Dictionary<string, int> skills;
        public List<string> abilities;
        public string currentLocation;
        public DateTime createdAt;
        public DateTime updatedAt;
        public bool isActive;
        
        public CharacterResponseDTO()
        {
            attributes = new Dictionary<string, int>();
            skills = new Dictionary<string, int>();
            abilities = new List<string>();
        }
    }

    [Serializable]
    public class CharacterCreateDTO
    {
        public string name;
        public Dictionary<string, int> attributes;
        
        public CharacterCreateDTO()
        {
            attributes = new Dictionary<string, int>();
        }
    }

    [Serializable]
    public class CharacterUpdateDTO
    {
        public string name;
        public int health;
        public int mana;
        public Dictionary<string, int> attributes;
        public Dictionary<string, int> skills;
        public string currentLocation;
        
        public CharacterUpdateDTO()
        {
            attributes = new Dictionary<string, int>();
            skills = new Dictionary<string, int>();
        }
    }

    [Serializable]
    public class CharacterListResponseDTO
    {
        public List<CharacterResponseDTO> characters;
        public int totalCount;
        public int page;
        public int pageSize;
        
        public CharacterListResponseDTO()
        {
            characters = new List<CharacterResponseDTO>();
        }
    }

    [Serializable]
    public class ExperienceGrantDTO
    {
        public int amount;
        public string source;
        public string reason;
    }

    [Serializable]
    public class SkillIncreaseDTO
    {
        public string skillName;
        public int amount;
        public string source;
    }

    [Serializable]
    public class AbilitySelectionDTO
    {
        public string abilityId;
        public string abilityName;
        public string description;
    }

    [Serializable]
    public class CharacterProgressionResponseDTO
    {
        public string characterId;
        public int currentLevel;
        public int currentExperience;
        public int experienceToNextLevel;
        public List<string> availableAbilities;
        public Dictionary<string, int> skillProgression;
        
        public CharacterProgressionResponseDTO()
        {
            availableAbilities = new List<string>();
            skillProgression = new Dictionary<string, int>();
        }
    }

    [Serializable]
    public class CharacterModel
    {
        public string id;
        public string name;
        public int level;
        public Vector3 position;
        public Quaternion rotation;
        public bool isPlayer;
        
        public CharacterModel()
        {
            position = Vector3.zero;
            rotation = Quaternion.identity;
        }
    }
} 