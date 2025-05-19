using System;
using System.Collections.Generic;
using System.Threading;

namespace VisualDM.Systems.Quest
{
    /// <summary>
    /// Thread-safe state machine for quest state transitions with validation and logging.
    /// </summary>
    public class QuestStateMachine
    {
        private QuestState _currentState;
        private readonly object _lock = new object();
        private readonly List<string> _transitionLog = new List<string>();

        public QuestState CurrentState
        {
            get { lock (_lock) { return _currentState; } }
        }

        public IReadOnlyList<string> TransitionLog => _transitionLog.AsReadOnly();

        public QuestStateMachine(QuestState initialState = QuestState.Locked)
        {
            _currentState = initialState;
            LogTransition(null, initialState);
        }

        /// <summary>
        /// Attempts to transition to a new state. Returns true if successful.
        /// </summary>
        public bool TryTransition(QuestState newState)
        {
            lock (_lock)
            {
                if (IsValidTransition(_currentState, newState))
                {
                    var oldState = _currentState;
                    _currentState = newState;
                    LogTransition(oldState, newState);
                    return true;
                }
                else
                {
                    LogInvalidTransition(_currentState, newState);
                    return false;
                }
            }
        }

        /// <summary>
        /// Validates if a transition from oldState to newState is allowed.
        /// </summary>
        private bool IsValidTransition(QuestState oldState, QuestState newState)
        {
            // Example rules (expand as needed):
            if (oldState == newState) return false;
            if (oldState.HasFlag(QuestState.Expired)) return false;
            if (oldState.HasFlag(QuestState.Complete) && !newState.HasFlag(QuestState.Repeatable)) return false;
            // Add more rules as needed for your quest logic
            return true;
        }

        private void LogTransition(QuestState? from, QuestState to)
        {
            string msg = from == null
                ? $"[QuestStateMachine] Initialized to {to} at {DateTime.UtcNow:o}"
                : $"[QuestStateMachine] Transition: {from} -> {to} at {DateTime.UtcNow:o}";
            _transitionLog.Add(msg);
            UnityEngine.Debug.Log(msg);
        }

        private void LogInvalidTransition(QuestState from, QuestState to)
        {
            string msg = $"[QuestStateMachine] Invalid transition: {from} -> {to} at {DateTime.UtcNow:o}";
            _transitionLog.Add(msg);
            UnityEngine.Debug.LogWarning(msg);
        }
    }
} 