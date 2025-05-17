using System;
using System.Collections;
using System.Threading.Tasks;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.TestTools;
using VisualDM.Core;

namespace VisualDM.Tests.Core
{
    public class EventBusTests
    {
        private EventBus eventBus;

        [SetUp]
        public void Setup()
        {
            eventBus = new EventBus();
        }

        [Test]
        public void Subscribe_And_Publish_DeliveredToHandler()
        {
            // Arrange
            bool eventReceived = false;
            string testMessage = "Hello World";
            
            // Act
            eventBus.Subscribe<string>(message => 
            {
                Assert.AreEqual(testMessage, message);
                eventReceived = true;
            });
            
            eventBus.Publish(testMessage);
            
            // Assert
            Assert.IsTrue(eventReceived);
        }
        
        [Test]
        public void Unsubscribe_Handler_NotCalled()
        {
            // Arrange
            bool eventReceived = false;
            Action<string> handler = _ => eventReceived = true;
            
            // Act
            eventBus.Subscribe(handler);
            eventBus.Unsubscribe(handler);
            eventBus.Publish("Test");
            
            // Assert
            Assert.IsFalse(eventReceived);
        }
        
        [Test]
        public void Prioritized_Handlers_CalledInOrder()
        {
            // Arrange
            int order = 0;
            int highPriorityOrder = -1;
            int normalPriorityOrder = -1;
            int lowPriorityOrder = -1;
            
            // Act
            eventBus.Subscribe<string>(_ => 
            {
                normalPriorityOrder = order++;
            }, EventPriority.Normal);
            
            eventBus.Subscribe<string>(_ => 
            {
                lowPriorityOrder = order++;
            }, EventPriority.Low);
            
            eventBus.Subscribe<string>(_ => 
            {
                highPriorityOrder = order++;
            }, EventPriority.High);
            
            eventBus.Publish("Test");
            
            // Assert
            Assert.AreEqual(0, highPriorityOrder);
            Assert.AreEqual(1, normalPriorityOrder);
            Assert.AreEqual(2, lowPriorityOrder);
        }
        
        [UnityTest]
        public IEnumerator AsyncHandler_CompletesProperly()
        {
            // Arrange
            bool eventReceived = false;
            
            // Act
            eventBus.SubscribeAsync<string>(async message => 
            {
                await Task.Delay(50); // Simulate async work
                eventReceived = true;
            });
            
            eventBus.Publish("Test");
            
            // Wait for the async handler to complete
            yield return new WaitForSeconds(0.1f);
            
            // Assert
            Assert.IsTrue(eventReceived);
        }
        
        [Test]
        public void Publish_WithoutSubscribers_DoesNotThrow()
        {
            // Act & Assert - should not throw
            Assert.DoesNotThrow(() => eventBus.Publish("Test"));
        }
        
        [Test]
        public void HandlerThrowsException_OtherHandlersStillCalled()
        {
            // Arrange
            bool firstHandlerCalled = false;
            bool secondHandlerCalled = false;
            
            // Act
            eventBus.Subscribe<string>(_ => 
            {
                firstHandlerCalled = true;
                throw new Exception("Test exception");
            });
            
            eventBus.Subscribe<string>(_ => 
            {
                secondHandlerCalled = true;
            });
            
            eventBus.Publish("Test");
            
            // Assert - second handler should still be called
            Assert.IsTrue(firstHandlerCalled);
            Assert.IsTrue(secondHandlerCalled);
        }
        
        [Test]
        public void SubscribeToBaseType_ReceivesSubtypeEvents()
        {
            // Arrange
            bool handlerCalled = false;
            
            // Act
            eventBus.Subscribe<object>(_ => handlerCalled = true);
            eventBus.Publish("This is a string but should be received by object handler");
            
            // Assert
            Assert.IsTrue(handlerCalled);
        }
        
        [Test]
        public void EventFilterWorks()
        {
            // Arrange
            int callCount = 0;
            
            // Act - handler with filter that only accepts strings starting with "Accept"
            eventBus.Subscribe<string>(
                str => callCount++,
                filter: str => str.StartsWith("Accept")
            );
            
            eventBus.Publish("Accept this message");  // Should be received
            eventBus.Publish("Reject this message");  // Should be filtered out
            
            // Assert
            Assert.AreEqual(1, callCount);
        }
    }
} 