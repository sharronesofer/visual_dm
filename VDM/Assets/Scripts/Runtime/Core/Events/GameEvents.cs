using System;

namespace VDM.Runtime.Core.Events
{
    /// <summary>
    /// Character-related events
    /// </summary>
    [Serializable]
    public class CharacterCreatedEvent
    {
        public string CharacterId { get; set; }
        public string CharacterName { get; set; }
        public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    }
    
    [Serializable]
    public class CharacterDeletedEvent
    {
        public string CharacterId { get; set; }
        public string CharacterName { get; set; }
        public DateTime DeletedAt { get; set; } = DateTime.UtcNow;
    }
    
    [Serializable]
    public class CharacterUpdatedEvent
    {
        public string CharacterId { get; set; }
        public string CharacterName { get; set; }
        public string[] UpdatedFields { get; set; }
        public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;
    }
} 