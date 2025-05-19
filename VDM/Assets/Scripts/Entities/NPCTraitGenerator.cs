using System;
using UnityEngine;

namespace VisualDM.Entities
{
    public static class NPCTraitGenerator
    {
        // Generate a random personality profile (optionally seeded)
        public static PersonalityProfile GenerateRandomProfile(System.Random rng = null)
        {
            rng = rng ?? new System.Random();
            return new PersonalityProfile(
                (float)rng.NextDouble(),
                (float)rng.NextDouble(),
                (float)rng.NextDouble(),
                (float)rng.NextDouble(),
                (float)rng.NextDouble(),
                (float)rng.NextDouble(),
                (float)rng.NextDouble()
            );
        }

        // Generate a profile based on a template, with optional variance
        public static PersonalityProfile GenerateFromTemplate(INPCTemplate template, float variance = 0.1f, System.Random rng = null)
        {
            rng = rng ?? new System.Random();
            var baseProfile = template.GetDefaultPersonality();
            return new PersonalityProfile(
                ClampWithVariance(baseProfile.Friendliness, variance, rng),
                ClampWithVariance(baseProfile.Aggression, variance, rng),
                ClampWithVariance(baseProfile.Curiosity, variance, rng),
                ClampWithVariance(baseProfile.Discipline, variance, rng),
                ClampWithVariance(baseProfile.Optimism, variance, rng),
                ClampWithVariance(baseProfile.Sociability, variance, rng),
                ClampWithVariance(baseProfile.Intelligence, variance, rng)
            );
        }

        private static float ClampWithVariance(float value, float variance, System.Random rng)
        {
            float delta = ((float)rng.NextDouble() * 2f - 1f) * variance;
            return Mathf.Clamp01(value + delta);
        }
    }
} 