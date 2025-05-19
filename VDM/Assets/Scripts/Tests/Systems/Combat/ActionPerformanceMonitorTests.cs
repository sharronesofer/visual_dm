using NUnit.Framework;
using VDM.Systems.Combat;

namespace VDM.Tests.Systems.Combat
{
    [TestFixture]
    public class ActionPerformanceMonitorTests
    {
        [Test]
        public void Constructor_InitializesCorrectly()
        {
            var monitor = new ActionPerformanceMonitor();
            Assert.IsNotNull(monitor);
        }

        [Test]
        public void RecordAction_PerformanceDataIsTracked()
        {
            var monitor = new ActionPerformanceMonitor();
            monitor.RecordAction("Attack", 0.25f);
            var stats = monitor.GetActionStats("Attack");
            Assert.IsNotNull(stats);
            Assert.AreEqual(1, stats.Count);
            Assert.AreEqual(0.25f, stats.TotalTime, 1e-4);
        }

        [Test]
        public void RecordAction_MultipleActions_AggregatesCorrectly()
        {
            var monitor = new ActionPerformanceMonitor();
            monitor.RecordAction("Attack", 0.2f);
            monitor.RecordAction("Attack", 0.3f);
            var stats = monitor.GetActionStats("Attack");
            Assert.AreEqual(2, stats.Count);
            Assert.AreEqual(0.5f, stats.TotalTime, 1e-4);
            Assert.AreEqual(0.25f, stats.AverageTime, 1e-4);
        }

        [Test]
        public void GetActionStats_UnknownAction_ReturnsDefault()
        {
            var monitor = new ActionPerformanceMonitor();
            var stats = monitor.GetActionStats("Nonexistent");
            Assert.IsNotNull(stats);
            Assert.AreEqual(0, stats.Count);
            Assert.AreEqual(0f, stats.TotalTime, 1e-4);
        }

        [Test]
        public void Reset_ClearsAllStats()
        {
            var monitor = new ActionPerformanceMonitor();
            monitor.RecordAction("Attack", 0.2f);
            monitor.Reset();
            var stats = monitor.GetActionStats("Attack");
            Assert.AreEqual(0, stats.Count);
        }

        [Test]
        public void RecordAction_NegativeTime_Throws()
        {
            var monitor = new ActionPerformanceMonitor();
            Assert.Throws<System.ArgumentOutOfRangeException>(() => monitor.RecordAction("Attack", -1f));
        }
    }
} 