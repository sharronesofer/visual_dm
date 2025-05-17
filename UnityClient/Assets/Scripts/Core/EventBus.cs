using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using UnityEngine;

namespace VisualDM.Core
{
    /// <summary>
    /// Priority levels for event handlers.
    /// </summary>
    public enum EventPriority
    {
        High = 0,
        Normal = 1,
        Low = 2,
        Background = 3
    }

    /// <summary>
    /// Core EventBus implementation providing a type-safe pub/sub pattern for Unity.
    /// Features:
    /// - Type safety with generics
    /// - Event prioritization
    /// - Weak references to prevent memory leaks
    /// - Thread-safe event dispatching
    /// - Asynchronous event handling
    /// </summary>
    public class EventBus : MonoBehaviour
    {
        #region Singleton Implementation

        private static EventBus _instance;
        private static readonly object _lock = new object();

        /// <summary>
        /// Singleton instance of the EventBus.
        /// </summary>
        public static EventBus Instance
        {
            get
            {
                if (_instance == null)
                {
                    lock (_lock)
                    {
                        if (_instance == null)
                        {
                            var go = new GameObject("[EventBus]");
                            _instance = go.AddComponent<EventBus>();
                            DontDestroyOnLoad(go);
                        }
                    }
                }
                return _instance;
            }
        }

        #endregion

        #region Private Fields

        // Avoid dictionary lookups for the most frequent operations
        private readonly Dictionary<Type, object> _handlers = new Dictionary<Type, object>();
        private readonly Dictionary<Type, object> _asyncHandlers = new Dictionary<Type, object>();
        private readonly SynchronizationContext _mainThreadContext;

        #endregion

        #region Unity Lifecycle

        private void Awake()
        {
            if (_instance != null && _instance != this)
            {
                Destroy(gameObject);
                return;
            }

            _instance = this;
            DontDestroyOnLoad(gameObject);
            _mainThreadContext = SynchronizationContext.Current;
        }

        private void OnDestroy()
        {
            ClearAllSubscriptions();
        }

        #endregion

        #region Handler Types

        /// <summary>
        /// Stores event handler information with priority and weak references.
        /// </summary>
        private class EventHandlerInfo<T>
        {
            public WeakReference<Action<T>> HandlerReference { get; }
            public EventPriority Priority { get; }
            public Func<T, bool> Filter { get; }
            public Action<T> StrongHandler { get; } // Strong reference for static methods

            public EventHandlerInfo(Action<T> handler, EventPriority priority, Func<T, bool> filter)
            {
                Priority = priority;
                Filter = filter;

                // If handler is a method on an object, store as weak reference
                if (handler.Target != null && !(handler.Target is Type))
                {
                    HandlerReference = new WeakReference<Action<T>>(handler);
                    StrongHandler = null;
                }
                else
                {
                    // Static methods and lambdas without captures need strong references
                    StrongHandler = handler;
                    HandlerReference = null;
                }
            }

            public bool TryGetHandler(out Action<T> handler)
            {
                if (StrongHandler != null)
                {
                    handler = StrongHandler;
                    return true;
                }

                if (HandlerReference != null && HandlerReference.TryGetTarget(out var target))
                {
                    handler = target;
                    return true;
                }

                handler = null;
                return false;
            }
        }

        /// <summary>
        /// Stores async event handler information with priority and weak references.
        /// </summary>
        private class AsyncEventHandlerInfo<T>
        {
            public WeakReference<Func<T, Task>> HandlerReference { get; }
            public EventPriority Priority { get; }
            public Func<T, bool> Filter { get; }
            public Func<T, Task> StrongHandler { get; } // Strong reference for static methods

            public AsyncEventHandlerInfo(Func<T, Task> handler, EventPriority priority, Func<T, bool> filter)
            {
                Priority = priority;
                Filter = filter;

                // If handler is a method on an object, store as weak reference
                if (handler.Target != null && !(handler.Target is Type))
                {
                    HandlerReference = new WeakReference<Func<T, Task>>(handler);
                    StrongHandler = null;
                }
                else
                {
                    // Static methods and lambdas without captures need strong references
                    StrongHandler = handler;
                    HandlerReference = null;
                }
            }

            public bool TryGetHandler(out Func<T, Task> handler)
            {
                if (StrongHandler != null)
                {
                    handler = StrongHandler;
                    return true;
                }

                if (HandlerReference != null && HandlerReference.TryGetTarget(out var target))
                {
                    handler = target;
                    return true;
                }

                handler = null;
                return false;
            }
        }

        // Type-safe handler collections
        private class EventHandlerCollection<T>
        {
            private readonly List<EventHandlerInfo<T>> _handlers = new List<EventHandlerInfo<T>>();
            private readonly object _lock = new object();
            private bool _needsSort = false;

            public void Add(EventHandlerInfo<T> handlerInfo)
            {
                lock (_lock)
                {
                    _handlers.Add(handlerInfo);
                    _needsSort = true;
                }
            }

            public bool Remove(Action<T> handler)
            {
                lock (_lock)
                {
                    int initialCount = _handlers.Count;
                    
                    // Find by reference equality
                    _handlers.RemoveAll(h => 
                    {
                        if (h.StrongHandler != null && h.StrongHandler == handler)
                            return true;
                        
                        if (h.HandlerReference != null && h.HandlerReference.TryGetTarget(out var target))
                            return target == handler;
                            
                        return false;
                    });
                    
                    return _handlers.Count < initialCount;
                }
            }

            public void Clear()
            {
                lock (_lock)
                {
                    _handlers.Clear();
                }
            }

            public List<EventHandlerInfo<T>> GetHandlers()
            {
                lock (_lock)
                {
                    if (_needsSort)
                    {
                        _handlers.Sort((a, b) => a.Priority.CompareTo(b.Priority));
                        _needsSort = false;
                    }
                    
                    // Clean up handlers with dead references
                    _handlers.RemoveAll(h => !h.TryGetHandler(out _));
                    
                    return new List<EventHandlerInfo<T>>(_handlers);
                }
            }
        }

        // Type-safe async handler collections
        private class AsyncEventHandlerCollection<T>
        {
            private readonly List<AsyncEventHandlerInfo<T>> _handlers = new List<AsyncEventHandlerInfo<T>>();
            private readonly object _lock = new object();
            private bool _needsSort = false;

            public void Add(AsyncEventHandlerInfo<T> handlerInfo)
            {
                lock (_lock)
                {
                    _handlers.Add(handlerInfo);
                    _needsSort = true;
                }
            }

            public bool Remove(Func<T, Task> handler)
            {
                lock (_lock)
                {
                    int initialCount = _handlers.Count;
                    
                    // Find by reference equality
                    _handlers.RemoveAll(h => 
                    {
                        if (h.StrongHandler != null && h.StrongHandler == handler)
                            return true;
                        
                        if (h.HandlerReference != null && h.HandlerReference.TryGetTarget(out var target))
                            return target == handler;
                            
                        return false;
                    });
                    
                    return _handlers.Count < initialCount;
                }
            }

            public void Clear()
            {
                lock (_lock)
                {
                    _handlers.Clear();
                }
            }

            public List<AsyncEventHandlerInfo<T>> GetHandlers()
            {
                lock (_lock)
                {
                    if (_needsSort)
                    {
                        _handlers.Sort((a, b) => a.Priority.CompareTo(b.Priority));
                        _needsSort = false;
                    }
                    
                    // Clean up handlers with dead references
                    _handlers.RemoveAll(h => !h.TryGetHandler(out _));
                    
                    return new List<AsyncEventHandlerInfo<T>>(_handlers);
                }
            }
        }

        #endregion

        #region Subscription Methods

        /// <summary>
        /// Subscribe to events of type T.
        /// </summary>
        /// <typeparam name="T">Type of event to subscribe to</typeparam>
        /// <param name="handler">Handler to call when event is published</param>
        /// <param name="priority">Priority of the handler (lower value = higher priority)</param>
        /// <param name="filter">Optional filter function to determine if handler should be called</param>
        public void Subscribe<T>(Action<T> handler, EventPriority priority = EventPriority.Normal, Func<T, bool> filter = null)
        {
            if (handler == null)
                throw new ArgumentNullException(nameof(handler));

            Type eventType = typeof(T);

            lock (_lock)
            {
                if (!_handlers.TryGetValue(eventType, out object value))
                {
                    var collection = new EventHandlerCollection<T>();
                    _handlers[eventType] = collection;
                    value = collection;
                }

                var typedCollection = (EventHandlerCollection<T>)value;
                typedCollection.Add(new EventHandlerInfo<T>(handler, priority, filter));
            }

            Debug.Log($"[EventBus] Subscribed to {eventType.Name} events");
        }

        /// <summary>
        /// Subscribe to events of type T with an async handler.
        /// </summary>
        /// <typeparam name="T">Type of event to subscribe to</typeparam>
        /// <param name="handler">Async handler to call when event is published</param>
        /// <param name="priority">Priority of the handler (lower value = higher priority)</param>
        /// <param name="filter">Optional filter function to determine if handler should be called</param>
        public void SubscribeAsync<T>(Func<T, Task> handler, EventPriority priority = EventPriority.Normal, Func<T, bool> filter = null)
        {
            if (handler == null)
                throw new ArgumentNullException(nameof(handler));

            Type eventType = typeof(T);

            lock (_lock)
            {
                if (!_asyncHandlers.TryGetValue(eventType, out object value))
                {
                    var collection = new AsyncEventHandlerCollection<T>();
                    _asyncHandlers[eventType] = collection;
                    value = collection;
                }

                var typedCollection = (AsyncEventHandlerCollection<T>)value;
                typedCollection.Add(new AsyncEventHandlerInfo<T>(handler, priority, filter));
            }

            Debug.Log($"[EventBus] Subscribed async handler to {eventType.Name} events");
        }

        /// <summary>
        /// Unsubscribe a handler from events of type T.
        /// </summary>
        /// <typeparam name="T">Type of event to unsubscribe from</typeparam>
        /// <param name="handler">Handler to unsubscribe</param>
        /// <returns>True if the handler was found and removed</returns>
        public bool Unsubscribe<T>(Action<T> handler)
        {
            if (handler == null)
                throw new ArgumentNullException(nameof(handler));

            Type eventType = typeof(T);
            bool removed = false;

            lock (_lock)
            {
                if (_handlers.TryGetValue(eventType, out object value))
                {
                    var typedCollection = (EventHandlerCollection<T>)value;
                    removed = typedCollection.Remove(handler);
                }
            }

            if (removed)
            {
                Debug.Log($"[EventBus] Unsubscribed from {eventType.Name} events");
            }

            return removed;
        }

        /// <summary>
        /// Unsubscribe an async handler from events of type T.
        /// </summary>
        /// <typeparam name="T">Type of event to unsubscribe from</typeparam>
        /// <param name="handler">Async handler to unsubscribe</param>
        /// <returns>True if the handler was found and removed</returns>
        public bool UnsubscribeAsync<T>(Func<T, Task> handler)
        {
            if (handler == null)
                throw new ArgumentNullException(nameof(handler));

            Type eventType = typeof(T);
            bool removed = false;

            lock (_lock)
            {
                if (_asyncHandlers.TryGetValue(eventType, out object value))
                {
                    var typedCollection = (AsyncEventHandlerCollection<T>)value;
                    removed = typedCollection.Remove(handler);
                }
            }

            if (removed)
            {
                Debug.Log($"[EventBus] Unsubscribed async handler from {eventType.Name} events");
            }

            return removed;
        }

        /// <summary>
        /// Clear all subscriptions for events of type T.
        /// </summary>
        /// <typeparam name="T">Type of event to clear subscriptions for</typeparam>
        public void ClearSubscriptions<T>()
        {
            Type eventType = typeof(T);

            lock (_lock)
            {
                if (_handlers.TryGetValue(eventType, out object value))
                {
                    var typedCollection = (EventHandlerCollection<T>)value;
                    typedCollection.Clear();
                }

                if (_asyncHandlers.TryGetValue(eventType, out object asyncValue))
                {
                    var typedCollection = (AsyncEventHandlerCollection<T>)asyncValue;
                    typedCollection.Clear();
                }
            }

            Debug.Log($"[EventBus] Cleared all subscriptions for {eventType.Name} events");
        }

        /// <summary>
        /// Clear all subscriptions for all event types.
        /// </summary>
        public void ClearAllSubscriptions()
        {
            lock (_lock)
            {
                foreach (var kvp in _handlers)
                {
                    dynamic collection = kvp.Value;
                    collection.Clear();
                }

                foreach (var kvp in _asyncHandlers)
                {
                    dynamic collection = kvp.Value;
                    collection.Clear();
                }

                _handlers.Clear();
                _asyncHandlers.Clear();
            }

            Debug.Log("[EventBus] Cleared all subscriptions");
        }

        #endregion

        #region Publishing Methods

        /// <summary>
        /// Publish an event to all subscribers.
        /// </summary>
        /// <typeparam name="T">Type of event to publish</typeparam>
        /// <param name="eventData">Event data to publish</param>
        public void Publish<T>(T eventData)
        {
            if (eventData == null)
                throw new ArgumentNullException(nameof(eventData));

            Type eventType = typeof(T);

            // Get synchronous handlers
            List<EventHandlerInfo<T>> handlers = null;
            lock (_lock)
            {
                if (_handlers.TryGetValue(eventType, out object value))
                {
                    var typedCollection = (EventHandlerCollection<T>)value;
                    handlers = typedCollection.GetHandlers();
                }
            }

            // Execute handlers on the main thread
            if (handlers != null && handlers.Count > 0)
            {
                // If already on main thread, execute directly
                if (SynchronizationContext.Current == _mainThreadContext)
                {
                    ExecuteHandlers(handlers, eventData);
                }
                else
                {
                    // Otherwise post to main thread
                    _mainThreadContext.Post(_ => ExecuteHandlers(handlers, eventData), null);
                }
            }

            // Process async handlers
            List<AsyncEventHandlerInfo<T>> asyncHandlers = null;
            lock (_lock)
            {
                if (_asyncHandlers.TryGetValue(eventType, out object value))
                {
                    var typedCollection = (AsyncEventHandlerCollection<T>)value;
                    asyncHandlers = typedCollection.GetHandlers();
                }
            }

            // Start async handlers
            if (asyncHandlers != null && asyncHandlers.Count > 0)
            {
                // Create tasks for async handlers but don't wait for them
                _ = ExecuteAsyncHandlersInBackground(asyncHandlers, eventData);
            }

            Debug.Log($"[EventBus] Published {eventType.Name} event");
        }

        /// <summary>
        /// Publish an event and wait for all async handlers to complete.
        /// </summary>
        /// <typeparam name="T">Type of event to publish</typeparam>
        /// <param name="eventData">Event data to publish</param>
        /// <returns>Task that completes when all async handlers have completed</returns>
        public async Task PublishAsync<T>(T eventData)
        {
            if (eventData == null)
                throw new ArgumentNullException(nameof(eventData));

            Type eventType = typeof(T);

            // Get synchronous handlers
            List<EventHandlerInfo<T>> handlers = null;
            lock (_lock)
            {
                if (_handlers.TryGetValue(eventType, out object value))
                {
                    var typedCollection = (EventHandlerCollection<T>)value;
                    handlers = typedCollection.GetHandlers();
                }
            }

            // Execute handlers on the main thread
            if (handlers != null && handlers.Count > 0)
            {
                // If already on main thread, execute directly
                if (SynchronizationContext.Current == _mainThreadContext)
                {
                    ExecuteHandlers(handlers, eventData);
                }
                else
                {
                    // Wait for main thread execution
                    var tcs = new TaskCompletionSource<bool>();
                    _mainThreadContext.Post(_ => 
                    {
                        ExecuteHandlers(handlers, eventData);
                        tcs.SetResult(true);
                    }, null);
                    await tcs.Task;
                }
            }

            // Process async handlers
            List<AsyncEventHandlerInfo<T>> asyncHandlers = null;
            lock (_lock)
            {
                if (_asyncHandlers.TryGetValue(eventType, out object value))
                {
                    var typedCollection = (AsyncEventHandlerCollection<T>)value;
                    asyncHandlers = typedCollection.GetHandlers();
                }
            }

            // Wait for all async handlers to complete
            if (asyncHandlers != null && asyncHandlers.Count > 0)
            {
                await ExecuteAsyncHandlersInBackground(asyncHandlers, eventData);
            }

            Debug.Log($"[EventBus] Published async {eventType.Name} event and waited for completion");
        }

        #endregion

        #region Helper Methods

        private void ExecuteHandlers<T>(List<EventHandlerInfo<T>> handlers, T eventData)
        {
            foreach (var handlerInfo in handlers)
            {
                if (handlerInfo.TryGetHandler(out Action<T> handler))
                {
                    try
                    {
                        // Apply filter if provided
                        if (handlerInfo.Filter != null && !handlerInfo.Filter(eventData))
                            continue;

                        handler(eventData);
                    }
                    catch (Exception ex)
                    {
                        Debug.LogError($"[EventBus] Error in handler for {typeof(T).Name} event: {ex}");
                    }
                }
            }
        }

        private async Task ExecuteAsyncHandlersInBackground<T>(List<AsyncEventHandlerInfo<T>> handlers, T eventData)
        {
            var tasks = new List<Task>();

            foreach (var handlerInfo in handlers)
            {
                if (handlerInfo.TryGetHandler(out Func<T, Task> handler))
                {
                    try
                    {
                        // Apply filter if provided
                        if (handlerInfo.Filter != null && !handlerInfo.Filter(eventData))
                            continue;

                        // Start the task but capture any exceptions
                        Task handlerTask = handler(eventData);
                        tasks.Add(handlerTask);
                    }
                    catch (Exception ex)
                    {
                        Debug.LogError($"[EventBus] Error starting async handler for {typeof(T).Name} event: {ex}");
                    }
                }
            }

            if (tasks.Count > 0)
            {
                // Wait for all tasks to complete, capturing any exceptions
                await Task.WhenAll(tasks.Select(t => t.ContinueWith(task =>
                {
                    if (task.IsFaulted && task.Exception != null)
                    {
                        Debug.LogError($"[EventBus] Error in async handler for {typeof(T).Name} event: {task.Exception.InnerException}");
                    }
                })));
            }
        }

        #endregion
    }
} 