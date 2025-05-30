using Newtonsoft.Json;
using System.Collections.Generic;
using System.Collections;
using System;
using UnityEngine;
using VDM.Runtime.Inventory.Models;


namespace VDM.Runtime.Services
{
    /// <summary>
    /// Service for managing inventory operations with backend synchronization
    /// Provides Unity interface to the backend inventory system
    /// </summary>
    public class InventoryService : BaseHTTPClient
    {
        [Header("Inventory Service Configuration")]
        [SerializeField] private float syncInterval = 30f; // Sync interval in seconds
        [SerializeField] private bool autoSync = true;
        
        // Cached inventory data
        private Dictionary<string, InventoryDTO> cachedInventories = new Dictionary<string, InventoryDTO>();
        private Dictionary<string, ItemDTO> cachedItems = new Dictionary<string, ItemDTO>();
        
        // Events
        public event Action<InventoryDTO> OnInventoryUpdated;
        public event Action<string, ItemDTO, int> OnItemAdded;
        public event Action<string, ItemDTO, int> OnItemRemoved;
        public event Action<string, string, ItemDTO, int> OnItemTransferred;
        public event Action<string> OnInventoryError;
        
        // Singleton instance
        private static InventoryService _instance;
        public static InventoryService Instance
        {
            get
            {
                if (_instance == null)
                {
                    _instance = FindObjectOfType<InventoryService>();
                    if (_instance == null)
                    {
                        GameObject serviceObject = new GameObject("InventoryService");
                        _instance = serviceObject.AddComponent<InventoryService>();
                        DontDestroyOnLoad(serviceObject);
                    }
                }
                return _instance;
            }
        }

        protected virtual void Awake()
        {
            if (_instance == null)
            {
                _instance = this;
                DontDestroyOnLoad(gameObject);
                InitializeClient();
            }
            else if (_instance != this)
            {
                Destroy(gameObject);
            }
        }

        protected virtual void Start()
        {
            base.Start();
            if (autoSync)
            {
                StartCoroutine(AutoSyncCoroutine());
            }
        }

        protected override string GetClientName() => "InventoryService";

        #region Inventory Operations

        /// <summary>
        /// Get all inventories with optional filtering
        /// </summary>
        public void GetInventories(Action<bool, List<InventoryDTO>> callback, string ownerId = null, string ownerType = null)
        {
            string endpoint = "/inventory/inventories";
            var queryParams = new List<string>();
            
            if (!string.IsNullOrEmpty(ownerId))
                queryParams.Add($"owner_id={ownerId}");
            if (!string.IsNullOrEmpty(ownerType))
                queryParams.Add($"inventory_type={ownerType}");
                
            if (queryParams.Count > 0)
                endpoint += "?" + string.Join("&", queryParams);

            StartCoroutine(GetRequestCoroutine(endpoint, (success, response) =>
            {
                if (success)
                {
                    try
                    {
                        var inventories = SafeDeserializeList<InventoryDTO>(response);
                        // Update cache
                        foreach (var inventory in inventories)
                        {
                            cachedInventories[inventory.Id] = inventory;
                        }
                        callback?.Invoke(true, inventories);
                    }
                    catch (Exception e)
                    {
                        Debug.LogError($"[InventoryService] Failed to parse inventories: {e.Message}");
                        callback?.Invoke(false, null);
                    }
                }
                else
                {
                    callback?.Invoke(false, null);
                }
            }));
        }

        /// <summary>
        /// Get a specific inventory by ID
        /// </summary>
        public void GetInventory(string inventoryId, Action<bool, InventoryDTO> callback, bool withItems = true)
        {
            string endpoint = $"/inventory/inventories/{inventoryId}?with_items={withItems}";
            
            StartCoroutine(GetRequestCoroutine(endpoint, (success, response) =>
            {
                if (success)
                {
                    var inventory = SafeDeserialize<InventoryDTO>(response);
                    if (inventory != null)
                    {
                        cachedInventories[inventoryId] = inventory;
                        OnInventoryUpdated?.Invoke(inventory);
                    }
                    callback?.Invoke(inventory != null, inventory);
                }
                else
                {
                    callback?.Invoke(false, null);
                }
            }));
        }

        /// <summary>
        /// Create a new inventory
        /// </summary>
        public void CreateInventory(CreateInventoryRequestDTO request, Action<bool, InventoryDTO> callback)
        {
            StartCoroutine(PostRequestCoroutine("/inventory/inventories", request, (success, response) =>
            {
                if (success)
                {
                    var inventory = SafeDeserialize<InventoryDTO>(response);
                    if (inventory != null)
                    {
                        cachedInventories[inventory.Id] = inventory;
                        OnInventoryUpdated?.Invoke(inventory);
                    }
                    callback?.Invoke(inventory != null, inventory);
                }
                else
                {
                    callback?.Invoke(false, null);
                }
            }));
        }

        /// <summary>
        /// Delete an inventory
        /// </summary>
        public void DeleteInventory(string inventoryId, Action<bool> callback)
        {
            StartCoroutine(DeleteRequestCoroutine($"/inventory/inventories/{inventoryId}", (success, response) =>
            {
                if (success)
                {
                    cachedInventories.Remove(inventoryId);
                }
                callback?.Invoke(success);
            }));
        }

        #endregion

        #region Item Operations

        /// <summary>
        /// Get all items with optional filtering
        /// </summary>
        public void GetItems(Action<bool, List<ItemDTO>> callback, ItemCategoryDTO? category = null, int limit = 100, int offset = 0)
        {
            string endpoint = $"/inventory/items?limit={limit}&offset={offset}";
            if (category.HasValue)
                endpoint += $"&category={category.Value}";

            StartCoroutine(GetRequestCoroutine(endpoint, (success, response) =>
            {
                if (success)
                {
                    var items = SafeDeserializeList<ItemDTO>(response);
                    // Update cache
                    foreach (var item in items)
                    {
                        cachedItems[item.Id] = item;
                    }
                    callback?.Invoke(true, items);
                }
                else
                {
                    callback?.Invoke(false, null);
                }
            }));
        }

        /// <summary>
        /// Get a specific item by ID
        /// </summary>
        public void GetItem(string itemId, Action<bool, ItemDTO> callback)
        {
            // Check cache first
            if (cachedItems.ContainsKey(itemId))
            {
                callback?.Invoke(true, cachedItems[itemId]);
                return;
            }

            StartCoroutine(GetRequestCoroutine($"/inventory/items/{itemId}", (success, response) =>
            {
                if (success)
                {
                    var item = SafeDeserialize<ItemDTO>(response);
                    if (item != null)
                    {
                        cachedItems[itemId] = item;
                    }
                    callback?.Invoke(item != null, item);
                }
                else
                {
                    callback?.Invoke(false, null);
                }
            }));
        }

        /// <summary>
        /// Create a new item
        /// </summary>
        public void CreateItem(CreateItemRequestDTO request, Action<bool, ItemDTO> callback)
        {
            StartCoroutine(PostRequestCoroutine("/inventory/items", request, (success, response) =>
            {
                if (success)
                {
                    var item = SafeDeserialize<ItemDTO>(response);
                    if (item != null)
                    {
                        cachedItems[item.Id] = item;
                    }
                    callback?.Invoke(item != null, item);
                }
                else
                {
                    callback?.Invoke(false, null);
                }
            }));
        }

        #endregion

        #region Inventory Item Operations

        /// <summary>
        /// Add an item to an inventory
        /// </summary>
        public void AddItemToInventory(string inventoryId, AddInventoryItemRequestDTO request, Action<bool, InventoryItemDTO> callback)
        {
            StartCoroutine(PostRequestCoroutine($"/inventory/inventories/{inventoryId}/items", request, (success, response) =>
            {
                if (success)
                {
                    var inventoryItem = SafeDeserialize<InventoryItemDTO>(response);
                    if (inventoryItem != null)
                    {
                        // Update cached inventory
                        if (cachedInventories.ContainsKey(inventoryId))
                        {
                            var inventory = cachedInventories[inventoryId];
                            inventory.Items.Add(inventoryItem);
                            OnInventoryUpdated?.Invoke(inventory);
                        }
                        
                        // Get item details for event
                        GetItem(request.ItemId, (itemSuccess, item) =>
                        {
                            if (itemSuccess && item != null)
                            {
                                OnItemAdded?.Invoke(inventoryId, item, request.Quantity);
                            }
                        });
                    }
                    callback?.Invoke(inventoryItem != null, inventoryItem);
                }
                else
                {
                    OnInventoryError?.Invoke($"Failed to add item to inventory {inventoryId}");
                    callback?.Invoke(false, null);
                }
            }));
        }

        /// <summary>
        /// Remove an item from an inventory
        /// </summary>
        public void RemoveItemFromInventory(string inventoryId, string inventoryItemId, Action<bool> callback, int? quantity = null)
        {
            string endpoint = $"/inventory/inventories/{inventoryId}/items/{inventoryItemId}";
            if (quantity.HasValue)
                endpoint += $"?quantity={quantity.Value}";

            StartCoroutine(DeleteRequestCoroutine(endpoint, (success, response) =>
            {
                if (success)
                {
                    // Update cached inventory
                    if (cachedInventories.ContainsKey(inventoryId))
                    {
                        var inventory = cachedInventories[inventoryId];
                        var itemToRemove = inventory.Items.Find(i => i.Id == inventoryItemId);
                        if (itemToRemove != null)
                        {
                            if (quantity.HasValue && quantity.Value < itemToRemove.Quantity)
                            {
                                itemToRemove.Quantity -= quantity.Value;
                            }
                            else
                            {
                                inventory.Items.Remove(itemToRemove);
                            }
                            OnInventoryUpdated?.Invoke(inventory);
                            
                            // Trigger event
                            if (itemToRemove.Item != null)
                            {
                                OnItemRemoved?.Invoke(inventoryId, itemToRemove.Item, quantity ?? itemToRemove.Quantity);
                            }
                        }
                    }
                }
                else
                {
                    OnInventoryError?.Invoke($"Failed to remove item from inventory {inventoryId}");
                }
                callback?.Invoke(success);
            }));
        }

        /// <summary>
        /// Transfer an item between inventories
        /// </summary>
        public void TransferItem(InventoryTransferRequestDTO request, Action<bool> callback)
        {
            StartCoroutine(PostRequestCoroutine("/inventory/transfer", request, (success, response) =>
            {
                if (success)
                {
                    // Update both cached inventories
                    if (cachedInventories.ContainsKey(request.SourceInventoryId))
                    {
                        RefreshInventory(request.SourceInventoryId);
                    }
                    if (cachedInventories.ContainsKey(request.TargetInventoryId))
                    {
                        RefreshInventory(request.TargetInventoryId);
                    }
                    
                    // Get item details for event
                    GetItem(request.InventoryItemId, (itemSuccess, item) =>
                    {
                        if (itemSuccess && item != null)
                        {
                            OnItemTransferred?.Invoke(request.SourceInventoryId, request.TargetInventoryId, item, request.Quantity);
                        }
                    });
                }
                else
                {
                    OnInventoryError?.Invoke("Failed to transfer item between inventories");
                }
                callback?.Invoke(success);
            }));
        }

        /// <summary>
        /// Get inventory statistics
        /// </summary>
        public void GetInventoryStats(string inventoryId, Action<bool, InventoryStatsDTO> callback)
        {
            StartCoroutine(GetRequestCoroutine($"/inventory/inventories/{inventoryId}/stats", (success, response) =>
            {
                if (success)
                {
                    var stats = SafeDeserialize<InventoryStatsDTO>(response);
                    callback?.Invoke(stats != null, stats);
                }
                else
                {
                    callback?.Invoke(false, null);
                }
            }));
        }

        #endregion

        #region Utility Methods

        /// <summary>
        /// Refresh an inventory from the server
        /// </summary>
        public void RefreshInventory(string inventoryId, Action<bool> callback = null)
        {
            GetInventory(inventoryId, (success, inventory) =>
            {
                callback?.Invoke(success);
            });
        }

        /// <summary>
        /// Get cached inventory if available
        /// </summary>
        public InventoryDTO GetCachedInventory(string inventoryId)
        {
            return cachedInventories.ContainsKey(inventoryId) ? cachedInventories[inventoryId] : null;
        }

        /// <summary>
        /// Get cached item if available
        /// </summary>
        public ItemDTO GetCachedItem(string itemId)
        {
            return cachedItems.ContainsKey(itemId) ? cachedItems[itemId] : null;
        }

        /// <summary>
        /// Clear all cached data
        /// </summary>
        public void ClearCache()
        {
            cachedInventories.Clear();
            cachedItems.Clear();
        }

        /// <summary>
        /// Auto-sync coroutine for periodic inventory updates
        /// </summary>
        private IEnumerator AutoSyncCoroutine()
        {
            while (autoSync)
            {
                yield return new WaitForSeconds(syncInterval);
                
                // Refresh all cached inventories
                foreach (var inventoryId in cachedInventories.Keys)
                {
                    RefreshInventory(inventoryId);
                }
            }
        }

        #endregion

        #region Validation Helpers

        /// <summary>
        /// Validate inventory operation locally before sending to server
        /// </summary>
        public bool ValidateAddItem(string inventoryId, ItemDTO item, int quantity)
        {
            var inventory = GetCachedInventory(inventoryId);
            if (inventory == null) return true; // Let server validate if not cached
            
            // Check weight limits
            float totalWeight = inventory.CurrentWeight + (item.Weight * quantity);
            if (totalWeight > inventory.MaxWeight)
            {
                OnInventoryError?.Invoke($"Adding {quantity} {item.Name} would exceed weight limit");
                return false;
            }
            
            // Check slot limits (simplified)
            int currentSlots = inventory.Items.Count;
            if (!item.Stackable && currentSlots + 1 > inventory.MaxSlots)
            {
                OnInventoryError?.Invoke($"No more slots available for {item.Name}");
                return false;
            }
            
            return true;
        }

        #endregion
    }
} 