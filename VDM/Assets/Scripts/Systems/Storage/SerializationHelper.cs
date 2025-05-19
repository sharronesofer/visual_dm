using System;
using System.IO;
using System.Text.Json;
using System.Runtime.Serialization.Formatters.Binary;

namespace VisualDM.Storage
{
    /// <summary>
    /// Helper class for standardized serialization and deserialization with versioning and validation.
    /// </summary>
    public static class SerializationHelper
    {
        /// <summary>
        /// Serializes an object to JSON (UTF-8 bytes).
        /// </summary>
        public static byte[] ToJsonBytes<T>(T obj)
        {
            return JsonSerializer.SerializeToUtf8Bytes(obj);
        }

        /// <summary>
        /// Deserializes an object from JSON (UTF-8 bytes).
        /// </summary>
        public static T FromJsonBytes<T>(byte[] data)
        {
            return JsonSerializer.Deserialize<T>(data);
        }

        /// <summary>
        /// Serializes an object to binary (byte array). WARNING: BinaryFormatter is obsolete and insecure for untrusted data.
        /// </summary>
        public static byte[] ToBinary<T>(T obj)
        {
            using var ms = new MemoryStream();
#pragma warning disable SYSLIB0011
            new BinaryFormatter().Serialize(ms, obj);
#pragma warning restore SYSLIB0011
            return ms.ToArray();
        }

        /// <summary>
        /// Deserializes an object from binary (byte array). WARNING: BinaryFormatter is obsolete and insecure for untrusted data.
        /// </summary>
        public static T FromBinary<T>(byte[] data)
        {
            using var ms = new MemoryStream(data);
#pragma warning disable SYSLIB0011
            return (T)new BinaryFormatter().Deserialize(ms);
#pragma warning restore SYSLIB0011
        }

        /// <summary>
        /// Validates that the deserialized object matches the expected schema version.
        /// </summary>
        public static bool ValidateVersioned<T>(T obj, int expectedVersion) where T : IStorable
        {
            return obj.DataVersion == expectedVersion;
        }

        /// <summary>
        /// Attempts to migrate data from an old version to the current version using a user-provided migration function.
        /// </summary>
        public static T Migrate<T>(T oldObj, int fromVersion, int toVersion, Func<T, int, int, T> migrationFunc)
        {
            return migrationFunc(oldObj, fromVersion, toVersion);
        }
    }
} 