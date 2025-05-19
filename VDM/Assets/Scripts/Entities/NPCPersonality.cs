using System;
using System.Collections.Generic;
using UnityEngine;

namespace VisualDM.Entities
{
    [Serializable]
    public class PersonalityProfile
    {
        // Core personality traits (0-1 range)
        [Range(0f, 1f)] public float Friendliness;
        [Range(0f, 1f)] public float Aggression;
        [Range(0f, 1f)] public float Curiosity;
        [Range(0f, 1f)] public float Discipline;
        [Range(0f, 1f)] public float Optimism;
        [Range(0f, 1f)] public float Sociability;
        [Range(0f, 1f)] public float Intelligence;

        public PersonalityProfile() { }

        public PersonalityProfile(float friendliness, float aggression, float curiosity, float discipline, float optimism, float sociability, float intelligence)
        {
            Friendliness = Mathf.Clamp01(friendliness);
            Aggression = Mathf.Clamp01(aggression);
            Curiosity = Mathf.Clamp01(curiosity);
            Discipline = Mathf.Clamp01(discipline);
            Optimism = Mathf.Clamp01(optimism);
            Sociability = Mathf.Clamp01(sociability);
            Intelligence = Mathf.Clamp01(intelligence);
        }

        // Compare two profiles for similarity (lower = more similar)
        public float Compare(PersonalityProfile other)
        {
            float diff = 0f;
            diff += Mathf.Abs(Friendliness - other.Friendliness);
            diff += Mathf.Abs(Aggression - other.Aggression);
            diff += Mathf.Abs(Curiosity - other.Curiosity);
            diff += Mathf.Abs(Discipline - other.Discipline);
            diff += Mathf.Abs(Optimism - other.Optimism);
            diff += Mathf.Abs(Sociability - other.Sociability);
            diff += Mathf.Abs(Intelligence - other.Intelligence);
            return diff / 7f;
        }

        // Returns a dictionary of trait names and values
        public Dictionary<string, float> ToDictionary()
        {
            return new Dictionary<string, float>
            {
                {"Friendliness", Friendliness},
                {"Aggression", Aggression},
                {"Curiosity", Curiosity},
                {"Discipline", Discipline},
                {"Optimism", Optimism},
                {"Sociability", Sociability},
                {"Intelligence", Intelligence}
            };
        }
    }
} 