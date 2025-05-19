using System;
using UnityEngine;

namespace VisualDM.AI
{
    /// <summary>
    /// Represents a game event that can be transformed into a rumor.
    /// </summary>
    [Serializable]
    public class RumorEvent
    {
        public string EventType; // e.g., "crime", "heroic_act", "gossip"
        public string[] Actors; // NPC or player IDs involved
        public string Location; // Location name or ID
        public DateTime Timestamp; // When the event occurred
        public string Context; // Additional context or description
        public string SourceNpcId; // (Optional) NPC who witnessed or originated the event
        public string TargetNpcId; // (Optional) NPC affected by the event
        // Add more fields as needed for narrative context
    }
}