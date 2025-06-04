using System;
using System.Collections.Generic;
using UnityEngine;

namespace VDM.DTOs.Game.Character
{
    /// <summary>
    /// Represents a weapon that can be equipped and used in combat
    /// </summary>
    [Serializable]
    public class WeaponModel
    {
        public string Id;
        public string Name;
        public string Description;
        public int Damage;
        public int Range;
        public WeaponType Type;
        public int Weight;
        public int Value;
        public List<string> Properties = new List<string>();
        
        public WeaponModel()
        {
            Id = System.Guid.NewGuid().ToString();
        }
    }

    /// <summary>
    /// Represents a spell that can be cast in combat or exploration
    /// </summary>
    [Serializable]
    public class SpellModel
    {
        public string Id;
        public string Name;
        public string Description;
        public int Level;
        public int ManaCost;
        public int Range;
        public string Duration;
        public SpellSchool School;
        public List<string> Components = new List<string>();
        
        public SpellModel()
        {
            Id = System.Guid.NewGuid().ToString();
        }
    }

    /// <summary>
    /// Item attribute bonuses for equipment items
    /// </summary>
    [Serializable]
    public class ItemAttributesDTO
    {
        public int Damage { get; set; } = 0;
        public int ArmorClass { get; set; } = 0;
        public int StrengthBonus { get; set; } = 0;
        public int DexterityBonus { get; set; } = 0;
        public int ConstitutionBonus { get; set; } = 0;
        public int IntelligenceBonus { get; set; } = 0;
        public int WisdomBonus { get; set; } = 0;
        public int CharismaBonus { get; set; } = 0;
    }

    /// <summary>
    /// Item in the game world
    /// </summary>
    [Serializable]
    public class ItemModel
    {
        public string Id;
        public string Name;
        public string Description;
        public ItemType Type;
        public int Quantity;
        public int Weight;
        public int Value;
        public bool IsConsumable;
        public Dictionary<string, object> Properties = new Dictionary<string, object>();
        public ItemAttributesDTO Stats = new ItemAttributesDTO(); // For backward compatibility with UI
        
        // Interface properties expected by InventoryPanel
        public bool IsUsable => IsConsumable || Type == ItemType.Consumable;
        public bool IsEquippable => Type == ItemType.Weapon || Type == ItemType.Armor;
        public bool CanSell => Type != ItemType.Quest;
        public bool IsStackable => IsConsumable || Type == ItemType.Material;
        public bool IsQuestItem => Type == ItemType.Quest;
        
        public ItemModel()
        {
            Id = System.Guid.NewGuid().ToString();
            Quantity = 1;
        }
    }

    /// <summary>
    /// Represents an enemy character or creature
    /// </summary>
    [Serializable]
    public class EnemyModel
    {
        public string Id;
        public string Name;
        public string Description;
        public int Level;
        public int Health;
        public int MaxHealth;
        public int ArmorClass;
        public EnemyType Type;
        public List<string> Abilities = new List<string>();
        public Dictionary<string, int> Stats = new Dictionary<string, int>();
        
        public EnemyModel()
        {
            Id = System.Guid.NewGuid().ToString();
        }
    }

    /// <summary>
    /// Weapon type enumeration
    /// </summary>
    public enum WeaponType
    {
        Sword,
        Axe,
        Mace,
        Dagger,
        Bow,
        Crossbow,
        Staff,
        Wand,
        Shield,
        Thrown
    }

    /// <summary>
    /// Spell school enumeration
    /// </summary>
    public enum SpellSchool
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
    /// Item type enumeration
    /// </summary>
    public enum ItemType
    {
        Weapon,
        Armor,
        Consumable,
        Tool,
        Treasure,
        Quest,
        Material,
        Container
    }

    /// <summary>
    /// Enemy type enumeration
    /// </summary>
    public enum EnemyType
    {
        Beast,
        Humanoid,
        Undead,
        Fiend,
        Celestial,
        Elemental,
        Fey,
        Dragon,
        Giant,
        Monstrosity
    }

    /// <summary>
    /// Represents an inventory containing items and currency
    /// </summary>
    [Serializable]
    public class InventoryModel
    {
        public string Id;
        public string CharacterId;
        public List<ItemModel> Items = new List<ItemModel>();
        public int Currency;
        public float CurrentWeight;
        public float MaxWeight;
        public int MaxSlots;
        
        public InventoryModel()
        {
            Id = System.Guid.NewGuid().ToString();
            MaxWeight = 100f;
            MaxSlots = 50;
        }
    }

    /// <summary>
    /// Represents a location in the game world
    /// </summary>
    [Serializable]
    public class LocationModel
    {
        public string Id;
        public string Name;
        public string Description;
        public LocationType Type;
        public Vector2 Position;
        public bool IsDiscovered;
        public bool IsAccessible;
        public string RegionId;
        public List<string> ConnectedLocations = new List<string>();
        public Dictionary<string, object> Properties = new Dictionary<string, object>();
        
        public LocationModel()
        {
            Id = System.Guid.NewGuid().ToString();
        }
    }

    /// <summary>
    /// Location type enumeration
    /// </summary>
    public enum LocationType
    {
        City,
        Town,
        Village,
        Dungeon,
        Forest,
        Mountain,
        Desert,
        Ocean,
        River,
        Cave,
        Ruins,
        Temple,
        Castle,
        Tower,
        Bridge,
        Crossroads,
        Camp,
        Outpost,
        Resource,
        Quest,
        Landmark
    }

    /// <summary>
    /// Represents a quest in the game
    /// </summary>
    [Serializable]
    public class QuestModel
    {
        public string Id;
        public string Title;
        public string Description;
        public QuestType Type;
        public QuestStatus Status;
        public QuestPriority Priority;
        public List<ObjectiveModel> Objectives = new List<ObjectiveModel>();
        public Dictionary<string, object> Requirements = new Dictionary<string, object>();
        public Dictionary<string, object> Rewards = new Dictionary<string, object>();
        public List<string> PrerequisiteQuestIds = new List<string>();
        public string QuestGiverId;
        public string QuestTurnInId;
        public List<string> Tags = new List<string>();
        public bool IsRepeatable;
        public int MinLevel = 1;
        public int MaxLevel = 100;
        public bool AutoComplete;
        public float RepeatCooldownHours = 24f;
        public DateTime CreatedAt;
        public DateTime UpdatedAt;
        public Dictionary<string, object> Metadata = new Dictionary<string, object>();
        public string ArcId;
        public string FactionId;
        public string RegionId;
        public Dictionary<string, object> ProgressData = new Dictionary<string, object>();
        
        public QuestModel()
        {
            Id = System.Guid.NewGuid().ToString();
            Status = QuestStatus.NotStarted;
            Type = QuestType.Side;
            Priority = QuestPriority.Medium;
            CreatedAt = DateTime.UtcNow;
            UpdatedAt = DateTime.UtcNow;
        }
    }

    /// <summary>
    /// Represents a quest objective
    /// </summary>
    [Serializable]
    public class ObjectiveModel
    {
        public int Id;
        public string Description;
        public ObjectiveType Type;
        public bool Completed;
        public List<Dictionary<string, object>> RequiredItems = new List<Dictionary<string, object>>();
        public List<Dictionary<string, object>> RequiredSkills = new List<Dictionary<string, object>>();
        public string TargetNpcId;
        public string TargetLocationId;
        public string TargetItemId;
        public string TargetEnemyId;
        public string TargetEnemyType;
        public int Quantity = 1;
        public int RequiredCount = 1;
        public int CurrentCount = 0;
        public float TimeRequirement;
        public int Order;
        public bool IsOptional;
        
        public ObjectiveModel()
        {
            Type = ObjectiveType.Collect;
        }
    }

    /// <summary>
    /// Represents the game world
    /// </summary>
    [Serializable]
    public class WorldModel
    {
        public string Id;
        public string Name;
        public string Description;
        public List<VDM.Systems.Region.Models.RegionModel> Regions = new List<VDM.Systems.Region.Models.RegionModel>();
        public Vector2 WorldSize;
        public Dictionary<string, object> Properties = new Dictionary<string, object>();
        
        public WorldModel()
        {
            Id = System.Guid.NewGuid().ToString();
            WorldSize = new Vector2(1000f, 1000f);
        }
    }

    /// <summary>
    /// Quest type enumeration
    /// </summary>
    public enum QuestType
    {
        Main,
        Side,
        Faction,
        Character,
        Daily,
        Weekly,
        Event,
        Tutorial
    }

    /// <summary>
    /// Quest status enumeration
    /// </summary>
    public enum QuestStatus
    {
        NotStarted,
        Active,
        Completed,
        Failed,
        Abandoned,
        TurnedIn
    }

    /// <summary>
    /// Quest priority enumeration
    /// </summary>
    public enum QuestPriority
    {
        Low,
        Medium,
        High,
        Urgent
    }

    /// <summary>
    /// Objective type enumeration
    /// </summary>
    public enum ObjectiveType
    {
        Dialogue,
        Collect,
        Visit,
        Kill,
        Deliver,
        Escort,
        Defend,
        Craft,
        Use,
        Interact
    }
} 