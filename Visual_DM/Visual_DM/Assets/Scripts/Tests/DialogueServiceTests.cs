using System;
using System.Collections;
using System.Collections.Generic;
using System.Threading.Tasks;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.TestTools;
using VisualDM.Dialogue;
using VisualDM.Core;

namespace VisualDM.Tests
{
    /// <summary>
    /// Tests for DialogueGenerationService functionality including async behaviors
    /// </summary>
    public class DialogueServiceTests
    {
        private DialogueGenerationService _dialogueService;
        private MockGPTClient _mockGPTClient;
        
        [SetUp]
        public void Setup()
        {
            // Create game object for tests
            GameObject testObject = new GameObject("DialogueTestObject");
            
            // Add mocked version of GPTClient
            _mockGPTClient = testObject.AddComponent<MockGPTClient>();
            
            // Add the dialogue service component
            _dialogueService = testObject.AddComponent<DialogueGenerationService>();
        }
        
        [TearDown]
        public void Teardown()
        {
            if (_dialogueService != null)
            {
                GameObject.Destroy(_dialogueService.gameObject);
            }
        }
        
        [UnityTest]
        public IEnumerator GenerateDialogue_WithValidPrompt_ReturnsExpectedResponse()
        {
            // Setup test data
            string prompt = "Hello, how are you?";
            List<string> context = new List<string> { "You are a helpful assistant." };
            
            // Set the mock response
            _mockGPTClient.SetNextResponse(new GPTResponse
            {
                text = "I'm doing well, thank you for asking!",
                error = null
            });
            
            // Call the async method
            Task<GPTResponse> task = _dialogueService.GenerateDialogueAsync(prompt, context);
            
            // Wait for completion
            while (!task.IsCompleted)
            {
                yield return null;
            }
            
            // Get the result
            GPTResponse response = task.Result;
            
            // Verify
            Assert.IsNotNull(response);
            Assert.AreEqual("I'm doing well, thank you for asking!", response.text);
            Assert.IsNull(response.error);
            
            // Verify the mock client was called correctly
            Assert.AreEqual(prompt, _mockGPTClient.LastPrompt);
            CollectionAssert.AreEqual(context, _mockGPTClient.LastContext);
        }
        
        [UnityTest]
        public IEnumerator GenerateDialogue_WithError_ReturnsErrorResponse()
        {
            // Setup error response
            _mockGPTClient.SetNextResponse(new GPTResponse
            {
                text = "",
                error = "API Error: 429 Too Many Requests"
            });
            
            // Call the method
            Task<GPTResponse> task = _dialogueService.GenerateDialogueAsync("Test prompt");
            
            // Wait for completion
            while (!task.IsCompleted)
            {
                yield return null;
            }
            
            // Get the result
            GPTResponse response = task.Result;
            
            // Verify
            Assert.IsNotNull(response);
            Assert.AreEqual("", response.text);
            Assert.AreEqual("API Error: 429 Too Many Requests", response.error);
        }
        
        [UnityTest]
        public IEnumerator GenerateDialogue_WithException_HandlesGracefully()
        {
            // Setup exception
            _mockGPTClient.SetNextException(new Exception("Network error"));
            
            // Call the method
            Task<GPTResponse> task = _dialogueService.GenerateDialogueAsync("Test prompt");
            
            // Wait for completion
            while (!task.IsCompleted)
            {
                yield return null;
            }
            
            // Get the result
            GPTResponse response = task.Result;
            
            // Verify
            Assert.IsNotNull(response);
            Assert.AreEqual("", response.text);
            Assert.AreEqual("Network error", response.error);
        }
        
        [UnityTest]
        public IEnumerator GenerateDialogue_WithConfigOverride_UsesMergedConfig()
        {
            // Create custom config
            GPTConfig customConfig = new GPTConfig
            {
                temperature = 0.9f,
                maxTokens = 50
            };
            
            // Set response
            _mockGPTClient.SetNextResponse(new GPTResponse
            {
                text = "Response with custom config",
                error = null
            });
            
            // Call with custom config
            Task<GPTResponse> task = _dialogueService.GenerateDialogueAsync("Test prompt", null, customConfig);
            
            // Wait for completion
            while (!task.IsCompleted)
            {
                yield return null;
            }
            
            // Verify
            Assert.AreEqual(0.9f, _mockGPTClient.LastConfig.temperature);
            Assert.AreEqual(50, _mockGPTClient.LastConfig.maxTokens);
        }
    }
    
    /// <summary>
    /// Mock implementation of GPTClient for testing DialogueGenerationService
    /// </summary>
    public class MockGPTClient : GPTClient
    {
        // Capture parameters
        public string LastPrompt { get; private set; }
        public List<string> LastContext { get; private set; }
        public GPTConfig LastConfig { get; private set; }
        
        // Response control
        private GPTResponse _nextResponse;
        private Exception _nextException;
        
        public void SetNextResponse(GPTResponse response)
        {
            _nextResponse = response;
            _nextException = null;
        }
        
        public void SetNextException(Exception exception)
        {
            _nextException = exception;
            _nextResponse = null;
        }
        
        // Override the async method
        public override async Task<GPTResponse> GenerateCompletionAsync(string prompt, List<string> context, GPTConfig config)
        {
            // Capture parameters
            LastPrompt = prompt;
            LastContext = context ?? new List<string>();
            LastConfig = config;
            
            // Simulate async operation
            await Task.Delay(50);
            
            // Return exception or response
            if (_nextException != null)
            {
                throw _nextException;
            }
            
            return _nextResponse ?? new GPTResponse { text = "Default mock response" };
        }
    }
} 