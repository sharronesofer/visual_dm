using NativeWebSocket;
using System;
using System.Collections.Generic;
using UnityEngine;
using Newtonsoft.Json;
using VDM.Infrastructure.Services.Websocket;
using VDM.DTOs.Common;
using VDM.Systems.Character.Models;
using VDM.Infrastructure.Services;
using VDM.Systems.Worldstate.Models;


namespace VDM.Systems.Worldstate.Services
{
    /// <summary>
    /// WebSocket handler for real-time world state updates
    /// </summary>
    public class WorldStateWebSocketHandler : MonoBehaviour
    {
        [Header("Configuration")]
        [SerializeField] private string webSocketUrl = "ws://localhost:8000/ws/world-state";
        [SerializeField] private bool enableLogging = true;
        [SerializeField] private float reconnectDelay = 5f;

        // Events for world state updates
        public event Action<WorldRegion> OnRegionCreated;
        public event Action<WorldRegion> OnRegionUpdated;
        public event Action<string> OnRegionDeleted;
        public event Action<string, StateCategory, Dictionary<string, object>> OnRegionStateChanged;
        public event Action<WorldMap> OnMapCreated;
        public event Action<WorldMap> OnMapUpdated;
        public event Action<WorldStateSnapshot> OnSnapshotCreated;
        public event Action<StateChangeRecord> OnStateChangeRecorded;
        public event Action<string> OnError;

        private WebSocketService webSocketService;
        private bool isConnected = false;
        private List<string> subscribedRegions = new List<string>();
        private List<StateCategory> subscribedCategories = new List<StateCategory>();

        private void Awake()
        {
            webSocketService = FindObjectOfType<WebSocketService>();
            if (webSocketService == null)
            {
                Debug.LogError("WorldStateWebSocketHandler requires WebSocketService to be present in the scene");
            }
        }

        private void Start()
        {
            if (webSocketService != null)
            {
                SetupWebSocketEvents();
            }
        }

        private void OnDestroy()
        {
            if (webSocketService != null && isConnected)
            {
                Disconnect();
            }
        }

        #region Connection Management

        /// <summary>
        /// Connect to the world state WebSocket
        /// </summary>
        public void Connect()
        {
            if (webSocketService == null)
            {
                Debug.LogError("[WorldStateWebSocketHandler] WebSocketService not available");
                return;
            }

            if (isConnected)
            {
                Debug.LogWarning("[WorldStateWebSocketHandler] Already connected");
                return;
            }

            if (enableLogging)
                Debug.Log($"[WorldStateWebSocketHandler] Connecting to: {webSocketUrl}");

            webSocketService.Connect(webSocketUrl);
        }

        /// <summary>
        /// Disconnect from the world state WebSocket
        /// </summary>
        public void Disconnect()
        {
            if (webSocketService == null || !isConnected)
                return;

            if (enableLogging)
                Debug.Log("[WorldStateWebSocketHandler] Disconnecting");

            webSocketService.Disconnect();
            isConnected = false;
        }

        /// <summary>
        /// Setup WebSocket event handlers
        /// </summary>
        private void SetupWebSocketEvents()
        {
            webSocketService.OnConnected += OnWebSocketConnected;
            webSocketService.OnDisconnected += OnWebSocketDisconnected;
            webSocketService.OnMessage += OnWebSocketMessage;
            webSocketService.OnError += OnWebSocketError;
        }

        #endregion

        #region WebSocket Event Handlers

        private void OnWebSocketConnected()
        {
            isConnected = true;
            if (enableLogging)
                Debug.Log("[WorldStateWebSocketHandler] Connected to world state WebSocket");

            // Re-subscribe to any previously subscribed regions/categories
            foreach (var regionId in subscribedRegions)
            {
                SubscribeToRegion(regionId);
            }

            foreach (var category in subscribedCategories)
            {
                SubscribeToStateCategory(category);
            }
        }

        private void OnWebSocketDisconnected()
        {
            isConnected = false;
            if (enableLogging)
                Debug.Log("[WorldStateWebSocketHandler] Disconnected from world state WebSocket");

            // Attempt to reconnect after delay
            Invoke(nameof(AttemptReconnect), reconnectDelay);
        }

        private void OnWebSocketMessage(string message)
        {
            try
            {
                var messageData = JsonUtility.FromJson<WebSocketMessage>(message);
                HandleWebSocketMessage(messageData);
            }
            catch (Exception ex)
            {
                Debug.LogError($"[WorldStateWebSocketHandler] Error parsing message: {ex.Message}");
                OnError?.Invoke($"Message parsing error: {ex.Message}");
            }
        }

        private void OnWebSocketError(string error)
        {
            Debug.LogError($"[WorldStateWebSocketHandler] WebSocket error: {error}");
            OnError?.Invoke(error);
        }

        private void AttemptReconnect()
        {
            if (!isConnected)
            {
                if (enableLogging)
                    Debug.Log("[WorldStateWebSocketHandler] Attempting to reconnect...");
                Connect();
            }
        }

        #endregion

        #region Message Handling

        /// <summary>
        /// Handle incoming WebSocket messages
        /// </summary>
        private void HandleWebSocketMessage(WebSocketMessage message)
        {
            if (enableLogging)
                Debug.Log($"[WorldStateWebSocketHandler] Received message: {message.type}");

            switch (message.type)
            {
                case "region_created":
                    HandleRegionCreated(message.data);
                    break;
                case "region_updated":
                    HandleRegionUpdated(message.data);
                    break;
                case "region_deleted":
                    HandleRegionDeleted(message.data);
                    break;
                case "region_state_changed":
                    HandleRegionStateChanged(message.data);
                    break;
                case "map_created":
                    HandleMapCreated(message.data);
                    break;
                case "map_updated":
                    HandleMapUpdated(message.data);
                    break;
                case "snapshot_created":
                    HandleSnapshotCreated(message.data);
                    break;
                case "state_change_recorded":
                    HandleStateChangeRecorded(message.data);
                    break;
                case "error":
                    HandleError(message.data);
                    break;
                default:
                    Debug.LogWarning($"[WorldStateWebSocketHandler] Unknown message type: {message.type}");
                    break;
            }
        }

        private void HandleRegionCreated(string data)
        {
            try
            {
                var region = JsonUtility.FromJson<WorldRegion>(data);
                OnRegionCreated?.Invoke(region);
            }
            catch (Exception ex)
            {
                Debug.LogError($"[WorldStateWebSocketHandler] Error handling region created: {ex.Message}");
            }
        }

        private void HandleRegionUpdated(string data)
        {
            try
            {
                var region = JsonUtility.FromJson<WorldRegion>(data);
                OnRegionUpdated?.Invoke(region);
            }
            catch (Exception ex)
            {
                Debug.LogError($"[WorldStateWebSocketHandler] Error handling region updated: {ex.Message}");
            }
        }

        private void HandleRegionDeleted(string data)
        {
            try
            {
                var deleteData = JsonUtility.FromJson<RegionDeletedData>(data);
                OnRegionDeleted?.Invoke(deleteData.regionId);
            }
            catch (Exception ex)
            {
                Debug.LogError($"[WorldStateWebSocketHandler] Error handling region deleted: {ex.Message}");
            }
        }

        private void HandleRegionStateChanged(string data)
        {
            try
            {
                var stateChangeData = JsonUtility.FromJson<RegionStateChangeData>(data);
                OnRegionStateChanged?.Invoke(stateChangeData.regionId, stateChangeData.category, stateChangeData.state);
            }
            catch (Exception ex)
            {
                Debug.LogError($"[WorldStateWebSocketHandler] Error handling region state changed: {ex.Message}");
            }
        }

        private void HandleMapCreated(string data)
        {
            try
            {
                var map = JsonUtility.FromJson<WorldMap>(data);
                OnMapCreated?.Invoke(map);
            }
            catch (Exception ex)
            {
                Debug.LogError($"[WorldStateWebSocketHandler] Error handling map created: {ex.Message}");
            }
        }

        private void HandleMapUpdated(string data)
        {
            try
            {
                var map = JsonUtility.FromJson<WorldMap>(data);
                OnMapUpdated?.Invoke(map);
            }
            catch (Exception ex)
            {
                Debug.LogError($"[WorldStateWebSocketHandler] Error handling map updated: {ex.Message}");
            }
        }

        private void HandleSnapshotCreated(string data)
        {
            try
            {
                var snapshot = JsonUtility.FromJson<WorldStateSnapshot>(data);
                OnSnapshotCreated?.Invoke(snapshot);
            }
            catch (Exception ex)
            {
                Debug.LogError($"[WorldStateWebSocketHandler] Error handling snapshot created: {ex.Message}");
            }
        }

        private void HandleStateChangeRecorded(string data)
        {
            try
            {
                var stateChange = JsonUtility.FromJson<StateChangeRecord>(data);
                OnStateChangeRecorded?.Invoke(stateChange);
            }
            catch (Exception ex)
            {
                Debug.LogError($"[WorldStateWebSocketHandler] Error handling state change recorded: {ex.Message}");
            }
        }

        private void HandleError(string data)
        {
            try
            {
                var errorData = JsonUtility.FromJson<ErrorData>(data);
                OnError?.Invoke(errorData.message);
            }
            catch (Exception ex)
            {
                Debug.LogError($"[WorldStateWebSocketHandler] Error handling error message: {ex.Message}");
            }
        }

        #endregion

        #region Subscription Management

        /// <summary>
        /// Subscribe to updates for a specific region
        /// </summary>
        public void SubscribeToRegion(string regionId)
        {
            if (!isConnected)
            {
                Debug.LogWarning("[WorldStateWebSocketHandler] Not connected, queuing subscription");
                if (!subscribedRegions.Contains(regionId))
                {
                    subscribedRegions.Add(regionId);
                }
                return;
            }

            var subscribeMessage = new WebSocketMessage
            {
                type = "subscribe_region",
                data = JsonUtility.ToJson(new { regionId = regionId })
            };

            SendMessage(subscribeMessage);

            if (!subscribedRegions.Contains(regionId))
            {
                subscribedRegions.Add(regionId);
            }

            if (enableLogging)
                Debug.Log($"[WorldStateWebSocketHandler] Subscribed to region: {regionId}");
        }

        /// <summary>
        /// Unsubscribe from updates for a specific region
        /// </summary>
        public void UnsubscribeFromRegion(string regionId)
        {
            if (!isConnected)
            {
                subscribedRegions.Remove(regionId);
                return;
            }

            var unsubscribeMessage = new WebSocketMessage
            {
                type = "unsubscribe_region",
                data = JsonUtility.ToJson(new { regionId = regionId })
            };

            SendMessage(unsubscribeMessage);
            subscribedRegions.Remove(regionId);

            if (enableLogging)
                Debug.Log($"[WorldStateWebSocketHandler] Unsubscribed from region: {regionId}");
        }

        /// <summary>
        /// Subscribe to updates for a specific state category
        /// </summary>
        public void SubscribeToStateCategory(StateCategory category)
        {
            if (!isConnected)
            {
                Debug.LogWarning("[WorldStateWebSocketHandler] Not connected, queuing subscription");
                if (!subscribedCategories.Contains(category))
                {
                    subscribedCategories.Add(category);
                }
                return;
            }

            var subscribeMessage = new WebSocketMessage
            {
                type = "subscribe_category",
                data = JsonUtility.ToJson(new { category = category.ToString() })
            };

            SendMessage(subscribeMessage);

            if (!subscribedCategories.Contains(category))
            {
                subscribedCategories.Add(category);
            }

            if (enableLogging)
                Debug.Log($"[WorldStateWebSocketHandler] Subscribed to category: {category}");
        }

        /// <summary>
        /// Unsubscribe from updates for a specific state category
        /// </summary>
        public void UnsubscribeFromStateCategory(StateCategory category)
        {
            if (!isConnected)
            {
                subscribedCategories.Remove(category);
                return;
            }

            var unsubscribeMessage = new WebSocketMessage
            {
                type = "unsubscribe_category",
                data = JsonUtility.ToJson(new { category = category.ToString() })
            };

            SendMessage(unsubscribeMessage);
            subscribedCategories.Remove(category);

            if (enableLogging)
                Debug.Log($"[WorldStateWebSocketHandler] Unsubscribed from category: {category}");
        }

        #endregion

        #region Utility Methods

        /// <summary>
        /// Send a message through the WebSocket
        /// </summary>
        private void SendMessage(WebSocketMessage message)
        {
            if (webSocketService != null && isConnected)
            {
                var json = JsonUtility.ToJson(message);
                webSocketService.SendMessage(json);
            }
        }

        /// <summary>
        /// Get connection status
        /// </summary>
        public bool IsConnected => isConnected;

        /// <summary>
        /// Get list of subscribed regions
        /// </summary>
        public List<string> GetSubscribedRegions() => new List<string>(subscribedRegions);

        /// <summary>
        /// Get list of subscribed categories
        /// </summary>
        public List<StateCategory> GetSubscribedCategories() => new List<StateCategory>(subscribedCategories);

        #endregion

        #region Data Classes

        [Serializable]
        private class WebSocketMessage
        {
            public string type;
            public string data;
        }

        [Serializable]
        private class RegionDeletedData
        {
            public string regionId;
        }

        [Serializable]
        private class RegionStateChangeData
        {
            public string regionId;
            public StateCategory category;
            public Dictionary<string, object> state;
        }

        [Serializable]
        private class ErrorData
        {
            public string message;
            public string code;
        }

        #endregion
    }
} 