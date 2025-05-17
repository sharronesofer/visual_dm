using System;
using System.Collections.Generic;
using System.Threading;
using UnityEngine;

namespace Core.Utils
{
    /// <summary>
    /// Thread-safe ID Generator with improved uniqueness guarantees
    /// and compatibility with Python-generated IDs.
    /// </summary>
    public class IDGenerator
    {
        private static readonly object _lock = new object();
        private static HashSet<string> _generatedIds = new HashSet<string>();
        private static int _collisionCount = 0;
        private static int _sequenceCounter = 0;
        
        // Singleton instance
        private static IDGenerator _instance;
        
        /// <summary>
        /// Singleton access to the IDGenerator
        /// </summary>
        public static IDGenerator Instance
        {
            get
            {
                if (_instance == null)
                {
                    _instance = new IDGenerator();
                }
                return _instance;
            }
        }
        
        /// <summary>
        /// Generates a unique, sortable identifier using timestamp, sequence counter,
        /// and random string with collision detection.
        /// </summary>
        /// <param name="prefix">Optional string prefix to identify the source/type of ID</param>
        /// <returns>A unique string identifier, compatible with Python-generated IDs</returns>
        public string GenerateUniqueId(string prefix = "")
        {
            lock (_lock)
            {
                // Increment sequence to ensure uniqueness even if generated in same millisecond
                _sequenceCounter = (_sequenceCounter + 1) % 10000;
                
                // Get current timestamp (milliseconds since epoch)
                long timestamp = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds();
                
                // Generate random string for uniqueness
                string randomStr = GenerateRandomString(8);
                
                // Format with same pattern as Python implementation for compatibility
                string baseId = $"{prefix}{timestamp:D15}_{_sequenceCounter:D4}_{randomStr}";
                
                // Check for collisions (extremely unlikely but handled for robustness)
                if (_generatedIds.Contains(baseId))
                {
                    _collisionCount++;
                    // Add collision count to ensure uniqueness
                    baseId = $"{baseId}_{_collisionCount}";
                }
                
                // Store ID to detect any future collisions
                _generatedIds.Add(baseId);
                return baseId;
            }
        }
        
        /// <summary>
        /// Generates a UUID (v4 or v5).
        /// </summary>
        /// <param name="namespaceName">Optional namespace for generating a v5 UUID</param>
        /// <param name="name">Optional name for generating a v5 UUID</param>
        /// <returns>A string representation of the UUID</returns>
        public string GenerateUuid(string namespaceName = null, string name = null)
        {
            if (!string.IsNullOrEmpty(namespaceName) && !string.IsNullOrEmpty(name))
            {
                // Generate a v5 UUID (deterministic based on namespace and name)
                Guid namespaceGuid;
                if (!Guid.TryParse(namespaceName, out namespaceGuid))
                {
                    namespaceGuid = NamespaceStringToGuid(namespaceName);
                }
                
                byte[] nameBytes = System.Text.Encoding.UTF8.GetBytes(name);
                byte[] namespaceBytes = namespaceGuid.ToByteArray();
                
                // Create v5 UUID using the same algorithm as Python's uuid5
                Guid uuid5 = CreateUuidV5(namespaceBytes, nameBytes);
                return uuid5.ToString();
            }
            else
            {
                // Generate a random v4 UUID
                return Guid.NewGuid().ToString();
            }
        }
        
        /// <summary>
        /// Clears the cache of generated IDs.
        /// Should be used carefully, typically for testing or when ID history is no longer needed.
        /// </summary>
        public void ClearIdCache()
        {
            lock (_lock)
            {
                _generatedIds.Clear();
                _collisionCount = 0;
            }
        }
        
        #region Helper Methods
        
        /// <summary>
        /// Creates a v5 UUID following RFC 4122.
        /// </summary>
        private Guid CreateUuidV5(byte[] namespaceBytes, byte[] nameBytes)
        {
            byte[] combined = new byte[namespaceBytes.Length + nameBytes.Length];
            Buffer.BlockCopy(namespaceBytes, 0, combined, 0, namespaceBytes.Length);
            Buffer.BlockCopy(nameBytes, 0, combined, namespaceBytes.Length, nameBytes.Length);
            
            // Compute SHA1 hash (similar to Python's uuid5 implementation)
            var sha1 = System.Security.Cryptography.SHA1.Create();
            byte[] hashBytes = sha1.ComputeHash(combined);
            
            // Set version and variant bits
            hashBytes[6] = (byte)((hashBytes[6] & 0x0F) | 0x50); // Version 5
            hashBytes[8] = (byte)((hashBytes[8] & 0x3F) | 0x80); // Variant RFC 4122
            
            // Create a Guid from the hash bytes
            byte[] guidBytes = new byte[16];
            Array.Copy(hashBytes, 0, guidBytes, 0, 16);
            return new Guid(guidBytes);
        }
        
        /// <summary>
        /// Generates a random alphanumeric string of specified length.
        /// </summary>
        private string GenerateRandomString(int length)
        {
            const string chars = "abcdefghijklmnopqrstuvwxyz0123456789";
            char[] result = new char[length];
            
            using (var rng = new System.Security.Cryptography.RNGCryptoServiceProvider())
            {
                byte[] randomBytes = new byte[length];
                rng.GetBytes(randomBytes);
                
                for (int i = 0; i < length; i++)
                {
                    result[i] = chars[randomBytes[i] % chars.Length];
                }
            }
            
            return new string(result);
        }
        
        /// <summary>
        /// Converts a string to a deterministic Guid.
        /// </summary>
        private Guid NamespaceStringToGuid(string value)
        {
            byte[] bytes = System.Text.Encoding.UTF8.GetBytes(value);
            var md5 = System.Security.Cryptography.MD5.Create();
            byte[] hashBytes = md5.ComputeHash(bytes);
            
            // Create a Guid from the hash bytes
            byte[] guidBytes = new byte[16];
            Array.Copy(hashBytes, 0, guidBytes, 0, 16);
            return new Guid(guidBytes);
        }
        
        #endregion
    }
    
    /// <summary>
    /// Static helper class for ID generation that uses the singleton IDGenerator internally.
    /// Provides compatibility with non-OOP code that needs to generate IDs.
    /// </summary>
    public static class IDHelper
    {
        /// <summary>
        /// Generates a unique ID using the singleton IDGenerator.
        /// </summary>
        /// <param name="prefix">Optional prefix for the ID</param>
        /// <returns>A unique ID string</returns>
        public static string GenerateUniqueId(string prefix = "")
        {
            return IDGenerator.Instance.GenerateUniqueId(prefix);
        }
        
        /// <summary>
        /// Generates a UUID using the singleton IDGenerator.
        /// </summary>
        /// <param name="namespaceName">Optional namespace for v5 UUID</param>
        /// <param name="name">Optional name for v5 UUID</param>
        /// <returns>A UUID string</returns>
        public static string GenerateUuid(string namespaceName = null, string name = null)
        {
            return IDGenerator.Instance.GenerateUuid(namespaceName, name);
        }
    }
} 