using NativeWebSocket;
using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using UnityEngine;
using Newtonsoft.Json;
using VDM.Systems.Chaos.Models;
using VDM.Infrastructure.Services;

namespace VDM.Systems.Chaos.Services
{
    /// <summary>
    /// Service for communicating with the backend chaos system API
    /// Handles both HTTP requests and WebSocket real-time updates
    /// </summary>
    public class ChaosService : MonoBehaviour
    {
        [Header("Configuration")]
        [SerializeField] private string chaosApiBaseUrl = "http://localhost:8000/api/chaos";
        [SerializeField] private string chaosWebSocketUrl = "ws://localhost:8000/ws/chaos";
        [SerializeField] private float updateInterval = 5.0f;
        [SerializeField] private bool autoConnectWebSocket = true;
        [SerializeField] private int maxRetries = 3;

        [Header("Authentication")]
        [SerializeField] private bool requiresAuthentication = true;
        [SerializeField] private string adminApiKey = "";

        private HttpService httpService;
        private OptimizedWebSocketClient webSocketClient;
        private bool isConnected = false;
        private bool isInitialized = false;

        // Events for UI components to subscribe to
        public event Action<ChaosEventDTO> OnChaosEventTriggered;
        public event Action<ChaosMetricsDTO> OnMetricsUpdated;
        public event Action<PressureSourceDTO> OnPressureUpdated;
        public event Action<ChaosConfigurationDTO> OnConfigurationUpdated;
        public event Action<ChaosAlert> OnAlertReceived;
        public event Action<bool> OnConnectionStatusChanged;
        public event Action<string> OnError;

        private void Awake()
        {
            InitializeService();
        }

        private void Start()
        {
            if (autoConnectWebSocket)
            {
                ConnectWebSocket();
            }
        }

        private void OnDestroy()
        {
            DisconnectWebSocket();
        }

        /// <summary>
        /// Initialize the chaos service
        /// </summary>
        private void InitializeService()
        {
            httpService = FindObjectOfType<HttpService>();
            if (httpService == null)
            {
                Debug.LogError("ChaosService: HttpService not found. Please ensure HttpService is present in the scene.");
                return;
            }

            webSocketClient = FindObjectOfType<OptimizedWebSocketClient>();
            if (webSocketClient == null)
            {
                Debug.LogError("ChaosService: WebSocketClient not found. Please ensure WebSocketClient is present in the scene.");
                return;
            }

            isInitialized = true;
            Debug.Log("ChaosService initialized successfully");
        }

        /// <summary>
        /// Connect to the chaos WebSocket for real-time updates
        /// </summary>
        public async Task<bool> ConnectWebSocket()
        {
            if (!isInitialized)
            {
                OnError?.Invoke("ChaosService not properly initialized");
                return false;
            }

            try
            {
                webSocketClient.SetServerUrl(chaosWebSocketUrl);
                webSocketClient.Connect();
                
                // Subscribe to WebSocket events
                webSocketClient.OnMessageReceived += HandleWebSocketMessage;
                webSocketClient.OnConnected += () => HandleConnectionStateChanged(true);
                webSocketClient.OnDisconnected += (reason) => HandleConnectionStateChanged(false);
                webSocketClient.OnError += HandleWebSocketError;

                // Wait a moment for connection to establish
                await Task.Delay(1000);
                
                isConnected = webSocketClient.IsConnected;
                OnConnectionStatusChanged?.Invoke(isConnected);
                Debug.Log("ChaosService: WebSocket connected successfully");
                return isConnected;
            }
            catch (Exception ex)
            {
                Debug.LogError($"ChaosService: Failed to connect WebSocket: {ex.Message}");
                OnError?.Invoke($"WebSocket connection failed: {ex.Message}");
                return false;
            }
        }

        /// <summary>
        /// Disconnect from the chaos WebSocket
        /// </summary>
        public void DisconnectWebSocket()
        {
            if (webSocketClient != null)
            {
                webSocketClient.OnMessageReceived -= HandleWebSocketMessage;
                webSocketClient.OnConnected -= () => HandleConnectionStateChanged(true);
                webSocketClient.OnDisconnected -= (reason) => HandleConnectionStateChanged(false);
                webSocketClient.OnError -= HandleWebSocketError;
                webSocketClient.Disconnect();
            }

            isConnected = false;
            OnConnectionStatusChanged?.Invoke(false);
            Debug.Log("ChaosService: WebSocket disconnected");
        }

        // HTTP API Methods

        /// <summary>
        /// Get current chaos metrics
        /// </summary>
        public async Task<ChaosMetricsDTO> GetMetricsAsync()
        {
            try
            {
                var response = await httpService.GetAsync($"{chaosApiBaseUrl}/metrics");
                if (response.IsSuccess)
                {
                    return JsonConvert.DeserializeObject<ChaosMetricsDTO>(response.Data);
                }
                else
                {
                    OnError?.Invoke($"Failed to get metrics: {response.Error}");
                    return null;
                }
            }
            catch (Exception ex)
            {
                OnError?.Invoke($"Error getting metrics: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Get all pressure sources
        /// </summary>
        public async Task<List<PressureSourceDTO>> GetPressureSourcesAsync()
        {
            try
            {
                var response = await httpService.GetAsync($"{chaosApiBaseUrl}/pressure-sources");
                if (response.IsSuccess)
                {
                    return JsonConvert.DeserializeObject<List<PressureSourceDTO>>(response.Data);
                }
                else
                {
                    OnError?.Invoke($"Failed to get pressure sources: {response.Error}");
                    return new List<PressureSourceDTO>();
                }
            }
            catch (Exception ex)
            {
                OnError?.Invoke($"Error getting pressure sources: {ex.Message}");
                return new List<PressureSourceDTO>();
            }
        }

        /// <summary>
        /// Get chaos events with optional filtering
        /// </summary>
        public async Task<List<ChaosEventDTO>> GetEventsAsync(int limit = 100, string status = null, string regionId = null)
        {
            try
            {
                var queryParams = new List<string>();
                if (limit > 0) queryParams.Add($"limit={limit}");
                if (!string.IsNullOrEmpty(status)) queryParams.Add($"status={status}");
                if (!string.IsNullOrEmpty(regionId)) queryParams.Add($"region_id={regionId}");

                var queryString = queryParams.Count > 0 ? "?" + string.Join("&", queryParams) : "";
                var response = await httpService.GetAsync($"{chaosApiBaseUrl}/events{queryString}");

                if (response.IsSuccess)
                {
                    return JsonConvert.DeserializeObject<List<ChaosEventDTO>>(response.Data);
                }
                else
                {
                    OnError?.Invoke($"Failed to get events: {response.Error}");
                    return new List<ChaosEventDTO>();
                }
            }
            catch (Exception ex)
            {
                OnError?.Invoke($"Error getting events: {ex.Message}");
                return new List<ChaosEventDTO>();
            }
        }

        /// <summary>
        /// Get historical chaos data
        /// </summary>
        public async Task<ChaosHistoryDTO> GetHistoryAsync(DateTime startTime, DateTime endTime, string regionId = null)
        {
            try
            {
                var queryParams = new List<string>
                {
                    $"start_time={startTime:yyyy-MM-ddTHH:mm:ssZ}",
                    $"end_time={endTime:yyyy-MM-ddTHH:mm:ssZ}"
                };

                if (!string.IsNullOrEmpty(regionId))
                    queryParams.Add($"region_id={regionId}");

                var queryString = "?" + string.Join("&", queryParams);
                var response = await httpService.GetAsync($"{chaosApiBaseUrl}/history{queryString}");

                if (response.IsSuccess)
                {
                    return JsonConvert.DeserializeObject<ChaosHistoryDTO>(response.Data);
                }
                else
                {
                    OnError?.Invoke($"Failed to get history: {response.Error}");
                    return null;
                }
            }
            catch (Exception ex)
            {
                OnError?.Invoke($"Error getting history: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Get chaos system configuration (admin only)
        /// </summary>
        public async Task<ChaosConfigurationDTO> GetConfigurationAsync()
        {
            try
            {
                var response = await httpService.GetAsync($"{chaosApiBaseUrl}/admin/configuration");
                if (response.IsSuccess)
                {
                    return JsonConvert.DeserializeObject<ChaosConfigurationDTO>(response.Data);
                }
                else
                {
                    OnError?.Invoke($"Failed to get configuration: {response.Error}");
                    return null;
                }
            }
            catch (Exception ex)
            {
                OnError?.Invoke($"Error getting configuration: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Update chaos system configuration (admin only)
        /// </summary>
        public async Task<bool> UpdateConfigurationAsync(ChaosConfigurationDTO configuration)
        {
            try
            {
                var response = await httpService.PutAsync($"{chaosApiBaseUrl}/admin/configuration", configuration);
                if (response.IsSuccess)
                {
                    Debug.Log("ChaosService: Configuration updated successfully");
                    return true;
                }
                else
                {
                    OnError?.Invoke($"Failed to update configuration: {response.Error}");
                    return false;
                }
            }
            catch (Exception ex)
            {
                OnError?.Invoke($"Error updating configuration: {ex.Message}");
                return false;
            }
        }

        /// <summary>
        /// Trigger a manual chaos event (admin only, for testing)
        /// </summary>
        public async Task<bool> TriggerEventAsync(string eventType, string regionId, float intensity, Dictionary<string, object> eventData = null)
        {
            try
            {
                var request = new
                {
                    EventType = eventType,
                    RegionId = regionId,
                    Intensity = intensity,
                    EventData = eventData ?? new Dictionary<string, object>(),
                    TriggeredBy = "Admin",
                    IsManual = true
                };

                var response = await httpService.PostAsync($"{chaosApiBaseUrl}/admin/trigger-event", request);
                if (response.IsSuccess)
                {
                    Debug.Log($"ChaosService: Event triggered successfully: {eventType}");
                    return true;
                }
                else
                {
                    OnError?.Invoke($"Failed to trigger event: {response.Error}");
                    return false;
                }
            }
            catch (Exception ex)
            {
                OnError?.Invoke($"Error triggering event: {ex.Message}");
                return false;
            }
        }

        /// <summary>
        /// Acknowledge an alert
        /// </summary>
        public async Task<bool> AcknowledgeAlertAsync(string alertId)
        {
            try
            {
                var response = await httpService.PostAsync($"{chaosApiBaseUrl}/alerts/{alertId}/acknowledge", new { });
                if (response.IsSuccess)
                {
                    Debug.Log($"ChaosService: Alert acknowledged: {alertId}");
                    return true;
                }
                else
                {
                    OnError?.Invoke($"Failed to acknowledge alert: {response.Error}");
                    return false;
                }
            }
            catch (Exception ex)
            {
                OnError?.Invoke($"Error acknowledging alert: {ex.Message}");
                return false;
            }
        }

        // WebSocket Event Handlers

        private void HandleWebSocketMessage(WebSocketMessage message)
        {
            try
            {
                // Convert the message data to string if needed
                string messageData = message.Data?.ToString() ?? string.Empty;
                var update = JsonConvert.DeserializeObject<ChaosUpdateDTO>(messageData);
                ProcessChaosUpdate(update);
            }
            catch (Exception ex)
            {
                Debug.LogError($"ChaosService: Failed to process WebSocket message: {ex.Message}");
                OnError?.Invoke($"Failed to process update: {ex.Message}");
            }
        }

        private void HandleConnectionStateChanged(bool connected)
        {
            isConnected = connected;
            OnConnectionStatusChanged?.Invoke(connected);
            
            if (connected)
            {
                Debug.Log("ChaosService: WebSocket connection established");
            }
            else
            {
                Debug.LogWarning("ChaosService: WebSocket connection lost");
            }
        }

        private void HandleWebSocketError(string error)
        {
            Debug.LogError($"ChaosService: WebSocket error: {error}");
            OnError?.Invoke($"WebSocket error: {error}");
        }

        /// <summary>
        /// Process real-time chaos updates from WebSocket
        /// </summary>
        private void ProcessChaosUpdate(ChaosUpdateDTO update)
        {
            switch (update.UpdateType)
            {
                case ChaosUpdateType.EventTriggered:
                    var eventData = JsonConvert.DeserializeObject<ChaosEventDTO>(JsonConvert.SerializeObject(update.UpdateData));
                    OnChaosEventTriggered?.Invoke(eventData);
                    break;

                case ChaosUpdateType.MetricsUpdate:
                    var metricsData = JsonConvert.DeserializeObject<ChaosMetricsDTO>(JsonConvert.SerializeObject(update.UpdateData));
                    OnMetricsUpdated?.Invoke(metricsData);
                    break;

                case ChaosUpdateType.PressureUpdate:
                    var pressureData = JsonConvert.DeserializeObject<PressureSourceDTO>(JsonConvert.SerializeObject(update.UpdateData));
                    OnPressureUpdated?.Invoke(pressureData);
                    break;

                case ChaosUpdateType.ConfigurationChanged:
                    var configData = JsonConvert.DeserializeObject<ChaosConfigurationDTO>(JsonConvert.SerializeObject(update.UpdateData));
                    OnConfigurationUpdated?.Invoke(configData);
                    break;

                case ChaosUpdateType.SystemAlert:
                    var alertData = JsonConvert.DeserializeObject<ChaosAlert>(JsonConvert.SerializeObject(update.UpdateData));
                    OnAlertReceived?.Invoke(alertData);
                    break;

                default:
                    Debug.LogWarning($"ChaosService: Unhandled update type: {update.UpdateType}");
                    break;
            }
        }

        // Public Properties

        public bool IsConnected => isConnected;
        public bool IsInitialized => isInitialized;
        public string ApiBaseUrl => chaosApiBaseUrl;
        public float UpdateInterval => updateInterval;
    }
} 