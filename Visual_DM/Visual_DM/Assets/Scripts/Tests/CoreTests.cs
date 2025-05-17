using NUnit.Framework;
using VisualDM.Core;
using UnityEngine;
using System;

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

        [Test]
        public void FixedPoint_Arithmetic_WorksCorrectly()
        {
            var a = FixedPoint.FromFloat(1.5f);
            var b = FixedPoint.FromFloat(2.25f);
            Assert.AreEqual(3.75f, (a + b).ToFloat(), 1e-4);
            Assert.AreEqual(-0.75f, (a - b).ToFloat(), 1e-4);
            Assert.AreEqual(3.375f, (a * b).ToFloat(), 1e-4);
            Assert.AreEqual(0.6666f, (a / b).ToFloat(), 1e-3);
        }

        [Test]
        public void FixedPoint_Conversion_IntFloat()
        {
            var fp = FixedPoint.FromInt(42);
            Assert.AreEqual(42, fp.ToInt());
            Assert.AreEqual(42f, fp.ToFloat(), 1e-4);
            var fp2 = FixedPoint.FromFloat(3.14159f);
            Assert.AreEqual(3, fp2.ToInt());
            Assert.AreEqual(3.14159f, fp2.ToFloat(), 1e-4);
        }

        [Test]
        public void PrecisionCoordinate_Normalization_WrapsCorrectly()
        {
            var coord = PrecisionCoordinate.FromInt(105, -7);
            var norm = coord.Normalize(100, 10);
            Assert.AreEqual((5, 3), norm.ToInt());
        }

        [Test]
        public void PrecisionCoordinate_PrecisionLossDetection_Works()
        {
            var coord = new PrecisionCoordinate(FixedPoint.FromFloat(1.00001f), FixedPoint.FromFloat(2.99999f));
            Assert.IsTrue(coord.HasPrecisionLoss(1e-5f));
            var coord2 = new PrecisionCoordinate(FixedPoint.FromInt(1), FixedPoint.FromInt(3));
            Assert.IsFalse(coord2.HasPrecisionLoss(1e-5f));
        }
    }
} 