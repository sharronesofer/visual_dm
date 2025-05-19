using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using UnityEngine;

namespace VisualDM.AI
{
    /// <summary>
    /// Singleton manager for capturing and queueing game events for rumor transformation.
    /// </summary>
    public class EventCaptureManager : MonoBehaviour
    {
        public static EventCaptureManager Instance { get; private set; }

        private ConcurrentQueue<RumorEvent> eventQueue = new ConcurrentQueue<RumorEvent>();
        public IReadOnlyCollection<RumorEvent> PendingEvents => eventQueue.ToArray();

        private void Awake()
        {
            if (Instance != null && Instance != this)
            {
                Destroy(this);
                return;
            }
            Instance = this;
            DontDestroyOnLoad(gameObject);
        }

        /// <summary>
        /// Record a new event and enqueue it for rumor processing.
        /// </summary>
        public void RecordEvent(RumorEvent rumorEvent)
        {
            eventQueue.Enqueue(rumorEvent);
            // Optionally: trigger event for listeners
        }

        /// <summary>
        /// Try to dequeue the next event for processing.
        /// </summary>
        public bool TryDequeueEvent(out RumorEvent rumorEvent)
        {
            return eventQueue.TryDequeue(out rumorEvent);
        }

        // Example: Hook up to other systems (NPC memory, player actions, world events)
        // public void OnNpcAction(NpcAction action) { ... }
        // public void OnWorldEvent(WorldEvent evt) { ... }
    }
}