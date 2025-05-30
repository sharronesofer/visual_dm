using System.Collections.Generic;
using System.Threading.Tasks;
using System;
using UnityEngine;
using VDM.Runtime.Core.Events;


namespace VDM.Runtime.Core.Patterns
{
    /// <summary>
    /// Base class for system managers that handle Unity lifecycle integration
    /// </summary>
    public abstract class SystemManager : MonoBehaviour
    {
        [SerializeField] protected bool _initializeOnAwake = true;
        [SerializeField] protected bool _enableLogging = true;
        
        protected bool _isInitialized = false;
        protected readonly List<string> _dependencies = new List<string>();

        protected virtual void Awake()
        {
            if (_initializeOnAwake)
            {
                _ = InitializeAsync();
            }
        }

        protected virtual void OnDestroy()
        {
            ShutdownSystem();
        }

        public virtual async Task InitializeAsync()
        {
            if (_isInitialized)
                return;

            LogMessage($"Initializing {GetType().Name}...");
            
            await CheckDependencies();
            await InitializeSystem();
            
            _isInitialized = true;
            LogMessage($"{GetType().Name} initialized successfully");
        }

        protected abstract Task InitializeSystem();
        protected abstract void ShutdownSystem();

        protected virtual async Task CheckDependencies()
        {
            foreach (var dependency in _dependencies)
            {
                var dependencySystem = FindObjectOfType<SystemManager>();
                if (dependencySystem != null && !dependencySystem._isInitialized)
                {
                    await dependencySystem.InitializeAsync();
                }
            }
        }

        protected virtual void LogMessage(string message)
        {
            if (_enableLogging)
                Debug.Log($"[{GetType().Name}] {message}");
        }

        public bool IsInitialized => _isInitialized;
    }

    /// <summary>
    /// Service locator pattern for dependency injection
    /// </summary>
    public class ServiceLocator : MonoBehaviour
    {
        private static ServiceLocator _instance;
        private readonly Dictionary<Type, object> _services = new Dictionary<Type, object>();

        public static ServiceLocator Instance
        {
            get
            {
                if (_instance == null)
                {
                    _instance = FindObjectOfType<ServiceLocator>();
                    if (_instance == null)
                    {
                        var go = new GameObject("ServiceLocator");
                        _instance = go.AddComponent<ServiceLocator>();
                        DontDestroyOnLoad(go);
                    }
                }
                return _instance;
            }
        }

        private void Awake()
        {
            if (_instance == null)
            {
                _instance = this;
                DontDestroyOnLoad(gameObject);
            }
            else if (_instance != this)
            {
                Destroy(gameObject);
            }
        }

        public void RegisterService<T>(T service)
        {
            var type = typeof(T);
            if (_services.ContainsKey(type))
            {
                Debug.LogWarning($"Service {type.Name} is already registered. Replacing...");
            }
            _services[type] = service;
        }

        public T GetService<T>()
        {
            var type = typeof(T);
            if (_services.TryGetValue(type, out var service))
            {
                return (T)service;
            }
            Debug.LogError($"Service {type.Name} not found!");
            return default(T);
        }

        public bool HasService<T>()
        {
            return _services.ContainsKey(typeof(T));
        }

        public void UnregisterService<T>()
        {
            var type = typeof(T);
            _services.Remove(type);
        }
    }

    /// <summary>
    /// Event bridge for Unity-backend event mapping
    /// </summary>
    public abstract class EventBridge : MonoBehaviour
    {
        protected readonly Dictionary<string, List<Action<object>>> _eventHandlers = new Dictionary<string, List<Action<object>>>();

        protected virtual void Start()
        {
            RegisterEventHandlers();
        }

        protected virtual void OnDestroy()
        {
            UnregisterEventHandlers();
        }

        protected abstract void RegisterEventHandlers();
        protected abstract void UnregisterEventHandlers();

        public virtual void Subscribe(string eventType, Action<object> handler)
        {
            if (!_eventHandlers.ContainsKey(eventType))
            {
                _eventHandlers[eventType] = new List<Action<object>>();
            }
            _eventHandlers[eventType].Add(handler);
        }

        public virtual void Unsubscribe(string eventType, Action<object> handler)
        {
            if (_eventHandlers.ContainsKey(eventType))
            {
                _eventHandlers[eventType].Remove(handler);
            }
        }

        protected virtual void TriggerEvent(string eventType, object data)
        {
            if (_eventHandlers.ContainsKey(eventType))
            {
                foreach (var handler in _eventHandlers[eventType])
                {
                    handler?.Invoke(data);
                }
            }
        }
    }

    /// <summary>
    /// Configuration manager for system settings
    /// </summary>
    public abstract class ConfigurationManager : ScriptableObject
    {
        [SerializeField] protected string _configVersion = "1.0.0";
        [SerializeField] protected bool _enableDebugMode = false;

        public string ConfigVersion => _configVersion;
        public bool EnableDebugMode => _enableDebugMode;

        public abstract void LoadConfiguration();
        public abstract void SaveConfiguration();
        public abstract void ResetToDefaults();

        protected virtual void OnValidate()
        {
            ValidateConfiguration();
        }

        protected abstract void ValidateConfiguration();
    }

    /// <summary>
    /// Cache manager for offline/performance optimization
    /// </summary>
    public abstract class CacheManager
    {
        protected readonly Dictionary<string, object> _cache = new Dictionary<string, object>();
        protected readonly Dictionary<string, DateTime> _cacheTimestamps = new Dictionary<string, DateTime>();
        protected readonly TimeSpan _defaultExpiry = TimeSpan.FromMinutes(5);

        public virtual void Set<T>(string key, T value, TimeSpan? expiry = null)
        {
            _cache[key] = value;
            _cacheTimestamps[key] = DateTime.UtcNow.Add(expiry ?? _defaultExpiry);
        }

        public virtual T Get<T>(string key)
        {
            if (_cache.TryGetValue(key, out var value) && 
                _cacheTimestamps.TryGetValue(key, out var expiry) &&
                DateTime.UtcNow < expiry)
            {
                return (T)value;
            }
            return default(T);
        }

        public virtual bool TryGet<T>(string key, out T value)
        {
            value = Get<T>(key);
            return !EqualityComparer<T>.Default.Equals(value, default(T));
        }

        public virtual void Remove(string key)
        {
            _cache.Remove(key);
            _cacheTimestamps.Remove(key);
        }

        public virtual void Clear()
        {
            _cache.Clear();
            _cacheTimestamps.Clear();
        }

        public virtual void ClearExpired()
        {
            var expiredKeys = new List<string>();
            var now = DateTime.UtcNow;

            foreach (var kvp in _cacheTimestamps)
            {
                if (now >= kvp.Value)
                {
                    expiredKeys.Add(kvp.Key);
                }
            }

            foreach (var key in expiredKeys)
            {
                Remove(key);
            }
        }
    }

    /// <summary>
    /// Event broadcaster for Unity event integration
    /// </summary>
    public class EventBroadcaster : MonoBehaviour
    {
        private static EventBroadcaster _instance;
        
        public static EventBroadcaster Instance
        {
            get
            {
                if (_instance == null)
                {
                    _instance = FindObjectOfType<EventBroadcaster>();
                    if (_instance == null)
                    {
                        var go = new GameObject("EventBroadcaster");
                        _instance = go.AddComponent<EventBroadcaster>();
                        DontDestroyOnLoad(go);
                    }
                }
                return _instance;
            }
        }

        private readonly Dictionary<Type, List<object>> _listeners = new Dictionary<Type, List<object>>();

        private void Awake()
        {
            if (_instance == null)
            {
                _instance = this;
                DontDestroyOnLoad(gameObject);
            }
            else if (_instance != this)
            {
                Destroy(gameObject);
            }
        }

        public void Subscribe<T>(Action<T> listener)
        {
            var eventType = typeof(T);
            if (!_listeners.ContainsKey(eventType))
            {
                _listeners[eventType] = new List<object>();
            }
            _listeners[eventType].Add(listener);
        }

        public void Unsubscribe<T>(Action<T> listener)
        {
            var eventType = typeof(T);
            if (_listeners.ContainsKey(eventType))
            {
                _listeners[eventType].Remove(listener);
            }
        }

        public void Broadcast<T>(T eventData)
        {
            var eventType = typeof(T);
            if (_listeners.ContainsKey(eventType))
            {
                foreach (var listener in _listeners[eventType])
                {
                    ((Action<T>)listener)?.Invoke(eventData);
                }
            }
        }
    }
} 