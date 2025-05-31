using NativeWebSocket;
using Newtonsoft.Json;
using System.Collections.Generic;
using System;
using UnityEngine;
using VDM.Infrastructure.Services.Websocket;
using VDM.Systems.Inventory.Models;


namespace VDM.Systems.Inventory.Services
{
    /// <summary>
    /// WebSocket handler for Inventory system real-time updates
    /// </summary>
    public class InventoryWebSocketHandler : BaseWebSocketHandler
    {
        #region Events

        public event Action<InventoryData> OnInventoryUpdated;
        public event Action<InventoryItemData> OnItemAdded;
        public event Action<InventoryItemData> OnItemRemoved;
        public event Action<InventoryItemData> OnItemUpdated;
        public event Action<InventoryTransferRequest> OnItemTransferred;
        public event Action<CharacterEquipmentData> OnEquipmentUpdated;
        public event Action<string, string, string> OnItemEquipped; // characterId, itemId, slot
        public event Action<string, string> OnItemUnequipped; // characterId, slot
        public event Action<InventoryStatsData> OnInventoryStatsUpdated;
        public event Action<string, Dictionary<string, object>> OnInventoryEvent;

        #endregion

        private const string INVENTORY_CHANNEL = "inventory";
        private const string ITEMS_CHANNEL = "items";
        private const string EQUIPMENT_CHANNEL = "equipment";
        private const string TRANSFER_CHANNEL = "transfer";
        private const string STATS_CHANNEL = "stats";

        public InventoryWebSocketHandler() : base() { }

        protected override void HandleMessage(string message)
        {
            try
            {
                var messageData = JsonConvert.DeserializeObject<Dictionary<string, object>>(message);
                
                if (!messageData.ContainsKey("type"))
                {
                    Debug.LogWarning($"Inventory WebSocket message missing type field: {message}");
                    return;
                }

                string messageType = messageData["type"].ToString();
                string channel = messageData.ContainsKey("channel") ? messageData["channel"].ToString() : "default";

                switch (channel)
                {
                    case INVENTORY_CHANNEL:
                        HandleInventoryMessage(messageType, messageData);
                        break;
                    case ITEMS_CHANNEL:
                        HandleItemMessage(messageType, messageData);
                        break;
                    case EQUIPMENT_CHANNEL:
                        HandleEquipmentMessage(messageType, messageData);
                        break;
                    case TRANSFER_CHANNEL:
                        HandleTransferMessage(messageType, messageData);
                        break;
                    case STATS_CHANNEL:
                        HandleStatsMessage(messageType, messageData);
                        break;
                    default:
                        Debug.LogWarning($"Unknown inventory channel: {channel}");
                        break;
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling inventory WebSocket message: {ex.Message}\nMessage: {message}");
            }
        }

        private void InitializeInventoryWebSocket(string serverUrl)
        {
            // Subscribe to inventory channels
            Subscribe(INVENTORY_CHANNEL);
            Subscribe(ITEMS_CHANNEL);
            Subscribe(EQUIPMENT_CHANNEL);
            Subscribe(TRANSFER_CHANNEL);
            Subscribe(STATS_CHANNEL);
        }

        #region Message Handlers

        private void HandleInventoryMessage(string messageType, Dictionary<string, object> messageData)
        {
            switch (messageType)
            {
                case "inventory_created":
                case "inventory_updated":
                    if (messageData.ContainsKey("inventory"))
                    {
                        var inventoryJson = JsonConvert.SerializeObject(messageData["inventory"]);
                        var inventory = JsonConvert.DeserializeObject<InventoryData>(inventoryJson);
                        OnInventoryUpdated?.Invoke(inventory);
                    }
                    break;

                case "inventory_event":
                    if (messageData.ContainsKey("inventory_id") && messageData.ContainsKey("event_data"))
                    {
                        string inventoryId = messageData["inventory_id"].ToString();
                        var eventData = messageData["event_data"] as Dictionary<string, object>;
                        OnInventoryEvent?.Invoke(inventoryId, eventData);
                    }
                    break;
            }
        }

        private void HandleItemMessage(string messageType, Dictionary<string, object> messageData)
        {
            switch (messageType)
            {
                case "item_added":
                    if (messageData.ContainsKey("inventory_item"))
                    {
                        var itemJson = JsonConvert.SerializeObject(messageData["inventory_item"]);
                        var item = JsonConvert.DeserializeObject<InventoryItemData>(itemJson);
                        OnItemAdded?.Invoke(item);
                    }
                    break;

                case "item_removed":
                    if (messageData.ContainsKey("inventory_item"))
                    {
                        var itemJson = JsonConvert.SerializeObject(messageData["inventory_item"]);
                        var item = JsonConvert.DeserializeObject<InventoryItemData>(itemJson);
                        OnItemRemoved?.Invoke(item);
                    }
                    break;

                case "item_updated":
                    if (messageData.ContainsKey("inventory_item"))
                    {
                        var itemJson = JsonConvert.SerializeObject(messageData["inventory_item"]);
                        var item = JsonConvert.DeserializeObject<InventoryItemData>(itemJson);
                        OnItemUpdated?.Invoke(item);
                    }
                    break;

                case "item_moved":
                    if (messageData.ContainsKey("inventory_item"))
                    {
                        var itemJson = JsonConvert.SerializeObject(messageData["inventory_item"]);
                        var item = JsonConvert.DeserializeObject<InventoryItemData>(itemJson);
                        OnItemUpdated?.Invoke(item);
                    }
                    break;
            }
        }

        private void HandleEquipmentMessage(string messageType, Dictionary<string, object> messageData)
        {
            switch (messageType)
            {
                case "item_equipped":
                    if (messageData.ContainsKey("character_id") && 
                        messageData.ContainsKey("item_id") && 
                        messageData.ContainsKey("slot"))
                    {
                        string characterId = messageData["character_id"].ToString();
                        string itemId = messageData["item_id"].ToString();
                        string slot = messageData["slot"].ToString();
                        OnItemEquipped?.Invoke(characterId, itemId, slot);
                    }
                    break;

                case "item_unequipped":
                    if (messageData.ContainsKey("character_id") && messageData.ContainsKey("slot"))
                    {
                        string characterId = messageData["character_id"].ToString();
                        string slot = messageData["slot"].ToString();
                        OnItemUnequipped?.Invoke(characterId, slot);
                    }
                    break;

                case "equipment_updated":
                    if (messageData.ContainsKey("equipment"))
                    {
                        var equipmentJson = JsonConvert.SerializeObject(messageData["equipment"]);
                        var equipment = JsonConvert.DeserializeObject<CharacterEquipmentData>(equipmentJson);
                        OnEquipmentUpdated?.Invoke(equipment);
                    }
                    break;
            }
        }

        private void HandleTransferMessage(string messageType, Dictionary<string, object> messageData)
        {
            switch (messageType)
            {
                case "item_transferred":
                    if (messageData.ContainsKey("transfer_request"))
                    {
                        var transferJson = JsonConvert.SerializeObject(messageData["transfer_request"]);
                        var transfer = JsonConvert.DeserializeObject<InventoryTransferRequest>(transferJson);
                        OnItemTransferred?.Invoke(transfer);
                    }
                    break;

                case "transfer_completed":
                    // Update both source and destination inventories
                    if (messageData.ContainsKey("source_inventory"))
                    {
                        var sourceJson = JsonConvert.SerializeObject(messageData["source_inventory"]);
                        var sourceInventory = JsonConvert.DeserializeObject<InventoryData>(sourceJson);
                        OnInventoryUpdated?.Invoke(sourceInventory);
                    }

                    if (messageData.ContainsKey("destination_inventory"))
                    {
                        var destJson = JsonConvert.SerializeObject(messageData["destination_inventory"]);
                        var destInventory = JsonConvert.DeserializeObject<InventoryData>(destJson);
                        OnInventoryUpdated?.Invoke(destInventory);
                    }
                    break;
            }
        }

        private void HandleStatsMessage(string messageType, Dictionary<string, object> messageData)
        {
            switch (messageType)
            {
                case "stats_updated":
                    if (messageData.ContainsKey("stats"))
                    {
                        var statsJson = JsonConvert.SerializeObject(messageData["stats"]);
                        var stats = JsonConvert.DeserializeObject<InventoryStatsData>(statsJson);
                        OnInventoryStatsUpdated?.Invoke(stats);
                    }
                    break;
            }
        }

        #endregion

        #region Subscription Management

        /// <summary>
        /// Subscribe to inventory updates for a specific inventory
        /// </summary>
        public void SubscribeToInventory(string inventoryId)
        {
            Subscribe($"{INVENTORY_CHANNEL}:{inventoryId}");
        }

        /// <summary>
        /// Unsubscribe from inventory updates for a specific inventory
        /// </summary>
        public void UnsubscribeFromInventory(string inventoryId)
        {
            Unsubscribe($"{INVENTORY_CHANNEL}:{inventoryId}");
        }

        /// <summary>
        /// Subscribe to character inventory updates
        /// </summary>
        public void SubscribeToCharacterInventory(string characterId)
        {
            Subscribe($"{INVENTORY_CHANNEL}:character:{characterId}");
        }

        /// <summary>
        /// Subscribe to equipment updates for a character
        /// </summary>
        public void SubscribeToCharacterEquipment(string characterId)
        {
            Subscribe($"{EQUIPMENT_CHANNEL}:{characterId}");
        }

        /// <summary>
        /// Subscribe to transfer events involving specific inventories
        /// </summary>
        public void SubscribeToTransfers(string inventoryId)
        {
            Subscribe($"{TRANSFER_CHANNEL}:{inventoryId}");
        }

        /// <summary>
        /// Subscribe to inventory statistics updates
        /// </summary>
        public void SubscribeToInventoryStats(string inventoryId)
        {
            Subscribe($"{STATS_CHANNEL}:{inventoryId}");
        }

        #endregion

        #region Utility Methods

        /// <summary>
        /// Send a request to track a specific inventory
        /// </summary>
        public void RequestInventoryTracking(string inventoryId)
        {
            var request = new
            {
                type = "track_inventory",
                inventory_id = inventoryId
            };

            SendMessage(INVENTORY_CHANNEL, JsonConvert.SerializeObject(request));
        }

        /// <summary>
        /// Send a request to get current inventory status
        /// </summary>
        public void RequestInventoryStatus(string inventoryId)
        {
            var request = new
            {
                type = "get_inventory_status",
                inventory_id = inventoryId
            };

            SendMessage(INVENTORY_CHANNEL, JsonConvert.SerializeObject(request));
        }

        /// <summary>
        /// Send a request to get real-time item updates
        /// </summary>
        public void RequestItemUpdates(string inventoryId)
        {
            var request = new
            {
                type = "request_item_updates",
                inventory_id = inventoryId
            };

            SendMessage(ITEMS_CHANNEL, JsonConvert.SerializeObject(request));
        }

        /// <summary>
        /// Send a request to synchronize inventory data
        /// </summary>
        public void RequestInventorySync(string inventoryId)
        {
            var request = new
            {
                type = "sync_inventory",
                inventory_id = inventoryId
            };

            SendMessage(INVENTORY_CHANNEL, JsonConvert.SerializeObject(request));
        }

        /// <summary>
        /// Send a request to validate an inventory operation before execution
        /// </summary>
        public void RequestOperationValidation(string inventoryId, string operation, Dictionary<string, object> parameters)
        {
            var request = new
            {
                type = "validate_operation",
                inventory_id = inventoryId,
                operation = operation,
                parameters = parameters
            };

            SendMessage(INVENTORY_CHANNEL, JsonConvert.SerializeObject(request));
        }

        #endregion
    }
} 