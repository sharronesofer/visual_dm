using System;
using System.Collections.Generic;
using System.Threading;

namespace VisualDM.World
{
    // Represents a transaction for world state changes
    public class WorldStateTransaction
    {
        private readonly List<Action> _commitActions = new List<Action>();
        private readonly List<Action> _rollbackActions = new List<Action>();
        private bool _committed = false;
        private bool _rolledBack = false;

        public void AddChange(Action commit, Action rollback)
        {
            if (_committed || _rolledBack)
                throw new InvalidOperationException("Cannot add changes after commit or rollback.");
            _commitActions.Add(commit);
            _rollbackActions.Add(rollback);
        }

        public bool Commit(Func<bool> validation = null)
        {
            if (_committed || _rolledBack)
                throw new InvalidOperationException("Transaction already finalized.");
            if (validation != null && !validation())
            {
                Rollback();
                return false;
            }
            foreach (var action in _commitActions)
            {
                action.Invoke();
            }
            _committed = true;
            return true;
        }

        public void Rollback()
        {
            if (_committed || _rolledBack)
                throw new InvalidOperationException("Transaction already finalized.");
            foreach (var action in _rollbackActions)
            {
                action.Invoke();
            }
            _rolledBack = true;
        }
    }

    // Thread-safe manager for world state transactions
    public class WorldStateTransactionManager
    {
        private static readonly object _lock = new object();
        private static WorldStateTransactionManager _instance;
        public static WorldStateTransactionManager Instance => _instance ?? (_instance = new WorldStateTransactionManager());

        private WorldStateTransactionManager() { }

        // Example: Transactional update for an observable property
        public bool UpdatePropertyTransactionally<T>(ObservableWorldStateProperty<T> property, T newValue, Func<T, T, bool> validate = null)
        {
            lock (_lock)
            {
                T oldValue = property.Value;
                var transaction = new WorldStateTransaction();
                transaction.AddChange(
                    commit: () => property.Value = newValue,
                    rollback: () => property.Value = oldValue
                );
                bool isValid = validate == null || validate(oldValue, newValue);
                return transaction.Commit(() => isValid);
            }
        }

        // General transaction execution for multiple changes
        public bool ExecuteTransaction(WorldStateTransaction transaction, Func<bool> validation = null)
        {
            lock (_lock)
            {
                return transaction.Commit(validation);
            }
        }
    }
}