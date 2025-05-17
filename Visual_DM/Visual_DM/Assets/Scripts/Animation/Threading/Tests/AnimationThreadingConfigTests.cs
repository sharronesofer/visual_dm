using NUnit.Framework;

namespace Visual_DM.Animation.Threading.Tests
{
    public class AnimationThreadingConfigTests
    {
        [Test]
        public void AnimationThreadingConfig_AdjustsThreadCount()
        {
            var config = new AnimationThreadingConfig();
            int original = config.WorkerThreads;
            config.AdjustThreadCount(4);
            Assert.AreEqual(4, config.WorkerThreads);
            config.AdjustThreadCount(0);
            Assert.AreEqual(1, config.WorkerThreads); // Minimum 1
        }

        [Test]
        public void AnimationThreadingConfig_TogglesLogging()
        {
            var config = new AnimationThreadingConfig();
            config.EnableLogging = true;
            Assert.IsTrue(config.EnableLogging);
            config.EnableLogging = false;
            Assert.IsFalse(config.EnableLogging);
        }
    }
} 