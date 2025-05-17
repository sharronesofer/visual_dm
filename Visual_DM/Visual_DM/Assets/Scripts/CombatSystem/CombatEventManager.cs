using System;
using System.Collections.Generic;
using UnityEngine;
using System.Linq;
using System.Runtime.Serialization.Formatters.Binary;
using System.IO;

namespace VisualDM.CombatSystem
{
    /// <summary>
    /// Types of combat events.
    /// </summary>
    public enum CombatEventType
    {
        ActionStarted,
        ActionCompleted,
        DamageDealt,
        EffectApplied,
        EffectRemoved,
        StatusChanged,
        Custom,
        ActionError
    }

    /// <summary>
    /// Serializable combat event data structure.
    /// </summary>
    [Serializable]
    public class CombatEvent
    {
        public CombatEventType EventType;
        public GameObject Actor;
        public GameObject Target;
        public object Payload;
        public DateTime Timestamp;

        public CombatEvent(CombatEventType type, GameObject actor, GameObject target, object payload)
        {
            EventType = type;
            Actor = actor;
            Target = target;
            Payload = payload;
            Timestamp = DateTime.UtcNow;
        }
    }

    /// <summary>
    /// Interface for combat event listeners.
    /// </summary>
    public interface ICombatEventListener
    {
        void OnCombatEvent(CombatEvent e);
    }

    /// <summary>
    /// Singleton manager for combat events, publisher/subscriber pattern, logging, and serialization.
    /// </summary>
    public class CombatEventManager
    {
        private static CombatEventManager _instance;
        private static readonly object _instanceLock = new object();
        public static CombatEventManager Instance
        {
            get
            {
                lock (_instanceLock)
                {
                    return _instance ??= new CombatEventManager();
                }
            }
        }

        private readonly Dictionary<CombatEventType, List<ICombatEventListener>> listeners = new();
        private readonly Queue<CombatEvent> eventQueue = new();
        private readonly List<CombatEvent> eventLog = new();
        private readonly int logCapacity = 256;
        private readonly object eventLock = new();
        private float lastDispatchTime = 0f;
        private float throttleInterval = 0.01f; // 10ms default

        private CombatEventManager() { }

        /// <summary>
        /// Subscribe a listener to one or more event types.
        /// </summary>
        public void Subscribe(ICombatEventListener listener, params CombatEventType[] eventTypes)
        {
            lock (eventLock)
            {
                foreach (var type in eventTypes)
                {
                    if (!listeners.ContainsKey(type))
                        listeners[type] = new List<ICombatEventListener>();
                    if (!listeners[type].Contains(listener))
                        listeners[type].Add(listener);
                }
            }
        }

        /// <summary>
        /// Unsubscribe a listener from all event types.
        /// </summary>
        public void Unsubscribe(ICombatEventListener listener)
        {
            lock (eventLock)
            {
                foreach (var list in listeners.Values)
                    list.Remove(listener);
            }
        }

        /// <summary>
        /// Raise a combat event (immediate or queued).
        /// </summary>
        public void RaiseEvent(CombatEventType type, GameObject actor, GameObject target, object payload = null, bool immediate = false)
        {
            var e = new CombatEvent(type, actor, target, payload);
            if (immediate)
                DispatchEvent(e);
            else
                lock (eventLock) { eventQueue.Enqueue(e); }
        }

        /// <summary>
        /// Dispatch queued events, with throttling and batching.
        /// </summary>
        public void DispatchQueuedEvents(float deltaTime)
        {
            lock (eventLock)
            {
                lastDispatchTime += deltaTime;
                if (lastDispatchTime < throttleInterval) return;
                lastDispatchTime = 0f;
                int batchSize = Math.Min(eventQueue.Count, 16);
                for (int i = 0; i < batchSize; i++)
                {
                    if (eventQueue.Count == 0) break;
                    var e = eventQueue.Dequeue();
                    DispatchEvent(e);
                }
            }
        }

        private void DispatchEvent(CombatEvent e)
        {
            lock (eventLock)
            {
                if (listeners.TryGetValue(e.EventType, out var subs))
                {
                    foreach (var l in subs.ToList())
                        l.OnCombatEvent(e);
                }
                LogEvent(e);
            }
        }

        private void LogEvent(CombatEvent e)
        {
            if (eventLog.Count >= logCapacity)
                eventLog.RemoveAt(0);
            eventLog.Add(e);
        }

        /// <summary>
        /// Get recent events of a specific type.
        /// </summary>
        public List<CombatEvent> GetRecentEvents(CombatEventType type, int count = 10)
        {
            lock (eventLock)
            {
                return eventLog.Where(ev => ev.EventType == type).Reverse().Take(count).ToList();
            }
        }

        /// <summary>
        /// Serialize a combat event for network transmission.
        /// </summary>
        public byte[] SerializeEvent(CombatEvent e)
        {
            using var ms = new MemoryStream();
            var formatter = new BinaryFormatter();
            formatter.Serialize(ms, e);
            return ms.ToArray();
        }

        /// <summary>
        /// Deserialize a combat event from network data.
        /// </summary>
        public CombatEvent DeserializeEvent(byte[] data)
        {
            using var ms = new MemoryStream(data);
            var formatter = new BinaryFormatter();
            return (CombatEvent)formatter.Deserialize(ms);
        }
    }
} 