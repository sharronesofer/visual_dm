// ActionRequest.cs
// Reference: See /docs/bible_qa.md for design rationale and requirements.
using System;
using System.Threading;

namespace VisualDM.Systems.Combat
{
    /// <summary>
    /// Represents a request to perform an action in the combat/contextual action system.
    /// </summary>
    public class ActionRequest
    {
        /// <summary>Type of action (basic, special, contextual, chain, etc.)</summary>
        public string ActionType { get; set; }
        /// <summary>Source of the action (player, AI, system, etc.)</summary>
        public string Source { get; }
        /// <summary>Priority of the action (higher = more important)</summary>
        public int Priority { get; }
        /// <summary>Time the request was created (ms since startup)</summary>
        public float Timestamp { get; }
        /// <summary>Optional context object for additional data</summary>
        public object Context { get; }
        /// <summary>Globally unique identifier for this action request</summary>
        public Guid RequestId { get; }

        // Thread-safe mutable state (e.g., for cancellation)
        private int _cancelled;
        /// <summary>Returns true if the request has been cancelled.</summary>
        public bool IsCancelled => Interlocked.CompareExchange(ref _cancelled, 0, 0) != 0;
        /// <summary>Cancel this request in a thread-safe way.</summary>
        public void Cancel() => Interlocked.Exchange(ref _cancelled, 1);

        public ActionRequest(string actionType, string source, int priority, float timestamp, object context = null)
        {
            ActionType = actionType;
            Source = source;
            Priority = priority;
            Timestamp = timestamp;
            Context = context;
            RequestId = Guid.NewGuid();
            _cancelled = 0;
        }
    }
} 