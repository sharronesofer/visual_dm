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
    public class WebSocketProviderTests : TestFramework
    {
        private GameObject _testGameObject;
        private MockWebSocketServer _mockServer;
        private WebSocketProvider _provider;

        [SetUp]
        public override void Setup()
        {
            base.Setup();
            
            // Create game objects for test
            _testGameObject = CreateTestObject("WebSocketProviderTest");
            _mockServer = _testGameObject.AddComponent<MockWebSocketServer>();
            _provider = _testGameObject.AddComponent<WebSocketProvider>();
        }

        [TearDown]
        public override void Teardown()
        {
            // Disconnect before cleanup
            if (_provider != null && _provider.ConnectionStatus == WebSocketConnectionStatus.Connected)
            {
                _provider.Disconnect();
            }
            
            base.Teardown();
        }

        [UnityTest]
        public IEnumerator Initialize_ShouldSetupProviderWithDefaultSettings()
        {
            // Arrange
            _mockServer.SetupSuccessfulConnection();
            
            // Act
            _provider.Initialize();
            
            // Wait for initialization
            yield return new WaitForSeconds(0.5f);
            
            // Assert
            Assert.AreEqual(WebSocketConnectionStatus.Disconnected, _provider.ConnectionStatus, "Status should be disconnected initially");
            Assert.IsNotNull(_provider.GetConnection("default"), "Default connection should be created");
        }

        [UnityTest]
        public IEnumerator Connect_ShouldEstablishConnection()
        {
            // Arrange
            _mockServer.SetupSuccessfulConnection();
            _provider.Initialize();
            
            // Act
            bool connected = false;
            _provider.OnConnectionStatusChanged += (id, status) => 
            {
                if (id == "default" && status == WebSocketConnectionStatus.Connected)
                    connected = true;
            };
            _provider.Connect("default", "ws://mock-server");
            
            // Wait for connection to establish
            yield return new WaitForSeconds(0.5f);
            
            // Assert
            Assert.IsTrue(connected, "Connection established callback should fire");
            Assert.AreEqual(WebSocketConnectionStatus.Connected, _provider.ConnectionStatus, "Status should be connected");
        }

        [UnityTest]
        public IEnumerator Connect_WithAuthToken_ShouldSendAuthMessage()
        {
            // Arrange
            _mockServer.SetupSuccessfulConnection();
            _provider.Initialize();
            bool authMessageReceived = false;
            
            _mockServer.OnMessageReceived += (msg) => 
            {
                if (msg.type == "auth_request")
                    authMessageReceived = true;
            };
            
            // Act
            _provider.Connect("default", "ws://mock-server", "test-auth-token");
            
            // Wait for connection and auth message
            yield return new WaitForSeconds(0.5f);
            
            // Assert
            Assert.IsTrue(authMessageReceived, "Auth message should be sent after connection");
        }

        [UnityTest]
        public IEnumerator SendMessage_WhenConnected_ShouldDeliverMessageToServer()
        {
            // Arrange
            _mockServer.SetupSuccessfulConnection();
            _provider.Initialize();
            _provider.Connect("default", "ws://mock-server");
            
            yield return new WaitForSeconds(0.5f);
            Assert.AreEqual(WebSocketConnectionStatus.Connected, _provider.ConnectionStatus, "Should be connected first");
            
            WebSocketMessage receivedMessage = null;
            _mockServer.OnMessageReceived += (msg) => receivedMessage = msg;
            
            // Act
            _provider.SendMessage("default", "test_message", new Dictionary<string, object> { { "key", "value" } });
            
            // Wait for message to be processed
            yield return new WaitForSeconds(0.5f);
            
            // Assert
            Assert.IsNotNull(receivedMessage, "Message should be received by server");
            Assert.AreEqual("test_message", receivedMessage.type, "Message type should match");
            Assert.AreEqual("value", receivedMessage.payload["key"], "Message payload should match");
        }
        
        [UnityTest]
        public IEnumerator ReceiveMessage_ShouldTriggerCallback()
        {
            // Arrange
            _mockServer.SetupSuccessfulConnection();
            _provider.Initialize();
            _provider.Connect("default", "ws://mock-server");
            
            yield return new WaitForSeconds(0.5f);
            
            WebSocketMessage receivedMessage = null;
            _provider.Subscribe("default", "server_message", (msg) => receivedMessage = msg);
            
            // Act
            var messageToSend = new WebSocketMessage
            {
                version = "1.0",
                type = "server_message",
                timestamp = DateTime.UtcNow.ToString("o"),
                requestId = "server-1",
                payload = new Dictionary<string, object> { { "server", "data" } }
            };
            
            _mockServer.SendMessageToClient(messageToSend);
            
            // Wait for message to be processed
            yield return new WaitForSeconds(0.5f);
            
            // Assert
            Assert.IsNotNull(receivedMessage, "Message should be received by callback");
            Assert.AreEqual("server_message", receivedMessage.type, "Message type should match");
            Assert.AreEqual("data", receivedMessage.payload["server"], "Message payload should match");
        }
        
        [UnityTest]
        public IEnumerator Disconnect_ShouldCloseConnection()
        {
            // Arrange
            _mockServer.SetupSuccessfulConnection();
            _provider.Initialize();
            _provider.Connect("default", "ws://mock-server");
            
            yield return new WaitForSeconds(0.5f);
            Assert.AreEqual(WebSocketConnectionStatus.Connected, _provider.ConnectionStatus, "Should be connected first");
            
            bool disconnectTriggered = false;
            _provider.OnConnectionStatusChanged += (id, status) => 
            {
                if (id == "default" && status == WebSocketConnectionStatus.Disconnected)
                    disconnectTriggered = true;
            };
            
            // Act
            _provider.Disconnect("default");
            
            // Wait for disconnection to process
            yield return new WaitForSeconds(0.5f);
            
            // Assert
            Assert.IsTrue(disconnectTriggered, "Disconnect event should be triggered");
            Assert.AreEqual(WebSocketConnectionStatus.Disconnected, _provider.ConnectionStatus, "Status should be disconnected");
        }
        
        [UnityTest]
        public IEnumerator GetConnection_InvalidConnectionId_ShouldReturnNull()
        {
            // Arrange
            _provider.Initialize();
            
            // Act
            var connection = _provider.GetConnection("nonexistent");
            
            // Assert
            yield return null;
            Assert.IsNull(connection, "Non-existent connection should return null");
        }
        
        [UnityTest]
        public IEnumerator MultipleConnections_ShouldBeHandledIndependently()
        {
            // Arrange
            _mockServer.SetupSuccessfulConnection();
            _provider.Initialize();
            
            // Act - Connect to two different endpoints
            _provider.CreateConnection("metrics", "ws://metrics-server");
            _provider.CreateConnection("ai", "ws://ai-server");
            
            _provider.Connect("metrics", "ws://metrics-server");
            _provider.Connect("ai", "ws://ai-server");
            
            // Wait for connections to establish
            yield return new WaitForSeconds(0.5f);
            
            // Disconnect one connection
            _provider.Disconnect("metrics");
            
            // Wait for disconnection to process
            yield return new WaitForSeconds(0.5f);
            
            // Assert
            Assert.IsNotNull(_provider.GetConnection("metrics"), "Metrics connection should exist");
            Assert.IsNotNull(_provider.GetConnection("ai"), "AI connection should exist");
            Assert.AreEqual(WebSocketConnectionStatus.Disconnected, _provider.GetConnectionStatus("metrics"), "Metrics should be disconnected");
            Assert.AreEqual(WebSocketConnectionStatus.Connected, _provider.GetConnectionStatus("ai"), "AI should still be connected");
        }
        
        [UnityTest]
        public IEnumerator Reconnect_AfterDisconnection_ShouldEstablishNewConnection()
        {
            // Arrange
            _mockServer.SetupSuccessfulConnection();
            _provider.Initialize();
            _provider.Connect("default", "ws://mock-server");
            
            yield return new WaitForSeconds(0.5f);
            Assert.AreEqual(WebSocketConnectionStatus.Connected, _provider.ConnectionStatus, "Should be connected first");
            
            _provider.Disconnect("default");
            yield return new WaitForSeconds(0.5f);
            Assert.AreEqual(WebSocketConnectionStatus.Disconnected, _provider.ConnectionStatus, "Should be disconnected");
            
            // Act
            bool reconnected = false;
            _provider.OnConnectionStatusChanged += (id, status) => 
            {
                if (id == "default" && status == WebSocketConnectionStatus.Connected)
                    reconnected = true;
            };
            
            _provider.Connect("default", "ws://mock-server");
            
            // Wait for reconnection
            yield return new WaitForSeconds(0.5f);
            
            // Assert
            Assert.IsTrue(reconnected, "Reconnection event should be triggered");
            Assert.AreEqual(WebSocketConnectionStatus.Connected, _provider.ConnectionStatus, "Status should be connected again");
        }
        
        [UnityTest]
        public IEnumerator AutoReconnect_AfterServerDisconnect_ShouldAttemptReconnection()
        {
            // Arrange
            _mockServer.SetupSuccessfulConnection();
            _provider.Initialize();
            _provider.EnableAutoReconnect("default", true, 3, 0.1f); // Fast reconnect for testing
            _provider.Connect("default", "ws://mock-server");
            
            yield return new WaitForSeconds(0.5f);
            Assert.AreEqual(WebSocketConnectionStatus.Connected, _provider.ConnectionStatus, "Should be connected first");
            
            bool reconnecting = false;
            bool reconnected = false;
            
            _provider.OnConnectionStatusChanged += (id, status) => 
            {
                if (id == "default" && status == WebSocketConnectionStatus.Reconnecting)
                    reconnecting = true;
                
                if (id == "default" && status == WebSocketConnectionStatus.Connected && reconnecting)
                    reconnected = true;
            };
            
            // Act - simulate server disconnecting the client
            _mockServer.DisconnectClient();
            
            // Wait for auto-reconnect attempts
            yield return new WaitForSeconds(1.0f);
            
            // Assert
            Assert.IsTrue(reconnecting, "Reconnecting state should be triggered");
            Assert.IsTrue(reconnected, "Should have reconnected automatically");
            Assert.AreEqual(WebSocketConnectionStatus.Connected, _provider.ConnectionStatus, "Should be connected again");
        }
        
        [UnityTest]
        public IEnumerator Subscribe_ShouldFilterMessagesByType()
        {
            // Arrange
            _mockServer.SetupSuccessfulConnection();
            _provider.Initialize();
            _provider.Connect("default", "ws://mock-server");
            
            yield return new WaitForSeconds(0.5f);
            
            WebSocketMessage typeAMessage = null;
            WebSocketMessage typeBMessage = null;
            
            _provider.Subscribe("default", "type_a", (msg) => typeAMessage = msg);
            _provider.Subscribe("default", "type_b", (msg) => typeBMessage = msg);
            
            // Act - send both message types
            var messageA = new WebSocketMessage
            {
                version = "1.0",
                type = "type_a",
                timestamp = DateTime.UtcNow.ToString("o"),
                payload = new Dictionary<string, object> { { "source", "a" } }
            };
            
            var messageB = new WebSocketMessage
            {
                version = "1.0",
                type = "type_b",
                timestamp = DateTime.UtcNow.ToString("o"),
                payload = new Dictionary<string, object> { { "source", "b" } }
            };
            
            _mockServer.SendMessageToClient(messageA);
            yield return new WaitForSeconds(0.2f);
            _mockServer.SendMessageToClient(messageB);
            yield return new WaitForSeconds(0.2f);
            
            // Assert
            Assert.IsNotNull(typeAMessage, "Type A message should be received");
            Assert.IsNotNull(typeBMessage, "Type B message should be received");
            Assert.AreEqual("a", typeAMessage.payload["source"], "Type A payload should match");
            Assert.AreEqual("b", typeBMessage.payload["source"], "Type B payload should match");
        }
        
        [UnityTest]
        public IEnumerator Unsubscribe_ShouldStopReceivingMessages()
        {
            // Arrange
            _mockServer.SetupSuccessfulConnection();
            _provider.Initialize();
            _provider.Connect("default", "ws://mock-server");
            
            yield return new WaitForSeconds(0.5f);
            
            int messageCount = 0;
            Action<WebSocketMessage> handler = (msg) => messageCount++;
            
            // Subscribe and verify it works
            _provider.Subscribe("default", "test_type", handler);
            
            var message = new WebSocketMessage
            {
                version = "1.0",
                type = "test_type",
                timestamp = DateTime.UtcNow.ToString("o"),
                payload = new Dictionary<string, object>()
            };
            
            _mockServer.SendMessageToClient(message);
            yield return new WaitForSeconds(0.2f);
            Assert.AreEqual(1, messageCount, "Should receive message while subscribed");
            
            // Act - unsubscribe
            _provider.Unsubscribe("default", "test_type", handler);
            
            // Send another message
            _mockServer.SendMessageToClient(message);
            yield return new WaitForSeconds(0.2f);
            
            // Assert
            Assert.AreEqual(1, messageCount, "Should not receive message after unsubscribing");
        }
    }
} 