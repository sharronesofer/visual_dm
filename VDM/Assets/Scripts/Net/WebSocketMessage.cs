using System;
using System.Collections.Generic;
using Newtonsoft.Json;

namespace VisualDM.Net
{
    /// <summary>
    /// Represents a standardized WebSocket message with a canonical envelope.
    /// </summary>
    public class WebSocketMessage
    {
        /// <summary>
        /// Protocol version for compatibility checking.
        /// </summary>
        public string version { get; set; } = "1.0";

        /// <summary>
        /// Message type that determines how it is handled.
        /// </summary>
        public string type { get; set; }

        /// <summary>
        /// Message payload containing the actual data.
        /// </summary>
        public Dictionary<string, object> payload { get; set; }

        /// <summary>
        /// ISO 8601 timestamp of when the message was created.
        /// </summary>
        public string timestamp { get; set; } = DateTime.UtcNow.ToString("o");

        /// <summary>
        /// Optional request ID for request-response pattern matching.
        /// </summary>
        public string requestId { get; set; }
        
        /// <summary>
        /// Creates a new empty WebSocketMessage.
        /// </summary>
        public WebSocketMessage()
        {
            payload = new Dictionary<string, object>();
        }
        
        /// <summary>
        /// Creates a new WebSocketMessage with the specified type.
        /// </summary>
        /// <param name="messageType">The message type.</param>
        public WebSocketMessage(string messageType)
        {
            type = messageType;
            payload = new Dictionary<string, object>();
        }
        
        /// <summary>
        /// Gets a typed value from the payload.
        /// </summary>
        /// <typeparam name="T">The expected type of the value.</typeparam>
        /// <param name="key">The key of the value in the payload dictionary.</param>
        /// <param name="defaultValue">Default value to return if key doesn't exist or value can't be converted.</param>
        /// <returns>The value cast to type T, or the default value.</returns>
        public T GetValue<T>(string key, T defaultValue = default)
        {
            if (payload == null || !payload.ContainsKey(key))
                return defaultValue;
                
            try
            {
                var value = payload[key];
                if (value is T typedValue)
                    return typedValue;
                    
                // Try converting directly
                if (typeof(T).IsEnum && value is string stringValue)
                    return (T)Enum.Parse(typeof(T), stringValue);
                    
                // Try Json.NET's conversion
                return JsonConvert.DeserializeObject<T>(JsonConvert.SerializeObject(value));
            }
            catch
            {
                return defaultValue;
            }
        }
        
        /// <summary>
        /// Sets a value in the payload with the specified key.
        /// </summary>
        /// <param name="key">The key to use in the payload dictionary.</param>
        /// <param name="value">The value to store.</param>
        public void SetValue(string key, object value)
        {
            if (payload == null)
                payload = new Dictionary<string, object>();
                
            payload[key] = value;
        }
        
        /// <summary>
        /// Creates a response message to this message.
        /// </summary>
        /// <param name="responseType">The type of the response message.</param>
        /// <returns>A new WebSocketMessage with the same requestId as this message.</returns>
        public WebSocketMessage CreateResponse(string responseType)
        {
            return new WebSocketMessage
            {
                type = responseType,
                requestId = this.requestId,
                version = this.version
            };
        }
    }

    // Canonical payloads as C# structs/classes

    /// <summary>
    /// Payload for metrics update messages.
    /// </summary>
    [Serializable]
    public class MetricsUpdatePayload
    {
        /// <summary>
        /// Name of the metric being updated.
        /// </summary>
        public string metricName;
        /// <summary>
        /// Value of the metric.
        /// </summary>
        public object value;
    }

    /// <summary>
    /// Payload for error messages.
    /// </summary>
    [Serializable]
    public class ErrorPayload
    {
        /// <summary>
        /// Error code (e.g., 400, 404, 500).
        /// </summary>
        public int code;
        /// <summary>
        /// Human-readable error message.
        /// </summary>
        public string message;
    }

    /// <summary>
    /// Payload for authentication request messages.
    /// </summary>
    [Serializable]
    public class AuthRequestPayload
    {
        /// <summary>
        /// Authentication token.
        /// </summary>
        public string token;
    }

    /// <summary>
    /// Payload for authentication response messages.
    /// </summary>
    [Serializable]
    public class AuthResponsePayload
    {
        /// <summary>
        /// Whether authentication was successful.
        /// </summary>
        public bool success;
        /// <summary>
        /// User ID if authentication succeeded.
        /// </summary>
        public string userId;
        /// <summary>
        /// Error message if authentication failed.
        /// </summary>
        public string error;
    }

    /// <summary>
    /// Payload for AI backend messages (e.g., gpt_rumor_server).
    /// </summary>
    [Serializable]
    public class AIMessagePayload
    {
        /// <summary>
        /// The generated rumor or AI message.
        /// </summary>
        public string Rumor;
    }

    /// <summary>
    /// Payload for heartbeat (ping/pong) messages.
    /// </summary>
    [Serializable]
    public class HeartbeatPayload
    {
        /// <summary>
        /// Heartbeat message (e.g., "ping", "pong").
        /// </summary>
        public string message;
    }
    // Add additional payload classes as needed for new message types 
} 