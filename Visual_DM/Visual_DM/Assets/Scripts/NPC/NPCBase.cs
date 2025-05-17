using System;
using UnityEngine;

namespace VisualDM.NPC
{
    public class NPCBase : MonoBehaviour
    {
        public string NPCName;
        public PersonalityProfile Personality { get; private set; }
        public NPCMood Mood { get; private set; }
        private NPCBehaviorModifier _behaviorModifier;

        // Initialization with random or template-based personality
        public void Initialize(INPCTemplate template = null, System.Random rng = null)
        {
            if (template != null)
                Personality = NPCTraitGenerator.GenerateFromTemplate(template, 0.1f, rng);
            else
                Personality = NPCTraitGenerator.GenerateRandomProfile(rng);
            Mood = new NPCMood();
            _behaviorModifier = new NPCBehaviorModifier(Personality, Mood);
        }

        // Expose behavior weights
        public float GetAggressionWeight() => _behaviorModifier.GetAggressionWeight();
        public float GetSociabilityWeight() => _behaviorModifier.GetSociabilityWeight();
        public float GetCuriosityWeight() => _behaviorModifier.GetCuriosityWeight();
        // Add more as needed

        // Event-driven mood change
        public void OnEventAffectingMood(MoodState mood, float intensity = 1f)
        {
            Mood.ApplyMood(mood, intensity);
        }

        // Call this in Update or via a manager to decay mood
        public void UpdateMood(float deltaTime)
        {
            Mood.DecayMood(deltaTime);
        }

        // For debugging
        public override string ToString()
        {
            return $"NPC: {NPCName}, Personality: {Personality.ToDictionary()}, Mood: {Mood}";
        }
    }
} 