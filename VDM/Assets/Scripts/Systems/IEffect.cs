namespace VisualDM.Systems
{
    /// <summary>
    /// Interface for game effects that can be applied to and removed from targets.
    /// Used for status effects, buffs, debuffs, and temporary modifications to game objects.
    /// </summary>
    public interface IEffect
    {
        /// <summary>
        /// Applies this effect to the specified target.
        /// </summary>
        /// <param name="target">The object to which the effect will be applied.</param>
        void Apply(object target);

        /// <summary>
        /// Removes this effect from the specified target.
        /// </summary>
        /// <param name="target">The object from which the effect will be removed.</param>
        void Remove(object target);
    }
} 