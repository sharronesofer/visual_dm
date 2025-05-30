using System.Collections.Generic;
using System;
using UnityEngine;
using VDM.Runtime.Core.Services;


namespace VDM.Runtime.Core.Integration
{
    /// <summary>
    /// Base class for system managers that handle Unity system lifecycle and integration
    /// Provides common functionality for managing system services, UI, and events
    /// </summary>
    public abstract class SystemManager : MonoBehaviour
    {
        [Header("System Manager Base Configuration")]
        [SerializeField] protected bool autoInitialize = true;
        [SerializeField] protected bool debugLogging = false;
        [SerializeField] protected int initializationOrder = 0;

        // System state
        protected bool _isInitialized = false;
        protected bool _isShuttingDown = false;
        
        // Service management
        protected Dictionary<Type, MonoBehaviour> _services = new Dictionary<Type, MonoBehaviour>();
        protected Dictionary<string, GameObject> _systemGameObjects = new Dictionary<string, GameObject>();

        // Events
        public event Action<SystemManager> OnSystemInitialized;
        public event Action<SystemManager> OnSystemShutdown;
        public event Action<string> OnSystemError;

        #region Unity Lifecycle

        protected virtual void Awake()
        {
            if (autoInitialize)
            {
                InitializeSystem();
            }
        }

        protected virtual void Start()
        {
            // Override in derived classes if needed
        }

        protected virtual void OnDestroy()
        {
            if (!_isShuttingDown)
            {
                ShutdownSystem();
            }
        }

        protected virtual void OnApplicationPause(bool pauseStatus)
        {
            // Override in derived classes to handle application pause/resume
        }

        protected virtual void OnApplicationFocus(bool hasFocus)
        {
            // Override in derived classes to handle application focus changes
        }

        #endregion

        #region System Lifecycle

        /// <summary>
        /// Initialize the system manager
        /// </summary>
        public virtual void InitializeSystem()
        {
            if (_isInitialized)
            {
                Debug.LogWarning($"[{GetSystemName()}] System already initialized!");
                return;
            }

            try
            {
                if (debugLogging)
                    Debug.Log($"[{GetSystemName()}] Initializing system...");

                // Initialize services first
                InitializeServices();

                // Then initialize the system-specific components
                InitializeSystemComponents();

                _isInitialized = true;
                OnSystemInitialized?.Invoke(this);

                if (debugLogging)
                    Debug.Log($"[{GetSystemName()}] System initialized successfully");
            }
            catch (Exception e)
            {
                HandleSystemError($"Failed to initialize system: {e.Message}", e);
            }
        }

        /// <summary>
        /// Shutdown the system manager
        /// </summary>
        public virtual void ShutdownSystem()
        {
            if (_isShuttingDown)
            {
                return;
            }

            _isShuttingDown = true;

            try
            {
                if (debugLogging)
                    Debug.Log($"[{GetSystemName()}] Shutting down system...");

                // Shutdown system-specific components first
                ShutdownSystemComponents();

                // Then shutdown services
                ShutdownServices();

                _isInitialized = false;
                OnSystemShutdown?.Invoke(this);

                if (debugLogging)
                    Debug.Log($"[{GetSystemName()}] System shutdown complete");
            }
            catch (Exception e)
            {
                HandleSystemError($"Error during system shutdown: {e.Message}", e);
            }
        }

        /// <summary>
        /// Restart the system manager
        /// </summary>
        public virtual void RestartSystem()
        {
            if (debugLogging)
                Debug.Log($"[{GetSystemName()}] Restarting system...");

            ShutdownSystem();
            _isShuttingDown = false;
            InitializeSystem();
        }

        #endregion

        #region Service Management

        /// <summary>
        /// Get or create a service of the specified type
        /// </summary>
        protected T GetOrCreateService<T>() where T : MonoBehaviour
        {
            Type serviceType = typeof(T);
            
            if (_services.ContainsKey(serviceType))
            {
                return _services[serviceType] as T;
            }

            // Try to find existing service in the scene
            T existingService = FindObjectOfType<T>();
            if (existingService != null)
            {
                _services[serviceType] = existingService;
                return existingService;
            }

            // Create new service
            GameObject serviceGO = new GameObject($"{serviceType.Name}_Service");
            serviceGO.transform.SetParent(transform);
            
            T newService = serviceGO.AddComponent<T>();
            _services[serviceType] = newService;
            
            if (debugLogging)
                Debug.Log($"[{GetSystemName()}] Created new service: {serviceType.Name}");

            return newService;
        }

        /// <summary>
        /// Get a service of the specified type
        /// </summary>
        protected T GetService<T>() where T : MonoBehaviour
        {
            Type serviceType = typeof(T);
            return _services.ContainsKey(serviceType) ? _services[serviceType] as T : null;
        }

        /// <summary>
        /// Register an existing service
        /// </summary>
        protected void RegisterService<T>(T service) where T : MonoBehaviour
        {
            if (service == null) return;

            Type serviceType = typeof(T);
            _services[serviceType] = service;
            
            if (debugLogging)
                Debug.Log($"[{GetSystemName()}] Registered service: {serviceType.Name}");
        }

        /// <summary>
        /// Unregister a service
        /// </summary>
        protected void UnregisterService<T>() where T : MonoBehaviour
        {
            Type serviceType = typeof(T);
            if (_services.ContainsKey(serviceType))
            {
                _services.Remove(serviceType);
                
                if (debugLogging)
                    Debug.Log($"[{GetSystemName()}] Unregistered service: {serviceType.Name}");
            }
        }

        #endregion

        #region GameObject Management

        /// <summary>
        /// Create and register a system GameObject
        /// </summary>
        protected GameObject CreateSystemGameObject(string name, Transform parent = null)
        {
            if (_systemGameObjects.ContainsKey(name))
            {
                Debug.LogWarning($"[{GetSystemName()}] GameObject '{name}' already exists!");
                return _systemGameObjects[name];
            }

            GameObject go = new GameObject(name);
            if (parent != null)
                go.transform.SetParent(parent);
            else
                go.transform.SetParent(transform);

            _systemGameObjects[name] = go;
            
            if (debugLogging)
                Debug.Log($"[{GetSystemName()}] Created system GameObject: {name}");

            return go;
        }

        /// <summary>
        /// Get a system GameObject by name
        /// </summary>
        protected GameObject GetSystemGameObject(string name)
        {
            return _systemGameObjects.ContainsKey(name) ? _systemGameObjects[name] : null;
        }

        /// <summary>
        /// Remove and destroy a system GameObject
        /// </summary>
        protected void RemoveSystemGameObject(string name)
        {
            if (_systemGameObjects.ContainsKey(name))
            {
                GameObject go = _systemGameObjects[name];
                _systemGameObjects.Remove(name);
                
                if (go != null)
                {
                    if (Application.isPlaying)
                        Destroy(go);
                    else
                        DestroyImmediate(go);
                }
                
                if (debugLogging)
                    Debug.Log($"[{GetSystemName()}] Removed system GameObject: {name}");
            }
        }

        #endregion

        #region Abstract Methods

        /// <summary>
        /// Get the name of this system (for logging and identification)
        /// </summary>
        protected virtual string GetSystemName()
        {
            return GetType().Name;
        }

        /// <summary>
        /// Initialize system-specific services
        /// Override in derived classes to initialize required services
        /// </summary>
        protected virtual void InitializeServices()
        {
            // Override in derived classes
        }

        /// <summary>
        /// Initialize system-specific components
        /// Override in derived classes to initialize system components
        /// </summary>
        protected virtual void InitializeSystemComponents()
        {
            // Override in derived classes
        }

        /// <summary>
        /// Shutdown system-specific components
        /// Override in derived classes to clean up system components
        /// </summary>
        protected virtual void ShutdownSystemComponents()
        {
            // Override in derived classes
        }

        /// <summary>
        /// Shutdown system-specific services
        /// Override in derived classes to clean up services
        /// </summary>
        protected virtual void ShutdownServices()
        {
            // Cleanup all registered services
            foreach (var kvp in _services)
            {
                if (kvp.Value != null)
                {
                    if (Application.isPlaying)
                        Destroy(kvp.Value.gameObject);
                    else
                        DestroyImmediate(kvp.Value.gameObject);
                }
            }
            _services.Clear();

            // Cleanup all system GameObjects
            foreach (var kvp in _systemGameObjects)
            {
                if (kvp.Value != null)
                {
                    if (Application.isPlaying)
                        Destroy(kvp.Value);
                    else
                        DestroyImmediate(kvp.Value);
                }
            }
            _systemGameObjects.Clear();
        }

        #endregion

        #region Properties

        /// <summary>
        /// Check if the system is initialized
        /// </summary>
        public bool IsInitialized => _isInitialized;

        /// <summary>
        /// Check if the system is shutting down
        /// </summary>
        public bool IsShuttingDown => _isShuttingDown;

        /// <summary>
        /// Get the initialization order for this system
        /// </summary>
        public int InitializationOrder => initializationOrder;

        #endregion

        #region Error Handling

        /// <summary>
        /// Handle system errors
        /// </summary>
        protected virtual void HandleSystemError(string message, Exception exception = null)
        {
            string fullMessage = $"[{GetSystemName()}] {message}";
            
            if (exception != null)
            {
                Debug.LogError($"{fullMessage}\nException: {exception}");
            }
            else
            {
                Debug.LogError(fullMessage);
            }

            OnSystemError?.Invoke(fullMessage);
        }

        #endregion

        #region Utility Methods

        /// <summary>
        /// Check if a service is available
        /// </summary>
        protected bool IsServiceAvailable<T>() where T : MonoBehaviour
        {
            return _services.ContainsKey(typeof(T)) && _services[typeof(T)] != null;
        }

        /// <summary>
        /// Get system status for debugging
        /// </summary>
        public virtual string GetSystemStatus()
        {
            return $"System: {GetSystemName()}, Initialized: {_isInitialized}, " +
                   $"Services: {_services.Count}, GameObjects: {_systemGameObjects.Count}";
        }

        #endregion
    }
} 