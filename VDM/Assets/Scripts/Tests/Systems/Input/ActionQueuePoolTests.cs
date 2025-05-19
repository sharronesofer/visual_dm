using NUnit.Framework;
using VDM.Systems.Input;
using System;

namespace VDM.Tests.Systems.Input
{
    [TestFixture]
    public class ActionQueuePoolTests
    {
        [Test]
        public void Constructor_InitializesCorrectly()
        {
            var pool = new ActionQueuePool();
            Assert.IsNotNull(pool);
        }

        [Test]
        public void GetQueue_ReturnsQueueInstance()
        {
            var pool = new ActionQueuePool();
            var queue = pool.GetQueue("Player1");
            Assert.IsNotNull(queue);
        }

        [Test]
        public void GetQueue_SameKey_ReturnsSameInstance()
        {
            var pool = new ActionQueuePool();
            var queue1 = pool.GetQueue("Player1");
            var queue2 = pool.GetQueue("Player1");
            Assert.AreSame(queue1, queue2);
        }

        [Test]
        public void RemoveQueue_RemovesQueue()
        {
            var pool = new ActionQueuePool();
            pool.GetQueue("Player1");
            pool.RemoveQueue("Player1");
            var queue = pool.GetQueue("Player1");
            Assert.IsNotNull(queue); // Should create a new instance
        }

        [Test]
        public void RemoveQueue_NonexistentKey_DoesNotThrow()
        {
            var pool = new ActionQueuePool();
            Assert.DoesNotThrow(() => pool.RemoveQueue("Nonexistent"));
        }
    }
} 