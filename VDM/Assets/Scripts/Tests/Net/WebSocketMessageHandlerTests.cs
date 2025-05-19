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
    public class WebSocketMessageHandlerTests : WebSocketTestRunner
    {
        private WebSocketMessageHandler _handler;
        private bool _messageHandled;
        private WebSocketMessage _lastMessage;
        private string _lastClientId;
        private int _handlerCallCount;
        
        [SetUp]
        public override void Setup()
        {
            base.Setup();
            
            // Create a new handler for each test
            _handler = new WebSocketMessageHandler();
            _messageHandled = false;
            _lastMessage = null;
            _lastClientId = null;
            _handlerCallCount = 0;
        }
        
        [Test]
        public void RegisterHandler_ShouldAddHandlerToCollection()
        {
            // Arrange
            Action<string, WebSocketMessage> handler = (clientId, msg) => { };
            string messageType = "test_message";
            
            // Act
            _handler.RegisterHandler(messageType, handler);
            
            // Assert
            Assert.IsTrue(_handler.HasHandler(messageType), "Handler should be registered for message type");
        }
        
        [Test]
        public void UnregisterHandler_ShouldRemoveHandlerFromCollection()
        {
            // Arrange
            Action<string, WebSocketMessage> handler = (clientId, msg) => { };
            string messageType = "test_message";
            _handler.RegisterHandler(messageType, handler);
            
            // Act
            _handler.UnregisterHandler(messageType);
            
            // Assert
            Assert.IsFalse(_handler.HasHandler(messageType), "Handler should be removed for message type");
        }
        
        [Test]
        public void UnregisterHandler_NonExistentHandler_ShouldNotThrowException()
        {
            // Act & Assert (no exception)
            _handler.UnregisterHandler("non_existent_type");
        }
        
        [Test]
        public void UnregisterAllHandlers_ShouldClearAllHandlers()
        {
            // Arrange
            Action<string, WebSocketMessage> handler = (clientId, msg) => { };
            _handler.RegisterHandler("type1", handler);
            _handler.RegisterHandler("type2", handler);
            _handler.RegisterHandler("type3", handler);
            
            // Act
            _handler.UnregisterAllHandlers();
            
            // Assert
            Assert.IsFalse(_handler.HasHandler("type1"), "Handler for type1 should be removed");
            Assert.IsFalse(_handler.HasHandler("type2"), "Handler for type2 should be removed");
            Assert.IsFalse(_handler.HasHandler("type3"), "Handler for type3 should be removed");
        }
        
        [UnityTest]
        public IEnumerator ProcessMessage_WithRegisteredHandler_ShouldInvokeHandler()
        {
            // Arrange
            string testClientId = "test_client";
            string messageType = "test_message";
            var payload = new Dictionary<string, object> { { "data", "test_data" } };
            
            _handler.RegisterHandler(messageType, (clientId, msg) => {
                _messageHandled = true;
                _lastClientId = clientId;
                _lastMessage = msg;
            });
            
            // Act
            var message = CreateTestMessage(messageType, payload);
            _handler.ProcessMessage(testClientId, message);
            
            yield return null;
            
            // Assert
            Assert.IsTrue(_messageHandled, "Message should be handled");
            Assert.AreEqual(testClientId, _lastClientId, "Client ID should be passed to handler");
            Assert.AreEqual(messageType, _lastMessage.type, "Message type should match");
            Assert.AreEqual("test_data", _lastMessage.payload["data"], "Payload should be passed to handler");
        }
        
        [UnityTest]
        public IEnumerator ProcessMessage_WithoutRegisteredHandler_ShouldNotError()
        {
            // Arrange
            string testClientId = "test_client";
            string messageType = "unhandled_message";
            var payload = new Dictionary<string, object> { { "data", "test_data" } };
            
            bool anyHandlerInvoked = false;
            _handler.RegisterHandler("other_type", (clientId, msg) => {
                anyHandlerInvoked = true;
            });
            
            // Act
            var message = CreateTestMessage(messageType, payload);
            _handler.ProcessMessage(testClientId, message);
            
            yield return null;
            
            // Assert
            Assert.IsFalse(anyHandlerInvoked, "No handler should be invoked");
        }
        
        [UnityTest]
        public IEnumerator ProcessMessage_WithNullPayload_ShouldNotError()
        {
            // Arrange
            string testClientId = "test_client";
            string messageType = "test_message";
            bool handlerCalled = false;
            
            _handler.RegisterHandler(messageType, (clientId, msg) => {
                handlerCalled = true;
            });
            
            // Act
            var message = new WebSocketMessage { 
                type = messageType,
                payload = null 
            };
            _handler.ProcessMessage(testClientId, message);
            
            yield return null;
            
            // Assert
            Assert.IsTrue(handlerCalled, "Handler should still be called with null payload");
        }
        
        [UnityTest]
        public IEnumerator ProcessMessage_WithMultipleHandlers_ShouldInvokeCorrectHandler()
        {
            // Arrange
            string testClientId = "test_client";
            string messageType1 = "message_type_1";
            string messageType2 = "message_type_2";
            
            bool handler1Called = false;
            bool handler2Called = false;
            
            _handler.RegisterHandler(messageType1, (clientId, msg) => {
                handler1Called = true;
            });
            
            _handler.RegisterHandler(messageType2, (clientId, msg) => {
                handler2Called = true;
            });
            
            // Act - send message of type 1
            var message1 = CreateTestMessage(messageType1);
            _handler.ProcessMessage(testClientId, message1);
            
            yield return null;
            
            // Assert for message 1
            Assert.IsTrue(handler1Called, "Handler 1 should be called");
            Assert.IsFalse(handler2Called, "Handler 2 should not be called");
            
            // Reset flags
            handler1Called = false;
            handler2Called = false;
            
            // Act - send message of type 2
            var message2 = CreateTestMessage(messageType2);
            _handler.ProcessMessage(testClientId, message2);
            
            yield return null;
            
            // Assert for message 2
            Assert.IsFalse(handler1Called, "Handler 1 should not be called");
            Assert.IsTrue(handler2Called, "Handler 2 should be called");
        }
        
        [UnityTest]
        public IEnumerator RegisterHandler_CalledMultipleTimes_ShouldReplaceHandler()
        {
            // Arrange
            string testClientId = "test_client";
            string messageType = "test_message";
            int handler1CallCount = 0;
            int handler2CallCount = 0;
            
            // Register first handler
            _handler.RegisterHandler(messageType, (clientId, msg) => {
                handler1CallCount++;
            });
            
            // Act - register second handler for same type
            _handler.RegisterHandler(messageType, (clientId, msg) => {
                handler2CallCount++;
            });
            
            // Send a message
            var message = CreateTestMessage(messageType);
            _handler.ProcessMessage(testClientId, message);
            
            yield return null;
            
            // Assert
            Assert.AreEqual(0, handler1CallCount, "First handler should not be called");
            Assert.AreEqual(1, handler2CallCount, "Second handler should be called");
        }
        
        [UnityTest]
        public IEnumerator ProcessMessage_WithWildcardHandler_ShouldHandleAllMessages()
        {
            // Arrange
            string testClientId = "test_client";
            int wildcardHandlerCallCount = 0;
            WebSocketMessage lastWildcardMessage = null;
            
            // Register a wildcard handler
            _handler.RegisterHandler("*", (clientId, msg) => {
                wildcardHandlerCallCount++;
                lastWildcardMessage = msg;
            });
            
            // Act - send different types of messages
            var message1 = CreateTestMessage("type1");
            var message2 = CreateTestMessage("type2");
            var message3 = CreateTestMessage("type3");
            
            _handler.ProcessMessage(testClientId, message1);
            _handler.ProcessMessage(testClientId, message2);
            _handler.ProcessMessage(testClientId, message3);
            
            yield return null;
            
            // Assert
            Assert.AreEqual(3, wildcardHandlerCallCount, "Wildcard handler should be called for all messages");
            Assert.AreEqual("type3", lastWildcardMessage.type, "Last message should be of type3");
        }
        
        [UnityTest]
        public IEnumerator ProcessMessage_WithWildcardAndSpecificHandlers_ShouldInvokeBoth()
        {
            // Arrange
            string testClientId = "test_client";
            string specificType = "specific_type";
            
            int wildcardHandlerCallCount = 0;
            int specificHandlerCallCount = 0;
            
            // Register handlers
            _handler.RegisterHandler("*", (clientId, msg) => {
                wildcardHandlerCallCount++;
            });
            
            _handler.RegisterHandler(specificType, (clientId, msg) => {
                specificHandlerCallCount++;
            });
            
            // Act - send a specific type message
            var message = CreateTestMessage(specificType);
            _handler.ProcessMessage(testClientId, message);
            
            yield return null;
            
            // Assert
            Assert.AreEqual(1, wildcardHandlerCallCount, "Wildcard handler should be called");
            Assert.AreEqual(1, specificHandlerCallCount, "Specific handler should be called");
        }
        
        [UnityTest]
        public IEnumerator ProcessMessage_HandlerThrowsException_ShouldLogErrorAndContinue()
        {
            // Arrange
            string testClientId = "test_client";
            string messageType = "test_message";
            bool errorLogged = false;
            
            // Mock the Debug.LogError method
            Debug.LogError = (message) => {
                if (message.ToString().Contains("Exception in message handler"))
                {
                    errorLogged = true;
                }
            };
            
            _handler.RegisterHandler(messageType, (clientId, msg) => {
                throw new Exception("Test exception");
            });
            
            // Act
            var message = CreateTestMessage(messageType);
            
            // This should not throw even though the handler throws
            _handler.ProcessMessage(testClientId, message);
            
            yield return null;
            
            // Assert
            Assert.IsTrue(errorLogged, "Error should be logged when handler throws exception");
        }
    }
} 