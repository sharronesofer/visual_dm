using NUnit.Framework;
using VisualDM.Core;
using UnityEngine;

namespace VisualDM.Tests
{
    [TestFixture]
    public class CoreTests
    {
        [Test]
        public void StateManager_SetAndGet_ReturnsCorrectValue()
        {
            StateManager.Instance.Set("test_key", 42);
            Assert.AreEqual(42, StateManager.Instance.Get<int>("test_key"));
        }

        [Test]
        public void StateManager_HasAndRemove_WorksCorrectly()
        {
            StateManager.Instance.Set("remove_key", "value");
            Assert.IsTrue(StateManager.Instance.Has("remove_key"));
            StateManager.Instance.Remove("remove_key");
            Assert.IsFalse(StateManager.Instance.Has("remove_key"));
        }

        [Test]
        public void IdGenerator_GeneratesUniqueIds()
        {
            var id1 = IdGenerator.GenerateId();
            var id2 = IdGenerator.GenerateId();
            Assert.AreNotEqual(id1, id2);
        }

        [Test]
        public void EventBus_SubscribeAndPublish_InvokesHandler()
        {
            bool called = false;
            EventBus.Subscribe("test_event", (args) => { called = true; });
            EventBus.Publish("test_event");
            Assert.IsTrue(called);
            EventBus.UnsubscribeAll();
        }
    }
} 