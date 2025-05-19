using System.Collections.Generic;

namespace VDM.Systems {
    public static class MemoryIntegrationPoints {
        public static void RecordFactionEvent(MemoryManager manager, string factionId, string eventDescription, float importance, List<string> tags) {
            manager.AddMemory(eventDescription, importance, new List<string> { factionId }, 0.05f, tags, MemoryType.Regular, 0.5f, 1.0f, 0.0f);
        }
        public static void RecordPOIStateChange(MemoryManager manager, string poiId, string stateDescription, float importance, List<string> tags) {
            manager.AddMemory(stateDescription, importance, new List<string> { poiId }, 0.03f, tags, MemoryType.Regular, 0.3f, 1.0f, 0.0f);
        }
        public static void RecordTensionWarEvent(MemoryManager manager, string factionA, string factionB, string eventDescription, float importance, List<string> tags) {
            manager.AddMemory(eventDescription, importance, new List<string> { factionA, factionB }, 0.07f, tags, MemoryType.Regular, 0.8f, 0.8f, 0.0f);
        }
    }
} 