using System;
using System.Collections.Generic;
using UnityEngine;
using System.Linq;

namespace VDM.Systems {
    /// <summary>
    /// Represents the type of memory: Core (permanent) or Regular (subject to decay).
    /// </summary>
    public enum MemoryType { Core, Regular }

    /// <summary>
    /// Represents a single memory instance with decay mechanics and metadata.
    /// </summary>
    [Serializable]
    public class Memory {
        /// <summary>Unique identifier for the memory.</summary>
        public string Id;
        /// <summary>Timestamp when the memory was created.</summary>
        public DateTime Timestamp;
        /// <summary>Initial importance of the memory.</summary>
        public float Importance;
        /// <summary>Textual content of the memory.</summary>
        public string Content;
        /// <summary>Entities associated with this memory.</summary>
        public List<string> AssociatedEntities;
        /// <summary>Decay rate per second for regular memories.</summary>
        public float DecayRate;
        /// <summary>Tags for categorization and query.</summary>
        public List<string> Tags;
        /// <summary>Type of memory (Core or Regular).</summary>
        public MemoryType Type;
        /// <summary>Current importance after decay.</summary>
        public float CurrentImportance;
        /// <summary>Emotional impact of the memory (higher = more memorable, decays slower).</summary>
        public float EmotionalImpact;
        /// <summary>Reliability of the source (0-1, affects recall and decay).</summary>
        public float SourceReliability;
        /// <summary>Probability this memory is a false memory (0-1, used for recall distortion).</summary>
        public float FalseMemoryProbability;
        /// <summary>
        /// Constructs a new Memory instance with extended metadata.
        /// </summary>
        public Memory(string content, float importance, List<string> entities, float decayRate, List<string> tags, MemoryType type, float emotionalImpact = 0f, float sourceReliability = 1f, float falseMemoryProbability = 0f) {
            Id = Guid.NewGuid().ToString();
            Timestamp = DateTime.UtcNow;
            Importance = importance;
            Content = content;
            AssociatedEntities = entities ?? new List<string>();
            DecayRate = decayRate;
            Tags = tags ?? new List<string>();
            Type = type;
            CurrentImportance = importance;
            EmotionalImpact = emotionalImpact;
            SourceReliability = sourceReliability;
            FalseMemoryProbability = falseMemoryProbability;
        }
        /// <summary>
        /// Applies decay to the memory's importance over time.
        /// </summary>
        public void Decay(float deltaTime) {
            if (Type == MemoryType.Core) return;
            CurrentImportance = Mathf.Max(0, CurrentImportance - DecayRate * deltaTime);
        }
        /// <summary>
        /// Determines if the memory is expired based on a threshold.
        /// </summary>
        public bool IsExpired(float threshold) {
            return Type == MemoryType.Regular && CurrentImportance < threshold;
        }
    }

    /// <summary>
    /// Manages a collection of memories, including decay, event emission, and queries.
    /// </summary>
    public class MemoryManager : MonoBehaviour {
        /// <summary>Event triggered for memory lifecycle changes (created, decayed, reinforced).</summary>
        public event Action<Memory, string> OnMemoryEvent;
        private List<Memory> memories = new List<Memory>();
        /// <summary>Importance threshold below which regular memories are pruned.</summary>
        public float DecayThreshold = 0.1f;
        /// <summary>
        /// Adds a new memory and emits a creation event.
        /// </summary>
        public void AddMemory(Memory memory) {
            memories.Add(memory);
            OnMemoryEvent?.Invoke(memory, "created");
            MemoryEventDispatcher.Instance.Dispatch(memory, "created");
        }
        /// <summary>
        /// Overload for legacy calls (no new fields)
        /// </summary>
        public void AddMemory(string content, float importance, List<string> entities, float decayRate, List<string> tags, MemoryType type) {
            AddMemory(new Memory(content, importance, entities, decayRate, tags, type));
        }
        /// <summary>
        /// Overload for full metadata
        /// </summary>
        public void AddMemory(string content, float importance, List<string> entities, float decayRate, List<string> tags, MemoryType type, float emotionalImpact, float sourceReliability, float falseMemoryProbability) {
            AddMemory(new Memory(content, importance, entities, decayRate, tags, type, emotionalImpact, sourceReliability, falseMemoryProbability));
        }
        /// <summary>
        /// Applies decay to all memories and emits events for those that cross the threshold.
        /// </summary>
        public void DecayMemories(float deltaTime) {
            foreach (var mem in memories) {
                float before = mem.CurrentImportance;
                mem.Decay(deltaTime);
                if (before >= DecayThreshold && mem.CurrentImportance < DecayThreshold) {
                    OnMemoryEvent?.Invoke(mem, "decayed");
                    MemoryEventDispatcher.Instance.Dispatch(mem, "decayed");
                }
            }
            PruneExpired();
        }
        /// <summary>
        /// Removes expired regular memories from the collection.
        /// </summary>
        public void PruneExpired() {
            memories.RemoveAll(m => m.IsExpired(DecayThreshold));
        }
        /// <summary>
        /// Queries memories using a custom predicate.
        /// </summary>
        public IEnumerable<Memory> Query(Func<Memory, bool> predicate) {
            return memories.Where(predicate);
        }
        /// <summary>
        /// Queries memories by tag.
        /// </summary>
        public IEnumerable<Memory> QueryByTag(string tag) {
            return memories.Where(m => m.Tags.Contains(tag));
        }
        /// <summary>
        /// Queries memories by importance range.
        /// </summary>
        public IEnumerable<Memory> QueryByImportance(float min, float max) {
            return memories.Where(m => m.CurrentImportance >= min && m.CurrentImportance <= max);
        }
        /// <summary>
        /// Queries memories by associated entity.
        /// </summary>
        public IEnumerable<Memory> QueryByEntity(string entityId) {
            return memories.Where(m => m.AssociatedEntities.Contains(entityId));
        }
        /// <summary>
        /// Reinforces a regular memory, increasing its importance and emitting an event.
        /// </summary>
        public void ReinforceMemory(string id, float amount) {
            var mem = memories.FirstOrDefault(m => m.Id == id);
            if (mem != null && mem.Type == MemoryType.Regular) {
                mem.CurrentImportance = Mathf.Min(mem.Importance, mem.CurrentImportance + amount);
                OnMemoryEvent?.Invoke(mem, "reinforced");
                MemoryEventDispatcher.Instance.Dispatch(mem, "reinforced");
            }
        }
        /// <summary>
        /// Serializes all memories to a JSON string.
        /// </summary>
        public string Serialize() {
            return JsonUtility.ToJson(new MemoryListWrapper { Memories = memories });
        }
        /// <summary>
        /// Deserializes memories from a JSON string.
        /// </summary>
        public void Deserialize(string json) {
            var wrapper = JsonUtility.FromJson<MemoryListWrapper>(json);
            memories = wrapper?.Memories ?? new List<Memory>();
        }
        [Serializable]
        private class MemoryListWrapper {
            public List<Memory> Memories;
        }
    }
} 