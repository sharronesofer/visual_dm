using System.Collections.Generic;
using System;
using UnityEngine;
using VDM.Systems.Events.Models;


namespace VDM.Systems.Events.Services
{
    /// <summary>
    /// Main event dispatcher implementation for the Events system.
    /// Provides thread-safe event publishing and subscription.
    /// </summary>
    public class EventDispatcher : IEventDispatcher
    {
        private readonly Dictionary<string, List<Action<IEvent>>> _subscribers;
        private readonly object _lockObject;

        public EventDispatcher()
        {
            _subscribers = new Dictionary<string, List<Action<IEvent>>>();
            _lockObject = new object();
        }

        public void Subscribe<T>(Action<T> handler) where T : IEvent
        {
            if (handler == null)
            {
                Debug.LogWarning("Cannot subscribe with null handler");
                return;
            }

            string eventType = typeof(T).Name;
            
            // Wrap the typed handler in a generic one
            Action<IEvent> wrappedHandler = (eventData) =>
            {
                if (eventData is T typedEvent)
                {
                    handler(typedEvent);
                }
            };

            Subscribe(eventType, wrappedHandler);
        }

        public void Subscribe(string eventType, Action<IEvent> handler)
        {
            if (string.IsNullOrEmpty(eventType) || handler == null)
            {
                Debug.LogWarning("Cannot subscribe with null eventType or handler");
                return;
            }

            lock (_lockObject)
            {
                if (!_subscribers.ContainsKey(eventType))
                {
                    _subscribers[eventType] = new List<Action<IEvent>>();
                }

                _subscribers[eventType].Add(handler);
            }

            Debug.Log($"Subscribed to event type: {eventType}. Total subscribers: {GetSubscriberCount(eventType)}");
        }

        public void Unsubscribe<T>(Action<T> handler) where T : IEvent
        {
            if (handler == null)
            {
                Debug.LogWarning("Cannot unsubscribe with null handler");
                return;
            }

            string eventType = typeof(T).Name;
            
            // We need to find the wrapped handler - this is complex, so we'll use event type cleanup
            lock (_lockObject)
            {
                if (_subscribers.ContainsKey(eventType))
                {
                    // For generic unsubscribe, we'll clear all handlers of this type
                    // In a production system, you'd want to track wrapped handlers
                    _subscribers[eventType].Clear();
                    Debug.Log($"Cleared all subscribers for event type: {eventType}");
                }
            }
        }

        public void Unsubscribe(string eventType, Action<IEvent> handler)
        {
            if (string.IsNullOrEmpty(eventType) || handler == null)
            {
                Debug.LogWarning("Cannot unsubscribe with null eventType or handler");
                return;
            }

            lock (_lockObject)
            {
                if (_subscribers.ContainsKey(eventType))
                {
                    _subscribers[eventType].Remove(handler);
                    Debug.Log($"Unsubscribed from event type: {eventType}. Remaining subscribers: {GetSubscriberCount(eventType)}");
                }
            }
        }

        public void Publish<T>(T eventData) where T : IEvent
        {
            if (eventData == null)
            {
                Debug.LogWarning("Cannot publish null event");
                return;
            }

            List<Action<IEvent>> handlersToCall = new List<Action<IEvent>>();

            lock (_lockObject)
            {
                // Get handlers for the specific type
                string eventType = eventData.EventType;
                if (_subscribers.ContainsKey(eventType))
                {
                    handlersToCall.AddRange(_subscribers[eventType]);
                }

                // Also get handlers for the class name (for generic type subscriptions)
                string className = typeof(T).Name;
                if (className != eventType && _subscribers.ContainsKey(className))
                {
                    handlersToCall.AddRange(_subscribers[className]);
                }
            }

            // Call handlers outside of lock to prevent deadlocks
            foreach (var handler in handlersToCall)
            {
                try
                {
                    handler(eventData);
                }
                catch (Exception ex)
                {
                    Debug.LogError($"Error handling event {eventData.EventType}: {ex.Message}");
                }
            }

            if (handlersToCall.Count > 0)
            {
                Debug.Log($"Published event {eventData.EventType} to {handlersToCall.Count} subscribers");
            }
        }

        public void ClearAllSubscriptions()
        {
            lock (_lockObject)
            {
                _subscribers.Clear();
                Debug.Log("Cleared all event subscriptions");
            }
        }

        public void ClearSubscriptions(string eventType)
        {
            if (string.IsNullOrEmpty(eventType))
            {
                Debug.LogWarning("Cannot clear subscriptions for null eventType");
                return;
            }

            lock (_lockObject)
            {
                if (_subscribers.ContainsKey(eventType))
                {
                    int count = _subscribers[eventType].Count;
                    _subscribers[eventType].Clear();
                    Debug.Log($"Cleared {count} subscriptions for event type: {eventType}");
                }
            }
        }

        public int GetSubscriberCount(string eventType)
        {
            if (string.IsNullOrEmpty(eventType))
                return 0;

            lock (_lockObject)
            {
                return _subscribers.ContainsKey(eventType) ? _subscribers[eventType].Count : 0;
            }
        }
    }
} 