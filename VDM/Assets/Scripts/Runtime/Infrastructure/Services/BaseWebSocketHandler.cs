using NativeWebSocket;
using System;
using System.Threading.Tasks;
using UnityEngine;

namespace VDM.Infrastructure.Services.Websocket
{
    /// <summary>
    /// Base class for WebSocket handlers in Unity frontend
    /// </summary>
    public abstract class BaseWebSocketHandler : MonoBehaviour
    {
        protected string ConnectionUrl { get; set; } = string.Empty;
        protected bool IsConnected { get; set; } = false;
        
        protected string SystemName { get; private set; }

        protected BaseWebSocketHandler() : this("UnknownSystem")
        {
        }

        protected BaseWebSocketHandler(string systemName = "")
        {
            SystemName = systemName;
        }

        /// <summary>
        /// Connect to WebSocket server
        /// </summary>
        protected virtual void Connect(string url)
        {
            ConnectionUrl = url;
            Debug.Log($"[{SystemName}] Connecting to WebSocket: {url}");
            
            // Simulate connection for compilation
            IsConnected = true;
        }

        /// <summary>
        /// Disconnect from WebSocket server
        /// </summary>
        protected virtual void Disconnect()
        {
            Debug.Log($"[{SystemName}] Disconnecting from WebSocket");
            IsConnected = false;
            ConnectionUrl = string.Empty;
        }

        /// <summary>
        /// Send message to WebSocket server
        /// </summary>
        protected virtual async Task SendMessage(object message)
        {
            if (!IsConnected)
            {
                Debug.LogWarning($"[{SystemName}] Cannot send message: not connected");
                return;
            }

            var json = UnityEngine.JsonUtility.ToJson(message);
            Debug.Log($"[{SystemName}] Sending message: {json}");
            
            // Simulate async send
            await Task.Delay(10);
        }

        /// <summary>
        /// Handle incoming WebSocket message - must be implemented by derived classes
        /// </summary>
        protected abstract void HandleMessage(string message);

        /// <summary>
        /// Subscribe to a channel or topic
        /// </summary>
        protected virtual void Subscribe(string channel)
        {
            Debug.Log($"[{SystemName}] Subscribing to channel: {channel}");
        }

        /// <summary>
        /// Unsubscribe from a channel or topic
        /// </summary>
        protected virtual void Unsubscribe(string channel)
        {
            Debug.Log($"[{SystemName}] Unsubscribing from channel: {channel}");
        }

        protected virtual void OnDestroy()
        {
            if (IsConnected)
            {
                Disconnect();
            }
        }
    }
} 