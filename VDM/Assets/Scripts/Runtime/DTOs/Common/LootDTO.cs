using System;
using System.Collections.Generic;
using VDM.DTOs.Core.Shared;

namespace VDM.DTOs.Economic.Loot
{
    /// <summary>
    /// Base DTO for loot system with common fields
    /// </summary>
    [Serializable]
    public abstract class LootBaseDTO : MetadataDTO
    {
        public bool IsActive { get; set; } = true;
    }

    /// <summary>
    /// Primary DTO for loot system
    /// </summary>
    [Serializable]
    public class LootDTO : LootBaseDTO
    {
        public string Name { get; set; } = string.Empty;
        public string Description { get; set; }
        public string Status { get; set; } = "active";
        public Dictionary<string, object> Properties { get; set; } = new Dictionary<string, object>();
    }

    /// <summary>
    /// Request DTO for creating loot
    /// </summary>
    [Serializable]
    public class CreateLootDTO
    {
        public string Name { get; set; } = string.Empty;
        public string Description { get; set; }
        public Dictionary<string, object> Properties { get; set; } = new Dictionary<string, object>();
    }

    /// <summary>
    /// Request DTO for updating loot
    /// </summary>
    [Serializable]
    public class UpdateLootDTO
    {
        public string Name { get; set; }
        public string Description { get; set; }
        public string Status { get; set; }
        public Dictionary<string, object> Properties { get; set; }
    }

    /// <summary>
    /// Response DTO for loot
    /// </summary>
    [Serializable]
    public class LootResponseDTO : SuccessResponseDTO
    {
        public LootDTO Loot { get; set; } = new LootDTO();
    }

    /// <summary>
    /// Response DTO for loot lists
    /// </summary>
    [Serializable]
    public class LootListResponseDTO : SuccessResponseDTO
    {
        public List<LootDTO> Loots { get; set; } = new List<LootDTO>();
        public int Total { get; set; }
        public int Page { get; set; }
        public int Size { get; set; }
        public bool HasNext { get; set; }
        public bool HasPrev { get; set; }
    }

    /// <summary>
    /// Loot item DTO for individual items in loot bundles
    /// </summary>
    [Serializable]
    public class LootItemDTO : LootBaseDTO
    {
        public string ItemId { get; set; } = string.Empty;
        public string ItemName { get; set; } = string.Empty;
        public string ItemType { get; set; } = string.Empty;
        public string Rarity { get; set; } = "common";
        public int Quantity { get; set; } = 1;
        public float Value { get; set; }
        public bool IsMagical { get; set; }
        public bool IsQuestItem { get; set; }
        public Dictionary<string, object> ItemProperties { get; set; } = new Dictionary<string, object>();
        public Dictionary<string, object> Appearance { get; set; } = new Dictionary<string, object>();
    }

    /// <summary>
    /// Loot bundle DTO for complete loot generation results
    /// </summary>
    [Serializable]
    public class LootBundleDTO : LootBaseDTO
    {
        public string BundleId { get; set; } = string.Empty;
        public int Gold { get; set; }
        public List<LootItemDTO> Equipment { get; set; } = new List<LootItemDTO>();
        public LootItemDTO QuestItem { get; set; }
        public LootItemDTO MagicalItem { get; set; }
        public string SourceType { get; set; } = "combat";
        public string LocationId { get; set; }
        public string RegionId { get; set; }
        public List<int> MonsterLevels { get; set; } = new List<int>();
        public DateTime GeneratedAt { get; set; } = DateTime.UtcNow;
    }

    /// <summary>
    /// Loot generation request DTO
    /// </summary>
    [Serializable]
    public class LootGenerationRequestDTO
    {
        public List<int> MonsterLevels { get; set; } = new List<int>();
        public string SourceType { get; set; } = "combat";
        public string LocationId { get; set; }
        public string RegionId { get; set; }
        public string FactionId { get; set; }
        public string Motif { get; set; }
        public Dictionary<string, object> Parameters { get; set; } = new Dictionary<string, object>();
    }

    /// <summary>
    /// Loot generation response DTO
    /// </summary>
    [Serializable]
    public class LootGenerationResponseDTO : SuccessResponseDTO
    {
        public LootBundleDTO LootBundle { get; set; } = new LootBundleDTO();
    }

    /// <summary>
    /// Drop table entry DTO for loot configuration
    /// </summary>
    [Serializable]
    public class DropTableEntryDTO : LootBaseDTO
    {
        public string EntryId { get; set; } = string.Empty;
        public string ItemId { get; set; } = string.Empty;
        public string ItemType { get; set; } = string.Empty;
        public float DropChance { get; set; }
        public int MinQuantity { get; set; } = 1;
        public int MaxQuantity { get; set; } = 1;
        public int MinLevel { get; set; } = 1;
        public int MaxLevel { get; set; } = 100;
        public List<string> Conditions { get; set; } = new List<string>();
        public Dictionary<string, object> Modifiers { get; set; } = new Dictionary<string, object>();
    }

    /// <summary>
    /// Drop table DTO for loot table configuration
    /// </summary>
    [Serializable]
    public class DropTableDTO : LootBaseDTO
    {
        public string TableId { get; set; } = string.Empty;
        public string TableName { get; set; } = string.Empty;
        public string TableType { get; set; } = "monster";
        public List<DropTableEntryDTO> Entries { get; set; } = new List<DropTableEntryDTO>();
        public int MinItems { get; set; } = 0;
        public int MaxItems { get; set; } = 5;
        public float GoldMultiplier { get; set; } = 1.0f;
        public Dictionary<string, object> TableModifiers { get; set; } = new Dictionary<string, object>();
    }

    /// <summary>
    /// Loot history entry DTO for tracking loot generation
    /// </summary>
    [Serializable]
    public class LootHistoryDTO : LootBaseDTO
    {
        public string HistoryId { get; set; } = string.Empty;
        public string PlayerId { get; set; } = string.Empty;
        public string SourceType { get; set; } = string.Empty;
        public string SourceId { get; set; } = string.Empty;
        public LootBundleDTO GeneratedLoot { get; set; } = new LootBundleDTO();
        public DateTime GeneratedAt { get; set; } = DateTime.UtcNow;
        public string LocationId { get; set; }
        public string RegionId { get; set; }
        public Dictionary<string, object> Context { get; set; } = new Dictionary<string, object>();
    }

    /// <summary>
    /// Loot analytics DTO for tracking loot statistics
    /// </summary>
    [Serializable]
    public class LootAnalyticsDTO : LootBaseDTO
    {
        public string AnalyticsId { get; set; } = string.Empty;
        public string MetricType { get; set; } = string.Empty;
        public float Value { get; set; }
        public string Period { get; set; } = "daily";
        public DateTime PeriodStart { get; set; } = DateTime.UtcNow;
        public DateTime PeriodEnd { get; set; } = DateTime.UtcNow;
        public Dictionary<string, object> Breakdown { get; set; } = new Dictionary<string, object>();
    }
} 