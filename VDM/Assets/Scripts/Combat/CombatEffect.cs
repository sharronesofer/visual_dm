namespace VDM.Combat
{
    /// <summary>
    /// Base class for all combat effects (buffs, debuffs, statuses).
    /// </summary>
    public abstract class CombatEffect
    {
        /// <summary>
        /// The type/category of this effect.
        /// </summary>
        public EffectType Type { get; protected set; }

        /// <summary>
        /// The number of turns this effect lasts. -1 for infinite.
        /// </summary>
        public int Duration { get; protected set; }

        /// <summary>
        /// Whether this effect can stack with others of the same type.
        /// </summary>
        public virtual bool CanStack => false;

        /// <summary>
        /// Whether this effect can be overridden by a new effect of the same type.
        /// </summary>
        public virtual bool CanOverride => true;

        /// <summary>
        /// Whether the target is resistant or immune to this effect.
        /// </summary>
        public virtual bool IsResisted(ICombatant target) => false;
        public virtual bool IsImmune(ICombatant target) => false;

        /// <summary>
        /// Called when the effect is applied to a target.
        /// </summary>
        public virtual void OnApply(ICombatant target) { }

        /// <summary>
        /// Called at the start of the target's turn.
        /// </summary>
        public virtual void OnTurnStart(ICombatant target) { }

        /// <summary>
        /// Called at the end of the target's turn.
        /// </summary>
        public virtual void OnTurnEnd(ICombatant target) { }

        /// <summary>
        /// Called when the effect is removed from the target.
        /// </summary>
        public virtual void OnRemove(ICombatant target) { }

        /// <summary>
        /// Called when the target takes damage.
        /// </summary>
        public virtual void OnDamage(ICombatant target, int damage) { }
    }
} 