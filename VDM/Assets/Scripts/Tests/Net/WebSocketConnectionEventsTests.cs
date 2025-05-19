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
    public class WebSocketConnectionEventsTests : WebSocketTestRunner
    {
        private WebSocketConnectionEvents _events;
        
        [SetUp]
        public override void Setup()
        {
            base.Setup();
            _events = new WebSocketConnectionEvents();
        }
        
        [Test]
        public void OnOpen_ShouldNotThrowWithNoSubscribers()
        {
            // Act & Assert - no exception
            _events.InvokeOnOpen();
        }
        
        [Test]
        public void OnClose_ShouldNotThrowWithNoSubscribers()
        {
            // Act & Assert - no exception
            _events.InvokeOnClose();
        }
        
        [Test]
        public void OnMessage_ShouldNotThrowWithNoSubscribers()
        {
            // Act & Assert - no exception
            _events.InvokeOnMessage(CreateTestMessage("test"));
        }
        
        [Test]
        public void OnError_ShouldNotThrowWithNoSubscribers()
        {
            // Act & Assert - no exception
            _events.InvokeOnError("Test error");
        }
        
        [Test]
        public void OnStatusChanged_ShouldNotThrowWithNoSubscribers()
        {
            // Act & Assert - no exception
            _events.InvokeOnStatusChanged(WebSocketConnectionStatus.Connected);
        }
        
        [Test]
        public void OnOpen_ShouldInvokeSubscribers()
        {
            // Arrange
            bool handlerCalled = false;
            _events.OnOpen += () => {
                handlerCalled = true;
            };
            
            // Act
            _events.InvokeOnOpen();
            
            // Assert
            Assert.IsTrue(handlerCalled, "OnOpen handler should be called");
        }
        
        [Test]
        public void OnClose_ShouldInvokeSubscribers()
        {
            // Arrange
            bool handlerCalled = false;
            _events.OnClose += () => {
                handlerCalled = true;
            };
            
            // Act
            _events.InvokeOnClose();
            
            // Assert
            Assert.IsTrue(handlerCalled, "OnClose handler should be called");
        }
        
        [Test]
        public void OnMessage_ShouldInvokeSubscribers()
        {
            // Arrange
            WebSocketMessage receivedMessage = null;
            _events.OnMessage += (msg) => {
                receivedMessage = msg;
            };
            
            var message = CreateTestMessage("test_message");
            
            // Act
            _events.InvokeOnMessage(message);
            
            // Assert
            Assert.IsNotNull(receivedMessage, "Message should be passed to handler");
            Assert.AreEqual("test_message", receivedMessage.type, "Message type should match");
        }
        
        [Test]
        public void OnError_ShouldInvokeSubscribers()
        {
            // Arrange
            string receivedError = null;
            _events.OnError += (error) => {
                receivedError = error;
            };
            
            // Act
            _events.InvokeOnError("Test error message");
            
            // Assert
            Assert.AreEqual("Test error message", receivedError, "Error message should be passed to handler");
        }
        
        [Test]
        public void OnStatusChanged_ShouldInvokeSubscribers()
        {
            // Arrange
            WebSocketConnectionStatus receivedStatus = WebSocketConnectionStatus.Disconnected;
            _events.OnStatusChanged += (status) => {
                receivedStatus = status;
            };
            
            // Act
            _events.InvokeOnStatusChanged(WebSocketConnectionStatus.Connected);
            
            // Assert
            Assert.AreEqual(WebSocketConnectionStatus.Connected, receivedStatus, "Status should be passed to handler");
        }
        
        [Test]
        public void MultipleSubscribers_ShouldAllBeInvoked()
        {
            // Arrange
            int handler1CallCount = 0;
            int handler2CallCount = 0;
            int handler3CallCount = 0;
            
            _events.OnOpen += () => { handler1CallCount++; };
            _events.OnOpen += () => { handler2CallCount++; };
            _events.OnOpen += () => { handler3CallCount++; };
            
            // Act
            _events.InvokeOnOpen();
            
            // Assert
            Assert.AreEqual(1, handler1CallCount, "First handler should be called once");
            Assert.AreEqual(1, handler2CallCount, "Second handler should be called once");
            Assert.AreEqual(1, handler3CallCount, "Third handler should be called once");
        }
        
        [Test]
        public void UnsubscribeHandler_ShouldPreventInvocation()
        {
            // Arrange
            int handlerCallCount = 0;
            Action handler = () => { handlerCallCount++; };
            
            _events.OnOpen += handler;
            
            // Verify handler works first
            _events.InvokeOnOpen();
            Assert.AreEqual(1, handlerCallCount, "Handler should be called initially");
            
            // Act - unsubscribe and invoke again
            _events.OnOpen -= handler;
            _events.InvokeOnOpen();
            
            // Assert
            Assert.AreEqual(1, handlerCallCount, "Handler should not be called after unsubscribing");
        }
        
        [Test]
        public void HandlerThrowsException_ShouldNotPreventOtherHandlers()
        {
            // Arrange
            bool firstHandlerCalled = false;
            bool secondHandlerCalled = false;
            bool errorLogged = false;
            
            // Mock Debug.LogError
            Debug.LogError = (message) => {
                if (message.ToString().Contains("Exception in event handler"))
                {
                    errorLogged = true;
                }
            };
            
            _events.OnOpen += () => {
                firstHandlerCalled = true;
                throw new Exception("Test exception");
            };
            
            _events.OnOpen += () => {
                secondHandlerCalled = true;
            };
            
            // Act - should not throw despite first handler throwing
            _events.InvokeOnOpen();
            
            // Assert
            Assert.IsTrue(firstHandlerCalled, "First handler should be called");
            Assert.IsTrue(secondHandlerCalled, "Second handler should still be called despite first handler exception");
            Assert.IsTrue(errorLogged, "Error should be logged when handler throws exception");
        }
        
        [Test]
        public void ClearAllEventHandlers_ShouldRemoveAllSubscribers()
        {
            // Arrange
            int openHandlerCalled = 0;
            int closeHandlerCalled = 0;
            int messageHandlerCalled = 0;
            int errorHandlerCalled = 0;
            int statusHandlerCalled = 0;
            
            _events.OnOpen += () => { openHandlerCalled++; };
            _events.OnClose += () => { closeHandlerCalled++; };
            _events.OnMessage += (msg) => { messageHandlerCalled++; };
            _events.OnError += (err) => { errorHandlerCalled++; };
            _events.OnStatusChanged += (status) => { statusHandlerCalled++; };
            
            // Act
            _events.ClearAllEventHandlers();
            
            // Invoke all events
            _events.InvokeOnOpen();
            _events.InvokeOnClose();
            _events.InvokeOnMessage(CreateTestMessage("test"));
            _events.InvokeOnError("test error");
            _events.InvokeOnStatusChanged(WebSocketConnectionStatus.Connected);
            
            // Assert
            Assert.AreEqual(0, openHandlerCalled, "Open handler should not be called after clearing");
            Assert.AreEqual(0, closeHandlerCalled, "Close handler should not be called after clearing");
            Assert.AreEqual(0, messageHandlerCalled, "Message handler should not be called after clearing");
            Assert.AreEqual(0, errorHandlerCalled, "Error handler should not be called after clearing");
            Assert.AreEqual(0, statusHandlerCalled, "Status handler should not be called after clearing");
        }
        
        [Test]
        public void InvokeOnStatusChanged_ShouldUpdateLastStatus()
        {
            // Arrange
            WebSocketConnectionStatus initialStatus = _events.LastStatus;
            Assert.AreEqual(WebSocketConnectionStatus.Disconnected, initialStatus, "Initial status should be Disconnected");
            
            // Act
            _events.InvokeOnStatusChanged(WebSocketConnectionStatus.Connecting);
            
            // Assert
            Assert.AreEqual(WebSocketConnectionStatus.Connecting, _events.LastStatus, "LastStatus should be updated");
            
            // Act again
            _events.InvokeOnStatusChanged(WebSocketConnectionStatus.Connected);
            
            // Assert again
            Assert.AreEqual(WebSocketConnectionStatus.Connected, _events.LastStatus, "LastStatus should be updated again");
        }
        
        [UnityTest]
        public IEnumerator DelayedEventHandling_ShouldWork()
        {
            // Arrange
            int handlerCallCount = 0;
            bool handlerCompleted = false;
            
            _events.OnMessage += async (msg) => {
                // Simulate async work in the handler
                handlerCallCount++;
                await System.Threading.Tasks.Task.Delay(100); // Wait 100ms
                handlerCompleted = true;
            };
            
            // Act
            _events.InvokeOnMessage(CreateTestMessage("test"));
            
            // Assert initial state
            Assert.AreEqual(1, handlerCallCount, "Handler should be called immediately");
            Assert.IsFalse(handlerCompleted, "Handler should not be completed yet");
            
            // Wait for handler to complete
            yield return new WaitForSeconds(0.2f);
            
            // Assert completion
            Assert.IsTrue(handlerCompleted, "Handler should be completed after waiting");
        }
    }
} 