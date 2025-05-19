using System.Collections.Generic;

namespace VDM.Combat
{
    /// <summary>
    /// Handles application, stacking, and removal of combat effects. Integrates with turn system.
    /// </summary>
    public class CombatEffectPipeline
    {
        private readonly Dictionary<ICombatant, List<CombatEffect>> _activeEffects = new();

        public IReadOnlyList<CombatEffect> GetEffects(ICombatant target)
        {
            if (_activeEffects.TryGetValue(target, out var list))
                return list.AsReadOnly();
            return new List<CombatEffect>().AsReadOnly();
        }

        public void ApplyEffect(ICombatant target, CombatEffect effect)
        {
            if (effect.IsImmune(target)) return;
            if (!_activeEffects.ContainsKey(target))
                _activeEffects[target] = new List<CombatEffect>();
            var effects = _activeEffects[target];
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
                    return;
                }
            }
            else
            {
                effects.Add(effect);
            }
            effect.OnApply(target);
        }

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

        public void OnTurnStart(ICombatant target)
        {
            if (!_activeEffects.TryGetValue(target, out var list)) return;
            foreach (var effect in new List<CombatEffect>(list))
            {
                effect.OnTurnStart(target);
            }
        }

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