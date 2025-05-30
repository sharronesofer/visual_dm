using System;
using UnityEngine;

namespace VDM.Runtime.Core.Services.WebSocket
{
    /// <summary>
    /// Base class for WebSocket handler implementations
    /// </summary>
    public abstract class BaseWebSocketHandler : MonoBehaviour
    {
        [Header("WebSocket Configuration")]
        [SerializeField] protected string serverUrl = "ws://localhost:8000/ws";
        [SerializeField] protected bool autoConnect = true;
        [SerializeField] protected float reconnectDelay = 5f;
        
        protected bool isConnected = false;
        protected bool isConnecting = false;
        
        public event Action OnConnected;
        public event Action OnDisconnected;
        public event Action<string> OnMessageReceived;
        public event Action<string> OnError;
        
        protected virtual void Start()
        {
            if (autoConnect)
            {
                Connect();
            }
        }
        
        public virtual void Connect()
        {
            if (isConnected || isConnecting)
            {
                Debug.LogWarning("WebSocket already connected or connecting");
                return;
            }
            
            isConnecting = true;
            Debug.Log($"Connecting to WebSocket: {serverUrl}");
            
            // Simulate connection for now
            Invoke(nameof(SimulateConnection), 1f);
        }
        
        public virtual void Disconnect()
        {
            if (!isConnected)
            {
                Debug.LogWarning("WebSocket not connected");
                return;
            }
            
            isConnected = false;
            isConnecting = false;
            OnDisconnected?.Invoke();
            Debug.Log("WebSocket disconnected");
        }
        
        public virtual void SendMessage(string message)
        {
            if (!isConnected)
            {
                Debug.LogError("Cannot send message: WebSocket not connected");
                return;
            }
            
            Debug.Log($"Sending WebSocket message: {message}");
            // Actual WebSocket implementation would go here
        }
        
        protected virtual void SimulateConnection()
        {
            isConnecting = false;
            isConnected = true;
            OnConnected?.Invoke();
            Debug.Log("WebSocket connected (simulated)");
        }
        
        protected virtual void HandleMessage(string message)
        {
            OnMessageReceived?.Invoke(message);
        }
        
        protected virtual void HandleError(string error)
        {
            Debug.LogError($"WebSocket error: {error}");
            OnError?.Invoke(error);
        }
    }
} 