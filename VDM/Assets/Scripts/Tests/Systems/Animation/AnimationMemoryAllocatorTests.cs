using NUnit.Framework;
using VDM.Systems;

namespace VDM.Tests.Systems.Animation
{
    [TestFixture]
    public class AnimationMemoryAllocatorTests
    {
        [Test]
        public void Constructor_InitializesCorrectly()
        {
            var allocator = new AnimationMemoryAllocator();
            Assert.IsNotNull(allocator);
        }

        [Test]
        public void AllocateMemory_AllocatesSuccessfully()
        {
            var allocator = new AnimationMemoryAllocator();
            var block = allocator.AllocateMemory(128);
            Assert.IsNotNull(block);
            Assert.AreEqual(128, block.Size);
        }

        [Test]
        public void FreeMemory_FreesSuccessfully()
        {
            var allocator = new AnimationMemoryAllocator();
            var block = allocator.AllocateMemory(64);
            allocator.FreeMemory(block);
            Assert.IsTrue(block.IsFreed);
        }

        [Test]
        public void AllocateMemory_NegativeSize_Throws()
        {
            var allocator = new AnimationMemoryAllocator();
            Assert.Throws<System.ArgumentOutOfRangeException>(() => allocator.AllocateMemory(-1));
        }
    }
} 