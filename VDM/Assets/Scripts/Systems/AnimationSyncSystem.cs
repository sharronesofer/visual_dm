using System;
using System.Collections.Generic;
using UnityEngine;

namespace VisualDM.Systems.Animation
{
    /// <summary>
    /// Central system for coordinating animation synchronization, blending, effects, feedback, and cancellation.
    /// </summary>
    public class AnimationSyncSystem
    {
        private readonly List<AnimationTimeline> activeTimelines = new List<AnimationTimeline>();
        private readonly List<AnimationBlendManager> activeBlends = new List<AnimationBlendManager>();
        private readonly List<DamageSync> activeDamageSyncs = new List<DamageSync>();
        private readonly List<AnimationCancellationHandler> activeCancellations = new List<AnimationCancellationHandler>();

        // Example: versioning and extensibility hooks (stub for integration)
        public string SystemVersion => "1.0.0"; // Integrate with Task #541
        // public IAnimationExtensibility Extensibility { get; set; } // Integrate with Task #540

        // Start a new synchronized animation
        public AnimationTimeline StartSynchronizedAnimation(string animationName, float duration, float playbackRate = 1.0f)
        {
            var timeline = new AnimationTimeline();
            timeline.Start(duration, playbackRate);
            activeTimelines.Add(timeline);
            // Load effect config and register events
            var triggers = AnimationEffectConfig.GetEffectsForAnimation(animationName);
            foreach (var trig in triggers)
            {
                timeline.RegisterEvent(trig.NormalizedTime, () => SystemsManager.Instance.EnqueueSystems(new SystemsEffect
                {
                    Type = SystemsType.Particle,
                    Priority = 0,
                    TriggerTime = Time.time,
                    Duration = 0.5f,
                    Callback = () => { /* Play effect */ },
                    IsActive = false
                }));
            }
            return timeline;
        }

        // Update all animation components
        public void UpdateAll(float deltaTime)
        {
            foreach (var t in activeTimelines)
                t.Update(deltaTime);
            foreach (var b in activeBlends)
                b.Update(deltaTime);
            SystemsManager.Instance.Update(deltaTime);
            // DamageSync and cancellation handlers can be updated as needed
        }

        // Cancel an animation and resolve effects
        public void CancelAnimation(AnimationTimeline timeline, CancellationType type)
        {
            var handler = new AnimationCancellationHandler();
            handler.RequestCancel(type);
            activeCancellations.Add(handler);
            // Remove timeline from active list
            activeTimelines.Remove(timeline);
        }

        // Register feedback for an animation event
        public void RegisterSystems(SystemsEffect effect)
        {
            SystemsManager.Instance.EnqueueSystems(effect);
        }

        // Diagnostics: validate synchronization state
        public bool DiagnoseSync()
        {
            // Example: check for timing discrepancies, missed triggers, etc.
            foreach (var t in activeTimelines)
            {
                // Add more detailed checks as needed
                if (!t.IsPlaying && t.CurrentTime < t.Duration)
                    return false;
            }
            return true;
        }

        // Get status of all active animations
        public List<string> GetAnimationStatus()
        {
            var status = new List<string>();
            foreach (var t in activeTimelines)
                status.Add($"Timeline: {t.CurrentTime}/{t.Duration} (Playing: {t.IsPlaying})");
            foreach (var b in activeBlends)
                status.Add($"Blend: {b.BlendWeight} (Blending: {b.IsBlending})");
            return status;
        }
    }
} 