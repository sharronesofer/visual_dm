using NUnit.Framework;
using VisualDM.Core;
using UnityEngine;
using System;
using VisualDM.Systems.Metrics;
using System.Threading.Tasks;
using System.Threading;
using System.Collections.Generic;

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

    [TestFixture]
    public class MetricsCollectorTests
    {
        [Test]
        public void ActiveInteractions_IncrementDecrement_Works()
        {
            var mc = new MetricsCollector();
            mc.IncrementActiveInteractions("id1", "active");
            Assert.AreEqual(1, mc.GetActiveInteractions());
            mc.DecrementActiveInteractions("id1");
            Assert.AreEqual(0, mc.GetActiveInteractions());
        }

        [Test]
        public void ResponseTime_RecordingAndStats_AreAccurate()
        {
            var mc = new MetricsCollector();
            mc.RecordResponseTime(100);
            mc.RecordResponseTime(200);
            mc.RecordResponseTime(300);
            var stats = mc.GetResponseTimeStats();
            Assert.AreEqual(100, stats.min);
            Assert.AreEqual(300, stats.max);
            Assert.AreEqual(200, stats.avg);
        }

        [Test]
        public void MemoryCpuBandwidthError_Metrics_AreSetAndGet()
        {
            var mc = new MetricsCollector();
            mc.SetMemoryUsage(123.4, new Dictionary<string, double> { { "id1", 12.3 } });
            Assert.AreEqual(123.4, mc.GetMemoryTotalMb());
            Assert.AreEqual(12.3, mc.GetMemoryPerInteraction()["id1"]);
            mc.SetCpuUsage(55.5, new Dictionary<string, double> { { "id1", 33.3 } });
            Assert.AreEqual(55.5, mc.GetCpuTotalPercent());
            Assert.AreEqual(33.3, mc.GetCpuPerThread()["id1"]);
            mc.SetBandwidth(42.0);
            Assert.AreEqual(42.0, mc.GetBandwidthKbps());
            mc.RecordError("Timeout", "Critical");
            Assert.AreEqual(1, mc.GetErrorTypeCounts()["Timeout:Critical"]);
            mc.SetErrorRate(0.05);
            Assert.AreEqual(0.05, mc.GetErrorRate());
        }

        [Test]
        public void ThreadSafety_MetricsCollector_IsThreadSafe()
        {
            var mc = new MetricsCollector();
            int threads = 10;
            int increments = 1000;
            var tasks = new List<Task>();
            for (int t = 0; t < threads; t++)
            {
                tasks.Add(Task.Run(() =>
                {
                    for (int i = 0; i < increments; i++)
                        mc.IncrementActiveInteractions(Guid.NewGuid().ToString(), "active");
                }));
            }
            Task.WaitAll(tasks.ToArray());
            Assert.AreEqual(threads * increments, mc.GetActiveInteractions());
        }
    }

    [TestFixture]
    public class InteractionMetricsCollectorIntegrationTests
    {
        [Test]
        public void SimulatedInteraction_RecordsMetrics()
        {
            var mc = new MetricsCollector();
            var collector = new GameObject().AddComponent<InteractionMetricsCollector>();
            collector.Initialize(mc);
            var id = collector.OnInteractionStart();
            Thread.Sleep(10); // Simulate some work
            collector.OnInteractionEnd(id);
            var stats = mc.GetResponseTimeStats();
            Assert.Greater(stats.max, 0);
            collector.RecordMemoryUsage(id.ToString(), 10.0);
            collector.RecordCpuUsage(id.ToString(), 5.0);
            collector.RecordBandwidth(1.0);
            collector.RecordError("Timeout", "Critical");
            collector.UpdateErrorRate();
            Assert.AreEqual(10.0, mc.GetMemoryPerInteraction()[id.ToString()]);
            Assert.AreEqual(5.0, mc.GetCpuPerThread()[id.ToString()]);
            Assert.AreEqual(1.0, mc.GetBandwidthKbps());
        }
    }
} 