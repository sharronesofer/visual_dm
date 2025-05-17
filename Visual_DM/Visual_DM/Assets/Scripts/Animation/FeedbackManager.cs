using System;
using System.Collections.Generic;
using UnityEngine;

namespace VisualDM.Animation
{
    public enum FeedbackType
    {
        HitReaction,
        Particle,
        CameraEffect,
        Custom
    }

    public class FeedbackEffect
    {
        public FeedbackType Type;
        public int Priority;
        public float TriggerTime;
        public float Duration;
        public Action Callback;
        public bool IsActive;
    }

    /// <summary>
    /// Manages a priority queue of visual feedback effects, supporting merging, cancellation, and sequencing.
    /// </summary>
    public class FeedbackManager
    {
        private static FeedbackManager _instance;
        public static FeedbackManager Instance => _instance ?? (_instance = new FeedbackManager());

        private readonly List<FeedbackEffect> queue = new List<FeedbackEffect>();
        private readonly Dictionary<FeedbackType, int> typePriority = new Dictionary<FeedbackType, int>
        {
            { FeedbackType.HitReaction, 100 },
            { FeedbackType.Particle, 50 },
            { FeedbackType.CameraEffect, 75 },
            { FeedbackType.Custom, 10 }
        };

        public void EnqueueFeedback(FeedbackEffect effect)
        {
            if (!typePriority.TryGetValue(effect.Type, out int basePriority))
                basePriority = 0;
            effect.Priority += basePriority;
            queue.Add(effect);
            queue.Sort((a, b) =>
            {
                int cmp = a.TriggerTime.CompareTo(b.TriggerTime);
                if (cmp == 0) cmp = b.Priority.CompareTo(a.Priority); // Higher priority first
                return cmp;
            });
        }

        public void Update(float deltaTime)
        {
            float now = Time.time;
            for (int i = queue.Count - 1; i >= 0; i--)
            {
                var effect = queue[i];
                if (!effect.IsActive && now >= effect.TriggerTime)
                {
                    effect.IsActive = true;
                    effect.Callback?.Invoke();
                }
                if (effect.IsActive && now >= effect.TriggerTime + effect.Duration)
                {
                    queue.RemoveAt(i);
                }
            }
        }

        public void CancelFeedback(Predicate<FeedbackEffect> match)
        {
            queue.RemoveAll(match);
        }

        public void SetPriority(FeedbackType type, int priority)
        {
            typePriority[type] = priority;
        }
    }
} 