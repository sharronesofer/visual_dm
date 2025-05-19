using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.TestTools;
using NUnit.Framework;
using VisualDM.Net;

namespace VDM.Tests.Net
{
    [TestFixture]
    public class WebSocketMessageValidationTests : TestFramework
    {
        [Test]
        public void Validate_ValidMessage_ShouldReturnTrue()
        {
            // Arrange
            var message = new WebSocketMessage
            {
                version = "1.0",
                type = "test_message",
                timestamp = DateTime.UtcNow.ToString("o"),
                requestId = "req-123",
                payload = new Dictionary<string, object> { { "key", "value" } }
            };
            
            // Act
            bool isValid = WebSocketMessageValidator.Validate(message, out string error);
            
            // Assert
            Assert.IsTrue(isValid, "Valid message should pass validation");
            Assert.IsNull(error, "No error should be returned for valid message");
        }
        
        [Test]
        public void Validate_NullMessage_ShouldReturnFalse()
        {
            // Arrange
            WebSocketMessage message = null;
            
            // Act
            bool isValid = WebSocketMessageValidator.Validate(message, out string error);
            
            // Assert
            Assert.IsFalse(isValid, "Null message should fail validation");
            Assert.IsNotNull(error, "Error should be returned for null message");
            Assert.IsTrue(error.Contains("null"), "Error should mention message is null");
        }
        
        [Test]
        public void Validate_MissingVersion_ShouldReturnFalse()
        {
            // Arrange
            var message = new WebSocketMessage
            {
                // Missing version
                type = "test_message",
                timestamp = DateTime.UtcNow.ToString("o"),
                requestId = "req-123",
                payload = new Dictionary<string, object> { { "key", "value" } }
            };
            
            // Act
            bool isValid = WebSocketMessageValidator.Validate(message, out string error);
            
            // Assert
            Assert.IsFalse(isValid, "Message without version should fail validation");
            Assert.IsNotNull(error, "Error should be returned for missing version");
            Assert.IsTrue(error.Contains("version"), "Error should mention missing version");
        }
        
        [Test]
        public void Validate_MissingType_ShouldReturnFalse()
        {
            // Arrange
            var message = new WebSocketMessage
            {
                version = "1.0",
                // Missing type
                timestamp = DateTime.UtcNow.ToString("o"),
                requestId = "req-123",
                payload = new Dictionary<string, object> { { "key", "value" } }
            };
            
            // Act
            bool isValid = WebSocketMessageValidator.Validate(message, out string error);
            
            // Assert
            Assert.IsFalse(isValid, "Message without type should fail validation");
            Assert.IsNotNull(error, "Error should be returned for missing type");
            Assert.IsTrue(error.Contains("type"), "Error should mention missing type");
        }
        
        [Test]
        public void Validate_MissingTimestamp_ShouldReturnFalse()
        {
            // Arrange
            var message = new WebSocketMessage
            {
                version = "1.0",
                type = "test_message",
                // Missing timestamp
                requestId = "req-123",
                payload = new Dictionary<string, object> { { "key", "value" } }
            };
            
            // Act
            bool isValid = WebSocketMessageValidator.Validate(message, out string error);
            
            // Assert
            Assert.IsFalse(isValid, "Message without timestamp should fail validation");
            Assert.IsNotNull(error, "Error should be returned for missing timestamp");
            Assert.IsTrue(error.Contains("timestamp"), "Error should mention missing timestamp");
        }
        
        [Test]
        public void Validate_NullPayload_ShouldReturnFalse()
        {
            // Arrange
            var message = new WebSocketMessage
            {
                version = "1.0",
                type = "test_message",
                timestamp = DateTime.UtcNow.ToString("o"),
                requestId = "req-123",
                payload = null // Null payload
            };
            
            // Act
            bool isValid = WebSocketMessageValidator.Validate(message, out string error);
            
            // Assert
            Assert.IsFalse(isValid, "Message with null payload should fail validation");
            Assert.IsNotNull(error, "Error should be returned for null payload");
            Assert.IsTrue(error.Contains("payload"), "Error should mention null payload");
        }
        
        [Test]
        public void Validate_EmptyType_ShouldReturnFalse()
        {
            // Arrange
            var message = new WebSocketMessage
            {
                version = "1.0",
                type = "", // Empty type
                timestamp = DateTime.UtcNow.ToString("o"),
                requestId = "req-123",
                payload = new Dictionary<string, object> { { "key", "value" } }
            };
            
            // Act
            bool isValid = WebSocketMessageValidator.Validate(message, out string error);
            
            // Assert
            Assert.IsFalse(isValid, "Message with empty type should fail validation");
            Assert.IsNotNull(error, "Error should be returned for empty type");
            Assert.IsTrue(error.Contains("type"), "Error should mention empty type");
        }
        
        [Test]
        public void Validate_InvalidTimestampFormat_ShouldReturnFalse()
        {
            // Arrange
            var message = new WebSocketMessage
            {
                version = "1.0",
                type = "test_message",
                timestamp = "not-a-valid-timestamp", // Invalid timestamp format
                requestId = "req-123",
                payload = new Dictionary<string, object> { { "key", "value" } }
            };
            
            // Act
            bool isValid = WebSocketMessageValidator.Validate(message, out string error);
            
            // Assert
            Assert.IsFalse(isValid, "Message with invalid timestamp should fail validation");
            Assert.IsNotNull(error, "Error should be returned for invalid timestamp");
            Assert.IsTrue(error.Contains("timestamp"), "Error should mention invalid timestamp");
        }
        
        [Test]
        public void Validate_InvalidVersionFormat_ShouldReturnFalse()
        {
            // Arrange
            var message = new WebSocketMessage
            {
                version = "invalid version", // Invalid version format
                type = "test_message",
                timestamp = DateTime.UtcNow.ToString("o"),
                requestId = "req-123",
                payload = new Dictionary<string, object> { { "key", "value" } }
            };
            
            // Act
            bool isValid = WebSocketMessageValidator.Validate(message, out string error);
            
            // Assert
            Assert.IsFalse(isValid, "Message with invalid version should fail validation");
            Assert.IsNotNull(error, "Error should be returned for invalid version");
            Assert.IsTrue(error.Contains("version"), "Error should mention invalid version");
        }
        
        [Test]
        public void Validate_MissingRequestId_ShouldStillBeValid()
        {
            // Arrange - RequestId is optional
            var message = new WebSocketMessage
            {
                version = "1.0",
                type = "test_message",
                timestamp = DateTime.UtcNow.ToString("o"),
                // Missing requestId is OK
                payload = new Dictionary<string, object> { { "key", "value" } }
            };
            
            // Act
            bool isValid = WebSocketMessageValidator.Validate(message, out string error);
            
            // Assert
            Assert.IsTrue(isValid, "Message without requestId should still be valid");
            Assert.IsNull(error, "No error should be returned for missing requestId");
        }
        
        [Test]
        public void Validate_MaxLengthExceeded_ShouldReturnFalse()
        {
            // Arrange
            var longString = new string('x', 10_000_000); // Very long string to test size limit
            var message = new WebSocketMessage
            {
                version = "1.0",
                type = "test_message",
                timestamp = DateTime.UtcNow.ToString("o"),
                requestId = "req-123",
                payload = new Dictionary<string, object> { { "key", longString } }
            };
            
            // Act
            bool isValid = WebSocketMessageValidator.Validate(message, out string error, maxSizeBytes: 1024); // 1KB max
            
            // Assert
            Assert.IsFalse(isValid, "Message exceeding max size should fail validation");
            Assert.IsNotNull(error, "Error should be returned for oversized message");
            Assert.IsTrue(error.Contains("size"), "Error should mention message size");
        }
        
        [Test]
        public void Parse_ValidJson_ShouldReturnMessage()
        {
            // Arrange
            string json = @"{
                ""version"": ""1.0"",
                ""type"": ""test_message"",
                ""timestamp"": ""2023-06-01T12:00:00.000Z"",
                ""requestId"": ""req-123"",
                ""payload"": {
                    ""key"": ""value"",
                    ""number"": 42
                }
            }";
            
            // Act
            bool success = WebSocketMessageParser.TryParse(json, out WebSocketMessage message, out string error);
            
            // Assert
            Assert.IsTrue(success, "Valid JSON should parse successfully");
            Assert.IsNull(error, "No error should be returned for valid JSON");
            Assert.IsNotNull(message, "Message should not be null");
            Assert.AreEqual("1.0", message.version, "Version should match");
            Assert.AreEqual("test_message", message.type, "Type should match");
            Assert.AreEqual("2023-06-01T12:00:00.000Z", message.timestamp, "Timestamp should match");
            Assert.AreEqual("req-123", message.requestId, "RequestId should match");
            Assert.AreEqual("value", message.payload["key"], "Payload string value should match");
            Assert.AreEqual(42, Convert.ToInt32(message.payload["number"]), "Payload number value should match");
        }
        
        [Test]
        public void Parse_InvalidJson_ShouldReturnFalse()
        {
            // Arrange
            string json = "{ not valid json }";
            
            // Act
            bool success = WebSocketMessageParser.TryParse(json, out WebSocketMessage message, out string error);
            
            // Assert
            Assert.IsFalse(success, "Invalid JSON should fail to parse");
            Assert.IsNotNull(error, "Error should be returned for invalid JSON");
            Assert.IsNull(message, "Message should be null for invalid JSON");
        }
        
        [Test]
        public void Parse_MissingRequiredFields_ShouldReturnFalse()
        {
            // Arrange
            string json = @"{
                ""type"": ""test_message"",
                ""payload"": {}
            }";
            
            // Act
            bool success = WebSocketMessageParser.TryParse(json, out WebSocketMessage message, out string error);
            
            // Assert
            Assert.IsFalse(success, "JSON missing required fields should fail to parse");
            Assert.IsNotNull(error, "Error should be returned for missing fields");
            Assert.IsNull(message, "Message should be null for invalid message");
        }
        
        [Test]
        public void Parse_IncorrectFieldTypes_ShouldReturnFalse()
        {
            // Arrange
            string json = @"{
                ""version"": 1.0,
                ""type"": 123,
                ""timestamp"": ""2023-06-01T12:00:00.000Z"",
                ""payload"": {}
            }";
            
            // Act
            bool success = WebSocketMessageParser.TryParse(json, out WebSocketMessage message, out string error);
            
            // Assert
            Assert.IsFalse(success, "JSON with incorrect field types should fail to parse");
            Assert.IsNotNull(error, "Error should be returned for incorrect types");
            Assert.IsNull(message, "Message should be null for invalid message");
        }
        
        [Test]
        public void Serialize_ValidMessage_ShouldReturnValidJson()
        {
            // Arrange
            var message = new WebSocketMessage
            {
                version = "1.0",
                type = "test_message",
                timestamp = "2023-06-01T12:00:00.000Z",
                requestId = "req-123",
                payload = new Dictionary<string, object> { { "key", "value" }, { "number", 42 } }
            };
            
            // Act
            string json = WebSocketMessageSerializer.Serialize(message);
            bool parseBack = WebSocketMessageParser.TryParse(json, out WebSocketMessage parsedMessage, out string error);
            
            // Assert
            Assert.IsNotNull(json, "Serialized JSON should not be null");
            Assert.IsTrue(parseBack, "Serialized JSON should parse back successfully");
            Assert.AreEqual(message.version, parsedMessage.version, "Version should match after serialize/parse cycle");
            Assert.AreEqual(message.type, parsedMessage.type, "Type should match after serialize/parse cycle");
            Assert.AreEqual(message.timestamp, parsedMessage.timestamp, "Timestamp should match after serialize/parse cycle");
            Assert.AreEqual(message.requestId, parsedMessage.requestId, "RequestId should match after serialize/parse cycle");
            Assert.AreEqual(message.payload["key"], parsedMessage.payload["key"], "Payload key should match after serialize/parse cycle");
            Assert.AreEqual(message.payload["number"], parsedMessage.payload["number"], "Payload number should match after serialize/parse cycle");
        }
        
        [Test]
        public void Serialize_NullMessage_ShouldThrowException()
        {
            // Arrange
            WebSocketMessage message = null;
            
            // Act & Assert
            Assert.Throws<ArgumentNullException>(() => WebSocketMessageSerializer.Serialize(message), 
                "Serializing null message should throw ArgumentNullException");
        }
    }
} 