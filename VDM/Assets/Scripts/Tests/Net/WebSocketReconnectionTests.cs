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
    public class WebSocketReconnectionTests : WebSocketTestRunner
    {
        private const float RECONNECT_WAIT_TIME = 0.5f;
        
        [UnityTest]
        public IEnumerator Reconnect_AfterDisconnect_ShouldReestablishConnection()
        {
            // Arrange
            _client = CreateAndConnectClient();
            yield return WaitForConnectionStatus(_client, WebSocketConnectionStatus.Connected);
            
            // Act - Disconnect
            _client.Disconnect();
            yield return WaitForConnectionStatus(_client, WebSocketConnectionStatus.Disconnected);
            
            // Act - Reconnect
            _client.Reconnect();
            
            // Assert
            yield return WaitForConnectionStatus(_client, WebSocketConnectionStatus.Connected);
        }
        
        [UnityTest]
        public IEnumerator Reconnect_WithServerDown_ShouldRetryUntilServerAvailable()
        {
            // Arrange
            _mockServer.StopServer();
            _client = CreateAndConnectClient();
            
            // Wait for connection to fail
            yield return new WaitForSeconds(RECONNECT_WAIT_TIME);
            Assert.AreEqual(WebSocketConnectionStatus.Failed, _client.Status, "Connection should fail initially");
            
            // Act - Start server and attempt reconnection
            _mockServer.StartServer();
            _client.Reconnect();
            
            // Assert
            yield return WaitForConnectionStatus(_client, WebSocketConnectionStatus.Connected);
        }
        
        [UnityTest]
        public IEnumerator AutoReconnect_AfterServerDisconnect_ShouldReestablishConnection()
        {
            // Arrange
            // Enable auto reconnect and set a shorter interval for testing
            _client = CreateAndConnectClient();
            _client.AutoReconnect = true;
            _client.ReconnectInterval = 0.2f;
            
            yield return WaitForConnectionStatus(_client, WebSocketConnectionStatus.Connected);
            
            // Track reconnections
            int reconnectAttempts = 0;
            _client.OnReconnectAttempt += () => {
                reconnectAttempts++;
            };
            
            // Act - Simulate server disconnect
            _mockServer.DisconnectAllClients();
            
            // Wait for auto reconnect
            yield return new WaitForSeconds(RECONNECT_WAIT_TIME);
            
            // Assert
            Assert.Greater(reconnectAttempts, 0, "Should have attempted to reconnect");
            yield return WaitForConnectionStatus(_client, WebSocketConnectionStatus.Connected);
        }
        
        [UnityTest]
        public IEnumerator Manager_ShouldReconnectSpecificClient_AfterDisconnect()
        {
            // Arrange
            _manager.Connect(_testClientId, _testServerUrl);
            yield return new WaitForSeconds(RECONNECT_WAIT_TIME);
            
            // Assert initial connection
            Assert.AreEqual(WebSocketConnectionStatus.Connected, _manager.GetStatus(_testClientId), 
                "Client should be connected initially");
            
            // Act - Disconnect
            _manager.Disconnect(_testClientId);
            yield return new WaitForSeconds(0.1f);
            
            // Assert disconnected
            Assert.AreEqual(WebSocketConnectionStatus.Disconnected, _manager.GetStatus(_testClientId), 
                "Client should be disconnected");
            
            // Act - Reconnect
            _manager.Reconnect(_testClientId);
            yield return new WaitForSeconds(RECONNECT_WAIT_TIME);
            
            // Assert reconnected
            Assert.AreEqual(WebSocketConnectionStatus.Connected, _manager.GetStatus(_testClientId), 
                "Client should be reconnected");
        }
        
        [UnityTest]
        public IEnumerator Manager_ShouldReconnectAllClients_AfterDisconnect()
        {
            // Arrange
            string client1Id = "client1";
            string client2Id = "client2";
            
            _manager.Connect(client1Id, _testServerUrl);
            _manager.Connect(client2Id, _testServerUrl);
            yield return new WaitForSeconds(RECONNECT_WAIT_TIME);
            
            // Assert initial connections
            Assert.AreEqual(WebSocketConnectionStatus.Connected, _manager.GetStatus(client1Id), 
                "Client 1 should be connected initially");
            Assert.AreEqual(WebSocketConnectionStatus.Connected, _manager.GetStatus(client2Id), 
                "Client 2 should be connected initially");
            
            // Act - Disconnect all
            _manager.DisconnectAll();
            yield return new WaitForSeconds(0.1f);
            
            // Assert disconnected
            Assert.AreEqual(WebSocketConnectionStatus.Disconnected, _manager.GetStatus(client1Id), 
                "Client 1 should be disconnected");
            Assert.AreEqual(WebSocketConnectionStatus.Disconnected, _manager.GetStatus(client2Id), 
                "Client 2 should be disconnected");
            
            // Act - Reconnect all
            _manager.ReconnectAll();
            yield return new WaitForSeconds(RECONNECT_WAIT_TIME);
            
            // Assert reconnected
            Assert.AreEqual(WebSocketConnectionStatus.Connected, _manager.GetStatus(client1Id), 
                "Client 1 should be reconnected");
            Assert.AreEqual(WebSocketConnectionStatus.Connected, _manager.GetStatus(client2Id), 
                "Client 2 should be reconnected");
        }
        
        [UnityTest]
        public IEnumerator Reconnect_WithNewUrl_ShouldConnectToNewServer()
        {
            // Arrange
            string originalUrl = "ws://localhost:8080/original";
            string newUrl = "ws://localhost:8080/new";
            
            // Track URLs
            string connectedUrl = null;
            _mockServer.OnClientConnected += (url) => {
                connectedUrl = url;
            };
            
            _client = CreateAndConnectClient(originalUrl);
            yield return WaitForConnectionStatus(_client, WebSocketConnectionStatus.Connected);
            
            // Assert original connection
            Assert.AreEqual(originalUrl, connectedUrl, "Should connect to original URL");
            
            // Act - Disconnect and reconnect with new URL
            _client.Disconnect();
            yield return WaitForConnectionStatus(_client, WebSocketConnectionStatus.Disconnected);
            
            _client.SetUrl(newUrl);
            _client.Reconnect();
            
            // Assert
            yield return WaitForConnectionStatus(_client, WebSocketConnectionStatus.Connected);
            Assert.AreEqual(newUrl, connectedUrl, "Should connect to new URL");
        }
        
        [UnityTest]
        public IEnumerator Manager_ShouldHandleReconnectionWithNewUrl()
        {
            // Arrange
            string clientId = "test_client";
            string originalUrl = "ws://localhost:8080/original";
            string newUrl = "ws://localhost:8080/new";
            
            // Track URLs
            string connectedUrl = null;
            _mockServer.OnClientConnected += (url) => {
                connectedUrl = url;
            };
            
            _manager.Connect(clientId, originalUrl);
            yield return new WaitForSeconds(RECONNECT_WAIT_TIME);
            
            // Assert original connection
            Assert.AreEqual(originalUrl, connectedUrl, "Should connect to original URL");
            Assert.AreEqual(WebSocketConnectionStatus.Connected, _manager.GetStatus(clientId), 
                "Client should be connected initially");
            
            // Act - Disconnect
            _manager.Disconnect(clientId);
            yield return new WaitForSeconds(0.1f);
            
            // Connect with new URL
            _manager.Connect(clientId, newUrl);
            yield return new WaitForSeconds(RECONNECT_WAIT_TIME);
            
            // Assert reconnected to new URL
            Assert.AreEqual(newUrl, connectedUrl, "Should connect to new URL");
            Assert.AreEqual(WebSocketConnectionStatus.Connected, _manager.GetStatus(clientId), 
                "Client should be connected to new URL");
        }
        
        [UnityTest]
        public IEnumerator MaxReconnectAttempts_ExceedLimit_ShouldStopRetrying()
        {
            // Arrange
            _mockServer.StopServer(); // Ensure server is down
            
            _client = CreateAndConnectClient();
            _client.AutoReconnect = true;
            _client.ReconnectInterval = 0.1f;
            _client.MaxReconnectAttempts = 3;
            
            int reconnectCount = 0;
            _client.OnReconnectAttempt += () => {
                reconnectCount++;
            };
            
            // Act - Attempt connection which will fail
            // Let auto reconnect try multiple times
            yield return new WaitForSeconds(2f); 
            
            // Assert
            Assert.LessOrEqual(reconnectCount, 3, "Should not exceed max reconnect attempts");
            Assert.AreEqual(WebSocketConnectionStatus.Failed, _client.Status, 
                "Status should be Failed after exceeding max attempts");
        }
        
        [UnityTest]
        public IEnumerator ReconnectWithIncreasingBackoff_ShouldIncreaseInterval()
        {
            // Arrange
            _mockServer.StopServer(); // Ensure server is down
            
            _client = CreateAndConnectClient();
            _client.AutoReconnect = true;
            _client.ReconnectInterval = 0.1f;
            _client.UseExponentialBackoff = true;
            _client.BackoffFactor = 2.0f;
            _client.MaxReconnectAttempts = 5;
            
            float lastReconnectTime = Time.time;
            List<float> intervals = new List<float>();
            
            _client.OnReconnectAttempt += () => {
                float currentTime = Time.time;
                intervals.Add(currentTime - lastReconnectTime);
                lastReconnectTime = currentTime;
            };
            
            // Act - Attempt connection which will fail
            // Let auto reconnect try multiple times with increasing intervals
            yield return new WaitForSeconds(3f);
            
            // Assert
            Assert.GreaterOrEqual(intervals.Count, 2, "Should have at least two reconnect attempts");
            
            // Verify intervals are increasing (with some tolerance for timing variations)
            for (int i = 1; i < intervals.Count; i++)
            {
                Assert.Greater(intervals[i], intervals[i-1] * 1.5f, 
                    $"Interval should increase: {intervals[i-1]} -> {intervals[i]}");
            }
        }
    }
} 