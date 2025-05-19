using NUnit.Framework;
using VDM.Systems;

namespace VDM.Tests.Systems.Animation
{
    [TestFixture]
    public class AnimationBlendManagerTests
    {
        [Test]
        public void Constructor_InitializesCorrectly()
        {
            var manager = new AnimationBlendManager();
            Assert.IsNotNull(manager);
        }

        [Test]
        public void AddBlend_AddsBlendSuccessfully()
        {
            var manager = new AnimationBlendManager();
            manager.AddBlend("Walk", 0.5f);
            Assert.AreEqual(0.5f, manager.GetBlend("Walk"), 1e-4);
        }

        [Test]
        public void GetBlend_UnknownKey_ReturnsDefault()
        {
            var manager = new AnimationBlendManager();
            Assert.AreEqual(0f, manager.GetBlend("Unknown"), 1e-4);
        }

        [Test]
        public void RemoveBlend_RemovesBlend()
        {
            var manager = new AnimationBlendManager();
            manager.AddBlend("Run", 1.0f);
            manager.RemoveBlend("Run");
            Assert.AreEqual(0f, manager.GetBlend("Run"), 1e-4);
        }

        [Test]
        public void AddBlend_NegativeValue_Throws()
        {
            var manager = new AnimationBlendManager();
            Assert.Throws<System.ArgumentOutOfRangeException>(() => manager.AddBlend("Jump", -1f));
        }
    }
} 