using System;
using System.Collections.Generic;
using System.IO;
using UnityEngine;

namespace VisualDM.UI
{
    /// <summary>
    /// Service for validating files before upload. Checks type, size, and optionally content.
    /// </summary>
    public static class FileValidationService
    {
        public static readonly HashSet<string> AllowedExtensions = new HashSet<string> { ".png", ".jpg", ".jpeg", ".gif", ".mp4", ".pdf" };
        public static long MaxFileSizeBytes = 50 * 1024 * 1024; // 50 MB

        public class ValidationResult
        {
            public bool IsValid;
            public string ErrorMessage;
        }

        /// <summary>
        /// Validate a file by path.
        /// </summary>
        public static ValidationResult Validate(string filePath)
        {
            if (!File.Exists(filePath))
                return new ValidationResult { IsValid = false, ErrorMessage = "File does not exist." };

            var ext = Path.GetExtension(filePath).ToLowerInvariant();
            if (!AllowedExtensions.Contains(ext))
                return new ValidationResult { IsValid = false, ErrorMessage = $"Invalid file type: {ext}" };

            var fileInfo = new FileInfo(filePath);
            if (fileInfo.Length > MaxFileSizeBytes)
                return new ValidationResult { IsValid = false, ErrorMessage = $"File too large: {fileInfo.Length / (1024 * 1024)} MB" };

            // Optional: content validation (e.g., image dimensions)
            if (ext == ".png" || ext == ".jpg" || ext == ".jpeg" || ext == ".gif")
            {
                try
                {
                    var bytes = File.ReadAllBytes(filePath);
                    Texture2D tex = new Texture2D(2, 2);
                    if (!tex.LoadImage(bytes))
                        return new ValidationResult { IsValid = false, ErrorMessage = "Invalid image file." };
                    // Example: limit image dimensions
                    if (tex.width > 8192 || tex.height > 8192)
                        return new ValidationResult { IsValid = false, ErrorMessage = "Image dimensions too large." };
                }
                catch (Exception)
                {
                    return new ValidationResult { IsValid = false, ErrorMessage = "Failed to read image file." };
                }
            }

            // TODO: Integrate virus scanning API if available

            return new ValidationResult { IsValid = true };
        }
    }
} 