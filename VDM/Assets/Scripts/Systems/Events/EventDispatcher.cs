using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using UnityEngine;

namespace VDM.Systems.Events
{
    public interface IEvent { int TypeId { get; } }

    public interface IEventSubscriber<T> where T : IEvent
    {
        void Handle(T evt);
    }

    public interface IEventMiddleware
    {
        IEvent Process(IEvent evt);
    }

    public sealed class EventDispatcher : MonoBehaviour
    {
        private static EventDispatcher _instance;
        public static EventDispatcher Instance
        {
            get
            {
                if (_instance == null)
                {
                    var go = new GameObject("EventDispatcher");
                    _instance = go.AddComponent<EventDispatcher>();
                    DontDestroyOnLoad(go);
                }
                return _instance;
            }
        }

        private readonly Dictionary<int, List<Action<IEvent>>> _subscribers = new Dictionary<int, List<Action<IEvent>>>();
        private readonly List<IEventMiddleware> _middlewares = new List<IEventMiddleware>();

        public void RegisterMiddleware(IEventMiddleware middleware)
        {
            _middlewares.Add(middleware);
        }

        public void Subscribe<T>(Action<T> handler) where T : IEvent
        {
            int typeId = typeof(T).GetHashCode();
            if (!_subscribers.ContainsKey(typeId))
                _subscribers[typeId] = new List<Action<IEvent>>();
            _subscribers[typeId].Add(evt => handler((T)evt));
        }

        public void Unsubscribe<T>(Action<T> handler) where T : IEvent
        {
            int typeId = typeof(T).GetHashCode();
            if (_subscribers.ContainsKey(typeId))
                _subscribers[typeId].RemoveAll(a => a.Equals(handler));
        }

        public void Dispatch(IEvent evt)
        {
            foreach (var middleware in _middlewares)
                evt = middleware.Process(evt);
            int typeId = evt.GetType().GetHashCode();
            if (_subscribers.ContainsKey(typeId))
                foreach (var handler in _subscribers[typeId])
                    handler(evt);
        }

        public async Task DispatchAsync(IEvent evt)
        {
            foreach (var middleware in _middlewares)
                evt = middleware.Process(evt);
            int typeId = evt.GetType().GetHashCode();
            if (_subscribers.ContainsKey(typeId))
                foreach (var handler in _subscribers[typeId])
                    await Task.Run(() => handler(evt));
        }
    }

    // Example canonical event types
    public class MemoryCreatedEvent : IEvent { public int TypeId => 1; public string Description; }
    public class MemoryReinforcedEvent : IEvent { public int TypeId => 2; public string Description; }
    public class MemoryDeletedEvent : IEvent { public int TypeId => 3; public string Description; }
    public class RumorSpreadEvent : IEvent { public int TypeId => 4; public string Content; }
    public class MotifChangedEvent : IEvent { public int TypeId => 5; public string Motif; }
    // ... add other canonical event types as needed

    // Canonical event types:
    // MemoryCreated, MemoryReinforced, MemoryDeleted, RumorSpread, MotifChanged, PopulationChanged, POIStateChanged, FactionChanged, QuestUpdated, CombatEvent, TimeAdvanced, EventLogged, RelationshipChanged, StorageEvent, WorldStateChanged
    // Extend event classes as needed for analytics, narrative, and system integration

    public class PopulationChangedEvent : IEvent { public int TypeId => 6; public string POIId; public int OldPopulation; public int NewPopulation; public DateTime Timestamp; }
    public class POIStateChangedEvent : IEvent { public int TypeId => 7; public string POIId; public string OldState; public string NewState; public DateTime Timestamp; }
    public class FactionChangedEvent : IEvent { public int TypeId => 8; public int FactionId; public string ChangeType; public string Details; public DateTime Timestamp; }
    public class QuestUpdatedEvent : IEvent { public int TypeId => 9; public int QuestId; public string Status; public float Progress; public DateTime Timestamp; }
    public class CombatEvent : IEvent { public int TypeId => 10; public string EventType; public string Details; public DateTime Timestamp; }
    public class TimeAdvancedEvent : IEvent { public int TypeId => 11; public DateTime NewTime; }
    public class EventLoggedEvent : IEvent { public int TypeId => 12; public string Category; public string Message; public DateTime Timestamp; }
    public class RelationshipChangedEvent : IEvent { public int TypeId => 13; public int SourceId; public int TargetId; public string RelationshipType; public string ChangeType; public DateTime Timestamp; }
    public class StorageEvent : IEvent { public int TypeId => 14; public string Operation; public string FileName; public bool Success; public DateTime Timestamp; }
    public class WorldStateChangedEvent : IEvent { public int TypeId => 15; public string Key; public object OldValue; public object NewValue; public DateTime Timestamp; }
} 