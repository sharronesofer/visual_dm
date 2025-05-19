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
    public class WebSocketMessageParsingTests : WebSocketTestRunner
    {
        private WebSocketMessageParser _parser;
        
        [SetUp]
        public override void Setup()
        {
            base.Setup();
            _parser = new WebSocketMessageParser();
        }
        
        [Test]
        public void SerializeMessage_WithValidData_ShouldProduceValidJson()
        {
            // Arrange
            var message = new WebSocketMessage
            {
                type = "test_message",
                payload = new Dictionary<string, object>
                {
                    { "string_value", "test" },
                    { "int_value", 123 },
                    { "bool_value", true }
                }
            };
            
            // Act
            string json = _parser.SerializeMessage(message);
            
            // Assert
            Assert.IsNotNull(json, "JSON should not be null");
            Assert.IsTrue(json.Contains("\"type\":\"test_message\""), "JSON should contain type");
            Assert.IsTrue(json.Contains("\"string_value\":\"test\""), "JSON should contain string value");
            Assert.IsTrue(json.Contains("\"int_value\":123"), "JSON should contain int value");
            Assert.IsTrue(json.Contains("\"bool_value\":true"), "JSON should contain bool value");
        }
        
        [Test]
        public void DeserializeMessage_WithValidJson_ShouldCreateMessage()
        {
            // Arrange
            string json = @"{
                ""type"": ""test_message"",
                ""payload"": {
                    ""string_value"": ""test"",
                    ""int_value"": 123,
                    ""bool_value"": true
                }
            }";
            
            // Act
            WebSocketMessage message = _parser.DeserializeMessage(json);
            
            // Assert
            Assert.IsNotNull(message, "Message should not be null");
            Assert.AreEqual("test_message", message.type, "Type should match");
            
            Assert.IsNotNull(message.payload, "Payload should not be null");
            Assert.AreEqual("test", message.payload["string_value"], "String value should match");
            Assert.AreEqual(123L, message.payload["int_value"], "Int value should match");
            Assert.AreEqual(true, message.payload["bool_value"], "Bool value should match");
        }
        
        [Test]
        public void DeserializeMessage_WithMissingType_ShouldThrowException()
        {
            // Arrange
            string json = @"{
                ""payload"": {
                    ""string_value"": ""test""
                }
            }";
            
            // Act & Assert
            Assert.Throws<JsonSerializationException>(() => _parser.DeserializeMessage(json), 
                "Should throw exception when message type is missing");
        }
        
        [Test]
        public void DeserializeMessage_WithInvalidJson_ShouldThrowException()
        {
            // Arrange
            string json = @"{
                ""type"": ""test_message"",
                ""payload"": {
                    ""string_value"": ""test""
                }, // Invalid trailing comma
            }";
            
            // Act & Assert
            Assert.Throws<JsonReaderException>(() => _parser.DeserializeMessage(json), 
                "Should throw exception with invalid JSON");
        }
        
        [Test]
        public void DeserializeMessage_WithEmptyJson_ShouldThrowException()
        {
            // Arrange
            string json = "";
            
            // Act & Assert
            Assert.Throws<JsonException>(() => _parser.DeserializeMessage(json), 
                "Should throw exception with empty JSON");
        }
        
        [Test]
        public void SerializeDeserialize_ShouldPreserveAllFields()
        {
            // Arrange
            var originalMessage = new WebSocketMessage
            {
                type = "complex_message",
                payload = new Dictionary<string, object>
                {
                    { "string_value", "test" },
                    { "int_value", 123 },
                    { "float_value", 12.34 },
                    { "bool_value", true },
                    { "null_value", null },
                    { "nested_object", new Dictionary<string, object>
                        {
                            { "nested_key", "nested_value" }
                        }
                    },
                    { "array_value", new List<object> { 1, 2, 3 } }
                }
            };
            
            // Act
            string json = _parser.SerializeMessage(originalMessage);
            WebSocketMessage deserializedMessage = _parser.DeserializeMessage(json);
            
            // Assert
            Assert.AreEqual(originalMessage.type, deserializedMessage.type, "Type should be preserved");
            
            // Check each value in the payload
            Assert.AreEqual(originalMessage.payload["string_value"], deserializedMessage.payload["string_value"], "String value should be preserved");
            Assert.AreEqual(123L, deserializedMessage.payload["int_value"], "Int value should be preserved (as long)");
            
            // For floating point values, we need to handle potential precision issues
            double originalFloat = Convert.ToDouble(originalMessage.payload["float_value"]);
            double deserializedFloat = Convert.ToDouble(deserializedMessage.payload["float_value"]);
            Assert.AreEqual(originalFloat, deserializedFloat, 0.0001, "Float value should be preserved");
            
            Assert.AreEqual(originalMessage.payload["bool_value"], deserializedMessage.payload["bool_value"], "Boolean value should be preserved");
            Assert.IsNull(deserializedMessage.payload["null_value"], "Null value should be preserved");
            
            // Check nested object
            var originalNested = originalMessage.payload["nested_object"] as Dictionary<string, object>;
            var deserializedNested = deserializedMessage.payload["nested_object"] as Newtonsoft.Json.Linq.JObject;
            Assert.IsNotNull(deserializedNested, "Nested object should not be null");
            Assert.AreEqual(originalNested["nested_key"].ToString(), deserializedNested["nested_key"].ToString(), "Nested value should be preserved");
            
            // Check array
            var originalArray = originalMessage.payload["array_value"] as List<object>;
            var deserializedArray = deserializedMessage.payload["array_value"] as Newtonsoft.Json.Linq.JArray;
            Assert.IsNotNull(deserializedArray, "Array should not be null");
            Assert.AreEqual(originalArray.Count, deserializedArray.Count, "Array length should be preserved");
            for (int i = 0; i < originalArray.Count; i++)
            {
                Assert.AreEqual(originalArray[i].ToString(), deserializedArray[i].ToString(), $"Array item {i} should be preserved");
            }
        }
        
        [Test]
        public void ValidateMessage_WithValidMessage_ShouldReturnTrue()
        {
            // Arrange
            var validator = new WebSocketMessageValidator();
            var message = new WebSocketMessage
            {
                type = "valid_message",
                payload = new Dictionary<string, object>
                {
                    { "data", "test" }
                }
            };
            
            // Act
            bool isValid = validator.ValidateMessage(message);
            
            // Assert
            Assert.IsTrue(isValid, "Valid message should validate successfully");
        }
        
        [Test]
        public void ValidateMessage_WithNullType_ShouldReturnFalse()
        {
            // Arrange
            var validator = new WebSocketMessageValidator();
            var message = new WebSocketMessage
            {
                type = null,
                payload = new Dictionary<string, object>
                {
                    { "data", "test" }
                }
            };
            
            // Act
            bool isValid = validator.ValidateMessage(message);
            
            // Assert
            Assert.IsFalse(isValid, "Message with null type should be invalid");
        }
        
        [Test]
        public void ValidateMessage_WithEmptyType_ShouldReturnFalse()
        {
            // Arrange
            var validator = new WebSocketMessageValidator();
            var message = new WebSocketMessage
            {
                type = "",
                payload = new Dictionary<string, object>
                {
                    { "data", "test" }
                }
            };
            
            // Act
            bool isValid = validator.ValidateMessage(message);
            
            // Assert
            Assert.IsFalse(isValid, "Message with empty type should be invalid");
        }
        
        [Test]
        public void ValidateMessage_WithNullPayload_ShouldReturnTrue()
        {
            // Arrange
            var validator = new WebSocketMessageValidator();
            var message = new WebSocketMessage
            {
                type = "valid_message",
                payload = null
            };
            
            // Act
            bool isValid = validator.ValidateMessage(message);
            
            // Assert
            Assert.IsTrue(isValid, "Message with null payload should be valid");
        }
        
        [Test]
        public void ValidateMessage_WithNullMessage_ShouldReturnFalse()
        {
            // Arrange
            var validator = new WebSocketMessageValidator();
            
            // Act
            bool isValid = validator.ValidateMessage(null);
            
            // Assert
            Assert.IsFalse(isValid, "Null message should be invalid");
        }
        
        [Test]
        public void ParseRawMessage_WithValidJson_ShouldReturnValidatedMessage()
        {
            // Arrange
            string json = @"{
                ""type"": ""test_message"",
                ""payload"": {
                    ""data"": ""test""
                }
            }";
            
            // Act
            WebSocketMessage message = _parser.ParseRawMessage(json);
            
            // Assert
            Assert.IsNotNull(message, "Message should not be null");
            Assert.AreEqual("test_message", message.type, "Type should match");
            Assert.IsNotNull(message.payload, "Payload should not be null");
            Assert.AreEqual("test", message.payload["data"], "Payload data should match");
        }
        
        [Test]
        public void ParseRawMessage_WithInvalidJson_ShouldReturnNull()
        {
            // Arrange
            string json = @"{
                ""type"": ""test_message"",
                ""payload"": {
                    ""data"": ""test""
                }, // Invalid trailing comma
            }";
            
            // Act
            WebSocketMessage message = _parser.ParseRawMessage(json);
            
            // Assert
            Assert.IsNull(message, "Message should be null with invalid JSON");
        }
        
        [Test]
        public void ParseRawMessage_WithInvalidMessageFormat_ShouldReturnNull()
        {
            // Arrange
            string json = @"{
                ""not_type"": ""test_message"",
                ""not_payload"": {
                    ""data"": ""test""
                }
            }";
            
            // Act
            WebSocketMessage message = _parser.ParseRawMessage(json);
            
            // Assert
            Assert.IsNull(message, "Message should be null with invalid message format");
        }
        
        [UnityTest]
        public IEnumerator WebSocketClient_ShouldParseIncomingMessages()
        {
            // Arrange
            WebSocketMessage receivedMessage = null;
            _client = CreateAndConnectClient();
            _client.OnMessage += (msg) => {
                receivedMessage = msg;
            };
            
            yield return WaitForConnectionStatus(_client, WebSocketConnectionStatus.Connected);
            
            // Create test message
            var testMessage = new WebSocketMessage
            {
                type = "test_parsed_message",
                payload = new Dictionary<string, object>
                {
                    { "key1", "value1" },
                    { "key2", 123 }
                }
            };
            
            // Act - Mock server sends message
            _mockServer.SendMessageToClient(testMessage);
            
            // Wait for message to be received and processed
            yield return new WaitForSeconds(0.5f);
            
            // Assert
            Assert.IsNotNull(receivedMessage, "Message should be received");
            Assert.AreEqual("test_parsed_message", receivedMessage.type, "Message type should match");
            Assert.AreEqual("value1", receivedMessage.payload["key1"], "Payload key1 should match");
            Assert.AreEqual(123L, receivedMessage.payload["key2"], "Payload key2 should match");
        }
        
        [UnityTest]
        public IEnumerator WebSocketClient_ShouldSerializeOutgoingMessages()
        {
            // Arrange
            string receivedJson = null;
            WebSocketMessage parsedMessage = null;
            
            _mockServer.OnRawMessageReceived += (json) => {
                receivedJson = json;
                try {
                    parsedMessage = JsonConvert.DeserializeObject<WebSocketMessage>(json);
                } catch {}
            };
            
            _client = CreateAndConnectClient();
            yield return WaitForConnectionStatus(_client, WebSocketConnectionStatus.Connected);
            
            // Create test message
            var testMessage = new WebSocketMessage
            {
                type = "outgoing_message",
                payload = new Dictionary<string, object>
                {
                    { "data", "test_data" }
                }
            };
            
            // Act
            _client.Send(testMessage);
            
            // Wait for message to be received by server
            yield return new WaitForSeconds(0.5f);
            
            // Assert
            Assert.IsNotNull(receivedJson, "Raw JSON should be received by server");
            Assert.IsNotNull(parsedMessage, "JSON should be parsable into a WebSocketMessage");
            Assert.AreEqual("outgoing_message", parsedMessage.type, "Message type should match");
            Assert.IsNotNull(parsedMessage.payload, "Payload should not be null");
            Assert.AreEqual("test_data", parsedMessage.payload["data"].ToString(), "Payload data should match");
        }
    }
} 