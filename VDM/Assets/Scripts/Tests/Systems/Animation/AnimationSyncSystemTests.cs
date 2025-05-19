using NUnit.Framework;
using VDM.Systems;

namespace VDM.Tests.Systems.Animation
{
    [TestFixture]
    public class AnimationSyncSystemTests
    {
        [Test]
        public void Constructor_InitializesCorrectly()
        {
            var syncSystem = new AnimationSyncSystem();
            Assert.IsNotNull(syncSystem);
        }

        [Test]
        public void SyncAnimation_SynchronizesSuccessfully()
        {
            var syncSystem = new AnimationSyncSystem();
            bool synced = syncSystem.SyncAnimation("Walk", 0.5f);
            Assert.IsTrue(synced);
        }

        [Test]
        public void SyncAnimation_InvalidName_ReturnsFalse()
        {
            var syncSystem = new AnimationSyncSystem();
            bool synced = syncSystem.SyncAnimation(null, 0.5f);
            Assert.IsFalse(synced);
        }
    }
} 