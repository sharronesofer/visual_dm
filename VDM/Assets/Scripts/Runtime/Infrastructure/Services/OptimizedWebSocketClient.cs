using NativeWebSocket;
using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using UnityEngine;
using VDM.Infrastructure.Services;

namespace VDM.Infrastructure.Services.Services.Websocket
{
    /// <summary>
    /// Optimized WebSocket client with message batching, compression, and performance monitoring.
    /// Designed for real-time communication with the VDM backend.
    /// </summary>
    public class OptimizedWebSocketClient : MonoBehaviour
    {
        [Header("Connection Configuration")]
        [SerializeField] private string _serverUrl = "ws://localhost:8001";
        [SerializeField] private float _connectionTimeout = 10f;
        [SerializeField] private float _heartbeatInterval = 30f;
        [SerializeField] private int _maxReconnectAttempts = 5;
        [SerializeField] private float _reconnectDelay = 2f;
        
        [Header("Message Configuration")]
        [SerializeField] private int _maxMessageQueueSize = 1000;
        [SerializeField] private float _messageBatchInterval = 0.05f; // 50ms batching
        [SerializeField] private int _maxBatchSize = 20;
        [SerializeField] private bool _enableMessageBatching = true;
        [SerializeField] private bool _enableCompression = true;
        
        [Header("Performance Optimization")]
        [SerializeField] private bool _enableMessagePriority = true;
        [SerializeField] private bool _enableDuplicateFiltering = true;
        [SerializeField] private float _duplicateFilterWindow = 1f; // 1 second window
        [SerializeField] private bool _enablePerformanceTracking = true;
        
        // Connection state
        private WebSocketConnection _connection;
        private ConnectionState _connectionState = ConnectionState.Disconnected;
        private int _reconnectAttempts = 0;
        private float _lastHeartbeat = 0f;
        private string _connectionId;
        
        // Message management
        private Queue<WebSocketMessage> _outgoingQueue = new Queue<WebSocketMessage>();
        private List<WebSocketMessage> _batchedMessages = new List<WebSocketMessage>();
        private Dictionary<string, DateTime> _recentMessages = new Dictionary<string, DateTime>();
        private Dictionary<string, Action<WebSocketMessage>> _messageHandlers = new Dictionary<string, Action<WebSocketMessage>>();
        
        // Performance tracking
        private PerformanceMonitor _performanceMonitor;
        private WebSocketStatistics _statistics = new WebSocketStatistics();
        private Dictionary<string, float> _messageSendTimes = new Dictionary<string, float>();
        
        // Events
        public event Action OnConnected;
        public event Action<string> OnDisconnected;
        public event Action<WebSocketMessage> OnMessageReceived;
        public event Action<string> OnError;
        public event Action<WebSocketStatistics> OnStatisticsUpdated;
        
        #region Unity Lifecycle
        
        private void Awake()
        {
            InitializeWebSocket();
        }
        
        private void Start()
        {
            _performanceMonitor = FindObjectOfType<PerformanceMonitor>();
            
            StartCoroutine(MessageProcessingLoop());
            StartCoroutine(HeartbeatLoop());
            StartCoroutine(PerformanceTrackingLoop());
            
            if (_enableMessageBatching)
            {
                StartCoroutine(MessageBatchingLoop());
            }
        }
        
        private void Update()
        {
            ProcessIncomingMessages();
            CleanupRecentMessages();
        }
        
        private void OnDestroy()
        {
            StopAllCoroutines();
            Disconnect();
        }
        
        #endregion
        
        #region Initialization
        
        private void InitializeWebSocket()
        {
            _connectionId = Guid.NewGuid().ToString("N")[0..8];
            
            // Initialize message handlers for system messages
            RegisterMessageHandler("heartbeat", HandleHeartbeat);
            RegisterMessageHandler("ping", HandlePing);
            RegisterMessageHandler("error", HandleError);
            RegisterMessageHandler("batch", HandleBatchMessage);
            
            Debug.Log($"[OptimizedWebSocketClient] Initialized with ID: {_connectionId}");
        }
        
        #endregion
        
        #region Connection Management
        
        public void Connect()
        {
            if (_connectionState == ConnectionState.Connected || _connectionState == ConnectionState.Connecting)
            {
                Debug.LogWarning("[OptimizedWebSocketClient] Already connected or connecting");
                return;
            }
            
            StartCoroutine(ConnectCoroutine());
        }
        
        private IEnumerator ConnectCoroutine()
        {
            _connectionState = ConnectionState.Connecting;
            _statistics.ConnectionAttempts++;
            
            try
            {
                _connection = new WebSocketConnection(_serverUrl);
                _connection.OnOpen += OnConnectionOpened;
                _connection.OnMessage += OnMessageReceivedInternal;
                _connection.OnError += OnConnectionError;
                _connection.OnClose += OnConnectionClosed;
                
                var timeout = Time.time + _connectionTimeout;
                while (_connectionState == ConnectionState.Connecting && Time.time < timeout)
                {
                    yield return new WaitForSeconds(0.1f);
                }
                
                if (_connectionState != ConnectionState.Connected)
                {
                    HandleConnectionFailure("Connection timeout");
                }
            }
            catch (Exception ex)
            {
                HandleConnectionFailure($"Connection error: {ex.Message}");
            }
        }
        
        public void Disconnect()
        {
            if (_connectionState == ConnectionState.Disconnected)
                return;
            
            _connectionState = ConnectionState.Disconnecting;
            
            try
            {
                _connection?.Close();
            }
            catch (Exception ex)
            {
                Debug.LogError($"[OptimizedWebSocketClient] Error during disconnect: {ex.Message}");
            }
            
            _connectionState = ConnectionState.Disconnected;
            _reconnectAttempts = 0;
            
            Debug.Log("[OptimizedWebSocketClient] Disconnected");
        }
        
        private void OnConnectionOpened()
        {
            _connectionState = ConnectionState.Connected;
            _reconnectAttempts = 0;
            _lastHeartbeat = Time.time;
            _statistics.TotalConnections++;
            
            Debug.Log("[OptimizedWebSocketClient] Connected successfully");
            OnConnected?.Invoke();
        }
        
        private void OnConnectionClosed(string reason)
        {
            var wasConnected = _connectionState == ConnectionState.Connected;
            _connectionState = ConnectionState.Disconnected;
            
            if (wasConnected)
            {
                _statistics.Disconnections++;
                Debug.Log($"[OptimizedWebSocketClient] Connection closed: {reason}");
                OnDisconnected?.Invoke(reason);
                
                // Attempt reconnection if not intentional
                if (_reconnectAttempts < _maxReconnectAttempts)
                {
                    StartCoroutine(AttemptReconnection());
                }
            }
        }
        
        private void OnConnectionError(string error)
        {
            _statistics.Errors++;
            Debug.LogError($"[OptimizedWebSocketClient] Connection error: {error}");
            OnError?.Invoke(error);
            
            if (_connectionState != ConnectionState.Disconnected)
            {
                HandleConnectionFailure(error);
            }
        }
        
        private void HandleConnectionFailure(string reason)
        {
            _connectionState = ConnectionState.Disconnected;
            Debug.LogError($"[OptimizedWebSocketClient] Connection failed: {reason}");
            
            if (_reconnectAttempts < _maxReconnectAttempts)
            {
                StartCoroutine(AttemptReconnection());
            }
            else
            {
                OnError?.Invoke($"Max reconnection attempts exceeded: {reason}");
            }
        }
        
        private IEnumerator AttemptReconnection()
        {
            _reconnectAttempts++;
            var delay = _reconnectDelay * Mathf.Pow(2, _reconnectAttempts - 1); // Exponential backoff
            
            Debug.Log($"[OptimizedWebSocketClient] Reconnecting in {delay}s (attempt {_reconnectAttempts}/{_maxReconnectAttempts})");
            
            yield return new WaitForSeconds(delay);
            
            if (_connectionState == ConnectionState.Disconnected)
            {
                Connect();
            }
        }
        
        #endregion
        
        #region Message Handling
        
        public void SendMessage(string type, object data, MessagePriority priority = MessagePriority.Normal)
        {
            if (_connectionState != ConnectionState.Connected)
            {
                Debug.LogWarning("[OptimizedWebSocketClient] Cannot send message: not connected");
                return;
            }
            
            var message = new WebSocketMessage
            {
                Id = Guid.NewGuid().ToString("N")[0..8],
                Type = type,
                Data = data,
                Priority = priority,
                Timestamp = DateTime.Now,
                ConnectionId = _connectionId
            };
            
            // Check for duplicates
            if (_enableDuplicateFiltering && IsDuplicateMessage(message))
            {
                _statistics.DuplicatesFiltered++;
                return;
            }
            
            EnqueueMessage(message);
        }
        
        public void SendMessageImmediate(string type, object data)
        {
            if (_connectionState != ConnectionState.Connected)
            {
                Debug.LogWarning("[OptimizedWebSocketClient] Cannot send immediate message: not connected");
                return;
            }
            
            var message = new WebSocketMessage
            {
                Id = Guid.NewGuid().ToString("N")[0..8],
                Type = type,
                Data = data,
                Priority = MessagePriority.Critical,
                Timestamp = DateTime.Now,
                ConnectionId = _connectionId
            };
            
            SendMessageDirect(message);
        }
        
        private void EnqueueMessage(WebSocketMessage message)
        {
            if (_outgoingQueue.Count >= _maxMessageQueueSize)
            {
                // Remove oldest low priority message
                var queueArray = _outgoingQueue.ToArray();
                var lowPriorityMessage = queueArray.FirstOrDefault(m => m.Priority == MessagePriority.Low);
                
                if (lowPriorityMessage != null)
                {
                    var tempQueue = new Queue<WebSocketMessage>();
                    while (_outgoingQueue.Count > 0)
                    {
                        var msg = _outgoingQueue.Dequeue();
                        if (msg != lowPriorityMessage)
                        {
                            tempQueue.Enqueue(msg);
                        }
                    }
                    _outgoingQueue = tempQueue;
                    _statistics.MessagesDropped++;
                }
                else
                {
                    Debug.LogWarning("[OptimizedWebSocketClient] Message queue full, dropping oldest message");
                    _outgoingQueue.Dequeue();
                    _statistics.MessagesDropped++;
                }
            }
            
            _outgoingQueue.Enqueue(message);
            
            // Send critical messages immediately
            if (message.Priority == MessagePriority.Critical)
            {
                SendMessageDirect(message);
                return;
            }
            
            TrackRecentMessage(message);
        }
        
        private void SendMessageDirect(WebSocketMessage message)
        {
            try
            {
                var json = JsonUtility.ToJson(message);
                var data = _enableCompression ? CompressMessage(json) : Encoding.UTF8.GetBytes(json);
                
                _connection.Send(data);
                _messageSendTimes[message.Id] = Time.time;
                _statistics.MessagesSent++;
                
                _performanceMonitor?.TrackSystemActivity("WebSocket", 0.1f);
                
                if (message.Priority != MessagePriority.Critical)
                {
                    // Remove from queue since we sent it directly
                    var tempQueue = new Queue<WebSocketMessage>();
                    while (_outgoingQueue.Count > 0)
                    {
                        var msg = _outgoingQueue.Dequeue();
                        if (msg.Id != message.Id)
                        {
                            tempQueue.Enqueue(msg);
                        }
                    }
                    _outgoingQueue = tempQueue;
                }
            }
            catch (Exception ex)
            {
                _statistics.SendErrors++;
                Debug.LogError($"[OptimizedWebSocketClient] Failed to send message: {ex.Message}");
            }
        }
        
        #endregion
        
        #region Message Processing
        
        private IEnumerator MessageProcessingLoop()
        {
            while (true)
            {
                if (_connectionState == ConnectionState.Connected && _outgoingQueue.Count > 0)
                {
                    ProcessOutgoingMessages();
                }
                
                yield return new WaitForSeconds(0.01f); // Process every 10ms
            }
        }
        
        private void ProcessOutgoingMessages()
        {
            var messagesToSend = new List<WebSocketMessage>();
            var maxMessages = _enableMessageBatching ? _maxBatchSize : 1;
            
            // Prioritize messages
            if (_enableMessagePriority)
            {
                var queueArray = _outgoingQueue.ToArray();
                var prioritizedMessages = queueArray
                    .OrderByDescending(m => (int)m.Priority)
                    .ThenBy(m => m.Timestamp)
                    .Take(maxMessages)
                    .ToList();
                
                messagesToSend.AddRange(prioritizedMessages);
                
                // Remove processed messages from queue
                _outgoingQueue.Clear();
                foreach (var msg in queueArray.Except(messagesToSend))
                {
                    _outgoingQueue.Enqueue(msg);
                }
            }
            else
            {
                for (int i = 0; i < maxMessages && _outgoingQueue.Count > 0; i++)
                {
                    messagesToSend.Add(_outgoingQueue.Dequeue());
                }
            }
            
            if (_enableMessageBatching && messagesToSend.Count > 1)
            {
                SendMessageBatch(messagesToSend);
            }
            else
            {
                foreach (var message in messagesToSend)
                {
                    SendMessageDirect(message);
                }
            }
        }
        
        private IEnumerator MessageBatchingLoop()
        {
            while (true)
            {
                yield return new WaitForSeconds(_messageBatchInterval);
                
                if (_batchedMessages.Count > 0)
                {
                    var batch = _batchedMessages.ToList();
                    _batchedMessages.Clear();
                    SendMessageBatch(batch);
                }
            }
        }
        
        private void SendMessageBatch(List<WebSocketMessage> messages)
        {
            try
            {
                var batchMessage = new WebSocketMessage
                {
                    Id = Guid.NewGuid().ToString("N")[0..8],
                    Type = "batch",
                    Data = messages,
                    Priority = MessagePriority.Normal,
                    Timestamp = DateTime.Now,
                    ConnectionId = _connectionId
                };
                
                var json = JsonUtility.ToJson(batchMessage);
                var data = _enableCompression ? CompressMessage(json) : Encoding.UTF8.GetBytes(json);
                
                _connection.Send(data);
                _statistics.MessagesSent += messages.Count;
                _statistics.BatchesSent++;
                
                foreach (var message in messages)
                {
                    _messageSendTimes[message.Id] = Time.time;
                }
                
                _performanceMonitor?.TrackSystemActivity("WebSocket", messages.Count * 0.05f);
            }
            catch (Exception ex)
            {
                _statistics.SendErrors++;
                Debug.LogError($"[OptimizedWebSocketClient] Failed to send message batch: {ex.Message}");
            }
        }
        
        private void OnMessageReceivedInternal(byte[] data)
        {
            try
            {
                var json = _enableCompression ? DecompressMessage(data) : Encoding.UTF8.GetString(data);
                var message = JsonUtility.FromJson<WebSocketMessage>(json);
                
                _statistics.MessagesReceived++;
                
                // Track round-trip time
                if (_messageSendTimes.ContainsKey(message.Id))
                {
                    var roundTripTime = (Time.time - _messageSendTimes[message.Id]) * 1000f;
                    _statistics.TotalRoundTripTime += roundTripTime;
                    _statistics.RoundTripSamples++;
                    _messageSendTimes.Remove(message.Id);
                }
                
                ProcessIncomingMessage(message);
            }
            catch (Exception ex)
            {
                _statistics.ReceiveErrors++;
                Debug.LogError($"[OptimizedWebSocketClient] Failed to process incoming message: {ex.Message}");
            }
        }
        
        private void ProcessIncomingMessage(WebSocketMessage message)
        {
            // Handle system messages
            if (_messageHandlers.ContainsKey(message.Type))
            {
                _messageHandlers[message.Type](message);
            }
            
            OnMessageReceived?.Invoke(message);
        }
        
        private void ProcessIncomingMessages()
        {
            // This method is called from Update() to process any queued incoming messages
            // Implementation depends on your WebSocket library
        }
        
        #endregion
        
        #region Message Handlers
        
        public void RegisterMessageHandler(string messageType, Action<WebSocketMessage> handler)
        {
            _messageHandlers[messageType] = handler;
        }
        
        public void UnregisterMessageHandler(string messageType)
        {
            _messageHandlers.Remove(messageType);
        }
        
        private void HandleHeartbeat(WebSocketMessage message)
        {
            _lastHeartbeat = Time.time;
            // Respond to heartbeat
            SendMessageImmediate("heartbeat_response", new { timestamp = DateTime.Now });
        }
        
        private void HandlePing(WebSocketMessage message)
        {
            // Respond to ping with pong
            SendMessageImmediate("pong", message.Data);
        }
        
        private void HandleError(WebSocketMessage message)
        {
            Debug.LogError($"[OptimizedWebSocketClient] Server error: {message.Data}");
            OnError?.Invoke(message.Data?.ToString());
        }
        
        private void HandleBatchMessage(WebSocketMessage message)
        {
            if (message.Data is List<WebSocketMessage> batchedMessages)
            {
                foreach (var msg in batchedMessages)
                {
                    ProcessIncomingMessage(msg);
                }
                _statistics.BatchesReceived++;
            }
        }
        
        #endregion
        
        #region Heartbeat and Health
        
        private IEnumerator HeartbeatLoop()
        {
            while (true)
            {
                yield return new WaitForSeconds(_heartbeatInterval);
                
                if (_connectionState == ConnectionState.Connected)
                {
                    // Check if we've received a heartbeat recently
                    if (Time.time - _lastHeartbeat > _heartbeatInterval * 2)
                    {
                        Debug.LogWarning("[OptimizedWebSocketClient] Heartbeat timeout, connection may be lost");
                        HandleConnectionFailure("Heartbeat timeout");
                    }
                    else
                    {
                        // Send heartbeat
                        SendMessageImmediate("heartbeat", new { timestamp = DateTime.Now });
                    }
                }
            }
        }
        
        #endregion
        
        #region Performance Tracking
        
        private IEnumerator PerformanceTrackingLoop()
        {
            while (_enablePerformanceTracking)
            {
                yield return new WaitForSeconds(5f); // Update every 5 seconds
                
                UpdateStatistics();
                OnStatisticsUpdated?.Invoke(_statistics);
            }
        }
        
        private void UpdateStatistics()
        {
            _statistics.AverageRoundTripTime = _statistics.RoundTripSamples > 0 
                ? _statistics.TotalRoundTripTime / _statistics.RoundTripSamples : 0f;
            _statistics.MessageSuccessRate = _statistics.MessagesSent > 0 
                ? 1f - (float)_statistics.SendErrors / _statistics.MessagesSent : 0f;
            _statistics.QueuedMessages = _outgoingQueue.Count;
            _statistics.LastUpdated = DateTime.Now;
        }
        
        public WebSocketStatistics GetStatistics()
        {
            UpdateStatistics();
            return _statistics;
        }
        
        #endregion
        
        #region Utility Methods
        
        private bool IsDuplicateMessage(WebSocketMessage message)
        {
            var key = $"{message.Type}:{JsonUtility.ToJson(message.Data)}";
            
            if (_recentMessages.ContainsKey(key))
            {
                var timeDiff = (DateTime.Now - _recentMessages[key]).TotalSeconds;
                return timeDiff < _duplicateFilterWindow;
            }
            
            return false;
        }
        
        private void TrackRecentMessage(WebSocketMessage message)
        {
            var key = $"{message.Type}:{JsonUtility.ToJson(message.Data)}";
            _recentMessages[key] = DateTime.Now;
        }
        
        private void CleanupRecentMessages()
        {
            var cutoff = DateTime.Now.AddSeconds(-_duplicateFilterWindow * 2);
            var keysToRemove = _recentMessages
                .Where(kvp => kvp.Value < cutoff)
                .Select(kvp => kvp.Key)
                .ToList();
            
            foreach (var key in keysToRemove)
            {
                _recentMessages.Remove(key);
            }
        }
        
        private byte[] CompressMessage(string message)
        {
            // Simple compression simulation - in real implementation, use GZip
            return Encoding.UTF8.GetBytes(message);
        }
        
        private string DecompressMessage(byte[] data)
        {
            // Simple decompression simulation
            return Encoding.UTF8.GetString(data);
        }
        
        #endregion
        
        #region Public API
        
        public bool IsConnected => _connectionState == ConnectionState.Connected;
        public ConnectionState State => _connectionState;
        public string ConnectionId => _connectionId;
        
        public void SetServerUrl(string url)
        {
            if (_connectionState == ConnectionState.Disconnected)
            {
                _serverUrl = url;
                Debug.Log($"[OptimizedWebSocketClient] Server URL updated to: {url}");
            }
            else
            {
                Debug.LogWarning("[OptimizedWebSocketClient] Cannot change server URL while connected");
            }
        }
        
        public void ClearMessageQueue()
        {
            var count = _outgoingQueue.Count;
            _outgoingQueue.Clear();
            _batchedMessages.Clear();
            Debug.Log($"[OptimizedWebSocketClient] Cleared {count} queued messages");
        }
        
        #endregion
    }
    
    #region Data Classes
    
    [Serializable]
    public class WebSocketMessage
    {
        public string Id;
        public string Type;
        public object Data;
        public MessagePriority Priority;
        public DateTime Timestamp;
        public string ConnectionId;
    }
    
    [Serializable]
    public class WebSocketStatistics
    {
        public int TotalConnections;
        public int Disconnections;
        public int MessagesSent;
        public int MessagesReceived;
        public int SendErrors;
        public int ReceiveErrors;
        public int Errors;
        public int BatchesSent;
        public int BatchesReceived;
        public int MessagesDropped;
        public int DuplicatesFiltered;
        public int QueuedMessages;
        public float TotalRoundTripTime;
        public int RoundTripSamples;
        public float AverageRoundTripTime;
        public float MessageSuccessRate;
        public DateTime LastUpdated;
    }
    
    public enum ConnectionState
    {
        Disconnected,
        Connecting,
        Connected,
        Disconnecting
    }
    
    public enum MessagePriority
    {
        Low = 0,
        Normal = 1,
        High = 2,
        Critical = 3
    }
    
    #endregion
    
    #region WebSocket Connection Interface
    
    // This would be implemented by your actual WebSocket library
    public interface IWebSocketConnection
    {
        event Action OnOpen;
        event Action<byte[]> OnMessage;
        event Action<string> OnError;
        event Action<string> OnClose;
        
        void Send(byte[] data);
        void Close();
    }
    
    // Mock implementation for compilation
    public class WebSocketConnection : IWebSocketConnection
    {
        public event Action OnOpen;
        public event Action<byte[]> OnMessage;
        public event Action<string> OnError;
        public event Action<string> OnClose;
        
        public WebSocketConnection(string url)
        {
            // Initialize actual WebSocket connection here
        }
        
        public void Send(byte[] data)
        {
            // Send data through actual WebSocket
        }
        
        public void Close()
        {
            // Close actual WebSocket connection
        }
    }
    
    #endregion
} 