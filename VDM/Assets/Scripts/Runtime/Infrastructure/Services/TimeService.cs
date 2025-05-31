using NativeWebSocket;
using Newtonsoft.Json;
using System.Collections.Generic;
using System.Collections;
using System.Threading.Tasks;
using System;
using UnityEngine;
using VDM.Systems.Time.Models;
using VDM.Infrastructure.Services;


namespace VDM.Infrastructure.Services
{
    /// <summary>
    /// Time synchronization service that handles communication with backend time system
    /// Implements the canonical time synchronization protocol from Development Bible
    /// </summary>
    public class TimeService : MonoBehaviour
    {
        private static TimeService _instance;
        public static TimeService Instance
        {
            get
            {
                if (_instance == null)
                {
                    GameObject go = new GameObject("TimeService");
                    _instance = go.AddComponent<TimeService>();
                    DontDestroyOnLoad(go);
                }
                return _instance;
            }
        }

        [Header("Configuration")]
        [SerializeField] private string baseUrl = "http://localhost:8000";
        [SerializeField] private string websocketUrl = "ws://localhost:8000/ws";
        [SerializeField] private float syncInterval = 30f; // Sync every 30 seconds
        [SerializeField] private bool enableAutoSync = true;
        [SerializeField] private bool enableWebSocketUpdates = true;

        [Header("Time Settings")]
        [SerializeField] private bool serverTimeAuthority = true; // True = server is time authority
        [SerializeField] private float timeSyncTolerance = 5f; // Seconds of acceptable drift

        // Client references
        private BaseHTTPClient httpClient;
        private MockServerWebSocket webSocketClient;
        private TimeSystemFacade timeSystemFacade;

        // State management
        private bool isInitialized = false;
        private bool isSyncing = false;
        private DateTime lastSyncTime = DateTime.MinValue;
        private float nextSyncCountdown = 0f;

        // Events for time synchronization
        public event Action<GameTimeDTO> OnTimeReceived;
        public event Action<TimeScaleChangedEvent> OnTimeScaleChanged;
        public event Action<bool> OnSyncStatusChanged;
        public event Action<string> OnSyncError;

        // Time synchronization data
        private GameTimeDTO lastServerTime;
        private float serverTimeScale = 1.0f;
        private bool serverTimePaused = false;

        private void Awake()
        {
            if (_instance == null)
            {
                _instance = this;
                DontDestroyOnLoad(gameObject);
            }
            else if (_instance != this)
            {
                Destroy(gameObject);
                return;
            }
        }

        private void Start()
        {
            InitializeAsync();
        }

        private void Update()
        {
            if (!isInitialized || !enableAutoSync)
                return;

            // Handle periodic sync
            nextSyncCountdown -= Time.deltaTime;
            if (nextSyncCountdown <= 0f)
            {
                nextSyncCountdown = syncInterval;
                StartCoroutine(SyncTimeWithServer());
            }
        }

        /// <summary>
        /// Initialize the time service with dependencies
        /// </summary>
        public async void InitializeAsync()
        {
            try
            {
                // Find required components
                timeSystemFacade = FindObjectOfType<TimeSystemFacade>();
                if (timeSystemFacade == null)
                {
                    Debug.LogError("TimeService: TimeSystemFacade not found!");
                    return;
                }

                // Initialize HTTP client
                httpClient = BaseHTTPClient.Instance;
                if (httpClient == null)
                {
                    Debug.LogError("TimeService: BaseHTTPClient not available!");
                    return;
                }

                // Initialize WebSocket client if enabled
                if (enableWebSocketUpdates)
                {
                    await InitializeWebSocketConnection();
                }

                // Perform initial sync
                await SyncTimeWithServerAsync();

                isInitialized = true;
                Debug.Log("TimeService: Initialized successfully");

                OnSyncStatusChanged?.Invoke(true);
            }
            catch (Exception ex)
            {
                Debug.LogError($"TimeService: Initialization failed - {ex.Message}");
                OnSyncError?.Invoke($"Initialization failed: {ex.Message}");
            }
        }

        /// <summary>
        /// Initialize WebSocket connection for real-time time updates
        /// </summary>
        private async Task InitializeWebSocketConnection()
        {
            try
            {
                // Find or create WebSocket client
                webSocketClient = FindObjectOfType<MockServerWebSocket>();
                if (webSocketClient == null)
                {
                    GameObject wsGo = new GameObject("TimeServiceWebSocket");
                    wsGo.transform.SetParent(transform);
                    webSocketClient = wsGo.AddComponent<MockServerWebSocket>();
                }

                // Subscribe to WebSocket events
                webSocketClient.OnConnected += OnWebSocketConnected;
                webSocketClient.OnDisconnected += OnWebSocketDisconnected;
                webSocketClient.OnMessageReceived += OnWebSocketMessageReceived;

                // Connect to WebSocket
                await webSocketClient.ConnectAsync(websocketUrl);

                Debug.Log("TimeService: WebSocket connection established");
            }
            catch (Exception ex)
            {
                Debug.LogError($"TimeService: WebSocket initialization failed - {ex.Message}");
                enableWebSocketUpdates = false; // Fallback to HTTP polling
            }
        }

        /// <summary>
        /// Synchronize time with server using HTTP
        /// </summary>
        public async Task SyncTimeWithServerAsync()
        {
            if (isSyncing) return;

            isSyncing = true;
            OnSyncStatusChanged?.Invoke(true);

            try
            {
                // Get current time from server
                var response = await httpClient.GetAsync<TimeSystemStatusDTO>("/api/time/current");
                
                if (response != null && response.Success)
                {
                    ProcessServerTimeUpdate(response.Data.CurrentTime);
                    lastSyncTime = DateTime.UtcNow;
                    Debug.Log($"TimeService: Successfully synced with server time: {response.Data.CurrentTime}");
                }
                else
                {
                    Debug.LogWarning("TimeService: Failed to get time from server");
                    OnSyncError?.Invoke("Failed to get time from server");
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"TimeService: Time sync failed - {ex.Message}");
                OnSyncError?.Invoke($"Time sync failed: {ex.Message}");
            }
            finally
            {
                isSyncing = false;
                OnSyncStatusChanged?.Invoke(false);
            }
        }

        /// <summary>
        /// Synchronize time with server using coroutine
        /// </summary>
        public IEnumerator SyncTimeWithServer()
        {
            var task = SyncTimeWithServerAsync();
            yield return new WaitUntil(() => task.IsCompleted);
        }

        /// <summary>
        /// Process time update from server
        /// </summary>
        private void ProcessServerTimeUpdate(GameTimeDTO serverTime)
        {
            if (serverTime == null) return;

            lastServerTime = serverTime;

            // Apply server time if server has authority
            if (serverTimeAuthority)
            {
                ApplyServerTimeToUnity(serverTime);
            }
            else
            {
                // Check for significant drift and warn
                CheckTimeDrift(serverTime);
            }

            OnTimeReceived?.Invoke(serverTime);
        }

        /// <summary>
        /// Apply server time to Unity time system
        /// </summary>
        private void ApplyServerTimeToUnity(GameTimeDTO serverTime)
        {
            if (timeSystemFacade == null) return;

            try
            {
                // Convert to Unity DateTime
                var unityTime = new DateTime(
                    serverTime.Year,
                    serverTime.Month,
                    serverTime.Day,
                    serverTime.Hour,
                    serverTime.Minute,
                    serverTime.Second
                );

                // Update Unity time system
                timeSystemFacade.CurrentTime = unityTime;
                
                // Update time scale if different
                if (Math.Abs(timeSystemFacade.TimeScale - serverTime.TimeScale) > 0.01f)
                {
                    timeSystemFacade.TimeScale = serverTime.TimeScale;
                }

                // Update pause state
                if (timeSystemFacade.IsPaused != serverTime.IsPaused)
                {
                    timeSystemFacade.SetPaused(serverTime.IsPaused);
                }

                Debug.Log($"TimeService: Applied server time to Unity: {unityTime}");
            }
            catch (Exception ex)
            {
                Debug.LogError($"TimeService: Failed to apply server time - {ex.Message}");
            }
        }

        /// <summary>
        /// Check for time drift between Unity and server
        /// </summary>
        private void CheckTimeDrift(GameTimeDTO serverTime)
        {
            if (timeSystemFacade == null) return;

            var unityTime = timeSystemFacade.CurrentTime;
            var serverDateTime = new DateTime(
                serverTime.Year,
                serverTime.Month,
                serverTime.Day,
                serverTime.Hour,
                serverTime.Minute,
                serverTime.Second
            );

            var drift = Math.Abs((unityTime - serverDateTime).TotalSeconds);
            
            if (drift > timeSyncTolerance)
            {
                Debug.LogWarning($"TimeService: Time drift detected - Unity: {unityTime}, Server: {serverDateTime}, Drift: {drift:F2}s");
                OnSyncError?.Invoke($"Time drift detected: {drift:F2} seconds");
            }
        }

        /// <summary>
        /// Send time advance request to server
        /// </summary>
        public async Task AdvanceTimeOnServer(int amount, TimeUnitDTO unit)
        {
            try
            {
                var request = new AdvanceTimeRequestDTO
                {
                    Amount = amount,
                    Unit = unit,
                    ForceAdvance = false,
                    TriggerEvents = true,
                    UpdateWeather = true
                };

                var response = await httpClient.PostAsync<AdvanceTimeRequestDTO, TimeSystemStatusDTO>("/api/time/advance", request);
                
                if (response != null && response.Success)
                {
                    Debug.Log($"TimeService: Successfully advanced server time by {amount} {unit}");
                    ProcessServerTimeUpdate(response.Data.CurrentTime);
                }
                else
                {
                    Debug.LogError("TimeService: Failed to advance server time");
                    OnSyncError?.Invoke("Failed to advance server time");
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"TimeService: Time advance failed - {ex.Message}");
                OnSyncError?.Invoke($"Time advance failed: {ex.Message}");
            }
        }

        /// <summary>
        /// Set time scale on server
        /// </summary>
        public async Task SetTimeScaleOnServer(float scale)
        {
            try
            {
                var response = await httpClient.PostAsync($"/api/time/scale?scale={scale}");
                
                if (response != null && response.Success)
                {
                    serverTimeScale = scale;
                    Debug.Log($"TimeService: Successfully set server time scale to {scale}");
                }
                else
                {
                    Debug.LogError("TimeService: Failed to set server time scale");
                    OnSyncError?.Invoke("Failed to set server time scale");
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"TimeService: Time scale update failed - {ex.Message}");
                OnSyncError?.Invoke($"Time scale update failed: {ex.Message}");
            }
        }

        /// <summary>
        /// Pause/resume time on server
        /// </summary>
        public async Task SetTimePausedOnServer(bool paused)
        {
            try
            {
                string endpoint = paused ? "/api/time/progression/pause" : "/api/time/progression/resume";
                var response = await httpClient.PostAsync(endpoint);
                
                if (response != null && response.Success)
                {
                    serverTimePaused = paused;
                    Debug.Log($"TimeService: Successfully {(paused ? "paused" : "resumed")} server time");
                }
                else
                {
                    Debug.LogError($"TimeService: Failed to {(paused ? "pause" : "resume")} server time");
                    OnSyncError?.Invoke($"Failed to {(paused ? "pause" : "resume")} server time");
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"TimeService: Time pause/resume failed - {ex.Message}");
                OnSyncError?.Invoke($"Time pause/resume failed: {ex.Message}");
            }
        }

        #region WebSocket Event Handlers

        private void OnWebSocketConnected()
        {
            Debug.Log("TimeService: WebSocket connected");
            
            // Send initial time sync request
            var message = new
            {
                type = "time_sync_request",
                timestamp = DateTime.UtcNow.ToString("O"),
                requestId = Guid.NewGuid().ToString(),
                version = "1.0"
            };
            
            webSocketClient.SendMessage(JsonConvert.SerializeObject(message));
        }

        private void OnWebSocketDisconnected()
        {
            Debug.Log("TimeService: WebSocket disconnected");
            OnSyncStatusChanged?.Invoke(false);
        }

        private void OnWebSocketMessageReceived(string message)
        {
            try
            {
                var jsonMessage = JsonConvert.DeserializeObject<Dictionary<string, object>>(message);
                
                if (jsonMessage.TryGetValue("type", out var typeObj))
                {
                    string messageType = typeObj.ToString();
                    
                    switch (messageType)
                    {
                        case "time_update":
                            HandleTimeUpdateMessage(jsonMessage);
                            break;
                        case "time_scale_changed":
                            HandleTimeScaleChangeMessage(jsonMessage);
                            break;
                        case "time_paused":
                        case "time_resumed":
                            HandleTimePauseMessage(jsonMessage, messageType == "time_paused");
                            break;
                        case "pong":
                            // Heartbeat response
                            break;
                        default:
                            Debug.Log($"TimeService: Unknown WebSocket message type: {messageType}");
                            break;
                    }
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"TimeService: WebSocket message processing failed - {ex.Message}");
            }
        }

        private void HandleTimeUpdateMessage(Dictionary<string, object> message)
        {
            try
            {
                if (message.TryGetValue("payload", out var payloadObj))
                {
                    var payloadStr = JsonConvert.SerializeObject(payloadObj);
                    var gameTime = JsonConvert.DeserializeObject<GameTimeDTO>(payloadStr);
                    
                    if (gameTime != null)
                    {
                        ProcessServerTimeUpdate(gameTime);
                    }
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"TimeService: Time update message processing failed - {ex.Message}");
            }
        }

        private void HandleTimeScaleChangeMessage(Dictionary<string, object> message)
        {
            try
            {
                if (message.TryGetValue("payload", out var payloadObj))
                {
                    var payloadDict = JsonConvert.DeserializeObject<Dictionary<string, object>>(JsonConvert.SerializeObject(payloadObj));
                    
                    if (payloadDict.TryGetValue("scale", out var scaleObj) && float.TryParse(scaleObj.ToString(), out float scale))
                    {
                        serverTimeScale = scale;
                        
                        if (serverTimeAuthority && timeSystemFacade != null)
                        {
                            timeSystemFacade.TimeScale = scale;
                        }
                        
                        var eventData = new TimeScaleChangedEvent
                        {
                            NewScale = scale,
                            OldScale = timeSystemFacade?.TimeScale ?? 1.0f,
                            Timestamp = DateTime.UtcNow
                        };
                        
                        OnTimeScaleChanged?.Invoke(eventData);
                    }
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"TimeService: Time scale change message processing failed - {ex.Message}");
            }
        }

        private void HandleTimePauseMessage(Dictionary<string, object> message, bool paused)
        {
            try
            {
                serverTimePaused = paused;
                
                if (serverTimeAuthority && timeSystemFacade != null)
                {
                    timeSystemFacade.SetPaused(paused);
                }
                
                Debug.Log($"TimeService: Server time {(paused ? "paused" : "resumed")}");
            }
            catch (Exception ex)
            {
                Debug.LogError($"TimeService: Time pause message processing failed - {ex.Message}");
            }
        }

        #endregion

        #region Public API

        /// <summary>
        /// Get the last known server time
        /// </summary>
        public GameTimeDTO GetLastServerTime()
        {
            return lastServerTime;
        }

        /// <summary>
        /// Get the server time scale
        /// </summary>
        public float GetServerTimeScale()
        {
            return serverTimeScale;
        }

        /// <summary>
        /// Check if server time is paused
        /// </summary>
        public bool IsServerTimePaused()
        {
            return serverTimePaused;
        }

        /// <summary>
        /// Check if time service is currently syncing
        /// </summary>
        public bool IsSyncing()
        {
            return isSyncing;
        }

        /// <summary>
        /// Get time since last successful sync
        /// </summary>
        public TimeSpan GetTimeSinceLastSync()
        {
            return DateTime.UtcNow - lastSyncTime;
        }

        /// <summary>
        /// Force immediate sync with server
        /// </summary>
        public void ForceSyncNow()
        {
            StartCoroutine(SyncTimeWithServer());
        }

        /// <summary>
        /// Enable/disable automatic time synchronization
        /// </summary>
        public void SetAutoSyncEnabled(bool enabled)
        {
            enableAutoSync = enabled;
            if (enabled)
            {
                nextSyncCountdown = 0f; // Trigger immediate sync
            }
        }

        /// <summary>
        /// Set server time authority
        /// </summary>
        public void SetServerTimeAuthority(bool authority)
        {
            serverTimeAuthority = authority;
            if (authority && isInitialized)
            {
                // Force sync when enabling server authority
                ForceSyncNow();
            }
        }

        #endregion

        #region Unity Lifecycle

        private void OnDestroy()
        {
            if (webSocketClient != null)
            {
                webSocketClient.OnConnected -= OnWebSocketConnected;
                webSocketClient.OnDisconnected -= OnWebSocketDisconnected;
                webSocketClient.OnMessageReceived -= OnWebSocketMessageReceived;
            }

            OnTimeReceived = null;
            OnTimeScaleChanged = null;
            OnSyncStatusChanged = null;
            OnSyncError = null;
        }

        #endregion

        #region Save/Load Support

        /// <summary>
        /// Get time save data for save system
        /// </summary>
        public Dictionary<string, object> GetTimeSaveData()
        {
            var saveData = new Dictionary<string, object>();
            
            try
            {
                // Save current server time if available
                if (lastServerTime != null)
                {
                    saveData["gameTime"] = new
                    {
                        year = lastServerTime.Year,
                        month = lastServerTime.Month,
                        day = lastServerTime.Day,
                        hour = lastServerTime.Hour,
                        minute = lastServerTime.Minute,
                        second = lastServerTime.Second,
                        dayOfWeek = lastServerTime.DayOfWeek,
                        season = lastServerTime.Season,
                        isNight = lastServerTime.IsNight
                    };
                }
                
                // Save time system settings
                saveData["timeScale"] = serverTimeScale;
                saveData["isPaused"] = serverTimePaused;
                saveData["serverTimeAuthority"] = serverTimeAuthority;
                saveData["lastSyncTime"] = lastSyncTime.ToString("O");
                
                // Save Unity time facade data if available
                if (timeSystemFacade != null)
                {
                    saveData["unityTimeScale"] = Time.timeScale;
                    saveData["unityTime"] = Time.time;
                    saveData["unityRealtimeSinceStartup"] = Time.realtimeSinceStartup;
                }
                
                saveData["saveTimestamp"] = DateTime.UtcNow.ToString("O");
            }
            catch (Exception ex)
            {
                Debug.LogError($"[TimeService] Error getting time save data: {ex.Message}");
            }
            
            return saveData;
        }

        /// <summary>
        /// Apply time save data from save system
        /// </summary>
        public void ApplyTimeSaveData(Dictionary<string, object> saveData)
        {
            try
            {
                // Apply game time if available
                if (saveData.ContainsKey("gameTime"))
                {
                    var gameTimeData = saveData["gameTime"] as Dictionary<string, object>;
                    if (gameTimeData != null)
                    {
                        lastServerTime = new GameTimeDTO
                        {
                            Year = Convert.ToInt32(gameTimeData["year"]),
                            Month = Convert.ToInt32(gameTimeData["month"]),
                            Day = Convert.ToInt32(gameTimeData["day"]),
                            Hour = Convert.ToInt32(gameTimeData["hour"]),
                            Minute = Convert.ToInt32(gameTimeData["minute"]),
                            Second = Convert.ToInt32(gameTimeData["second"]),
                            DayOfWeek = gameTimeData["dayOfWeek"].ToString(),
                            Season = gameTimeData["season"].ToString(),
                            IsNight = Convert.ToBoolean(gameTimeData["isNight"])
                        };
                        
                        // Apply to Unity time system
                        if (timeSystemFacade != null)
                        {
                            ApplyServerTimeToUnity(lastServerTime);
                        }
                        
                        OnTimeReceived?.Invoke(lastServerTime);
                    }
                }
                
                // Apply time scale
                if (saveData.ContainsKey("timeScale"))
                {
                    serverTimeScale = Convert.ToSingle(saveData["timeScale"]);
                    if (!serverTimeAuthority && timeSystemFacade != null)
                    {
                        Time.timeScale = serverTimeScale;
                    }
                }
                
                // Apply pause state
                if (saveData.ContainsKey("isPaused"))
                {
                    serverTimePaused = Convert.ToBoolean(saveData["isPaused"]);
                    if (!serverTimeAuthority && timeSystemFacade != null)
                    {
                        Time.timeScale = serverTimePaused ? 0f : serverTimeScale;
                    }
                }
                
                // Apply server time authority
                if (saveData.ContainsKey("serverTimeAuthority"))
                {
                    serverTimeAuthority = Convert.ToBoolean(saveData["serverTimeAuthority"]);
                }
                
                // Apply last sync time
                if (saveData.ContainsKey("lastSyncTime"))
                {
                    var lastSyncTimeStr = saveData["lastSyncTime"].ToString();
                    if (DateTime.TryParse(lastSyncTimeStr, out DateTime parsedTime))
                    {
                        lastSyncTime = parsedTime;
                    }
                }
                
                Debug.Log("[TimeService] Time save data applied successfully");
                
                // Force sync with server to validate time consistency
                if (isInitialized && enableAutoSync)
                {
                    ForceSyncNow();
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"[TimeService] Error applying time save data: {ex.Message}");
            }
        }

        #endregion
    }

    /// <summary>
    /// Event data for time scale changes
    /// </summary>
    [Serializable]
    public class TimeScaleChangedEvent
    {
        public float NewScale;
        public float OldScale;
        public DateTime Timestamp;
    }
} 