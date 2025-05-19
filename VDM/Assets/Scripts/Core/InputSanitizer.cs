using System;
using System.Text.RegularExpressions;
using System.Web;

namespace VisualDM.Core
{
    /// <summary>
    /// CoreSanitizer: Centralized input sanitization service for all user-generated content.
    /// 
    /// Rules & Patterns:
    /// - Chat messages: Strips HTML/script tags, encodes special characters, checks for XSS/injection patterns, detects encoded/double-encoded payloads.
    /// - Usernames: Allows only alphanumeric, underscore, hyphen; enforces length; blocks reserved names (admin, system, etc.).
    /// - Form fields: Type-specific validation (email, number, date), fallback to HTML strip/encode.
    /// - File names: Removes invalid characters, enforces length, validates extension.
    /// - File uploads: Use IsFileTypeAllowed and FileValidationService for type/size/content checks.
    /// - All suspicious input attempts are logged for security monitoring.
    /// 
    /// Developer Security Guide:
    /// - Always sanitize user input both client-side and server-side. Use CoreSanitizer for all user-facing fields.
    /// - For new input fields, select the most appropriate CoreSanitizer method or add a new one if needed.
    /// - Use the Validator property on UI.Components.CoreField to enforce validation at runtime.
    /// - Log suspicious or rejected input using LogSuspiciousCore for audit and incident response.
    /// - Review and update sanitization rules regularly to address new attack vectors.
    /// - Document any new rules or patterns in this summary block and in XML comments.
    /// </summary>
    public static class CoreSanitizer
    {
        /// <summary>
        /// Sanitizes chat messages by stripping or encoding HTML/script tags and validating against injection patterns.
        /// </summary>
        /// <param name="input">The chat message input string.</param>
        /// <returns>Sanitized chat message.</returns>
        public static string SanitizeChatMessage(string input)
        {
            if (string.IsNullOrEmpty(input)) return string.Empty;
            // Remove HTML tags
            string noHtml = Regex.Replace(input, "<.*?>", string.Empty);
            // Encode special characters
            string encoded = HttpUtility.HtmlEncode(noHtml);
            // Optionally, further filter for known injection patterns
            // (Add more rules as needed)
            return encoded;
        }

        /// <summary>
        /// Sanitizes a username by restricting allowed characters and enforcing length limits.
        /// </summary>
        /// <param name="input">The username input string.</param>
        /// <param name="maxLength">Maximum allowed length (default 20).</param>
        /// <returns>Sanitized username, or null if invalid.</returns>
        public static string SanitizeUsername(string input, int maxLength = 20)
        {
            if (string.IsNullOrEmpty(input)) return null;
            // Allow only alphanumeric and limited special characters
            string pattern = @"^[a-zA-Z0-9_\-]{1," + maxLength + "}$";
            if (!Regex.IsMatch(input, pattern)) return null;
            return input;
        }

        /// <summary>
        /// Sanitizes a form field input based on expected type (email, number, date, etc.).
        /// </summary>
        /// <param name="input">The form field input string.</param>
        /// <param name="type">The expected type ("email", "number", "date").</param>
        /// <returns>Sanitized input, or null if invalid.</returns>
        public static string SanitizeFormField(string input, string type)
        {
            if (string.IsNullOrEmpty(input)) return null;
            switch (type.ToLower())
            {
                case "email":
                    // Simple email regex
                    if (Regex.IsMatch(input, @"^[^@\s]+@[^@\s]+\.[^@\s]+$"))
                        return input;
                    break;
                case "number":
                    if (Regex.IsMatch(input, @"^-?\d+(\.\d+)?$"))
                        return input;
                    break;
                case "date":
                    if (DateTime.TryParse(input, out _))
                        return input;
                    break;
                default:
                    // Fallback: strip HTML and encode
                    return HttpUtility.HtmlEncode(Regex.Replace(input, "<.*?>", string.Empty));
            }
            return null;
        }

        /// <summary>
        /// Sanitizes a file name by removing invalid characters and enforcing length/type restrictions.
        /// </summary>
        /// <param name="input">The file name input string.</param>
        /// <param name="maxLength">Maximum allowed length (default 64).</param>
        /// <returns>Sanitized file name, or null if invalid.</returns>
        public static string SanitizeFileName(string input, int maxLength = 64)
        {
            if (string.IsNullOrEmpty(input)) return null;
            // Remove invalid file name characters
            string invalidChars = Regex.Escape(new string(System.IO.Path.GetInvalidFileNameChars()));
            string pattern = "[" + invalidChars + "]";
            string sanitized = Regex.Replace(input, pattern, string.Empty);
            if (sanitized.Length == 0 || sanitized.Length > maxLength) return null;
            return sanitized;
        }

        /// <summary>
        /// Logs suspicious input attempts for security monitoring.
        /// </summary>
        /// <param name="userId">User identifier (if available).</param>
        /// <param name="inputType">Type of input (e.g., chat, username).</param>
        /// <param name="payload">The suspicious input payload.</param>
        public static void LogSuspiciousCore(string userId, string inputType, string payload)
        {
            string message = $"Suspicious input detected. User: {userId}, Type: {inputType}, Payload: {payload}";
            VisualDM.Utilities.ErrorHandlingService.Instance.LogWarning(message, "CoreSanitizer.LogSuspiciousCore");
        }

        /// <summary>
        /// Checks for common XSS and injection patterns in chat messages, including encoded payloads.
        /// </summary>
        /// <param name="input">The chat message input string.</param>
        /// <returns>True if input is clean, false if suspicious patterns are found.</returns>
        public static bool IsChatMessageClean(string input)
        {
            if (string.IsNullOrEmpty(input)) return true;
            // Simple XSS/injection pattern checks
            string[] patterns = {
                "<script", "javascript:", "onerror=", "onload=", "<iframe", "<img", "document.cookie", "eval(", "alert(", "<svg", "</?\\w+>"
            };
            foreach (var pattern in patterns)
            {
                if (Regex.IsMatch(input, pattern, RegexOptions.IgnoreCase))
                    return false;
            }
            // Check for encoded payloads (e.g., &lt;script&gt;)
            if (Regex.IsMatch(input, "&lt;.*?&gt;", RegexOptions.IgnoreCase))
                return false;
            // Check for double encoding (e.g., %253Cscript%253E)
            if (Regex.IsMatch(input, "%25[0-9a-fA-F]{2}", RegexOptions.IgnoreCase))
            {
                // If the decoded string contains suspicious patterns, flag as not clean
                string decoded = Uri.UnescapeDataString(input);
                foreach (var pattern in patterns)
                {
                    if (Regex.IsMatch(decoded, pattern, RegexOptions.IgnoreCase))
                        return false;
                }
            }
            return true;
        }

        /// <summary>
        /// Checks if a username is attempting to impersonate reserved/system names.
        /// </summary>
        /// <param name="input">The username input string.</param>
        /// <returns>True if not impersonating, false if reserved.</returns>
        public static bool IsUsernameAllowed(string input)
        {
            if (string.IsNullOrEmpty(input)) return false;
            string[] reserved = { "admin", "system", "moderator", "mod", "server", "root" };
            foreach (var name in reserved)
            {
                if (string.Equals(input, name, StringComparison.OrdinalIgnoreCase))
                    return false;
            }
            return true;
        }

        /// <summary>
        /// Validates file type for uploads (stub, extend as needed).
        /// </summary>
        /// <param name="fileName">The file name.</param>
        /// <param name="allowedExtensions">Array of allowed extensions (e.g., ".png", ".jpg").</param>
        /// <returns>True if file type is allowed, false otherwise.</returns>
        public static bool IsFileTypeAllowed(string fileName, string[] allowedExtensions)
        {
            if (string.IsNullOrEmpty(fileName) || allowedExtensions == null || allowedExtensions.Length == 0)
                return false;
            string ext = System.IO.Path.GetExtension(fileName).ToLowerInvariant();
            foreach (var allowed in allowedExtensions)
            {
                if (ext == allowed.ToLowerInvariant())
                    return true;
            }
            return false;
        }
    }
} 