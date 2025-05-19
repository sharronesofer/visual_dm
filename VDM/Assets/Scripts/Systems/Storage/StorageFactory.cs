using System;

namespace VisualDM.Storage
{
    /// <summary>
    /// Factory for creating storage provider instances.
    /// </summary>
    public static class StorageFactory
    {
        /// <summary>
        /// Gets a storage provider based on the given type and configuration.
        /// </summary>
        /// <param name="type">The type of storage provider (e.g., "filesystem").</param>
        /// <param name="config">Configuration string (e.g., root directory for filesystem).</param>
        /// <returns>An IStorageProvider instance.</returns>
        public static IStorageProvider GetProvider(string type, string config)
        {
            switch (type.ToLower())
            {
                case "filesystem":
                    return new FileSystemStorageProvider(config);
                case "sqlite":
                    return new SQLiteStorageProvider(config);
                case "cloud":
                    return new CloudStorageProvider(config);
                default:
                    throw new ArgumentException($"Unknown storage provider type: {type}");
            }
        }
    }
} 