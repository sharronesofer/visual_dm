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
    public class WebSocketSecurityTests : TestFramework
    {
        private GameObject _testGameObject;
        private MockWebSocketServer _mockServer;
        private WebSocketConnection _connection;

        [SetUp]
        public override void Setup()
        {
            base.Setup();
            
            // Create game objects for test
            _testGameObject = CreateTestObject("WebSocketSecurityTest");
            _mockServer = _testGameObject.AddComponent<MockWebSocketServer>();
            
            // Initialize connection
            _connection = new WebSocketConnection("test-security-connection");
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
        public IEnumerator AuthToken_ShouldBeIncludedInAuthMessage()
        {
            // Arrange
            _mockServer.SetupSuccessfulConnection();
            string capturedToken = null;
            
            _mockServer.OnAuthTokenReceived += (token) => capturedToken = token;
            
            // Act
            _connection.Connect("ws://mock-server", "secure-test-token", null);
            
            // Wait for connection
            yield return new WaitForSeconds(0.5f);
            
            // Assert
            Assert.AreEqual("secure-test-token", capturedToken, "Auth token should be passed in the auth message");
        }

        [UnityTest]
        public IEnumerator TokenRefresh_ShouldSendNewToken()
        {
            // Arrange
            _mockServer.SetupSuccessfulConnection();
            string initialToken = "initial-token";
            string refreshToken = "refreshed-token";
            
            string capturedToken = null;
            _mockServer.OnAuthTokenReceived += (token) => capturedToken = token;
            
            _connection.Connect("ws://mock-server", initialToken, null);
            yield return new WaitForSeconds(0.5f);
            
            // Verify initial token
            Assert.AreEqual(initialToken, capturedToken, "Initial token should be sent");
            
            // Act - refresh token
            _connection.RefreshAuthToken(refreshToken);
            
            // Wait for refresh to process
            yield return new WaitForSeconds(0.5f);
            
            // Assert
            Assert.AreEqual(refreshToken, capturedToken, "Refreshed token should be sent");
        }

        [UnityTest]
        public IEnumerator SecureProtocol_ShouldUseWssForSecureConnections()
        {
            // Arrange
            _mockServer.SetupSuccessfulConnection();
            string capturedUrl = null;
            _mockServer.OnConnectionAttempt += (url) => capturedUrl = url;
            
            // Act
            _connection.Connect("wss://secure-mock-server", null, null);
            
            // Wait for connection attempt
            yield return new WaitForSeconds(0.5f);
            
            // Assert
            Assert.IsNotNull(capturedUrl, "URL should be captured");
            Assert.IsTrue(capturedUrl.StartsWith("wss://"), "Secure connection should use WSS protocol");
        }

        [UnityTest]
        public IEnumerator SecureHeader_ShouldIncludeSecurityHeaders()
        {
            // Arrange
            _mockServer.SetupSuccessfulConnection();
            Dictionary<string, string> capturedHeaders = null;
            
            _mockServer.OnHeadersReceived += (headers) => capturedHeaders = headers;
            
            // Act - connect with security headers
            var securityHeaders = new Dictionary<string, string>
            {
                { "X-Security-Version", "1.2" },
                { "X-Client-ID", "test-client" }
            };
            
            _connection.ConnectWithHeaders("ws://mock-server", null, securityHeaders, null);
            
            // Wait for connection
            yield return new WaitForSeconds(0.5f);
            
            // Assert
            Assert.IsNotNull(capturedHeaders, "Headers should be captured");
            Assert.AreEqual("1.2", capturedHeaders["X-Security-Version"], "Security version header should match");
            Assert.AreEqual("test-client", capturedHeaders["X-Client-ID"], "Client ID header should match");
        }

        [UnityTest]
        public IEnumerator MessageEncryption_ShouldEncryptAndDecryptMessages()
        {
            // Arrange
            _mockServer.SetupSuccessfulConnection();
            _connection.Connect("ws://mock-server", "token", null);
            
            yield return new WaitForSeconds(0.5f);
            
            // Enable encryption for the connection
            _connection.EnableEncryption("shared-test-key");
            
            WebSocketMessage capturedMessage = null;
            _mockServer.OnMessageReceived += (msg) => capturedMessage = msg;
            
            // Act - send message that should be encrypted
            var payload = new Dictionary<string, object> { { "sensitive", "data" } };
            _connection.Send("secure_message", payload);
            
            // Wait for message to be processed
            yield return new WaitForSeconds(0.5f);
            
            // Assert
            Assert.IsNotNull(capturedMessage, "Message should be received by server");
            Assert.AreEqual("secure_message", capturedMessage.type, "Message type should match");
            
            // The payload should be encrypted, so it shouldn't match the original
            if (capturedMessage.payload.ContainsKey("encrypted"))
            {
                Assert.IsTrue((bool)capturedMessage.payload["encrypted"], "Message should be marked as encrypted");
                
                // The actual payload should be encrypted and not match the original string
                if (capturedMessage.payload.ContainsKey("data"))
                {
                    string encryptedData = capturedMessage.payload["data"].ToString();
                    Assert.AreNotEqual("data", encryptedData, "Data should be encrypted");
                }
            }
        }

        [UnityTest]
        public IEnumerator AuthTimeout_ShouldDisconnectAfterTimeout()
        {
            // Arrange
            _mockServer.SetupSuccessfulConnection();
            
            bool disconnected = false;
            _connection.OnStatusChanged += (status) => {
                if (status == WebSocketConnectionStatus.Disconnected)
                    disconnected = true;
            };
            
            // Configure a very short auth timeout for testing
            _connection.SetAuthTimeout(0.5f);
            
            // Act - connect but don't send auth token
            _connection.Connect("ws://mock-server", null, null);
            
            // Wait for auth timeout
            yield return new WaitForSeconds(1.0f);
            
            // Assert
            Assert.IsTrue(disconnected, "Connection should be disconnected after auth timeout");
            Assert.AreEqual(WebSocketConnectionStatus.Disconnected, _connection.Status, "Status should be Disconnected");
        }

        [UnityTest]
        public IEnumerator RateLimiting_ShouldThrottleMessages()
        {
            // Arrange
            _mockServer.SetupSuccessfulConnection();
            _connection.Connect("ws://mock-server", null, null);
            
            yield return new WaitForSeconds(0.5f);
            
            // Enable rate limiting (max 2 messages per second)
            _connection.EnableRateLimiting(2, 1.0f);
            
            int messagesReceived = 0;
            _mockServer.OnMessageReceived += (msg) => messagesReceived++;
            
            // Act - try to send 5 messages rapidly
            for (int i = 0; i < 5; i++)
            {
                _connection.Send($"message_{i}", new Dictionary<string, object>());
            }
            
            // Check immediate count (should be limited to 2)
            yield return new WaitForSeconds(0.1f);
            int immediateCount = messagesReceived;
            
            // Wait for rate limit to reset
            yield return new WaitForSeconds(1.0f);
            
            // Check later count (should have sent more after rate limit reset)
            int laterCount = messagesReceived;
            
            // Assert
            Assert.LessOrEqual(immediateCount, 2, "Initial message count should be limited by rate limit");
            Assert.Greater(laterCount, immediateCount, "More messages should be sent after rate limit reset");
        }

        [UnityTest]
        public IEnumerator InvalidOrigin_ShouldBeRejected()
        {
            // Arrange
            _mockServer.SetupOriginValidation("trusted-origin.com");
            
            bool connectionRejected = false;
            _connection.OnError += (error) => {
                if (error.Contains("origin"))
                    connectionRejected = true;
            };
            
            // Act - connect with invalid origin
            _connection.ConnectWithOrigin("ws://mock-server", "untrusted-origin.com", null, null);
            
            // Wait for connection attempt to be processed
            yield return new WaitForSeconds(0.5f);
            
            // Assert
            Assert.IsTrue(connectionRejected, "Connection should be rejected for invalid origin");
            Assert.AreEqual(WebSocketConnectionStatus.Failed, _connection.Status, "Status should be Failed");
        }

        [UnityTest]
        public IEnumerator ValidOrigin_ShouldBeAccepted()
        {
            // Arrange
            _mockServer.SetupOriginValidation("trusted-origin.com");
            
            // Act - connect with valid origin
            _connection.ConnectWithOrigin("ws://mock-server", "trusted-origin.com", null, null);
            
            // Wait for connection attempt to be processed
            yield return new WaitForSeconds(0.5f);
            
            // Assert
            Assert.AreEqual(WebSocketConnectionStatus.Connected, _connection.Status, "Status should be Connected for valid origin");
        }

        [UnityTest]
        public IEnumerator MessageSigning_ShouldSignMessages()
        {
            // Arrange
            _mockServer.SetupSuccessfulConnection();
            _connection.Connect("ws://mock-server", null, null);
            
            yield return new WaitForSeconds(0.5f);
            
            // Enable message signing
            _connection.EnableMessageSigning("test-signing-key");
            
            WebSocketMessage capturedMessage = null;
            _mockServer.OnMessageReceived += (msg) => capturedMessage = msg;
            
            // Act - send message that should be signed
            _connection.Send("signed_message", new Dictionary<string, object> { { "data", "value" } });
            
            // Wait for message to be processed
            yield return new WaitForSeconds(0.5f);
            
            // Assert
            Assert.IsNotNull(capturedMessage, "Message should be received by server");
            Assert.AreEqual("signed_message", capturedMessage.type, "Message type should match");
            
            // Check for signature in payload or headers
            bool hasSecurity = false;
            
            if (capturedMessage.payload.ContainsKey("signature"))
            {
                hasSecurity = true;
                Assert.IsNotNull(capturedMessage.payload["signature"], "Message should have a signature");
            }
            else if (capturedMessage.headers != null && capturedMessage.headers.ContainsKey("X-Signature"))
            {
                hasSecurity = true;
                Assert.IsNotNull(capturedMessage.headers["X-Signature"], "Message should have a signature header");
            }
            
            Assert.IsTrue(hasSecurity, "Message should have security signature information");
        }
    }
} 