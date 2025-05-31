using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Newtonsoft.Json;
using System.Text;

#if UNITY_WEBGL && !UNITY_EDITOR
using System.Runtime.InteropServices;
#else
using NativeWebSocket;
#endif

namespace VDM.Infrastructure.Services
{
    /// <summary>
    /// WebSocket client for Mock Server integration testing
    /// Handles connection, messaging, and event broadcasting
    /// </summary>
    public class MockServerWebSocket : MonoBehaviour
    {
        private const string DEFAULT_URL = "ws://localhost:8001/ws";
        
        public static MockServerWebSocket Instance { get; private set; }
        
        private WebSocket webSocket;
        private bool isConnected = false;
        
        // Events for testing integration
        public event Action OnConnected;
        public event Action OnDisconnected;
        public event Action<WebSocketMessage> OnMessageReceived;
        public event Action<string> OnError;
        
        [Header("Configuration")]
        [SerializeField] private string serverUrl = DEFAULT_URL;
        [SerializeField] private bool autoReconnect = true;
        [SerializeField] private float reconnectDelay = 5f;
        [SerializeField] private bool debugLogging = true;
        
        private void Awake()
        {
            if (Instance == null)
            {
                Instance = this;
                DontDestroyOnLoad(gameObject);
            }
            else
            {
                Destroy(gameObject);
            }
        }
        
        private void Start()
        {
            // Auto-connect for testing scenarios
            if (Application.isPlaying && !Application.isEditor)
            {
                Connect();
            }
        }
        
        private void Update()
        {
            // Dispatch WebSocket messages on Unity's main thread
            if (webSocket != null)
            {
                webSocket.DispatchMessageQueue();
            }
        }
        
        private void OnDestroy()
        {
            if (webSocket != null)
            {
                webSocket.Close();
            }
        }
        
        #region Connection Management
        
        /// <summary>
        /// Connect to the mock server WebSocket
        /// </summary>
        public async void Connect()
        {
            Connect(serverUrl);
        }
        
        /// <summary>
        /// Connect to a specific WebSocket URL
        /// </summary>
        public async void Connect(string url)
        {
            if (isConnected)
            {
                LogDebug("Already connected to WebSocket");
                return;
            }
            
            try
            {
                LogDebug($"Connecting to WebSocket: {url}");
                
                webSocket = new WebSocket(url);
                
                webSocket.OnOpen += OnWebSocketOpen;
                webSocket.OnMessage += OnWebSocketMessage;
                webSocket.OnError += OnWebSocketError;
                webSocket.OnClose += OnWebSocketClose;
                
                await webSocket.Connect();
            }
            catch (Exception ex)
            {
                LogError($"Failed to connect to WebSocket: {ex.Message}");
                OnError?.Invoke(ex.Message);
            }
        }
        
        /// <summary>
        /// Disconnect from the WebSocket
        /// </summary>
        public async void Disconnect()
        {
            if (webSocket != null && isConnected)
            {
                LogDebug("Disconnecting from WebSocket");
                await webSocket.Close();
            }
        }
        
        #endregion
        
        #region Message Sending
        
        /// <summary>
        /// Send a JSON message to the server
        /// </summary>
        public void SendMessage(string messageType, object data)
        {
            if (!isConnected)
            {
                LogError("Cannot send message - not connected to WebSocket");
                return;
            }
            
            try
            {
                var message = new WebSocketMessage
                {
                    type = messageType,
                    data = data,
                    timestamp = DateTime.Now.ToString("O"),
                    id = Guid.NewGuid().ToString()
                };
                
                string jsonMessage = JsonConvert.SerializeObject(message);
                
                LogDebug($"Sending WebSocket message: {messageType}");
                
                webSocket.SendText(jsonMessage);
            }
            catch (Exception ex)
            {
                LogError($"Failed to send WebSocket message: {ex.Message}");
                OnError?.Invoke(ex.Message);
            }
        }
        
        /// <summary>
        /// Send a ping message for testing
        /// </summary>
        public void SendPing()
        {
            SendMessage("ping", new { message = "Unity ping", timestamp = DateTime.Now });
        }
        
        #endregion
        
        #region WebSocket Event Handlers
        
        private void OnWebSocketOpen()
        {
            isConnected = true;
            LogDebug("WebSocket connection opened");
            OnConnected?.Invoke();
        }
        
        private void OnWebSocketMessage(byte[] data)
        {
            try
            {
                string messageText = System.Text.Encoding.UTF8.GetString(data);
                LogDebug($"Received WebSocket message: {messageText}");
                
                var message = JsonConvert.DeserializeObject<WebSocketMessage>(messageText);
                OnMessageReceived?.Invoke(message);
                
                // Handle specific message types
                HandleMessage(message);
            }
            catch (Exception ex)
            {
                LogError($"Failed to process WebSocket message: {ex.Message}");
                OnError?.Invoke(ex.Message);
            }
        }
        
        private void OnWebSocketError(string error)
        {
            LogError($"WebSocket error: {error}");
            OnError?.Invoke(error);
        }
        
        private void OnWebSocketClose(WebSocketCloseCode closeCode)
        {
            isConnected = false;
            LogDebug($"WebSocket connection closed: {closeCode}");
            OnDisconnected?.Invoke();
            
            // Auto-reconnect if enabled
            if (autoReconnect && Application.isPlaying)
            {
                StartCoroutine(ReconnectAfterDelay());
            }
        }
        
        #endregion
        
        #region Message Handling
        
        private void HandleMessage(WebSocketMessage message)
        {
            switch (message.type)
            {
                case "system_message":
                    LogDebug($"System message: {message.data}");
                    break;
                    
                case "echo":
                    LogDebug("Received echo response");
                    break;
                    
                case "time_update":
                    LogDebug("Received time update");
                    break;
                    
                case "character_update":
                    LogDebug("Received character update");
                    break;
                    
                case "quest_update":
                    LogDebug("Received quest update");
                    break;
                    
                case "combat_update":
                    LogDebug("Received combat update");
                    break;
                    
                case "region_event":
                    LogDebug("Received region event");
                    break;
                    
                default:
                    LogDebug($"Unhandled message type: {message.type}");
                    break;
            }
        }
        
        #endregion
        
        #region Helper Methods
        
        private IEnumerator ReconnectAfterDelay()
        {
            LogDebug($"Attempting to reconnect in {reconnectDelay} seconds...");
            yield return new WaitForSeconds(reconnectDelay);
            
            if (!isConnected)
            {
                Connect();
            }
        }
        
        private void LogDebug(string message)
        {
            if (debugLogging)
            {
                Debug.Log($"[MockServerWebSocket] {message}");
            }
        }
        
        private void LogError(string message)
        {
            Debug.LogError($"[MockServerWebSocket] {message}");
        }
        
        #endregion
        
        #region Public Properties
        
        public bool IsConnected => isConnected;
        public string ServerUrl => serverUrl;
        
        #endregion
    }
    
    /// <summary>
    /// WebSocket message structure for communication with mock server
    /// </summary>
    [Serializable]
    public class WebSocketMessage
    {
        public string type;
        public object data;
        public string timestamp;
        public string id;
    }
} 