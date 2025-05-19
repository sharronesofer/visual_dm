using NUnit.Framework;
using System.Threading;

namespace VisualDM.Tests
{
    public class AnimationMetricsTests
    {
        [Test]
        public void AnimationMetrics_RecordsAndCalculatesCorrectly()
        {
            AnimationMetrics.RecordTaskExecution(10000);
            AnimationMetrics.RecordTaskExecution(20000);
            Assert.Greater(AnimationMetrics.AverageTaskMs, 0);
            AnimationMetrics.RecordThreadActive(Thread.CurrentThread.ManagedThreadId, 5000);
            Assert.GreaterOrEqual(AnimationMetrics.ThreadUtilizationPercent, 0);
        }
    }
} 