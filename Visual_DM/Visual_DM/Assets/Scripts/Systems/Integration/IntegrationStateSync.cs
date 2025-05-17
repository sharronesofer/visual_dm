using System;
using System.Collections.Generic;
using System.Threading;

namespace Systems.Integration
{
    public interface IStateSyncObserver<T>
    {
        void OnStateChanged(T newState, T oldState);
    }

    public class StateSyncManager<T>
    {
        private T _currentState;
        private readonly List<IStateSyncObserver<T>> _observers = new List<IStateSyncObserver<T>>();
        private readonly Stack<T> _snapshots = new Stack<T>();
        private readonly ReaderWriterLockSlim _lock = new ReaderWriterLockSlim();

        // Conflict resolver: (current, incoming) => resolved
        public Func<T, T, T> ConflictResolver { get; set; }
        // Validation hooks
        public Func<T, bool> PreValidation { get; set; }
        public Func<T, bool> PostValidation { get; set; }

        public void RegisterObserver(IStateSyncObserver<T> observer)
        {
            if (!_observers.Contains(observer))
                _observers.Add(observer);
        }

        public void UnregisterObserver(IStateSyncObserver<T> observer)
        {
            _observers.Remove(observer);
        }

        public void SetState(T newState)
        {
            _lock.EnterWriteLock();
            try
            {
                if (PreValidation != null && !PreValidation(newState))
                    throw new InvalidOperationException("Pre-validation failed for new state.");
                var oldState = _currentState;
                _snapshots.Push(oldState);
                if (ConflictResolver != null)
                    _currentState = ConflictResolver(_currentState, newState);
                else
                    _currentState = newState;
                if (PostValidation != null && !PostValidation(_currentState))
                {
                    Rollback();
                    throw new InvalidOperationException("Post-validation failed for new state.");
                }
                foreach (var observer in _observers)
                    observer.OnStateChanged(_currentState, oldState);
            }
            finally
            {
                _lock.ExitWriteLock();
            }
        }

        public T GetState()
        {
            _lock.EnterReadLock();
            try { return _currentState; }
            finally { _lock.ExitReadLock(); }
        }

        public void Rollback()
        {
            _lock.EnterWriteLock();
            try
            {
                if (_snapshots.Count > 0)
                {
                    var prevState = _snapshots.Pop();
                    _currentState = prevState;
                }
            }
            finally
            {
                _lock.ExitWriteLock();
            }
        }

        // Example delta update (assumes T is a class with a MergeDelta method)
        public void ApplyDelta(Func<T, T, T> deltaFunc, T delta)
        {
            _lock.EnterWriteLock();
            try
            {
                _currentState = deltaFunc(_currentState, delta);
                foreach (var observer in _observers)
                    observer.OnStateChanged(_currentState, _currentState); // Could pass old state if needed
            }
            finally
            {
                _lock.ExitWriteLock();
            }
        }
    }
} 