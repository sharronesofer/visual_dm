using System;
using System.Collections.Generic;
using UnityEngine;

namespace VisualDM.World
{
    /// <summary>
    /// Represents a significant world event for rumor generation.
    /// </summary>
    public class WorldEvent
    {
        public enum EventType { NPCDeath, ItemAcquisition, FactionChange, Other }
        public EventType Type;
        public Vector2 Location;
        public DateTime Time;
        public List<string> InvolvedEntities; // e.g., NPC IDs, item names
        public string Description;

        public WorldEvent(EventType type, Vector2 location, DateTime time, List<string> involvedEntities, string description)
        {
            Type = type;
            Location = location;
            Time = time;
            InvolvedEntities = involvedEntities;
            Description = description;
        }
    }

    /// <summary>
    /// Manages world event subscriptions and dispatching for rumor integration.
    /// </summary>
    public static class WorldEventManager
    {
        public static event Action<WorldEvent> OnWorldEvent;
        private static List<WorldEvent> eventLog = new List<WorldEvent>();

        // Batching fields
        private static Queue<WorldEvent> eventQueue = new Queue<WorldEvent>();
        public static int BatchSize { get; set; } = 10;
        public static bool UseBatching { get; set; } = true;

        /// <summary>
        /// Call this to register a new world event. Triggers listeners and stores the event.
        /// If batching is enabled, events are queued and processed in batches.
        /// </summary>
        public static void RegisterEvent(WorldEvent worldEvent)
        {
            if (IsRumorWorthy(worldEvent))
            {
                if (UseBatching)
                {
                    eventQueue.Enqueue(worldEvent);
                    if (eventQueue.Count >= BatchSize)
                    {
                        ProcessEventBatch();
                    }
                }
                else
                {
                    eventLog.Add(worldEvent);
                    OnWorldEvent?.Invoke(worldEvent);
                }
            }
        }

        /// <summary>
        /// Processes all events in the queue as a batch, triggering listeners and storing them.
        /// </summary>
        public static void ProcessEventBatch()
        {
            while (eventQueue.Count > 0)
            {
                var evt = eventQueue.Dequeue();
                eventLog.Add(evt);
                OnWorldEvent?.Invoke(evt);
            }
        }

        /// <summary>
        /// Determines if an event is rumor-worthy based on type and context.
        /// </summary>
        public static bool IsRumorWorthy(WorldEvent worldEvent)
        {
            // Example: Only certain types are rumor-worthy, can expand logic as needed
            switch (worldEvent.Type)
            {
                case WorldEvent.EventType.NPCDeath:
                case WorldEvent.EventType.ItemAcquisition:
                case WorldEvent.EventType.FactionChange:
                    return true;
                default:
                    return false;
            }
        }

        /// <summary>
        /// Returns a copy of the event log for external systems (e.g., rumor system).
        /// </summary>
        public static List<WorldEvent> GetEventLog()
        {
            return new List<WorldEvent>(eventLog);
        }
    }

    /// <summary>
    /// Listens for world state changes and registers significant events.
    /// Attach this to a runtime GameObject or call from GameLoader.
    /// </summary>
    public class WorldEventListener : MonoBehaviour
    {
        void Awake()
        {
            // Example: Subscribe to other systems' events here
            // e.g., WorldManager.OnNPCDeath += OnNPCDeath;
            // e.g., FactionSystem.OnFactionChange += OnFactionChange;
        }

        // Example event handler for NPC death
        public void OnNPCDeath(string npcId, Vector2 location)
        {
            var evt = new WorldEvent(
                WorldEvent.EventType.NPCDeath,
                location,
                DateTime.Now,
                new List<string> { npcId },
                $"NPC {npcId} died at {location}"
            );
            WorldEventManager.RegisterEvent(evt);
        }

        // Example event handler for item acquisition
        public void OnItemAcquisition(string npcId, string itemName, Vector2 location)
        {
            var evt = new WorldEvent(
                WorldEvent.EventType.ItemAcquisition,
                location,
                DateTime.Now,
                new List<string> { npcId, itemName },
                $"NPC {npcId} acquired {itemName} at {location}"
            );
            WorldEventManager.RegisterEvent(evt);
        }

        // Example event handler for faction change
        public void OnFactionChange(string npcId, string factionName, Vector2 location)
        {
            var evt = new WorldEvent(
                WorldEvent.EventType.FactionChange,
                location,
                DateTime.Now,
                new List<string> { npcId, factionName },
                $"NPC {npcId} joined/left faction {factionName} at {location}"
            );
            WorldEventManager.RegisterEvent(evt);
        }
    }
}