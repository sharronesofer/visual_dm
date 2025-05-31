using System;
using System.Collections.Generic;
using System.Linq;
using VDM.DTOs.Core.Shared;

namespace VDM.DTOs.Economic.Equipment
{
    // ===========================================
    // ENUMS - Equipment System Types
    // ===========================================

    public enum EquipmentType
    {
        Weapon,     // Melee/ranged weapons
        Armor,      // Body armor protection
        Shield,     // Blocking equipment
        Accessory,  // Rings, amulets, etc.
        Tool,       // Crafting/utility tools
        Misc        // Other equippable items
    }

    public enum EquipmentSlot
    {
        Head,       // Helmets, hats
        Body,       // Chest armor, robes
        Hands,      // Gloves, gauntlets
        Feet,       // Boots, shoes
        MainHand,   // Primary weapon
        OffHand,    // Shield, secondary weapon
        Ring,       // Rings (multiple allowed)
        Neck,       // Amulets, necklaces
        Waist,      // Belts
        Back,       // Cloaks, capes
        Accessory   // General accessories
    }

    public enum ItemRarity
    {
        Common,     // Basic items
        Uncommon,   // Enhanced items
        Rare,       // Powerful items
        Epic,       // Very powerful items
        Legendary,  // Extremely powerful items
        Artifact    // Unique legendary items
    }

    public enum WeaponType
    {
        Sword,      // One-handed swords
        GreatSword, // Two-handed swords
        Axe,        // One-handed axes
        GreatAxe,   // Two-handed axes
        Mace,       // Blunt weapons
        Hammer,     // Two-handed blunt
        Dagger,     // Light piercing
        Spear,      // Polearms
        Staff,      // Magical staffs
        Wand,       // Magical wands
        Bow,        // Ranged bows
        Crossbow,   // Mechanical ranged
        Thrown,     // Throwing weapons
        Unarmed     // Fist weapons
    }

    public enum ArmorType
    {
        Cloth,      // Light magical armor
        Leather,    // Light physical armor
        Studded,    // Medium armor
        Chain,      // Medium metal armor
        Scale,      // Medium scaled armor
        Plate,      // Heavy metal armor
        Shield      // Blocking equipment
    }

    public enum DamageType
    {
        Physical,   // Physical damage
        Slashing,   // Cutting damage
        Piercing,   // Stabbing damage
        Bludgeoning,// Blunt damage
        Fire,       // Fire elemental
        Ice,        // Ice/cold elemental
        Lightning,  // Electric elemental
        Acid,       // Corrosive damage
        Poison,     // Toxic damage
        Necrotic,   // Death magic
        Radiant,    // Holy/light magic
        Psychic,    // Mental damage
        Force       // Pure magical force
    }

    public enum DurabilityStatus
    {
        Perfect,        // 100% durability
        Excellent,      // 90-99% durability
        Good,          // 75-89% durability
        Worn,          // 50-74% durability
        Damaged,       // 25-49% durability
        VeryDamaged,   // 10-24% durability
        Broken         // 0-9% durability
    }

    public enum IdentificationLevel
    {
        Unknown,        // Completely unidentified
        Basic,          // Name and type known
        Partial,        // Some properties known
        Advanced,       // Most properties known
        Complete        // All properties known
    }

    // ===========================================
    // CORE EQUIPMENT DTOs
    // ===========================================

    /// <summary>
    /// Base equipment item DTO
    /// </summary>
    public class EquipmentItemDTO : MetadataDTO
    {
        public string Id { get; set; }

        public string Name { get; set; }

        public string Description { get; set; }

        public EquipmentType EquipmentType { get; set; }

        public EquipmentSlot Slot { get; set; }

        public ItemRarity Rarity { get; set; } = ItemRarity.Common;

        public int Value { get; set; } = 0;

        public float Weight { get; set; } = 1.0f;

        public int LevelRequirement { get; set; } = 1;

        public Dictionary<string, int> StatRequirements { get; set; } = new Dictionary<string, int>();

        public List<string> ClassRestrictions { get; set; } = new List<string>();

        public List<string> FactionRestrictions { get; set; } = new List<string>();

        public bool IsIdentified { get; set; } = true;

        public IdentificationLevel IdentificationLevel { get; set; } = IdentificationLevel.Complete;

        public List<string> HiddenProperties { get; set; } = new List<string>();

        public string LoreText { get; set; }

        public string FlavorText { get; set; }

        public string IconId { get; set; }

        public string ModelId { get; set; }

        public string Material { get; set; }

        public float Quality { get; set; } = 1.0f;

        public int EnchantmentSlots { get; set; } = 0;

        public int UsedEnchantmentSlots { get; set; } = 0;

        public List<string> Tags { get; set; } = new List<string>();

        public Dictionary<string, object> CustomProperties { get; set; } = new Dictionary<string, object>();

        // Computed properties
        public bool CanBeEnchanted => EnchantmentSlots > UsedEnchantmentSlots;
        public int AvailableEnchantmentSlots => EnchantmentSlots - UsedEnchantmentSlots;
        public bool IsFullyIdentified => IdentificationLevel == IdentificationLevel.Complete;
    }

    /// <summary>
    /// Equipment durability information DTO
    /// </summary>
    public class EquipmentDurabilityDTO
    {
        public float Current { get; set; } = 100.0f;

        public float Maximum { get; set; } = 100.0f;

        public float WearRate { get; set; } = 1.0f;

        public bool IsBroken { get; set; } = false;

        public int RepairCost { get; set; } = 0;

        public Dictionary<string, int> RepairMaterials { get; set; } = new Dictionary<string, int>();

        public DateTime? LastRepairDate { get; set; }

        // Computed properties
        public float Percentage => Maximum > 0 ? (Current / Maximum) * 100f : 0f;
        public DurabilityStatus Status
        {
            get
            {
                var percentage = Percentage;
                if (percentage >= 100f) return DurabilityStatus.Perfect;
                if (percentage >= 90f) return DurabilityStatus.Excellent;
                if (percentage >= 75f) return DurabilityStatus.Good;
                if (percentage >= 50f) return DurabilityStatus.Worn;
                if (percentage >= 25f) return DurabilityStatus.Damaged;
                if (percentage >= 10f) return DurabilityStatus.VeryDamaged;
                return DurabilityStatus.Broken;
            }
        }
        public float StatPenaltyMultiplier
        {
            get
            {
                return Status switch
                {
                    DurabilityStatus.Perfect => 0.0f,
                    DurabilityStatus.Excellent => 0.0f,
                    DurabilityStatus.Good => 0.0f,
                    DurabilityStatus.Worn => 0.1f,
                    DurabilityStatus.Damaged => 0.25f,
                    DurabilityStatus.VeryDamaged => 0.5f,
                    DurabilityStatus.Broken => 1.0f,
                    _ => 0.0f
                };
            }
        }
    }

    /// <summary>
    /// Equipment statistics DTO
    /// </summary>
    public class EquipmentStatsDTO
    {
        public int ArmorClass { get; set; } = 0;

        public int AttackBonus { get; set; } = 0;

        public int DamageBonus { get; set; } = 0;

        public Dictionary<string, int> StatBonuses { get; set; } = new Dictionary<string, int>();

        public Dictionary<DamageType, float> Resistances { get; set; } = new Dictionary<DamageType, float>();

        public List<DamageType> Immunities { get; set; } = new List<DamageType>();

        public Dictionary<DamageType, float> Vulnerabilities { get; set; } = new Dictionary<DamageType, float>();

        public List<string> SpecialAbilities { get; set; } = new List<string>();

        public int MovementBonus { get; set; } = 0;

        public Dictionary<string, int> SkillBonuses { get; set; } = new Dictionary<string, int>();

        public Dictionary<string, int> SavingThrowBonuses { get; set; } = new Dictionary<string, int>();

        public List<string> ConditionImmunities { get; set; } = new List<string>();
    }

    /// <summary>
    /// Weapon-specific properties DTO
    /// </summary>
    public class WeaponPropertiesDTO
    {
        public WeaponType WeaponType { get; set; }

        public string DamageDice { get; set; } = "1d4";

        public DamageType DamageType { get; set; } = DamageType.Physical;

        public int Range { get; set; } = 5; // feet

        public int Reach { get; set; } = 5; // feet

        public float CriticalChance { get; set; } = 0.05f;

        public float CriticalMultiplier { get; set; } = 2.0f;

        public float AttackSpeed { get; set; } = 1.0f;

        public bool TwoHanded { get; set; } = false;

        public bool Finesse { get; set; } = false;

        public bool Light { get; set; } = false;

        public bool Heavy { get; set; } = false;

        public bool Thrown { get; set; } = false;

        public bool Versatile { get; set; } = false;

        public string VersatileDamage { get; set; }

        public List<string> WeaponProperties { get; set; } = new List<string>();

        public string AmmunitionType { get; set; }

        public float ReloadTime { get; set; } = 0.0f;
    }

    /// <summary>
    /// Armor-specific properties DTO
    /// </summary>
    public class ArmorPropertiesDTO
    {
        public ArmorType ArmorType { get; set; }

        public int BaseArmorClass { get; set; } = 10;

        public int? MaxDexBonus { get; set; }

        public int StrengthRequirement { get; set; } = 0;

        public bool StealthDisadvantage { get; set; } = false;

        public int MovementPenalty { get; set; } = 0;

        public float NoiseLevel { get; set; } = 1.0f;

        public List<string> CoverageAreas { get; set; } = new List<string>();

        public bool Layered { get; set; } = false;

        public Dictionary<string, float> EnvironmentalProtection { get; set; } = new Dictionary<string, float>();
    }

    // ===========================================
    // EQUIPPED ITEM DTOs
    // ===========================================

    /// <summary>
    /// Equipped item DTO representing an item currently equipped by a character
    /// </summary>
    public class EquippedItemDTO : MetadataDTO
    {
        public int Id { get; set; }

        public int CharacterId { get; set; }

        public EquipmentSlot Slot { get; set; }

        public EquipmentItemDTO Item { get; set; }

        public EquipmentDurabilityDTO Durability { get; set; }

        public EquipmentStatsDTO Stats { get; set; }

        public WeaponPropertiesDTO WeaponProperties { get; set; }

        public ArmorPropertiesDTO ArmorProperties { get; set; }

        public List<EquipmentEnchantmentDTO> Enchantments { get; set; } = new List<EquipmentEnchantmentDTO>();

        public string SetId { get; set; }

        public string SetPieceName { get; set; }

        public DateTime EquippedAt { get; set; }

        public DateTime? LastUsed { get; set; }

        public Dictionary<string, object> Properties { get; set; } = new Dictionary<string, object>();

        // Computed properties
        public bool IsWeapon => Item.EquipmentType == EquipmentType.Weapon;
        public bool IsArmor => Item.EquipmentType == EquipmentType.Armor;
        public bool IsBroken => Durability.IsBroken;
        public bool NeedsRepair => Durability.Percentage < 25f;
        public bool IsPartOfSet => !string.IsNullOrEmpty(SetId);
    }

    /// <summary>
    /// Equipment enchantment DTO
    /// </summary>
    public class EquipmentEnchantmentDTO
    {
        public string Id { get; set; }

        public string Name { get; set; }

        public string Description { get; set; }

        public string Type { get; set; }

        public int Level { get; set; } = 1;

        public ItemRarity Rarity { get; set; }

        public Dictionary<string, object> Effects { get; set; } = new Dictionary<string, object>();

        public int? Charges { get; set; }

        public int? MaxCharges { get; set; }

        public int? Duration { get; set; } // seconds

        public int? Cooldown { get; set; } // seconds

        public Dictionary<string, object> ActivationRequirements { get; set; } = new Dictionary<string, object>();

        public int EnchantmentSlotsUsed { get; set; } = 1;

        // Computed properties
        public bool HasCharges => Charges.HasValue && MaxCharges.HasValue;
        public bool IsExpended => HasCharges && Charges <= 0;
        public float ChargePercentage => HasCharges && MaxCharges > 0 ? (float)Charges.Value / MaxCharges.Value : 1.0f;
    }

    // ===========================================
    // EQUIPMENT SET DTOs
    // ===========================================

    /// <summary>
    /// Equipment set definition DTO
    /// </summary>
    public class EquipmentSetDTO
    {
        public string Id { get; set; }

        public string Name { get; set; }

        public string Description { get; set; }

        public string Lore { get; set; }

        public List<EquipmentSetPieceDTO> SetPieces { get; set; } = new List<EquipmentSetPieceDTO>();

        public List<EquipmentSetBonusDTO> SetBonuses { get; set; } = new List<EquipmentSetBonusDTO>();

        public int MinimumLevel { get; set; } = 1;

        public ItemRarity Rarity { get; set; }

        public string Theme { get; set; }

        public string Origin { get; set; }

        public string CreatedBy { get; set; }

        // Computed properties
        public int TotalPieces => SetPieces.Count;
        public int MaxBonusTier => SetBonuses.Count > 0 ? SetBonuses.Max(b => b.PiecesRequired) : 0;
    }

    /// <summary>
    /// Equipment set piece DTO
    /// </summary>
    public class EquipmentSetPieceDTO
    {
        public string ItemId { get; set; }

        public string PieceName { get; set; }

        public EquipmentSlot Slot { get; set; }

        public bool Required { get; set; } = true;

        public List<string> AlternativeItems { get; set; } = new List<string>();
    }

    /// <summary>
    /// Equipment set bonus DTO
    /// </summary>
    public class EquipmentSetBonusDTO
    {
        public int PiecesRequired { get; set; }

        public string Name { get; set; }

        public string Description { get; set; }

        public Dictionary<string, int> StatBonuses { get; set; } = new Dictionary<string, int>();

        public List<string> SpecialEffects { get; set; } = new List<string>();

        public List<string> PassiveAbilities { get; set; } = new List<string>();

        public List<string> ActiveAbilities { get; set; } = new List<string>();
    }

    /// <summary>
    /// Character's active set bonuses DTO
    /// </summary>
    public class ActiveSetBonusDTO
    {
        public string SetId { get; set; }

        public string SetName { get; set; }

        public int EquippedPieces { get; set; }

        public int TotalPieces { get; set; }

        public List<EquipmentSetBonusDTO> ActiveBonuses { get; set; } = new List<EquipmentSetBonusDTO>();

        public EquipmentSetBonusDTO NextBonus { get; set; }

        public List<EquipmentSlot> EquippedPieceSlots { get; set; } = new List<EquipmentSlot>();

        // Computed properties
        public float CompletionPercentage => TotalPieces > 0 ? (float)EquippedPieces / TotalPieces : 0f;
        public bool IsComplete => EquippedPieces >= TotalPieces;
        public int PiecesNeededForNextBonus => NextBonus?.PiecesRequired - EquippedPieces ?? 0;
    }

    // ===========================================
    // EQUIPMENT MANAGEMENT DTOs
    // ===========================================

    /// <summary>
    /// Equip item request DTO
    /// </summary>
    public class EquipItemRequestDTO
    {
        public int CharacterId { get; set; }

        public string ItemId { get; set; }

        public EquipmentSlot Slot { get; set; }

        public bool ForceEquip { get; set; } = false;

        public bool AutoUnequipConflicting { get; set; } = true;
    }

    /// <summary>
    /// Unequip item request DTO
    /// </summary>
    public class UnequipItemRequestDTO
    {
        public int CharacterId { get; set; }

        public EquipmentSlot Slot { get; set; }

        public bool ToInventory { get; set; } = true;
    }

    /// <summary>
    /// Character equipment loadout DTO
    /// </summary>
    public class CharacterEquipmentDTO
    {
        public int CharacterId { get; set; }

        public Dictionary<EquipmentSlot, EquippedItemDTO> EquippedItems { get; set; } = new Dictionary<EquipmentSlot, EquippedItemDTO>();

        public EquipmentStatsDTO TotalStats { get; set; }

        public List<ActiveSetBonusDTO> ActiveSetBonuses { get; set; } = new List<ActiveSetBonusDTO>();

        public float TotalWeight { get; set; } = 0.0f;

        public int TotalValue { get; set; } = 0;

        public float AverageDurability { get; set; } = 100.0f;

        public int ItemsNeedingRepair { get; set; } = 0;

        public int BrokenItems { get; set; } = 0;

        public int EnchantedItems { get; set; } = 0;

        public DateTime LastUpdated { get; set; }

        // Computed properties
        public bool HasBrokenItems => BrokenItems > 0;
        public bool NeedsMaintenance => ItemsNeedingRepair > 0 || BrokenItems > 0;
        public int TotalEquippedItems => EquippedItems.Count;
        public bool IsFullyEquipped => EquippedItems.Count >= Enum.GetValues(typeof(EquipmentSlot)).Length - 1; // -1 for multiple ring slots
    }

    // ===========================================
    // DURABILITY & REPAIR DTOs
    // ===========================================

    /// <summary>
    /// Apply durability damage request DTO
    /// </summary>
    public class ApplyDurabilityDamageRequestDTO
    {
        public int EquipmentId { get; set; }

        public float DamageAmount { get; set; }

        public string DamageType { get; set; } // "combat", "wear", "environmental"

        public string Context { get; set; }

        public bool IgnoreResistance { get; set; } = false;
    }

    /// <summary>
    /// Repair equipment request DTO
    /// </summary>
    public class RepairEquipmentRequestDTO
    {
        public int EquipmentId { get; set; }

        public float? RepairAmount { get; set; } // null for full repair

        public bool UseMaterials { get; set; } = true;

        public bool PayCost { get; set; } = true;

        public int RepairerSkillLevel { get; set; } = 50;
    }

    /// <summary>
    /// Durability damage response DTO
    /// </summary>
    public class DurabilityDamageResponseDTO : SuccessResponseDTO
    {
        public int EquipmentId { get; set; }

        public float DamageApplied { get; set; }

        public float PreviousDurability { get; set; }

        public float NewDurability { get; set; }

        public DurabilityStatus PreviousStatus { get; set; }

        public DurabilityStatus NewStatus { get; set; }

        public bool BecameBroken { get; set; } = false;

        public bool StatPenaltyChanged { get; set; } = false;
    }

    /// <summary>
    /// Repair equipment response DTO
    /// </summary>
    public class RepairEquipmentResponseDTO : SuccessResponseDTO
    {
        public int EquipmentId { get; set; }

        public float RepairAmount { get; set; }

        public float PreviousDurability { get; set; }

        public float NewDurability { get; set; }

        public int CostPaid { get; set; }

        public Dictionary<string, int> MaterialsUsed { get; set; } = new Dictionary<string, int>();

        public float RepairQuality { get; set; } = 1.0f;

        public bool WasBroken { get; set; } = false;

        public bool FullyRepaired { get; set; } = false;
    }

    // ===========================================
    // IDENTIFICATION DTOs
    // ===========================================

    /// <summary>
    /// Identify item request DTO
    /// </summary>
    public class IdentifyItemRequestDTO
    {
        public string ItemId { get; set; }

        public IdentificationLevel TargetLevel { get; set; }

        public bool PayCost { get; set; } = true;

        public int IdentifierSkillLevel { get; set; } = 50;

        public bool UseMagic { get; set; } = false;
    }

    /// <summary>
    /// Item identification response DTO
    /// </summary>
    public class ItemIdentificationResponseDTO : SuccessResponseDTO
    {
        public string ItemId { get; set; }

        public IdentificationLevel PreviousLevel { get; set; }

        public IdentificationLevel NewLevel { get; set; }

        public List<string> RevealedProperties { get; set; } = new List<string>();

        public int CostPaid { get; set; }

        public string IdentificationText { get; set; }

        public string LoreRevealed { get; set; }

        public int RemainingHiddenProperties { get; set; }
    }

    // ===========================================
    // EQUIPMENT QUERY & FILTER DTOs
    // ===========================================

    /// <summary>
    /// Equipment query request DTO
    /// </summary>
    public class EquipmentQueryRequestDTO
    {
        public int? CharacterId { get; set; }

        public List<EquipmentType> EquipmentTypes { get; set; } = new List<EquipmentType>();

        public List<EquipmentSlot> Slots { get; set; } = new List<EquipmentSlot>();

        public List<ItemRarity> Rarities { get; set; } = new List<ItemRarity>();

        public int? MinLevel { get; set; }

        public int? MaxLevel { get; set; }

        public float? MinDurability { get; set; }

        public float? MaxDurability { get; set; }

        public bool IdentifiedOnly { get; set; } = false;

        public bool ExcludeBroken { get; set; } = false;

        public bool IncludeEquipped { get; set; } = true;

        public string SetId { get; set; }

        public bool? HasEnchantments { get; set; }

        public string SearchText { get; set; }

        public List<string> Tags { get; set; } = new List<string>();

        public string SortBy { get; set; } = "name"; // "name", "rarity", "level", "durability", "value"

        public string SortOrder { get; set; } = "asc"; // "asc", "desc"

        public int Limit { get; set; } = 50;

        public int Offset { get; set; } = 0;
    }

    /// <summary>
    /// Equipment query response DTO
    /// </summary>
    public class EquipmentQueryResponseDTO : SuccessResponseDTO
    {
        public List<EquipmentItemDTO> Items { get; set; } = new List<EquipmentItemDTO>();

        public List<EquippedItemDTO> EquippedItems { get; set; } = new List<EquippedItemDTO>();

        public int TotalCount { get; set; }

        public int FilteredCount { get; set; }

        public EquipmentQueryRequestDTO QueryParameters { get; set; }
    }

    // ===========================================
    // RESPONSES & COMMON DTOs
    // ===========================================

    /// <summary>
    /// Equipment operation response DTO
    /// </summary>
    public class EquipmentResponseDTO : SuccessResponseDTO
    {
        public EquippedItemDTO EquippedItem { get; set; }

        public EquipmentItemDTO UnequippedItem { get; set; }

        public CharacterEquipmentDTO CharacterEquipment { get; set; }
    }

    /// <summary>
    /// Equipment statistics summary DTO
    /// </summary>
    public class EquipmentStatisticsDTO
    {
        public int TotalItems { get; set; }

        public int EquippedItems { get; set; }

        public Dictionary<EquipmentType, int> ItemsByType { get; set; } = new Dictionary<EquipmentType, int>();

        public Dictionary<ItemRarity, int> ItemsByRarity { get; set; } = new Dictionary<ItemRarity, int>();

        public Dictionary<DurabilityStatus, int> ItemsByDurabilityStatus { get; set; } = new Dictionary<DurabilityStatus, int>();

        public int EnchantedItems { get; set; }

        public int SetItems { get; set; }

        public int UnidentifiedItems { get; set; }

        public int TotalValue { get; set; }

        public float AverageDurability { get; set; }

        public int RepairCosts { get; set; }
    }
} 