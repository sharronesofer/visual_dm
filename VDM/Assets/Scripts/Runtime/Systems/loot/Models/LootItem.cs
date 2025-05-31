using System;
using System.Collections.Generic;
using UnityEngine;
using Newtonsoft.Json;

namespace VDM.Systems.Loot.Models
{
    /// <summary>
    /// Model representing a loot item in the game.
    /// Mirrors the backend loot item structure for API communication.
    /// </summary>
    [Serializable]
    public class LootItem
    {
        [JsonProperty("id")]
        public string Id { get; set; }
        
        [JsonProperty("name")]
        public string Name { get; set; }
        
        [JsonProperty("description")]
        public string Description { get; set; }
        
        [JsonProperty("rarity")]
        public string Rarity { get; set; } = "common";
        
        [JsonProperty("level")]
        public int Level { get; set; } = 1;
        
        [JsonProperty("category")]
        public string Category { get; set; }
        
        [JsonProperty("type")]
        public string Type { get; set; }
        
        [JsonProperty("slot")]
        public string Slot { get; set; }
        
        [JsonProperty("value")]
        public float Value { get; set; }
        
        [JsonProperty("properties")]
        public Dictionary<string, object> Properties { get; set; } = new Dictionary<string, object>();
        
        [JsonProperty("stats")]
        public Dictionary<string, float> Stats { get; set; } = new Dictionary<string, float>();
        
        [JsonProperty("effects")]
        public List<ItemEffect> Effects { get; set; } = new List<ItemEffect>();
        
        [JsonProperty("enchantments")]
        public List<ItemEnhancement> Enchantments { get; set; } = new List<ItemEnhancement>();
        
        [JsonProperty("unknown_effects")]
        public List<string> UnknownEffects { get; set; } = new List<string>();
        
        [JsonProperty("revealed_effects")]
        public List<string> RevealedEffects { get; set; } = new List<string>();
        
        [JsonProperty("name_revealed")]
        public bool NameRevealed { get; set; } = true;
        
        [JsonProperty("identified_name")]
        public string IdentifiedName { get; set; }
        
        [JsonProperty("is_magical")]
        public bool IsMagical { get; set; } = false;
        
        [JsonProperty("is_cursed")]
        public bool IsCursed { get; set; } = false;
        
        [JsonProperty("durability")]
        public float Durability { get; set; } = 100f;
        
        [JsonProperty("max_durability")]
        public float MaxDurability { get; set; } = 100f;
        
        [JsonProperty("weight")]
        public float Weight { get; set; } = 1f;
        
        [JsonProperty("created_at")]
        public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
        
        [JsonProperty("metadata")]
        public Dictionary<string, object> Metadata { get; set; } = new Dictionary<string, object>();
        
        /// <summary>
        /// Constructor for creating a new loot item
        /// </summary>
        public LootItem()
        {
            Id = Guid.NewGuid().ToString();
            CreatedAt = DateTime.UtcNow;
        }
        
        /// <summary>
        /// Get the display name for the item (considers identification state)
        /// </summary>
        public string GetDisplayName()
        {
            if (!NameRevealed)
                return "Unidentified Item";
            
            return !string.IsNullOrEmpty(IdentifiedName) ? IdentifiedName : Name;
        }
        
        /// <summary>
        /// Get the effective description (considers identification state)
        /// </summary>
        public string GetDisplayDescription()
        {
            if (!NameRevealed)
                return "This item's true nature is unknown. It must be identified to reveal its properties.";
            
            return Description;
        }
        
        /// <summary>
        /// Check if the item needs identification
        /// </summary>
        public bool NeedsIdentification()
        {
            return !NameRevealed || UnknownEffects.Count > 0;
        }
        
        /// <summary>
        /// Get the rarity color for UI display
        /// </summary>
        public Color GetRarityColor()
        {
            return Rarity?.ToLower() switch
            {
                "common" => Color.gray,
                "uncommon" => Color.green,
                "rare" => Color.blue,
                "epic" => new Color(0.5f, 0f, 1f), // Purple
                "legendary" => new Color(1f, 0.5f, 0f), // Orange
                _ => Color.white
            };
        }
        
        /// <summary>
        /// Calculate the total power score of the item
        /// </summary>
        public float CalculatePowerScore()
        {
            float powerScore = 0f;
            
            // Base stats contribution
            foreach (var stat in Stats.Values)
            {
                powerScore += stat;
            }
            
            // Effects contribution
            powerScore += Effects.Count * 10f;
            
            // Enchantments contribution
            powerScore += Enchantments.Count * 15f;
            
            // Level multiplier
            powerScore *= (1f + Level * 0.1f);
            
            // Rarity multiplier
            float rarityMultiplier = Rarity?.ToLower() switch
            {
                "common" => 1f,
                "uncommon" => 1.5f,
                "rare" => 2.5f,
                "epic" => 4f,
                "legendary" => 6f,
                _ => 1f
            };
            
            return powerScore * rarityMultiplier;
        }
        
        /// <summary>
        /// Get item value adjusted for condition and other factors
        /// </summary>
        public float GetAdjustedValue()
        {
            float adjustedValue = Value;
            
            // Durability factor
            if (MaxDurability > 0)
            {
                adjustedValue *= (Durability / MaxDurability);
            }
            
            // Cursed items have reduced value
            if (IsCursed)
            {
                adjustedValue *= 0.3f;
            }
            
            return adjustedValue;
        }
        
        /// <summary>
        /// Clone this item (for duplication, modification, etc.)
        /// </summary>
        public LootItem Clone()
        {
            var json = JsonConvert.SerializeObject(this);
            var clone = JsonConvert.DeserializeObject<LootItem>(json);
            clone.Id = Guid.NewGuid().ToString(); // New unique ID
            return clone;
        }
    }
    
    /// <summary>
    /// Model for item effects
    /// </summary>
    [Serializable]
    public class ItemEffect
    {
        [JsonProperty("name")]
        public string Name { get; set; }
        
        [JsonProperty("description")]
        public string Description { get; set; }
        
        [JsonProperty("type")]
        public string Type { get; set; }
        
        [JsonProperty("value")]
        public float Value { get; set; }
        
        [JsonProperty("duration")]
        public float Duration { get; set; } = -1f; // -1 for permanent
        
        [JsonProperty("trigger")]
        public string Trigger { get; set; } = "passive";
        
        [JsonProperty("metadata")]
        public Dictionary<string, object> Metadata { get; set; } = new Dictionary<string, object>();
    }
    
    /// <summary>
    /// Model for item enhancements/enchantments
    /// </summary>
    [Serializable]
    public class ItemEnhancement
    {
        [JsonProperty("type")]
        public string Type { get; set; }
        
        [JsonProperty("value")]
        public float Value { get; set; }
        
        [JsonProperty("applied_at")]
        public DateTime AppliedAt { get; set; } = DateTime.UtcNow;
        
        [JsonProperty("applied_by")]
        public string AppliedBy { get; set; }
        
        [JsonProperty("enhancement_level")]
        public int EnhancementLevel { get; set; } = 1;
        
        [JsonProperty("metadata")]
        public Dictionary<string, object> Metadata { get; set; } = new Dictionary<string, object>();
    }
} 