using System;

namespace VisualDM.Systems.MotifSystem
{
    /// <summary>
    /// Manages the lifecycle state of a Motif, validates transitions, and emits events.
    /// </summary>
    public class MotifStateMachine
    {
        public Motif Motif { get; }
        public MotifLifecycleState State { get; private set; }

        public MotifStateMachine(Motif motif, MotifLifecycleState initialState = MotifLifecycleState.Created)
        {
            Motif = motif;
            State = initialState;
        }

        /// <summary>
        /// Attempts to transition the motif to a new state. Returns false if invalid or on error.
        /// </summary>
        /// <param name="newState">The new state to transition to.</param>
        /// <param name="actor">The actor performing the transition.</param>
        /// <param name="context">The context for the transition.</param>
        /// <returns>True if the transition succeeded, false otherwise.</returns>
        public bool TryTransition(MotifLifecycleState newState, string actor = null, string context = null)
        {
            try
            {
                if (!MotifValidator.ValidateMotif(Motif))
                {
                    VisualDM.Utilities.ErrorHandlingService.Instance.LogUserError($"MotifStateMachine: Invalid motif in state transition: {Motif?.Theme ?? "<null>"}", "MotifStateMachine.TryTransition");
                    VisualDM.Core.MonitoringManager.Instance?.IncrementErrorCount();
                    return false;
                }
                if (!MotifLifecycleStateHelper.IsValidTransition(State, newState))
                    return false;
                var oldState = State;
                State = newState;
                MotifEventDispatcher.PublishStateChanged(new MotifStateChangedEvent(
                    Motif,
                    oldState,
                    newState,
                    actor,
                    context,
                    DateTime.UtcNow
                ));
                return true;
            }
            catch (Exception ex)
            {
                VisualDM.Utilities.ErrorHandlingService.Instance.LogException(ex, "MotifStateMachine.TryTransition failed", "MotifStateMachine.TryTransition");
                VisualDM.Core.MonitoringManager.Instance?.IncrementErrorCount();
                return false;
            }
        }
    }
}