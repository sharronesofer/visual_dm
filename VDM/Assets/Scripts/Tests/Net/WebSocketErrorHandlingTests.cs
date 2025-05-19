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
    public class WebSocketErrorHandlingTests : WebSocketTestRunner
    {
        private const float ERROR_WAIT_TIME = 0.5f;
        
        [UnityTest]
        public IEnumerator ConnectionFailure_ShouldTriggerErrorEvent()
        {
            // Arrange
            bool errorEventTriggered = false;
            string errorMessage = null;
            
            _mockServer.StopServer(); // Ensure server is down
            
            _client = CreateAndConnectClient();
            _client.OnError += (error) => {
                errorEventTriggered = true;
                errorMessage = error;
            };
            
            // Act - Connection will fail because server is down
            
            // Wait for connection attempt to fail
            yield return new WaitForSeconds(ERROR_WAIT_TIME);
            
            // Assert
            Assert.IsTrue(errorEventTriggered, "Error event should be triggered");
            Assert.IsNotNull(errorMessage, "Error message should not be null");
            Assert.AreEqual(WebSocketConnectionStatus.Failed, _client.Status, "Connection status should be Failed");
        }
        
        [UnityTest]
        public IEnumerator ConnectionTimeout_ShouldTriggerErrorEvent()
        {
            // Arrange
            bool errorEventTriggered = false;
            
            // Setup mock server to not respond (simulating timeout)
            _mockServer.SetupTimeoutConnection();
            
            _client = CreateAndConnectClient();
            _client.ConnectionTimeout = 0.2f; // Set short timeout for test
            
            _client.OnError += (error) => {
                errorEventTriggered = true;
            };
            
            // Act - Connection will time out
            
            // Wait for timeout
            yield return new WaitForSeconds(1f);
            
            // Assert
            Assert.IsTrue(errorEventTriggered, "Error event should be triggered on timeout");
            Assert.AreEqual(WebSocketConnectionStatus.Failed, _client.Status, "Connection status should be Failed on timeout");
        }
        
        [UnityTest]
        public IEnumerator ServerError_ShouldBeHandledGracefully()
        {
            // Arrange
            bool errorEventTriggered = false;
            string errorMessage = null;
            
            // Setup mock server to send an error
            _mockServer.SetupSuccessfulConnection(); // Connect first
            
            _client = CreateAndConnectClient();
            _client.OnError += (error) => {
                errorEventTriggered = true;
                errorMessage = error;
            };
            
            yield return WaitForConnectionStatus(_client, WebSocketConnectionStatus.Connected);
            
            // Act - Simulate server error
            _mockServer.SendErrorToClient("Server error message");
            
            // Wait for error to be processed
            yield return new WaitForSeconds(ERROR_WAIT_TIME);
            
            // Assert
            Assert.IsTrue(errorEventTriggered, "Error event should be triggered");
            Assert.IsNotNull(errorMessage, "Error message should not be null");
            Assert.IsTrue(errorMessage.Contains("Server error message"), "Error message should contain the server error message");
        }
        
        [UnityTest]
        public IEnumerator InvalidMessage_ShouldTriggerErrorEvent()
        {
            // Arrange
            bool errorEventTriggered = false;
            
            _client = CreateAndConnectClient();
            _client.OnError += (error) => {
                errorEventTriggered = true;
            };
            
            yield return WaitForConnectionStatus(_client, WebSocketConnectionStatus.Connected);
            
            // Act - Send invalid JSON
            _mockServer.SendRawMessageToClient("{invalid json}");
            
            // Wait for message to be processed
            yield return new WaitForSeconds(ERROR_WAIT_TIME);
            
            // Assert
            Assert.IsTrue(errorEventTriggered, "Error event should be triggered for invalid message");
        }
        
        [UnityTest]
        public IEnumerator InternalException_ShouldBeHandledGracefully()
        {
            // Arrange
            bool errorEventTriggered = false;
            
            // Create a client with a faulty message handler that throws exception
            _client = CreateAndConnectClient();
            _client.OnMessage += (msg) => {
                throw new Exception("Test exception in message handler");
            };
            
            _client.OnError += (error) => {
                errorEventTriggered = true;
            };
            
            yield return WaitForConnectionStatus(_client, WebSocketConnectionStatus.Connected);
            
            // Act - Send a message that will trigger the exception
            _mockServer.SendMessageToClient(CreateTestMessage("test"));
            
            // Wait for message to be processed
            yield return new WaitForSeconds(ERROR_WAIT_TIME);
            
            // Assert
            Assert.IsTrue(errorEventTriggered, "Error event should be triggered for internal exception");
        }
        
        [UnityTest]
        public IEnumerator Manager_ShouldHandleClientErrors()
        {
            // Arrange
            bool managerErrorEventTriggered = false;
            string clientId = null;
            string errorMessage = null;
            
            _mockServer.SetupFailedConnection("Test connection error");
            
            _manager.OnError += (id, error) => {
                managerErrorEventTriggered = true;
                clientId = id;
                errorMessage = error;
            };
            
            // Act
            _manager.Connect(_testClientId, _testServerUrl);
            
            // Wait for error to be processed
            yield return new WaitForSeconds(ERROR_WAIT_TIME);
            
            // Assert
            Assert.IsTrue(managerErrorEventTriggered, "Manager error event should be triggered");
            Assert.AreEqual(_testClientId, clientId, "Client ID should match");
            Assert.IsNotNull(errorMessage, "Error message should not be null");
            Assert.IsTrue(errorMessage.Contains("Test connection error"), "Error should contain the expected message");
        }
        
        [UnityTest]
        public IEnumerator Manager_ShouldHandleMultipleClientErrors()
        {
            // Arrange
            string client1Id = "client1";
            string client2Id = "client2";
            
            List<string> errorClientIds = new List<string>();
            
            _mockServer.SetupFailedConnection("Test error");
            
            _manager.OnError += (id, error) => {
                errorClientIds.Add(id);
            };
            
            // Act
            _manager.Connect(client1Id, _testServerUrl);
            _manager.Connect(client2Id, _testServerUrl);
            
            // Wait for errors to be processed
            yield return new WaitForSeconds(ERROR_WAIT_TIME);
            
            // Assert
            Assert.AreEqual(2, errorClientIds.Count, "Both clients should trigger errors");
            Assert.IsTrue(errorClientIds.Contains(client1Id), "Client 1 should trigger error");
            Assert.IsTrue(errorClientIds.Contains(client2Id), "Client 2 should trigger error");
        }
        
        [UnityTest]
        public IEnumerator DisconnectDuringReconnect_ShouldStopReconnectAttempts()
        {
            // Arrange
            _mockServer.StopServer(); // Ensure server is down
            
            int reconnectAttempts = 0;
            
            _client = CreateAndConnectClient();
            _client.AutoReconnect = true;
            _client.ReconnectInterval = 0.1f;
            
            _client.OnReconnectAttempt += () => {
                reconnectAttempts++;
            };
            
            // Wait for first connection attempt to fail
            yield return new WaitForSeconds(0.3f);
            int initialAttempts = reconnectAttempts;
            
            // Act - Disconnect during reconnect attempts
            _client.Disconnect();
            
            // Wait to see if more reconnect attempts happen
            yield return new WaitForSeconds(0.5f);
            
            // Assert
            Assert.AreEqual(initialAttempts, reconnectAttempts, "No additional reconnect attempts should occur after disconnect");
            Assert.AreEqual(WebSocketConnectionStatus.Disconnected, _client.Status, "Status should be Disconnected");
        }
        
        [UnityTest]
        public IEnumerator ErrorDuringReconnect_ShouldContinueReconnectAttempts()
        {
            // Arrange
            _mockServer.StopServer(); // Ensure server is down
            
            int reconnectAttempts = 0;
            int errorCount = 0;
            
            _client = CreateAndConnectClient();
            _client.AutoReconnect = true;
            _client.ReconnectInterval = 0.1f;
            _client.MaxReconnectAttempts = 3;
            
            _client.OnReconnectAttempt += () => {
                reconnectAttempts++;
            };
            
            _client.OnError += (error) => {
                errorCount++;
            };
            
            // Act - Let reconnect attempts happen
            
            // Wait for all reconnect attempts
            yield return new WaitForSeconds(1f);
            
            // Assert
            Assert.AreEqual(3, reconnectAttempts, "Should have exactly max reconnect attempts");
            Assert.Greater(errorCount, 0, "Error events should be triggered during failed reconnects");
            Assert.AreEqual(WebSocketConnectionStatus.Failed, _client.Status, "Status should be Failed after max attempts");
        }
        
        [UnityTest]
        public IEnumerator ServerDisconnect_ShouldTriggerStatusChange()
        {
            // Arrange
            WebSocketConnectionStatus lastStatus = WebSocketConnectionStatus.Disconnected;
            bool disconnectReceived = false;
            
            _client = CreateAndConnectClient();
            _client.OnStatusChanged += (status) => {
                lastStatus = status;
                if (status == WebSocketConnectionStatus.Disconnected)
                    disconnectReceived = true;
            };
            
            yield return WaitForConnectionStatus(_client, WebSocketConnectionStatus.Connected);
            
            // Act - Simulate server disconnect
            _mockServer.DisconnectAllClients();
            
            // Wait for disconnect to be processed
            yield return new WaitForSeconds(ERROR_WAIT_TIME);
            
            // Assert
            Assert.IsTrue(disconnectReceived, "Disconnect status should be received");
            Assert.AreEqual(WebSocketConnectionStatus.Disconnected, lastStatus, "Last status should be Disconnected");
        }
        
        [UnityTest]
        public IEnumerator Manager_ShouldPropagateServerDisconnect()
        {
            // Arrange
            bool disconnectReceived = false;
            string disconnectedClientId = null;
            
            _manager.Connect(_testClientId, _testServerUrl);
            _manager.OnStatusChanged += (clientId, status) => {
                if (status == WebSocketConnectionStatus.Disconnected)
                {
                    disconnectReceived = true;
                    disconnectedClientId = clientId;
                }
            };
            
            yield return new WaitForSeconds(ERROR_WAIT_TIME);
            
            // Act - Simulate server disconnect
            _mockServer.DisconnectAllClients();
            
            // Wait for disconnect to be processed
            yield return new WaitForSeconds(ERROR_WAIT_TIME);
            
            // Assert
            Assert.IsTrue(disconnectReceived, "Manager should receive disconnect event");
            Assert.AreEqual(_testClientId, disconnectedClientId, "Disconnected client ID should match");
            Assert.AreEqual(WebSocketConnectionStatus.Disconnected, _manager.GetStatus(_testClientId), 
                "Client status should be Disconnected");
        }
    }
} 