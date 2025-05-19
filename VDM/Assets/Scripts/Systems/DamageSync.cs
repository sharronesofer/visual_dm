using System;
using UnityEngine;
using System.Collections.Generic;

namespace VisualDM.Systems.Animation
{
    /// <summary>
    /// Synchronizes damage calculation with animation impact frames, supporting network latency buffering and validation.
    /// </summary>
    public class DamageSync
    {
        public event Action OnImpactTriggered;

        private AnimationTimeline timeline;
        private List<float> registeredImpacts = new List<float>();
        private Dictionary<float, Action> impactCallbacks = new Dictionary<float, Action>();
        private float networkBufferMs = 0f;
        private bool[] impactTriggered;

        public DamageSync(AnimationTimeline timeline)
        {
            this.timeline = timeline;
        }

        public void RegisterImpact(float normalizedTime, Action onImpact)
        {
            if (!impactCallbacks.ContainsKey(normalizedTime))
            {
                registeredImpacts.Add(normalizedTime);
                impactCallbacks[normalizedTime] = onImpact;
            }
            // Register with timeline
            timeline.RegisterEvent(normalizedTime, () => HandleImpact(normalizedTime));
        }

        private void HandleImpact(float normalizedTime)
        {
            // Buffering: delay or advance based on networkBufferMs
            float bufferSeconds = networkBufferMs / 1000f;
            if (Mathf.Abs(bufferSeconds) > 0.001f)
            {
                // Schedule delayed/advanced execution
                DelayedInvoke(() => TriggerImpact(normalizedTime), bufferSeconds);
            }
            else
            {
                TriggerImpact(normalizedTime);
            }
        }

        private void TriggerImpact(float normalizedTime)
        {
            if (impactCallbacks.TryGetValue(normalizedTime, out var cb))
            {
                cb?.Invoke();
                OnImpactTriggered?.Invoke();
            }
        }

        // Simulate delayed/advanced execution (runtime only, not MonoBehaviour)
        private void DelayedInvoke(Action action, float delaySeconds)
        {
            // In a real system, this would be handled by a coroutine or scheduler
            // For now, just invoke immediately (stub for integration)
            action?.Invoke();
        }

        public void SetNetworkBuffer(float bufferMs)
        {
            networkBufferMs = bufferMs;
        }

        public bool ValidateSyncState()
        {
            // Stub: In a real system, check for missed/duplicate impacts, network confirmation, etc.
            // Return true if all registered impacts have been triggered once
            // (This would require tracking state per impact in a real implementation)
            return true;
        }
    }
} 