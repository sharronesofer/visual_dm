using System.Collections.Generic;
using System;
using UnityEngine;


namespace VDM.Systems.Inventory.Models
{
    /// <summary>
    /// Item category enumeration
    /// </summary>
    public enum ItemCategory
    {
        MISC,
        WEAPON,
        ARMOR,
        CONSUMABLE,
        TOOL,
        RESOURCE,
        QUEST_ITEM,
        VALUABLE,
        BOOK
    }

    /// <summary>
    /// Base item model representing any item in the game
    /// </summary>
    [Serializable]
    public class ItemData
    {
        public string id;
        public string name;
        public string description;
        public float weight;
        public int value;
        public bool stackable;
        public int maxStack;
        public ItemCategory category;
        public string equipmentSlot; // e.g., "main_hand", "chest", "head"
        public bool canBeEquipped;
        public bool applyWeightWhenEquipped;
        public Dictionary<string, object> properties;
        public DateTime createdAt;
        public DateTime updatedAt;

        public ItemData()
        {
            id = Guid.NewGuid().ToString();
            properties = new Dictionary<string, object>();
            weight = 0.0f;
            value = 0;
            stackable = false;
            maxStack = 1;
            category = ItemCategory.MISC;
            canBeEquipped = false;
            applyWeightWhenEquipped = true;
            createdAt = DateTime.UtcNow;
            updatedAt = DateTime.UtcNow;
        }
    }

    /// <summary>
    /// Inventory item model representing an item instance in an inventory
    /// </summary>
    [Serializable]
    public class InventoryItemData
    {
        public string id;
        public string inventoryId;
        public string itemId;
        public int quantity;
        public int slot;
        public bool isEquipped;
        public Dictionary<string, object> metadata;
        public DateTime createdAt;
        public DateTime updatedAt;

        // Reference to the item data (populated by services)
        public ItemData itemData;

        public InventoryItemData()
        {
            id = Guid.NewGuid().ToString();
            metadata = new Dictionary<string, object>();
            quantity = 1;
            slot = -1;
            isEquipped = false;
            createdAt = DateTime.UtcNow;
            updatedAt = DateTime.UtcNow;
        }
    }

    /// <summary>
    /// Inventory model representing a container for items
    /// </summary>
    [Serializable]
    public class InventoryData
    {
        public string id;
        public string ownerId;
        public string ownerType; // character, container, building, etc.
        public string name;
        public int maxSlots;
        public float maxWeight;
        public float currentWeight;
        public List<InventoryItemData> items;
        public Dictionary<string, object> metadata;
        public DateTime createdAt;
        public DateTime updatedAt;

        public InventoryData()
        {
            id = Guid.NewGuid().ToString();
            items = new List<InventoryItemData>();
            metadata = new Dictionary<string, object>();
            maxSlots = 20;
            maxWeight = 100.0f;
            currentWeight = 0.0f;
            createdAt = DateTime.UtcNow;
            updatedAt = DateTime.UtcNow;
        }
    }

    /// <summary>
    /// Inventory statistics model
    /// </summary>
    [Serializable]
    public class InventoryStatsData
    {
        public int totalItems;
        public int usedSlots;
        public int freeSlots;
        public float totalWeight;
        public float weightCapacity;
        public float weightPercentage;
        public int totalValue;
        public Dictionary<ItemCategory, int> itemsByCategory;

        public InventoryStatsData()
        {
            itemsByCategory = new Dictionary<ItemCategory, int>();
        }
    }

    /// <summary>
    /// Inventory transfer request model
    /// </summary>
    [Serializable]
    public class InventoryTransferRequest
    {
        public string fromInventoryId;
        public string toInventoryId;
        public string itemId;
        public int quantity;
        public int fromSlot;
        public int toSlot;
        public Dictionary<string, object> metadata;

        public InventoryTransferRequest()
        {
            metadata = new Dictionary<string, object>();
            fromSlot = -1;
            toSlot = -1;
        }
    }

    /// <summary>
    /// Add item to inventory request model
    /// </summary>
    [Serializable]
    public class AddInventoryItemRequest
    {
        public string inventoryId;
        public string itemId;
        public int quantity;
        public int slot;
        public Dictionary<string, object> metadata;

        public AddInventoryItemRequest()
        {
            metadata = new Dictionary<string, object>();
            quantity = 1;
            slot = -1;
        }
    }

    /// <summary>
    /// Remove item from inventory request model
    /// </summary>
    [Serializable]
    public class RemoveInventoryItemRequest
    {
        public string inventoryId;
        public string inventoryItemId;
        public int quantity;
        public Dictionary<string, object> metadata;

        public RemoveInventoryItemRequest()
        {
            metadata = new Dictionary<string, object>();
            quantity = 1;
        }
    }

    /// <summary>
    /// Inventory filter parameters for searching and filtering
    /// </summary>
    [Serializable]
    public class InventoryFilterParams
    {
        public string searchTerm;
        public ItemCategory? category;
        public bool? equipped;
        public float? minWeight;
        public float? maxWeight;
        public int? minValue;
        public int? maxValue;
        public string sortBy; // name, weight, value, category, etc.
        public bool sortAscending;

        public InventoryFilterParams()
        {
            sortBy = "name";
            sortAscending = true;
        }
    }

    /// <summary>
    /// Equipment slot data for managing equipped items
    /// </summary>
    [Serializable]
    public class EquipmentSlotData
    {
        public string slotName;
        public string equippedItemId;
        public bool isRequired;
        public List<ItemCategory> allowedCategories;
        public Dictionary<string, object> metadata;

        public EquipmentSlotData()
        {
            allowedCategories = new List<ItemCategory>();
            metadata = new Dictionary<string, object>();
        }
    }

    /// <summary>
    /// Character equipment model for managing equipped items
    /// </summary>
    [Serializable]
    public class CharacterEquipmentData
    {
        public string characterId;
        public Dictionary<string, EquipmentSlotData> equipmentSlots;
        public List<string> equippedItemIds;
        public DateTime updatedAt;

        public CharacterEquipmentData()
        {
            equipmentSlots = new Dictionary<string, EquipmentSlotData>();
            equippedItemIds = new List<string>();
            updatedAt = DateTime.UtcNow;
        }
    }

    /// <summary>
    /// Item stack helper for managing stackable items
    /// </summary>
    [Serializable]
    public class ItemStackData
    {
        public string itemId;
        public List<InventoryItemData> stacks;
        public int totalQuantity;
        public int availableStackSpace;

        public ItemStackData()
        {
            stacks = new List<InventoryItemData>();
        }
    }

    /// <summary>
    /// DTO alias for InventoryData to match API expectations
    /// </summary>
    [Serializable]
    public class InventoryDTO : InventoryData
    {
        public InventoryDTO() : base() { }
    }
} 