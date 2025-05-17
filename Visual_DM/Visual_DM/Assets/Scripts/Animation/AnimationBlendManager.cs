using System;
using UnityEngine;

namespace VisualDM.Animation
{
    /// <summary>
    /// Manages blending and transitions between AnimationTimeline instances.
    /// </summary>
    public class AnimationBlendManager
    {
        public event Action OnBlendComplete;

        private AnimationTimeline fromTimeline;
        private AnimationTimeline toTimeline;
        private float blendDuration;
        private float blendElapsed;
        private bool isBlending;

        // Blend weight: 0.0 = fromTimeline, 1.0 = toTimeline
        public float BlendWeight { get; private set; }
        public bool IsBlending => isBlending;
        public AnimationTimeline CurrentTimeline => (BlendWeight < 0.5f) ? fromTimeline : toTimeline;

        public void StartBlend(AnimationTimeline from, AnimationTimeline to, float duration)
        {
            if (duration <= 0f) duration = 0.01f;
            fromTimeline = from;
            toTimeline = to;
            blendDuration = duration;
            blendElapsed = 0f;
            isBlending = true;
            BlendWeight = 0f;
        }

        public void Update(float deltaTime)
        {
            if (!isBlending) return;
            blendElapsed += deltaTime;
            BlendWeight = Mathf.Clamp01(blendElapsed / blendDuration);

            // Update both timelines
            fromTimeline?.Update(deltaTime);
            toTimeline?.Update(deltaTime);

            // Event/effect triggering logic:
            // - By default, trigger events from the dominant timeline (higher weight)
            // - Optionally, could trigger both with weighted intensity (not implemented here)

            if (blendElapsed >= blendDuration)
            {
                isBlending = false;
                BlendWeight = 1f;
                OnBlendComplete?.Invoke();
            }
        }

        public void CancelBlend()
        {
            isBlending = false;
            BlendWeight = 1f;
            // Optionally, handle pending effects from fromTimeline (trigger/cancel/transfer)
        }

        public AnimationTimeline GetCurrentTimeline()
        {
            return (BlendWeight < 0.5f) ? fromTimeline : toTimeline;
        }
    }
} 