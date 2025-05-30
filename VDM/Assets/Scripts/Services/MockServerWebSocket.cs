using NativeWebSocket;
using Newtonsoft.Json;
using System.Collections.Generic;
using System.Collections;
using System.Runtime.InteropServices;
using System.Text;
using System;
using UnityEngine;


#if UNITY_WEBGL && !UNITY_EDITOR
#else
#endif

namespace VDM.Runtime.Services
{
    /// <summary>
    /// WebSocket client for real-time communication with the Visual DM Mock Server
    /// Handles connection management, automatic reconnection, and event broadcasting
    /// </summary>
    public class MockServerWebSocket : MonoBehaviour
    {
        public static MockServerWebSocket Instance { get; private set; }

        [Header("WebSocket Configuration")]
        [SerializeField] private string websocketUrl = "ws://localhost:8001/ws";
        [SerializeField] private float reconnectDelay = 5f;
        [SerializeField] private float heartbeatInterval = 30f;
        [SerializeField] private bool autoReconnect = true;
        [SerializeField] private bool debugLogging = true;

        // Events for WebSocket communication
        public event Action OnConnected;
        public event Action OnDisconnected;
        public event Action<WebSocketMessage> OnMessageReceived;
        public event Action<string> OnError;

        // Specific events for different message types
        public event Action<MockTimeState> OnTimeUpdated;
        public event Action<MockCharacter> OnCharacterCreated;
        public event Action<MockCharacter> OnCharacterUpdated;
        public event Action<string, Vector2> OnCharacterMoved;
        public event Action<MockQuest> OnQuestProgressUpdated;
        public event Action<MockWorldState> OnWorldStateUpdated;

#if !UNITY_WEBGL || UNITY_EDITOR
        private WebSocket websocket;
#endif

        private bool isConnected = false;
        private bool shouldReconnect = true;
        private Coroutine heartbeatCoroutine;
        private Coroutine reconnectCoroutine;

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
            Connect();
        }

        private void OnDestroy()
        {
            shouldReconnect = false;
            Disconnect();
        }

        #region Public Methods

        /// <summary>
        /// Connect to the WebSocket server
        /// </summary>
        public async void Connect()
        {
            if (isConnected)
            {
                if (debugLogging)
                    Debug.Log("[MockServerWebSocket] Already connected");
                return;
            }

            try
            {
#if !UNITY_WEBGL || UNITY_EDITOR
                websocket = new WebSocket(websocketUrl);

                websocket.OnOpen += OnWebSocketOpen;
                websocket.OnMessage += OnWebSocketMessage;
                websocket.OnError += OnWebSocketError;
                websocket.OnClose += OnWebSocketClose;

                await websocket.Connect();
#else
                // WebGL implementation would go here
                Debug.LogWarning("[MockServerWebSocket] WebGL WebSocket implementation not available");
#endif
            }
            catch (Exception e)
            {
                Debug.LogError($"[MockServerWebSocket] Failed to connect: {e.Message}");
                OnError?.Invoke(e.Message);
                
                if (autoReconnect)
                    StartReconnectCoroutine();
            }
        }

        /// <summary>
        /// Disconnect from the WebSocket server
        /// </summary>
        public async void Disconnect()
        {
            shouldReconnect = false;
            
            if (heartbeatCoroutine != null)
            {
                StopCoroutine(heartbeatCoroutine);
                heartbeatCoroutine = null;
            }

            if (reconnectCoroutine != null)
            {
                StopCoroutine(reconnectCoroutine);
                reconnectCoroutine = null;
            }

#if !UNITY_WEBGL || UNITY_EDITOR
            if (websocket != null)
            {
                await websocket.Close();
                websocket = null;
            }
#endif

            isConnected = false;
        }

        /// <summary>
        /// Send a ping message to the server
        /// </summary>
        public void SendPing()
        {
            var message = new WebSocketMessage
            {
                type = "ping",
                data = new { timestamp = DateTime.Now.ToString("O") }
            };
            SendMessage(message);
        }

        /// <summary>
        /// Send time advance request
        /// </summary>
        public void SendTimeAdvance(int minutes)
        {
            var message = new WebSocketMessage
            {
                type = "time_advance",
                amount = minutes
            };
            SendMessage(message);
        }

        /// <summary>
        /// Send character movement update
        /// </summary>
        public void SendCharacterMove(string characterId, Vector2 position)
        {
            var message = new WebSocketMessage
            {
                type = "character_move",
                character_id = characterId,
                position = new { x = position.x, y = position.y }
            };
            SendMessage(message);
        }

        /// <summary>
        /// Send a generic message to the server
        /// </summary>
        public void SendMessage(WebSocketMessage message)
        {
            if (!isConnected)
            {
                Debug.LogWarning("[MockServerWebSocket] Cannot send message - not connected");
                return;
            }

            try
            {
                string jsonMessage = JsonConvert.SerializeObject(message);
                
#if !UNITY_WEBGL || UNITY_EDITOR
                websocket.SendText(jsonMessage);
#endif

                if (debugLogging)
                    Debug.Log($"[MockServerWebSocket] Sent message: {message.type}");
            }
            catch (Exception e)
            {
                Debug.LogError($"[MockServerWebSocket] Failed to send message: {e.Message}");
            }
        }

        #endregion

        #region WebSocket Event Handlers

#if !UNITY_WEBGL || UNITY_EDITOR
        private void OnWebSocketOpen()
        {
            isConnected = true;
            
            if (debugLogging)
                Debug.Log("[MockServerWebSocket] Connected to server");
            
            OnConnected?.Invoke();
            
            // Start heartbeat
            if (heartbeatCoroutine != null)
                StopCoroutine(heartbeatCoroutine);
            heartbeatCoroutine = StartCoroutine(HeartbeatCoroutine());
        }

        private void OnWebSocketMessage(byte[] data)
        {
            try
            {
                string jsonMessage = Encoding.UTF8.GetString(data);
                var message = JsonConvert.DeserializeObject<WebSocketMessage>(jsonMessage);
                
                if (debugLogging)
                    Debug.Log($"[MockServerWebSocket] Received message: {message.type}");
                
                HandleMessage(message);
                OnMessageReceived?.Invoke(message);
            }
            catch (Exception e)
            {
                Debug.LogError($"[MockServerWebSocket] Failed to parse message: {e.Message}");
            }
        }

        private void OnWebSocketError(string error)
        {
            Debug.LogError($"[MockServerWebSocket] WebSocket error: {error}");
            OnError?.Invoke(error);
        }

        private void OnWebSocketClose(WebSocketCloseCode closeCode)
        {
            isConnected = false;
            
            if (debugLogging)
                Debug.Log($"[MockServerWebSocket] Connection closed: {closeCode}");
            
            OnDisconnected?.Invoke();
            
            if (heartbeatCoroutine != null)
            {
                StopCoroutine(heartbeatCoroutine);
                heartbeatCoroutine = null;
            }
            
            if (autoReconnect && shouldReconnect)
                StartReconnectCoroutine();
        }
#endif

        #endregion

        #region Message Handling

        private void HandleMessage(WebSocketMessage message)
        {
            switch (message.type)
            {
                case "connected":
                    if (debugLogging)
                        Debug.Log("[MockServerWebSocket] Welcome message received");
                    break;

                case "pong":
                    if (debugLogging)
                        Debug.Log("[MockServerWebSocket] Pong received");
                    break;

                case "time_update":
                case "time_advanced":
                    HandleTimeUpdate(message);
                    break;

                case "character_created":
                    HandleCharacterCreated(message);
                    break;

                case "character_updated":
                    HandleCharacterUpdated(message);
                    break;

                case "character_moved":
                    HandleCharacterMoved(message);
                    break;

                case "quest_progress_updated":
                    HandleQuestProgressUpdated(message);
                    break;

                case "world_state_updated":
                    HandleWorldStateUpdated(message);
                    break;

                case "user_disconnected":
                    if (debugLogging)
                        Debug.Log("[MockServerWebSocket] User disconnected notification");
                    break;

                case "error":
                    Debug.LogError($"[MockServerWebSocket] Server error: {message.data}");
                    break;

                default:
                    if (debugLogging)
                        Debug.Log($"[MockServerWebSocket] Unknown message type: {message.type}");
                    break;
            }
        }

        private void HandleTimeUpdate(WebSocketMessage message)
        {
            try
            {
                var timeState = JsonConvert.DeserializeObject<MockTimeState>(message.data.ToString());
                OnTimeUpdated?.Invoke(timeState);
            }
            catch (Exception e)
            {
                Debug.LogError($"[MockServerWebSocket] Failed to parse time update: {e.Message}");
            }
        }

        private void HandleCharacterCreated(WebSocketMessage message)
        {
            try
            {
                var character = JsonConvert.DeserializeObject<MockCharacter>(message.data.ToString());
                OnCharacterCreated?.Invoke(character);
            }
            catch (Exception e)
            {
                Debug.LogError($"[MockServerWebSocket] Failed to parse character creation: {e.Message}");
            }
        }

        private void HandleCharacterUpdated(WebSocketMessage message)
        {
            try
            {
                var character = JsonConvert.DeserializeObject<MockCharacter>(message.data.ToString());
                OnCharacterUpdated?.Invoke(character);
            }
            catch (Exception e)
            {
                Debug.LogError($"[MockServerWebSocket] Failed to parse character update: {e.Message}");
            }
        }

        private void HandleCharacterMoved(WebSocketMessage message)
        {
            try
            {
                dynamic data = JsonConvert.DeserializeObject(message.data.ToString());
                string characterId = data.character_id;
                Vector2 position = new Vector2((float)data.position.x, (float)data.position.y);
                OnCharacterMoved?.Invoke(characterId, position);
            }
            catch (Exception e)
            {
                Debug.LogError($"[MockServerWebSocket] Failed to parse character movement: {e.Message}");
            }
        }

        private void HandleQuestProgressUpdated(WebSocketMessage message)
        {
            try
            {
                var quest = JsonConvert.DeserializeObject<MockQuest>(message.data.ToString());
                OnQuestProgressUpdated?.Invoke(quest);
            }
            catch (Exception e)
            {
                Debug.LogError($"[MockServerWebSocket] Failed to parse quest progress: {e.Message}");
            }
        }

        private void HandleWorldStateUpdated(WebSocketMessage message)
        {
            try
            {
                var worldState = JsonConvert.DeserializeObject<MockWorldState>(message.data.ToString());
                OnWorldStateUpdated?.Invoke(worldState);
            }
            catch (Exception e)
            {
                Debug.LogError($"[MockServerWebSocket] Failed to parse world state: {e.Message}");
            }
        }

        #endregion

        #region Coroutines

        private IEnumerator HeartbeatCoroutine()
        {
            while (isConnected)
            {
                yield return new WaitForSeconds(heartbeatInterval);
                
                if (isConnected)
                {
                    SendPing();
                }
            }
        }

        private void StartReconnectCoroutine()
        {
            if (reconnectCoroutine != null)
                StopCoroutine(reconnectCoroutine);
                
            reconnectCoroutine = StartCoroutine(ReconnectCoroutine());
        }

        private IEnumerator ReconnectCoroutine()
        {
            while (!isConnected && shouldReconnect)
            {
                if (debugLogging)
                    Debug.Log($"[MockServerWebSocket] Attempting reconnection in {reconnectDelay} seconds...");
                
                yield return new WaitForSeconds(reconnectDelay);
                
                if (shouldReconnect)
                {
                    Connect();
                }
            }
            
            reconnectCoroutine = null;
        }

        #endregion

        #region Unity Update

        private void Update()
        {
#if !UNITY_WEBGL || UNITY_EDITOR
            websocket?.DispatchMessageQueue();
#endif
        }

        #endregion

        #region Public Properties

        public bool IsConnected => isConnected;
        public string WebSocketUrl => websocketUrl;

        #endregion
    }

    #region WebSocket Message Data Structures

    [System.Serializable]
    public class WebSocketMessage
    {
        public string type;
        public object data;
        public int amount;
        public string character_id;
        public object position;
    }

    #endregion
} 