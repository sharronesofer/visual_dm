using System;
using System.Collections.Generic;
using UnityEngine;

namespace VisualDM.Net
{
    /// <summary>
    /// Manages multiple WebSocket connections by key.
    /// </summary>
    public class WebSocketManager : MonoBehaviour
    {
        private static WebSocketManager _instance;
        public static WebSocketManager Instance
        {
            get
            {
                if (_instance == null)
                {
                    var go = new GameObject("WebSocketManager");
                    _instance = go.AddComponent<WebSocketManager>();
                    DontDestroyOnLoad(go);
                }
                return _instance;
            }
        }

        private Dictionary<string, WebSocketClient> connections = new Dictionary<string, WebSocketClient>();
        
        /// <summary>
        /// Event fired when a connection's status changes.
        /// </summary>
        public event Action<string, WebSocketConnectionStatus> OnStatusChanged;

        /// <summary>
        /// Unity Awake lifecycle method. Ensures singleton pattern.
        /// </summary>
        private void Awake()
        {
            if (_instance != null && _instance != this)
            {
                Destroy(gameObject);
                return;
            }
            _instance = this;
            DontDestroyOnLoad(gameObject);
        }

        /// <summary>
        /// Connect to a WebSocket server with a specified key.
        /// </summary>
        /// <param name="key">Unique identifier for this connection.</param>
        /// <param name="uri">URI of the WebSocket server.</param>
        /// <param name="authToken">Optional authentication token.</param>
        /// <returns>The WebSocketClient instance.</returns>
        public WebSocketClient Connect(string key, string uri, string authToken = null)
        {
            WebSocketClient client;
            if (connections.TryGetValue(key, out client))
            {
                client.Disconnect();
            }
            else
            {
                var go = new GameObject($"WebSocketClient_{key}");
                go.transform.SetParent(transform);
                client = go.AddComponent<WebSocketClient>();
                client.OnStatusChanged += status => OnStatusChanged?.Invoke(key, status);
                connections[key] = client;
            }
            
            client.Connect(uri, authToken);
            return client;
        }

        /// <summary>
        /// Get a WebSocketClient by its key.
        /// </summary>
        /// <param name="key">The connection key.</param>
        /// <returns>The WebSocketClient instance, or null if not found.</returns>
        public WebSocketClient GetClient(string key)
        {
            if (connections.TryGetValue(key, out var client))
                return client;
            return null;
        }

        /// <summary>
        /// Disconnect a WebSocketClient by its key.
        /// </summary>
        /// <param name="key">The connection key.</param>
        public void Disconnect(string key)
        {
            if (connections.TryGetValue(key, out var client))
            {
                client.Disconnect();
                connections.Remove(key);
                Destroy(client.gameObject);
            }
        }

        /// <summary>
        /// Disconnect all WebSocketClients.
        /// </summary>
        public void DisconnectAll()
        {
            foreach (var kvp in connections)
            {
                kvp.Value.Disconnect();
                Destroy(kvp.Value.gameObject);
            }
            connections.Clear();
        }

        /// <summary>
        /// Unity OnDestroy lifecycle method. Disconnects all clients.
        /// </summary>
        private void OnDestroy()
        {
            DisconnectAll();
        }
    }
} 