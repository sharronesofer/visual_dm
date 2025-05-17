using System;
using System.Collections.Generic;

namespace Visual_DM.WorldState
{
    // Represents a causality event between world state and arcs
    public class CausalityEvent
    {
        public string SourceId { get; private set; } // e.g., arc or system
        public string TargetProperty { get; private set; }
        public DateTime Timestamp { get; private set; }
        public int Priority { get; private set; }
        public int Depth { get; set; } // For dampening/cascade control

        public CausalityEvent(string sourceId, string targetProperty, int priority, int depth = 0)
        {
            SourceId = sourceId;
            TargetProperty = targetProperty;
            Priority = priority;
            Timestamp = DateTime.UtcNow;
            Depth = depth;
        }
    }

    // Manages causality tracking and feedback loop prevention
    public class WorldStateCausalityManager
    {
        private const int MaxCascadeDepth = 5; // Prevent runaway cascades
        private readonly HashSet<string> _activeEvents = new HashSet<string>();
        private readonly Queue<CausalityEvent> _eventQueue = new Queue<CausalityEvent>();

        private static WorldStateCausalityManager _instance;
        public static WorldStateCausalityManager Instance => _instance ?? (_instance = new WorldStateCausalityManager());

        private WorldStateCausalityManager() { }

        // Enqueue a world state change event
        public void EnqueueEvent(CausalityEvent evt)
        {
            if (evt.Depth > MaxCascadeDepth)
                return; // Dampening: ignore deep cascades
            string eventKey = GetEventKey(evt);
            if (_activeEvents.Contains(eventKey))
                return; // Prevent infinite loop
            _eventQueue.Enqueue(evt);
        }

        // Process queued events by priority
        public void ProcessEvents(Action<CausalityEvent> handler)
        {
            var sortedEvents = new List<CausalityEvent>(_eventQueue);
            sortedEvents.Sort((a, b) => b.Priority.CompareTo(a.Priority));
            _eventQueue.Clear();
            foreach (var evt in sortedEvents)
            {
                string eventKey = GetEventKey(evt);
                if (_activeEvents.Contains(eventKey))
                    continue;
                _activeEvents.Add(eventKey);
                handler(evt);
                _activeEvents.Remove(eventKey);
            }
        }

        private string GetEventKey(CausalityEvent evt)
        {
            return $"{evt.SourceId}:{evt.TargetProperty}";
        }
    }
}