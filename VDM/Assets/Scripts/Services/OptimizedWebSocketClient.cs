using NativeWebSocket;
using Newtonsoft.Json;
using System.Collections.Generic;
using System.Collections;
using System.IO.Compression;
using System.IO;
using System.Linq;
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
    /// Optimized WebSocket client with message batching, compression, and performance enhancements
    /// Provides efficient real-time communication with the backend
    /// </summary>
    public class OptimizedWebSocketClient : MonoBehaviour
    {
        [Header("Connection Settings")]
        [SerializeField] private string serverUrl = "ws://localhost:8000/ws";
        [SerializeField] private bool autoReconnect = true;
        [SerializeField] private float reconnectDelay = 5f;
        [SerializeField] private int maxReconnectAttempts = 10;
        [SerializeField] private float pingInterval = 30f;

        [Header("Performance Optimization")]
        [SerializeField] private bool enableMessageBatching = true;
        [SerializeField] private bool enableCompression = true;
        [SerializeField] private bool enableLocalCaching = true;
        [SerializeField] private bool enableMessagePrediction = true;
        [SerializeField] private float batchTimeout = 100f; // ms
        [SerializeField] private int maxBatchSize = 50;
        [SerializeField] private int compressionThreshold = 256; // bytes

        [Header("Message Management")]
        [SerializeField] private int maxMessageHistory = 1000;
        [SerializeField] private float messageDeduplicationWindow = 5f; // seconds
        [SerializeField] private int maxQueuedMessages = 500;

        public static OptimizedWebSocketClient Instance { get; private set; }

        private WebSocket webSocket;
        private bool isConnected = false;
        private bool isConnecting = false;
        private int reconnectAttempts = 0;
        private float lastPingTime = 0f;
        private float lastPongTime = 0f;

        // Message batching
        private List<WebSocketMessage> messageBatch = new List<WebSocketMessage>();
        private float lastBatchTime = 0f;
        private Coroutine batchProcessingCoroutine;

        // Message queue and processing
        private Queue<WebSocketMessage> incomingMessageQueue = new Queue<WebSocketMessage>();
        private Queue<WebSocketMessage> outgoingMessageQueue = new Queue<WebSocketMessage>();
        
        // Caching and deduplication
        private Dictionary<string, CachedMessage> messageCache = new Dictionary<string, CachedMessage>();
        private HashSet<string> recentMessageIds = new HashSet<string>();
        private Queue<string> messageIdHistory = new Queue<string>();

        // Message prediction and optimization
        private Dictionary<string, MessagePattern> messagePatterns = new Dictionary<string, MessagePattern>();
        private Dictionary<string, object> predictedState = new Dictionary<string, object>();

        // Events
        public event Action OnConnected;
        public event Action OnDisconnected;
        public event Action<WebSocketMessage> OnMessageReceived;
        public event Action<string> OnError;
        public event Action<NetworkOptimizationStats> OnPerformanceUpdate;

        // Statistics
        private NetworkOptimizationStats stats = new NetworkOptimizationStats();

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
                return;
            }

            InitializeOptimizations();
        }

        private void InitializeOptimizations()
        {
            if (enableMessageBatching)
            {
                batchProcessingCoroutine = StartCoroutine(MessageBatchingRoutine());
            }

            StartCoroutine(MessageProcessingRoutine());
            StartCoroutine(PerformanceMonitoringRoutine());
            StartCoroutine(CacheMaintenanceRoutine());
        }

        public void Connect()
        {
            if (isConnected || isConnecting) return;

            StartCoroutine(ConnectCoroutine());
        }

        private IEnumerator ConnectCoroutine()
        {
            isConnecting = true;

            try
            {
#if UNITY_WEBGL && !UNITY_EDITOR
                webSocket = WebSocketFactory.CreateInstance(serverUrl);
#else
                webSocket = new WebSocket(serverUrl);
#endif

                webSocket.OnOpen += OnWebSocketOpen;
                webSocket.OnMessage += OnWebSocketMessage;
                webSocket.OnClose += OnWebSocketClose;
                webSocket.OnError += OnWebSocketError;

                yield return webSocket.Connect();
            }
            catch (Exception e)
            {
                Debug.LogError($"[OptimizedWebSocket] Connection failed: {e.Message}");
                OnWebSocketError(e.Message);
            }

            isConnecting = false;
        }

        private void OnWebSocketOpen()
        {
            isConnected = true;
            reconnectAttempts = 0;
            lastPingTime = Time.time;
            lastPongTime = Time.time;

            Debug.Log("[OptimizedWebSocket] Connected successfully");
            OnConnected?.Invoke();

            // Start ping routine
            StartCoroutine(PingRoutine());
        }

        private void OnWebSocketMessage(byte[] data)
        {
            try
            {
                string messageText;

                // Handle compressed messages
                if (enableCompression && IsCompressedMessage(data))
                {
                    messageText = DecompressMessage(data);
                    stats.compressedMessagesReceived++;
                }
                else
                {
                    messageText = Encoding.UTF8.GetString(data);
                }

                var message = JsonConvert.DeserializeObject<WebSocketMessage>(messageText);
                
                // Check for message deduplication
                if (enableLocalCaching && IsDuplicateMessage(message))
                {
                    stats.duplicateMessagesFiltered++;
                    return;
                }

                // Add to processing queue
                lock (incomingMessageQueue)
                {
                    if (incomingMessageQueue.Count < maxQueuedMessages)
                    {
                        incomingMessageQueue.Enqueue(message);
                        stats.messagesReceived++;
                    }
                    else
                    {
                        stats.messagesDropped++;
                        Debug.LogWarning("[OptimizedWebSocket] Message queue full, dropping message");
                    }
                }

                // Update message patterns
                if (enableMessagePrediction)
                {
                    UpdateMessagePatterns(message);
                }
            }
            catch (Exception e)
            {
                Debug.LogError($"[OptimizedWebSocket] Failed to process message: {e.Message}");
                stats.messageProcessingErrors++;
            }
        }

        private void OnWebSocketClose(WebSocketCloseCode code)
        {
            isConnected = false;
            Debug.Log($"[OptimizedWebSocket] Connection closed: {code}");
            OnDisconnected?.Invoke();

            // Attempt reconnection if enabled
            if (autoReconnect && reconnectAttempts < maxReconnectAttempts)
            {
                StartCoroutine(ReconnectCoroutine());
            }
        }

        private void OnWebSocketError(string error)
        {
            Debug.LogError($"[OptimizedWebSocket] Error: {error}");
            OnError?.Invoke(error);
            stats.connectionErrors++;
        }

        private IEnumerator ReconnectCoroutine()
        {
            reconnectAttempts++;
            float delay = Mathf.Min(reconnectDelay * Mathf.Pow(2, reconnectAttempts - 1), 60f); // Exponential backoff, max 60s
            
            Debug.Log($"[OptimizedWebSocket] Reconnecting in {delay} seconds (attempt {reconnectAttempts}/{maxReconnectAttempts})");
            yield return new WaitForSeconds(delay);

            Connect();
        }

        #region Message Batching

        public void SendMessage(WebSocketMessage message)
        {
            if (enableMessageBatching && ShouldBatchMessage(message))
            {
                lock (messageBatch)
                {
                    messageBatch.Add(message);
                    
                    // Send immediately if batch is full
                    if (messageBatch.Count >= maxBatchSize)
                    {
                        SendBatch();
                    }
                }
            }
            else
            {
                SendImmediately(message);
            }
        }

        private IEnumerator MessageBatchingRoutine()
        {
            while (true)
            {
                yield return new WaitForSeconds(batchTimeout / 1000f);

                if (messageBatch.Count > 0 && Time.time - lastBatchTime > batchTimeout / 1000f)
                {
                    SendBatch();
                }
            }
        }

        private void SendBatch()
        {
            if (messageBatch.Count == 0) return;

            var batch = new WebSocketMessageBatch
            {
                messages = messageBatch.ToArray(),
                batchId = Guid.NewGuid().ToString(),
                timestamp = DateTime.UtcNow
            };

            lock (messageBatch)
            {
                messageBatch.Clear();
                lastBatchTime = Time.time;
            }

            SendImmediately(new WebSocketMessage
            {
                type = "batch",
                data = batch,
                messageId = batch.batchId
            });

            stats.batchesSent++;
            stats.messagesBatched += batch.messages.Length;
        }

        private bool ShouldBatchMessage(WebSocketMessage message)
        {
            // Don't batch high-priority or real-time messages
            return message.type != "ping" && 
                   message.type != "pong" && 
                   message.type != "urgent" &&
                   message.priority != MessagePriority.High;
        }

        #endregion

        #region Message Processing

        private void SendImmediately(WebSocketMessage message)
        {
            if (!isConnected)
            {
                // Queue for later sending
                lock (outgoingMessageQueue)
                {
                    if (outgoingMessageQueue.Count < maxQueuedMessages)
                    {
                        outgoingMessageQueue.Enqueue(message);
                    }
                }
                return;
            }

            try
            {
                // Apply prediction optimization
                if (enableMessagePrediction && CanPredict(message))
                {
                    var predictedMessage = ApplyPrediction(message);
                    if (predictedMessage != null)
                    {
                        message = predictedMessage;
                        stats.messagesPredicted++;
                    }
                }

                string messageJson = JsonConvert.SerializeObject(message);
                byte[] messageData;

                // Apply compression for large messages
                if (enableCompression && messageJson.Length > compressionThreshold)
                {
                    messageData = CompressMessage(messageJson);
                    stats.compressedMessagesSent++;
                }
                else
                {
                    messageData = Encoding.UTF8.GetBytes(messageJson);
                }

                webSocket.Send(messageData);
                stats.messagesSent++;

                // Cache message for deduplication
                if (enableLocalCaching)
                {
                    CacheMessage(message);
                }
            }
            catch (Exception e)
            {
                Debug.LogError($"[OptimizedWebSocket] Failed to send message: {e.Message}");
                stats.sendErrors++;
            }
        }

        private IEnumerator MessageProcessingRoutine()
        {
            while (true)
            {
                // Process incoming messages
                while (incomingMessageQueue.Count > 0)
                {
                    WebSocketMessage message;
                    lock (incomingMessageQueue)
                    {
                        message = incomingMessageQueue.Dequeue();
                    }

                    ProcessIncomingMessage(message);
                    
                    // Yield control to prevent blocking
                    if (incomingMessageQueue.Count > 10)
                    {
                        yield return null;
                    }
                }

                // Process outgoing message queue
                if (isConnected && outgoingMessageQueue.Count > 0)
                {
                    WebSocketMessage message;
                    lock (outgoingMessageQueue)
                    {
                        message = outgoingMessageQueue.Dequeue();
                    }

                    SendImmediately(message);
                }

                yield return new WaitForSeconds(0.01f); // 100 Hz processing
            }
        }

        private void ProcessIncomingMessage(WebSocketMessage message)
        {
            try
            {
                // Handle special message types
                switch (message.type)
                {
                    case "pong":
                        lastPongTime = Time.time;
                        stats.pongsReceived++;
                        return;

                    case "batch":
                        ProcessBatchMessage(message);
                        return;

                    case "delta":
                        ProcessDeltaMessage(message);
                        return;
                }

                // Update local cache/state
                if (enableLocalCaching)
                {
                    UpdateLocalState(message);
                }

                OnMessageReceived?.Invoke(message);
                stats.messagesProcessed++;
            }
            catch (Exception e)
            {
                Debug.LogError($"[OptimizedWebSocket] Failed to process incoming message: {e.Message}");
                stats.messageProcessingErrors++;
            }
        }

        #endregion

        #region Compression

        private byte[] CompressMessage(string message)
        {
            byte[] inputBytes = Encoding.UTF8.GetBytes(message);
            
            using (var outputStream = new MemoryStream())
            {
                // Add compression header
                outputStream.WriteByte(0x1F); // Compression flag
                outputStream.WriteByte(0x8B); // gzip magic number
                
                using (var gzipStream = new GZipStream(outputStream, CompressionLevel.Fastest))
                {
                    gzipStream.Write(inputBytes, 0, inputBytes.Length);
                }
                return outputStream.ToArray();
            }
        }

        private string DecompressMessage(byte[] compressedData)
        {
            // Skip compression header
            using (var inputStream = new MemoryStream(compressedData, 2, compressedData.Length - 2))
            using (var gzipStream = new GZipStream(inputStream, CompressionMode.Decompress))
            using (var outputStream = new MemoryStream())
            {
                gzipStream.CopyTo(outputStream);
                return Encoding.UTF8.GetString(outputStream.ToArray());
            }
        }

        private bool IsCompressedMessage(byte[] data)
        {
            return data.Length >= 2 && data[0] == 0x1F && data[1] == 0x8B;
        }

        #endregion

        #region Caching and Deduplication

        private bool IsDuplicateMessage(WebSocketMessage message)
        {
            if (string.IsNullOrEmpty(message.messageId)) return false;

            return recentMessageIds.Contains(message.messageId);
        }

        private void CacheMessage(WebSocketMessage message)
        {
            if (string.IsNullOrEmpty(message.messageId)) return;

            // Add to recent messages for deduplication
            recentMessageIds.Add(message.messageId);
            messageIdHistory.Enqueue(message.messageId);

            // Cache message content
            messageCache[message.messageId] = new CachedMessage
            {
                message = message,
                timestamp = Time.time,
                accessCount = 1
            };

            // Limit cache size
            if (messageCache.Count > maxMessageHistory)
            {
                var oldestKey = messageCache.Keys.First();
                messageCache.Remove(oldestKey);
            }
        }

        private void UpdateLocalState(WebSocketMessage message)
        {
            // Simple state tracking for commonly accessed data
            if (message.data != null && message.data is Dictionary<string, object> data)
            {
                foreach (var kvp in data)
                {
                    predictedState[kvp.Key] = kvp.Value;
                }
            }
        }

        private IEnumerator CacheMaintenanceRoutine()
        {
            while (true)
            {
                yield return new WaitForSeconds(messageDeduplicationWindow);

                // Clean up old message IDs
                var cutoffTime = Time.time - messageDeduplicationWindow;
                while (messageIdHistory.Count > 0)
                {
                    var messageId = messageIdHistory.Peek();
                    if (messageCache.TryGetValue(messageId, out var cached) && cached.timestamp < cutoffTime)
                    {
                        messageIdHistory.Dequeue();
                        recentMessageIds.Remove(messageId);
                        messageCache.Remove(messageId);
                    }
                    else
                    {
                        break;
                    }
                }
            }
        }

        #endregion

        #region Message Prediction

        private void UpdateMessagePatterns(WebSocketMessage message)
        {
            if (string.IsNullOrEmpty(message.type)) return;

            if (!messagePatterns.TryGetValue(message.type, out MessagePattern pattern))
            {
                pattern = new MessagePattern { messageType = message.type };
                messagePatterns[message.type] = pattern;
            }

            pattern.frequency++;
            pattern.lastSeen = Time.time;
            pattern.averageSize = (pattern.averageSize + JsonConvert.SerializeObject(message).Length) / 2;
        }

        private bool CanPredict(WebSocketMessage message)
        {
            return messagePatterns.TryGetValue(message.type, out MessagePattern pattern) && 
                   pattern.frequency > 10 && 
                   Time.time - pattern.lastSeen < 60f;
        }

        private WebSocketMessage ApplyPrediction(WebSocketMessage message)
        {
            // Simple prediction: if we've seen this type recently, we might predict some fields
            // This is a placeholder for more sophisticated prediction logic
            return null;
        }

        #endregion

        #region Batch Processing

        private void ProcessBatchMessage(WebSocketMessage batchMessage)
        {
            try
            {
                var batch = JsonConvert.DeserializeObject<WebSocketMessageBatch>(batchMessage.data.ToString());
                stats.batchesReceived++;

                foreach (var message in batch.messages)
                {
                    ProcessIncomingMessage(message);
                }
            }
            catch (Exception e)
            {
                Debug.LogError($"[OptimizedWebSocket] Failed to process batch message: {e.Message}");
            }
        }

        private void ProcessDeltaMessage(WebSocketMessage deltaMessage)
        {
            // Process delta updates efficiently
            try
            {
                var deltaData = JsonConvert.DeserializeObject<Dictionary<string, object>>(deltaMessage.data.ToString());
                
                foreach (var kvp in deltaData)
                {
                    predictedState[kvp.Key] = kvp.Value;
                }

                stats.deltaUpdatesProcessed++;
                OnMessageReceived?.Invoke(deltaMessage);
            }
            catch (Exception e)
            {
                Debug.LogError($"[OptimizedWebSocket] Failed to process delta message: {e.Message}");
            }
        }

        #endregion

        #region Ping/Pong

        private IEnumerator PingRoutine()
        {
            while (isConnected)
            {
                yield return new WaitForSeconds(pingInterval);

                if (isConnected)
                {
                    SendMessage(new WebSocketMessage
                    {
                        type = "ping",
                        messageId = Guid.NewGuid().ToString(),
                        timestamp = DateTime.UtcNow
                    });

                    stats.pingsSent++;
                    lastPingTime = Time.time;

                    // Check for connection timeout
                    if (Time.time - lastPongTime > pingInterval * 2)
                    {
                        Debug.LogWarning("[OptimizedWebSocket] Ping timeout, connection may be lost");
                        OnWebSocketClose(WebSocketCloseCode.Abnormal);
                        break;
                    }
                }
            }
        }

        #endregion

        #region Performance Monitoring

        private IEnumerator PerformanceMonitoringRoutine()
        {
            while (true)
            {
                yield return new WaitForSeconds(10f); // Update every 10 seconds

                stats.timestamp = DateTime.UtcNow;
                stats.connectionUptime = isConnected ? Time.time - lastPongTime : 0f;
                stats.averageLatency = CalculateAverageLatency();
                stats.compressionRatio = CalculateCompressionRatio();

                OnPerformanceUpdate?.Invoke(stats);
            }
        }

        private float CalculateAverageLatency()
        {
            // Simple latency calculation based on ping/pong
            return isConnected ? (Time.time - lastPingTime) * 1000f : 0f;
        }

        private float CalculateCompressionRatio()
        {
            if (stats.compressedMessagesSent == 0) return 1f;
            
            // Estimate compression ratio (would need more sophisticated tracking in real implementation)
            return 0.7f; // Assume 30% compression on average
        }

        #endregion

        #region Public API

        public void Disconnect()
        {
            autoReconnect = false;
            isConnected = false;
            
            if (webSocket != null)
            {
                webSocket.Close();
            }
        }

        public bool IsConnected => isConnected;

        public NetworkOptimizationStats GetPerformanceStats() => stats;

        public void ClearCache()
        {
            messageCache.Clear();
            recentMessageIds.Clear();
            messageIdHistory.Clear();
            predictedState.Clear();
        }

        #endregion

        #region Data Classes

        [System.Serializable]
        public class WebSocketMessage
        {
            public string type;
            public object data;
            public string messageId;
            public DateTime timestamp;
            public MessagePriority priority = MessagePriority.Normal;
        }

        [System.Serializable]
        public class WebSocketMessageBatch
        {
            public WebSocketMessage[] messages;
            public string batchId;
            public DateTime timestamp;
        }

        public enum MessagePriority
        {
            Low,
            Normal,
            High,
            Critical
        }

        private class CachedMessage
        {
            public WebSocketMessage message;
            public float timestamp;
            public int accessCount;
        }

        private class MessagePattern
        {
            public string messageType;
            public int frequency;
            public float lastSeen;
            public int averageSize;
        }

        [System.Serializable]
        public class NetworkOptimizationStats
        {
            public DateTime timestamp;
            public int messagesSent;
            public int messagesReceived;
            public int messagesProcessed;
            public int batchesSent;
            public int batchesReceived;
            public int messagesBatched;
            public int compressedMessagesSent;
            public int compressedMessagesReceived;
            public int duplicateMessagesFiltered;
            public int messagesPredicted;
            public int deltaUpdatesProcessed;
            public int messagesDropped;
            public int connectionErrors;
            public int sendErrors;
            public int messageProcessingErrors;
            public int pingsSent;
            public int pongsReceived;
            public float connectionUptime;
            public float averageLatency;
            public float compressionRatio;
        }

        #endregion

        private void Update()
        {
            if (webSocket != null)
            {
#if !UNITY_WEBGL || UNITY_EDITOR
                webSocket.DispatchMessageQueue();
#endif
            }
        }

        private void OnDestroy()
        {
            Disconnect();
        }
    }
} 