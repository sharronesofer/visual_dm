using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.TestTools;
using NUnit.Framework;
using VisualDM.Net;
using Newtonsoft.Json;

namespace VDM.Tests.Net
{
    /// <summary>
    /// Base class for WebSocket tests that provides common setup, teardown, and utility methods.
    /// Manages test objects and provides a controlled environment for WebSocket testing.
    /// </summary>
    public class WebSocketTestRunner : TestFramework
    {
        protected GameObject _testRoot;
        protected MockWebSocketServer _mockServer;
        protected WebSocketClient _client;
        protected WebSocketManager _manager;
        
        // Test configuration
        protected string _testClientId = "test-client";
        protected string _testServerUrl = "ws://localhost:8080";
        protected string _testAuthToken = "test-auth-token";
        
        // Message tracking for tests
        protected bool _messageSent;
        protected bool _messageReceived;
        protected bool _errorOccurred;
        protected bool _connectionStatusChanged;
        protected WebSocketMessage _lastReceivedMessage;
        protected string _lastErrorMessage;
        protected WebSocketConnectionStatus _lastStatus;
        
        [SetUp]
        public override void Setup()
        {
            base.Setup();
            
            // Initialize test objects
            _testRoot = CreateGameObject("WebSocketTestRoot");
            
            // Create mock server
            _mockServer = CreateComponent<MockWebSocketServer>("MockWebSocketServer");
            _mockServer.StartServer();
            
            // Create WebSocketManager
            var managerObject = CreateGameObject("WebSocketManager");
            _manager = managerObject.AddComponent<WebSocketManager>();
            
            // Reset tracking variables
            ResetTracking();
        }
        
        [TearDown]
        public override void TearDown()
        {
            // Safely disconnect all WebSocket connections
            if (_manager != null && _manager.Clients != null)
            {
                foreach (var clientId in new List<string>(_manager.Clients.Keys))
                {
                    try
                    {
                        _manager.Disconnect(clientId);
                    }
                    catch (Exception ex)
                    {
                        Debug.LogWarning($"Error disconnecting client {clientId}: {ex.Message}");
                    }
                }
            }
            
            // Stop the mock server
            if (_mockServer != null)
            {
                _mockServer.StopServer();
            }
            
            base.TearDown();
        }
        
        /// <summary>
        /// Resets all tracking variables for clean test state.
        /// </summary>
        protected void ResetTracking()
        {
            _messageSent = false;
            _messageReceived = false;
            _errorOccurred = false;
            _connectionStatusChanged = false;
            _lastReceivedMessage = null;
            _lastErrorMessage = null;
            _lastStatus = WebSocketConnectionStatus.Disconnected;
        }
        
        /// <summary>
        /// Creates a test WebSocket message with the specified type and payload.
        /// </summary>
        /// <param name="type">Message type.</param>
        /// <param name="payload">Optional message payload.</param>
        /// <returns>A WebSocketMessage instance.</returns>
        protected WebSocketMessage CreateTestMessage(string type, Dictionary<string, object> payload = null)
        {
            return new WebSocketMessage
            {
                type = type,
                payload = payload ?? new Dictionary<string, object>()
            };
        }
        
        /// <summary>
        /// Sets up event tracking for WebSocketClient objects.
        /// </summary>
        /// <param name="client">The client to track.</param>
        protected void SetupClientEventTracking(WebSocketClient client)
        {
            client.OnMessage += (msg) => {
                _messageReceived = true;
                _lastReceivedMessage = msg;
            };
            
            client.OnError += (error) => {
                _errorOccurred = true;
                _lastErrorMessage = error;
            };
            
            client.OnStatusChanged += (status) => {
                _connectionStatusChanged = true;
                _lastStatus = status;
            };
        }
        
        /// <summary>
        /// Sets up event tracking for WebSocketManager.
        /// </summary>
        protected void SetupManagerEventTracking()
        {
            _manager.OnMessageReceived += (clientId, msg) => {
                _messageReceived = true;
                _lastReceivedMessage = msg;
            };
            
            _manager.OnError += (clientId, error) => {
                _errorOccurred = true;
                _lastErrorMessage = error;
            };
            
            _manager.OnStatusChanged += (clientId, status) => {
                _connectionStatusChanged = true;
                _lastStatus = status;
            };
        }
        
        /// <summary>
        /// Waits for a specific connection status with timeout.
        /// </summary>
        /// <param name="client">The client to check.</param>
        /// <param name="status">The expected status.</param>
        /// <param name="timeout">Maximum time to wait.</param>
        /// <returns>Coroutine IEnumerator.</returns>
        protected IEnumerator WaitForConnectionStatus(WebSocketClient client, WebSocketConnectionStatus status, float timeout = 5f)
        {
            return AssertEventually(() => client.Status == status, 
                $"Connection status should be {status}, but was {client.Status}", timeout);
        }
        
        /// <summary>
        /// Waits for a message to be received with timeout.
        /// </summary>
        /// <param name="timeout">Maximum time to wait.</param>
        /// <returns>Coroutine IEnumerator.</returns>
        protected IEnumerator WaitForMessageReceived(float timeout = 5f)
        {
            return AssertEventually(() => _messageReceived, 
                "Message should be received", timeout);
        }
        
        /// <summary>
        /// Waits for an error to occur with timeout.
        /// </summary>
        /// <param name="timeout">Maximum time to wait.</param>
        /// <returns>Coroutine IEnumerator.</returns>
        protected IEnumerator WaitForError(float timeout = 5f)
        {
            return AssertEventually(() => _errorOccurred, 
                "Error should occur", timeout);
        }
        
        /// <summary>
        /// Creates and connects a WebSocketClient for testing.
        /// </summary>
        /// <param name="url">The WebSocket server URL.</param>
        /// <param name="authToken">Optional authentication token.</param>
        /// <returns>The connected WebSocketClient.</returns>
        protected WebSocketClient CreateAndConnectClient(string url = null, string authToken = null)
        {
            var client = new WebSocketClient();
            SetupClientEventTracking(client);
            client.Connect(url ?? _testServerUrl, authToken);
            return client;
        }
        
        /// <summary>
        /// Creates a message payload from the given parameters.
        /// </summary>
        /// <param name="keyValuePairs">Key-value pairs for the payload.</param>
        /// <returns>A dictionary representing the payload.</returns>
        protected Dictionary<string, object> CreatePayload(params object[] keyValuePairs)
        {
            if (keyValuePairs.Length % 2 != 0)
            {
                throw new ArgumentException("Must provide key-value pairs (even number of arguments)");
            }
            
            var payload = new Dictionary<string, object>();
            for (int i = 0; i < keyValuePairs.Length; i += 2)
            {
                payload[keyValuePairs[i].ToString()] = keyValuePairs[i + 1];
            }
            
            return payload;
        }
        
        /// <summary>
        /// Serializes and deserializes a WebSocketMessage to simulate network transmission.
        /// </summary>
        /// <param name="message">The message to process.</param>
        /// <returns>The processed message.</returns>
        protected WebSocketMessage ProcessThroughSerialization(WebSocketMessage message)
        {
            string json = JsonConvert.SerializeObject(message);
            return JsonConvert.DeserializeObject<WebSocketMessage>(json);
        }
        
        /// <summary>
        /// Asserts that a WebSocketMessage matches the expected type and payload.
        /// </summary>
        /// <param name="message">The message to check.</param>
        /// <param name="expectedType">The expected message type.</param>
        /// <param name="expectedPayload">The expected payload entries.</param>
        protected void AssertMessageMatches(WebSocketMessage message, string expectedType, Dictionary<string, object> expectedPayload = null)
        {
            Assert.IsNotNull(message, "Message should not be null");
            Assert.AreEqual(expectedType, message.type, "Message type should match");
            
            if (expectedPayload != null)
            {
                Assert.IsNotNull(message.payload, "Message payload should not be null");
                
                foreach (var entry in expectedPayload)
                {
                    Assert.IsTrue(message.payload.ContainsKey(entry.Key), 
                        $"Message payload should contain key: {entry.Key}");
                    
                    Assert.AreEqual(entry.Value?.ToString(), message.payload[entry.Key]?.ToString(),
                        $"Payload value for key {entry.Key} should match");
                }
            }
        }
    }
} 