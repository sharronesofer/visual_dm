using UnityEngine;

namespace VDM.Runtime.Core.Systems
{
    /// <summary>
    /// Base class for system managers
    /// </summary>
    public abstract class SystemManager : MonoBehaviour, ISystemManager
    {
        [Header("System Configuration")]
        [SerializeField] protected bool autoInitialize = true;
        [SerializeField] protected string systemName = "";
        
        public virtual string SystemName => string.IsNullOrEmpty(systemName) ? GetType().Name : systemName;
        public bool IsInitialized { get; protected set; } = false;
        public SystemHealthStatus HealthStatus { get; protected set; } = SystemHealthStatus.Unknown;
        
        protected virtual void Start()
        {
            if (autoInitialize)
            {
                InitializeSystem();
            }
        }
        
        public virtual void InitializeSystem()
        {
            if (IsInitialized)
            {
                Debug.LogWarning($"System {SystemName} already initialized");
                return;
            }
            
            Debug.Log($"Initializing system: {SystemName}");
            OnInitializeSystem();
            IsInitialized = true;
            HealthStatus = SystemHealthStatus.Healthy;
        }
        
        public virtual void ShutdownSystem()
        {
            if (!IsInitialized)
            {
                Debug.LogWarning($"System {SystemName} not initialized");
                return;
            }
            
            Debug.Log($"Shutting down system: {SystemName}");
            OnShutdownSystem();
            IsInitialized = false;
            HealthStatus = SystemHealthStatus.Unknown;
        }
        
        public virtual void UpdateSystem()
        {
            if (!IsInitialized)
            {
                return;
            }
            
            OnUpdateSystem();
        }
        
        public virtual SystemHealthStatus GetHealthStatus()
        {
            return HealthStatus;
        }
        
        protected abstract void OnInitializeSystem();
        protected abstract void OnShutdownSystem();
        protected virtual void OnUpdateSystem() { }
        
        protected virtual void Update()
        {
            UpdateSystem();
        }
    }
} 