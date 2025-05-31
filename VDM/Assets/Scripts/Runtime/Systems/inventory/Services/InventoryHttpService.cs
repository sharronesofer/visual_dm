using Newtonsoft.Json;
using System.Collections.Generic;
using System.Threading.Tasks;
using System;
using UnityEngine;
using VDM.Infrastructure.Services;
using VDM.Systems.Inventory.Models;


namespace VDM.Systems.Inventory.Services
{
    /// <summary>
    /// HTTP service for Inventory system API communication
    /// </summary>
    public class InventoryHttpService : BaseHttpService
    {
        private const string INVENTORY_ENDPOINT = "/api/v1/inventory";
        private const string ITEMS_ENDPOINT = "/api/v1/inventory/items";
        private const string INVENTORIES_ENDPOINT = "/api/v1/inventory/inventories";
        private const string TRANSFER_ENDPOINT = "/api/v1/inventory/transfer";
        private const string EQUIPMENT_ENDPOINT = "/api/v1/inventory/equipment";

        public InventoryHttpService() : base() { }

        #region Inventory Operations

        /// <summary>
        /// Get inventory by ID
        /// </summary>
        public async Task<InventoryData> GetInventoryAsync(string inventoryId)
        {
            try
            {
                string response = await GetAsync($"{INVENTORIES_ENDPOINT}/{inventoryId}");
                return JsonConvert.DeserializeObject<InventoryData>(response);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error getting inventory {inventoryId}: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Get inventories by owner
        /// </summary>
        public async Task<List<InventoryData>> GetInventoriesByOwnerAsync(string ownerId, string ownerType = "character")
        {
            try
            {
                string response = await GetAsync($"{INVENTORIES_ENDPOINT}?owner_id={ownerId}&owner_type={ownerType}");
                return JsonConvert.DeserializeObject<List<InventoryData>>(response);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error getting inventories for owner {ownerId}: {ex.Message}");
                return new List<InventoryData>();
            }
        }

        /// <summary>
        /// Create a new inventory
        /// </summary>
        public async Task<InventoryData> CreateInventoryAsync(InventoryData inventoryData)
        {
            try
            {
                string json = JsonConvert.SerializeObject(inventoryData);
                string response = await PostAsync(INVENTORIES_ENDPOINT, json);
                return JsonConvert.DeserializeObject<InventoryData>(response);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error creating inventory: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Update inventory
        /// </summary>
        public async Task<InventoryData> UpdateInventoryAsync(string inventoryId, InventoryData inventoryData)
        {
            try
            {
                string json = JsonConvert.SerializeObject(inventoryData);
                string response = await PutAsync($"{INVENTORIES_ENDPOINT}/{inventoryId}", json);
                return JsonConvert.DeserializeObject<InventoryData>(response);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error updating inventory {inventoryId}: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Delete inventory
        /// </summary>
        public async Task<bool> DeleteInventoryAsync(string inventoryId)
        {
            try
            {
                await DeleteAsync($"{INVENTORIES_ENDPOINT}/{inventoryId}");
                return true;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error deleting inventory {inventoryId}: {ex.Message}");
                return false;
            }
        }

        #endregion

        #region Item Operations

        /// <summary>
        /// Get all items
        /// </summary>
        public async Task<List<ItemData>> GetItemsAsync()
        {
            try
            {
                string response = await GetAsync(ITEMS_ENDPOINT);
                return JsonConvert.DeserializeObject<List<ItemData>>(response);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error getting items: {ex.Message}");
                return new List<ItemData>();
            }
        }

        /// <summary>
        /// Get item by ID
        /// </summary>
        public async Task<ItemData> GetItemAsync(string itemId)
        {
            try
            {
                string response = await GetAsync($"{ITEMS_ENDPOINT}/{itemId}");
                return JsonConvert.DeserializeObject<ItemData>(response);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error getting item {itemId}: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Search items by criteria
        /// </summary>
        public async Task<List<ItemData>> SearchItemsAsync(InventoryFilterParams filterParams)
        {
            try
            {
                var queryParams = new List<string>();
                
                if (!string.IsNullOrEmpty(filterParams.searchTerm))
                    queryParams.Add($"search={Uri.EscapeDataString(filterParams.searchTerm)}");
                
                if (filterParams.category.HasValue)
                    queryParams.Add($"category={filterParams.category.Value}");
                
                if (filterParams.minValue.HasValue)
                    queryParams.Add($"min_value={filterParams.minValue.Value}");
                
                if (filterParams.maxValue.HasValue)
                    queryParams.Add($"max_value={filterParams.maxValue.Value}");
                
                if (filterParams.minWeight.HasValue)
                    queryParams.Add($"min_weight={filterParams.minWeight.Value}");
                
                if (filterParams.maxWeight.HasValue)
                    queryParams.Add($"max_weight={filterParams.maxWeight.Value}");

                string queryString = queryParams.Count > 0 ? "?" + string.Join("&", queryParams) : "";
                string response = await GetAsync($"{ITEMS_ENDPOINT}/search{queryString}");
                return JsonConvert.DeserializeObject<List<ItemData>>(response);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error searching items: {ex.Message}");
                return new List<ItemData>();
            }
        }

        /// <summary>
        /// Create a new item
        /// </summary>
        public async Task<ItemData> CreateItemAsync(ItemData itemData)
        {
            try
            {
                string json = JsonConvert.SerializeObject(itemData);
                string response = await PostAsync(ITEMS_ENDPOINT, json);
                return JsonConvert.DeserializeObject<ItemData>(response);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error creating item: {ex.Message}");
                return null;
            }
        }

        #endregion

        #region Inventory Item Operations

        /// <summary>
        /// Add item to inventory
        /// </summary>
        public async Task<InventoryItemData> AddItemToInventoryAsync(AddInventoryItemRequest request)
        {
            try
            {
                string json = JsonConvert.SerializeObject(request);
                string response = await PostAsync($"{INVENTORIES_ENDPOINT}/{request.inventoryId}/items", json);
                return JsonConvert.DeserializeObject<InventoryItemData>(response);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error adding item to inventory: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Remove item from inventory
        /// </summary>
        public async Task<bool> RemoveItemFromInventoryAsync(RemoveInventoryItemRequest request)
        {
            try
            {
                string json = JsonConvert.SerializeObject(request);
                await DeleteAsync($"{INVENTORIES_ENDPOINT}/{request.inventoryId}/items/{request.inventoryItemId}", json);
                return true;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error removing item from inventory: {ex.Message}");
                return false;
            }
        }

        /// <summary>
        /// Update inventory item (quantity, slot, etc.)
        /// </summary>
        public async Task<InventoryItemData> UpdateInventoryItemAsync(string inventoryId, string inventoryItemId, InventoryItemData itemData)
        {
            try
            {
                string json = JsonConvert.SerializeObject(itemData);
                string response = await PutAsync($"{INVENTORIES_ENDPOINT}/{inventoryId}/items/{inventoryItemId}", json);
                return JsonConvert.DeserializeObject<InventoryItemData>(response);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error updating inventory item: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Transfer item between inventories
        /// </summary>
        public async Task<bool> TransferItemAsync(InventoryTransferRequest request)
        {
            try
            {
                string json = JsonConvert.SerializeObject(request);
                await PostAsync(TRANSFER_ENDPOINT, json);
                return true;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error transferring item: {ex.Message}");
                return false;
            }
        }

        #endregion

        #region Equipment Operations

        /// <summary>
        /// Get character equipment
        /// </summary>
        public async Task<CharacterEquipmentData> GetCharacterEquipmentAsync(string characterId)
        {
            try
            {
                string response = await GetAsync($"{EQUIPMENT_ENDPOINT}/{characterId}");
                return JsonConvert.DeserializeObject<CharacterEquipmentData>(response);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error getting equipment for character {characterId}: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Equip item
        /// </summary>
        public async Task<bool> EquipItemAsync(string characterId, string inventoryItemId, string slot)
        {
            try
            {
                var request = new
                {
                    character_id = characterId,
                    inventory_item_id = inventoryItemId,
                    slot = slot
                };

                string json = JsonConvert.SerializeObject(request);
                await PostAsync($"{EQUIPMENT_ENDPOINT}/{characterId}/equip", json);
                return true;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error equipping item: {ex.Message}");
                return false;
            }
        }

        /// <summary>
        /// Unequip item
        /// </summary>
        public async Task<bool> UnequipItemAsync(string characterId, string slot)
        {
            try
            {
                var request = new
                {
                    character_id = characterId,
                    slot = slot
                };

                string json = JsonConvert.SerializeObject(request);
                await PostAsync($"{EQUIPMENT_ENDPOINT}/{characterId}/unequip", json);
                return true;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error unequipping item: {ex.Message}");
                return false;
            }
        }

        #endregion

        #region Statistics Operations

        /// <summary>
        /// Get inventory statistics
        /// </summary>
        public async Task<InventoryStatsData> GetInventoryStatsAsync(string inventoryId)
        {
            try
            {
                string response = await GetAsync($"{INVENTORIES_ENDPOINT}/{inventoryId}/stats");
                return JsonConvert.DeserializeObject<InventoryStatsData>(response);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error getting inventory stats for {inventoryId}: {ex.Message}");
                return null;
            }
        }

        #endregion

        #region Utility Operations

        /// <summary>
        /// Validate inventory operation (check weight, slots, etc.)
        /// </summary>
        public async Task<Dictionary<string, object>> ValidateInventoryOperationAsync(string inventoryId, string operation, Dictionary<string, object> parameters)
        {
            try
            {
                var request = new
                {
                    inventory_id = inventoryId,
                    operation = operation,
                    parameters = parameters
                };

                string json = JsonConvert.SerializeObject(request);
                string response = await PostAsync($"{INVENTORIES_ENDPOINT}/validate", json);
                return JsonConvert.DeserializeObject<Dictionary<string, object>>(response);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error validating inventory operation: {ex.Message}");
                return new Dictionary<string, object> { { "valid", false }, { "error", ex.Message } };
            }
        }

        /// <summary>
        /// Optimize inventory (auto-organize items)
        /// </summary>
        public async Task<InventoryData> OptimizeInventoryAsync(string inventoryId)
        {
            try
            {
                string response = await PostAsync($"{INVENTORIES_ENDPOINT}/{inventoryId}/optimize", "{}");
                return JsonConvert.DeserializeObject<InventoryData>(response);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error optimizing inventory {inventoryId}: {ex.Message}");
                return null;
            }
        }

        #endregion
    }
} 