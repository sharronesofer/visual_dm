using System;

namespace Visual_DM.Storage
{
    /// <summary>
    /// Factory for creating storage provider instances.
    /// </summary>
    public static class StorageFactory
    {
        /// <summary>
        /// Gets a storage provider based on the given type and configuration.
        /// </summary>
        /// <param name="providerType">The type of storage provider (e.g., "filesystem").</param>
        /// <param name="config">Configuration string (e.g., root directory for filesystem).</param>
        /// <returns>An IStorageProvider instance.</returns>
        public static IStorageProvider GetProvider(string providerType, string config)
        {
            switch (providerType.ToLowerInvariant())
            {
                case "filesystem":
                    return new FileSystemStorageProvider(config);
                // Future: add cases for other providers (e.g., cloud, database)
                default:
                    throw new NotSupportedException($"Unknown storage provider type: {providerType}");
            }
        }
    }
} 