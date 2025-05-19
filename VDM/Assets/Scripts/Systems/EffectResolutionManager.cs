using System;
using System.Collections.Generic;

namespace VisualDM.Systems.Animation
{
    public enum EffectType
    {
        Damage,
        Status,
        Custom
    }

    public enum ResolutionPolicy
    {
        ApplyImmediately,
        ScaleByProgress,
        Cancel
    }

    public class PendingEffect
    {
        public EffectType Type;
        public Action Callback;
        public float Progress;
    }

    /// <summary>
    /// Tracks and resolves pending gameplay effects on animation cancellation.
    /// </summary>
    public class EffectResolutionManager
    {
        private static EffectResolutionManager _instance;
        public static EffectResolutionManager Instance => _instance ?? (_instance = new EffectResolutionManager());

        private readonly List<PendingEffect> pendingEffects = new List<PendingEffect>();
        private readonly Dictionary<EffectType, ResolutionPolicy> policies = new Dictionary<EffectType, ResolutionPolicy>
        {
            { EffectType.Damage, ResolutionPolicy.ApplyImmediately },
            { EffectType.Status, ResolutionPolicy.ScaleByProgress },
            { EffectType.Custom, ResolutionPolicy.Cancel }
        };

        public void RegisterPendingEffect(EffectType type, Action effect, float progress)
        {
            pendingEffects.Add(new PendingEffect { Type = type, Callback = effect, Progress = progress });
        }

        public void SetResolutionPolicy(EffectType type, ResolutionPolicy policy)
        {
            policies[type] = policy;
        }

        public void ResolveEffectsOnCancel(CancellationType cancelType)
        {
            foreach (var pe in pendingEffects)
            {
                var policy = policies.TryGetValue(pe.Type, out var p) ? p : ResolutionPolicy.Cancel;
                switch (policy)
                {
                    case ResolutionPolicy.ApplyImmediately:
                        pe.Callback?.Invoke();
                        break;
                    case ResolutionPolicy.ScaleByProgress:
                        if (pe.Progress > 0.5f) pe.Callback?.Invoke();
                        break;
                    case ResolutionPolicy.Cancel:
                    default:
                        // Do nothing
                        break;
                }
            }
            pendingEffects.Clear();
        }

        public bool ValidateState()
        {
            // Stub: In a real system, check for consistency after effect resolution
            return pendingEffects.Count == 0;
        }
    }
} 