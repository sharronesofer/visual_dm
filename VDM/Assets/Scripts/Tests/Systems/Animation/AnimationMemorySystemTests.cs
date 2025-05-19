using NUnit.Framework;
using VDM.Systems;

namespace VDM.Tests.Systems.Animation
{
    [TestFixture]
    public class AnimationMemorySystemTests
    {
        [Test]
        public void Constructor_InitializesCorrectly()
        {
            var system = new AnimationMemorySystem();
            Assert.IsNotNull(system);
        }

        [Test]
        public void AllocateAndFreeMemory_TracksUsage()
        {
            var system = new AnimationMemorySystem();
            var block = system.Allocate(256);
            Assert.IsNotNull(block);
            Assert.AreEqual(256, block.Size);
            system.Free(block);
            Assert.IsTrue(block.IsFreed);
        }

        [Test]
        public void GetTotalAllocatedMemory_ReflectsAllocations()
        {
            var system = new AnimationMemorySystem();
            system.Allocate(100);
            system.Allocate(200);
            Assert.AreEqual(300, system.GetTotalAllocatedMemory());
        }

        [Test]
        public void Allocate_NegativeSize_Throws()
        {
            var system = new AnimationMemorySystem();
            Assert.Throws<System.ArgumentOutOfRangeException>(() => system.Allocate(-1));
        }
    }
} 