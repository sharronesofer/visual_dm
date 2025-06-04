using System;
using System.Collections.Generic;
using UnityEngine;
using Newtonsoft.Json;
using VDM.Infrastructure.Services;
using VDM.Systems.Dialogue.Models;

namespace VDM.Systems.Dialogue.Services
{
    /// <summary>
    /// Handles real-time dialogue latency updates from the backend WebSocket service.
    /// Provides placeholder message management and latency feedback for NPC dialogue.
    /// </summary>
    public class DialogueLatencyHandler : MonoBehaviour
    {
        [Header("Configuration")]
        [SerializeField] private string webSocketUrl = "ws://localhost:8000/dialogue/ws/latency";
        [SerializeField] private bool enableLogging = true;
        [SerializeField] private float reconnectDelay = 5f;
        [SerializeField] private bool autoConnect = true;

        [Header("Latency Thresholds")]
        [SerializeField] private float instantThreshold = 0.0f;
        [SerializeField] private float shortThreshold = 1.5f;
        [SerializeField] private float mediumThreshold = 3.0f;
        [SerializeField] private float longThreshold = 8.0f;
        [SerializeField] private float timeoutThreshold = 30.0f;

        // Events for dialogue latency updates
        public event Action<string, string> OnPlaceholderMessageReceived; // conversationId, message
        public event Action<string, string> OnFinalResponseReceived; // conversationId, response
        public event Action<string, float> OnLatencyUpdate; // conversationId, elapsedTime
        public event Action<string> OnDialogueTimeout; // conversationId
        public event Action<string> OnDialogueStarted; // conversationId
        public event Action<string> OnDialogueEnded; // conversationId
        public event Action<string> OnError; // errorMessage

        private WebSocketService webSocketService;
        private bool isConnected = false;
        private Dictionary<string, DialogueLatencySession> activeSessions = new Dictionary<string, DialogueLatencySession>();

        private void Awake()
        {
            webSocketService = FindObjectOfType<WebSocketService>();
            if (webSocketService == null)
            {
                Debug.LogError("DialogueLatencyHandler requires WebSocketService to be present in the scene");
            }
        }

        private void Start()
        {
            if (webSocketService != null && autoConnect)
            {
                SetupWebSocketEvents();
                ConnectToDialogueLatencyService();
            }
        }

        private void OnDestroy()
        {
            if (webSocketService != null)
            {
                CleanupWebSocketEvents();
                DisconnectFromDialogueLatencyService();
            }
        }

        #region Connection Management

        /// <summary>
        /// Connect to the dialogue latency WebSocket service
        /// </summary>
        public async void ConnectToDialogueLatencyService()
        {
            if (isConnected)
            {
                LogDebug("Already connected to dialogue latency service");
                return;
            }

            try
            {
                LogDebug($"Connecting to dialogue latency service: {webSocketUrl}");
                await webSocketService.ConnectAsync(webSocketUrl);
                isConnected = true;
                LogDebug("Connected to dialogue latency service");
            }
            catch (Exception ex)
            {
                LogError($"Failed to connect to dialogue latency service: {ex.Message}");
                OnError?.Invoke(ex.Message);
            }
        }

        /// <summary>
        /// Disconnect from the dialogue latency WebSocket service
        /// </summary>
        public async void DisconnectFromDialogueLatencyService()
        {
            if (!isConnected)
            {
                return;
            }

            try
            {
                LogDebug("Disconnecting from dialogue latency service");
                await webSocketService.DisconnectAsync();
                isConnected = false;
                LogDebug("Disconnected from dialogue latency service");
            }
            catch (Exception ex)
            {
                LogError($"Error disconnecting from dialogue latency service: {ex.Message}");
            }
        }

        #endregion

        #region WebSocket Event Handling

        private void SetupWebSocketEvents()
        {
            if (webSocketService != null)
            {
                webSocketService.OnConnected += OnWebSocketConnected;
                webSocketService.OnDisconnected += OnWebSocketDisconnected;
                webSocketService.OnMessageReceived += OnWebSocketMessageReceived;
                webSocketService.OnError += OnWebSocketError;
            }
        }

        private void CleanupWebSocketEvents()
        {
            if (webSocketService != null)
            {
                webSocketService.OnConnected -= OnWebSocketConnected;
                webSocketService.OnDisconnected -= OnWebSocketDisconnected;
                webSocketService.OnMessageReceived -= OnWebSocketMessageReceived;
                webSocketService.OnError -= OnWebSocketError;
            }
        }

        private void OnWebSocketConnected()
        {
            isConnected = true;
            LogDebug("WebSocket connected to dialogue latency service");
        }

        private void OnWebSocketDisconnected()
        {
            isConnected = false;
            LogDebug("WebSocket disconnected from dialogue latency service");
            
            // Clear active sessions
            activeSessions.Clear();
        }

        private void OnWebSocketError(string error)
        {
            LogError($"WebSocket error: {error}");
            OnError?.Invoke(error);
        }

        private void OnWebSocketMessageReceived(string message)
        {
            try
            {
                LogDebug($"Received WebSocket message: {message}");
                
                var messageData = JsonConvert.DeserializeObject<WebSocketMessage>(message);
                HandleDialogueLatencyMessage(messageData);
            }
            catch (Exception ex)
            {
                LogError($"Failed to process WebSocket message: {ex.Message}");
                OnError?.Invoke(ex.Message);
            }
        }

        #endregion

        #region Message Handling

        private void HandleDialogueLatencyMessage(WebSocketMessage message)
        {
            try
            {
                switch (message.Type)
                {
                    case "latency_update":
                        HandleLatencyUpdate(message);
                        break;
                        
                    case "final_response":
                        HandleFinalResponse(message);
                        break;
                        
                    case "connection_status":
                        HandleConnectionStatus(message);
                        break;
                        
                    case "dialogue_started":
                        HandleDialogueStarted(message);
                        break;
                        
                    case "dialogue_ended":
                        HandleDialogueEnded(message);
                        break;
                        
                    case "dialogue_timeout":
                        HandleDialogueTimeout(message);
                        break;
                        
                    case "error":
                        HandleError(message);
                        break;
                        
                    default:
                        LogError($"Unknown message type: {message.Type}");
                        break;
                }
            }
            catch (Exception ex)
            {
                LogError($"Error handling dialogue latency message: {ex.Message}");
            }
        }

        private void HandleLatencyUpdate(WebSocketMessage message)
        {
            try
            {
                var data = JsonConvert.DeserializeObject<DialogueLatencyUpdate>(message.Data.ToString());
                
                // Update or create session
                if (!activeSessions.ContainsKey(data.conversation_id))
                {
                    activeSessions[data.conversation_id] = new DialogueLatencySession
                    {
                        ConversationId = data.conversation_id,
                        NpcId = data.npc_id,
                        StartTime = DateTime.UtcNow
                    };
                }
                
                var session = activeSessions[data.conversation_id];
                session.LastUpdate = DateTime.UtcNow;
                session.LastPlaceholderMessage = data.message;
                session.LastPlaceholderCategory = data.category;
                session.ElapsedTime = data.elapsed_time;
                
                LogDebug($"Latency update for {data.conversation_id}: {data.message} ({data.elapsed_time:F1}s)");
                
                // Fire events
                OnLatencyUpdate?.Invoke(data.conversation_id, data.elapsed_time);
                OnPlaceholderMessageReceived?.Invoke(data.conversation_id, data.message);
            }
            catch (Exception ex)
            {
                LogError($"Error handling latency update: {ex.Message}");
            }
        }

        private void HandleFinalResponse(WebSocketMessage message)
        {
            try
            {
                var data = JsonConvert.DeserializeObject<DialogueFinalResponse>(message.Data.ToString());
                
                // Update session with final response
                if (activeSessions.ContainsKey(data.conversation_id))
                {
                    var session = activeSessions[data.conversation_id];
                    session.FinalResponse = data.response;
                    session.TotalLatency = data.total_latency;
                    session.IsCompleted = true;
                }
                
                LogDebug($"Final response for {data.conversation_id}: {data.response}");
                
                // Fire event
                OnFinalResponseReceived?.Invoke(data.conversation_id, data.response);
            }
            catch (Exception ex)
            {
                LogError($"Error handling final response: {ex.Message}");
            }
        }

        private void HandleConnectionStatus(WebSocketMessage message)
        {
            LogDebug("Dialogue latency connection established");
        }

        private void HandleDialogueStarted(WebSocketMessage message)
        {
            try
            {
                var data = JsonConvert.DeserializeObject<Dictionary<string, object>>(message.Data.ToString());
                var conversationId = data.ContainsKey("conversation_id") 
                    ? data["conversation_id"].ToString() 
                    : "unknown";
                
                LogDebug($"Dialogue started: {conversationId}");
                OnDialogueStarted?.Invoke(conversationId);
            }
            catch (Exception ex)
            {
                LogError($"Error handling dialogue started: {ex.Message}");
            }
        }

        private void HandleDialogueEnded(WebSocketMessage message)
        {
            try
            {
                var data = JsonConvert.DeserializeObject<Dictionary<string, object>>(message.Data.ToString());
                var conversationId = data.ContainsKey("conversation_id") 
                    ? data["conversation_id"].ToString() 
                    : "unknown";
                
                // Clean up session
                if (activeSessions.ContainsKey(conversationId))
                {
                    activeSessions.Remove(conversationId);
                }

                LogDebug($"Dialogue ended: {conversationId}");
                OnDialogueEnded?.Invoke(conversationId);
            }
            catch (Exception ex)
            {
                LogError($"Error handling dialogue ended: {ex.Message}");
            }
        }

        private void HandleDialogueTimeout(WebSocketMessage message)
        {
            try
            {
                var data = JsonConvert.DeserializeObject<Dictionary<string, object>>(message.Data.ToString());
                var conversationId = data.ContainsKey("conversation_id") 
                    ? data["conversation_id"].ToString() 
                    : "unknown";
                
                LogDebug($"Dialogue timeout: {conversationId}");
                OnDialogueTimeout?.Invoke(conversationId);
            }
            catch (Exception ex)
            {
                LogError($"Error handling dialogue timeout: {ex.Message}");
            }
        }

        private void HandleError(WebSocketMessage message)
        {
            var data = JsonConvert.DeserializeObject<Dictionary<string, object>>(message.Data.ToString());
            var errorMessage = data.ContainsKey("message") 
                ? data["message"].ToString() 
                : "Unknown error";
            
            LogError($"Dialogue latency service error: {errorMessage}");
            OnError?.Invoke(errorMessage);
        }

        #endregion

        #region Public API

        /// <summary>
        /// Get the current latency session for a conversation
        /// </summary>
        public DialogueLatencySession GetLatencySession(string conversationId)
        {
            return activeSessions.ContainsKey(conversationId) ? activeSessions[conversationId] : null;
        }

        /// <summary>
        /// Get all active latency sessions
        /// </summary>
        public Dictionary<string, DialogueLatencySession> GetAllLatencySessions()
        {
            return new Dictionary<string, DialogueLatencySession>(activeSessions);
        }

        /// <summary>
        /// Check if a conversation has an active latency session
        /// </summary>
        public bool HasActiveSession(string conversationId)
        {
            return activeSessions.ContainsKey(conversationId);
        }

        /// <summary>
        /// Send a ping message to test connection
        /// </summary>
        public void SendPing()
        {
            if (isConnected && webSocketService != null)
            {
                var pingMessage = new
                {
                    type = "ping",
                    timestamp = DateTime.UtcNow.ToString("O")
                };
                
                webSocketService.SendMessage(JsonConvert.SerializeObject(pingMessage));
                LogDebug("Sent ping to dialogue latency service");
            }
        }

        #endregion

        #region Utility Methods

        private void LogDebug(string message)
        {
            if (enableLogging)
            {
                Debug.Log($"[DialogueLatencyHandler] {message}");
            }
        }

        private void LogError(string message)
        {
            if (enableLogging)
            {
                Debug.LogError($"[DialogueLatencyHandler] {message}");
            }
        }

        #endregion
    }

    #region Data Models

    [Serializable]
    public class DialogueLatencyUpdate
    {
        public string conversation_id;
        public string npc_id;
        public string message;
        public string category;
        public string context;
        public float elapsed_time;
        public string timestamp;
    }

    [Serializable]
    public class DialogueFinalResponse
    {
        public string conversation_id;
        public string npc_id;
        public string response;
        public float? total_latency;
        public string timestamp;
    }

    [Serializable]
    public class DialogueLatencySession
    {
        public string ConversationId { get; set; }
        public string NpcId { get; set; }
        public DateTime StartTime { get; set; }
        public DateTime LastUpdate { get; set; }
        public string LastPlaceholderMessage { get; set; }
        public string LastPlaceholderCategory { get; set; }
        public float ElapsedTime { get; set; }
        public string FinalResponse { get; set; }
        public float? TotalLatency { get; set; }
        public bool IsCompleted { get; set; }
    }

    #endregion
} 