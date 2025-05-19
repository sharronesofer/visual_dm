using System;
using System.IO;
using System.Text.RegularExpressions;

namespace VisualDM.Storage
{
    /// <summary>
    /// Utility methods for storage path normalization and security.
    /// </summary>
    public static class StorageUtils
    {
        /// <summary>
        /// Normalizes a path to use forward slashes and trims whitespace.
        /// </summary>
        public static string NormalizePath(string path)
        {
            if (string.IsNullOrWhiteSpace(path))
                throw new ArgumentException("Path cannot be null or empty.");
            return path.Replace("\\", "/").Trim();
        }

        /// <summary>
        /// Validates that a path does not contain traversal or invalid characters.
        /// </summary>
        public static void ValidatePath(string path)
        {
            if (path.Contains(".."))
                throw new UnauthorizedAccessException("Path traversal is not allowed.");
            if (path.IndexOfAny(Path.GetInvalidPathChars()) >= 0)
                throw new ArgumentException("Path contains invalid characters.");
        }

        /// <summary>
        /// Generates a safe filename for a given key (removes invalid characters).
        /// </summary>
        public static string SafeFilename(string key)
        {
            foreach (var c in System.IO.Path.GetInvalidFileNameChars())
                key = key.Replace(c, '_');
            return key;
        }

        /// <summary>
        /// Generates a versioned save file name for migration support.
        /// </summary>
        public static string VersionedSaveName(string baseName, int version)
        {
            return $"{SafeFilename(baseName)}_v{version}.dat";
        }
    }
} 