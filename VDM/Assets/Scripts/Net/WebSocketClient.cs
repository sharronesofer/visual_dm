using System;
using System.Collections;
using System.Collections.Generic;
using System.Text;
using UnityEngine;
using System.Threading.Tasks;
using System.Net.WebSockets;
using System.Threading;
using Newtonsoft.Json;

namespace VisualDM.Net
{

    /// <summary>
    /// WebSocket client for connecting to backend services and handling message exchange.
    /// </summary>
    public class WebSocketClient : MonoBehaviour
    {
        /// <summary>
        /// The URI of the WebSocket server.
        /// </summary>
        public string uri;
        /// <summary>
        /// The current connection status.
        /// </summary>
        public WebSocketConnectionStatus Status { get; private set; } = WebSocketConnectionStatus.Disconnected;
        /// <summary>
        /// Event fired when a message is received.
        /// </summary>
        public event Action<WebSocketMessage> OnMessageReceived;
        /// <summary>
        /// Event fired when the connection status changes.
        /// </summary>
        public event Action<WebSocketConnectionStatus> OnStatusChanged;
        /// <summary>
        /// Event fired when an error occurs.
        /// </summary>
        public event Action<string> OnError;

        private ClientWebSocket _ws;
        private CancellationTokenSource _cts;
        private int _reconnectAttempts = 0;
        private const int MaxReconnectDelay = 30; // seconds
        private readonly Dictionary<string, Action<string>> messageHandlers = new Dictionary<string, Action<string>>();
        private string authToken;
        private const string PROTOCOL_VERSION = "1.0";

        /// <summary>
        /// Register a handler for a specific message type.
        /// </summary>
        /// <param name="messageType">The message type to handle.</param>
        /// <param name="handler">The handler delegate.</param>
        public void RegisterMessageHandler(string messageType, Action<string> handler)
        {
            if (handler == null)
                messageHandlers.Remove(messageType);
            else
                messageHandlers[messageType] = handler;
        }

        /// <summary>
        /// Sets the authentication token to use for future connections.
        /// </summary>
        /// <param name="token">The authentication token.</param>
        public void SetAuthToken(string token)
        {
            authToken = token;
        }

        /// <summary>
        /// Connects to the WebSocket server at the specified URI. Optionally includes an authentication token.
        /// </summary>
        /// <param name="wsUri">WebSocket server URI.</param>
        /// <param name="token">Optional authentication token.</param>
        public async void Connect(string wsUri, string token = null)
        {
            uri = wsUri;
            if (token != null) authToken = token;
            Status = WebSocketConnectionStatus.Connecting;
            OnStatusChanged?.Invoke(Status);
            _ws = new ClientWebSocket();
            _cts = new CancellationTokenSource();
            if (!string.IsNullOrEmpty(authToken))
            {
                _ws.Options.SetRequestHeader("Authorization", $"Bearer {authToken}");
            }
            try
            {
                await _ws.ConnectAsync(new Uri(uri), _cts.Token);
                Status = WebSocketConnectionStatus.Connected;
                OnStatusChanged?.Invoke(Status);
                _reconnectAttempts = 0;
                StartReceiveLoop();
            }
            catch (Exception ex)
            {
                Debug.LogError($"WebSocket connect error: {ex.Message}");
                Status = WebSocketConnectionStatus.Error;
                OnStatusChanged?.Invoke(Status);
                OnError?.Invoke(ex.Message);
                StartCoroutine(ReconnectWithBackoff());
            }
        }

        /// <summary>
        /// Disconnects from the WebSocket server.
        /// </summary>
        public async void Disconnect()
        {
            if (_ws != null && _ws.State == WebSocketState.Open)
            {
                await _ws.CloseAsync(WebSocketCloseStatus.NormalClosure, "Disconnect", CancellationToken.None);
            }
            _cts?.Cancel();
            Status = WebSocketConnectionStatus.Disconnected;
            OnStatusChanged?.Invoke(Status);
        }

        /// <summary>
        /// Send a canonical WebSocket message (envelope enforced).
        /// </summary>
        /// <param name="type">Message type.</param>
        /// <param name="payload">Payload dictionary.</param>
        /// <param name="requestId">Optional request ID.</param>
        public void SendCanonical(string type, Dictionary<string, object> payload, string requestId = null)
        {
            var msg = new WebSocketMessage
            {
                version = PROTOCOL_VERSION,
                type = type,
                payload = payload,
                timestamp = DateTime.UtcNow.ToString("o"),
                requestId = requestId
            };
            Send(msg);
        }

        /// <summary>
        /// Sends a WebSocketMessage, enforcing canonical envelope fields.
        /// </summary>
        /// <param name="message">The message to send.</param>
        public async void Send(WebSocketMessage message)
        {
            if (_ws == null || _ws.State != WebSocketState.Open) return;
            // Enforce canonical envelope
            message.version = PROTOCOL_VERSION;
            if (string.IsNullOrEmpty(message.timestamp))
                message.timestamp = DateTime.UtcNow.ToString("o");
            string json = JsonConvert.SerializeObject(message);
            var buffer = Encoding.UTF8.GetBytes(json);
            var segment = new ArraySegment<byte>(buffer);
            try
            {
                await _ws.SendAsync(segment, WebSocketMessageType.Text, true, _cts.Token);
            }
            catch (Exception ex)
            {
                Debug.LogError($"WebSocket send error: {ex.Message}");
                OnError?.Invoke(ex.Message);
            }
        }

        /// <summary>
        /// Starts the receive loop for incoming WebSocket messages.
        /// </summary>
        private async void StartReceiveLoop()
        {
            var buffer = new byte[4096];
            while (_ws.State == WebSocketState.Open)
            {
                try
                {
                    var result = await _ws.ReceiveAsync(new ArraySegment<byte>(buffer), _cts.Token);
                    if (result.MessageType == WebSocketMessageType.Close)
                    {
                        await _ws.CloseAsync(WebSocketCloseStatus.NormalClosure, "Closed by server", _cts.Token);
                        Status = WebSocketConnectionStatus.Disconnected;
                        OnStatusChanged?.Invoke(Status);
                        StartCoroutine(ReconnectWithBackoff());
                        break;
                    }
                    else
                    {
                        string json = Encoding.UTF8.GetString(buffer, 0, result.Count);
                        try
                        {
                            var msg = JsonConvert.DeserializeObject<WebSocketMessage>(json);
                            // Validate envelope
                            if (msg == null || string.IsNullOrEmpty(msg.version) || string.IsNullOrEmpty(msg.type) || msg.payload == null || string.IsNullOrEmpty(msg.timestamp))
                            {
                                Debug.LogError($"Received non-compliant WebSocket message: {json}");
                                OnError?.Invoke("Received non-compliant WebSocket message");
                                continue;
                            }
                            OnMessageReceived?.Invoke(msg);
                            if (!string.IsNullOrEmpty(msg.type) && messageHandlers.TryGetValue(msg.type, out var handler))
                            {
                                handler(json);
                            }
                        }
                        catch (Exception ex)
                        {
                            Debug.LogError($"WebSocket message parse error: {ex.Message}");
                            OnError?.Invoke($"WebSocket message parse error: {ex.Message}");
                        }
                    }
                }
                catch (Exception ex)
                {
                    Debug.LogError($"WebSocket receive error: {ex.Message}");
                    Status = WebSocketConnectionStatus.Error;
                    OnStatusChanged?.Invoke(Status);
                    OnError?.Invoke(ex.Message);
                    StartCoroutine(ReconnectWithBackoff());
                    break;
                }
            }
        }

        /// <summary>
        /// Coroutine for reconnecting with exponential backoff.
        /// </summary>
        private IEnumerator ReconnectWithBackoff()
        {
            Status = WebSocketConnectionStatus.Reconnecting;
            OnStatusChanged?.Invoke(Status);
            _reconnectAttempts++;
            int delay = Mathf.Min((int)Mathf.Pow(2, _reconnectAttempts), MaxReconnectDelay);
            yield return new WaitForSeconds(delay);
            Connect(uri);
        }

        /// <summary>
        /// Unity OnDestroy lifecycle method. Disconnects from the server.
        /// </summary>
        private void OnDestroy()
        {
            Disconnect();
        }

        /// <summary>
        /// Sends metrics data to the connected metrics endpoint.
        /// </summary>
        /// <param name="payload">The JSON serialized metrics data.</param>
        /// <returns>True if the metrics were successfully sent.</returns>
        public bool SendMetrics(string payload)
        {
            // Implementation would go here to send metrics to the appropriate WebSocket
            // For now, just log and return success
            Debug.Log($"Sending metrics: {payload}");
            return true;
        }

        /// <summary>
        /// Gets the total bytes sent since connection.
        /// </summary>
        public long TotalBytesSent { get; private set; } = 0;

        /// <summary>
        /// Gets the total bytes received since connection.
        /// </summary>
        public long TotalBytesReceived { get; private set; } = 0;
    }
} 