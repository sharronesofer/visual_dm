using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using UnityEngine;

namespace VisualDM.Dialogue
{
    /// <summary>
    /// Configuration for GPT API requests
    /// </summary>
    [Serializable]
    public class GPTConfig
    {
        public string model = "gpt-3.5-turbo";
        public float temperature = 0.7f;
        public int maxTokens = 512;
        public List<string> stop = new List<string>();
    }

    /// <summary>
    /// Response from GPT API
    /// </summary>
    [Serializable]
    public class GPTResponse
    {
        public string text = "";
        public GPTUsage usage;
        public string error;
        public object raw;

        [Serializable]
        public class GPTUsage
        {
            public int promptTokens;
            public int completionTokens;
            public int totalTokens;
        }
    }

    /// <summary>
    /// DialogueGenerationService provides a high-level interface for generating dialogue using GPTClient.
    /// Handles prompt formatting, context, error propagation, and logging.
    /// </summary>
    public class DialogueGenerationService : MonoBehaviour
    {
        [SerializeField] private GPTConfig defaultConfig = new GPTConfig();
        
        private GPTClient _gptClient;

        private void Awake()
        {
            // Initialize the GPT client when the service starts
            _gptClient = GetComponent<GPTClient>();
            
            if (_gptClient == null)
            {
                _gptClient = gameObject.AddComponent<GPTClient>();
                Debug.LogWarning("GPTClient was not attached to DialogueGenerationService; adding component automatically.");
            }
        }

        /// <summary>
        /// Generates dialogue text given a prompt and context.
        /// </summary>
        /// <param name="prompt">The main prompt string</param>
        /// <param name="context">Array of previous conversation strings</param>
        /// <param name="config">Optional GPTConfig overrides</param>
        /// <returns>A GPTResponse containing the generated text or error information</returns>
        public async Task<GPTResponse> GenerateDialogueAsync(string prompt, List<string> context = null, GPTConfig config = null)
        {
            context = context ?? new List<string>();
            GPTConfig mergedConfig = MergeConfigs(config);
            
            try
            {
                var response = await _gptClient.GenerateCompletionAsync(prompt, context, mergedConfig);
                
                if (!string.IsNullOrEmpty(response.error))
                {
                    LogError("GPT API Error", response.error, new Dictionary<string, object>
                    {
                        { "prompt", prompt },
                        { "context", context },
                        { "config", mergedConfig }
                    });
                }
                
                return response;
            }
            catch (Exception ex)
            {
                LogError("DialogueGenerationService Exception", ex.Message, new Dictionary<string, object>
                {
                    { "prompt", prompt },
                    { "context", context },
                    { "config", mergedConfig }
                });
                
                return new GPTResponse
                {
                    text = "",
                    error = ex.Message,
                    raw = ex
                };
            }
        }

        /// <summary>
        /// Merges default and custom GPT configs, with custom settings taking precedence
        /// </summary>
        private GPTConfig MergeConfigs(GPTConfig customConfig)
        {
            if (customConfig == null)
            {
                return defaultConfig;
            }
            
            GPTConfig mergedConfig = new GPTConfig
            {
                model = !string.IsNullOrEmpty(customConfig.model) ? customConfig.model : defaultConfig.model,
                temperature = customConfig.temperature > 0 ? customConfig.temperature : defaultConfig.temperature,
                maxTokens = customConfig.maxTokens > 0 ? customConfig.maxTokens : defaultConfig.maxTokens,
                stop = customConfig.stop != null && customConfig.stop.Count > 0 ? customConfig.stop : defaultConfig.stop
            };
            
            return mergedConfig;
        }

        /// <summary>
        /// Logs errors for debugging and monitoring
        /// </summary>
        private void LogError(string message, string error, Dictionary<string, object> meta)
        {
            string metaJson = JsonUtility.ToJson(meta);
            Debug.LogError($"[DialogueGenerationService] {message}: {error} | Meta: {metaJson}");
        }
    }
} 