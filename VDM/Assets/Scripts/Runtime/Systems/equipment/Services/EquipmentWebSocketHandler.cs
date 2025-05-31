using NativeWebSocket;
using System;
using System.Collections.Generic;
using UnityEngine;
using VDM.Infrastructure.Services.Websocket;
using VDM.Systems.Equipment.Models;
using Newtonsoft.Json;
using VDM.Systems.Inventory.Models;

namespace VDM.Systems.Equipment.Services
{
    /// <summary>
    /// WebSocket handler for real-time equipment system updates
    /// </summary>
    public class EquipmentWebSocketHandler : BaseWebSocketHandler
    {
        #region Events

        public event Action<EquipmentEvent> OnEquipmentEvent;
        public event Action<EquipmentSystemState> OnEquipmentStateUpdated;
        public event Action<string, InventoryData> OnInventoryUpdated;
        public event Action<string, Models.Equipment> OnItemEquipped;
        public event Action<string, Models.Equipment> OnItemUnequipped;
        public event Action<string, Models.Equipment> OnItemUpgraded;
        public event Action<string, Models.Equipment> OnItemDestroyed;
        public event Action<string, Models.Equipment> OnItemRepaired;
        public event Action<Models.Equipment> OnItemCreated;
        public event Action<Models.Equipment> OnItemEvolved;
        public event Action<Models.Equipment> OnItemIdentified;
        public event Action<string, EquipmentProperty> OnPropertyActivated;
        public event Action<string, string> OnPropertyDeactivated;

        #endregion

        #region Room Management

        /// <summary>
        /// Join equipment room for real-time updates
        /// </summary>
        public async void JoinEquipmentRoom(string playerId)
        {
            try
            {
                await SendMessageAsync("join_equipment", new { playerId });
                Debug.Log($"Joined equipment room for player: {playerId}");
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to join equipment room for {playerId}: {ex.Message}");
            }
        }

        /// <summary>
        /// Leave equipment room
        /// </summary>
        public async void LeaveEquipmentRoom(string playerId)
        {
            try
            {
                await SendMessageAsync("leave_equipment", new { playerId });
                Debug.Log($"Left equipment room for player: {playerId}");
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to leave equipment room for {playerId}: {ex.Message}");
            }
        }

        #endregion

        #region WebSocket Message Handling

        protected override void HandleMessage(string message)
        {
            try
            {
                var data = JsonUtility.FromJson<Dictionary<string, object>>(message);
                if (data.ContainsKey("type"))
                {
                    string messageType = data["type"].ToString();
                    string messageData = data.ContainsKey("data") ? data["data"].ToString() : message;
                    
                    switch (messageType)
                    {
                        case "equipment_updated":
                            HandleEquipmentStateUpdatedMessage(messageData);
                            break;
                        case "inventory_updated":
                            HandleInventoryUpdatedMessage(messageData);
                            break;
                        case "item_equipped":
                            HandleItemEquippedMessage(messageData);
                            break;
                        case "item_unequipped":
                            HandleItemUnequippedMessage(messageData);
                            break;
                        case "item_destroyed":
                            HandleItemDestroyedMessage(messageData);
                            break;
                        case "property_activated":
                            HandlePropertyActivatedMessage(messageData);
                            break;
                        case "property_deactivated":
                            HandlePropertyDeactivatedMessage(messageData);
                            break;
                        default:
                            Debug.LogWarning($"Unknown equipment event type: {messageType}");
                            break;
                    }
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling equipment WebSocket message: {ex.Message}");
            }
        }

        private void HandleEquipmentStateUpdatedMessage(string data)
        {
            try
            {
                var state = JsonUtility.FromJson<EquipmentSystemState>(data);
                if (state != null)
                {
                    OnEquipmentStateUpdated?.Invoke(state);
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error parsing equipment state: {ex.Message}");
            }
        }

        private void HandleInventoryUpdatedMessage(string data)
        {
            try
            {
                var message = JsonUtility.FromJson<InventoryUpdateMessage>(data);
                if (message != null && message.Inventory != null)
                {
                    OnInventoryUpdated?.Invoke(message.PlayerId, message.Inventory);
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error parsing inventory update: {ex.Message}");
            }
        }

        private void HandleItemEquippedMessage(string data)
        {
            try
            {
                var message = JsonUtility.FromJson<ItemEquippedMessage>(data);
                if (message != null && message.Equipment != null)
                {
                    OnItemEquipped?.Invoke(message.PlayerId, message.Equipment);
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error parsing item equipped message: {ex.Message}");
            }
        }

        private void HandleItemUnequippedMessage(string data)
        {
            try
            {
                var message = JsonUtility.FromJson<ItemUnequippedMessage>(data);
                if (message != null)
                {
                    OnItemUnequipped?.Invoke(message.PlayerId, message.Equipment);
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error parsing item unequipped message: {ex.Message}");
            }
        }

        private void HandleItemDestroyedMessage(string data)
        {
            try
            {
                var message = JsonUtility.FromJson<ItemDestroyedMessage>(data);
                if (message != null)
                {
                    OnItemDestroyed?.Invoke(message.PlayerId, message.Equipment);
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error parsing item destroyed message: {ex.Message}");
            }
        }

        private void HandlePropertyActivatedMessage(string data)
        {
            try
            {
                var message = JsonUtility.FromJson<PropertyActivatedMessage>(data);
                if (message != null)
                {
                    OnPropertyActivated?.Invoke(message.ItemId, message.Property);
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error parsing property activated message: {ex.Message}");
            }
        }

        private void HandlePropertyDeactivatedMessage(string data)
        {
            try
            {
                var message = JsonUtility.FromJson<PropertyDeactivatedMessage>(data);
                if (message != null)
                {
                    OnPropertyDeactivated?.Invoke(message.ItemId, message.PropertyId);
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error parsing property deactivated message: {ex.Message}");
            }
        }

        #endregion

        #region Equipment Actions

        /// <summary>
        /// Request to equip an item
        /// </summary>
        public async void RequestEquipItem(string playerId, string itemId)
        {
            try
            {
                await SendMessageAsync("equip_item", new { playerId, itemId });
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to request equip item: {ex.Message}");
            }
        }

        /// <summary>
        /// Request to unequip an item
        /// </summary>
        public async void RequestUnequipItem(string playerId, EquipmentSlot slot)
        {
            try
            {
                await SendMessageAsync("unequip_item", new { playerId, slot = slot.ToString() });
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to request unequip item: {ex.Message}");
            }
        }

        /// <summary>
        /// Request to repair an item
        /// </summary>
        public async void RequestRepairItem(string itemId, int repairAmount)
        {
            try
            {
                await SendMessageAsync("repair_item", new { itemId, repairAmount });
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to request repair item: {ex.Message}");
            }
        }

        /// <summary>
        /// Request to evolve an item
        /// </summary>
        public async void RequestEvolveItem(string itemId)
        {
            try
            {
                await SendMessageAsync("evolve_item", new { itemId });
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to request evolve item: {ex.Message}");
            }
        }

        /// <summary>
        /// Request to identify an item
        /// </summary>
        public async void RequestIdentifyItem(string itemId)
        {
            try
            {
                await SendMessageAsync("identify_item", new { itemId });
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to request identify item: {ex.Message}");
            }
        }

        /// <summary>
        /// Request to activate item property
        /// </summary>
        public async void RequestActivateProperty(string itemId, string propertyId)
        {
            try
            {
                await SendMessageAsync("activate_property", new { itemId, propertyId });
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to request activate property: {ex.Message}");
            }
        }

        /// <summary>
        /// Request to deactivate item property
        /// </summary>
        public async void RequestDeactivateProperty(string itemId, string propertyId)
        {
            try
            {
                await SendMessageAsync("deactivate_property", new { itemId, propertyId });
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to request deactivate property: {ex.Message}");
            }
        }

        /// <summary>
        /// Request to transfer item between players
        /// </summary>
        public async void RequestTransferItem(string fromPlayerId, string toPlayerId, string itemId)
        {
            try
            {
                await SendMessageAsync("transfer_item", new { fromPlayerId, toPlayerId, itemId });
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to request transfer item: {ex.Message}");
            }
        }

        #endregion
    }

    #region Message Data Classes

    [Serializable]
    public class InventoryUpdateMessage
    {
        public string PlayerId { get; set; }
        public InventoryDTO Inventory { get; set; }
    }

    [Serializable]
    public class ItemEquippedMessage
    {
        public string PlayerId { get; set; }
        public Models.Equipment Equipment { get; set; }
    }

    [Serializable]
    public class ItemUnequippedMessage
    {
        public string PlayerId { get; set; }
        public Models.Equipment Equipment { get; set; }
    }

    [Serializable]
    public class ItemDestroyedMessage
    {
        public string PlayerId { get; set; }
        public Models.Equipment Equipment { get; set; }
    }

    [Serializable]
    public class PropertyActivatedMessage
    {
        public string ItemId { get; set; }
        public EquipmentProperty Property { get; set; }
    }

    [Serializable]
    public class PropertyDeactivatedMessage
    {
        public string ItemId { get; set; }
        public string PropertyId { get; set; }
    }

    #endregion
} 