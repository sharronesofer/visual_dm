using System;
using System.Collections.Generic;
using UnityEngine;
using VisualDM.CombatSystem;
using VisualDM.Systems.EventSystem;

namespace VisualDM.CombatSystem
{
    /// <summary>
    /// Types of action errors for detection and reporting.
    /// </summary>
    public enum ActionErrorType
    {
        None,
        InvalidTarget,
        InsufficientResources,
        StateConflict,
        Timeout,
        Unknown,
    }

    /// <summary>
    /// Data structure for action error events.
    /// </summary>
    public class ActionErrorEvent
    {
        public ActionErrorType ErrorType;
        public CombatActionHandler Handler;
        public string Message;
        public DateTime Timestamp;
        public object Context;

        public ActionErrorEvent(ActionErrorType type, CombatActionHandler handler, string message, object context = null)
        {
            ErrorType = type;
            Handler = handler;
            Message = message;
            Timestamp = DateTime.UtcNow;
            Context = context;
        }
    }

    /// <summary>
    /// Centralized error detection, logging, and reporting for combat actions.
    /// </summary>
    public class ErrorDetector
    {
        private static ErrorDetector _instance;
        public static ErrorDetector Instance => _instance ?? (_instance = new ErrorDetector());

        // Track actions and their start times for timeout detection
        private readonly Dictionary<CombatActionHandler, float> _activeActions = new();
        private readonly float _defaultTimeoutSeconds = 5f;

        // Error logging system
        private readonly List<ActionErrorEvent> _errorLog = new();
        private readonly int _maxLogEntries = 500;

        /// <summary>
        /// Register an action as started (for timeout tracking).
        /// </summary>
        public void RegisterActionStart(CombatActionHandler handler)
        {
            if (handler == null) return;
            _activeActions[handler] = Time.time;
        }

        /// <summary>
        /// Register an action as completed (removes from timeout tracking).
        /// </summary>
        public void RegisterActionComplete(CombatActionHandler handler)
        {
            if (handler == null) return;
            _activeActions.Remove(handler);
        }

        /// <summary>
        /// Check for actions that have timed out and report errors.
        /// </summary>
        public void CheckForTimeouts()
        {
            float now = Time.time;
            var timedOut = new List<CombatActionHandler>();
            foreach (var kvp in _activeActions)
            {
                if (now - kvp.Value > _defaultTimeoutSeconds)
                    timedOut.Add(kvp.Key);
            }
            foreach (var handler in timedOut)
            {
                ReportError(ActionErrorType.Timeout, handler, $"Action timed out after {_defaultTimeoutSeconds} seconds.");
                _activeActions.Remove(handler);
            }
        }

        /// <summary>
        /// Report an error from any action handler or system. Logs, broadcasts, and attempts recovery.
        /// </summary>
        /// <param name="type">The error type.</param>
        /// <param name="handler">The action handler reporting the error.</param>
        /// <param name="message">A descriptive error message.</param>
        /// <param name="context">Optional context for the error.</param>
        public void ReportError(ActionErrorType type, CombatActionHandler handler, string message, object context = null)
        {
            Debug.LogError($"[ErrorDetector] {type}: {message} (Handler: {handler?.GetType().Name})");
            var evt = new ActionErrorEvent(type, handler, message, context);
            LogError(evt);
            EventBus.Instance.Publish(evt);
            CombatEventManager.Instance.RaiseEvent(CombatEventType.ActionError, handler?.Actor, handler?.Target, evt);
            if (type != ActionErrorType.Timeout && type != ActionErrorType.Unknown)
            {
                RecoveryStrategyManager.Instance.Recover(handler, type, context);
            }
        }

        // Log an error event
        private void LogError(ActionErrorEvent evt)
        {
            if (_errorLog.Count >= _maxLogEntries)
                _errorLog.RemoveAt(0);
            _errorLog.Add(evt);
        }

        /// <summary>
        /// Get all error logs, optionally filtered by error type.
        /// </summary>
        /// <param name="filterType">Optional error type to filter by.</param>
        /// <returns>List of error events.</returns>
        public List<ActionErrorEvent> GetErrorLog(ActionErrorType? filterType = null)
        {
            if (filterType == null)
                return new List<ActionErrorEvent>(_errorLog);
            return _errorLog.FindAll(e => e.ErrorType == filterType);
        }

        /// <summary>
        /// Search error logs by message substring.
        /// </summary>
        /// <param name="search">Substring to search for in error messages.</param>
        /// <returns>List of matching error events.</returns>
        public List<ActionErrorEvent> SearchErrorLog(string search)
        {
            return _errorLog.FindAll(e => e.Message != null && e.Message.Contains(search, StringComparison.OrdinalIgnoreCase));
        }

        /// <summary>
        /// Export the error log as a formatted string (for developer tools or file output).
        /// </summary>
        /// <returns>String representation of the error log.</returns>
        public string ExportErrorLog()
        {
            System.Text.StringBuilder sb = new System.Text.StringBuilder();
            foreach (var evt in _errorLog)
            {
                sb.AppendLine($"[{evt.Timestamp:u}] {evt.ErrorType}: {evt.Message} (Handler: {evt.Handler?.GetType().Name})");
            }
            return sb.ToString();
        }
    }
} 