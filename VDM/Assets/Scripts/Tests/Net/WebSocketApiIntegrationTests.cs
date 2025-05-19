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
    public class WebSocketApiIntegrationTests : TestFramework
    {
        private GameObject _testGameObject;
        private MockWebSocketServer _mockServer;
        private WebSocketClient _client;
        
        [SetUp]
        public void SetUp()
        {
            // Create game objects for test
            _testGameObject = new GameObject("WebSocketApiTest");
            _mockServer = _testGameObject.AddComponent<MockWebSocketServer>();
            _client = _testGameObject.AddComponent<WebSocketClient>();
        }

        [TearDown]
        public void TearDown()
        {
            // Clean up test objects
            if (_testGameObject != null)
            {
                GameObject.Destroy(_testGameObject);
            }
        }

        [UnityTest]
        public IEnumerator AuthenticationFlow_CompletesSuccessfully()
        {
            // Arrange
            bool authSuccessReceived = false;
            string userId = null;
            
            _mockServer.SetupSuccessfulConnection();
            _client.Connect("ws://mock-server");
            
            // Wait for connection
            yield return new WaitForSeconds(0.5f);
            Assert.IsTrue(_client.IsConnected, "Client should be connected");
            
            // Register for auth response
            _client.OnMessageReceived += (msg) => {
                if (msg.type == "auth_response")
                {
                    // Extract response from payload
                    var payload = msg.payload;
                    var success = Convert.ToBoolean(payload["success"]);
                    
                    if (success)
                    {
                        authSuccessReceived = true;
                        userId = payload["userId"].ToString();
                    }
                }
            };
            
            // Setup server to receive auth request
            WebSocketMessage receivedAuthRequest = null;
            _mockServer.OnMessageReceived += (msg) => {
                if (msg.type == "auth_request")
                {
                    receivedAuthRequest = msg;
                    
                    // Simulate successful auth response
                    var response = new WebSocketMessage
                    {
                        version = "1.0",
                        type = "auth_response",
                        timestamp = DateTime.UtcNow.ToString("o"),
                        requestId = msg.requestId,
                        payload = new Dictionary<string, object>
                        {
                            { "success", true },
                            { "userId", "test-user-id" },
                            { "error", null }
                        }
                    };
                    
                    _mockServer.SendMessageToClient(response);
                }
            };
            
            // Act - send auth request
            _client.SendAuthRequest("test-jwt-token");
            
            // Wait for response
            yield return new WaitForSeconds(0.5f);
            
            // Assert
            Assert.IsNotNull(receivedAuthRequest, "Auth request should be sent to server");
            Assert.IsTrue(authSuccessReceived, "Auth success response should be received");
            Assert.AreEqual("test-user-id", userId, "User ID from response should match");
        }

        [UnityTest]
        public IEnumerator AuthenticationFlow_HandlesFailure()
        {
            // Arrange
            bool authFailureReceived = false;
            string errorMessage = null;
            
            _mockServer.SetupSuccessfulConnection();
            _client.Connect("ws://mock-server");
            
            // Wait for connection
            yield return new WaitForSeconds(0.5f);
            Assert.IsTrue(_client.IsConnected, "Client should be connected");
            
            // Register for auth response
            _client.OnMessageReceived += (msg) => {
                if (msg.type == "auth_response")
                {
                    // Extract response from payload
                    var payload = msg.payload;
                    var success = Convert.ToBoolean(payload["success"]);
                    
                    if (!success)
                    {
                        authFailureReceived = true;
                        errorMessage = payload["error"].ToString();
                    }
                }
            };
            
            // Setup server to receive auth request
            _mockServer.OnMessageReceived += (msg) => {
                if (msg.type == "auth_request")
                {
                    // Simulate failed auth response
                    var response = new WebSocketMessage
                    {
                        version = "1.0",
                        type = "auth_response",
                        timestamp = DateTime.UtcNow.ToString("o"),
                        requestId = msg.requestId,
                        payload = new Dictionary<string, object>
                        {
                            { "success", false },
                            { "userId", null },
                            { "error", "Invalid token" }
                        }
                    };
                    
                    _mockServer.SendMessageToClient(response);
                }
            };
            
            // Act - send auth request with invalid token
            _client.SendAuthRequest("invalid-token");
            
            // Wait for response
            yield return new WaitForSeconds(0.5f);
            
            // Assert
            Assert.IsTrue(authFailureReceived, "Auth failure response should be received");
            Assert.AreEqual("Invalid token", errorMessage, "Error message should match");
        }

        [UnityTest]
        public IEnumerator MetricsUpdate_ProcessedCorrectly()
        {
            // Arrange
            bool metricsUpdateReceived = false;
            string metricName = null;
            object metricValue = null;
            
            _mockServer.SetupSuccessfulConnection();
            _client.Connect("ws://mock-server");
            
            // Wait for connection
            yield return new WaitForSeconds(0.5f);
            Assert.IsTrue(_client.IsConnected, "Client should be connected");
            
            // Register for metrics update
            _client.OnMessageReceived += (msg) => {
                if (msg.type == "metrics_update")
                {
                    // Extract metrics data from payload
                    var payload = msg.payload;
                    metricsUpdateReceived = true;
                    metricName = payload["metricName"].ToString();
                    metricValue = payload["value"];
                }
            };
            
            // Act - server sends metrics update
            var metricsMessage = new WebSocketMessage
            {
                version = "1.0",
                type = "metrics_update",
                timestamp = DateTime.UtcNow.ToString("o"),
                requestId = "server-123",
                payload = new Dictionary<string, object>
                {
                    { "metricName", "active_players" },
                    { "value", 42 }
                }
            };
            
            _mockServer.SendMessageToClient(metricsMessage);
            
            // Wait for processing
            yield return new WaitForSeconds(0.5f);
            
            // Assert
            Assert.IsTrue(metricsUpdateReceived, "Metrics update should be received");
            Assert.AreEqual("active_players", metricName, "Metric name should match");
            Assert.AreEqual(42L, metricValue, "Metric value should match");
        }

        [UnityTest]
        public IEnumerator AIMessageResponse_ProcessedCorrectly()
        {
            // Arrange
            bool aiMessageReceived = false;
            string rumorText = null;
            
            _mockServer.SetupSuccessfulConnection();
            _client.Connect("ws://mock-server");
            
            // Wait for connection
            yield return new WaitForSeconds(0.5f);
            Assert.IsTrue(_client.IsConnected, "Client should be connected");
            
            // Register for AI message
            _client.OnMessageReceived += (msg) => {
                if (msg.type == "ai_message")
                {
                    // Extract data from payload
                    var payload = msg.payload;
                    aiMessageReceived = true;
                    rumorText = payload["Rumor"].ToString();
                }
            };
            
            // Act - server sends AI message
            var aiMessage = new WebSocketMessage
            {
                version = "1.0",
                type = "ai_message",
                timestamp = DateTime.UtcNow.ToString("o"),
                requestId = "server-456",
                payload = new Dictionary<string, object>
                {
                    { "Rumor", "The king is planning to raise taxes next month." }
                }
            };
            
            _mockServer.SendMessageToClient(aiMessage);
            
            // Wait for processing
            yield return new WaitForSeconds(0.5f);
            
            // Assert
            Assert.IsTrue(aiMessageReceived, "AI message should be received");
            Assert.AreEqual("The king is planning to raise taxes next month.", rumorText, "Rumor text should match");
        }

        [UnityTest]
        public IEnumerator ErrorResponse_HandledCorrectly()
        {
            // Arrange
            bool errorReceived = false;
            int errorCode = 0;
            string errorMessage = null;
            
            _mockServer.SetupSuccessfulConnection();
            _client.Connect("ws://mock-server");
            
            // Wait for connection
            yield return new WaitForSeconds(0.5f);
            Assert.IsTrue(_client.IsConnected, "Client should be connected");
            
            // Register for error message
            _client.OnMessageReceived += (msg) => {
                if (msg.type == "error")
                {
                    // Extract error data from payload
                    var payload = msg.payload;
                    errorReceived = true;
                    errorCode = Convert.ToInt32(payload["code"]);
                    errorMessage = payload["message"].ToString();
                }
            };
            
            // Act - server sends error message
            var errorMsg = new WebSocketMessage
            {
                version = "1.0",
                type = "error",
                timestamp = DateTime.UtcNow.ToString("o"),
                requestId = "server-789",
                payload = new Dictionary<string, object>
                {
                    { "code", 404 },
                    { "message", "Resource not found" }
                }
            };
            
            _mockServer.SendMessageToClient(errorMsg);
            
            // Wait for processing
            yield return new WaitForSeconds(0.5f);
            
            // Assert
            Assert.IsTrue(errorReceived, "Error message should be received");
            Assert.AreEqual(404, errorCode, "Error code should match");
            Assert.AreEqual("Resource not found", errorMessage, "Error message should match");
        }

        [UnityTest]
        public IEnumerator RequestResponse_CorrelatesCorrectly()
        {
            // Arrange
            bool responseReceived = false;
            string responseData = null;
            string requestId = Guid.NewGuid().ToString();
            
            _mockServer.SetupSuccessfulConnection();
            _client.Connect("ws://mock-server");
            
            // Wait for connection
            yield return new WaitForSeconds(0.5f);
            Assert.IsTrue(_client.IsConnected, "Client should be connected");
            
            // Setup handler for specific requestId
            _client.OnMessageReceived += (msg) => {
                if (msg.requestId == requestId && msg.type == "data_response")
                {
                    responseReceived = true;
                    responseData = msg.payload["data"].ToString();
                }
            };
            
            // Setup server to receive request and send response with same requestId
            _mockServer.OnMessageReceived += (msg) => {
                if (msg.type == "data_request" && msg.requestId == requestId)
                {
                    // Send response with same requestId
                    var response = new WebSocketMessage
                    {
                        version = "1.0",
                        type = "data_response",
                        timestamp = DateTime.UtcNow.ToString("o"),
                        requestId = msg.requestId, // Use same requestId
                        payload = new Dictionary<string, object>
                        {
                            { "data", "Requested data result" }
                        }
                    };
                    
                    _mockServer.SendMessageToClient(response);
                }
            };
            
            // Act - send data request
            var requestMessage = new WebSocketMessage
            {
                version = "1.0",
                type = "data_request",
                timestamp = DateTime.UtcNow.ToString("o"),
                requestId = requestId,
                payload = new Dictionary<string, object>
                {
                    { "query", "test_data" }
                }
            };
            
            _client.SendMessage(requestMessage);
            
            // Wait for response
            yield return new WaitForSeconds(0.5f);
            
            // Assert
            Assert.IsTrue(responseReceived, "Response should be received with matching requestId");
            Assert.AreEqual("Requested data result", responseData, "Response data should match");
        }

        [UnityTest]
        public IEnumerator ReconnectFlow_MaintainsState()
        {
            // Arrange
            int connectionCount = 0;
            _client.OnConnected += () => connectionCount++;
            
            _mockServer.SetupSuccessfulConnection();
            _client.Connect("ws://mock-server");
            
            // Wait for connection
            yield return new WaitForSeconds(0.5f);
            Assert.IsTrue(_client.IsConnected, "Client should be connected initially");
            Assert.AreEqual(1, connectionCount, "Should have connected once");
            
            // Act - simulate server disconnect and reconnect
            _mockServer.DisconnectClient();
            yield return new WaitForSeconds(0.5f);
            Assert.IsFalse(_client.IsConnected, "Client should be disconnected");
            
            // Re-enable connection and reconnect
            _mockServer.SetupSuccessfulConnection();
            _client.Connect("ws://mock-server");
            yield return new WaitForSeconds(0.5f);
            
            // Assert
            Assert.IsTrue(_client.IsConnected, "Client should be reconnected");
            Assert.AreEqual(2, connectionCount, "Should have connected twice");
            
            // Verify we can still send/receive messages
            bool messageReceived = false;
            _client.OnMessageReceived += (msg) => {
                if (msg.type == "test_response")
                {
                    messageReceived = true;
                }
            };
            
            var testMsg = new WebSocketMessage
            {
                version = "1.0",
                type = "test_response",
                timestamp = DateTime.UtcNow.ToString("o"),
                requestId = "post-reconnect",
                payload = new Dictionary<string, object> { { "test", true } }
            };
            
            _mockServer.SendMessageToClient(testMsg);
            yield return new WaitForSeconds(0.5f);
            
            Assert.IsTrue(messageReceived, "Should receive messages after reconnect");
        }

        [UnityTest]
        public IEnumerator HeartbeatExchange_MaintainsConnection()
        {
            // Arrange
            bool pingReceived = false;
            bool pongReceived = false;
            
            _mockServer.SetupSuccessfulConnection();
            _client.Connect("ws://mock-server");
            
            // Wait for connection
            yield return new WaitForSeconds(0.5f);
            Assert.IsTrue(_client.IsConnected, "Client should be connected");
            
            // Setup server to track client responses
            _mockServer.OnMessageReceived += (msg) => {
                if (msg.type == "heartbeat_response")
                {
                    pongReceived = true;
                }
            };
            
            // Setup client to track server pings
            _client.OnMessageReceived += (msg) => {
                if (msg.type == "heartbeat")
                {
                    pingReceived = true;
                }
            };
            
            // Act - server sends heartbeat ping
            var heartbeatMsg = new WebSocketMessage
            {
                version = "1.0",
                type = "heartbeat",
                timestamp = DateTime.UtcNow.ToString("o"),
                requestId = "heartbeat-test",
                payload = new Dictionary<string, object>
                {
                    { "message", "ping" }
                }
            };
            
            _mockServer.SendMessageToClient(heartbeatMsg);
            
            // Wait for heartbeat exchange
            yield return new WaitForSeconds(0.5f);
            
            // Assert
            Assert.IsTrue(pingReceived, "Client should receive heartbeat ping");
            Assert.IsTrue(pongReceived, "Server should receive heartbeat response");
            Assert.IsTrue(_client.IsConnected, "Connection should remain open");
        }
    }
} 