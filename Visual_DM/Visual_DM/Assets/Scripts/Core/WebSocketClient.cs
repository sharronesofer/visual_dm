using System;
using System.Collections;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using UnityEngine;
using System.Net.WebSockets;
using System.Text;

namespace VisualDM.Core
{
    /// <summary>
    /// Basic WebSocket client for real-time communication. Designed for runtime use only.
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

        private async Task ReceiveLoop()
        {
            var buffer = new byte[4096];
            while (_connected && _ws.State == WebSocketState.Open)
            {
                var result = await _ws.ReceiveAsync(new ArraySegment<byte>(buffer), _cts.Token);
                if (result.MessageType == WebSocketMessageType.Close)
                {
                    await Disconnect();
                    // Attempt to reconnect
                    await ReconnectAsync();
                    break;
                }
                var msg = Encoding.UTF8.GetString(buffer, 0, result.Count);
                // Dispatch to registered handler if message type matches
                // TODO: Parse message type from msg (stub)
                string messageType = "default"; // Replace with real parsing
                if (messageHandlers.TryGetValue(messageType, out var handler))
                    handler(msg);
                OnMessageReceived?.Invoke(msg);
            }
        }
    }
} 