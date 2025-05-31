using System;
using System.Threading.Tasks;

namespace VDM.Infrastructure.Core.Core.Systems
{
    /// <summary>
    /// Interface for all game systems in Unity frontend
    /// </summary>
    public interface IGameSystem
    {
        /// <summary>
        /// System name identifier
        /// </summary>
        string SystemName { get; }

        /// <summary>
        /// Whether the system is currently active
        /// </summary>
        bool IsActive { get; }

        /// <summary>
        /// Initialize the system
        /// </summary>
        Task InitializeAsync();

        /// <summary>
        /// Start the system
        /// </summary>
        Task StartAsync();

        /// <summary>
        /// Stop the system
        /// </summary>
        Task StopAsync();

        /// <summary>
        /// Shutdown the system
        /// </summary>
        Task ShutdownAsync();

        /// <summary>
        /// Update system state
        /// </summary>
        void Update();

        /// <summary>
        /// Handle system events
        /// </summary>
        void HandleEvent(object eventData);
    }
} 