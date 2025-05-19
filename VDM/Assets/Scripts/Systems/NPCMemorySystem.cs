using System;
using System.Collections.Generic;
using UnityEngine;
using VisualDM.Systems.EventSystem;
using VDM.Systems;
using VDM.NPC.MotifSystem;
using VisualDM.Entities;
using VisualDM.Systems.Rivalry;

namespace VisualDM.Systems
{
    /// <summary>
    /// Centralized, modular NPC Memory System for runtime-only use.
    /// Manages per-NPC memories, decay, recall, event emission, and integration with Rumor, Motif, and Relationship systems.
    /// </summary>
    public class NPCMemorySystem : MonoBehaviour
    {
        public static NPCMemorySystem Instance { get; private set; }

        // Per-NPC memory managers
        private readonly Dictionary<string, MemoryManager> _npcMemoryManagers = new();
        // Configurable decay parameters
        [Header("Memory Decay Settings")]
        public float DefaultDecayRate = 0.01f; // Per second
        public float TraumaticDecayMultiplier = 0.25f;
        public float MundaneDecayMultiplier = 1.5f;
        public float ReinforcementAmount = 0.2f;
        public float PruneThreshold = 0.05f;
        public float DecayInterval = 5.0f; // seconds
        private float _decayTimer = 0f;

        void Awake()
        {
            if (Instance != null && Instance != this)
            {
                Destroy(gameObject);
                return;
            }
            Instance = this;
            DontDestroyOnLoad(gameObject);
        }

        void Update()
        {
            _decayTimer += Time.deltaTime;
            if (_decayTimer >= DecayInterval)
            {
                _decayTimer = 0f;
                DecayAllNPCMemories(DecayInterval);
            }
        }

        /// <summary>
        /// Get or create a MemoryManager for an NPC by ID.
        /// </summary>
        public MemoryManager GetOrCreateMemoryManager(string npcId)
        {
            if (!_npcMemoryManagers.TryGetValue(npcId, out var manager))
            {
                var go = new GameObject($"MemoryManager_{npcId}");
                manager = go.AddComponent<MemoryManager>();
                _npcMemoryManagers[npcId] = manager;
            }
            return manager;
        }

        /// <summary>
        /// Add a memory to an NPC, with metadata and event emission.
        /// </summary>
        public void AddMemory(string npcId, string content, float importance, List<string> associatedEntities, float decayRate, List<string> tags, MemoryType type, string source = null, float emotionalImpact = 0f, float reliability = 1f, float falseMemoryProbability = 0f)
        {
            var manager = GetOrCreateMemoryManager(npcId);
            if (manager == null) return;
            // Use the new overload with all metadata
            manager.AddMemory(content, importance, associatedEntities, decayRate, tags, type, emotionalImpact, reliability, falseMemoryProbability);
            // Optionally, emit event with source if needed
        }

        /// <summary>
        /// Decay all NPC memories, applying motif and relationship modifiers.
        /// </summary>
        public void DecayAllNPCMemories(float deltaTime)
        {
            foreach (var kvp in _npcMemoryManagers)
            {
                string npcId = kvp.Key;
                var manager = kvp.Value;
                float decayRate = DefaultDecayRate;
                // Motif integration: adjust decay based on active motifs
                var npc = FindNPCById(npcId);
                if (npc != null)
                {
                    var motifs = npc.GetActiveMotifs();
                    foreach (var motif in motifs)
                    {
                        // Example: motifs with "memory_boost" tag slow decay
                        if (motif.Tags.Contains("memory_boost"))
                            decayRate *= 0.8f;
                        if (motif.Tags.Contains("memory_fade"))
                            decayRate *= 1.2f;
                    }
                    // Relationship integration: close relationships slow decay
                    foreach (var entity in manager.QueryByTag("person"))
                    {
                        float relStrength = npc.RelationshipStateMachine?.GetIntensity(entity.Content) ?? 0f;
                        if (relStrength > 50f)
                            decayRate *= 0.7f;
                    }
                }
                // Decay and prune
                manager.DecayMemories(deltaTime * decayRate);
                manager.PruneExpired();
            }
        }

        /// <summary>
        /// Recall a memory for an NPC, with probability based on decay and context.
        /// </summary>
        public Memory RecallMemory(string npcId, Func<Memory, bool> predicate, float contextBoost = 0f)
        {
            var manager = GetOrCreateMemoryManager(npcId);
            foreach (var mem in manager.Query(predicate))
            {
                float recallChance = Mathf.Clamp01(mem.CurrentImportance + contextBoost);
                if (UnityEngine.Random.value < recallChance)
                {
                    // Emit recall event
                    EventBus.Instance.Publish(new MemoryEvent(npcId, mem, "recalled"));
                    return mem;
                }
                else if (mem.CurrentImportance < PruneThreshold && UnityEngine.Random.value < 0.1f)
                {
                    // False memory: emit event
                    EventBus.Instance.Publish(new MemoryEvent(npcId, mem, "false_recall"));
                }
            }
            return null;
        }

        /// <summary>
        /// Reinforce a memory for an NPC (e.g., when repeated or discussed).
        /// </summary>
        public void ReinforceMemory(string npcId, string memoryId, float amount = -1f)
        {
            var manager = GetOrCreateMemoryManager(npcId);
            if (amount < 0) amount = ReinforcementAmount;
            manager.ReinforceMemory(memoryId, amount);
            var mem = manager.Query(m => m.Id == memoryId);
            foreach (var m in mem)
                EventBus.Instance.Publish(new MemoryEvent(npcId, m, "reinforced"));
        }

        /// <summary>
        /// Prune insignificant/old memories for all NPCs.
        /// </summary>
        public void PruneAll()
        {
            foreach (var manager in _npcMemoryManagers.Values)
                manager.PruneExpired();
        }

        /// <summary>
        /// Find an NPCBase by ID (runtime only, no scene refs).
        /// </summary>
        private NPCBase FindNPCById(string npcId)
        {
            foreach (var npc in GameObject.FindObjectsOfType<NPCBase>())
                if (npc.NPCName == npcId)
                    return npc;
            return null;
        }
    }

    /// <summary>
    /// Event data for memory-related events.
    /// </summary>
    public class MemoryEvent
    {
        public string NpcId { get; }
        public Memory Memory { get; }
        public string EventType { get; }
        public DateTime Timestamp { get; }
        public MemoryEvent(string npcId, Memory memory, string eventType)
        {
            NpcId = npcId;
            Memory = memory;
            EventType = eventType;
            Timestamp = DateTime.UtcNow;
        }
    }
} 