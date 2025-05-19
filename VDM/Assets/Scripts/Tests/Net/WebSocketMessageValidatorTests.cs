using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.TestTools;
using NUnit.Framework;
using VisualDM.Net;
using Newtonsoft.Json;

namespace VDM.Tests.Net
{
    [TestFixture]
    public class WebSocketMessageValidatorTests : WebSocketTestRunner
    {
        private WebSocketMessageValidator _validator;

        [SetUp]
        public override void Setup()
        {
            base.Setup();
            _validator = new WebSocketMessageValidator();
        }

        [Test]
        public void ValidateMessage_WithValidMessage_ShouldReturnTrue()
        {
            // Arrange
            var message = new WebSocketMessage
            {
                version = "1.0",
                type = "test_message",
                timestamp = DateTime.UtcNow.ToString("o"),
                payload = new Dictionary<string, object> { { "key", "value" } }
            };
            
            // Act
            bool isValid = _validator.ValidateMessage(message);
            
            // Assert
            Assert.IsTrue(isValid, "Valid message should be validated successfully");
        }
        
        [Test]
        public void ValidateMessage_WithMissingVersion_ShouldReturnFalse()
        {
            // Arrange
            var message = new WebSocketMessage
            {
                type = "test_message",
                timestamp = DateTime.UtcNow.ToString("o"),
                payload = new Dictionary<string, object> { { "key", "value" } }
            };
            
            // Act
            bool isValid = _validator.ValidateMessage(message);
            
            // Assert
            Assert.IsFalse(isValid, "Message without version should be invalid");
        }
        
        [Test]
        public void ValidateMessage_WithMissingType_ShouldReturnFalse()
        {
            // Arrange
            var message = new WebSocketMessage
            {
                version = "1.0",
                timestamp = DateTime.UtcNow.ToString("o"),
                payload = new Dictionary<string, object> { { "key", "value" } }
            };
            
            // Act
            bool isValid = _validator.ValidateMessage(message);
            
            // Assert
            Assert.IsFalse(isValid, "Message without type should be invalid");
        }
        
        [Test]
        public void ValidateMessage_WithMissingTimestamp_ShouldReturnFalse()
        {
            // Arrange
            var message = new WebSocketMessage
            {
                version = "1.0",
                type = "test_message",
                payload = new Dictionary<string, object> { { "key", "value" } }
            };
            
            // Act
            bool isValid = _validator.ValidateMessage(message);
            
            // Assert
            Assert.IsFalse(isValid, "Message without timestamp should be invalid");
        }
        
        [Test]
        public void ValidateMessage_WithMissingPayload_ShouldReturnFalse()
        {
            // Arrange
            var message = new WebSocketMessage
            {
                version = "1.0",
                type = "test_message",
                timestamp = DateTime.UtcNow.ToString("o")
            };
            
            // Act
            bool isValid = _validator.ValidateMessage(message);
            
            // Assert
            Assert.IsFalse(isValid, "Message without payload should be invalid");
        }
        
        [Test]
        public void ValidateMessage_WithNullMessage_ShouldReturnFalse()
        {
            // Act
            bool isValid = _validator.ValidateMessage(null);
            
            // Assert
            Assert.IsFalse(isValid, "Null message should be invalid");
        }
        
        [Test]
        public void ValidateMessage_WithEmptyType_ShouldReturnFalse()
        {
            // Arrange
            var message = new WebSocketMessage
            {
                version = "1.0",
                type = "",
                timestamp = DateTime.UtcNow.ToString("o"),
                payload = new Dictionary<string, object> { { "key", "value" } }
            };
            
            // Act
            bool isValid = _validator.ValidateMessage(message);
            
            // Assert
            Assert.IsFalse(isValid, "Message with empty type should be invalid");
        }
        
        [Test]
        public void ValidateMessage_WithEmptyVersion_ShouldReturnFalse()
        {
            // Arrange
            var message = new WebSocketMessage
            {
                version = "",
                type = "test_message",
                timestamp = DateTime.UtcNow.ToString("o"),
                payload = new Dictionary<string, object> { { "key", "value" } }
            };
            
            // Act
            bool isValid = _validator.ValidateMessage(message);
            
            // Assert
            Assert.IsFalse(isValid, "Message with empty version should be invalid");
        }
        
        [Test]
        public void ValidateMessage_WithInvalidTimestampFormat_ShouldReturnFalse()
        {
            // Arrange
            var message = new WebSocketMessage
            {
                version = "1.0",
                type = "test_message",
                timestamp = "not-a-timestamp",
                payload = new Dictionary<string, object> { { "key", "value" } }
            };
            
            // Act
            bool isValid = _validator.ValidateMessage(message);
            
            // Assert
            Assert.IsFalse(isValid, "Message with invalid timestamp format should be invalid");
        }
        
        [Test]
        public void ValidateMessage_WithEmptyPayload_ShouldReturnTrue()
        {
            // Arrange
            var message = new WebSocketMessage
            {
                version = "1.0",
                type = "test_message",
                timestamp = DateTime.UtcNow.ToString("o"),
                payload = new Dictionary<string, object>()
            };
            
            // Act
            bool isValid = _validator.ValidateMessage(message);
            
            // Assert
            Assert.IsTrue(isValid, "Message with empty payload dictionary should still be valid");
        }
        
        [Test]
        public void ValidateMessage_WithRequestId_ShouldReturnTrue()
        {
            // Arrange
            var message = new WebSocketMessage
            {
                version = "1.0",
                type = "test_message",
                timestamp = DateTime.UtcNow.ToString("o"),
                requestId = "request-123",
                payload = new Dictionary<string, object> { { "key", "value" } }
            };
            
            // Act
            bool isValid = _validator.ValidateMessage(message);
            
            // Assert
            Assert.IsTrue(isValid, "Message with requestId should be valid");
        }
        
        [Test]
        public void ValidateMessageJson_WithValidJson_ShouldReturnTrue()
        {
            // Arrange
            var message = new WebSocketMessage
            {
                version = "1.0",
                type = "test_message",
                timestamp = DateTime.UtcNow.ToString("o"),
                payload = new Dictionary<string, object> { { "key", "value" } }
            };
            string json = JsonConvert.SerializeObject(message);
            
            // Act
            bool isValid = _validator.ValidateMessageJson(json, out WebSocketMessage parsedMessage);
            
            // Assert
            Assert.IsTrue(isValid, "Valid JSON should be validated successfully");
            Assert.IsNotNull(parsedMessage, "Parsed message should not be null");
            Assert.AreEqual("test_message", parsedMessage.type, "Parsed message should have correct type");
            Assert.AreEqual("1.0", parsedMessage.version, "Parsed message should have correct version");
            Assert.IsNotNull(parsedMessage.payload, "Parsed message should have a payload");
            Assert.AreEqual("value", parsedMessage.payload["key"], "Parsed message payload should have correct value");
        }
        
        [Test]
        public void ValidateMessageJson_WithInvalidJson_ShouldReturnFalse()
        {
            // Arrange
            string json = "this is not valid json";
            
            // Act
            bool isValid = _validator.ValidateMessageJson(json, out WebSocketMessage parsedMessage);
            
            // Assert
            Assert.IsFalse(isValid, "Invalid JSON should fail validation");
            Assert.IsNull(parsedMessage, "Parsed message should be null for invalid JSON");
        }
        
        [Test]
        public void ValidateMessageJson_WithIncompleteJson_ShouldReturnFalse()
        {
            // Arrange
            string json = @"{""version"":""1.0"",""type"":""test_message""}"; // Missing timestamp and payload
            
            // Act
            bool isValid = _validator.ValidateMessageJson(json, out WebSocketMessage parsedMessage);
            
            // Assert
            Assert.IsFalse(isValid, "Incomplete JSON should fail validation");
            Assert.IsNotNull(parsedMessage, "Parsed message should be populated even if validation fails");
        }
        
        [Test]
        public void ValidateMessageJson_WithNullOrEmptyJson_ShouldReturnFalse()
        {
            // Act & Assert
            Assert.IsFalse(_validator.ValidateMessageJson(null, out _), "Null JSON should fail validation");
            Assert.IsFalse(_validator.ValidateMessageJson("", out _), "Empty JSON should fail validation");
            Assert.IsFalse(_validator.ValidateMessageJson("  ", out _), "Whitespace JSON should fail validation");
        }
        
        [Test]
        public void IsValidTimestamp_WithValidISO8601_ShouldReturnTrue()
        {
            // Arrange
            string timestamp = DateTime.UtcNow.ToString("o");
            
            // Act
            bool isValid = _validator.IsValidTimestamp(timestamp);
            
            // Assert
            Assert.IsTrue(isValid, "Valid ISO8601 timestamp should be valid");
        }
        
        [Test]
        public void IsValidTimestamp_WithInvalidFormat_ShouldReturnFalse()
        {
            // Act & Assert
            Assert.IsFalse(_validator.IsValidTimestamp("2023-01-01"), "Incomplete timestamp should be invalid");
            Assert.IsFalse(_validator.IsValidTimestamp("not-a-timestamp"), "Non-timestamp string should be invalid");
            Assert.IsFalse(_validator.IsValidTimestamp(""), "Empty timestamp should be invalid");
            Assert.IsFalse(_validator.IsValidTimestamp(null), "Null timestamp should be invalid");
        }
        
        [Test]
        public void GetErrorsForMessage_WithValidMessage_ShouldReturnEmptyList()
        {
            // Arrange
            var message = new WebSocketMessage
            {
                version = "1.0",
                type = "test_message",
                timestamp = DateTime.UtcNow.ToString("o"),
                payload = new Dictionary<string, object> { { "key", "value" } }
            };
            
            // Act
            var errors = _validator.GetErrorsForMessage(message);
            
            // Assert
            Assert.IsEmpty(errors, "Valid message should have no validation errors");
        }
        
        [Test]
        public void GetErrorsForMessage_WithInvalidMessage_ShouldReturnErrors()
        {
            // Arrange
            var message = new WebSocketMessage(); // Empty message
            
            // Act
            var errors = _validator.GetErrorsForMessage(message);
            
            // Assert
            Assert.IsNotEmpty(errors, "Invalid message should have validation errors");
            Assert.AreEqual(4, errors.Count, "Should have 4 validation errors (missing version, type, timestamp, payload)");
            Assert.IsTrue(errors.Contains("Missing version"), "Errors should include missing version");
            Assert.IsTrue(errors.Contains("Missing type"), "Errors should include missing type");
            Assert.IsTrue(errors.Contains("Missing timestamp"), "Errors should include missing timestamp");
            Assert.IsTrue(errors.Contains("Missing payload"), "Errors should include missing payload");
        }
        
        [Test]
        public void GetTimestampAge_WithRecentTimestamp_ShouldReturnCorrectAge()
        {
            // Arrange
            DateTime now = DateTime.UtcNow;
            string timestamp = now.AddSeconds(-30).ToString("o"); // 30 seconds ago
            
            // Act
            TimeSpan age = _validator.GetTimestampAge(timestamp);
            
            // Assert
            Assert.IsTrue(age.TotalSeconds >= 29 && age.TotalSeconds <= 31, 
                $"Age should be approximately 30 seconds (was: {age.TotalSeconds})");
        }
        
        [Test]
        public void GetTimestampAge_WithInvalidTimestamp_ShouldThrowException()
        {
            // Act & Assert
            Assert.Throws<FormatException>(() => _validator.GetTimestampAge("not-a-timestamp"), 
                "Invalid timestamp should throw FormatException");
        }
        
        [Test]
        public void IsMessageExpired_WithFreshMessage_ShouldReturnFalse()
        {
            // Arrange
            var message = new WebSocketMessage
            {
                version = "1.0",
                type = "test_message",
                timestamp = DateTime.UtcNow.ToString("o"),
                payload = new Dictionary<string, object> { { "key", "value" } }
            };
            
            // Act
            bool isExpired = _validator.IsMessageExpired(message, TimeSpan.FromMinutes(5));
            
            // Assert
            Assert.IsFalse(isExpired, "Fresh message should not be expired");
        }
        
        [Test]
        public void IsMessageExpired_WithOldMessage_ShouldReturnTrue()
        {
            // Arrange
            var message = new WebSocketMessage
            {
                version = "1.0",
                type = "test_message",
                timestamp = DateTime.UtcNow.AddMinutes(-10).ToString("o"), // 10 minutes old
                payload = new Dictionary<string, object> { { "key", "value" } }
            };
            
            // Act
            bool isExpired = _validator.IsMessageExpired(message, TimeSpan.FromMinutes(5));
            
            // Assert
            Assert.IsTrue(isExpired, "Message older than expiration time should be expired");
        }
    }
} 