using System;
using System.Collections.Generic;

namespace VisualDM.Systems.Rivalry
{
    /// <summary>
    /// RelationshipMemory stores significant events and interactions for rival/nemesis systems.
    /// Used for memory integration, event tracking, and narrative hooks.
    /// </summary>
    [Serializable]
    public class RelationshipMemory
    {
        public DateTime Timestamp;
        public string EventType;
        public string Description;
        public float Impact;
        public RelationshipMemory(DateTime timestamp, string eventType, string description, float impact)
        {
            Timestamp = timestamp;
            EventType = eventType;
            Description = description;
            Impact = impact;
        }
    }
}