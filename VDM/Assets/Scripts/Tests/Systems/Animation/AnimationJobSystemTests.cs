using NUnit.Framework;
using VDM.Systems;

namespace VDM.Tests.Systems.Animation
{
    [TestFixture]
    public class AnimationJobSystemTests
    {
        [Test]
        public void Constructor_InitializesCorrectly()
        {
            var jobSystem = new AnimationJobSystem();
            Assert.IsNotNull(jobSystem);
        }

        [Test]
        public void ScheduleJob_AddsJobToQueue()
        {
            var jobSystem = new AnimationJobSystem();
            bool executed = false;
            jobSystem.ScheduleJob(() => executed = true);
            jobSystem.ExecuteAllJobs();
            Assert.IsTrue(executed);
        }

        [Test]
        public void ExecuteAllJobs_EmptiesQueue()
        {
            var jobSystem = new AnimationJobSystem();
            jobSystem.ScheduleJob(() => { });
            jobSystem.ExecuteAllJobs();
            Assert.AreEqual(0, jobSystem.PendingJobCount);
        }

        [Test]
        public void ScheduleJob_NullAction_Throws()
        {
            var jobSystem = new AnimationJobSystem();
            Assert.Throws<System.ArgumentNullException>(() => jobSystem.ScheduleJob(null));
        }
    }
} 