using System;
using System.Text;
using UnityEngine;

namespace VisualDM.Core
{
    /// <summary>
    /// Utility class for generating unique IDs in Unity
    /// </summary>
    public static class IdGenerator
    {
        private static readonly System.Random Random = new System.Random();
        
        /// <summary>
        /// Generates a unique identifier using a combination of timestamp and random string.
        /// Equivalent to the TypeScript implementation.
        /// </summary>
        /// <returns>A unique string identifier</returns>
        public static string GenerateUniqueId()
        {
            // Get timestamp (milliseconds since epoch)
            var timestamp = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds();
            
            // Generate a random string
            var randomString = GenerateRandomString(10);
            
            return $"{timestamp}_{randomString}";
        }
        
        /// <summary>
        /// Generates a globally unique identifier (GUID)
        /// </summary>
        /// <returns>A string representation of the GUID</returns>
        public static string GenerateGuid()
        {
            return Guid.NewGuid().ToString();
        }
        
        /// <summary>
        /// Generates a UUID with a specific format 
        /// </summary>
        /// <param name="format">Format of the UUID (default is 'N' for 32 digits without hyphens)</param>
        /// <returns>A formatted UUID string</returns>
        public static string GenerateUuid(string format = "N")
        {
            return Guid.NewGuid().ToString(format);
        }
        
        /// <summary>
        /// Generates a deterministic GUID based on a namespace VisualDM.Core
        /// </summary>
        /// <param name="namespace">The namespace VisualDM.Core
        /// <param name="name">The name to hash</param>
        /// <returns>A deterministic GUID based on the inputs</returns>
        public static string GenerateDeterministicGuid(string @namespace, string name)
        {
            // Combine namespace and name
            var combinedBytes = Encoding.UTF8.GetBytes(@namespace + name);
            
            // Use MD5 hashing to create a deterministic GUID
            using (var md5 = System.Security.Cryptography.MD5.Create())
            {
                var hashBytes = md5.ComputeHash(combinedBytes);
                
                // Set the variant and version
                hashBytes[6] = (byte)((hashBytes[6] & 0x0F) | 0x30); // Version 3
                hashBytes[8] = (byte)((hashBytes[8] & 0x3F) | 0x80); // Variant
                
                return new Guid(hashBytes).ToString();
            }
        }
        
        /// <summary>
        /// Generate a random string of the specified length
        /// </summary>
        /// <param name="length">The length of the random string</param>
        /// <returns>A random string</returns>
        private static string GenerateRandomString(int length)
        {
            const string chars = "abcdefghijklmnopqrstuvwxyz0123456789";
            var stringBuilder = new StringBuilder(length);
            
            for (int i = 0; i < length; i++)
            {
                stringBuilder.Append(chars[Random.Next(chars.Length)]);
            }
            
            return stringBuilder.ToString();
        }
        
        /// <summary>
        /// Generates a unique action ID for replay protection, combining timestamp, secure random nonce, and session/user ID.
        /// Use this for all critical actions (e.g., purchases, combat, permission changes) to prevent replay attacks.
        /// Usage:
        ///     var actionId = IdGenerator.GenerateActionId(sessionId);
        ///     // Include actionId in all critical API requests and validate on the backend
        /// </summary>
        /// <param name="sessionId">The user or session identifier to include in the action ID</param>
        /// <returns>A unique action ID string</returns>
        public static string GenerateActionId(string sessionId)
        {
            // High-precision UTC timestamp (ticks)
            var timestamp = DateTime.UtcNow.Ticks;

            // Cryptographically secure random nonce (16 bytes, hex encoded)
            byte[] nonceBytes = new byte[16];
            using (var rng = System.Security.Cryptography.RandomNumberGenerator.Create())
            {
                rng.GetBytes(nonceBytes);
            }
            string nonceHex = BitConverter.ToString(nonceBytes).Replace("-", "").ToLowerInvariant();

            // Compose action ID
            return $"{timestamp}_{nonceHex}_{sessionId}";
        }
    }
} 