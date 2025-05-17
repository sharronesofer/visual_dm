using System;
using System.Collections.Generic;
using System.Net.WebSockets;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using UnityEngine;

/// <summary>
/// WebSocket client for Unity 2D runtime. Handles real-time communication with backend.
/// </summary>
public class WebSocketClient : MonoBehaviour
{
    private ClientWebSocket _ws;
    private CancellationTokenSource _cts;
    private Uri _serverUri;
    private string _token;
    private string _clientId;
    private int _width;
    private int _height;
    private readonly Dictionary<string, Action<string>> _eventHandlers = new();
    private readonly Queue<string> _receiveQueue = new();
    private bool _connected = false;

    /// <summary>
    /// Event triggered on notification message.
    /// </summary>
    public event Action<string, string> OnNotification;
    /// <summary>
    /// Event triggered on error message.
    /// </summary>
    public event Action<string, int> OnError;
    /// <summary>
    /// Event triggered on presence update.
    /// </summary>
    public event Action<string, bool, float?> OnPresence;
    /// <summary>
    /// Event triggered on typing indicator.
    /// </summary>
    public event Action<string, bool> OnTyping;
    /// <summary>
    /// Event triggered on raw message.
    /// </summary>
    public event Action<string> OnRawMessage;

    /// <summary>
    /// Connect to the WebSocket server.
    /// </summary>
    public async Task ConnectAsync(string server, string token, string clientId, int width, int height)
    {
        _ws = new ClientWebSocket();
        _cts = new CancellationTokenSource();
        _token = token;
        _clientId = clientId;
        _width = width;
        _height = height;
        string url = $"ws://{server}/ws?token={token}&client_id={clientId}&width={width}&height={height}";
        _serverUri = new Uri(url);
        await _ws.ConnectAsync(_serverUri, _cts.Token);
        _connected = true;
        _ = Task.Run(ReceiveLoop);
    }

    /// <summary>
    /// Disconnect from the WebSocket server.
    /// </summary>
    public async Task DisconnectAsync()
    {
        if (_ws != null && _ws.State == WebSocketState.Open)
        {
            await _ws.CloseAsync(WebSocketCloseStatus.NormalClosure, "Disconnect", _cts.Token);
        }
        _connected = false;
        _cts?.Cancel();
    }

    /// <summary>
    /// Subscribe to a channel.
    /// </summary>
    public async Task SubscribeAsync(string channel)
    {
        var msg = $"{{\"type\":\"subscribe\",\"channel\":\"{channel}\"}}";
        await SendAsync(msg);
    }

    /// <summary>
    /// Unsubscribe from a channel.
    /// </summary>
    public async Task UnsubscribeAsync(string channel)
    {
        var msg = $"{{\"type\":\"unsubscribe\",\"channel\":\"{channel}\"}}";
        await SendAsync(msg);
    }

    /// <summary>
    /// Send a typing indicator.
    /// </summary>
    public async Task SendTypingAsync(bool isTyping)
    {
        var msg = $"{{\"type\":\"typing\",\"is_typing\":{(isTyping ? "true" : "false")}}}";
        await SendAsync(msg);
    }

    /// <summary>
    /// Send a raw JSON message.
    /// </summary>
    public async Task SendAsync(string message)
    {
        if (_ws == null || _ws.State != WebSocketState.Open) return;
        var buffer = Encoding.UTF8.GetBytes(message);
        await _ws.SendAsync(new ArraySegment<byte>(buffer), WebSocketMessageType.Text, true, _cts.Token);
    }

    /// <summary>
    /// Main receive loop. Dispatches events based on message type.
    /// </summary>
    private async Task ReceiveLoop()
    {
        var buffer = new byte[4096];
        while (_connected && _ws.State == WebSocketState.Open)
        {
            var result = await _ws.ReceiveAsync(new ArraySegment<byte>(buffer), _cts.Token);
            if (result.MessageType == WebSocketMessageType.Close)
            {
                _connected = false;
                break;
            }
            var msg = Encoding.UTF8.GetString(buffer, 0, result.Count);
            _receiveQueue.Enqueue(msg);
            DispatchMessage(msg);
        }
    }

    /// <summary>
    /// Dispatch a received message to the appropriate event.
    /// </summary>
    private void DispatchMessage(string msg)
    {
        try
        {
            var json = JsonUtility.FromJson<WSMessage>(msg);
            switch (json.type)
            {
                case "notification":
                    OnNotification?.Invoke(json.message, json.level);
                    break;
                case "error":
                    OnError?.Invoke(json.message, json.code);
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
        catch (Exception)
        {
            OnRawMessage?.Invoke(msg);
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