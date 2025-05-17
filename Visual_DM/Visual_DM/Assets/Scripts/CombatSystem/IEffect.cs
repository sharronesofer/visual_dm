using UnityEngine;

namespace VisualDM.CombatSystem
{
    /// <summary>
    /// Interface for all combat effects.
    /// </summary>
    public interface IEffect
    {
        /// <summary>
        /// Applies the effect to the target.
        /// </summary>
        void Apply(GameObject target);

        /// <summary>
        /// Removes the effect from the target.
        /// </summary>
        void Remove(GameObject target);

        /// <summary>
        /// Gets the remaining duration of the effect in seconds.
        /// </summary>
        float GetDuration();

        /// <summary>
        /// Gets the effect's priority for processing order.
        /// </summary>
        int GetPriority();

        /// <summary>
        /// Returns true if the effect is currently active.
        /// </summary>
        bool IsActive();

        /// <summary>
        /// Event triggered when the effect is applied.
        /// </summary>
        event System.Action<GameObject, IEffect> OnEffectApplied;

        /// <summary>
        /// Event triggered when the effect is removed.
        /// </summary>
        event System.Action<GameObject, IEffect> OnEffectRemoved;
    }
} 