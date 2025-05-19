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
    public class WebSocketConnectionTests : TestFramework
    {
        private GameObject _testGameObject;
        private MockWebSocketServer _mockServer;
        private WebSocketConnection _connection;

        [SetUp]
        public override void Setup()
        {
            base.Setup();
            
            // Create game objects for test
            _testGameObject = CreateTestObject("WebSocketConnectionTest");
            _mockServer = _testGameObject.AddComponent<MockWebSocketServer>();
            
            // Initialize connection
            _connection = new WebSocketConnection("test-connection");
        }

        [TearDown]
        public override void Teardown()
        {
            // Close connection before cleanup
            if (_connection != null && _connection.Status == WebSocketConnectionStatus.Connected)
            {
                _connection.Close();
            }
            
            base.Teardown();
        }

        [UnityTest]
        public IEnumerator Constructor_ShouldInitializeWithCorrectValues()
        {
            // Arrange & Act
            var connection = new WebSocketConnection("custom-id", "ws://custom-url");
            
            // Assert
            Assert.AreEqual("custom-id", connection.Id, "Id should match constructor parameter");
            Assert.AreEqual("ws://custom-url", connection.Url, "Url should match constructor parameter");
            Assert.AreEqual(WebSocketConnectionStatus.Disconnected, connection.Status, "Initial status should be Disconnected");
            
            yield return null;
        }

        [UnityTest]
        public IEnumerator Connect_ShouldUpdateStatus()
        {
            // Arrange
            _mockServer.SetupSuccessfulConnection();
            
            bool connectCalled = false;
            bool statusChanged = false;
            
            _connection.OnStatusChanged += (status) => statusChanged = true;
            
            // Act
            _connection.Connect("ws://mock-server", null, () => connectCalled = true);
            
            // Wait for connection to establish
            yield return new WaitForSeconds(0.5f);
            
            // Assert
            Assert.IsTrue(connectCalled, "Connect callback should be invoked");
            Assert.IsTrue(statusChanged, "Status changed event should be triggered");
            Assert.AreEqual(WebSocketConnectionStatus.Connected, _connection.Status, "Status should be Connected");
        }

        [UnityTest]
        public IEnumerator Connect_WithAuthToken_ShouldAttachToken()
        {
            // Arrange
            _mockServer.SetupSuccessfulConnection();
            string capturedToken = null;
            
            _mockServer.OnAuthTokenReceived += (token) => capturedToken = token;
            
            // Act
            _connection.Connect("ws://mock-server", "test-token", null);
            
            // Wait for connection and auth
            yield return new WaitForSeconds(0.5f);
            
            // Assert
            Assert.AreEqual("test-token", capturedToken, "Auth token should be passed to the server");
        }

        [UnityTest]
        public IEnumerator Close_ShouldDisconnectAndUpdateStatus()
        {
            // Arrange
            _mockServer.SetupSuccessfulConnection();
            _connection.Connect("ws://mock-server", null, null);
            
            yield return new WaitForSeconds(0.5f);
            Assert.AreEqual(WebSocketConnectionStatus.Connected, _connection.Status, "Should be connected first");
            
            bool disconnectCalled = false;
            bool statusChanged = false;
            
            _connection.OnStatusChanged += (status) => {
                if (status == WebSocketConnectionStatus.Disconnected)
                    statusChanged = true;
            };
            
            // Act
            _connection.Close(() => disconnectCalled = true);
            
            // Wait for disconnection
            yield return new WaitForSeconds(0.5f);
            
            // Assert
            Assert.IsTrue(disconnectCalled, "Disconnect callback should be invoked");
            Assert.IsTrue(statusChanged, "Status changed event should be triggered");
            Assert.AreEqual(WebSocketConnectionStatus.Disconnected, _connection.Status, "Status should be Disconnected");
        }

        [UnityTest]
        public IEnumerator Send_MessageShouldBeDeliveredToServer()
        {
            // Arrange
            _mockServer.SetupSuccessfulConnection();
            _connection.Connect("ws://mock-server", null, null);
            
            yield return new WaitForSeconds(0.5f);
            
            WebSocketMessage capturedMessage = null;
            _mockServer.OnMessageReceived += (msg) => capturedMessage = msg;
            
            // Act
            var payload = new Dictionary<string, object> { { "test", 123 }, { "hello", "world" } };
            _connection.Send("test-message", payload);
            
            // Wait for message to be processed
            yield return new WaitForSeconds(0.5f);
            
            // Assert
            Assert.IsNotNull(capturedMessage, "Message should be received by server");
            Assert.AreEqual("test-message", capturedMessage.type, "Message type should match");
            Assert.AreEqual(123, capturedMessage.payload["test"], "Message payload numeric value should match");
            Assert.AreEqual("world", capturedMessage.payload["hello"], "Message payload string value should match");
        }

        [UnityTest]
        public IEnumerator Send_WithCallback_ShouldInvokeCallbackWhenProcessed()
        {
            // Arrange
            _mockServer.SetupSuccessfulConnection();
            _connection.Connect("ws://mock-server", null, null);
            
            yield return new WaitForSeconds(0.5f);
            
            bool callbackInvoked = false;
            string requestId = null;
            
            // Act
            _connection.Send("test-message", new Dictionary<string, object>(), (id) => {
                callbackInvoked = true;
                requestId = id;
            });
            
            // Wait for message to be processed
            yield return new WaitForSeconds(0.5f);
            
            // Assert
            Assert.IsTrue(callbackInvoked, "Send callback should be invoked");
            Assert.IsNotNull(requestId, "Request ID should be returned");
        }

        [UnityTest]
        public IEnumerator Send_WhenDisconnected_ShouldQueueMessages()
        {
            // Arrange
            int messagesSent = 0;
            _mockServer.OnMessageReceived += (msg) => messagesSent++;
            
            // Send while disconnected
            _connection.Send("queued-message", new Dictionary<string, object>());
            _connection.Send("another-queued", new Dictionary<string, object>());
            
            // Verify no messages sent yet
            yield return new WaitForSeconds(0.2f);
            Assert.AreEqual(0, messagesSent, "No messages should be sent while disconnected");
            
            // Act - connect now
            _mockServer.SetupSuccessfulConnection();
            _connection.Connect("ws://mock-server", null, null);
            
            // Wait for connection and queued messages
            yield return new WaitForSeconds(1.0f);
            
            // Assert
            Assert.AreEqual(2, messagesSent, "Queued messages should be sent after connection");
        }
        
        [UnityTest]
        public IEnumerator ReceiveMessage_ShouldTriggerOnMessageEvent()
        {
            // Arrange
            _mockServer.SetupSuccessfulConnection();
            _connection.Connect("ws://mock-server", null, null);
            
            yield return new WaitForSeconds(0.5f);
            
            WebSocketMessage receivedMessage = null;
            _connection.OnMessage += (msg) => receivedMessage = msg;
            
            // Act
            var messageToSend = new WebSocketMessage
            {
                version = "1.0",
                type = "server-message",
                timestamp = DateTime.UtcNow.ToString("o"),
                payload = new Dictionary<string, object> { { "data", "value" } }
            };
            
            _mockServer.SendMessageToClient(messageToSend);
            
            // Wait for message to be processed
            yield return new WaitForSeconds(0.5f);
            
            // Assert
            Assert.IsNotNull(receivedMessage, "Message should be received");
            Assert.AreEqual("server-message", receivedMessage.type, "Message type should match");
            Assert.AreEqual("value", receivedMessage.payload["data"], "Message payload should match");
        }
        
        [UnityTest]
        public IEnumerator AutoReconnect_WhenEnabled_ShouldReconnectAfterDisconnection()
        {
            // Arrange
            _mockServer.SetupSuccessfulConnection();
            _connection.EnableAutoReconnect(true, 3, 0.1f); // Fast retry for testing
            _connection.Connect("ws://mock-server", null, null);
            
            yield return new WaitForSeconds(0.5f);
            Assert.AreEqual(WebSocketConnectionStatus.Connected, _connection.Status, "Should be connected first");
            
            bool reconnecting = false;
            bool reconnected = false;
            
            _connection.OnStatusChanged += (status) => {
                if (status == WebSocketConnectionStatus.Reconnecting)
                    reconnecting = true;
                
                if (status == WebSocketConnectionStatus.Connected && reconnecting)
                    reconnected = true;
            };
            
            // Act - simulate server disconnection
            _mockServer.DisconnectClient();
            
            // Wait for auto-reconnect attempts
            yield return new WaitForSeconds(1.0f);
            
            // Assert
            Assert.IsTrue(reconnecting, "Reconnecting status should be triggered");
            Assert.IsTrue(reconnected, "Should have reconnected automatically");
            Assert.AreEqual(WebSocketConnectionStatus.Connected, _connection.Status, "Should be connected again");
        }
        
        [UnityTest]
        public IEnumerator AutoReconnect_WhenDisabled_ShouldNotReconnect()
        {
            // Arrange
            _mockServer.SetupSuccessfulConnection();
            _connection.EnableAutoReconnect(false);
            _connection.Connect("ws://mock-server", null, null);
            
            yield return new WaitForSeconds(0.5f);
            Assert.AreEqual(WebSocketConnectionStatus.Connected, _connection.Status, "Should be connected first");
            
            bool reconnecting = false;
            _connection.OnStatusChanged += (status) => {
                if (status == WebSocketConnectionStatus.Reconnecting)
                    reconnecting = true;
            };
            
            // Act - simulate server disconnection
            _mockServer.DisconnectClient();
            
            // Wait to ensure no reconnection attempts
            yield return new WaitForSeconds(1.0f);
            
            // Assert
            Assert.IsFalse(reconnecting, "Reconnecting status should not be triggered");
            Assert.AreEqual(WebSocketConnectionStatus.Disconnected, _connection.Status, "Should remain disconnected");
        }
        
        [UnityTest]
        public IEnumerator RequestResponse_ShouldMatchRequestIds()
        {
            // Arrange
            _mockServer.SetupSuccessfulConnection();
            _connection.Connect("ws://mock-server", null, null);
            
            yield return new WaitForSeconds(0.5f);
            
            WebSocketMessage responseMessage = null;
            string capturedRequestId = null;
            
            // Setup mock server to echo back response with same request ID
            _mockServer.OnMessageReceived += (msg) => {
                capturedRequestId = msg.requestId;
                
                // Send response with same request ID
                var response = new WebSocketMessage {
                    type = "response",
                    requestId = msg.requestId,
                    timestamp = DateTime.UtcNow.ToString("o"),
                    payload = new Dictionary<string, object> { { "status", "success" } }
                };
                
                _mockServer.SendMessageToClient(response);
            };
            
            _connection.OnMessage += (msg) => {
                if (msg.type == "response")
                    responseMessage = msg;
            };
            
            // Act
            _connection.Send("request", new Dictionary<string, object>());
            
            // Wait for request-response cycle
            yield return new WaitForSeconds(0.5f);
            
            // Assert
            Assert.IsNotNull(capturedRequestId, "Request ID should be captured");
            Assert.IsNotNull(responseMessage, "Response should be received");
            Assert.AreEqual(capturedRequestId, responseMessage.requestId, "Request and response IDs should match");
        }
        
        [UnityTest]
        public IEnumerator ConnectionError_ShouldTriggerErrorEvent()
        {
            // Arrange
            _mockServer.SetupConnectionFailure();
            
            string errorMessage = null;
            _connection.OnError += (error) => errorMessage = error;
            
            // Act
            _connection.Connect("ws://invalid-server", null, null);
            
            // Wait for error to be triggered
            yield return new WaitForSeconds(0.5f);
            
            // Assert
            Assert.IsNotNull(errorMessage, "Error event should be triggered");
            Assert.IsTrue(errorMessage.Contains("connection"), "Error should mention connection issue");
        }
        
        [UnityTest]
        public IEnumerator MessageValidation_ShouldRejectInvalidMessages()
        {
            // Arrange
            _mockServer.SetupSuccessfulConnection();
            _connection.Connect("ws://mock-server", null, null);
            
            yield return new WaitForSeconds(0.5f);
            
            string validationError = null;
            _connection.OnValidationError += (error) => validationError = error;
            
            // Act - send message with missing required fields
            var invalidMessage = new WebSocketMessage {
                // Missing version and timestamp
                type = "test-type",
                payload = new Dictionary<string, object>()
            };
            
            _mockServer.SendInvalidMessageToClient(invalidMessage);
            
            // Wait for validation to occur
            yield return new WaitForSeconds(0.5f);
            
            // Assert
            Assert.IsNotNull(validationError, "Validation error should be triggered");
        }
        
        [UnityTest]
        public IEnumerator KeepAlive_ShouldSendPingMessages()
        {
            // Arrange
            _mockServer.SetupSuccessfulConnection();
            
            int pingCount = 0;
            _mockServer.OnMessageReceived += (msg) => {
                if (msg.type == "ping") 
                    pingCount++;
            };
            
            // Act - enable keep alive with short interval for testing
            _connection.EnableKeepAlive(true, 0.2f);
            _connection.Connect("ws://mock-server", null, null);
            
            // Wait for multiple ping intervals
            yield return new WaitForSeconds(0.7f);
            
            // Assert
            Assert.IsTrue(pingCount >= 2, "At least 2 ping messages should be sent");
        }
    }
} 