using System;
using System.Threading.Tasks;
using NUnit.Framework;

namespace Systems.Integration.Tests
{
    public class StateSyncManagerTests
    {
        private StateSyncManager<int> _manager;
        private int _observerCount;
        private int _lastOldState;

        [SetUp]
        public void SetUp()
        {
            _manager = new StateSyncManager<int>();
            _observerCount = 0;
            _lastOldState = -1;
        }

        [Test]
        public void TestObserverNotification()
        {
            _manager.RegisterObserver(new IntObserver(this));
            _manager.SetState(5);
            Assert.AreEqual(1, _observerCount);
            Assert.AreEqual(0, _lastOldState);
        }

        [Test]
        public void TestConflictResolution()
        {
            _manager.ConflictResolver = (current, incoming) => Math.Max(current, incoming);
            _manager.SetState(3);
            _manager.SetState(7);
            _manager.SetState(5); // Should keep 7
            Assert.AreEqual(7, _manager.GetState());
        }

        [Test]
        public void TestValidationHooks()
        {
            _manager.PreValidation = s => s >= 0;
            _manager.PostValidation = s => s < 10;
            _manager.SetState(5);
            Assert.Throws<InvalidOperationException>(() => _manager.SetState(-1)); // Pre-validation fail
            Assert.Throws<InvalidOperationException>(() => _manager.SetState(15)); // Post-validation fail
        }

        [Test]
        public void TestRollback()
        {
            _manager.SetState(1);
            _manager.SetState(2);
            _manager.Rollback();
            Assert.AreEqual(1, _manager.GetState());
        }

        [Test]
        public void TestConcurrentModifications()
        {
            _manager.SetState(0);
            _manager.ConflictResolver = (current, incoming) => current + incoming;
            Parallel.For(0, 100, i => _manager.SetState(1));
            Assert.AreEqual(100, _manager.GetState());
        }

        private class IntObserver : IStateSyncObserver<int>
        {
            private readonly StateSyncManagerTests _parent;
            public IntObserver(StateSyncManagerTests parent) { _parent = parent; }
            public void OnStateChanged(int newState, int oldState)
            {
                _parent._observerCount++;
                _parent._lastOldState = oldState;
            }
        }
    }
} 