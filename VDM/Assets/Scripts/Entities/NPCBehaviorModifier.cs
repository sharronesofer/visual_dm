using System;

namespace VisualDM.Entities
{
    public class NPCBehaviorModifier
    {
        private readonly PersonalityProfile _personality;
        private readonly NPCMood _mood;

        public NPCBehaviorModifier(PersonalityProfile personality, NPCMood mood)
        {
            _personality = personality;
            _mood = mood;
        }

        // Example: Calculate aggression weight (0-1)
        public float GetAggressionWeight()
        {
            float baseAggression = _personality.Aggression;
            float moodBoost = 0f;
            if (_mood.CurrentMood == MoodState.Angry)
                moodBoost = _mood.MoodIntensity * 0.5f;
            return Clamp01(baseAggression + moodBoost);
        }

        // Example: Calculate sociability weight (0-1)
        public float GetSociabilityWeight()
        {
            float baseSociability = _personality.Sociability;
            float moodBoost = 0f;
            if (_mood.CurrentMood == MoodState.Happy)
                moodBoost = _mood.MoodIntensity * 0.3f;
            if (_mood.CurrentMood == MoodState.Sad)
                moodBoost = -_mood.MoodIntensity * 0.2f;
            return Clamp01(baseSociability + moodBoost);
        }

        // Example: Calculate curiosity weight (0-1)
        public float GetCuriosityWeight()
        {
            float baseCuriosity = _personality.Curiosity;
            float moodBoost = 0f;
            if (_mood.CurrentMood == MoodState.Curious)
                moodBoost = _mood.MoodIntensity * 0.4f;
            return Clamp01(baseCuriosity + moodBoost);
        }

        // Add more behavior weights as needed (discipline, optimism, etc.)

        private float Clamp01(float value) => Math.Max(0f, Math.Min(1f, value));
    }
} 