using System;


namespace VDM.Systems.Events.Models
{
    /// <summary>
    /// Core interface for all event objects in the system.
    /// Aligned with backend events system architecture.
    /// </summary>
    public interface IEvent
    {
        /// <summary>
        /// Unique identifier for this specific event instance
        /// </summary>
        string EventId { get; }
        
        /// <summary>
        /// Type identifier for the event category
        /// </summary>
        string EventType { get; }
        
        /// <summary>
        /// Timestamp when the event was created
        /// </summary>
        DateTime Timestamp { get; }
        
        /// <summary>
        /// Source system or component that generated the event
        /// </summary>
        string Source { get; }
        
        /// <summary>
        /// Priority level for event processing
        /// </summary>
        EventPriority Priority { get; }
    }
    
    /// <summary>
    /// Event priority levels for processing order
    /// </summary>
    public enum EventPriority
    {
        Low = 0,
        Normal = 1,
        High = 2,
        Critical = 3
    }
} 