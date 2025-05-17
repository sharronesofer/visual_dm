using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using UnityEngine;
using UnityEngine.Networking;
using System.Text;
using VisualDM.Core;

namespace VisualDM.Dialogue
{
    /// <summary>
    /// Client for interacting with GPT/OpenAI API
    /// </summary>
    public class GPTClient : MonoBehaviour
    {
        [Header("API Configuration")]
        [SerializeField] private string apiUrl = "https://api.openai.com/v1/chat/completions";
        [SerializeField] private int requestTimeoutSeconds = 10;
        [SerializeField] private int maxRetries = 3;
        [SerializeField] private int backoffBaseMs = 500;

        [Header("Rate Limiting")]
        [SerializeField] private int rateLimit = 60; // Max requests per minute
        [SerializeField] private int windowMs = 60000; // 60 seconds

        private string _apiKey;
        private List<long> _requests = new List<long>();
        private GPTUsageStats _usageStats;
        private EventBus _eventBus;

        [Serializable]
        private class GPTUsageStats
        {
            public int totalTokens;
            public int rollingTokens;
            public int windowMs;
            public long lastReset;
        }

        [Serializable]
        private class ChatMessage
        {
            public string role;
            public string content;
        }

        [Serializable]
        private class ChatRequestBody
        {
            public string model;
            public List<ChatMessage> messages;
            public float temperature;
            public int max_tokens;
            public List<string> stop;
        }

        [Serializable]
        private class ChatResponseBody
        {
            public ChatChoice[] choices;
            public ChatUsage usage;

            [Serializable]
            public class ChatChoice
            {
                public ChatMessage message;
                public int index;
                public string finish_reason;
            }

            [Serializable]
            public class ChatUsage
            {
                public int prompt_tokens;
                public int completion_tokens;
                public int total_tokens;
            }
        }

        private void Awake()
        {
            _usageStats = new GPTUsageStats
            {
                totalTokens = 0,
                rollingTokens = 0,
                windowMs = windowMs,
                lastReset = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds()
            };
            
            // Get the EventBus from the scene
            _eventBus = EventBus.Instance;
            
            // Try to get the API key from PlayerPrefs or a secure storage
            _apiKey = PlayerPrefs.GetString("OpenAI_APIKey", "");
        }

        /// <summary>
        /// Sets the API key for OpenAI requests
        /// </summary>
        public void SetApiKey(string apiKey)
        {
            _apiKey = apiKey;
            PlayerPrefs.SetString("OpenAI_APIKey", apiKey);
        }

        /// <summary>
        /// Generates a completion from GPT given a prompt and context
        /// </summary>
        public async Task<GPTResponse> GenerateCompletionAsync(string prompt, List<string> context, GPTConfig config)
        {
            // Check if API key is set
            if (string.IsNullOrEmpty(_apiKey))
            {
                return new GPTResponse
                {
                    text = "",
                    error = "API key not set",
                    raw = null
                };
            }
            
            await EnforceRateLimitAsync();
            
            // Create the messages array from context and prompt
            var messages = new List<ChatMessage>();
            foreach (var ctx in context)
            {
                messages.Add(new ChatMessage { role = "system", content = ctx });
            }
            messages.Add(new ChatMessage { role = "user", content = prompt });
            
            // Create the request body
            var requestBody = new ChatRequestBody
            {
                model = config.model,
                messages = messages,
                temperature = config.temperature,
                max_tokens = config.maxTokens,
                stop = config.stop
            };
            
            // Emit request event
            _eventBus.Emit("gpt_request", new Dictionary<string, object>
            {
                { "prompt", prompt },
                { "context", context },
                { "config", config }
            });
            
            // Send the request
            try
            {
                return await SendRequestWithRetriesAsync(requestBody);
            }
            catch (Exception ex)
            {
                _eventBus.Emit("gpt_error", ex);
                return new GPTResponse
                {
                    text = "",
                    error = ex.Message,
                    raw = ex
                };
            }
        }

        /// <summary>
        /// Sends the GPT request with retry logic
        /// </summary>
        private async Task<GPTResponse> SendRequestWithRetriesAsync(ChatRequestBody requestBody)
        {
            Exception lastException = null;
            
            // Try initial request
            try
            {
                return await SendRequestAsync(requestBody);
            }
            catch (Exception ex)
            {
                lastException = ex;
                _eventBus.Emit("gpt_error", ex);
            }
            
            // Retry with exponential backoff
            for (int attempt = 1; attempt <= maxRetries; attempt++)
            {
                try
                {
                    // Wait with exponential backoff
                    int delayMs = (int)Math.Pow(2, attempt) * backoffBaseMs;
                    await Task.Delay(delayMs);
                    
                    return await SendRequestAsync(requestBody);
                }
                catch (Exception ex)
                {
                    lastException = ex;
                    
                    if (attempt == maxRetries)
                    {
                        _eventBus.Emit("gpt_fallback", ex);
                    }
                }
            }
            
            // All attempts failed
            return new GPTResponse
            {
                text = "",
                error = lastException?.Message ?? "Unknown error during API request",
                raw = lastException
            };
        }

        /// <summary>
        /// Sends a single request to the GPT API
        /// </summary>
        private async Task<GPTResponse> SendRequestAsync(ChatRequestBody requestBody)
        {
            // Convert request body to JSON
            string jsonBody = JsonUtility.ToJson(requestBody);
            
            // Create web request
            using (UnityWebRequest request = new UnityWebRequest(apiUrl, "POST"))
            {
                byte[] bodyRaw = Encoding.UTF8.GetBytes(jsonBody);
                request.uploadHandler = new UploadHandlerRaw(bodyRaw);
                request.downloadHandler = new DownloadHandlerBuffer();
                request.SetRequestHeader("Content-Type", "application/json");
                request.SetRequestHeader("Authorization", $"Bearer {_apiKey}");
                request.timeout = requestTimeoutSeconds;
                
                // Send request
                var operation = request.SendWebRequest();
                
                // Wait for completion
                while (!operation.isDone)
                {
                    await Task.Yield();
                }
                
                // Check for errors
                if (request.result != UnityWebRequest.Result.Success)
                {
                    throw new Exception($"API Error: {request.responseCode} - {request.error} - {request.downloadHandler.text}");
                }
                
                // Parse response
                string responseJson = request.downloadHandler.text;
                ChatResponseBody responseBody = JsonUtility.FromJson<ChatResponseBody>(responseJson);
                
                if (responseBody == null || responseBody.choices == null || responseBody.choices.Length == 0 || 
                    responseBody.choices[0].message == null)
                {
                    throw new Exception("Invalid API response format");
                }
                
                // Update token usage
                if (responseBody.usage != null)
                {
                    UpdateUsage(responseBody.usage.total_tokens);
                }
                
                // Return response
                return new GPTResponse
                {
                    text = responseBody.choices[0].message.content,
                    usage = new GPTResponse.GPTUsage
                    {
                        promptTokens = responseBody.usage?.prompt_tokens ?? 0,
                        completionTokens = responseBody.usage?.completion_tokens ?? 0,
                        totalTokens = responseBody.usage?.total_tokens ?? 0
                    },
                    raw = responseBody,
                    error = null
                };
            }
        }

        /// <summary>
        /// Enforces the rate limit by waiting if necessary
        /// </summary>
        private async Task EnforceRateLimitAsync()
        {
            long now = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds();
            
            // Remove timestamps older than window
            _requests.RemoveAll(t => now - t >= windowMs);
            
            // If at rate limit, wait until we can make a new request
            if (_requests.Count >= rateLimit && _requests.Count > 0)
            {
                long wait = windowMs - (now - _requests[0]);
                if (wait > 0)
                {
                    await Task.Delay((int)wait);
                }
            }
            
            // Add current request timestamp
            _requests.Add(DateTimeOffset.UtcNow.ToUnixTimeMilliseconds());
        }

        /// <summary>
        /// Updates token usage statistics
        /// </summary>
        private void UpdateUsage(int tokens)
        {
            long now = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds();
            
            // Reset rolling tokens if window has passed
            if (now - _usageStats.lastReset > _usageStats.windowMs)
            {
                _usageStats.rollingTokens = 0;
                _usageStats.lastReset = now;
            }
            
            // Update token counts
            if (tokens > 0)
            {
                _usageStats.totalTokens += tokens;
                _usageStats.rollingTokens += tokens;
            }
        }

        /// <summary>
        /// Returns current usage statistics
        /// </summary>
        public GPTUsageStats GetUsageStats()
        {
            return _usageStats;
        }

        /// <summary>
        /// Formats emotion context for prompt injection
        /// </summary>
        public static string FormatEmotionContextForPrompt(List<EmotionState> emotions)
        {
            if (emotions == null || emotions.Count == 0)
            {
                return "No emotions are currently active.";
            }
            
            List<string> formattedEmotions = new List<string>();
            foreach (var emotion in emotions)
            {
                string desc = !string.IsNullOrEmpty(emotion.description) ? $", {emotion.description}" : "";
                formattedEmotions.Add($"{emotion.name} (intensity: {emotion.intensity}{desc})");
            }
            
            return "Current emotions: " + string.Join(", ", formattedEmotions);
        }

        /// <summary>
        /// Emotion state for prompt injection
        /// </summary>
        [Serializable]
        public class EmotionState
        {
            public string name;
            public float intensity;
            public string description;
        }
        
        /// <summary>
        /// Estimates the token count in a text string
        /// </summary>
        public static int CountTokens(string text)
        {
            // Simple approximation: 1 token ≈ 4 characters (for English)
            if (string.IsNullOrEmpty(text)) return 0;
            return Mathf.CeilToInt(text.Length / 4f);
        }
    }
} 