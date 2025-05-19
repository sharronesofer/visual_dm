using NUnit.Framework;
using VDM.Systems;

namespace VDM.Tests.Systems.Animation
{
    [TestFixture]
    public class AnimationTimelineTests
    {
        [Test]
        public void Constructor_InitializesCorrectly()
        {
            var timeline = new AnimationTimeline();
            Assert.IsNotNull(timeline);
        }

        [Test]
        public void AddKeyframe_AddsKeyframeSuccessfully()
        {
            var timeline = new AnimationTimeline();
            timeline.AddKeyframe(0.0f, "Idle");
            Assert.AreEqual("Idle", timeline.GetKeyframe(0.0f));
        }

        [Test]
        public void GetKeyframe_UnknownTime_ReturnsNull()
        {
            var timeline = new AnimationTimeline();
            Assert.IsNull(timeline.GetKeyframe(1.0f));
        }

        [Test]
        public void RemoveKeyframe_RemovesKeyframe()
        {
            var timeline = new AnimationTimeline();
            timeline.AddKeyframe(0.0f, "Idle");
            timeline.RemoveKeyframe(0.0f);
            Assert.IsNull(timeline.GetKeyframe(0.0f));
        }
    }
} 