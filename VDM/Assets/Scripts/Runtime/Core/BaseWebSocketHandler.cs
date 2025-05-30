using System;
using System.Collections.Generic;
using UnityEngine;

namespace VDM.Runtime.Core.WebSocket
{
    /// <summary>
    /// Base WebSocket handler for real-time communication
    /// Provides common functionality for all WebSocket handlers
    /// </summary>
    public abstract class BaseWebSocketHandler : MonoBehaviour
    {
        [Header("WebSocket Configuration")]
        [SerializeField] protected string serverUrl = "ws://localhost:8000";
        [SerializeField] protected bool autoConnect = true;
        [SerializeField] protected float reconnectDelay = 5.0f;
        
        protected bool isConnected = false;
        protected bool isConnecting = false;
        
        // Events
        public event Action OnConnected;
        public event Action OnDisconnected;
        public event Action<string> OnError;
        public event Action<string> OnMessageReceived;
        
        protected virtual void Start()
        {
            if (autoConnect)
            {
                Connect();
            }
        }
        
        protected virtual void OnDestroy()
        {
            Disconnect();
        }
        
        /// <summary>
        /// Connect to WebSocket server
        /// </summary>
        public virtual void Connect()
        {
            if (isConnected || isConnecting)
                return;
                
            isConnecting = true;
            Debug.Log($"Connecting to WebSocket: {serverUrl}");
            
            // Implementation would use actual WebSocket library
            // For now, simulate connection
            StartCoroutine(SimulateConnection());
        }
        
        /// <summary>
        /// Disconnect from WebSocket server
        /// </summary>
        public virtual void Disconnect()
        {
            if (!isConnected)
                return;
                
            isConnected = false;
            isConnecting = false;
            
            Debug.Log("Disconnected from WebSocket");
            OnDisconnected?.Invoke();
        }
        
        /// <summary>
        /// Send message to server
        /// </summary>
        public virtual void SendMessage(string message)
        {
            if (!isConnected)
            {
                Debug.LogWarning("Cannot send message: WebSocket not connected");
                return;
            }
            
            Debug.Log($"Sending WebSocket message: {message}");
            // Implementation would send actual message
        }
        
        /// <summary>
        /// Send JSON object to server
        /// </summary>
        public virtual void SendJson<T>(T data)
        {
            string json = JsonUtility.ToJson(data);
            SendMessage(json);
        }
        
        /// <summary>
        /// Handle incoming message
        /// </summary>
        protected virtual void HandleMessage(string message)
        {
            Debug.Log($"Received WebSocket message: {message}");
            OnMessageReceived?.Invoke(message);
        }
        
        /// <summary>
        /// Handle connection established
        /// </summary>
        protected virtual void HandleConnected()
        {
            isConnected = true;
            isConnecting = false;
            Debug.Log("WebSocket connected successfully");
            OnConnected?.Invoke();
        }
        
        /// <summary>
        /// Handle connection error
        /// </summary>
        protected virtual void HandleError(string error)
        {
            Debug.LogError($"WebSocket error: {error}");
            OnError?.Invoke(error);
            
            if (isConnecting)
            {
                isConnecting = false;
                // Attempt reconnection
                Invoke(nameof(Connect), reconnectDelay);
            }
        }
        
        private System.Collections.IEnumerator SimulateConnection()
        {
            yield return new UnityEngine.WaitForSeconds(1.0f);
            HandleConnected();
        }
    }
} 