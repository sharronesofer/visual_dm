using System;
using System.Collections.Generic;
using VisualDM.NPC;

namespace VisualDM.AI
{
    /// <summary>
    /// Represents a single rumor in the world, with distributed knowledge among NPCs.
    /// 
    /// SERIALIZATION NOTE:
    /// - For performance, only serialize rumor IDs and essential fields (not full NPC or rumor objects).
    /// - Use lightweight DTOs for save/load if needed.
    /// </summary>
    public class Rumor
    {
        public string CoreContent { get; set; } // The base information of the rumor
        public bool? TruthValue { get; set; } // Nullable, as per Task #663
        public RumorOriginMetadata Origin { get; set; }
        public List<RumorTransformation> TransformationHistory { get; set; } = new();
        // Per-NPC memory: maps NPC unique ID to their memory of this rumor
        public Dictionary<string, RumorMemory> NpcMemories { get; set; } = new();

        // Importance: higher values decay slower (e.g., 0.0 = trivial, 1.0 = critical)
        public float Importance { get; set; } = 0.5f;
    }

    /// <summary>
    /// Metadata about the origin of a rumor.
    /// </summary>
    public class RumorOriginMetadata
    {
        public string OriginNpcId { get; set; }
        public DateTime OriginTimestamp { get; set; }
        public string OriginEventId { get; set; } // Optional: link to the event that spawned the rumor
    }

    /// <summary>
    /// Represents a single transformation (retelling, distortion, etc.) of a rumor.
    /// </summary>
    public class RumorTransformation
    {
        public string NpcId { get; set; }
        public DateTime Timestamp { get; set; }
        public string TransformationType { get; set; } // e.g., "retell", "exaggerate", "clarify"
        public string NewContent { get; set; } // The rumor content after transformation
        public float DistortionLevel { get; set; } // 0.0 (truthful) to 1.0 (max distortion)
    }

    /// <summary>
    /// Represents an NPC's memory of a rumor.
    /// </summary>
    public class RumorMemory
    {
        public DateTime LearnedTimestamp { get; set; }
        public float MemoryStrength { get; set; } // Decays over time
        public bool IsForgotten { get; set; }
        public List<RumorTransformation> Transformations { get; set; } = new();
    }
}