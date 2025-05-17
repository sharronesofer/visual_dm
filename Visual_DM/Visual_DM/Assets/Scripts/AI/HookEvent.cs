using System;
using System.Collections.Generic;

namespace AI
{
    public enum HookEventType { Combat, Exploration, Collection, Custom }
    public enum HookPriority { Low, Medium, High, Critical }

    [Serializable]
    public class HookEvent
    {
        public HookEventType EventType { get; set; }
        public HookPriority Priority { get; set; }
        public Dictionary<string, object> PlayerContext { get; set; } = new Dictionary<string, object>();
        public object Payload { get; set; }
        public DateTime Timestamp { get; set; } = DateTime.UtcNow;

        public HookEvent(HookEventType eventType, HookPriority priority, object payload = null)
        {
            EventType = eventType;
            Priority = priority;
            Payload = payload;
        }
    }
} 