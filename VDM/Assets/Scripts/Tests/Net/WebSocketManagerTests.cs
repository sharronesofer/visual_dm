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
    public class WebSocketManagerTests : WebSocketTestRunner
    {
        private const string SERVER_1_KEY = "server1";
        private const string SERVER_2_KEY = "server2";
        private const string SERVER_1_URL = "ws://localhost:8080/server1";
        private const string SERVER_2_URL = "ws://localhost:8080/server2";
        
        private int _messageCount;
        private int _statusChangeCount;
        private int _errorCount;
        private string _lastClientId;
        
        [SetUp]
        public override void Setup()
        {
            base.Setup();
            
            // Reset tracking variables
            _messageCount = 0;
            _statusChangeCount = 0;
            _errorCount = 0;
            _lastClientId = null;
            
            // Setup event tracking
            SetupManagerEventTracking();
        }
        
        [UnityTest]
        public IEnumerator Manager_ShouldBeSingleton()
        {
            // Arrange
            var firstManager = _manager;
            var secondManagerObject = new GameObject("SecondManager");
            var secondManager = secondManagerObject.AddComponent<WebSocketManager>();
            
            // Allow for Awake to run
            yield return null;
            
            // Assert
            Assert.IsNotNull(WebSocketManager.Instance, "WebSocketManager.Instance should not be null");
            Assert.AreEqual(firstManager, WebSocketManager.Instance, "First manager should be the singleton instance");
            Assert.IsFalse(secondManager != null && secondManager.gameObject != null, 
                "Second manager should be destroyed");
            
            // Cleanup
            if (secondManager != null && secondManager.gameObject != null)
            {
                GameObject.Destroy(secondManagerObject);
            }
        }
        
        [UnityTest]
        public IEnumerator Connect_ShouldCreateClient()
        {
            // Act
            _manager.Connect(SERVER_1_KEY, SERVER_1_URL);
            
            // Wait for connection processing
            yield return null;
            
            // Assert
            Assert.IsTrue(_manager.Clients.ContainsKey(SERVER_1_KEY), "Manager should contain client with specified key");
            Assert.IsNotNull(_manager.Clients[SERVER_1_KEY], "Client should not be null");
        }
        
        [UnityTest]
        public IEnumerator Connect_WithExistingKey_ShouldReplaceClient()
        {
            // Arrange
            _manager.Connect(SERVER_1_KEY, SERVER_1_URL);
            yield return null;
            var firstClient = _manager.Clients[SERVER_1_KEY];
            
            // Act
            _manager.Connect(SERVER_1_KEY, SERVER_1_URL + "/different");
            yield return null;
            var secondClient = _manager.Clients[SERVER_1_KEY];
            
            // Assert
            Assert.IsTrue(_manager.Clients.ContainsKey(SERVER_1_KEY), "Manager should still contain client with specified key");
            Assert.AreNotEqual(firstClient, secondClient, "Second client should be a different instance");
        }
        
        [UnityTest]
        public IEnumerator Connect_MultipleServers_ShouldManageMultipleClients()
        {
            // Act
            _manager.Connect(SERVER_1_KEY, SERVER_1_URL);
            _manager.Connect(SERVER_2_KEY, SERVER_2_URL);
            
            // Wait for connections to process
            yield return null;
            
            // Assert
            Assert.AreEqual(2, _manager.Clients.Count, "Manager should contain two clients");
            Assert.IsTrue(_manager.Clients.ContainsKey(SERVER_1_KEY), "Manager should contain first client");
            Assert.IsTrue(_manager.Clients.ContainsKey(SERVER_2_KEY), "Manager should contain second client");
        }
        
        [UnityTest]
        public IEnumerator Disconnect_ShouldRemoveClient()
        {
            // Arrange
            _manager.Connect(SERVER_1_KEY, SERVER_1_URL);
            yield return null;
            Assert.IsTrue(_manager.Clients.ContainsKey(SERVER_1_KEY), "Client should be added first");
            
            // Act
            _manager.Disconnect(SERVER_1_KEY);
            yield return null;
            
            // Assert
            Assert.IsFalse(_manager.Clients.ContainsKey(SERVER_1_KEY), "Client should be removed after disconnection");
        }
        
        [UnityTest]
        public IEnumerator Disconnect_NonExistentKey_ShouldNotError()
        {
            // Act & Assert (no exception)
            _manager.Disconnect("non-existent-key");
            yield return null;
        }
        
        [UnityTest]
        public IEnumerator Send_ShouldDeliverMessageToSpecificClient()
        {
            // Arrange
            bool firstClientMessageReceived = false;
            bool secondClientMessageReceived = false;
            
            _mockServer.OnMessageReceived += (msg) => {
                if (msg.payload.ContainsKey("clientId"))
                {
                    if (msg.payload["clientId"].ToString() == SERVER_1_KEY)
                        firstClientMessageReceived = true;
                    else if (msg.payload["clientId"].ToString() == SERVER_2_KEY)
                        secondClientMessageReceived = true;
                }
            };
            
            _manager.Connect(SERVER_1_KEY, SERVER_1_URL);
            _manager.Connect(SERVER_2_KEY, SERVER_2_URL);
            yield return null;
            
            // Act
            var message1 = CreateTestMessage("test", new Dictionary<string, object> { 
                { "clientId", SERVER_1_KEY } 
            });
            _manager.Send(SERVER_1_KEY, message1);
            
            yield return new WaitForSeconds(0.5f);
            
            // Assert
            Assert.IsTrue(firstClientMessageReceived, "Message should be received by first client");
            Assert.IsFalse(secondClientMessageReceived, "Message should not be received by second client");
        }
        
        [UnityTest]
        public IEnumerator Send_NonExistentKey_ShouldNotError()
        {
            // Act & Assert (no exception)
            var message = CreateTestMessage("test");
            _manager.Send("non-existent-key", message);
            yield return null;
        }
        
        [UnityTest]
        public IEnumerator GetStatus_ShouldReturnCorrectStatus()
        {
            // Arrange
            _manager.Connect(SERVER_1_KEY, SERVER_1_URL);
            yield return new WaitForSeconds(0.5f);
            
            // Act
            var status = _manager.GetStatus(SERVER_1_KEY);
            
            // Assert
            Assert.AreEqual(WebSocketConnectionStatus.Connected, status, "Status should be Connected");
        }
        
        [UnityTest]
        public IEnumerator GetStatus_NonExistentKey_ShouldReturnDisconnected()
        {
            // Act
            var status = _manager.GetStatus("non-existent-key");
            
            // Assert
            Assert.AreEqual(WebSocketConnectionStatus.Disconnected, status, "Status should be Disconnected for non-existent key");
            
            yield return null;
        }
        
        [UnityTest]
        public IEnumerator OnMessageReceived_ShouldBeTriggeredForSpecificClient()
        {
            // Arrange
            string messageClientId = null;
            string messageType = null;
            
            _manager.OnMessageReceived += (clientId, msg) => {
                messageClientId = clientId;
                messageType = msg.type;
            };
            
            _manager.Connect(SERVER_1_KEY, SERVER_1_URL);
            _manager.Connect(SERVER_2_KEY, SERVER_2_URL);
            yield return new WaitForSeconds(0.5f);
            
            // Act
            var message = CreateTestMessage("test_event");
            _mockServer.SendMessageToClient(message);
            
            yield return new WaitForSeconds(0.5f);
            
            // Assert
            Assert.IsNotNull(messageClientId, "Message client ID should be set");
            Assert.AreEqual("test_event", messageType, "Message type should be correct");
        }
        
        [UnityTest]
        public IEnumerator OnStatusChanged_ShouldBeTriggeredForSpecificClient()
        {
            // Arrange
            string statusClientId = null;
            WebSocketConnectionStatus newStatus = WebSocketConnectionStatus.Disconnected;
            
            _manager.OnStatusChanged += (clientId, status) => {
                statusClientId = clientId;
                newStatus = status;
            };
            
            // Act
            _manager.Connect(SERVER_1_KEY, SERVER_1_URL);
            
            yield return new WaitForSeconds(0.5f);
            
            // Assert
            Assert.IsNotNull(statusClientId, "Status client ID should be set");
            Assert.AreEqual(SERVER_1_KEY, statusClientId, "Status client ID should match");
            Assert.AreEqual(WebSocketConnectionStatus.Connected, newStatus, "Status should be Connected");
        }
        
        [UnityTest]
        public IEnumerator OnError_ShouldBeTriggeredForSpecificClient()
        {
            // Arrange
            string errorClientId = null;
            string errorMessage = null;
            
            _manager.OnError += (clientId, error) => {
                errorClientId = clientId;
                errorMessage = error;
            };
            
            _mockServer.SetupFailedConnection("Test error");
            
            // Act
            _manager.Connect(SERVER_1_KEY, SERVER_1_URL);
            
            yield return new WaitForSeconds(0.5f);
            
            // Assert
            Assert.IsNotNull(errorClientId, "Error client ID should be set");
            Assert.AreEqual(SERVER_1_KEY, errorClientId, "Error client ID should match");
            Assert.IsNotNull(errorMessage, "Error message should be set");
            Assert.IsTrue(errorMessage.Contains("Test error"), "Error message should contain the expected error");
        }
        
        [UnityTest]
        public IEnumerator OnDestroy_ShouldCleanUpAllConnections()
        {
            // Arrange
            _manager.Connect(SERVER_1_KEY, SERVER_1_URL);
            _manager.Connect(SERVER_2_KEY, SERVER_2_URL);
            yield return new WaitForSeconds(0.5f);
            
            Assert.AreEqual(2, _manager.Clients.Count, "Should have 2 connections initially");
            
            // Act
            GameObject.Destroy(_manager.gameObject);
            
            // Wait for the destruction to be processed
            yield return null;
            
            // Assert - this is somewhat limited, but we can verify the singleton is gone
            Assert.IsNull(WebSocketManager.Instance, "Instance should be null after destruction");
        }
        
        [UnityTest]
        public IEnumerator Connect_WithAuthToken_ShouldPassToken()
        {
            // Arrange
            string receivedToken = null;
            _mockServer.OnAuthTokenReceived += (token) => {
                receivedToken = token;
            };
            
            // Act
            _manager.Connect(SERVER_1_KEY, SERVER_1_URL, "test-auth-token");
            
            // Wait for connection
            yield return new WaitForSeconds(0.5f);
            
            // Assert
            Assert.AreEqual("test-auth-token", receivedToken, "Auth token should be passed to the server");
        }
        
        [UnityTest]
        public IEnumerator MultipleClients_ShouldHandleEventsIndependently()
        {
            // Arrange
            Dictionary<string, bool> messageReceived = new Dictionary<string, bool>
            {
                { SERVER_1_KEY, false },
                { SERVER_2_KEY, false }
            };
            
            _manager.OnMessageReceived += (clientId, msg) => {
                if (messageReceived.ContainsKey(clientId))
                    messageReceived[clientId] = true;
            };
            
            _manager.Connect(SERVER_1_KEY, SERVER_1_URL);
            _manager.Connect(SERVER_2_KEY, SERVER_2_URL);
            yield return new WaitForSeconds(0.5f);
            
            // Act
            var server1Message = CreateTestMessage("server1_message");
            var server2Message = CreateTestMessage("server2_message");
            
            // Send server 1 message
            _mockServer.SendMessageToClient(server1Message);
            yield return new WaitForSeconds(0.2f);
            
            // Assert for server 1
            Assert.IsTrue(messageReceived[SERVER_1_KEY], "Message should be received by first client");
            Assert.IsFalse(messageReceived[SERVER_2_KEY], "Message should not be received by second client yet");
            
            // Reset tracking for second message
            messageReceived[SERVER_1_KEY] = false;
            
            // Send server 2 message
            _mockServer.SendMessageToClient(server2Message);
            yield return new WaitForSeconds(0.2f);
            
            // Assert for server 2
            Assert.IsFalse(messageReceived[SERVER_1_KEY], "First client should not receive second message");
            Assert.IsTrue(messageReceived[SERVER_2_KEY], "Second client should receive message");
        }
    }
} 