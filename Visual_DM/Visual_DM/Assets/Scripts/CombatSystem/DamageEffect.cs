using UnityEngine;
using System;

namespace VisualDM.CombatSystem
{
    /// <summary>
    /// Represents a damage effect applied to a target.
    /// </summary>
    public class DamageEffect : IEffect
    {
        public float Amount { get; private set; }
        public float Duration { get; private set; }
        public int Priority { get; private set; }
        private float elapsed;
        private bool active;

        public event Action<GameObject, IEffect> OnEffectApplied;
        public event Action<GameObject, IEffect> OnEffectRemoved;

        public DamageEffect(float amount, float duration = 0f, int priority = 0)
        {
            Amount = amount;
            Duration = duration;
            Priority = priority;
            elapsed = 0f;
            active = false;
        }

        public void Apply(GameObject target)
        {
            if (active) return;
            var health = target.GetComponent<IHealthComponent>();
            if (health != null)
            {
                health.TakeDamage(Amount);
            }
            active = true;
            OnEffectApplied?.Invoke(target, this);
        }

        public void Remove(GameObject target)
        {
            if (!active) return;
            // No removal logic for instant damage, but could be extended for DoT
            active = false;
            OnEffectRemoved?.Invoke(target, this);
        }

        public float GetDuration() => Duration;
        public int GetPriority() => Priority;
        public bool IsActive() => active;

        public void Update(float deltaTime, GameObject target)
        {
            if (!active || Duration <= 0f) return;
            elapsed += deltaTime;
            if (elapsed >= Duration)
            {
                Remove(target);
            }
        }
    }
} 