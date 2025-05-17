using System.Collections.Generic;
using UnityEngine;

namespace VisualDM.CombatSystem
{
    /// <summary>
    /// Manages a pipeline of combat effects for a target.
    /// </summary>
    public class EffectProcessor
    {
        private readonly List<IEffect> activeEffects = new List<IEffect>();
        private readonly List<EffectModifier> modifiers = new List<EffectModifier>();
        private readonly object lockObj = new object();

        public event System.Action<IEffect, GameObject> OnEffectApplied;
        public event System.Action<IEffect, GameObject> OnEffectRemoved;

        public void AddModifier(EffectModifier modifier)
        {
            modifiers.Add(modifier);
        }

        public void ApplyEffect(IEffect effect, GameObject target)
        {
            lock (lockObj)
            {
                // Apply modifiers
                foreach (var mod in modifiers)
                    mod.Modify(effect, target);
                // Stacking: check if effect of same type exists
                var existing = activeEffects.Find(e => e.GetType() == effect.GetType());
                if (existing != null && effect is StatusEffect status)
                {
                    (existing as StatusEffect)?.Apply(target); // Stack
                    return;
                }
                effect.OnEffectApplied += HandleEffectApplied;
                effect.OnEffectRemoved += HandleEffectRemoved;
                effect.Apply(target);
                activeEffects.Add(effect);
            }
        }

        public void RemoveEffect(IEffect effect, GameObject target)
        {
            lock (lockObj)
            {
                if (activeEffects.Contains(effect))
                {
                    effect.Remove(target);
                    activeEffects.Remove(effect);
                }
            }
        }

        public void UpdateEffects(float deltaTime, GameObject target)
        {
            lock (lockObj)
            {
                for (int i = activeEffects.Count - 1; i >= 0; i--)
                {
                    var effect = activeEffects[i];
                    if (effect is DamageEffect dmg)
                        dmg.Update(deltaTime, target);
                    else if (effect is HealEffect heal)
                        heal.Update(deltaTime, target);
                    else if (effect is StatusEffect status)
                        status.Update(deltaTime, target);
                    if (!effect.IsActive())
                        activeEffects.RemoveAt(i);
                }
            }
        }

        public void InterruptAll(GameObject target)
        {
            lock (lockObj)
            {
                foreach (var effect in activeEffects)
                {
                    effect.Remove(target);
                }
                activeEffects.Clear();
            }
        }

        private void HandleEffectApplied(GameObject target, IEffect effect)
        {
            OnEffectApplied?.Invoke(effect, target);
        }

        private void HandleEffectRemoved(GameObject target, IEffect effect)
        {
            OnEffectRemoved?.Invoke(effect, target);
        }
    }
} 