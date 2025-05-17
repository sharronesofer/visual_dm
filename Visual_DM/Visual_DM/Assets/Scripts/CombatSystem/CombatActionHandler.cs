using System;
using UnityEngine;
using VisualDM.CombatSystem;

namespace VisualDM.CombatSystem
{
    /// <summary>
    /// Abstract base class for all combat action handlers.
    /// </summary>
    public abstract class CombatActionHandler : IActionProcessor
    {
        public enum ActionState { Ready, InProgress, Completed, Cancelled }

        public ActionState State { get; protected set; } = ActionState.Ready;
        public GameObject Actor { get; protected set; }
        public GameObject Target { get; protected set; }
        public float Cooldown { get; protected set; }
        public float ResourceCost { get; protected set; }

        protected float cooldownTimer = 0f;

        public CombatActionHandler(GameObject actor, GameObject target, float cooldown, float resourceCost)
        {
            Actor = actor;
            Target = target;
            Cooldown = cooldown;
            ResourceCost = resourceCost;
        }

        /// <summary>
        /// Called when the action starts.
        /// </summary>
        public virtual void StartAction() 
        { 
            State = ActionState.InProgress;
            ErrorDetector.Instance.RegisterActionStart(this);
        }

        /// <summary>
        /// Called every update tick while the action is in progress.
        /// </summary>
        public virtual void UpdateAction(float deltaTime) { }

        /// <summary>
        /// Called when the action ends.
        /// </summary>
        public virtual void EndAction() 
        { 
            State = ActionState.Completed;
            ErrorDetector.Instance.RegisterActionComplete(this);
        }

        /// <summary>
        /// Cancels the action.
        /// </summary>
        public virtual void CancelAction() 
        { 
            State = ActionState.Cancelled;
            ErrorDetector.Instance.RegisterActionComplete(this);
        }

        /// <summary>
        /// Interrupts the action, cleans up, and broadcasts interruption event.
        /// </summary>
        public virtual void InterruptAction(InterruptionSource source, string reason, object context = null)
        {
            // Subclasses can override to clean up temporary resources or states
            InterruptionHandler.Instance.InterruptAction(this, source, reason, context);
        }

        /// <summary>
        /// Report an error for this action.
        /// </summary>
        public void ReportError(ActionErrorType type, string message, object context = null)
        {
            ErrorDetector.Instance.ReportError(type, this, message, context);
        }
    }
} 