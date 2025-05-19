using System;
using System.Collections.Generic;
using UnityEngine;

namespace VisualDM.Systems.Animation
{
    [CreateAssetMenu(fileName = "AnimationEffectConfig", menuName = "VisualDM/Animation/EffectConfig", order = 1)]
    public class AnimationEffectConfig : ScriptableObject
    {
        public string AnimationName;
        public List<EffectTrigger> Triggers = new List<EffectTrigger>();

        [Serializable]
        public struct EffectTrigger
        {
            [Range(0f, 1f)] public float NormalizedTime;
            public string EffectId;
        }

        // Validation method
        public bool Validate(out string error)
        {
            var seen = new HashSet<float>();
            foreach (var trig in Triggers)
            {
                if (trig.NormalizedTime < 0f || trig.NormalizedTime > 1f)
                {
                    error = $"Trigger time {trig.NormalizedTime} out of bounds in {AnimationName}";
                    return false;
                }
                if (string.IsNullOrEmpty(trig.EffectId))
                {
                    error = $"Missing EffectId at {trig.NormalizedTime} in {AnimationName}";
                    return false;
                }
                if (!seen.Add(trig.NormalizedTime))
                {
                    error = $"Duplicate trigger time {trig.NormalizedTime} in {AnimationName}";
                    return false;
                }
            }
            error = null;
            return true;
        }

        // Static loader for all configs in Resources/AnimationConfigs
        private static List<AnimationEffectConfig> _allConfigs;
        public static List<AnimationEffectConfig> GetAllConfigs()
        {
            if (_allConfigs == null)
            {
                _allConfigs = new List<AnimationEffectConfig>(Resources.LoadAll<AnimationEffectConfig>("AnimationConfigs"));
            }
            return _allConfigs;
        }

        public static List<EffectTrigger> GetEffectsForAnimation(string animationName)
        {
            foreach (var config in GetAllConfigs())
            {
                if (config.AnimationName == animationName)
                    return config.Triggers;
            }
            return new List<EffectTrigger>();
        }

        // Runtime batch config generator (for tests or procedural setup)
        public static AnimationEffectConfig CreateConfig(string animationName, List<EffectTrigger> triggers)
        {
            var config = ScriptableObject.CreateInstance<AnimationEffectConfig>();
            config.AnimationName = animationName;
            config.Triggers = new List<EffectTrigger>(triggers);
            return config;
        }
    }
} 