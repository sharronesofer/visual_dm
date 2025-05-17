using System;
using System.Collections.Generic;
using System.Threading;
using UnityEngine;

namespace VisualDM.CombatSystem
{
    /// <summary>
    /// Singleton for managing global combat state, transitions, and synchronization.
    /// </summary>
    public class CombatStateManager
    {
        private static CombatStateManager _instance;
        private static readonly object _instanceLock = new object();
        public static CombatStateManager Instance
        {
            get
            {
                lock (_instanceLock)
                {
                    return _instance ??= new CombatStateManager();
                }
            }
        }

        private readonly HashSet<GameObject> activeCombatants = new HashSet<GameObject>();
        private readonly Dictionary<GameObject, CombatActionHandler> currentActions = new Dictionary<GameObject, CombatActionHandler>();
        private readonly Dictionary<GameObject, List<IEffect>> statusEffects = new Dictionary<GameObject, List<IEffect>>();
        private readonly Stack<StateSnapshot> rollbackStack = new Stack<StateSnapshot>();
        private readonly object stateLock = new object();

        // Transaction support for multi-step actions
        private StateSnapshot _pendingTransactionSnapshot = null;
        private bool _transactionActive = false;

        private CombatStateManager() { }

        #region State Tracking
        public void AddCombatant(GameObject combatant)
        {
            lock (stateLock)
            {
                activeCombatants.Add(combatant);
            }
        }

        public void RemoveCombatant(GameObject combatant)
        {
            lock (stateLock)
            {
                activeCombatants.Remove(combatant);
                currentActions.Remove(combatant);
                statusEffects.Remove(combatant);
            }
        }

        public void SetCurrentAction(GameObject combatant, CombatActionHandler action)
        {
            lock (stateLock)
            {
                currentActions[combatant] = action;
            }
        }

        public CombatActionHandler GetCurrentAction(GameObject combatant)
        {
            lock (stateLock)
            {
                return currentActions.TryGetValue(combatant, out var action) ? action : null;
            }
        }

        public void AddStatusEffect(GameObject combatant, IEffect effect)
        {
            lock (stateLock)
            {
                if (!statusEffects.ContainsKey(combatant))
                    statusEffects[combatant] = new List<IEffect>();
                statusEffects[combatant].Add(effect);
            }
        }

        public List<IEffect> GetStatusEffects(GameObject combatant)
        {
            lock (stateLock)
            {
                return statusEffects.TryGetValue(combatant, out var effects) ? new List<IEffect>(effects) : new List<IEffect>();
            }
        }
        #endregion

        #region State Transition Validation
        public bool ValidateStateTransition(GameObject combatant, CombatActionHandler.ActionState from, CombatActionHandler.ActionState to)
        {
            // Example: Only allow Ready -> InProgress, InProgress -> Completed/Cancelled
            if (from == CombatActionHandler.ActionState.Ready && to == CombatActionHandler.ActionState.InProgress)
                return true;
            if (from == CombatActionHandler.ActionState.InProgress && (to == CombatActionHandler.ActionState.Completed || to == CombatActionHandler.ActionState.Cancelled))
                return true;
            return false;
        }
        #endregion

        #region Conflict Resolution
        public bool ResolveActionConflict(GameObject combatant, CombatActionHandler newAction)
        {
            lock (stateLock)
            {
                var existing = GetCurrentAction(combatant);
                if (existing == null) return true;
                // Example: Prefer higher priority, then earlier timestamp
                int newPriority = GetPriority(newAction);
                int existingPriority = GetPriority(existing);
                if (newPriority > existingPriority) return true;
                if (newPriority == existingPriority)
                {
                    // Use timestamp if available
                    return DateTime.UtcNow < DateTime.UtcNow.AddMilliseconds(1); // Placeholder, replace with real timestamp logic
                }
                return false;
            }
        }
        private int GetPriority(CombatActionHandler action)
        {
            // Placeholder: derive from action type or data
            return 0;
        }
        #endregion

        #region State Rollback
        private class StateSnapshot
        {
            public HashSet<GameObject> Combatants;
            public Dictionary<GameObject, CombatActionHandler> Actions;
            public Dictionary<GameObject, List<IEffect>> Effects;
        }
        public void SaveStateSnapshot()
        {
            lock (stateLock)
            {
                rollbackStack.Push(new StateSnapshot
                {
                    Combatants = new HashSet<GameObject>(activeCombatants),
                    Actions = new Dictionary<GameObject, CombatActionHandler>(currentActions),
                    Effects = new Dictionary<GameObject, List<IEffect>>()
                });
                foreach (var kvp in statusEffects)
                {
                    rollbackStack.Peek().Effects[kvp.Key] = new List<IEffect>(kvp.Value);
                }
            }
        }
        public void RollbackState()
        {
            lock (stateLock)
            {
                if (rollbackStack.Count == 0) return;
                var snap = rollbackStack.Pop();
                activeCombatants.Clear();
                foreach (var c in snap.Combatants) activeCombatants.Add(c);
                currentActions.Clear();
                foreach (var kvp in snap.Actions) currentActions[kvp.Key] = kvp.Value;
                statusEffects.Clear();
                foreach (var kvp in snap.Effects) statusEffects[kvp.Key] = new List<IEffect>(kvp.Value);
            }
        }
        #endregion

        #region Synchronization
        public void SynchronizeWithActionSystem(/* params as needed */)
        {
            // Implement integration logic here
        }
        #endregion

        // Add this method to be called from the main game loop or a MonoBehaviour
        public void Update(float deltaTime)
        {
            // ... existing update logic ...
            ErrorDetector.Instance.CheckForTimeouts();
        }

        public void BeginTransaction()
        {
            lock (stateLock)
            {
                if (_transactionActive) throw new InvalidOperationException("Transaction already active");
                _pendingTransactionSnapshot = new StateSnapshot
                {
                    Combatants = new HashSet<GameObject>(activeCombatants),
                    Actions = new Dictionary<GameObject, CombatActionHandler>(currentActions),
                    Effects = new Dictionary<GameObject, List<IEffect>>()
                };
                foreach (var kvp in statusEffects)
                {
                    _pendingTransactionSnapshot.Effects[kvp.Key] = new List<IEffect>(kvp.Value);
                }
                _transactionActive = true;
            }
        }

        public void CommitTransaction()
        {
            lock (stateLock)
            {
                if (!_transactionActive) throw new InvalidOperationException("No active transaction");
                _pendingTransactionSnapshot = null;
                _transactionActive = false;
            }
        }

        public void RollbackTransaction()
        {
            lock (stateLock)
            {
                if (!_transactionActive) throw new InvalidOperationException("No active transaction");
                if (_pendingTransactionSnapshot == null) return;
                activeCombatants.Clear();
                foreach (var c in _pendingTransactionSnapshot.Combatants) activeCombatants.Add(c);
                currentActions.Clear();
                foreach (var kvp in _pendingTransactionSnapshot.Actions) currentActions[kvp.Key] = kvp.Value;
                statusEffects.Clear();
                foreach (var kvp in _pendingTransactionSnapshot.Effects) statusEffects[kvp.Key] = new List<IEffect>(kvp.Value);
                _pendingTransactionSnapshot = null;
                _transactionActive = false;
            }
        }
    }
} 