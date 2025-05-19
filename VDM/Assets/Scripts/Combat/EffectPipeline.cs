using System.Collections.Generic;

namespace VDM.Combat
{
    /// <summary>
    /// Handles application, timing, and removal of combat effects.
    /// </summary>
    public class EffectPipeline
    {
        private readonly Dictionary<ICombatant, List<CombatEffect>> _activeEffects = new();

        /// <summary>
        /// Gets the list of active effects for a combatant.
        /// </summary>
        public IReadOnlyList<CombatEffect> GetEffects(ICombatant target)
        {
            if (_activeEffects.TryGetValue(target, out var list))
                return list.AsReadOnly();
            return new List<CombatEffect>().AsReadOnly();
        }

        /// <summary>
        /// Applies an effect to a combatant, handling stacking/overriding/resistance.
        /// </summary>
        public void ApplyEffect(ICombatant target, CombatEffect effect)
        {
            if (effect.IsImmune(target)) return;
            if (!_activeEffects.ContainsKey(target))
                _activeEffects[target] = new List<CombatEffect>();
            var effects = _activeEffects[target];

            // Check for existing effect of same type
            var existing = effects.Find(e => e.GetType() == effect.GetType());
            if (existing != null)
            {
                if (existing.CanStack && effect.CanStack)
                {
                    effects.Add(effect);
                }
                else if (effect.CanOverride)
                {
                    RemoveEffect(target, existing);
                    effects.Add(effect);
                }
                else
                {
                    // Effect is resisted or cannot override
                    return;
                }
            }
            else
            {
                effects.Add(effect);
            }
            effect.OnApply(target);
        }

        /// <summary>
        /// Removes an effect from a combatant.
        /// </summary>
        public void RemoveEffect(ICombatant target, CombatEffect effect)
        {
            if (_activeEffects.TryGetValue(target, out var list))
            {
                if (list.Remove(effect))
                {
                    effect.OnRemove(target);
                }
            }
        }

        /// <summary>
        /// Called at the start of a combatant's turn to process effect hooks and durations.
        /// </summary>
        public void OnTurnStart(ICombatant target)
        {
            if (!_activeEffects.TryGetValue(target, out var list)) return;
            foreach (var effect in new List<CombatEffect>(list))
            {
                effect.OnTurnStart(target);
            }
        }

        /// <summary>
        /// Called at the end of a combatant's turn to process effect hooks and decrement durations.
        /// </summary>
        public void OnTurnEnd(ICombatant target)
        {
            if (!_activeEffects.TryGetValue(target, out var list)) return;
            var toRemove = new List<CombatEffect>();
            foreach (var effect in list)
            {
                effect.OnTurnEnd(target);
                if (effect.Duration > 0)
                {
                    effect.Duration--;
                    if (effect.Duration == 0)
                        toRemove.Add(effect);
                }
            }
            foreach (var effect in toRemove)
            {
                RemoveEffect(target, effect);
            }
        }

        /// <summary>
        /// Called when a combatant takes damage to process effect hooks.
        /// </summary>
        public void OnDamage(ICombatant target, int damage)
        {
            if (!_activeEffects.TryGetValue(target, out var list)) return;
            foreach (var effect in new List<CombatEffect>(list))
            {
                effect.OnDamage(target, damage);
            }
        }
    }
} 