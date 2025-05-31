using System;
using System.Collections.Generic;
using VDM.DTOs.Core.Shared;

namespace VDM.DTOs.Economic.Inventory
{
    /// <summary>
    /// Item category enumeration
    /// </summary>
    public enum ItemCategoryDTO
    {
        Weapon,
        Armor,
        Shield,
        Consumable,
        Tool,
        Misc,
        Quest,
        Valuable,
        Container,
        Ammunition
    }

    /// <summary>
    /// Item model for the inventory system
    /// </summary>
    [Serializable]
    public class ItemDTO : MetadataDTO
    {
        public string Id { get; set; } = string.Empty;
        public string Name { get; set; } = string.Empty;
        public string Description { get; set; }
        public float Weight { get; set; } = 0.0f;
        public int Value { get; set; } = 0;
        public bool Stackable { get; set; } = false;
        public int MaxStack { get; set; } = 1;
        public ItemCategoryDTO Category { get; set; } = ItemCategoryDTO.Misc;
        public string EquipmentSlot { get; set; } // e.g., "main_hand", "chest", "head"
        public bool CanBeEquipped { get; set; } = false;
        public bool ApplyWeightWhenEquipped { get; set; } = true;
        public Dictionary<string, object> Properties { get; set; } = new Dictionary<string, object>();
    }

    /// <summary>
    /// Inventory item representing an item instance in an inventory
    /// </summary>
    [Serializable]
    public class InventoryItemDTO : MetadataDTO
    {
        public string Id { get; set; } = string.Empty;
        public string InventoryId { get; set; } = string.Empty;
        public string ItemId { get; set; } = string.Empty;
        public int Quantity { get; set; } = 1;
        public int? SlotPosition { get; set; }
        public bool Equipped { get; set; } = false;
        public float Condition { get; set; } = 1.0f; // 0.0 = broken, 1.0 = perfect
        public Dictionary<string, object> Properties { get; set; } = new Dictionary<string, object>();

        // Navigation property for the item details
        public ItemDTO Item { get; set; }
    }

    /// <summary>
    /// Inventory container model
    /// </summary>
    [Serializable]
    public class InventoryDTO : MetadataDTO
    {
        public string Id { get; set; } = string.Empty;
        public string OwnerId { get; set; } = string.Empty;
        public string OwnerType { get; set; } = "character"; // 'character', 'npc', 'container'
        public string Name { get; set; }
        public int MaxSlots { get; set; } = 20;
        public float MaxWeight { get; set; } = 100.0f;
        public float CurrentWeight { get; set; } = 0.0f;
        public Dictionary<string, object> Properties { get; set; } = new Dictionary<string, object>();
        public List<InventoryItemDTO> Items { get; set; } = new List<InventoryItemDTO>();
    }

    /// <summary>
    /// Inventory statistics
    /// </summary>
    [Serializable]
    public class InventoryStatsDTO
    {
        public int TotalItems { get; set; } = 0;
        public float TotalWeight { get; set; } = 0.0f;
        public int TotalValue { get; set; } = 0;
        public int SlotsUsed { get; set; } = 0;
        public int SlotsAvailable { get; set; } = 0;
        public float WeightCapacityUsed { get; set; } = 0.0f;
        public Dictionary<string, int> ItemsByCategory { get; set; } = new Dictionary<string, int>();
    }

    /// <summary>
    /// Detailed inventory response with statistics
    /// </summary>
    [Serializable]
    public class InventoryDetailResponseDTO
    {
        public InventoryDTO Inventory { get; set; } = new InventoryDTO();
        public InventoryStatsDTO Stats { get; set; } = new InventoryStatsDTO();
    }

    // ================ Request DTOs ================

    /// <summary>
    /// Request to create a new item
    /// </summary>
    [Serializable]
    public class CreateItemRequestDTO
    {
        public string Name { get; set; } = string.Empty;
        public string Description { get; set; }
        public float Weight { get; set; } = 0.0f;
        public int Value { get; set; } = 0;
        public bool Stackable { get; set; } = false;
        public int MaxStack { get; set; } = 1;
        public ItemCategoryDTO Category { get; set; } = ItemCategoryDTO.Misc;
        public string EquipmentSlot { get; set; }
        public bool CanBeEquipped { get; set; } = false;
        public bool ApplyWeightWhenEquipped { get; set; } = true;
        public Dictionary<string, object> Properties { get; set; }
    }

    /// <summary>
    /// Request to update an item
    /// </summary>
    [Serializable]
    public class UpdateItemRequestDTO
    {
        public string Name { get; set; }
        public string Description { get; set; }
        public float? Weight { get; set; }
        public int? Value { get; set; }
        public bool? Stackable { get; set; }
        public int? MaxStack { get; set; }
        public ItemCategoryDTO? Category { get; set; }
        public string EquipmentSlot { get; set; }
        public bool? CanBeEquipped { get; set; }
        public bool? ApplyWeightWhenEquipped { get; set; }
        public Dictionary<string, object> Properties { get; set; }
    }

    /// <summary>
    /// Request to create an inventory
    /// </summary>
    [Serializable]
    public class CreateInventoryRequestDTO
    {
        public string OwnerId { get; set; } = string.Empty;
        public string OwnerType { get; set; } = "character";
        public string Name { get; set; }
        public int MaxSlots { get; set; } = 20;
        public float MaxWeight { get; set; } = 100.0f;
        public Dictionary<string, object> Properties { get; set; }
    }

    /// <summary>
    /// Request to add an item to an inventory
    /// </summary>
    [Serializable]
    public class AddInventoryItemRequestDTO
    {
        public string ItemId { get; set; } = string.Empty;
        public int Quantity { get; set; } = 1;
        public int? SlotPosition { get; set; }
        public Dictionary<string, object> Properties { get; set; }
    }

    /// <summary>
    /// Request to transfer items between inventories
    /// </summary>
    [Serializable]
    public class InventoryTransferRequestDTO
    {
        public string SourceInventoryId { get; set; } = string.Empty;
        public string TargetInventoryId { get; set; } = string.Empty;
        public string InventoryItemId { get; set; } = string.Empty;
        public int Quantity { get; set; } = 1;
        public int? TargetSlotPosition { get; set; }
    }

    /// <summary>
    /// Request to equip/unequip an item
    /// </summary>
    [Serializable]
    public class EquipItemRequestDTO
    {
        public string InventoryItemId { get; set; } = string.Empty;
        public bool Equipped { get; set; } = true;
        public string EquipmentSlot { get; set; }
    }

    /// <summary>
    /// Bulk item transfer request
    /// </summary>
    [Serializable]
    public class BulkItemTransferRequestDTO
    {
        public string SourceInventoryId { get; set; } = string.Empty;
        public string TargetInventoryId { get; set; } = string.Empty;
        public List<InventoryTransferRequestDTO> Transfers { get; set; } = new List<InventoryTransferRequestDTO>();
    }

    /// <summary>
    /// Inventory filter parameters
    /// </summary>
    [Serializable]
    public class InventoryFilterParamsDTO
    {
        public ItemCategoryDTO? Category { get; set; }
        public bool? Equipped { get; set; }
        public int? MinValue { get; set; }
        public int? MaxValue { get; set; }
        public string SearchTerm { get; set; }
    }

    /// <summary>
    /// Validation result for inventory operations
    /// </summary>
    [Serializable]
    public class ValidationResultDTO
    {
        public bool Valid { get; set; } = true;
        public string ErrorMessage { get; set; }
        public Dictionary<string, object> Details { get; set; }
    }
} 