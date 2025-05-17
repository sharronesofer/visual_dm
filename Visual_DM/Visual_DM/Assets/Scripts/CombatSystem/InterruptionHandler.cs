using System;
using UnityEngine;
using VisualDM.Systems.EventSystem;

namespace VisualDM.CombatSystem
{
    public enum InterruptionSource
    {
        PlayerInput,
        GameEvent,
        System,
        Unknown
    }

    public class ActionInterruptedEvent
    {
        public CombatActionHandler Handler;
        public InterruptionSource Source;
        public string Reason;
        public DateTime Timestamp;
        public object Context;

        public ActionInterruptedEvent(CombatActionHandler handler, InterruptionSource source, string reason, object context = null)
        {
            Handler = handler;
            Source = source;
            Reason = reason;
            Timestamp = DateTime.UtcNow;
            Context = context;
        }
    }

    /// <summary>
    /// Handles detection and cleanup for interrupted actions.
    /// </summary>
    public class InterruptionHandler
    {
        private static InterruptionHandler _instance;
        public static InterruptionHandler Instance => _instance ?? (_instance = new InterruptionHandler());

        // Interrupt an action, clean up, and broadcast event
        public void InterruptAction(CombatActionHandler handler, InterruptionSource source, string reason, object context = null)
        {
            if (handler == null) return;
            // Clean cancellation of animations/effects (extend as needed)
            handler.CancelAction();
            // TODO: Add animation/effect cleanup hooks here
            // Broadcast interruption event
            var evt = new ActionInterruptedEvent(handler, source, reason, context);
            EventBus.Instance.Publish(evt);
            // Log as error for analytics/debugging
            ErrorDetector.Instance.ReportError(ActionErrorType.StateConflict, handler, $"Action interrupted: {reason}", context);
        }
    }
} 