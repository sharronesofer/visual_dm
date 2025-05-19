using System;

namespace VDM.POI
{
    /// <summary>
    /// Abstract base class for all POI states.
    /// </summary>
    public abstract class POIState
    {
        protected IPOIStateContext context;

        protected POIState(IPOIStateContext context)
        {
            this.context = context;
        }

        /// <summary>
        /// Called when entering this state.
        /// </summary>
        public abstract void EnterState();

        /// <summary>
        /// Called when exiting this state.
        /// </summary>
        public abstract void ExitState();

        /// <summary>
        /// Checks if a transition to another state should occur.
        /// </summary>
        public abstract void CheckTransition();

        /// <summary>
        /// Returns the name of the state.
        /// </summary>
        public abstract string StateName { get; }
    }
} 