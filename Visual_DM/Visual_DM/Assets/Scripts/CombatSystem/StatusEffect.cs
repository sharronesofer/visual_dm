using UnityEngine;
using System;
using System.Collections.Generic;

namespace VisualDM.CombatSystem
{
    /// <summary>
    /// Represents a status effect (buff or debuff) applied to a target.
    /// </summary>
    public class StatusEffect : IEffect
    {
        public string EffectName { get; private set; }
        public float Duration { get; private set; }
        public int Priority { get; private set; }
        public int MaxStacks { get; private set; }
        private int currentStacks;
        private float elapsed;
        private bool active;

        public event Action<GameObject, IEffect> OnEffectApplied;
        public event Action<GameObject, IEffect> OnEffectRemoved;

        public StatusEffect(string effectName, float duration, int priority = 0, int maxStacks = 1)
        {
            EffectName = effectName;
            Duration = duration;
            Priority = priority;
            MaxStacks = maxStacks;
            currentStacks = 1;
            elapsed = 0f;
            active = false;
        }

        public void Apply(GameObject target)
        {
            if (!active)
            {
                active = true;
                OnEffectApplied?.Invoke(target, this);
            }
            else if (currentStacks < MaxStacks)
            {
                currentStacks++;
                // Optionally refresh duration on stacking
                elapsed = 0f;
            }
        }

        public void Remove(GameObject target)
        {
            if (!active) return;
            active = false;
            currentStacks = 0;
            OnEffectRemoved?.Invoke(target, this);
        }

        public float GetDuration() => Duration;
        public int GetPriority() => Priority;
        public bool IsActive() => active;
        public int GetCurrentStacks() => currentStacks;

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