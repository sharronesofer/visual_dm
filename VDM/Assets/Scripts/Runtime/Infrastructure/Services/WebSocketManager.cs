using System;
using System.Collections.Generic;
using UnityEngine;
using NativeWebSocket;
using Newtonsoft.Json;

namespace VDM.Infrastructure.Core
{
    public class WebSocketManager : MonoBehaviour
    {
        private static WebSocketManager _instance;
        public static WebSocketManager Instance
        {
            get
            {
                if (_instance == null)
                {
                    _instance = FindObjectOfType<WebSocketManager>();
                    if (_instance == null)
                    {
                        GameObject go = new GameObject("WebSocketManager");
                        _instance = go.AddComponent<WebSocketManager>();
                        DontDestroyOnLoad(go);
                    }
                }
                return _instance;
            }
        }

        [Header("WebSocket Settings")]
        public string serverUrl = "ws://localhost:8000/ws";
        public bool autoReconnect = true;
        public float reconnectInterval = 5f;
        public int maxReconnectAttempts = 10;
        public bool enableLogging = true;
        
        private WebSocket webSocket;
        private bool isConnecting = false;
        private int reconnectAttempts = 0;
        private float lastReconnectTime = 0f;
        
        // Event handlers
        public event Action OnConnected;
        public event Action<WebSocketCloseCode> OnDisconnected;
        public event Action<string> OnError;
        public event Action<string> OnMessageReceived;
        
        // Message handlers by type
        private Dictionary<string, Action<string>> messageHandlers = new Dictionary<string, Action<string>>();
        
        void Start()
        {
            if (_instance != null && _instance != this)
            {
                Destroy(gameObject);
                return;
            }
            
            _instance = this;
            DontDestroyOnLoad(gameObject);
        }
        
        void Update()
        {
            // Dispatch WebSocket messages on main thread
            if (webSocket != null)
            {
                webSocket.DispatchMessageQueue();
            }
            
            // Handle auto-reconnection
            if (autoReconnect && webSocket != null && webSocket.State == WebSocketState.Closed && 
                !isConnecting && reconnectAttempts < maxReconnectAttempts &&
                Time.time - lastReconnectTime > reconnectInterval)
            {
                Reconnect();
            }
        }
        
        public async void Connect(string url = null)
        {
            if (isConnecting || (webSocket != null && webSocket.State == WebSocketState.Open))
            {
                if (enableLogging)
                    Debug.Log("WebSocketManager: Already connected or connecting");
                return;
            }
            
            isConnecting = true;
            string connectUrl = url ?? serverUrl;
            
            try
            {
                webSocket = new WebSocket(connectUrl);
                
                webSocket.OnOpen += OnWebSocketOpen;
                webSocket.OnError += OnWebSocketError;
                webSocket.OnClose += OnWebSocketClose;
                webSocket.OnMessage += OnWebSocketMessage;
                
                if (enableLogging)
                    Debug.Log($"WebSocketManager: Connecting to {connectUrl}");
                
                await webSocket.Connect();
            }
            catch (Exception ex)
            {
                isConnecting = false;
                if (enableLogging)
                    Debug.LogError($"WebSocketManager: Connection failed - {ex.Message}");
                OnError?.Invoke(ex.Message);
            }
        }
        
        public async void Disconnect()
        {
            autoReconnect = false;
            
            if (webSocket != null && webSocket.State == WebSocketState.Open)
            {
                if (enableLogging)
                    Debug.Log("WebSocketManager: Disconnecting");
                
                await webSocket.Close();
            }
        }
        
        public async void SendMessage(string message)
        {
            if (webSocket != null && webSocket.State == WebSocketState.Open)
            {
                try
                {
                    await webSocket.SendText(message);
                    if (enableLogging)
                        Debug.Log($"WebSocketManager: Sent message - {message}");
                }
                catch (Exception ex)
                {
                    if (enableLogging)
                        Debug.LogError($"WebSocketManager: Send failed - {ex.Message}");
                    OnError?.Invoke(ex.Message);
                }
            }
            else
            {
                if (enableLogging)
                    Debug.LogWarning("WebSocketManager: Cannot send message - not connected");
            }
        }
        
        public void SendMessage<T>(string messageType, T data)
        {
            var message = new
            {
                type = messageType,
                data = data,
                timestamp = DateTime.UtcNow
            };
            
            string json = JsonConvert.SerializeObject(message);
            SendMessage(json);
        }
        
        public void RegisterMessageHandler(string messageType, Action<string> handler)
        {
            if (messageHandlers.ContainsKey(messageType))
            {
                messageHandlers[messageType] += handler;
            }
            else
            {
                messageHandlers[messageType] = handler;
            }
            
            if (enableLogging)
                Debug.Log($"WebSocketManager: Registered handler for message type '{messageType}'");
        }
        
        public void UnregisterMessageHandler(string messageType, Action<string> handler)
        {
            if (messageHandlers.ContainsKey(messageType))
            {
                messageHandlers[messageType] -= handler;
                if (messageHandlers[messageType] == null)
                {
                    messageHandlers.Remove(messageType);
                }
            }
        }
        
        private async void Reconnect()
        {
            if (isConnecting) return;
            
            reconnectAttempts++;
            lastReconnectTime = Time.time;
            
            if (enableLogging)
                Debug.Log($"WebSocketManager: Reconnection attempt {reconnectAttempts}/{maxReconnectAttempts}");
            
            await Connect();
        }
        
        private void OnWebSocketOpen()
        {
            isConnecting = false;
            reconnectAttempts = 0;
            
            if (enableLogging)
                Debug.Log("WebSocketManager: Connected successfully");
            
            OnConnected?.Invoke();
        }
        
        private void OnWebSocketError(string error)
        {
            isConnecting = false;
            
            if (enableLogging)
                Debug.LogError($"WebSocketManager: Error - {error}");
            
            OnError?.Invoke(error);
        }
        
        private void OnWebSocketClose(WebSocketCloseCode closeCode)
        {
            isConnecting = false;
            
            if (enableLogging)
                Debug.Log($"WebSocketManager: Connection closed - {closeCode}");
            
            OnDisconnected?.Invoke(closeCode);
        }
        
        private void OnWebSocketMessage(byte[] data)
        {
            string message = System.Text.Encoding.UTF8.GetString(data);
            
            if (enableLogging)
                Debug.Log($"WebSocketManager: Received message - {message}");
            
            OnMessageReceived?.Invoke(message);
            
            // Try to parse and route message
            try
            {
                var messageObj = JsonConvert.DeserializeObject<dynamic>(message);
                string messageType = messageObj.type;
                
                if (messageHandlers.ContainsKey(messageType))
                {
                    messageHandlers[messageType]?.Invoke(message);
                }
            }
            catch (Exception ex)
            {
                if (enableLogging)
                    Debug.LogWarning($"WebSocketManager: Failed to parse message - {ex.Message}");
            }
        }
        
        public bool IsConnected()
        {
            return webSocket != null && webSocket.State == WebSocketState.Open;
        }
        
        public WebSocketState GetState()
        {
            return webSocket?.State ?? WebSocketState.Closed;
        }
        
        void OnDestroy()
        {
            if (webSocket != null)
            {
                webSocket.Close();
            }
        }
        
        void OnApplicationPause(bool pauseStatus)
        {
            if (pauseStatus && webSocket != null && webSocket.State == WebSocketState.Open)
            {
                // Optionally close connection when app is paused
                // webSocket.Close();
            }
        }
    }
} 