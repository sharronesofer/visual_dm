using System;
using UnityEngine;


namespace VDM.Runtime.Events.Models
{
    /// <summary>
    /// Base implementation for all events in the system.
    /// Provides common functionality and properties.
    /// </summary>
    [Serializable]
    public abstract class BaseEvent : IEvent
    {
        [SerializeField] private string _eventId;
        [SerializeField] private string _eventType;
        [SerializeField] private DateTime _timestamp;
        [SerializeField] private string _source;
        [SerializeField] private EventPriority _priority;

        /// <summary>
        /// Unique identifier for this specific event instance
        /// </summary>
        public string EventId => _eventId;

        /// <summary>
        /// Type identifier for the event category
        /// </summary>
        public string EventType => _eventType;

        /// <summary>
        /// Timestamp when the event was created
        /// </summary>
        public DateTime Timestamp => _timestamp;

        /// <summary>
        /// Source system or component that generated the event
        /// </summary>
        public string Source => _source;

        /// <summary>
        /// Priority level for event processing
        /// </summary>
        public EventPriority Priority => _priority;

        /// <summary>
        /// Initialize base event properties
        /// </summary>
        /// <param name="eventType">Type of the event</param>
        /// <param name="source">Source system generating the event</param>
        /// <param name="priority">Processing priority</param>
        protected BaseEvent(string eventType, string source = null, EventPriority priority = EventPriority.Normal)
        {
            _eventId = Guid.NewGuid().ToString();
            _eventType = eventType;
            _timestamp = DateTime.UtcNow;
            _source = source ?? "Unknown";
            _priority = priority;
        }

        /// <summary>
        /// Constructor for deserialization
        /// </summary>
        protected BaseEvent()
        {
            // For Unity serialization
        }

        public override string ToString()
        {
            return $"[{EventType}] {EventId} from {Source} at {Timestamp:yyyy-MM-dd HH:mm:ss}";
        }
    }
} 