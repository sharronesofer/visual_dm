using System;
using System.IO;
using System.Text.RegularExpressions;

namespace Visual_DM.Storage
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
        /// Generates a safe filename from an arbitrary string.
        /// </summary>
        public static string SafeFilename(string name)
        {
            var invalid = new string(Path.GetInvalidFileNameChars());
            var regex = new Regex($"[{Regex.Escape(invalid)}]");
            return regex.Replace(name, "_");
        }
    }
} 