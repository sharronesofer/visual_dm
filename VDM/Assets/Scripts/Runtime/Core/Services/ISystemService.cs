using System;

namespace VDM.Runtime.Core.Services
{
    /// <summary>
    /// Interface for all system services providing common functionality
    /// </summary>
    public interface ISystemService
    {
        /// <summary>
        /// Initialize the service
        /// </summary>
        void Initialize();

        /// <summary>
        /// Clean up the service
        /// </summary>
        void Cleanup();
    }
} 