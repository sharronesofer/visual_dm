using System;
using System.Collections.Generic;
using UnityEngine;
using VDM.Systems.Events;

namespace VDM.Systems.Memory
{
    public enum MemoryType
    {
        Core,
        Event,
        Relationship,
        Achievement,
        Trauma,
        Rumor,
        Knowledge,
        Location,
        Item,
        Quest,
        Motif,
        Faction,
        Combat,
        Loss,
        Discovery
    }

    // Canonical memory types:
    // Core, Event, Relationship, Achievement, Trauma, Rumor, Knowledge, Location, Item, Quest, Motif, Faction, Combat, Loss, Discovery
    [Serializable]
    public class Memory
    {
        public MemoryType Type;
        public string Description;
        public float Relevance; // 0.0 (forgotten) to 1.0 (vivid)
        public bool IsCore;
        public DateTime CreatedAt;
        public DateTime LastReinforcedAt;
        public string Category;
        // Extend with additional fields as needed
    }

    public class MemoryManager : MonoBehaviour
    {
        public List<Memory> Memories { get; private set; } = new List<Memory>();
        private const float DecayRate = 0.01f; // per day
        public event Action<Memory> OnMemoryCreated;
        public event Action<Memory> OnMemoryReinforced;
        public event Action<Memory> OnMemoryDeleted;

        public void AddMemory(Memory memory)
        {
            Memories.Add(memory);
            OnMemoryCreated?.Invoke(memory);
            var evt = new MemoryCreatedEvent { Description = memory.Description };
            EventDispatcher.Instance.Dispatch(evt);
        }

        public void ReinforceMemory(Memory memory, float amount = 0.2f)
        {
            memory.Relevance = Mathf.Clamp01(memory.Relevance + amount);
            memory.LastReinforcedAt = DateTime.UtcNow;
            OnMemoryReinforced?.Invoke(memory);
            var evt = new MemoryReinforcedEvent { Description = memory.Description };
            EventDispatcher.Instance.Dispatch(evt);
        }

        public void DecayMemories()
        {
            for (int i = Memories.Count - 1; i >= 0; i--)
            {
                var mem = Memories[i];
                if (!mem.IsCore)
                {
                    mem.Relevance = Mathf.Max(0f, mem.Relevance - DecayRate);
                    if (mem.Relevance <= 0f)
                    {
                        OnMemoryDeleted?.Invoke(mem);
                        var evt = new MemoryDeletedEvent { Description = mem.Description };
                        EventDispatcher.Instance.Dispatch(evt);
                        Memories.RemoveAt(i);
                    }
                }
            }
        }

        // Narrative hook: get current memory context for GPT or narrative systems
        public string GetMemoryContext()
        {
            if (Memories.Count == 0) return "No significant memories.";
            var mem = Memories[UnityEngine.Random.Range(0, Memories.Count)];
            return $"Memory: {mem.Type} - {mem.Description} (Relevance: {mem.Relevance:F2})";
        }
    }
} 