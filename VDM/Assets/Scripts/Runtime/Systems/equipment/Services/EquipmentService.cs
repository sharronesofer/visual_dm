using System;
using System.Collections;
using System.Collections.Generic;
using System.Threading.Tasks;
using UnityEngine;
using VDM.Systems.Equipment.Models;
using VDM.Systems.Inventory.Models;
using VDM.Infrastructure.Services;
using VDM.DTOs.Equipment;

namespace VDM.Systems.Equipment.Services
{
    /// <summary>
    /// HTTP service for equipment system operations
    /// </summary>
    public class EquipmentService : BaseHttpService
    {
        private const string EQUIPMENT_ENDPOINT = "/api/equipment";
        private const string INVENTORY_ENDPOINT = "/api/inventory";
        private const string ITEMS_ENDPOINT = "/api/items";

        public EquipmentService() : base()
        {
        }

        #region Inventory Management

        /// <summary>
        /// Get a player's inventory
        /// </summary>
        public async Task<Models.Inventory> GetInventoryAsync(string playerId)
        {
            try
            {
                var url = $"{INVENTORY_ENDPOINT}/{playerId}";
                var response = await GetAsync<Models.Inventory>(url);
                return response;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get inventory for player {playerId}: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Update a player's inventory
        /// </summary>
        public async Task<bool> UpdateInventoryAsync(string playerId, Models.Inventory inventory)
        {
            try
            {
                var url = $"{INVENTORY_ENDPOINT}/{playerId}";
                var response = await PutAsync<Models.Inventory, bool>(url, inventory);
                return response;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to update inventory for player {playerId}: {ex.Message}");
                return false;
            }
        }

        /// <summary>
        /// Add item to player's inventory
        /// </summary>
        public async Task<EquipmentActionResult> AddItemToInventoryAsync(string playerId, Models.Equipment item)
        {
            try
            {
                var url = $"{INVENTORY_ENDPOINT}/{playerId}/add";
                var response = await PostAsync<Models.Equipment, EquipmentActionResult>(url, item);
                return response;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to add item to inventory for player {playerId}: {ex.Message}");
                return new EquipmentActionResult { Success = false, Message = ex.Message };
            }
        }

        /// <summary>
        /// Remove item from player's inventory
        /// </summary>
        public async Task<EquipmentActionResult> RemoveItemFromInventoryAsync(string playerId, string itemId)
        {
            try
            {
                var url = $"{INVENTORY_ENDPOINT}/{playerId}/remove/{itemId}";
                var response = await DeleteAsync<EquipmentActionResult>(url);
                return response;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to remove item from inventory for player {playerId}: {ex.Message}");
                return new EquipmentActionResult { Success = false, Message = ex.Message };
            }
        }

        #endregion

        #region Equipment Operations

        /// <summary>
        /// Equip an item
        /// </summary>
        public async Task<EquipmentActionResult> EquipItemAsync(string playerId, string itemId)
        {
            try
            {
                var url = $"{EQUIPMENT_ENDPOINT}/{playerId}/equip";
                var data = new { ItemId = itemId };
                var response = await PostAsync<object, EquipmentActionResult>(url, data);
                return response;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to equip item {itemId} for player {playerId}: {ex.Message}");
                return new EquipmentActionResult { Success = false, Message = ex.Message };
            }
        }

        /// <summary>
        /// Unequip an item
        /// </summary>
        public async Task<EquipmentActionResult> UnequipItemAsync(string playerId, EquipmentSlot slot)
        {
            try
            {
                var url = $"{EQUIPMENT_ENDPOINT}/{playerId}/unequip";
                var data = new { Slot = slot.ToString() };
                var response = await PostAsync<object, EquipmentActionResult>(url, data);
                return response;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to unequip item from slot {slot} for player {playerId}: {ex.Message}");
                return new EquipmentActionResult { Success = false, Message = ex.Message };
            }
        }

        /// <summary>
        /// Get all equipped items for a player
        /// </summary>
        public async Task<List<Models.Equipment>> GetEquippedItemsAsync(string playerId)
        {
            try
            {
                var url = $"{EQUIPMENT_ENDPOINT}/{playerId}/equipped";
                var response = await GetAsync<List<Models.Equipment>>(url);
                return response ?? new List<Models.Equipment>();
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get equipped items for player {playerId}: {ex.Message}");
                return new List<Models.Equipment>();
            }
        }

        /// <summary>
        /// Get equipment stats for a player
        /// </summary>
        public async Task<Dictionary<string, int>> GetEquipmentStatsAsync(string playerId)
        {
            try
            {
                var url = $"{EQUIPMENT_ENDPOINT}/{playerId}/stats";
                var response = await GetAsync<Dictionary<string, int>>(url);
                return response ?? new Dictionary<string, int>();
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get equipment stats for player {playerId}: {ex.Message}");
                return new Dictionary<string, int>();
            }
        }

        #endregion

        #region Item Management

        /// <summary>
        /// Get item details by ID
        /// </summary>
        public async Task<Models.Equipment> GetItemAsync(string itemId)
        {
            try
            {
                var url = $"{ITEMS_ENDPOINT}/{itemId}";
                var response = await GetAsync<Models.Equipment>(url);
                return response;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get item {itemId}: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Create a new item
        /// </summary>
        public async Task<Models.Equipment> CreateItemAsync(Models.Equipment item)
        {
            try
            {
                var url = ITEMS_ENDPOINT;
                var response = await PostAsync<Models.Equipment, Models.Equipment>(url, item);
                return response;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to create item: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Update an existing item
        /// </summary>
        public async Task<Models.Equipment> UpdateItemAsync(string itemId, Models.Equipment item)
        {
            try
            {
                var url = $"{ITEMS_ENDPOINT}/{itemId}";
                var response = await PutAsync<Models.Equipment, Models.Equipment>(url, item);
                return response;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to update item {itemId}: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Delete an item
        /// </summary>
        public async Task<bool> DeleteItemAsync(string itemId)
        {
            try
            {
                var url = $"{ITEMS_ENDPOINT}/{itemId}";
                var response = await DeleteAsync<bool>(url);
                return response;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to delete item {itemId}: {ex.Message}");
                return false;
            }
        }

        /// <summary>
        /// Search for items
        /// </summary>
        public async Task<List<Models.Equipment>> SearchItemsAsync(Dictionary<string, object> filters)
        {
            try
            {
                var url = $"{ITEMS_ENDPOINT}/search";
                var response = await PostAsync<Dictionary<string, object>, List<Models.Equipment>>(url, filters);
                return response ?? new List<Models.Equipment>();
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to search items: {ex.Message}");
                return new List<Models.Equipment>();
            }
        }

        #endregion

        #region Item Enhancement

        /// <summary>
        /// Repair an item
        /// </summary>
        public async Task<EquipmentActionResult> RepairItemAsync(string itemId, int repairAmount)
        {
            try
            {
                var url = $"{ITEMS_ENDPOINT}/{itemId}/repair";
                var data = new { RepairAmount = repairAmount };
                var response = await PostAsync<object, EquipmentActionResult>(url, data);
                return response;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to repair item {itemId}: {ex.Message}");
                return new EquipmentActionResult { Success = false, Message = ex.Message };
            }
        }

        /// <summary>
        /// Add experience to an item for evolution
        /// </summary>
        public async Task<EquipmentActionResult> AddItemExperienceAsync(string itemId, int experience)
        {
            try
            {
                var url = $"{ITEMS_ENDPOINT}/{itemId}/experience";
                var data = new { Experience = experience };
                var response = await PostAsync<object, EquipmentActionResult>(url, data);
                return response;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to add experience to item {itemId}: {ex.Message}");
                return new EquipmentActionResult { Success = false, Message = ex.Message };
            }
        }

        /// <summary>
        /// Evolve an item
        /// </summary>
        public async Task<EquipmentActionResult> EvolveItemAsync(string itemId)
        {
            try
            {
                var url = $"{ITEMS_ENDPOINT}/{itemId}/evolve";
                var response = await PostAsync<object, EquipmentActionResult>(url, new { });
                return response;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to evolve item {itemId}: {ex.Message}");
                return new EquipmentActionResult { Success = false, Message = ex.Message };
            }
        }

        /// <summary>
        /// Identify an item
        /// </summary>
        public async Task<EquipmentActionResult> IdentifyItemAsync(string itemId)
        {
            try
            {
                var url = $"{ITEMS_ENDPOINT}/{itemId}/identify";
                var response = await PostAsync<object, EquipmentActionResult>(url, new { });
                return response;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to identify item {itemId}: {ex.Message}");
                return new EquipmentActionResult { Success = false, Message = ex.Message };
            }
        }

        /// <summary>
        /// Add enchantment to an item
        /// </summary>
        public async Task<EquipmentActionResult> AddEnchantmentAsync(string itemId, string enchantmentId)
        {
            try
            {
                var url = $"{ITEMS_ENDPOINT}/{itemId}/enchantments";
                var data = new { EnchantmentId = enchantmentId };
                var response = await PostAsync<object, EquipmentActionResult>(url, data);
                return response;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to add enchantment to item {itemId}: {ex.Message}");
                return new EquipmentActionResult { Success = false, Message = ex.Message };
            }
        }

        /// <summary>
        /// Remove enchantment from an item
        /// </summary>
        public async Task<EquipmentActionResult> RemoveEnchantmentAsync(string itemId, string enchantmentId)
        {
            try
            {
                var url = $"{ITEMS_ENDPOINT}/{itemId}/enchantments/{enchantmentId}";
                var response = await DeleteAsync<EquipmentActionResult>(url);
                return response;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to remove enchantment from item {itemId}: {ex.Message}");
                return new EquipmentActionResult { Success = false, Message = ex.Message };
            }
        }

        #endregion

        #region Properties

        /// <summary>
        /// Get available equipment properties
        /// </summary>
        public async Task<List<EquipmentProperty>> GetAvailablePropertiesAsync()
        {
            try
            {
                var url = $"{EQUIPMENT_ENDPOINT}/properties";
                var response = await GetAsync<List<EquipmentProperty>>(url);
                return response ?? new List<EquipmentProperty>();
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get available properties: {ex.Message}");
                return new List<EquipmentProperty>();
            }
        }

        /// <summary>
        /// Add property to an item
        /// </summary>
        public async Task<EquipmentActionResult> AddPropertyAsync(string itemId, EquipmentProperty property)
        {
            try
            {
                var url = $"{ITEMS_ENDPOINT}/{itemId}/properties";
                var response = await PostAsync<EquipmentProperty, EquipmentActionResult>(url, property);
                return response;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to add property to item {itemId}: {ex.Message}");
                return new EquipmentActionResult { Success = false, Message = ex.Message };
            }
        }

        /// <summary>
        /// Remove property from an item
        /// </summary>
        public async Task<EquipmentActionResult> RemovePropertyAsync(string itemId, string propertyId)
        {
            try
            {
                var url = $"{ITEMS_ENDPOINT}/{itemId}/properties/{propertyId}";
                var response = await DeleteAsync<EquipmentActionResult>(url);
                return response;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to remove property from item {itemId}: {ex.Message}");
                return new EquipmentActionResult { Success = false, Message = ex.Message };
            }
        }

        /// <summary>
        /// Activate item property
        /// </summary>
        public async Task<EquipmentActionResult> ActivatePropertyAsync(string itemId, string propertyId)
        {
            try
            {
                var url = $"{ITEMS_ENDPOINT}/{itemId}/properties/{propertyId}/activate";
                var response = await PostAsync<object, EquipmentActionResult>(url, new { });
                return response;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to activate property {propertyId} on item {itemId}: {ex.Message}");
                return new EquipmentActionResult { Success = false, Message = ex.Message };
            }
        }

        /// <summary>
        /// Deactivate item property
        /// </summary>
        public async Task<EquipmentActionResult> DeactivatePropertyAsync(string itemId, string propertyId)
        {
            try
            {
                var url = $"{ITEMS_ENDPOINT}/{itemId}/properties/{propertyId}/deactivate";
                var response = await PostAsync<object, EquipmentActionResult>(url, new { });
                return response;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to deactivate property {propertyId} on item {itemId}: {ex.Message}");
                return new EquipmentActionResult { Success = false, Message = ex.Message };
            }
        }

        #endregion

        #region System State

        /// <summary>
        /// Get equipment system state
        /// </summary>
        public async Task<EquipmentSystemState> GetEquipmentSystemStateAsync()
        {
            try
            {
                var url = $"{EQUIPMENT_ENDPOINT}/state";
                var response = await GetAsync<EquipmentSystemState>(url);
                return response;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get equipment system state: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Get equipment events
        /// </summary>
        public async Task<List<EquipmentEvent>> GetEquipmentEventsAsync(string playerId = null, int limit = 50)
        {
            try
            {
                var url = $"{EQUIPMENT_ENDPOINT}/events";
                if (!string.IsNullOrEmpty(playerId))
                {
                    url += $"?playerId={playerId}";
                }
                url += $"{(url.Contains("?") ? "&" : "?")}limit={limit}";
                
                var response = await GetAsync<List<EquipmentEvent>>(url);
                return response ?? new List<EquipmentEvent>();
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get equipment events: {ex.Message}");
                return new List<EquipmentEvent>();
            }
        }

        #endregion

        #region Bulk Operations

        /// <summary>
        /// Transfer item between players
        /// </summary>
        public async Task<EquipmentActionResult> TransferItemAsync(string fromPlayerId, string toPlayerId, string itemId)
        {
            try
            {
                var url = $"{EQUIPMENT_ENDPOINT}/transfer";
                var data = new 
                { 
                    FromPlayerId = fromPlayerId, 
                    ToPlayerId = toPlayerId, 
                    ItemId = itemId 
                };
                var response = await PostAsync<object, EquipmentActionResult>(url, data);
                return response;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to transfer item {itemId} from {fromPlayerId} to {toPlayerId}: {ex.Message}");
                return new EquipmentActionResult { Success = false, Message = ex.Message };
            }
        }

        /// <summary>
        /// Generate random loot
        /// </summary>
        public async Task<List<Models.Equipment>> GenerateLootAsync(Dictionary<string, object> parameters)
        {
            try
            {
                var url = $"{EQUIPMENT_ENDPOINT}/generate-loot";
                var response = await PostAsync<Dictionary<string, object>, List<Models.Equipment>>(url, parameters);
                return response ?? new List<Models.Equipment>();
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to generate loot: {ex.Message}");
                return new List<Models.Equipment>();
            }
        }

        /// <summary>
        /// Get item templates
        /// </summary>
        public async Task<List<Models.Equipment>> GetItemTemplatesAsync(EquipmentType? type = null, EquipmentQuality? quality = null)
        {
            try
            {
                var url = $"{ITEMS_ENDPOINT}/templates";
                var queryParams = new List<string>();
                
                if (type.HasValue)
                    queryParams.Add($"type={type.Value}");
                if (quality.HasValue)
                    queryParams.Add($"quality={quality.Value}");
                
                if (queryParams.Count > 0)
                    url += "?" + string.Join("&", queryParams);
                
                var response = await GetAsync<List<Models.Equipment>>(url);
                return response ?? new List<Models.Equipment>();
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get item templates: {ex.Message}");
                return new List<Models.Equipment>();
            }
        }

        #endregion

        /// <summary>
        /// Get equipment for a character
        /// </summary>
        public void GetCharacterEquipment(string characterId, System.Action<bool, List<EquipmentDTO>> callback)
        {
            if (string.IsNullOrEmpty(characterId))
            {
                Debug.LogWarning("[EquipmentService] Character ID is required");
                callback?.Invoke(false, null);
                return;
            }

            StartCoroutine(GetCharacterEquipmentCoroutine(characterId, callback));
        }

        /// <summary>
        /// Get character inventory
        /// </summary>
        public void GetCharacterInventory(string characterId, System.Action<bool, InventoryDTO> callback)
        {
            if (string.IsNullOrEmpty(characterId))
            {
                Debug.LogWarning("[EquipmentService] Character ID is required");
                callback?.Invoke(false, null);
                return;
            }

            StartCoroutine(GetCharacterInventoryCoroutine(characterId, callback));
        }

        /// <summary>
        /// Equip an item
        /// </summary>
        public void EquipItem(string characterId, string itemId, System.Action<bool, EquipmentDTO> callback)
        {
            if (string.IsNullOrEmpty(characterId) || string.IsNullOrEmpty(itemId))
            {
                Debug.LogWarning("[EquipmentService] Character ID and Item ID are required");
                callback?.Invoke(false, null);
                return;
            }

            StartCoroutine(EquipItemCoroutine(characterId, itemId, callback));
        }
    }
} 