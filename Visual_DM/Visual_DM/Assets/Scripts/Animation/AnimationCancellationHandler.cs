using System;
using System.Collections.Generic;

namespace VisualDM.Animation
{
    public enum CancellationType
    {
        Immediate,
        Blended,
        Recovery
    }

    /// <summary>
    /// Handles animation cancellation, transition states, and pending effect resolution.
    /// </summary>
    public class AnimationCancellationHandler
    {
        public event Action<CancellationType> OnCancelled;

        private List<(Action effect, float progress)> pendingEffects = new List<(Action, float)>();
        private bool isCancelling = false;
        private CancellationType currentType;

        public void RequestCancel(CancellationType type)
        {
            if (isCancelling) return;
            isCancelling = true;
            currentType = type;
            // Handle transition state logic here (stub)
            // For Immediate: stop animation, resolve effects now
            // For Blended: start blend-out, resolve effects at end
            // For Recovery: play recovery anim, resolve effects after
            ResolvePendingEffects();
            OnCancelled?.Invoke(type);
            isCancelling = false;
        }

        public void RegisterPendingEffect(Action effect, float progress)
        {
            pendingEffects.Add((effect, progress));
        }

        public void ResolvePendingEffects()
        {
            foreach (var (effect, progress) in pendingEffects)
            {
                // Policy: apply immediately, scale by progress, or cancel
                // For now, apply immediately if progress > 0.5, else cancel
                if (progress > 0.5f)
                    effect?.Invoke();
                // else: skip/cancel
            }
            pendingEffects.Clear();
        }
    }
} 