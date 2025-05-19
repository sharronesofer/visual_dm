using NUnit.Framework;
using VDM.Core;
using System;

namespace VDM.Tests.Core
{
    [TestFixture]
    public class ActionQueueTests
    {
        [Test]
        public void Constructor_InitializesCorrectly()
        {
            var queue = new ActionQueue();
            Assert.IsNotNull(queue);
        }

        [Test]
        public void Enqueue_AddsItemToQueue()
        {
            var queue = new ActionQueue();
            queue.Enqueue("TestAction");
            Assert.AreEqual(1, queue.Count);
        }

        [Test]
        public void Dequeue_RemovesAndReturnsItem()
        {
            var queue = new ActionQueue();
            queue.Enqueue("Action1");
            var item = queue.Dequeue();
            Assert.AreEqual("Action1", item);
            Assert.AreEqual(0, queue.Count);
        }

        [Test]
        public void Dequeue_EmptyQueue_Throws()
        {
            var queue = new ActionQueue();
            Assert.Throws<InvalidOperationException>(() => queue.Dequeue());
        }

        [Test]
        public void Peek_ReturnsFirstItemWithoutRemoving()
        {
            var queue = new ActionQueue();
            queue.Enqueue("Action1");
            var item = queue.Peek();
            Assert.AreEqual("Action1", item);
            Assert.AreEqual(1, queue.Count);
        }

        [Test]
        public void Clear_EmptiesQueue()
        {
            var queue = new ActionQueue();
            queue.Enqueue("Action1");
            queue.Clear();
            Assert.AreEqual(0, queue.Count);
        }
    }
} 