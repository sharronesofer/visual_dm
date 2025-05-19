using System;
using System.Collections.Generic;
using UnityEngine;

namespace VDM.NPC.MotifSystem
{
    public enum MotifScope { Global, Regional, Local }

    [Serializable]
    public class Motif
    {
        public string Name { get; private set; }
        public float Intensity { get; private set; }
        public MotifScope Scope { get; private set; }
        public float Duration { get; private set; } // in seconds
        public int Priority { get; private set; }
        public List<string> Tags { get; private set; }
        public DateTime StartTime { get; private set; }
        public Vector2 Center { get; private set; } // For regional/local
        public float Radius { get; private set; } // For regional/local

        public Motif(string name, float intensity, MotifScope scope, float duration, int priority, List<string> tags, DateTime startTime, Vector2 center, float radius)
        {
            Name = name;
            Intensity = intensity;
            Scope = scope;
            Duration = duration;
            Priority = priority;
            Tags = tags ?? new List<string>();
            StartTime = startTime;
            Center = center;
            Radius = radius;
        }

        public bool IsActive()
        {
            if (Duration < 0) return true; // Permanent motif
            return (DateTime.UtcNow - StartTime).TotalSeconds < Duration;
        }

        public bool IsLocationAffected(Vector2 location)
        {
            if (Scope == MotifScope.Global) return true;
            if (Scope == MotifScope.Regional || Scope == MotifScope.Local)
            {
                return Vector2.Distance(location, Center) <= Radius;
            }
            return false;
        }

        // Serialization to JSON
        public string Serialize()
        {
            return JsonUtility.ToJson(this);
        }

        // Deserialization from JSON
        public static Motif Deserialize(string json)
        {
            return JsonUtility.FromJson<Motif>(json);
        }
    }
} 