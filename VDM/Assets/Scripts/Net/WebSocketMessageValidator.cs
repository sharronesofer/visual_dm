using System;
using System.Collections.Generic;
using System.Text;
using UnityEngine;

namespace VisualDM.Net
{
    /// <summary>
    /// Provides validation functionality for WebSocket messages
    /// </summary>
    public static class WebSocketMessageValidator
    {
        // Default maximum message size is 5MB
        private const int DEFAULT_MAX_SIZE_BYTES = 5 * 1024 * 1024;
        
        /// <summary>
        /// Validates a WebSocketMessage for required fields and correct formatting
        /// </summary>
        /// <param name="message">The message to validate</param>
        /// <param name="error">Output parameter that will contain error message if validation fails</param>
        /// <param name="maxSizeBytes">Maximum allowed message size in bytes</param>
        /// <returns>True if the message is valid, false otherwise</returns>
        public static bool Validate(WebSocketMessage message, out string error, int maxSizeBytes = DEFAULT_MAX_SIZE_BYTES)
        {
            error = null;
            
            // Check for null message
            if (message == null)
            {
                error = "Message cannot be null";
                return false;
            }
            
            // Check for required fields
            if (string.IsNullOrEmpty(message.version))
            {
                error = "Message version is required";
                return false;
            }
            
            if (string.IsNullOrEmpty(message.type))
            {
                error = "Message type is required";
                return false;
            }
            
            if (string.IsNullOrEmpty(message.timestamp))
            {
                error = "Message timestamp is required";
                return false;
            }
            
            if (message.payload == null)
            {
                error = "Message payload cannot be null";
                return false;
            }
            
            // Validate version format (should be semantic versioning)
            if (!ValidateVersionFormat(message.version))
            {
                error = $"Invalid message version format: {message.version}";
                return false;
            }
            
            // Validate timestamp format (should be ISO 8601)
            if (!ValidateTimestampFormat(message.timestamp))
            {
                error = $"Invalid timestamp format: {message.timestamp}";
                return false;
            }
            
            // Validate message size
            if (!ValidateMessageSize(message, maxSizeBytes))
            {
                error = $"Message exceeds maximum size of {maxSizeBytes} bytes";
                return false;
            }
            
            return true;
        }
        
        /// <summary>
        /// Validates the version format (should be semantic versioning or similar)
        /// </summary>
        private static bool ValidateVersionFormat(string version)
        {
            // Basic version validation
            // Valid formats: "1.0", "1.0.0", "1.0.0-alpha"
            if (string.IsNullOrEmpty(version))
                return false;
            
            // Check for at least one digit and possibly a dot
            foreach (char c in version)
            {
                if (char.IsDigit(c) || c == '.')
                    return true;
            }
            
            return false;
        }
        
        /// <summary>
        /// Validates timestamp format (should be ISO 8601)
        /// </summary>
        private static bool ValidateTimestampFormat(string timestamp)
        {
            if (string.IsNullOrEmpty(timestamp))
                return false;
            
            // Attempt to parse the timestamp
            try
            {
                DateTime.Parse(timestamp);
                return true;
            }
            catch (FormatException)
            {
                return false;
            }
        }
        
        /// <summary>
        /// Checks if the message size is within limits
        /// </summary>
        private static bool ValidateMessageSize(WebSocketMessage message, int maxSizeBytes)
        {
            // Serialize the message to estimate its size
            string json = WebSocketMessageSerializer.Serialize(message);
            int sizeBytes = Encoding.UTF8.GetByteCount(json);
            
            return sizeBytes <= maxSizeBytes;
        }
    }
    
    /// <summary>
    /// Provides serialization functionality for WebSocket messages
    /// </summary>
    public static class WebSocketMessageSerializer
    {
        /// <summary>
        /// Serializes a WebSocketMessage to JSON
        /// </summary>
        /// <param name="message">The message to serialize</param>
        /// <returns>JSON representation of the message</returns>
        public static string Serialize(WebSocketMessage message)
        {
            if (message == null)
                throw new ArgumentNullException(nameof(message), "Cannot serialize null message");
            
            return JsonUtility.ToJson(message);
        }
    }
    
    /// <summary>
    /// Provides parsing functionality for WebSocket messages
    /// </summary>
    public static class WebSocketMessageParser
    {
        /// <summary>
        /// Attempts to parse a JSON string into a WebSocketMessage
        /// </summary>
        /// <param name="json">The JSON string to parse</param>
        /// <param name="message">Output parameter that will contain the parsed message if successful</param>
        /// <param name="error">Output parameter that will contain error message if parsing fails</param>
        /// <returns>True if parsing was successful, false otherwise</returns>
        public static bool TryParse(string json, out WebSocketMessage message, out string error)
        {
            message = null;
            error = null;
            
            if (string.IsNullOrEmpty(json))
            {
                error = "JSON string cannot be null or empty";
                return false;
            }
            
            try
            {
                // Parse the JSON
                message = JsonUtility.FromJson<WebSocketMessage>(json);
                
                // Validate the parsed message
                if (!WebSocketMessageValidator.Validate(message, out error))
                {
                    message = null;
                    return false;
                }
                
                return true;
            }
            catch (Exception ex)
            {
                error = $"Failed to parse JSON: {ex.Message}";
                return false;
            }
        }
    }
} 