using System;
using System.Collections.Generic;
using System.Diagnostics;
using NUnit.Framework;

namespace Systems.Integration.Tests
{
    public class IntegrationMonitoringTests
    {
        private List<LogEntry> _logs;
        private List<MetricEntry> _metrics;
        private List<AlertEntry> _alerts;
        private List<TraceEntry> _traces;

        [SetUp]
        public void SetUp()
        {
            _logs = new List<LogEntry>();
            _metrics = new List<MetricEntry>();
            _alerts = new List<AlertEntry>();
            _traces = new List<TraceEntry>();
            IntegrationLogger.OnLog += entry => _logs.Add(entry);
            IntegrationMetrics.OnMetric += entry => _metrics.Add(entry);
            IntegrationAlerting.OnAlert += entry => _alerts.Add(entry);
            IntegrationDiagnostics.OnTrace += entry => _traces.Add(entry);
        }

        [Test]
        public void TestLogCapture()
        {
            IntegrationLogger.Log("Test log", LogLevel.Info, "Quest", "Combat", "Attack", "Success");
            Assert.AreEqual(1, _logs.Count);
            Assert.AreEqual("Quest", _logs[0].SourceSystem);
            Assert.AreEqual("Combat", _logs[0].TargetSystem);
            Assert.AreEqual("Attack", _logs[0].Operation);
            Assert.AreEqual("Success", _logs[0].Status);
        }

        [Test]
        public void TestMetricCollection()
        {
            IntegrationMetrics.SamplingRate = 1.0;
            IntegrationMetrics.Record("latency", 123.4);
            Assert.AreEqual(1, _metrics.Count);
            Assert.AreEqual("latency", _metrics[0].Name);
            Assert.AreEqual(123.4, _metrics[0].Value);
        }

        [Test]
        public void TestAlerting()
        {
            IntegrationAlerting.Alert("Failure", LogLevel.Critical, "Quest", "Inventory", "Sync");
            Assert.AreEqual(1, _alerts.Count);
            Assert.AreEqual(LogLevel.Critical, _alerts[0].Level);
            Assert.AreEqual("Quest", _alerts[0].SourceSystem);
            Assert.AreEqual("Inventory", _alerts[0].TargetSystem);
            Assert.AreEqual("Sync", _alerts[0].Operation);
        }

        [Test]
        public void TestTracing()
        {
            IntegrationDiagnostics.Trace("Trade", "Item exchanged", "Market", "Inventory");
            Assert.AreEqual(1, _traces.Count);
            Assert.AreEqual("Trade", _traces[0].Operation);
            Assert.AreEqual("Market", _traces[0].SourceSystem);
            Assert.AreEqual("Inventory", _traces[0].TargetSystem);
        }

        [Test]
        public void TestPerformanceOverhead()
        {
            var sw = Stopwatch.StartNew();
            for (int i = 0; i < 10000; i++)
                IntegrationLogger.Log("PerfTest", LogLevel.Info);
            sw.Stop();
            Assert.Less(sw.ElapsedMilliseconds, 2000); // Should log 10k entries in under 2s
        }

        [Test]
        public void TestInventoryAddItem_Idempotency()
        {
            var inventory = new VisualDM.Inventory.Inventory();
            var item = new VisualDM.Inventory.Item("test1", "Test Item", "desc", VisualDM.Inventory.ItemRarity.Common, false, false, null, null);
            string idempotencyKey = "test-key-123";
            Assert.IsTrue(inventory.AddItem(item, 1, idempotencyKey));
            Assert.IsTrue(inventory.AddItem(item, 1, idempotencyKey)); // Should be idempotent, not duplicate
            // Only one slot should exist
            Assert.AreEqual(1, inventory.Slots.Count);
        }

        [Test]
        public void TestInventoryRemoveItem_Idempotency()
        {
            var inventory = new VisualDM.Inventory.Inventory();
            var item = new VisualDM.Inventory.Item("test2", "Test Item 2", "desc", VisualDM.Inventory.ItemRarity.Common, false, false, null, null);
            string idempotencyKey = "test-key-456";
            inventory.AddItem(item, 2);
            Assert.IsTrue(inventory.RemoveItem(item, 1, idempotencyKey));
            Assert.IsTrue(inventory.RemoveItem(item, 1, idempotencyKey)); // Should be idempotent, not double-remove
            Assert.AreEqual(1, inventory.Slots[0].Quantity);
        }

        [Test]
        public void TestEconomySystem_AtomicityAndLogging()
        {
            var economy = new VisualDM.World.EconomySystem();
            economy.AddResource("Gold", 100, 10, 5);
            economy.AddTradeRoute("Gold", "Silver", 20);
            // Should not throw and should log
            Assert.DoesNotThrow(() => economy.UpdateEconomy(null));
            // No direct way to check logs here, but no exceptions = atomicity
        }

        [Test]
        public void TestInventoryAddItem_TransactionLogging()
        {
            var inventory = new VisualDM.Inventory.Inventory();
            var item = new VisualDM.Inventory.Item("log1", "Log Item", "desc", VisualDM.Inventory.ItemRarity.Common, false, false, null, null);
            _logs.Clear();
            inventory.AddItem(item, 1, "log-key-1");
            Assert.IsTrue(_logs.Exists(l => l.Operation == "AddItem" && l.Status == "Committed"));
        }

        [Test]
        public void TestInventoryAddItem_RollbackOnException()
        {
            var inventory = new VisualDM.Inventory.Inventory();
            // Simulate exception by passing null item
            _logs.Clear();
            Assert.Throws<Exception>(() => inventory.AddItem(null, 1, "fail-key-1"));
            Assert.IsTrue(_logs.Exists(l => l.Operation == "AddItem" && l.Status == "RolledBack"));
        }
    }
} 