using System;
using System.Collections.Generic;
using System.Linq;

namespace VDM.Systems {
    public class MemoryQuery {
        public string EntityId;
        public DateTime? StartTime;
        public DateTime? EndTime;
        public float? MinImportance;
        public float? MaxImportance;
        public List<string> Tags;
        public MemoryType? Type;

        public IEnumerable<Memory> Execute(MemoryManager manager) {
            return manager.Query(m =>
                (string.IsNullOrEmpty(EntityId) || m.AssociatedEntities.Contains(EntityId)) &&
                (!StartTime.HasValue || m.Timestamp >= StartTime.Value) &&
                (!EndTime.HasValue || m.Timestamp <= EndTime.Value) &&
                (!MinImportance.HasValue || m.CurrentImportance >= MinImportance.Value) &&
                (!MaxImportance.HasValue || m.CurrentImportance <= MaxImportance.Value) &&
                (Tags == null || Tags.Count == 0 || Tags.Any(tag => m.Tags.Contains(tag))) &&
                (!Type.HasValue || m.Type == Type.Value)
            );
        }
    }
} 