using System;
using System.Collections;
using System.Collections.Generic;
using System.Text;
using UnityEngine;
using Newtonsoft.Json;
using VisualDM.Net;

namespace VDM.Tests.Net
{
    /// <summary>
    /// A mock WebSocket server for testing WebSocket communication without actual network connections.
    /// Simulates server responses, connection events, and error conditions.
    /// </summary>
    public class MockWebSocketServer : MonoBehaviour
    {
        /// <summary>
        /// Event fired when a client connects to the mock server.
        /// </summary>
        public event Action<string> OnClientConnected;
        
        /// <summary>
        /// Event fired when a client disconnects from the mock server.
        /// </summary>
        public event Action<string> OnClientDisconnected;
        
        /// <summary>
        /// Event fired when the mock server receives a message from a client.
        /// </summary>
        public event Action<WebSocketMessage> OnMessageReceived;
        
        /// <summary>
        /// Event fired when an auth token is received from a client.
        /// </summary>
        public event Action<string> OnAuthTokenReceived;
        
        /// <summary>
        /// Event fired when a connection attempt is made to the mock server.
        /// </summary>
        public event Action<string> OnConnectionAttempt;
        
        /// <summary>
        /// Event fired when headers are received from a client.
        /// </summary>
        public event Action<Dictionary<string, string>> OnHeadersReceived;
        
        /// <summary>
        /// Event fired when a binary message is received from a client.
        /// </summary>
        public event Action<string, byte[]> OnBinaryMessageReceived;
        
        /// <summary>
        /// Represents whether a client is currently connected.
        /// </summary>
        public bool IsClientConnected { get; private set; }

        private bool _simulateConnectionTimeoutOnNextConnect;
        private bool _simulateConnectionFailureOnNextConnect;
        private string _connectionFailureReason;
        private string _connectedClientId;
        private WebSocketClient _connectedClient;
        private bool _shouldFailConnection = false;
        private bool _simulatedServerDown = false;
        private string _validOrigin = null;
        private bool _enforceOriginValidation = false;

        private void Awake()
        {
            IsClientConnected = false;
            _connectedClientId = null;
            _connectedClient = null;
            _shouldFailConnection = false;
            _simulatedServerDown = false;
            _validOrigin = null;
            _enforceOriginValidation = false;
        }

        /// <summary>
        /// Configures the mock server to simulate a successful connection on the next connect attempt.
        /// </summary>
        public void SetupSuccessfulConnection()
        {
            _simulateConnectionTimeoutOnNextConnect = false;
            _simulateConnectionFailureOnNextConnect = false;
            _connectionFailureReason = null;
            _shouldFailConnection = false;
            _simulatedServerDown = false;
            _enforceOriginValidation = false;
        }

        /// <summary>
        /// Configures the mock server to simulate a connection failure on the next connect attempt.
        /// </summary>
        /// <param name="reason">The reason for the connection failure.</param>
        public void SetupFailedConnection(string reason)
        {
            _simulateConnectionTimeoutOnNextConnect = false;
            _simulateConnectionFailureOnNextConnect = true;
            _connectionFailureReason = reason;
            _shouldFailConnection = true;
        }

        /// <summary>
        /// Configures the mock server to simulate a connection timeout on the next connect attempt.
        /// </summary>
        public void SetupConnectionTimeout()
        {
            _simulateConnectionTimeoutOnNextConnect = true;
            _simulateConnectionFailureOnNextConnect = false;
        }

        /// <summary>
        /// Configures the mock server to simulate being unavailable.
        /// </summary>
        public void SetupServerDown()
        {
            _simulatedServerDown = true;
        }

        /// <summary>
        /// Configures the mock server to validate origin headers.
        /// </summary>
        /// <param name="validOrigin">The trusted origin that should be accepted</param>
        public void SetupOriginValidation(string validOrigin)
        {
            _validOrigin = validOrigin;
            _enforceOriginValidation = true;
        }

        /// <summary>
        /// Simulates a client connecting to the server.
        /// </summary>
        /// <param name="client">The WebSocketClient instance connecting to the server.</param>
        /// <param name="url">The URL the client is attempting to connect to.</param>
        public void SimulateClientConnect(WebSocketClient client, string url)
        {
            // Notify of connection attempt
            OnConnectionAttempt?.Invoke(url);
            
            if (_shouldFailConnection || _simulatedServerDown)
            {
                // Simulate connection failure after a short delay
                StartCoroutine(SimulateConnectionFailureAfterDelay(client));
                return;
            }

            if (_simulateConnectionTimeoutOnNextConnect)
            {
                // Simulate connection timeout after a longer delay
                StartCoroutine(SimulateConnectionTimeoutAfterDelay(client));
                return;
            }

            // Generate a unique client ID
            _connectedClientId = Guid.NewGuid().ToString();
            _connectedClient = client;
            IsClientConnected = true;
            
            // Simulate successful connection after a short delay
            StartCoroutine(SimulateSuccessfulConnectionAfterDelay(client));
        }

        /// <summary>
        /// Simulates a client connecting to the server with custom headers.
        /// </summary>
        /// <param name="client">The client attempting to connect</param>
        /// <param name="url">The URL the client is connecting to</param>
        /// <param name="headers">Custom headers for the connection</param>
        /// <param name="origin">The origin header if specified</param>
        public void SimulateClientConnectWithHeaders(WebSocketClient client, string url, 
                                                    Dictionary<string, string> headers, 
                                                    string origin)
        {
            // Notify of connection attempt
            OnConnectionAttempt?.Invoke(url);
            
            // Process headers
            OnHeadersReceived?.Invoke(headers);
            
            // Check for origin validation
            if (_enforceOriginValidation && !string.IsNullOrEmpty(origin))
            {
                if (origin != _validOrigin)
                {
                    // Origin validation failure
                    StartCoroutine(SimulateConnectionOriginFailure(client, "Invalid origin"));
                    return;
                }
            }
            
            if (_shouldFailConnection || _simulatedServerDown)
            {
                // Simulate connection failure after a short delay
                StartCoroutine(SimulateConnectionFailureAfterDelay(client));
                return;
            }
            
            // Generate a unique client ID
            _connectedClientId = Guid.NewGuid().ToString();
            _connectedClient = client;
            IsClientConnected = true;
            
            // Simulate successful connection after a short delay
            StartCoroutine(SimulateSuccessfulConnectionAfterDelay(client));
        }

        private IEnumerator SimulateSuccessfulConnectionAfterDelay(WebSocketClient client)
        {
            yield return new WaitForSeconds(0.2f);
            
            // Notify the client of successful connection via reflection
            var connectionHandler = client.GetType().GetMethod("HandleConnected", 
                System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.NonPublic);
            
            if (connectionHandler != null)
            {
                connectionHandler.Invoke(client, null);
                OnClientConnected?.Invoke(_connectedClientId);
            }
        }

        private IEnumerator SimulateConnectionFailureAfterDelay(WebSocketClient client)
        {
            yield return new WaitForSeconds(0.2f);
            
            // Notify the client of connection failure via reflection
            var errorHandler = client.GetType().GetMethod("HandleError", 
                System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.NonPublic);
            
            if (errorHandler != null)
            {
                errorHandler.Invoke(client, new object[] { _connectionFailureReason });
            }
        }

        private IEnumerator SimulateConnectionTimeoutAfterDelay(WebSocketClient client)
        {
            yield return new WaitForSeconds(1.5f);
            
            // Notify the client of timeout via reflection
            var errorHandler = client.GetType().GetMethod("HandleError", 
                System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.NonPublic);
            
            if (errorHandler != null)
            {
                errorHandler.Invoke(client, new object[] { "Connection timeout" });
            }
        }

        /// <summary>
        /// Simulates receiving a message from the connected client.
        /// </summary>
        /// <param name="message">The message received from the client.</param>
        public void SimulateClientMessage(WebSocketMessage message)
        {
            if (!IsClientConnected)
            {
                Debug.LogWarning("MockWebSocketServer: Cannot receive message, no client connected");
                return;
            }

            OnMessageReceived?.Invoke(message);

            // Auto-respond to heartbeat messages
            if (message.type == "heartbeat")
            {
                var response = new WebSocketMessage
                {
                    version = "1.0",
                    type = "heartbeat_response",
                    timestamp = DateTime.UtcNow.ToString("o"),
                    requestId = message.requestId,
                    payload = new Dictionary<string, object> { { "message", "pong" } }
                };

                SendMessageToClient(response);
            }
        }

        /// <summary>
        /// Sends a message to the connected client.
        /// </summary>
        /// <param name="message">The message to send to the client.</param>
        public void SendMessageToClient(WebSocketMessage message)
        {
            if (!IsClientConnected || _connectedClient == null)
            {
                Debug.LogWarning("MockWebSocketServer: Cannot send message, no client connected");
                return;
            }

            // Convert to JSON
            string json = JsonConvert.SerializeObject(message);
            
            // Simulate receive on client via reflection
            var messageHandler = _connectedClient.GetType().GetMethod("HandleMessageReceived", 
                System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.NonPublic);
            
            if (messageHandler != null)
            {
                messageHandler.Invoke(_connectedClient, new object[] { json });
            }
        }

        /// <summary>
        /// Sends a binary message to the connected client.
        /// </summary>
        /// <param name="messageType">The type of the message.</param>
        /// <param name="data">The binary data to send.</param>
        public void SendBinaryMessageToClient(string messageType, byte[] data)
        {
            if (!IsClientConnected || _connectedClient == null)
            {
                Debug.LogWarning("MockWebSocketServer: Cannot send binary message, no client connected");
                return;
            }
            
            // Simulate receive on client via reflection
            var binaryMessageHandler = _connectedClient.GetType().GetMethod("HandleBinaryMessageReceived", 
                System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.NonPublic);
            
            if (binaryMessageHandler != null)
            {
                binaryMessageHandler.Invoke(_connectedClient, new object[] { messageType, data });
            }
        }

        /// <summary>
        /// Simulates receiving a binary message from the connected client.
        /// </summary>
        /// <param name="messageType">The type of the message.</param>
        /// <param name="data">The binary data received.</param>
        public void SimulateClientBinaryMessage(string messageType, byte[] data)
        {
            if (!IsClientConnected)
            {
                Debug.LogWarning("MockWebSocketServer: Cannot receive binary message, no client connected");
                return;
            }

            OnBinaryMessageReceived?.Invoke(messageType, data);
        }

        /// <summary>
        /// Simulates the server initiating a client disconnection.
        /// </summary>
        public void DisconnectClient()
        {
            if (!IsClientConnected || _connectedClient == null)
            {
                Debug.LogWarning("MockWebSocketServer: Cannot disconnect, no client connected");
                return;
            }

            // Notify the client of disconnection via reflection
            var disconnectHandler = _connectedClient.GetType().GetMethod("HandleDisconnected", 
                System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.NonPublic);
            
            if (disconnectHandler != null)
            {
                disconnectHandler.Invoke(_connectedClient, null);
                OnClientDisconnected?.Invoke(_connectedClientId);
                
                IsClientConnected = false;
                _connectedClientId = null;
                _connectedClient = null;
            }
        }

        /// <summary>
        /// Simulates a network failure causing client disconnection.
        /// </summary>
        public void SimulateNetworkFailure()
        {
            if (!IsClientConnected || _connectedClient == null)
            {
                Debug.LogWarning("MockWebSocketServer: Cannot simulate network failure, no client connected");
                return;
            }

            // Notify the client of disconnection via reflection
            var disconnectHandler = _connectedClient.GetType().GetMethod("HandleDisconnected", 
                System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.NonPublic);
            
            if (disconnectHandler != null)
            {
                disconnectHandler.Invoke(_connectedClient, null);
                OnClientDisconnected?.Invoke(_connectedClientId);
                
                IsClientConnected = false;
                _connectedClientId = null;
                _connectedClient = null;
            }
        }

        /// <summary>
        /// Simulates the client disconnecting from the server.
        /// </summary>
        public void SimulateClientDisconnect()
        {
            if (!IsClientConnected)
            {
                Debug.LogWarning("MockWebSocketServer: Cannot disconnect, no client connected");
                return;
            }

            OnClientDisconnected?.Invoke(_connectedClientId);
            IsClientConnected = false;
            _connectedClientId = null;
            _connectedClient = null;
        }

        /// <summary>
        /// Processes a message received from the client.
        /// </summary>
        /// <param name="message">The message received from the client.</param>
        public void ProcessMessageFromClient(WebSocketMessage message)
        {
            if (!IsClientConnected)
            {
                Debug.LogWarning("MockWebSocketServer: Received message while disconnected");
                return;
            }
            
            // Detect auth messages
            if (message.type == "auth_request" && message.payload.ContainsKey("token"))
            {
                string token = message.payload["token"].ToString();
                OnAuthTokenReceived?.Invoke(token);
            }
            
            // Raise message received event
            OnMessageReceived?.Invoke(message);
        }

        /// <summary>
        /// Sends an invalid message to the client for testing validation.
        /// </summary>
        /// <param name="message">The message to send to the client.</param>
        public void SendInvalidMessageToClient(WebSocketMessage message)
        {
            if (!IsClientConnected || _connectedClient == null)
            {
                Debug.LogWarning("MockWebSocketServer: Cannot send message while disconnected");
                return;
            }
            
            // Convert to a string that will be recognized as a message but fail validation
            string invalidJson = "{\"version\":null,\"type\":\"" + message.type + "\",\"payload\":{}}";
            
            // Simulate receive on client via reflection
            var messageHandler = _connectedClient.GetType().GetMethod("HandleMessageReceived", 
                System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.NonPublic);
            
            if (messageHandler != null)
            {
                messageHandler.Invoke(_connectedClient, new object[] { invalidJson });
            }
        }

        /// <summary>
        /// Simulates a latency delay before message processing.
        /// </summary>
        /// <param name="seconds">The duration of the latency delay.</param>
        /// <returns>An enumerator for the coroutine.</returns>
        public IEnumerator SimulateLatency(float seconds)
        {
            yield return new WaitForSeconds(seconds);
        }

        /// <summary>
        /// Simulates intermittent connection issues.
        /// </summary>
        /// <param name="disconnectCount">The number of disconnections and reconnections.</param>
        /// <param name="interval">The interval between disconnections and reconnections.</param>
        /// <returns>An enumerator for the coroutine.</returns>
        public IEnumerator SimulateConnectionIssues(int disconnectCount, float interval)
        {
            for (int i = 0; i < disconnectCount; i++)
            {
                DisconnectClient();
                yield return new WaitForSeconds(interval / 2);
                
                if (_connectedClient != null)
                {
                    SimulateClientConnect(_connectedClient, _connectedClient.Url);
                }
                
                yield return new WaitForSeconds(interval / 2);
            }
        }

        /// <summary>
        /// Simulates a connection failure with delay.
        /// </summary>
        private IEnumerator SimulateConnectionFailure(WebSocketClient client)
        {
            yield return new WaitForSeconds(0.1f);
            client.OnError("Connection failed: Server error");
        }
        
        /// <summary>
        /// Simulates an origin validation failure with delay.
        /// </summary>
        private IEnumerator SimulateConnectionOriginFailure(WebSocketClient client, string reason)
        {
            yield return new WaitForSeconds(0.1f);
            client.OnError($"Connection failed: {reason}");
        }

        void OnDestroy()
        {
            // Clean up any connections
            if (IsClientConnected && _connectedClient != null)
            {
                DisconnectClient();
            }
        }
    }
} 