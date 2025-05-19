using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.TestTools;
using NUnit.Framework;
using Newtonsoft.Json;
using VisualDM.Net;

namespace VDM.Tests.Net
{
    [TestFixture]
    public class WebSocketMessageTests : TestFramework
    {
        [Test]
        public void WebSocketMessage_Serialization_ContainsAllRequiredFields()
        {
            // Arrange
            var timestamp = DateTime.UtcNow.ToString("o");
            var message = new WebSocketMessage
            {
                version = "1.0",
                type = "test_message",
                timestamp = timestamp,
                requestId = "req-123",
                payload = new Dictionary<string, object>
                {
                    { "key1", "value1" },
                    { "key2", 42 }
                }
            };

            // Act
            string json = JsonConvert.SerializeObject(message);

            // Assert
            Assert.IsTrue(json.Contains("\"version\":\"1.0\""), "Serialized JSON should contain version");
            Assert.IsTrue(json.Contains("\"type\":\"test_message\""), "Serialized JSON should contain type");
            Assert.IsTrue(json.Contains($"\"timestamp\":\"{timestamp}\""), "Serialized JSON should contain timestamp");
            Assert.IsTrue(json.Contains("\"requestId\":\"req-123\""), "Serialized JSON should contain requestId");
            Assert.IsTrue(json.Contains("\"payload\":{"), "Serialized JSON should contain payload");
            Assert.IsTrue(json.Contains("\"key1\":\"value1\""), "Serialized JSON should contain payload values");
            Assert.IsTrue(json.Contains("\"key2\":42"), "Serialized JSON should contain payload values");
        }

        [Test]
        public void WebSocketMessage_Deserialization_ReconstructsObjectCorrectly()
        {
            // Arrange
            string timestamp = DateTime.UtcNow.ToString("o");
            string json = $"{{\"version\":\"1.0\",\"type\":\"test_message\",\"timestamp\":\"{timestamp}\",\"requestId\":\"req-123\",\"payload\":{{\"key1\":\"value1\",\"key2\":42}}}}";

            // Act
            var message = JsonConvert.DeserializeObject<WebSocketMessage>(json);

            // Assert
            Assert.IsNotNull(message, "Deserialized message should not be null");
            Assert.AreEqual("1.0", message.version, "Version should match");
            Assert.AreEqual("test_message", message.type, "Type should match");
            Assert.AreEqual(timestamp, message.timestamp, "Timestamp should match");
            Assert.AreEqual("req-123", message.requestId, "RequestId should match");
            Assert.IsNotNull(message.payload, "Payload should not be null");
            Assert.AreEqual(2, message.payload.Count, "Payload should have correct number of items");
            Assert.AreEqual("value1", message.payload["key1"], "Payload value should match");
            Assert.AreEqual(42L, message.payload["key2"], "Payload value should match"); // Note: JSON.NET deserializes numbers as long
        }

        [Test]
        public void WebSocketMessage_Serialization_HandlesNullValues()
        {
            // Arrange
            var message = new WebSocketMessage
            {
                version = "1.0",
                type = "test_message",
                timestamp = null,
                requestId = null,
                payload = null
            };

            // Act
            string json = JsonConvert.SerializeObject(message);
            var deserializedMessage = JsonConvert.DeserializeObject<WebSocketMessage>(json);

            // Assert
            Assert.IsNotNull(deserializedMessage, "Deserialized message should not be null");
            Assert.AreEqual("1.0", deserializedMessage.version, "Version should match");
            Assert.AreEqual("test_message", deserializedMessage.type, "Type should match");
            Assert.IsNull(deserializedMessage.timestamp, "Timestamp should be null");
            Assert.IsNull(deserializedMessage.requestId, "RequestId should be null");
            Assert.IsNull(deserializedMessage.payload, "Payload should be null");
        }

        [Test]
        public void MetricsUpdatePayload_SerializationAndDeserialization()
        {
            // Arrange
            var payload = new MetricsUpdatePayload
            {
                metricName = "player_count",
                value = 42
            };

            // Act
            string json = JsonConvert.SerializeObject(payload);
            var deserializedPayload = JsonConvert.DeserializeObject<MetricsUpdatePayload>(json);

            // Assert
            Assert.IsNotNull(deserializedPayload, "Deserialized payload should not be null");
            Assert.AreEqual("player_count", deserializedPayload.metricName, "Metric name should match");
            Assert.AreEqual(42L, deserializedPayload.value, "Metric value should match"); // Note: JSON.NET deserializes numbers as long
        }

        [Test]
        public void ErrorPayload_SerializationAndDeserialization()
        {
            // Arrange
            var payload = new ErrorPayload
            {
                code = 404,
                message = "Resource not found"
            };

            // Act
            string json = JsonConvert.SerializeObject(payload);
            var deserializedPayload = JsonConvert.DeserializeObject<ErrorPayload>(json);

            // Assert
            Assert.IsNotNull(deserializedPayload, "Deserialized payload should not be null");
            Assert.AreEqual(404, deserializedPayload.code, "Error code should match");
            Assert.AreEqual("Resource not found", deserializedPayload.message, "Error message should match");
        }

        [Test]
        public void AuthRequestPayload_SerializationAndDeserialization()
        {
            // Arrange
            var payload = new AuthRequestPayload
            {
                token = "jwt-token-123"
            };

            // Act
            string json = JsonConvert.SerializeObject(payload);
            var deserializedPayload = JsonConvert.DeserializeObject<AuthRequestPayload>(json);

            // Assert
            Assert.IsNotNull(deserializedPayload, "Deserialized payload should not be null");
            Assert.AreEqual("jwt-token-123", deserializedPayload.token, "Auth token should match");
        }

        [Test]
        public void AuthResponsePayload_SerializationAndDeserialization()
        {
            // Arrange
            var payload = new AuthResponsePayload
            {
                success = true,
                userId = "user-123",
                error = null
            };

            // Act
            string json = JsonConvert.SerializeObject(payload);
            var deserializedPayload = JsonConvert.DeserializeObject<AuthResponsePayload>(json);

            // Assert
            Assert.IsNotNull(deserializedPayload, "Deserialized payload should not be null");
            Assert.IsTrue(deserializedPayload.success, "Success flag should match");
            Assert.AreEqual("user-123", deserializedPayload.userId, "User ID should match");
            Assert.IsNull(deserializedPayload.error, "Error should be null");
        }

        [Test]
        public void AuthResponsePayload_Error_SerializationAndDeserialization()
        {
            // Arrange
            var payload = new AuthResponsePayload
            {
                success = false,
                userId = null,
                error = "Invalid token"
            };

            // Act
            string json = JsonConvert.SerializeObject(payload);
            var deserializedPayload = JsonConvert.DeserializeObject<AuthResponsePayload>(json);

            // Assert
            Assert.IsNotNull(deserializedPayload, "Deserialized payload should not be null");
            Assert.IsFalse(deserializedPayload.success, "Success flag should match");
            Assert.IsNull(deserializedPayload.userId, "User ID should be null");
            Assert.AreEqual("Invalid token", deserializedPayload.error, "Error message should match");
        }

        [Test]
        public void AIMessagePayload_SerializationAndDeserialization()
        {
            // Arrange
            var payload = new AIMessagePayload
            {
                Rumor = "The king plans to raise taxes next month."
            };

            // Act
            string json = JsonConvert.SerializeObject(payload);
            var deserializedPayload = JsonConvert.DeserializeObject<AIMessagePayload>(json);

            // Assert
            Assert.IsNotNull(deserializedPayload, "Deserialized payload should not be null");
            Assert.AreEqual("The king plans to raise taxes next month.", deserializedPayload.Rumor, "Rumor text should match");
        }

        [Test]
        public void HeartbeatPayload_SerializationAndDeserialization()
        {
            // Arrange
            var payload = new HeartbeatPayload
            {
                message = "ping"
            };

            // Act
            string json = JsonConvert.SerializeObject(payload);
            var deserializedPayload = JsonConvert.DeserializeObject<HeartbeatPayload>(json);

            // Assert
            Assert.IsNotNull(deserializedPayload, "Deserialized payload should not be null");
            Assert.AreEqual("ping", deserializedPayload.message, "Heartbeat message should match");
        }

        [Test]
        public void WebSocketMessage_WithNestedObjects_SerializesAndDeserializesCorrectly()
        {
            // Arrange
            var nestedDict = new Dictionary<string, object>
            {
                { "nestedKey", "nestedValue" },
                { "nestedArray", new[] { 1, 2, 3 } }
            };

            var message = new WebSocketMessage
            {
                version = "1.0",
                type = "complex_message",
                timestamp = DateTime.UtcNow.ToString("o"),
                requestId = "req-123",
                payload = new Dictionary<string, object>
                {
                    { "stringKey", "stringValue" },
                    { "numberKey", 42 },
                    { "boolKey", true },
                    { "nullKey", null },
                    { "nestedObject", nestedDict }
                }
            };

            // Act
            string json = JsonConvert.SerializeObject(message);
            var deserializedMessage = JsonConvert.DeserializeObject<WebSocketMessage>(json);

            // Assert
            Assert.IsNotNull(deserializedMessage, "Deserialized message should not be null");
            Assert.AreEqual(5, deserializedMessage.payload.Count, "Payload should have correct number of items");
            Assert.AreEqual("stringValue", deserializedMessage.payload["stringKey"], "String value should match");
            Assert.AreEqual(42L, deserializedMessage.payload["numberKey"], "Number value should match");
            Assert.AreEqual(true, deserializedMessage.payload["boolKey"], "Boolean value should match");
            Assert.IsNull(deserializedMessage.payload["nullKey"], "Null value should be null");
            
            // Nested object will be deserialized as JObject by JSON.NET, so we need to check differently
            Assert.IsNotNull(deserializedMessage.payload["nestedObject"], "Nested object should not be null");
            var nestedObj = JsonConvert.DeserializeObject<Dictionary<string, object>>(
                JsonConvert.SerializeObject(deserializedMessage.payload["nestedObject"]));
            Assert.AreEqual("nestedValue", nestedObj["nestedKey"], "Nested value should match");
        }

        [Test]
        public void WebSocketMessage_WithLargePayload_SerializesAndDeserializesCorrectly()
        {
            // Arrange
            var message = new WebSocketMessage
            {
                version = "1.0",
                type = "large_payload",
                timestamp = DateTime.UtcNow.ToString("o"),
                requestId = "req-123",
                payload = new Dictionary<string, object>()
            };

            // Add 100 items to the payload
            for (int i = 0; i < 100; i++)
            {
                message.payload[$"key_{i}"] = $"value_{i}";
            }

            // Act
            string json = JsonConvert.SerializeObject(message);
            var deserializedMessage = JsonConvert.DeserializeObject<WebSocketMessage>(json);

            // Assert
            Assert.IsNotNull(deserializedMessage, "Deserialized message should not be null");
            Assert.AreEqual(100, deserializedMessage.payload.Count, "Payload should have correct number of items");
            
            // Check a few random items
            Assert.AreEqual("value_0", deserializedMessage.payload["key_0"], "Payload value should match");
            Assert.AreEqual("value_50", deserializedMessage.payload["key_50"], "Payload value should match");
            Assert.AreEqual("value_99", deserializedMessage.payload["key_99"], "Payload value should match");
        }

        [Test]
        public void WebSocketMessage_InvalidJsonDeserialization_ReturnsNullOrThrows()
        {
            // Arrange
            string invalidJson = "{ this is not valid json }";

            // Act & Assert
            Assert.Throws<JsonReaderException>(() => 
                JsonConvert.DeserializeObject<WebSocketMessage>(invalidJson),
                "Invalid JSON should throw exception");
        }
    }
} 