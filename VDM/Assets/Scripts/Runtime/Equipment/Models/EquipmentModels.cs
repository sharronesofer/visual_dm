using System.Collections.Generic;
using System;
using UnityEngine;


namespace VDM.Runtime.Equipment.Models
{
    /// <summary>
    /// Types of equipment
    /// </summary>
    public enum EquipmentType
    {
        Weapon,
        Armor,
        Shield,
        Accessory,
        Consumable,
        Tool,
        Miscellaneous
    }

    /// <summary>
    /// Equipment quality/rarity tiers
    /// </summary>
    public enum EquipmentQuality
    {
        Common,
        Uncommon,
        Rare,
        Epic,
        Legendary,
        Artifact
    }

    /// <summary>
    /// Equipment slot types
    /// </summary>
    public enum EquipmentSlot
    {
        None,
        MainHand,
        OffHand,
        TwoHanded,
        Head,
        Chest,
        Legs,
        Feet,
        Hands,
        Ring,
        Neck,
        Belt,
        Back
    }

    /// <summary>
    /// Weapon types for combat mechanics
    /// </summary>
    public enum WeaponType
    {
        Sword,
        Axe,
        Mace,
        Dagger,
        Spear,
        Bow,
        Crossbow,
        Staff,
        Wand,
        Unarmed
    }

    /// <summary>
    /// Armor types for protection mechanics
    /// </summary>
    public enum ArmorType
    {
        None,
        Light,
        Medium,
        Heavy,
        Natural
    }

    /// <summary>
    /// Property types for equipment enhancement
    /// </summary>
    public enum PropertyType
    {
        Magical,
        Masterwork,
        Enchanted,
        Cursed,
        Blessed,
        Elemental
    }

    /// <summary>
    /// Represents a piece of equipment with all its properties
    /// </summary>
    [Serializable]
    public class Equipment
    {
        public string Id { get; set; }
        public string Name { get; set; }
        public string Description { get; set; }
        public EquipmentType Type { get; set; }
        public EquipmentQuality Quality { get; set; }
        public EquipmentSlot Slot { get; set; }
        public WeaponType WeaponType { get; set; }
        public ArmorType ArmorType { get; set; }
        
        // Base properties
        public int Level { get; set; }
        public int Value { get; set; }
        public float Weight { get; set; }
        public bool IsIdentified { get; set; }
        public bool IsEquipped { get; set; }
        public bool IsCursed { get; set; }
        public bool IsDestroyed { get; set; }
        
        // Combat properties
        public Dictionary<string, int> Stats { get; set; } = new Dictionary<string, int>();
        public Dictionary<string, float> Bonuses { get; set; } = new Dictionary<string, float>();
        public List<EquipmentProperty> Properties { get; set; } = new List<EquipmentProperty>();
        public List<string> Enchantments { get; set; } = new List<string>();
        
        // Requirements
        public Dictionary<string, int> Requirements { get; set; } = new Dictionary<string, int>();
        public List<string> ClassRestrictions { get; set; } = new List<string>();
        
        // Evolution data
        public int EvolutionLevel { get; set; }
        public int Experience { get; set; }
        public int ExperienceToNext { get; set; }
        public bool CanEvolve { get; set; }
        
        // Durability
        public int MaxDurability { get; set; }
        public int CurrentDurability { get; set; }
        
        // Creation/modification tracking
        public DateTime CreatedAt { get; set; }
        public DateTime ModifiedAt { get; set; }
        public string CreatedBy { get; set; }
        
        public Equipment()
        {
            Id = Guid.NewGuid().ToString();
            CreatedAt = DateTime.UtcNow;
            ModifiedAt = DateTime.UtcNow;
            IsIdentified = true;
        }

        /// <summary>
        /// Get the display name including quality and enchantment info
        /// </summary>
        public string GetDisplayName()
        {
            string prefix = "";
            string suffix = "";
            
            // Add quality prefix
            switch (Quality)
            {
                case EquipmentQuality.Uncommon:
                    prefix = "Fine ";
                    break;
                case EquipmentQuality.Rare:
                    prefix = "Superior ";
                    break;
                case EquipmentQuality.Epic:
                    prefix = "Exceptional ";
                    break;
                case EquipmentQuality.Legendary:
                    prefix = "Legendary ";
                    break;
                case EquipmentQuality.Artifact:
                    prefix = "Artifact ";
                    break;
            }
            
            // Add evolution suffix
            if (EvolutionLevel > 0)
            {
                suffix = $" +{EvolutionLevel}";
            }
            
            // Add cursed prefix
            if (IsCursed)
            {
                prefix = "Cursed " + prefix;
            }
            
            return $"{prefix}{Name}{suffix}";
        }

        /// <summary>
        /// Get equipment stat value including bonuses
        /// </summary>
        public int GetStatValue(string statName)
        {
            int baseValue = Stats.ContainsKey(statName) ? Stats[statName] : 0;
            float bonus = Bonuses.ContainsKey(statName) ? Bonuses[statName] : 0f;
            return Mathf.RoundToInt(baseValue + (baseValue * bonus));
        }

        /// <summary>
        /// Check if equipment meets requirements for a character
        /// </summary>
        public bool MeetsRequirements(Dictionary<string, int> characterStats, string characterClass)
        {
            // Check stat requirements
            foreach (var requirement in Requirements)
            {
                if (!characterStats.ContainsKey(requirement.Key) || 
                    characterStats[requirement.Key] < requirement.Value)
                {
                    return false;
                }
            }
            
            // Check class restrictions
            if (ClassRestrictions.Count > 0 && !ClassRestrictions.Contains(characterClass))
            {
                return false;
            }
            
            return true;
        }

        /// <summary>
        /// Add experience to the equipment for evolution
        /// </summary>
        public bool AddExperience(int amount)
        {
            if (!CanEvolve)
                return false;
            
            Experience += amount;
            ModifiedAt = DateTime.UtcNow;
            
            return Experience >= ExperienceToNext;
        }

        /// <summary>
        /// Damage the equipment
        /// </summary>
        public void TakeDamage(int damage)
        {
            CurrentDurability = Mathf.Max(0, CurrentDurability - damage);
            ModifiedAt = DateTime.UtcNow;
            
            if (CurrentDurability <= 0)
            {
                IsDestroyed = true;
            }
        }

        /// <summary>
        /// Repair the equipment
        /// </summary>
        public void Repair(int amount)
        {
            if (IsDestroyed)
                return;
            
            CurrentDurability = Mathf.Min(MaxDurability, CurrentDurability + amount);
            ModifiedAt = DateTime.UtcNow;
        }

        /// <summary>
        /// Clone the equipment
        /// </summary>
        public Equipment Clone()
        {
            var clone = new Equipment
            {
                Id = Guid.NewGuid().ToString(),
                Name = Name,
                Description = Description,
                Type = Type,
                Quality = Quality,
                Slot = Slot,
                WeaponType = WeaponType,
                ArmorType = ArmorType,
                Level = Level,
                Value = Value,
                Weight = Weight,
                IsIdentified = IsIdentified,
                IsCursed = IsCursed,
                MaxDurability = MaxDurability,
                CurrentDurability = CurrentDurability,
                EvolutionLevel = EvolutionLevel,
                Experience = Experience,
                ExperienceToNext = ExperienceToNext,
                CanEvolve = CanEvolve,
                CreatedBy = CreatedBy
            };
            
            // Deep copy collections
            clone.Stats = new Dictionary<string, int>(Stats);
            clone.Bonuses = new Dictionary<string, float>(Bonuses);
            clone.Requirements = new Dictionary<string, int>(Requirements);
            clone.ClassRestrictions = new List<string>(ClassRestrictions);
            clone.Enchantments = new List<string>(Enchantments);
            clone.Properties = new List<EquipmentProperty>();
            foreach (var prop in Properties)
            {
                clone.Properties.Add(prop.Clone());
            }
            
            return clone;
        }
    }

    /// <summary>
    /// Represents a special property of equipment
    /// </summary>
    [Serializable]
    public class EquipmentProperty
    {
        public string Id { get; set; }
        public string Name { get; set; }
        public string Description { get; set; }
        public PropertyType Type { get; set; }
        public Dictionary<string, object> Parameters { get; set; } = new Dictionary<string, object>();
        public bool IsActive { get; set; } = true;
        public int Charges { get; set; }
        public int MaxCharges { get; set; }
        
        public EquipmentProperty()
        {
            Id = Guid.NewGuid().ToString();
        }

        public EquipmentProperty Clone()
        {
            return new EquipmentProperty
            {
                Id = Guid.NewGuid().ToString(),
                Name = Name,
                Description = Description,
                Type = Type,
                IsActive = IsActive,
                Charges = Charges,
                MaxCharges = MaxCharges,
                Parameters = new Dictionary<string, object>(Parameters)
            };
        }
    }

    /// <summary>
    /// Represents an inventory containing equipment
    /// </summary>
    [Serializable]
    public class Inventory
    {
        public string Id { get; set; }
        public string OwnerId { get; set; }
        public List<Equipment> Items { get; set; } = new List<Equipment>();
        public Dictionary<EquipmentSlot, Equipment> EquippedItems { get; set; } = new Dictionary<EquipmentSlot, Equipment>();
        public int MaxSlots { get; set; } = 50;
        public float MaxWeight { get; set; } = 100f;
        
        public Inventory()
        {
            Id = Guid.NewGuid().ToString();
        }

        /// <summary>
        /// Get current weight of all items
        /// </summary>
        public float GetCurrentWeight()
        {
            float weight = 0f;
            foreach (var item in Items)
            {
                weight += item.Weight;
            }
            foreach (var equipped in EquippedItems.Values)
            {
                weight += equipped.Weight;
            }
            return weight;
        }

        /// <summary>
        /// Check if item can be added to inventory
        /// </summary>
        public bool CanAddItem(Equipment item)
        {
            if (Items.Count >= MaxSlots)
                return false;
            
            if (GetCurrentWeight() + item.Weight > MaxWeight)
                return false;
            
            return true;
        }

        /// <summary>
        /// Add item to inventory
        /// </summary>
        public bool AddItem(Equipment item)
        {
            if (!CanAddItem(item))
                return false;
            
            Items.Add(item);
            return true;
        }

        /// <summary>
        /// Remove item from inventory
        /// </summary>
        public bool RemoveItem(string itemId)
        {
            var item = Items.Find(i => i.Id == itemId);
            if (item != null)
            {
                Items.Remove(item);
                return true;
            }
            return false;
        }

        /// <summary>
        /// Equip an item
        /// </summary>
        public bool EquipItem(string itemId, Dictionary<string, int> characterStats, string characterClass)
        {
            var item = Items.Find(i => i.Id == itemId);
            if (item == null)
                return false;
            
            if (!item.MeetsRequirements(characterStats, characterClass))
                return false;
            
            // Unequip existing item in slot
            if (EquippedItems.ContainsKey(item.Slot))
            {
                UnequipItem(item.Slot);
            }
            
            // Move item from inventory to equipped
            Items.Remove(item);
            EquippedItems[item.Slot] = item;
            item.IsEquipped = true;
            
            return true;
        }

        /// <summary>
        /// Unequip an item
        /// </summary>
        public bool UnequipItem(EquipmentSlot slot)
        {
            if (!EquippedItems.ContainsKey(slot))
                return false;
            
            var item = EquippedItems[slot];
            EquippedItems.Remove(slot);
            item.IsEquipped = false;
            
            // Add back to inventory if there's space
            if (CanAddItem(item))
            {
                Items.Add(item);
                return true;
            }
            
            // Drop item if no space
            return false;
        }

        /// <summary>
        /// Get all equipped items as a list
        /// </summary>
        public List<Equipment> GetEquippedItems()
        {
            return new List<Equipment>(EquippedItems.Values);
        }

        /// <summary>
        /// Get total stats from all equipped items
        /// </summary>
        public Dictionary<string, int> GetTotalStats()
        {
            var totalStats = new Dictionary<string, int>();
            
            foreach (var item in EquippedItems.Values)
            {
                foreach (var stat in item.Stats)
                {
                    if (totalStats.ContainsKey(stat.Key))
                    {
                        totalStats[stat.Key] += item.GetStatValue(stat.Key);
                    }
                    else
                    {
                        totalStats[stat.Key] = item.GetStatValue(stat.Key);
                    }
                }
            }
            
            return totalStats;
        }
    }

    /// <summary>
    /// Equipment system state
    /// </summary>
    [Serializable]
    public class EquipmentSystemState
    {
        public List<Inventory> Inventories { get; set; } = new List<Inventory>();
        public List<Equipment> GlobalItems { get; set; } = new List<Equipment>();
        public Dictionary<string, EquipmentProperty> AvailableProperties { get; set; } = new Dictionary<string, EquipmentProperty>();
        public List<EquipmentEvent> RecentEvents { get; set; } = new List<EquipmentEvent>();
        public DateTime LastUpdated { get; set; }
        
        public EquipmentSystemState()
        {
            LastUpdated = DateTime.UtcNow;
        }

        public void AddEvent(EquipmentEvent equipmentEvent)
        {
            RecentEvents.Add(equipmentEvent);
            LastUpdated = DateTime.UtcNow;
            
            // Keep only recent events
            if (RecentEvents.Count > 100)
            {
                RecentEvents.RemoveAt(0);
            }
        }
    }

    /// <summary>
    /// Equipment events for tracking equipment actions
    /// </summary>
    [Serializable]
    public class EquipmentEvent
    {
        public string EventId { get; set; }
        public EquipmentEventType EventType { get; set; }
        public string PlayerId { get; set; }
        public string ItemId { get; set; }
        public string ItemName { get; set; }
        public Dictionary<string, object> EventData { get; set; } = new Dictionary<string, object>();
        public DateTime Timestamp { get; set; }
        
        public EquipmentEvent()
        {
            EventId = Guid.NewGuid().ToString();
            Timestamp = DateTime.UtcNow;
        }
    }

    /// <summary>
    /// Types of equipment events
    /// </summary>
    public enum EquipmentEventType
    {
        ItemEquipped,
        ItemUnequipped,
        ItemDestroyed,
        ItemRepaired,
        ItemEvolved,
        ItemCreated,
        ItemDropped,
        ItemPickedUp,
        ItemIdentified,
        PropertyActivated,
        PropertyDeactivated
    }

    /// <summary>
    /// Equipment action result
    /// </summary>
    [Serializable]
    public class EquipmentActionResult
    {
        public bool Success { get; set; }
        public string Message { get; set; }
        public Equipment Equipment { get; set; }
        public Dictionary<string, object> Data { get; set; } = new Dictionary<string, object>();
    }
} 