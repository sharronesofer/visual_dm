using System;
using UnityEngine;

namespace VisualDM.NPC
{
    public enum MoodState
    {
        Neutral,
        Happy,
        Angry,
        Afraid,
        Curious,
        Sad
    }

    [Serializable]
    public class NPCMood
    {
        public MoodState CurrentMood { get; private set; } = MoodState.Neutral;
        public float MoodIntensity { get; private set; } = 0f; // 0 = baseline, 1 = max
        private float decayRate = 0.05f; // How quickly mood returns to neutral

        public NPCMood() { }

        public void ApplyMood(MoodState newMood, float intensity = 1f)
        {
            if (newMood == CurrentMood)
            {
                MoodIntensity = Mathf.Clamp01(MoodIntensity + intensity * 0.5f);
            }
            else
            {
                CurrentMood = newMood;
                MoodIntensity = Mathf.Clamp01(intensity);
            }
        }

        // Call this per frame or per time step to decay mood
        public void DecayMood(float deltaTime)
        {
            if (CurrentMood == MoodState.Neutral)
                return;
            MoodIntensity -= decayRate * deltaTime;
            if (MoodIntensity <= 0f)
            {
                MoodIntensity = 0f;
                CurrentMood = MoodState.Neutral;
            }
        }

        // For debugging
        public override string ToString()
        {
            return $"{CurrentMood} ({MoodIntensity:0.00})";
        }
    }
} 