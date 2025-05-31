using System;

namespace VDM.Infrastructure.Core.Core.Events
{
    /// <summary>
    /// Base class for all game events
    /// </summary>
    public abstract class GameEvent
    {
        /// <summary>
        /// Timestamp when the event was created
        /// </summary>
        public DateTime Timestamp { get; private set; } = DateTime.UtcNow;

        /// <summary>
        /// Event type identifier
        /// </summary>
        public virtual string EventType => GetType().Name;

        /// <summary>
        /// Unique event ID
        /// </summary>
        public string EventId { get; private set; } = Guid.NewGuid().ToString();
    }

    /// <summary>
    /// Character creation event
    /// </summary>
    public class CharacterCreatedEvent : GameEvent
    {
        public CharacterDTO Character { get; set; }
    }

    /// <summary>
    /// Character deletion event
    /// </summary>
    public class CharacterDeletedEvent : GameEvent
    {
        public string CharacterId { get; set; }
        public string CharacterName { get; set; }
    }

    /// <summary>
    /// Character update event
    /// </summary>
    public class CharacterUpdatedEvent : GameEvent
    {
        public string CharacterId { get; set; }
        public string CharacterName { get; set; }
        public string[] UpdatedFields { get; set; }
    }

    /// <summary>
    /// Simple DTO for character information
    /// </summary>
    [Serializable]
    public class CharacterDTO
    {
        public string Id { get; set; } = string.Empty;
        public string Name { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
    }
} 