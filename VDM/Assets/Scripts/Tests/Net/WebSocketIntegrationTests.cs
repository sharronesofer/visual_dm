using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.TestTools;
using NUnit.Framework;
using VisualDM.Net;

namespace VDM.Tests.Net
{
    [TestFixture]
    public class WebSocketIntegrationTests : TestFramework
    {
        private GameObject _testGameObject;
        private MockWebSocketServer _mockServer;
        private WebSocketProvider _provider;
        
        [SetUp]
        public override void Setup()
        {
            base.Setup();
            
            // Create game objects for test
            _testGameObject = CreateTestObject("WebSocketIntegrationTest");
            _mockServer = _testGameObject.AddComponent<MockWebSocketServer>();
            _provider = _testGameObject.AddComponent<WebSocketProvider>();
            
            // Initialize provider
            _provider.Initialize();
        }
        
        [TearDown]
        public override void Teardown()
        {
            // Disconnect all connections before cleanup
            _provider.DisconnectAll();
            
            base.Teardown();
        }
        
        [UnityTest]
        public IEnumerator FullRequestResponse_Cycle_ShouldWork()
        {
            // Arrange
            _mockServer.SetupSuccessfulConnection();
            _provider.Connect("default", "ws://mock-server");
            
            yield return new WaitForSeconds(0.5f);
            
            // Setup mock server to respond to requests with matching IDs
            _mockServer.OnMessageReceived += (msg) => {
                if (msg.type == "get_data_request")
                {
                    // Create response message with same request ID
                    var response = new WebSocketMessage
                    {
                        version = "1.0",
                        type = "get_data_response",
                        timestamp = DateTime.UtcNow.ToString("o"),
                        requestId = msg.requestId,
                        payload = new Dictionary<string, object>
                        {
                            { "data", new Dictionary<string, object> 
                                {
                                    { "id", 123 },
                                    { "name", "Test Item" },
                                    { "value", 456 }
                                }
                            },
                            { "success", true }
                        }
                    };
                    
                    // Send response back to client
                    _mockServer.SendMessageToClient(response);
                }
            };
            
            // Variables for tracking response
            Dictionary<string, object> responseData = null;
            
            // Act - use the provider to make a request
            _provider.Request(
                "default", 
                "get_data_request",
                new Dictionary<string, object> { { "itemId", 123 } },
                (success, data) => {
                    if (success)
                    {
                        responseData = (Dictionary<string, object>)data["data"];
                    }
                }
            );
            
            // Wait for request-response cycle
            yield return new WaitForSeconds(0.7f);
            
            // Assert
            Assert.IsNotNull(responseData, "Response data should be received");
            Assert.AreEqual(123, responseData["id"], "Data ID should match");
            Assert.AreEqual("Test Item", responseData["name"], "Data name should match");
            Assert.AreEqual(456, responseData["value"], "Data value should match");
        }
        
        [UnityTest]
        public IEnumerator RequestWithTimeout_ShouldInvokeTimeoutCallback()
        {
            // Arrange
            _mockServer.SetupSuccessfulConnection();
            _provider.Connect("default", "ws://mock-server");
            
            yield return new WaitForSeconds(0.5f);
            
            // No response handler, so server will not respond
            
            // Variables for tracking timeout
            bool timeoutInvoked = false;
            
            // Act - use the provider to make a request with a short timeout
            _provider.RequestWithTimeout(
                "default", 
                "get_data_with_timeout",
                new Dictionary<string, object> { { "itemId", 123 } },
                0.3f, // short timeout for testing
                (success, data) => {
                    // This should not be called
                },
                (requestId) => {
                    timeoutInvoked = true;
                }
            );
            
            // Wait for timeout to occur
            yield return new WaitForSeconds(0.5f);
            
            // Assert
            Assert.IsTrue(timeoutInvoked, "Timeout callback should be invoked");
        }
        
        [UnityTest]
        public IEnumerator Broadcast_ShouldDeliverMessageToAllSubscribers()
        {
            // Arrange
            _mockServer.SetupSuccessfulConnection();
            _provider.Connect("default", "ws://mock-server");
            
            yield return new WaitForSeconds(0.5f);
            
            // Set up multiple subscribers
            int subscriber1CallCount = 0;
            int subscriber2CallCount = 0;
            WebSocketMessage receivedMessage1 = null;
            WebSocketMessage receivedMessage2 = null;
            
            _provider.Subscribe("default", "broadcast_event", (msg) => {
                subscriber1CallCount++;
                receivedMessage1 = msg;
            });
            
            _provider.Subscribe("default", "broadcast_event", (msg) => {
                subscriber2CallCount++;
                receivedMessage2 = msg;
            });
            
            // Act - simulate server broadcasting a message
            var broadcastMessage = new WebSocketMessage
            {
                version = "1.0",
                type = "broadcast_event",
                timestamp = DateTime.UtcNow.ToString("o"),
                payload = new Dictionary<string, object> { { "announcement", "System update scheduled" } }
            };
            
            _mockServer.SendMessageToClient(broadcastMessage);
            
            // Wait for message to be processed
            yield return new WaitForSeconds(0.5f);
            
            // Assert
            Assert.AreEqual(1, subscriber1CallCount, "First subscriber should receive the message");
            Assert.AreEqual(1, subscriber2CallCount, "Second subscriber should receive the message");
            Assert.IsNotNull(receivedMessage1, "First subscriber should have valid message");
            Assert.IsNotNull(receivedMessage2, "Second subscriber should have valid message");
            Assert.AreEqual("broadcast_event", receivedMessage1.type, "Message type should match");
            Assert.AreEqual("System update scheduled", receivedMessage1.payload["announcement"], "Message payload should match");
        }
        
        [UnityTest]
        public IEnumerator ServiceDiscovery_ShouldConnectToCorrectEndpoint()
        {
            // Arrange
            _mockServer.SetupSuccessfulConnection();
            
            string capturedDiscoveryUrl = null;
            string capturedServiceUrl = null;
            
            _mockServer.OnConnectionAttempt += (url) => {
                if (capturedDiscoveryUrl == null)
                    capturedDiscoveryUrl = url;
                else if (capturedServiceUrl == null)
                    capturedServiceUrl = url;
            };
            
            // Setup mock server to respond with service endpoint
            _mockServer.OnMessageReceived += (msg) => {
                if (msg.type == "discover_services")
                {
                    // Create response with service endpoints
                    var response = new WebSocketMessage
                    {
                        version = "1.0",
                        type = "service_endpoints",
                        timestamp = DateTime.UtcNow.ToString("o"),
                        requestId = msg.requestId,
                        payload = new Dictionary<string, object>
                        {
                            { "gameService", "ws://game-service" },
                            { "chatService", "ws://chat-service" }
                        }
                    };
                    
                    // Send response back to client
                    _mockServer.SendMessageToClient(response);
                }
            };
            
            bool gameServiceConnected = false;
            
            // Act - connect to discovery endpoint, then use it to find game service
            _provider.Connect("discovery", "ws://discovery-service");
            
            yield return new WaitForSeconds(0.5f);
            
            // Request service discovery
            _provider.Request(
                "discovery",
                "discover_services",
                new Dictionary<string, object>(),
                (success, data) => {
                    if (success)
                    {
                        string gameServiceUrl = data["gameService"].ToString();
                        _provider.Connect("game", gameServiceUrl, null, () => {
                            gameServiceConnected = true;
                        });
                    }
                }
            );
            
            // Wait for discovery and connection
            yield return new WaitForSeconds(1.0f);
            
            // Assert
            Assert.AreEqual("ws://discovery-service", capturedDiscoveryUrl, "Should connect to discovery service first");
            Assert.AreEqual("ws://game-service", capturedServiceUrl, "Should connect to game service after discovery");
            Assert.IsTrue(gameServiceConnected, "Game service connection callback should be invoked");
        }
        
        [UnityTest]
        public IEnumerator SessionReconnect_ShouldRestoreSession()
        {
            // Arrange
            _mockServer.SetupSuccessfulConnection();
            string sessionToken = null;
            
            // Mock server generates session token on first connection
            _mockServer.OnClientConnected += () => {
                if (sessionToken == null)
                {
                    sessionToken = "session-" + Guid.NewGuid().ToString();
                    
                    var sessionMessage = new WebSocketMessage
                    {
                        version = "1.0",
                        type = "session_established",
                        timestamp = DateTime.UtcNow.ToString("o"),
                        payload = new Dictionary<string, object> { { "sessionToken", sessionToken } }
                    };
                    
                    _mockServer.SendMessageToClient(sessionMessage);
                }
            };
            
            string capturedReconnectToken = null;
            
            // Mock server verifies session token on reconnect
            _mockServer.OnMessageReceived += (msg) => {
                if (msg.type == "session_reconnect" && msg.payload.ContainsKey("sessionToken"))
                {
                    capturedReconnectToken = msg.payload["sessionToken"].ToString();
                    
                    var reconnectResponse = new WebSocketMessage
                    {
                        version = "1.0",
                        type = "session_restored",
                        timestamp = DateTime.UtcNow.ToString("o"),
                        requestId = msg.requestId,
                        payload = new Dictionary<string, object> { { "success", true } }
                    };
                    
                    _mockServer.SendMessageToClient(reconnectResponse);
                }
            };
            
            string receivedSessionToken = null;
            bool sessionRestored = false;
            
            // Subscribe to session messages
            _provider.Connect("default", "ws://mock-server");
            
            _provider.Subscribe("default", "session_established", (msg) => {
                receivedSessionToken = msg.payload["sessionToken"].ToString();
            });
            
            _provider.Subscribe("default", "session_restored", (msg) => {
                sessionRestored = true;
            });
            
            // Wait for initial session
            yield return new WaitForSeconds(0.5f);
            
            // Verify we have a session token
            Assert.IsNotNull(receivedSessionToken, "Should receive session token");
            
            // Act - disconnect and reconnect with session token
            _provider.Disconnect("default");
            
            yield return new WaitForSeconds(0.5f);
            
            // Reconnect with session
            _provider.ConnectWithSession("default", "ws://mock-server", receivedSessionToken);
            
            // Wait for reconnection
            yield return new WaitForSeconds(0.5f);
            
            // Assert
            Assert.AreEqual(receivedSessionToken, capturedReconnectToken, "Reconnect should use the same session token");
            Assert.IsTrue(sessionRestored, "Session should be restored");
        }
        
        [UnityTest]
        public IEnumerator LoadBalancing_ShouldSelectAppropriateServer()
        {
            // Arrange
            _mockServer.SetupSuccessfulConnection();
            
            List<string> serverEndpoints = new List<string>
            {
                "ws://server1",
                "ws://server2",
                "ws://server3"
            };
            
            // Track which server was selected
            string selectedServerUrl = null;
            _mockServer.OnConnectionAttempt += (url) => {
                selectedServerUrl = url;
            };
            
            // Mock endpoint status response
            var endpointStatus = new Dictionary<string, object>
            {
                { "ws://server1", new Dictionary<string, object> { { "load", 0.9 }, { "online", true } } },
                { "ws://server2", new Dictionary<string, object> { { "load", 0.2 }, { "online", true } } },
                { "ws://server3", new Dictionary<string, object> { { "load", 0.6 }, { "online", true } } }
            };
            
            // Act - use the load balancer to select best server
            _provider.ConnectToOptimalServer("game", serverEndpoints, endpointStatus);
            
            // Wait for connection
            yield return new WaitForSeconds(0.5f);
            
            // Assert - should select server2 with lowest load
            Assert.AreEqual("ws://server2", selectedServerUrl, "Should select the server with lowest load");
        }
        
        [UnityTest]
        public IEnumerator MultiServiceIntegration_ShouldWorkTogether()
        {
            // Arrange
            _mockServer.SetupSuccessfulConnection();
            
            // Connect to multiple services
            _provider.Connect("game", "ws://game-service");
            _provider.Connect("chat", "ws://chat-service");
            
            yield return new WaitForSeconds(0.5f);
            
            // Variables for tracking received messages
            WebSocketMessage gameMessage = null;
            WebSocketMessage chatMessage = null;
            
            // Subscribe to both services
            _provider.Subscribe("game", "game_update", (msg) => gameMessage = msg);
            _provider.Subscribe("chat", "chat_message", (msg) => chatMessage = msg);
            
            // Act - simulate messages from both services
            var mockGameMessage = new WebSocketMessage
            {
                version = "1.0",
                type = "game_update",
                timestamp = DateTime.UtcNow.ToString("o"),
                payload = new Dictionary<string, object> { { "event", "player_joined" } }
            };
            
            var mockChatMessage = new WebSocketMessage
            {
                version = "1.0",
                type = "chat_message",
                timestamp = DateTime.UtcNow.ToString("o"),
                payload = new Dictionary<string, object> { { "sender", "Player1" }, { "text", "Hello!" } }
            };
            
            // Send messages as if they came from the respective services
            _mockServer.SendMessageToClient(mockGameMessage);
            yield return new WaitForSeconds(0.1f);
            _mockServer.SendMessageToClient(mockChatMessage);
            
            // Wait for messages to be processed
            yield return new WaitForSeconds(0.5f);
            
            // Assert
            Assert.IsNotNull(gameMessage, "Game message should be received");
            Assert.IsNotNull(chatMessage, "Chat message should be received");
            Assert.AreEqual("game_update", gameMessage.type, "Game message type should match");
            Assert.AreEqual("chat_message", chatMessage.type, "Chat message type should match");
            Assert.AreEqual("player_joined", gameMessage.payload["event"], "Game event should match");
            Assert.AreEqual("Player1", chatMessage.payload["sender"], "Chat sender should match");
            Assert.AreEqual("Hello!", chatMessage.payload["text"], "Chat text should match");
        }
    }
} 