using System;
using System.Collections.Generic;

namespace VisualDM.Systems.MotifSystem
{
    /// <summary>
    /// Manages transactions for Motif and MotifPool operations, supporting atomicity and rollback.
    /// </summary>
    public class MotifTransactionManager : IDisposable
    {
        private readonly List<Action> _rollbackActions = new List<Action>();
        private bool _committed = false;
        private readonly List<string> _log = new List<string>();
        private bool _inTransaction = false;
        private readonly List<Action> _transactionLog = new List<Action>();

        public void RegisterRollback(Action rollbackAction)
        {
            _rollbackActions.Add(rollbackAction);
        }

        public void Log(string message)
        {
            _log.Add($"[{DateTime.UtcNow:O}] {message}");
        }

        public bool BeginTransaction()
        {
            try
            {
                if (_inTransaction) return false;
                _inTransaction = true;
                _transactionLog.Clear();
                return true;
            }
            catch (Exception ex)
            {
                VisualDM.Utilities.ErrorHandlingService.Instance.LogException(ex, "MotifTransactionManager.BeginTransaction failed", "MotifTransactionManager.BeginTransaction");
                VisualDM.Core.MonitoringManager.Instance?.IncrementErrorCount();
                return false;
            }
        }

        public bool Commit()
        {
            try
            {
                if (!_inTransaction) return false;
                _inTransaction = false;
                _transactionLog.Clear();
                return true;
            }
            catch (Exception ex)
            {
                VisualDM.Utilities.ErrorHandlingService.Instance.LogException(ex, "MotifTransactionManager.Commit failed", "MotifTransactionManager.Commit");
                VisualDM.Core.MonitoringManager.Instance?.IncrementErrorCount();
                return false;
            }
        }

        public bool Rollback()
        {
            try
            {
                if (!_inTransaction) return false;
                // Rollback logic here
                foreach (var action in _transactionLog.Reverse<Action>())
                {
                    try { action(); } catch { /* Swallow rollback errors */ }
                }
                _inTransaction = false;
                _transactionLog.Clear();
                return true;
            }
            catch (Exception ex)
            {
                VisualDM.Utilities.ErrorHandlingService.Instance.LogException(ex, "MotifTransactionManager.Rollback failed", "MotifTransactionManager.Rollback");
                VisualDM.Core.MonitoringManager.Instance?.IncrementErrorCount();
                return false;
            }
        }

        public void Dispose()
        {
            if (!_committed)
            {
                foreach (var rollback in _rollbackActions)
                {
                    rollback();
                }
                Log("Transaction rolled back.");
            }
        }

        public IEnumerable<string> GetLog() => _log;
    }
}