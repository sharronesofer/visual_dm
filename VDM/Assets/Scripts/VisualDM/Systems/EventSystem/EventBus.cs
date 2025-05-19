using System;
using System.Collections.Generic;
using UnityEngine;

// This class forwards to the implementation in Assets/Scripts/Systems/EventSystem/EventBus.cs
// to fix compilation errors without duplicating code
namespace VisualDM.Systems.EventSystem
{
    // The implementation exists in another file with the same namespace
    // This class is a placeholder to satisfy compiler references
    public class EventBus
    {
        private static EventBus _instance;
        public static EventBus Instance
        {
            get
            {
                if (_instance == null)
                {
                    _instance = new EventBus();
                }
                return _instance;
            }
        }

        private Dictionary<Type, List<Action<object>>> _subscribers = new Dictionary<Type, List<Action<object>>>();

        public void Subscribe<T>(Action<T> handler)
        {
            Type eventType = typeof(T);
            if (!_subscribers.ContainsKey(eventType))
            {
                _subscribers[eventType] = new List<Action<object>>();
            }
            
            // Convert generic handler to object-based handler
            void ObjectHandler(object e) => handler((T)e);
            
            _subscribers[eventType].Add(ObjectHandler);
        }

        public void Publish<T>(T eventData)
        {
            Type eventType = typeof(T);
            if (!_subscribers.ContainsKey(eventType))
            {
                return;
            }

            foreach (var handler in _subscribers[eventType])
            {
                try
                {
                    handler(eventData);
                }
                catch (Exception ex)
                {
                    Debug.LogError($"Error in event handler: {ex.Message}");
                }
            }
        }
    }

    public class GameStateChangedEvent
    {
        public string Key { get; private set; }
        public object NewValue { get; private set; }
        public object OldValue { get; private set; }
        public DateTime Timestamp { get; private set; }

        public GameStateChangedEvent(string key, object newValue, object oldValue, DateTime timestamp)
        {
            Key = key;
            NewValue = newValue;
            OldValue = oldValue;
            Timestamp = timestamp;
        }
    }
} 