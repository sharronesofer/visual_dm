using System;
using System.Collections;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using UnityEngine;
using System.Net.WebSockets;
using System.Text;
using VisualDM.Systems.EventSystem;

namespace VisualDM.Core
{
    /// <summary>
    /// Basic WebSocket client for real-time communication. Designed for runtime use only.
    /// Now uses EventBus and UINotificationEvent for notifications.
    /// </summary>
    public class WebSocketClient : MonoBehaviour
    {
        private ClientWebSocket _ws;
        private CancellationTokenSource _cts;
        private Uri _uri;
        private bool _connected;
        private readonly Dictionary<string, Action<string>> messageHandlers = new Dictionary<string, Action<string>>();
        private string jwtToken;
        private string clientId;
        private string serverUri;
        private int width;
        private int height;

        public event Action<string> OnMessageReceived;
        public event Action OnConnected;
        public event Action OnDisconnected;
        public event Action<Exception> OnError;
        public event Action<string, string> OnNotification;
        public event Action<string, int> OnErrorMessage;
        public event Action<string, bool, float?> OnPresence;
        public event Action<string, bool> OnTyping;
        public event Action<string> OnRawMessage;

        public void RegisterMessageHandler(string messageType, Action<string> handler)
        {
            messageHandlers[messageType] = handler;
        }

        public async Task ConnectAsync(string server, string token, string clientId, int width, int height)
        {
            this.serverUri = server;
            this.jwtToken = token;
            this.clientId = clientId;
            this.width = width;
            this.height = height;
            await Connect($"ws://{server}");
        }

        public async Task ReconnectAsync()
        {
            if (!string.IsNullOrEmpty(serverUri) && !string.IsNullOrEmpty(jwtToken) && !string.IsNullOrEmpty(clientId))
            {
                await ConnectAsync(serverUri, jwtToken, clientId, width, height);
            }
        }

        public async Task Connect(string uri)
        {
            _uri = new Uri(uri);
            _ws = new ClientWebSocket();
            _cts = new CancellationTokenSource();
            try
            {
                await _ws.ConnectAsync(_uri, _cts.Token);
                _connected = true;
                OnConnected?.Invoke();
                _ = ReceiveLoop();
            }
            catch (Exception ex)
            {
                OnError?.Invoke(ex);
            }
        }

        public async Task Send(string message)
        {
            if (_ws == null || !_connected) return;
            var bytes = Encoding.UTF8.GetBytes(message);
            var buffer = new ArraySegment<byte>(bytes);
            await _ws.SendAsync(buffer, WebSocketMessageType.Text, true, _cts.Token);
        }

        public async Task Disconnect()
        {
            if (_ws == null || !_connected) return;
            _connected = false;
            await _ws.CloseAsync(WebSocketCloseStatus.NormalClosure, "Disconnect", _cts.Token);
            _ws.Dispose();
            _cts.Cancel();
            OnDisconnected?.Invoke();
        }

        public async Task SubscribeAsync(string channel)
        {
            var msg = $"{{\"type\":\"subscribe\",\"channel\":\"{channel}\"}}";
            await Send(msg);
        }

        public async Task UnsubscribeAsync(string channel)
        {
            var msg = $"{{\"type\":\"unsubscribe\",\"channel\":\"{channel}\"}}";
            await Send(msg);
        }

        public async Task SendTypingAsync(bool isTyping)
        {
            var msg = $"{{\"type\":\"typing\",\"is_typing\":{(isTyping ? "true" : "false")}}}";
            await Send(msg);
        }

        private async Task ReceiveLoop()
        {
            var buffer = new byte[4096];
            while (_connected && _ws.State == WebSocketState.Open)
            {
                var result = await _ws.ReceiveAsync(new ArraySegment<byte>(buffer), _cts.Token);
                if (result.MessageType == WebSocketMessageType.Close)
                {
                    await Disconnect();
                    await ReconnectAsync();
                    break;
                }
                var msg = Encoding.UTF8.GetString(buffer, 0, result.Count);
                // Parse message type from JSON (expects { "type": "...", ... })
                string messageType = "default";
                try
                {
                    var json = JsonUtility.FromJson<WSMessage>(msg);
                    if (!string.IsNullOrEmpty(json.type))
                        messageType = json.type;
                    switch (json.type)
                    {
                        case "notification":
                            OnNotification?.Invoke(json.message, json.level);
                            try
                            {
                                var evt = new UINotificationEvent(
                                    json.message,
                                    json.level,
                                    DateTime.UtcNow
                                );
                                EventBus.Instance.Publish(evt);
                            }
                            catch (Exception ex)
                            {
                                Debug.LogError($"[WebSocketClient] Failed to publish notification event: {ex.Message}");
                            }
                            break;
                        case "error":
                            OnErrorMessage?.Invoke(json.message, json.code);
                            break;
                        case "presence":
                            OnPresence?.Invoke(json.client_id, json.online, json.last_seen);
                            break;
                        case "typing":
                            OnTyping?.Invoke(json.client_id, json.is_typing);
                            break;
                        default:
                            OnRawMessage?.Invoke(msg);
                            break;
                    }
                }
                catch
                {
                    // If parsing fails, fallback to default
                    OnRawMessage?.Invoke(msg);
                }
                if (messageHandlers.TryGetValue(messageType, out var handler))
                    handler(msg);
                OnMessageReceived?.Invoke(msg);
            }
        }
    }

    [Serializable]
    private class WSMessage
    {
        public string type;
        public string message;
        public string level;
        public int code;
        public string client_id;
        public bool online;
        public float last_seen;
        public bool is_typing;
    }
}