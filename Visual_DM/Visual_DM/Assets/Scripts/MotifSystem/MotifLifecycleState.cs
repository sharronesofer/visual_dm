using System;

namespace VisualDM.MotifSystem
{
    /// <summary>
    /// Defines all possible states in a motif's lifecycle.
    /// </summary>
    public enum MotifLifecycleState
    {
        Created,
        Active,
        Triggered,
        Completed,
        Archived
    }

    public static class MotifLifecycleStateHelper
    {
        /// <summary>
        /// Validates if a transition from one state to another is allowed.
        /// </summary>
        public static bool IsValidTransition(MotifLifecycleState from, MotifLifecycleState to)
        {
            switch (from)
            {
                case MotifLifecycleState.Created:
                    return to == MotifLifecycleState.Active;
                case MotifLifecycleState.Active:
                    return to == MotifLifecycleState.Triggered || to == MotifLifecycleState.Completed;
                case MotifLifecycleState.Triggered:
                    return to == MotifLifecycleState.Completed;
                case MotifLifecycleState.Completed:
                    return to == MotifLifecycleState.Archived;
                case MotifLifecycleState.Archived:
                    return false;
                default:
                    return false;
            }
        }
    }
} 