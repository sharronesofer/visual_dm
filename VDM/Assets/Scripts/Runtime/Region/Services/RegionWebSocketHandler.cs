using System.Collections.Generic;
using System;
using UnityEngine;
using VDM.Runtime.Region.Models;
using VDM.Runtime.WebSocket;


namespace VDM.Runtime.Region.Services
{
    /// <summary>
    /// WebSocket handler for real-time region updates
    /// </summary>
    public class RegionWebSocketHandler : MonoBehaviour
    {
        [Header("Configuration")]
        [SerializeField] private string webSocketUrl = "ws://localhost:8000/ws/regions";
        [SerializeField] private bool enableLogging = true;
        [SerializeField] private float reconnectDelay = 5f;

        // Events for region updates
        public event Action<RegionModel> OnRegionCreated;
        public event Action<RegionModel> OnRegionUpdated;
        public event Action<string> OnRegionDeleted;
        public event Action<string, WeatherForecast> OnWeatherUpdated;
        public event Action<string, List<POIModel>> OnPOIsUpdated;
        public event Action<string, List<SettlementModel>> OnSettlementsUpdated;
        public event Action<RegionAnalytics> OnAnalyticsUpdated;
        public event Action<string> OnError;

        private WebSocketService webSocketService;
        private bool isConnected = false;
        private List<string> subscribedRegions = new List<string>();

        private void Awake()
        {
            webSocketService = FindObjectOfType<WebSocketService>();
            if (webSocketService == null)
            {
                Debug.LogError("RegionWebSocketHandler requires WebSocketService to be present in the scene");
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
        /// Connect to the region WebSocket
        /// </summary>
        public void Connect()
        {
            if (webSocketService == null)
            {
                Debug.LogError("[RegionWebSocketHandler] WebSocketService not available");
                return;
            }

            if (isConnected)
            {
                Debug.LogWarning("[RegionWebSocketHandler] Already connected");
                return;
            }

            if (enableLogging)
                Debug.Log($"[RegionWebSocketHandler] Connecting to: {webSocketUrl}");

            webSocketService.Connect(webSocketUrl);
        }

        /// <summary>
        /// Disconnect from the region WebSocket
        /// </summary>
        public void Disconnect()
        {
            if (webSocketService == null || !isConnected)
                return;

            if (enableLogging)
                Debug.Log("[RegionWebSocketHandler] Disconnecting");

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
                Debug.Log("[RegionWebSocketHandler] Connected to region WebSocket");

            // Re-subscribe to any previously subscribed regions
            foreach (var regionId in subscribedRegions)
            {
                SubscribeToRegion(regionId);
            }
        }

        private void OnWebSocketDisconnected()
        {
            isConnected = false;
            if (enableLogging)
                Debug.Log("[RegionWebSocketHandler] Disconnected from region WebSocket");

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
                Debug.LogError($"[RegionWebSocketHandler] Error parsing message: {ex.Message}");
                OnError?.Invoke($"Message parsing error: {ex.Message}");
            }
        }

        private void OnWebSocketError(string error)
        {
            Debug.LogError($"[RegionWebSocketHandler] WebSocket error: {error}");
            OnError?.Invoke(error);
        }

        private void AttemptReconnect()
        {
            if (!isConnected)
            {
                if (enableLogging)
                    Debug.Log("[RegionWebSocketHandler] Attempting to reconnect...");
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
                Debug.Log($"[RegionWebSocketHandler] Received message: {message.type}");

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
                case "weather_updated":
                    HandleWeatherUpdated(message.data);
                    break;
                case "pois_updated":
                    HandlePOIsUpdated(message.data);
                    break;
                case "settlements_updated":
                    HandleSettlementsUpdated(message.data);
                    break;
                case "analytics_updated":
                    HandleAnalyticsUpdated(message.data);
                    break;
                case "error":
                    HandleError(message.data);
                    break;
                default:
                    Debug.LogWarning($"[RegionWebSocketHandler] Unknown message type: {message.type}");
                    break;
            }
        }

        private void HandleRegionCreated(string data)
        {
            try
            {
                var region = JsonUtility.FromJson<RegionModel>(data);
                OnRegionCreated?.Invoke(region);
            }
            catch (Exception ex)
            {
                Debug.LogError($"[RegionWebSocketHandler] Error handling region created: {ex.Message}");
            }
        }

        private void HandleRegionUpdated(string data)
        {
            try
            {
                var region = JsonUtility.FromJson<RegionModel>(data);
                OnRegionUpdated?.Invoke(region);
            }
            catch (Exception ex)
            {
                Debug.LogError($"[RegionWebSocketHandler] Error handling region updated: {ex.Message}");
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
                Debug.LogError($"[RegionWebSocketHandler] Error handling region deleted: {ex.Message}");
            }
        }

        private void HandleWeatherUpdated(string data)
        {
            try
            {
                var weatherData = JsonUtility.FromJson<WeatherUpdateData>(data);
                OnWeatherUpdated?.Invoke(weatherData.regionId, weatherData.forecast);
            }
            catch (Exception ex)
            {
                Debug.LogError($"[RegionWebSocketHandler] Error handling weather updated: {ex.Message}");
            }
        }

        private void HandlePOIsUpdated(string data)
        {
            try
            {
                var poisData = JsonUtility.FromJson<POIsUpdateData>(data);
                OnPOIsUpdated?.Invoke(poisData.regionId, poisData.pois);
            }
            catch (Exception ex)
            {
                Debug.LogError($"[RegionWebSocketHandler] Error handling POIs updated: {ex.Message}");
            }
        }

        private void HandleSettlementsUpdated(string data)
        {
            try
            {
                var settlementsData = JsonUtility.FromJson<SettlementsUpdateData>(data);
                OnSettlementsUpdated?.Invoke(settlementsData.regionId, settlementsData.settlements);
            }
            catch (Exception ex)
            {
                Debug.LogError($"[RegionWebSocketHandler] Error handling settlements updated: {ex.Message}");
            }
        }

        private void HandleAnalyticsUpdated(string data)
        {
            try
            {
                var analytics = JsonUtility.FromJson<RegionAnalytics>(data);
                OnAnalyticsUpdated?.Invoke(analytics);
            }
            catch (Exception ex)
            {
                Debug.LogError($"[RegionWebSocketHandler] Error handling analytics updated: {ex.Message}");
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
                Debug.LogError($"[RegionWebSocketHandler] Error handling error message: {ex.Message}");
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
                Debug.LogWarning("[RegionWebSocketHandler] Not connected, queuing subscription");
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
                Debug.Log($"[RegionWebSocketHandler] Subscribed to region: {regionId}");
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
                Debug.Log($"[RegionWebSocketHandler] Unsubscribed from region: {regionId}");
        }

        /// <summary>
        /// Subscribe to weather updates for all regions
        /// </summary>
        public void SubscribeToWeatherUpdates()
        {
            if (!isConnected)
            {
                Debug.LogWarning("[RegionWebSocketHandler] Not connected");
                return;
            }

            var subscribeMessage = new WebSocketMessage
            {
                type = "subscribe_weather",
                data = "{}"
            };

            SendMessage(subscribeMessage);

            if (enableLogging)
                Debug.Log("[RegionWebSocketHandler] Subscribed to weather updates");
        }

        /// <summary>
        /// Subscribe to analytics updates
        /// </summary>
        public void SubscribeToAnalytics()
        {
            if (!isConnected)
            {
                Debug.LogWarning("[RegionWebSocketHandler] Not connected");
                return;
            }

            var subscribeMessage = new WebSocketMessage
            {
                type = "subscribe_analytics",
                data = "{}"
            };

            SendMessage(subscribeMessage);

            if (enableLogging)
                Debug.Log("[RegionWebSocketHandler] Subscribed to analytics updates");
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
        private class WeatherUpdateData
        {
            public string regionId;
            public WeatherForecast forecast;
        }

        [Serializable]
        private class POIsUpdateData
        {
            public string regionId;
            public List<POIModel> pois;
        }

        [Serializable]
        private class SettlementsUpdateData
        {
            public string regionId;
            public List<SettlementModel> settlements;
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