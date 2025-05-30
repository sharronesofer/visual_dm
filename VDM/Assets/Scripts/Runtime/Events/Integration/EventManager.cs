using System;
using UnityEngine;
using VDM.Runtime.Events.Models;
using VDM.Runtime.Events.Services;


namespace VDM.Runtime.Events.Integration
{
    /// <summary>
    /// Unity MonoBehaviour EventManager that provides Unity lifecycle management
    /// and integration with the backend event system.
    /// </summary>
    public class EventManager : MonoBehaviour
    {
        [Header("Event System Configuration")]
        [SerializeField] private bool enableDebugLogging = true;
        [SerializeField] private bool persistThroughScenes = true;

        private static EventManager _instance;
        private IEventDispatcher _eventDispatcher;
        private bool _isInitialized = false;

        /// <summary>
        /// Singleton instance of EventManager
        /// </summary>
        public static EventManager Instance
        {
            get
            {
                if (_instance == null)
                {
                    _instance = FindObjectOfType<EventManager>();
                    if (_instance == null)
                    {
                        GameObject go = new GameObject("EventManager");
                        _instance = go.AddComponent<EventManager>();
                    }
                }
                return _instance;
            }
        }

        /// <summary>
        /// Event dispatcher for publishing and subscribing to events
        /// </summary>
        public static IEventDispatcher Dispatcher => Instance._eventDispatcher;

        private void Awake()
        {
            // Ensure singleton pattern
            if (_instance != null && _instance != this)
            {
                Destroy(gameObject);
                return;
            }

            _instance = this;
            
            if (persistThroughScenes)
            {
                DontDestroyOnLoad(gameObject);
            }

            Initialize();
        }

        private void Initialize()
        {
            if (_isInitialized)
                return;

            _eventDispatcher = new EventDispatcher();
            _isInitialized = true;

            if (enableDebugLogging)
            {
                Debug.Log("EventManager initialized successfully");
            }

            // Publish system initialized event
            PublishSystemEvent(EventTypes.SystemInitialized, "EventManager");
        }

        private void OnDestroy()
        {
            if (_instance == this)
            {
                // Publish system shutdown event
                PublishSystemEvent(EventTypes.SystemShutdown, "EventManager");
                
                // Clear all subscriptions
                _eventDispatcher?.ClearAllSubscriptions();
                
                if (enableDebugLogging)
                {
                    Debug.Log("EventManager destroyed and cleaned up");
                }
            }
        }

        #region Public API

        /// <summary>
        /// Subscribe to events of a specific type
        /// </summary>
        /// <typeparam name="T">Event type to subscribe to</typeparam>
        /// <param name="handler">Handler function to call when event is published</param>
        public static void Subscribe<T>(Action<T> handler) where T : IEvent
        {
            Instance._eventDispatcher?.Subscribe(handler);
        }

        /// <summary>
        /// Subscribe to events by type string
        /// </summary>
        /// <param name="eventType">Event type string to subscribe to</param>
        /// <param name="handler">Handler function to call when event is published</param>
        public static void Subscribe(string eventType, Action<IEvent> handler)
        {
            Instance._eventDispatcher?.Subscribe(eventType, handler);
        }

        /// <summary>
        /// Unsubscribe from events of a specific type
        /// </summary>
        /// <typeparam name="T">Event type to unsubscribe from</typeparam>
        /// <param name="handler">Handler function to remove</param>
        public static void Unsubscribe<T>(Action<T> handler) where T : IEvent
        {
            Instance._eventDispatcher?.Unsubscribe(handler);
        }

        /// <summary>
        /// Unsubscribe from events by type string
        /// </summary>
        /// <param name="eventType">Event type string to unsubscribe from</param>
        /// <param name="handler">Handler function to remove</param>
        public static void Unsubscribe(string eventType, Action<IEvent> handler)
        {
            Instance._eventDispatcher?.Unsubscribe(eventType, handler);
        }

        /// <summary>
        /// Publish an event to all subscribers
        /// </summary>
        /// <typeparam name="T">Event type</typeparam>
        /// <param name="eventData">Event data to publish</param>
        public static void Publish<T>(T eventData) where T : IEvent
        {
            Instance._eventDispatcher?.Publish(eventData);
        }

        /// <summary>
        /// Publish a simple system event
        /// </summary>
        /// <param name="eventType">Type of the event</param>
        /// <param name="source">Source system</param>
        /// <param name="priority">Event priority</param>
        public static void PublishSystemEvent(string eventType, string source, EventPriority priority = EventPriority.Normal)
        {
            var systemEvent = new SystemEvent(eventType, source, priority);
            Publish(systemEvent);
        }

        /// <summary>
        /// Get the number of subscribers for a specific event type
        /// </summary>
        /// <param name="eventType">Event type to check</param>
        /// <returns>Number of subscribers</returns>
        public static int GetSubscriberCount(string eventType)
        {
            return Instance._eventDispatcher?.GetSubscriberCount(eventType) ?? 0;
        }

        #endregion

        #region Unity Lifecycle Events

        private void Start()
        {
            PublishSystemEvent(EventTypes.GameStarted, "EventManager");
        }

        private void OnApplicationPause(bool pauseStatus)
        {
            if (pauseStatus)
            {
                PublishSystemEvent("application.paused", "EventManager");
            }
            else
            {
                PublishSystemEvent("application.resumed", "EventManager");
            }
        }

        private void OnApplicationFocus(bool hasFocus)
        {
            if (hasFocus)
            {
                PublishSystemEvent("application.focused", "EventManager");
            }
            else
            {
                PublishSystemEvent("application.unfocused", "EventManager");
            }
        }

        #endregion
    }

    /// <summary>
    /// Basic system event implementation
    /// </summary>
    [Serializable]
    public class SystemEvent : BaseEvent
    {
        public SystemEvent(string eventType, string source, EventPriority priority = EventPriority.Normal) 
            : base(eventType, source, priority)
        {
        }

        public SystemEvent() : base()
        {
            // For Unity serialization
        }
    }
} 