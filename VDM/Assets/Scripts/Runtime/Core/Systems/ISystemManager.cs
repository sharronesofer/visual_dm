using System;

namespace VDM.Runtime.Core.Systems
{
    /// <summary>
    /// Interface for system managers
    /// </summary>
    public interface ISystemManager
    {
        string SystemName { get; }
        bool IsInitialized { get; }
        SystemHealthStatus HealthStatus { get; }
        
        void InitializeSystem();
        void ShutdownSystem();
        void UpdateSystem();
        SystemHealthStatus GetHealthStatus();
    }
    
    /// <summary>
    /// System health status enumeration
    /// </summary>
    public enum SystemHealthStatus
    {
        Unknown,
        Healthy,
        Warning,
        Error,
        Critical
    }
} 