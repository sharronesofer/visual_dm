using System;
using System.Collections.Generic;
using UnityEngine;
using Newtonsoft.Json;

namespace VDM.Systems.Loot.Models
{
    /// <summary>
    /// Model representing a shop and its properties
    /// </summary>
    [Serializable]
    public class Shop
    {
        [JsonProperty("id")]
        public string Id { get; set; }
        
        [JsonProperty("name")]
        public string Name { get; set; }
        
        [JsonProperty("type")]
        public string Type { get; set; } = "general_store";
        
        [JsonProperty("tier")]
        public int Tier { get; set; } = 1;
        
        [JsonProperty("location_id")]
        public int? LocationId { get; set; }
        
        [JsonProperty("region_id")]
        public int? RegionId { get; set; }
        
        [JsonProperty("faction_id")]
        public int? FactionId { get; set; }
        
        [JsonProperty("specialty")]
        public string Specialty { get; set; }
        
        [JsonProperty("description")]
        public string Description { get; set; }
        
        [JsonProperty("keeper_name")]
        public string KeeperName { get; set; }
        
        [JsonProperty("reputation")]
        public int Reputation { get; set; } = 0;
        
        [JsonProperty("relationship")]
        public string Relationship { get; set; } = "neutral";
        
        [JsonProperty("is_open")]
        public bool IsOpen { get; set; } = true;
        
        [JsonProperty("inventory")]
        public List<ShopItem> Inventory { get; set; } = new List<ShopItem>();
        
        [JsonProperty("last_restock")]
        public DateTime LastRestock { get; set; } = DateTime.UtcNow;
        
        [JsonProperty("economic_modifiers")]
        public Dictionary<string, float> EconomicModifiers { get; set; } = new Dictionary<string, float>();
        
        [JsonProperty("metadata")]
        public Dictionary<string, object> Metadata { get; set; } = new Dictionary<string, object>();
        
        /// <summary>
        /// Get the shop's specialization modifier for a given item type
        /// </summary>
        public float GetSpecializationModifier(string itemType)
        {
            // Shop type specialization bonuses
            var typeModifiers = Type?.ToLower() switch
            {
                "weapon_smith" when itemType?.ToLower().Contains("weapon") == true => 0.8f,
                "armor_crafter" when itemType?.ToLower().Contains("armor") == true => 0.8f,
                "magic_shop" when itemType?.ToLower().Contains("magic") == true => 0.9f,
                "alchemist" when itemType?.ToLower().Contains("potion") == true => 0.85f,
                "black_market" => 1.2f, // Higher prices but rare items
                "general_store" => 1.0f,
                _ => 1.0f
            };
            
            return typeModifiers;
        }
        
        /// <summary>
        /// Get the reputation modifier for pricing
        /// </summary>
        public float GetReputationModifier()
        {
            return Relationship?.ToLower() switch
            {
                "hostile" => 1.5f,
                "unfriendly" => 1.2f,
                "neutral" => 1.0f,
                "friendly" => 0.9f,
                "allied" => 0.8f,
                _ => 1.0f
            };
        }
    }
    
    /// <summary>
    /// Model representing an item in a shop's inventory
    /// </summary>
    [Serializable]
    public class ShopItem
    {
        [JsonProperty("item")]
        public LootItem Item { get; set; }
        
        [JsonProperty("price")]
        public float Price { get; set; }
        
        [JsonProperty("base_price")]
        public float BasePrice { get; set; }
        
        [JsonProperty("quantity")]
        public int Quantity { get; set; } = 1;
        
        [JsonProperty("max_quantity")]
        public int MaxQuantity { get; set; } = 1;
        
        [JsonProperty("restock_rate")]
        public float RestockRate { get; set; } = 0.1f; // Chance to restock per day
        
        [JsonProperty("discount")]
        public float Discount { get; set; } = 0f;
        
        [JsonProperty("markup")]
        public float Markup { get; set; } = 0f;
        
        [JsonProperty("is_featured")]
        public bool IsFeatured { get; set; } = false;
        
        [JsonProperty("is_limited")]
        public bool IsLimited { get; set; } = false;
        
        [JsonProperty("added_at")]
        public DateTime AddedAt { get; set; } = DateTime.UtcNow;
        
        [JsonProperty("last_sold")]
        public DateTime? LastSold { get; set; }
        
        [JsonProperty("times_sold")]
        public int TimesSold { get; set; } = 0;
        
        /// <summary>
        /// Get the final adjusted price considering all modifiers
        /// </summary>
        public float GetFinalPrice(Shop shop = null)
        {
            float finalPrice = Price;
            
            // Apply discount
            if (Discount > 0)
            {
                finalPrice *= (1f - Discount);
            }
            
            // Apply markup
            if (Markup > 0)
            {
                finalPrice *= (1f + Markup);
            }
            
            // Apply shop modifiers if shop is provided
            if (shop != null)
            {
                finalPrice *= shop.GetSpecializationModifier(Item?.Type);
                finalPrice *= shop.GetReputationModifier();
            }
            
            return Mathf.Max(1f, finalPrice); // Minimum price of 1
        }
        
        /// <summary>
        /// Check if the item is available for purchase
        /// </summary>
        public bool IsAvailable()
        {
            return Quantity > 0;
        }
    }
    
    /// <summary>
    /// Model for shop transactions
    /// </summary>
    [Serializable]
    public class ShopTransaction
    {
        [JsonProperty("transaction_id")]
        public string TransactionId { get; set; }
        
        [JsonProperty("shop_id")]
        public string ShopId { get; set; }
        
        [JsonProperty("player_id")]
        public string PlayerId { get; set; }
        
        [JsonProperty("item_id")]
        public string ItemId { get; set; }
        
        [JsonProperty("transaction_type")]
        public TransactionType Type { get; set; } = TransactionType.Purchase;
        
        [JsonProperty("quantity")]
        public int Quantity { get; set; } = 1;
        
        [JsonProperty("price")]
        public float Price { get; set; }
        
        [JsonProperty("base_price")]
        public float BasePrice { get; set; }
        
        [JsonProperty("final_price")]
        public float FinalPrice { get; set; }
        
        [JsonProperty("shop_modifier")]
        public float ShopModifier { get; set; } = 1.0f;
        
        [JsonProperty("reputation_modifier")]
        public float ReputationModifier { get; set; } = 1.0f;
        
        [JsonProperty("economic_modifier")]
        public float EconomicModifier { get; set; } = 1.0f;
        
        [JsonProperty("bulk_discount")]
        public float BulkDiscount { get; set; } = 0f;
        
        [JsonProperty("transaction_successful")]
        public bool TransactionSuccessful { get; set; } = true;
        
        [JsonProperty("failure_reason")]
        public string FailureReason { get; set; }
        
        [JsonProperty("reputation_change")]
        public int ReputationChange { get; set; } = 0;
        
        [JsonProperty("timestamp")]
        public DateTime Timestamp { get; set; } = DateTime.UtcNow;
        
        [JsonProperty("metadata")]
        public Dictionary<string, object> Metadata { get; set; } = new Dictionary<string, object>();
        
        public ShopTransaction()
        {
            TransactionId = Guid.NewGuid().ToString();
        }
    }
    
    /// <summary>
    /// Enumeration of transaction types
    /// </summary>
    public enum TransactionType
    {
        Purchase,
        Sale,
        Trade,
        Refund
    }
    
    /// <summary>
    /// Model for loot generation requests
    /// </summary>
    [Serializable]
    public class LootGenerationRequest
    {
        [JsonProperty("monster_levels")]
        public List<int> MonsterLevels { get; set; } = new List<int>();
        
        [JsonProperty("location_id")]
        public int? LocationId { get; set; }
        
        [JsonProperty("region_id")]
        public int? RegionId { get; set; }
        
        [JsonProperty("biome_type")]
        public string BiomeType { get; set; }
        
        [JsonProperty("faction_id")]
        public int? FactionId { get; set; }
        
        [JsonProperty("faction_type")]
        public string FactionType { get; set; }
        
        [JsonProperty("motif")]
        public string Motif { get; set; }
        
        [JsonProperty("source_type")]
        public string SourceType { get; set; } = "combat";
        
        [JsonProperty("quest_related")]
        public bool QuestRelated { get; set; } = false;
        
        [JsonProperty("force_magical")]
        public bool ForceMagical { get; set; } = false;
        
        [JsonProperty("rarity_bias")]
        public string RarityBias { get; set; }
    }
    
    /// <summary>
    /// Model for item identification requests
    /// </summary>
    [Serializable]
    public class ItemIdentificationRequest
    {
        [JsonProperty("item")]
        public LootItem Item { get; set; }
        
        [JsonProperty("character_id")]
        public int CharacterId { get; set; }
        
        [JsonProperty("skill_level")]
        public int SkillLevel { get; set; } = 0;
        
        [JsonProperty("use_magic")]
        public bool UseMagic { get; set; } = false;
        
        [JsonProperty("spellcraft_bonus")]
        public int SpellcraftBonus { get; set; } = 0;
        
        [JsonProperty("method")]
        public string Method { get; set; } = "skill";
    }
    
    /// <summary>
    /// Model for item enhancement requests
    /// </summary>
    [Serializable]
    public class ItemEnhancementRequest
    {
        [JsonProperty("item")]
        public LootItem Item { get; set; }
        
        [JsonProperty("character_id")]
        public int CharacterId { get; set; }
        
        [JsonProperty("enhancement_type")]
        public string EnhancementType { get; set; } = "enchantment";
        
        [JsonProperty("craft_skill_used")]
        public string CraftSkillUsed { get; set; } = "crafting";
        
        [JsonProperty("character_craft_skill")]
        public int CharacterCraftSkill { get; set; } = 0;
        
        [JsonProperty("tool_quality")]
        public int ToolQuality { get; set; } = 1;
        
        [JsonProperty("material_quality")]
        public int MaterialQuality { get; set; } = 1;
        
        [JsonProperty("special_ingredients")]
        public List<string> SpecialIngredients { get; set; } = new List<string>();
        
        [JsonProperty("force_success")]
        public bool ForceSuccess { get; set; } = false;
        
        [JsonProperty("risk_level")]
        public string RiskLevel { get; set; } = "low";
    }
} 