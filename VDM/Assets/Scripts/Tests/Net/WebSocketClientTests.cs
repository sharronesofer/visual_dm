using System;
using System.Collections;
using System.Collections.Generic;
using System.Threading.Tasks;
using UnityEngine;
using UnityEngine.TestTools;
using NUnit.Framework;
using VisualDM.Net;
using System.Text;
using UnityEngine.Networking;

namespace VDM.Tests.Net
{
    [TestFixture]
    public class WebSocketClientTests : TestFramework
    {
        private GameObject _testGameObject;
        private MockWebSocketServer _mockServer;
        private WebSocketClient _client;

        [SetUp]
        public override void Setup()
        {
            base.Setup();
            
            // Create game objects for test
            _testGameObject = CreateTestObject("WebSocketClientTest");
            _mockServer = _testGameObject.AddComponent<MockWebSocketServer>();
            
            // Create client
            _client = new WebSocketClient("test-client");
        }

        [TearDown]
        public override void Teardown()
        {
            // Disconnect client if connected
            if (_client != null && _client.IsConnected)
            {
                _client.Disconnect();
            }
            
            base.Teardown();
        }

        [UnityTest]
        public IEnumerator Constructor_ShouldInitializeWithDefaultValues()
        {
            // Act
            var client = new WebSocketClient("test-client-id");
            
            // Assert
            Assert.AreEqual("test-client-id", client.Id, "Client ID should match constructor parameter");
            Assert.IsFalse(client.IsConnected, "Client should not be connected initially");
            Assert.IsNull(client.Url, "URL should be null initially");
            
            yield return null;
        }

        [UnityTest]
        public IEnumerator Connect_ShouldEstablishConnection()
        {
            // Arrange
            _mockServer.SetupSuccessfulConnection();
            
            bool connectCallbackCalled = false;
            bool messageEventTriggered = false;
            
            _client.OnConnected += () => connectCallbackCalled = true;
            _client.OnMessage += (msg) => messageEventTriggered = true;
            
            // Act
            _client.Connect("ws://mock-server");
            
            // Wait for connection to establish
            yield return new WaitForSeconds(0.5f);
            
            // Assert
            Assert.IsTrue(connectCallbackCalled, "Connected callback should be called");
            Assert.IsTrue(_client.IsConnected, "Client should be connected");
            Assert.AreEqual("ws://mock-server", _client.Url, "URL should be set correctly");
        }

        [UnityTest]
        public IEnumerator Connect_WithFailure_ShouldTriggerErrorCallback()
        {
            // Arrange
            _mockServer.SetupFailedConnection("Network error");
            
            bool errorCallbackCalled = false;
            string errorMessage = null;
            
            _client.OnError += (error) => {
                errorCallbackCalled = true;
                errorMessage = error;
            };
            
            // Act
            _client.Connect("ws://failing-server");
            
            // Wait for error to occur
            yield return new WaitForSeconds(0.5f);
            
            // Assert
            Assert.IsTrue(errorCallbackCalled, "Error callback should be called");
            Assert.IsFalse(_client.IsConnected, "Client should not be connected");
            Assert.IsNotNull(errorMessage, "Error message should be provided");
            Assert.IsTrue(errorMessage.Contains("Network error"), "Error message should contain reason");
        }

        [UnityTest]
        public IEnumerator Disconnect_ShouldCloseConnection()
        {
            // Arrange
            _mockServer.SetupSuccessfulConnection();
            _client.Connect("ws://mock-server");
            
            yield return new WaitForSeconds(0.5f);
            Assert.IsTrue(_client.IsConnected, "Client should be connected first");
            
            bool disconnectCallbackCalled = false;
            _client.OnDisconnected += () => disconnectCallbackCalled = true;
            
            // Act
            _client.Disconnect();
            
            // Wait for disconnection to complete
            yield return new WaitForSeconds(0.5f);
            
            // Assert
            Assert.IsTrue(disconnectCallbackCalled, "Disconnected callback should be called");
            Assert.IsFalse(_client.IsConnected, "Client should be disconnected");
        }

        [UnityTest]
        public IEnumerator SendMessage_ShouldDeliverToServer()
        {
            // Arrange
            _mockServer.SetupSuccessfulConnection();
            _client.Connect("ws://mock-server");
            
            yield return new WaitForSeconds(0.5f);
            
            WebSocketMessage receivedMessage = null;
            _mockServer.OnMessageReceived += (msg) => receivedMessage = msg;
            
            // Act
            var message = new WebSocketMessage
            {
                version = "1.0",
                type = "client_message",
                timestamp = DateTime.UtcNow.ToString("o"),
                requestId = "test-request-1",
                payload = new Dictionary<string, object> { { "test", "data" } }
            };
            
            _client.SendMessage(message);
            
            // Wait for message to be processed
            yield return new WaitForSeconds(0.5f);
            
            // Assert
            Assert.IsNotNull(receivedMessage, "Message should be received by server");
            Assert.AreEqual("client_message", receivedMessage.type, "Message type should match");
            Assert.AreEqual("test-request-1", receivedMessage.requestId, "Request ID should match");
            Assert.AreEqual("data", receivedMessage.payload["test"], "Payload should match");
        }

        [UnityTest]
        public IEnumerator ReceiveMessage_ShouldTriggerCallback()
        {
            // Arrange
            _mockServer.SetupSuccessfulConnection();
            _client.Connect("ws://mock-server");
            
            yield return new WaitForSeconds(0.5f);
            
            WebSocketMessage receivedMessage = null;
            _client.OnMessage += (msg) => receivedMessage = msg;
            
            // Act
            var message = new WebSocketMessage
            {
                version = "1.0",
                type = "server_message",
                timestamp = DateTime.UtcNow.ToString("o"),
                requestId = "server-1",
                payload = new Dictionary<string, object> { { "response", "value" } }
            };
            
            _mockServer.SendMessageToClient(message);
            
            // Wait for message to be processed
            yield return new WaitForSeconds(0.5f);
            
            // Assert
            Assert.IsNotNull(receivedMessage, "Message should be received by client");
            Assert.AreEqual("server_message", receivedMessage.type, "Message type should match");
            Assert.AreEqual("server-1", receivedMessage.requestId, "Request ID should match");
            Assert.AreEqual("value", receivedMessage.payload["response"], "Payload should match");
        }

        [UnityTest]
        public IEnumerator ServerDisconnect_ShouldTriggerCallback()
        {
            // Arrange
            _mockServer.SetupSuccessfulConnection();
            _client.Connect("ws://mock-server");
            
            yield return new WaitForSeconds(0.5f);
            
            bool disconnectCallbackCalled = false;
            _client.OnDisconnected += () => disconnectCallbackCalled = true;
            
            // Act - server initiates disconnect
            _mockServer.DisconnectClient();
            
            // Wait for disconnection to be processed
            yield return new WaitForSeconds(0.5f);
            
            // Assert
            Assert.IsTrue(disconnectCallbackCalled, "Disconnected callback should be called");
            Assert.IsFalse(_client.IsConnected, "Client should be disconnected");
        }

        [UnityTest]
        public IEnumerator NetworkInterruption_ShouldTriggerDisconnect()
        {
            // Arrange
            _mockServer.SetupSuccessfulConnection();
            _client.Connect("ws://mock-server");
            
            yield return new WaitForSeconds(0.5f);
            
            bool disconnectCallbackCalled = false;
            _client.OnDisconnected += () => disconnectCallbackCalled = true;
            
            // Act - simulate network failure
            _mockServer.SimulateNetworkFailure();
            
            // Wait for disconnection to be processed
            yield return new WaitForSeconds(0.5f);
            
            // Assert
            Assert.IsTrue(disconnectCallbackCalled, "Disconnected callback should be called");
            Assert.IsFalse(_client.IsConnected, "Client should be disconnected");
        }

        [UnityTest]
        public IEnumerator InvalidMessage_ShouldTriggerErrorCallback()
        {
            // Arrange
            _mockServer.SetupSuccessfulConnection();
            _client.Connect("ws://mock-server");
            
            yield return new WaitForSeconds(0.5f);
            
            bool errorCallbackCalled = false;
            string errorMessage = null;
            
            _client.OnError += (error) => {
                errorCallbackCalled = true;
                errorMessage = error;
            };
            
            // Act - send invalid JSON
            string invalidJson = "{ this is not valid JSON }";
            
            // Use reflection to bypass normal checks
            var messageReceivedMethod = typeof(WebSocketClient).GetMethod(
                "HandleMessageReceived", 
                System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.NonPublic);
                
            messageReceivedMethod.Invoke(_client, new object[] { invalidJson });
            
            // Wait for error to be processed
            yield return new WaitForSeconds(0.5f);
            
            // Assert
            Assert.IsTrue(errorCallbackCalled, "Error callback should be called");
            Assert.IsTrue(errorMessage.Contains("Invalid message"), "Error should mention invalid message");
        }

        [UnityTest]
        public IEnumerator ConnectionWithCustomHeaders_ShouldSendHeaders()
        {
            // Arrange
            _mockServer.SetupSuccessfulConnection();
            
            Dictionary<string, string> capturedHeaders = null;
            _mockServer.OnHeadersReceived += (headers) => capturedHeaders = headers;
            
            // Create custom headers
            Dictionary<string, string> customHeaders = new Dictionary<string, string>
            {
                { "X-Client-Version", "1.2.3" },
                { "X-Client-Type", "Unity" },
                { "Authorization", "Bearer test-token" }
            };
            
            // Act
            _client.ConnectWithHeaders("ws://mock-server", customHeaders);
            
            // Wait for connection
            yield return new WaitForSeconds(0.5f);
            
            // Assert
            Assert.IsNotNull(capturedHeaders, "Headers should be captured by server");
            Assert.AreEqual("1.2.3", capturedHeaders["X-Client-Version"], "Client version header should match");
            Assert.AreEqual("Unity", capturedHeaders["X-Client-Type"], "Client type header should match");
            Assert.AreEqual("Bearer test-token", capturedHeaders["Authorization"], "Authorization header should match");
        }

        [UnityTest]
        public IEnumerator ConnectionTimeout_ShouldTriggerErrorCallback()
        {
            // Arrange
            _mockServer.SetupConnectionTimeout();
            
            bool errorCallbackCalled = false;
            string errorMessage = null;
            
            _client.OnError += (error) => {
                errorCallbackCalled = true;
                errorMessage = error;
            };
            
            // Set a short timeout
            _client.ConnectionTimeout = 1.0f;
            
            // Act
            _client.Connect("ws://timeout-server");
            
            // Wait for timeout to occur
            yield return new WaitForSeconds(1.2f);
            
            // Assert
            Assert.IsTrue(errorCallbackCalled, "Error callback should be called");
            Assert.IsFalse(_client.IsConnected, "Client should not be connected");
            Assert.IsTrue(errorMessage.Contains("timeout"), "Error message should mention timeout");
        }

        [UnityTest]
        public IEnumerator BinaryMessage_ShouldBeProcessedCorrectly()
        {
            // Arrange
            _mockServer.SetupSuccessfulConnection();
            _client.Connect("ws://mock-server");
            
            yield return new WaitForSeconds(0.5f);
            
            string receivedMessageType = null;
            byte[] receivedBinaryData = null;
            
            _client.OnBinaryMessage += (type, data) => {
                receivedMessageType = type;
                receivedBinaryData = data;
            };
            
            // Act - send binary message
            string messageType = "binary_data";
            byte[] binaryData = Encoding.UTF8.GetBytes("This is binary test data");
            
            _mockServer.SendBinaryMessageToClient(messageType, binaryData);
            
            // Wait for message to be processed
            yield return new WaitForSeconds(0.5f);
            
            // Assert
            Assert.IsNotNull(receivedMessageType, "Message type should be received");
            Assert.IsNotNull(receivedBinaryData, "Binary data should be received");
            Assert.AreEqual("binary_data", receivedMessageType, "Message type should match");
            CollectionAssert.AreEqual(binaryData, receivedBinaryData, "Binary data should match");
        }

        [UnityTest]
        public IEnumerator ReconnectAfterDisconnect_ShouldEstablishNewConnection()
        {
            // Arrange
            _mockServer.SetupSuccessfulConnection();
            _client.Connect("ws://mock-server");
            
            yield return new WaitForSeconds(0.5f);
            Assert.IsTrue(_client.IsConnected, "Client should be connected first");
            
            _client.Disconnect();
            yield return new WaitForSeconds(0.5f);
            Assert.IsFalse(_client.IsConnected, "Client should be disconnected after first disconnect");
            
            int connectCallCount = 0;
            _client.OnConnected += () => connectCallCount++;
            
            // Act
            _client.Connect("ws://mock-server");
            
            // Wait for reconnection
            yield return new WaitForSeconds(0.5f);
            
            // Assert
            Assert.AreEqual(1, connectCallCount, "Connected callback should be called once");
            Assert.IsTrue(_client.IsConnected, "Client should be connected again");
        }

        [UnityTest]
        public IEnumerator SendMessageWhileDisconnected_ShouldTriggerError()
        {
            // Arrange
            bool errorCallbackCalled = false;
            string errorMessage = null;
            
            _client.OnError += (error) => {
                errorCallbackCalled = true;
                errorMessage = error;
            };
            
            // Act - try to send message while disconnected
            var message = new WebSocketMessage
            {
                version = "1.0",
                type = "test_message",
                timestamp = DateTime.UtcNow.ToString("o"),
                payload = new Dictionary<string, object>()
            };
            
            _client.SendMessage(message);
            
            // Wait a moment
            yield return new WaitForSeconds(0.2f);
            
            // Assert
            Assert.IsTrue(errorCallbackCalled, "Error callback should be called");
            Assert.IsTrue(errorMessage.Contains("not connected"), "Error message should mention not being connected");
        }
    }
} 