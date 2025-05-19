using System;
using System.IO;
using System.Security.Cryptography;
using System.Text;

namespace VisualDM.Storage
{
    /// <summary>
    /// Provides AES-256 encryption/decryption and HMAC integrity for storage.
    /// </summary>
    public class EncryptionService : PersistenceManager.IEncryptionService
    {
        private readonly byte[] _key;
        private readonly byte[] _hmacKey;

        /// <summary>
        /// Create an EncryptionService with a 256-bit key and HMAC key.
        /// </summary>
        public EncryptionService(byte[] key, byte[] hmacKey)
        {
            if (key.Length != 32) throw new ArgumentException("Key must be 32 bytes (256 bits)");
            if (hmacKey.Length != 32) throw new ArgumentException("HMAC key must be 32 bytes (256 bits)");
            _key = key;
            _hmacKey = hmacKey;
        }

        /// <summary>
        /// Encrypts data with AES-256-CBC and appends HMAC-SHA256 for integrity.
        /// </summary>
        public byte[] Encrypt(byte[] data)
        {
            using var aes = Aes.Create();
            aes.Key = _key;
            aes.GenerateIV();
            aes.Mode = CipherMode.CBC;
            using var encryptor = aes.CreateEncryptor();
            var cipher = encryptor.TransformFinalBlock(data, 0, data.Length);
            // Combine IV + cipher
            var combined = new byte[aes.IV.Length + cipher.Length];
            Buffer.BlockCopy(aes.IV, 0, combined, 0, aes.IV.Length);
            Buffer.BlockCopy(cipher, 0, combined, aes.IV.Length, cipher.Length);
            // Compute HMAC
            using var hmac = new HMACSHA256(_hmacKey);
            var tag = hmac.ComputeHash(combined);
            // Combine all: IV + cipher + HMAC
            var result = new byte[combined.Length + tag.Length];
            Buffer.BlockCopy(combined, 0, result, 0, combined.Length);
            Buffer.BlockCopy(tag, 0, result, combined.Length, tag.Length);
            return result;
        }

        /// <summary>
        /// Decrypts data with AES-256-CBC and verifies HMAC-SHA256.
        /// </summary>
        public byte[] Decrypt(byte[] encrypted)
        {
            // Extract IV, cipher, HMAC
            int ivLen = 16, tagLen = 32;
            if (encrypted.Length < ivLen + tagLen) throw new ArgumentException("Invalid encrypted data");
            var tag = new byte[tagLen];
            Buffer.BlockCopy(encrypted, encrypted.Length - tagLen, tag, 0, tagLen);
            var combined = new byte[encrypted.Length - tagLen];
            Buffer.BlockCopy(encrypted, 0, combined, 0, combined.Length);
            // Verify HMAC
            using var hmac = new HMACSHA256(_hmacKey);
            var computed = hmac.ComputeHash(combined);
            if (!CryptographicOperations.FixedTimeEquals(tag, computed))
                throw new CryptographicException("HMAC validation failed");
            // Extract IV and cipher
            var iv = new byte[ivLen];
            Buffer.BlockCopy(combined, 0, iv, 0, ivLen);
            var cipher = new byte[combined.Length - ivLen];
            Buffer.BlockCopy(combined, ivLen, cipher, 0, cipher.Length);
            using var aes = Aes.Create();
            aes.Key = _key;
            aes.IV = iv;
            aes.Mode = CipherMode.CBC;
            using var decryptor = aes.CreateDecryptor();
            return decryptor.TransformFinalBlock(cipher, 0, cipher.Length);
        }

        /// <summary>
        /// Derives a 256-bit key and HMAC key from a password and salt using PBKDF2.
        /// </summary>
        public static (byte[] key, byte[] hmacKey) DeriveKeys(string password, byte[] salt, int iterations = 100_000)
        {
            using var pbkdf2 = new Rfc2898DeriveBytes(password, salt, iterations, HashAlgorithmName.SHA256);
            var key = pbkdf2.GetBytes(32);
            var hmacKey = pbkdf2.GetBytes(32);
            return (key, hmacKey);
        }

        /// <summary>
        /// Generates a random 256-bit key.
        /// </summary>
        public static byte[] GenerateRandomKey()
        {
            var key = new byte[32];
            using var rng = RandomNumberGenerator.Create();
            rng.GetBytes(key);
            return key;
        }

        /// <summary>
        /// Stub for secure key storage (platform-specific implementation recommended).
        /// </summary>
        public static void StoreKeySecurely(string keyName, byte[] key)
        {
            // TODO: Implement platform-specific secure storage (e.g., Keychain, DPAPI, Android Keystore)
            File.WriteAllBytes($"{keyName}.key", key);
        }

        public static byte[] LoadKeySecurely(string keyName)
        {
            // TODO: Implement platform-specific secure storage
            return File.ReadAllBytes($"{keyName}.key");
        }
    }
} 