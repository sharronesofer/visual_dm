using System;
using System.Collections.Generic;

namespace VisualDM.Systems.FeatHistory
{
    [Serializable]
    public class FeatAchievementEvent
    {
        public string Id { get; set; } // Unique event ID
        public string CharacterId { get; set; } // Reference to character
        public string FeatId { get; set; } // Reference to feat
        public DateTime Timestamp { get; set; } // When the feat was acquired
        public int CharacterLevel { get; set; } // Level at acquisition
        public CharacterSnapshot StatsSnapshot { get; set; } // Character stats at acquisition
        public string Context { get; set; } // Contextual info (JSON or string)
    }
} 