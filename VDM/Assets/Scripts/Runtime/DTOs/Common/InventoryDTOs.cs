using System;
using System.Collections.Generic;
using UnityEngine;

namespace VDM.DTOs.Inventory
{
    [Serializable]
    public class InventoryDTO
    {
        public string id;
        public string characterId;
        public List<InventoryItemDTO> items;
        public int maxCapacity;
        public int currentWeight;
        public int maxWeight;
        public DateTime lastUpdated;
        
        public InventoryDTO()
        {
            items = new List<InventoryItemDTO>();
        }
    }

    [Serializable]
    public class ItemDTO
    {
        public string id;
        public string name;
        public string description;
        public string category;
        public string rarity;
        public int value;
        public int weight;
        public bool isStackable;
        public int maxStackSize;
        public Dictionary<string, object> properties;
        
        public ItemDTO()
        {
            properties = new Dictionary<string, object>();
        }
    }

    [Serializable]
    public class InventoryItemDTO
    {
        public string inventoryId;
        public string itemId;
        public ItemDTO item;
        public int quantity;
        public int slotIndex;
        public bool isEquipped;
        public DateTime acquiredAt;
    }

    [Serializable]
    public class ItemCategoryDTO
    {
        public string id;
        public string name;
        public string description;
        public string parentCategory;
        public List<string> allowedProperties;
        
        public ItemCategoryDTO()
        {
            allowedProperties = new List<string>();
        }
    }

    [Serializable]
    public class CreateInventoryRequestDTO
    {
        public string characterId;
        public int maxCapacity;
        public int maxWeight;
    }

    [Serializable]
    public class CreateItemRequestDTO
    {
        public string name;
        public string description;
        public string category;
        public string rarity;
        public int value;
        public int weight;
        public bool isStackable;
        public int maxStackSize;
        public Dictionary<string, object> properties;
        
        public CreateItemRequestDTO()
        {
            properties = new Dictionary<string, object>();
        }
    }

    [Serializable]
    public class AddInventoryItemRequestDTO
    {
        public string itemId;
        public int quantity;
        public int slotIndex;
    }

    [Serializable]
    public class InventoryTransferRequestDTO
    {
        public string fromInventoryId;
        public string toInventoryId;
        public string itemId;
        public int quantity;
    }

    [Serializable]
    public class InventoryStatsDTO
    {
        public int totalItems;
        public int totalWeight;
        public int totalValue;
        public float capacityUsed;
        public float weightUsed;
        public Dictionary<string, int> itemsByCategory;
        
        public InventoryStatsDTO()
        {
            itemsByCategory = new Dictionary<string, int>();
        }
    }
} 