using NUnit.Framework;
using System.Threading;

namespace Visual_DM.Animation.Threading.Tests
{
    public class ThreadPoolManagerTests
    {
        [Test]
        public void ThreadPool_CreatesAndDisposesWithoutError()
        {
            using (var pool = new ThreadPoolManager(2))
            {
                Assert.Pass();
            }
        }

        [Test]
        public void ThreadPool_ExecutesTask()
        {
            using (var pool = new ThreadPoolManager(2))
            {
                bool executed = false;
                var task = new TestTask(() => executed = true);
                pool.Enqueue(task);
                Thread.Sleep(50); // Allow time for execution
                Assert.IsTrue(executed);
            }
        }

        private class TestTask : AnimationTask
        {
            private readonly System.Action _action;
            public TestTask(System.Action action) { _action = action; }
            public override void Execute() { _action(); IsCompleted = true; }
        }
    }
} 