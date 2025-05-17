using System;
using System.Collections.Generic;
using UnityEngine;
using System.Threading.Tasks;

namespace VisualDM.Core
{
    /// <summary>
    /// Event bus for Unity runtime events, implementing a publish-subscribe pattern.
    /// Allows components to communicate without direct references.
    /// </summary>
    public class EventBus : MonoBehaviour
    {
        // Singleton instance
        private static EventBus _instance;
        
        public static EventBus Instance
        {
            get
            {
                if (_instance == null)
                {
                    GameObject go = new GameObject("EventBus");
                    _instance = go.AddComponent<EventBus>();
                    DontDestroyOnLoad(go);
                }
                return _instance;
            }
        }

        // Dictionary to store event handlers by event type
        private readonly Dictionary<string, List<Action<object>>> _eventHandlers = new Dictionary<string, List<Action<object>>>();
        
        // Dictionary to store async event handlers by event type
        private readonly Dictionary<string, List<Func<object, Task>>> _asyncEventHandlers = new Dictionary<string, List<Func<object, Task>>>();

        private void Awake()
        {
            if (_instance != null && _instance != this)
            {
                Destroy(gameObject);
                return;
            }

            _instance = this;
            DontDestroyOnLoad(gameObject);
        }

        /// <summary>
        /// Emit an event synchronously to all registered handlers
        /// </summary>
        /// <param name="eventType">The event type identifier</param>
        /// <param name="payload">Data to pass to event handlers</param>
        public void Emit(string eventType, object payload)
        {
            Debug.Log($"[EventBus] Emitting event: {eventType}");
            
            if (_eventHandlers.TryGetValue(eventType, out var handlers))
            {
                // Create a copy to avoid issues if handlers register/unregister during execution
                var handlersCopy = new List<Action<object>>(handlers);
                
                foreach (var handler in handlersCopy)
                {
                    try
                    {
                        handler(payload);
                    }
                    catch (Exception e)
                    {
                        Debug.LogError($"[EventBus] Error in handler for event {eventType}: {e.Message}");
                    }
                }
            }
        }

        /// <summary>
        /// Emit an event asynchronously to all registered handlers
        /// </summary>
        /// <param name="eventType">The event type identifier</param>
        /// <param name="payload">Data to pass to event handlers</param>
        public async Task EmitAsync(string eventType, object payload)
        {
            Debug.Log($"[EventBus] Emitting async event: {eventType}");
            
            // Handle synchronous event handlers
            if (_eventHandlers.TryGetValue(eventType, out var handlers))
            {
                foreach (var handler in new List<Action<object>>(handlers))
                {
                    try
                    {
                        // Run on main thread to prevent threading issues
                        await Task.Run(() => handler(payload));
                    }
                    catch (Exception e)
                    {
                        Debug.LogError($"[EventBus] Error in sync handler for async event {eventType}: {e.Message}");
                    }
                }
            }
            
            // Handle asynchronous event handlers
            if (_asyncEventHandlers.TryGetValue(eventType, out var asyncHandlers))
            {
                var tasks = new List<Task>();
                
                foreach (var handler in new List<Func<object, Task>>(asyncHandlers))
                {
                    try
                    {
                        tasks.Add(handler(payload));
                    }
                    catch (Exception e)
                    {
                        Debug.LogError($"[EventBus] Error in async handler for event {eventType}: {e.Message}");
                    }
                }
                
                await Task.WhenAll(tasks);
            }
        }

        /// <summary>
        /// Register a synchronous event handler
        /// </summary>
        /// <param name="eventType">The event type to listen for</param>
        /// <param name="handler">The handler function to execute when the event occurs</param>
        public void On(string eventType, Action<object> handler)
        {
            Debug.Log($"[EventBus] Registering handler for event: {eventType}");
            
            if (!_eventHandlers.ContainsKey(eventType))
            {
                _eventHandlers[eventType] = new List<Action<object>>();
            }
            
            _eventHandlers[eventType].Add(handler);
        }

        /// <summary>
        /// Register an asynchronous event handler
        /// </summary>
        /// <param name="eventType">The event type to listen for</param>
        /// <param name="handler">The async handler function to execute when the event occurs</param>
        public void OnAsync(string eventType, Func<object, Task> handler)
        {
            Debug.Log($"[EventBus] Registering async handler for event: {eventType}");
            
            if (!_asyncEventHandlers.ContainsKey(eventType))
            {
                _asyncEventHandlers[eventType] = new List<Func<object, Task>>();
            }
            
            _asyncEventHandlers[eventType].Add(handler);
        }

        /// <summary>
        /// Unregister a synchronous event handler
        /// </summary>
        /// <param name="eventType">The event type to stop listening for</param>
        /// <param name="handler">The handler function to remove</param>
        public void Off(string eventType, Action<object> handler)
        {
            Debug.Log($"[EventBus] Unregistering handler for event: {eventType}");
            
            if (_eventHandlers.TryGetValue(eventType, out var handlers))
            {
                handlers.Remove(handler);
                
                // Clean up empty lists
                if (handlers.Count == 0)
                {
                    _eventHandlers.Remove(eventType);
                }
            }
        }

        /// <summary>
        /// Unregister an asynchronous event handler
        /// </summary>
        /// <param name="eventType">The event type to stop listening for</param>
        /// <param name="handler">The async handler function to remove</param>
        public void OffAsync(string eventType, Func<object, Task> handler)
        {
            Debug.Log($"[EventBus] Unregistering async handler for event: {eventType}");
            
            if (_asyncEventHandlers.TryGetValue(eventType, out var handlers))
            {
                handlers.Remove(handler);
                
                // Clean up empty lists
                if (handlers.Count == 0)
                {
                    _asyncEventHandlers.Remove(eventType);
                }
            }
        }

        /// <summary>
        /// Clear all event handlers
        /// </summary>
        public void ClearAll()
        {
            Debug.Log("[EventBus] Clearing all event handlers");
            
            _eventHandlers.Clear();
            _asyncEventHandlers.Clear();
        }
    }
} 