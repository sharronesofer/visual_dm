using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using UnityEngine;
using UnityEngine.Networking;
using Newtonsoft.Json;
using Newtonsoft.Json.Serialization;
using System.Text;

namespace VDM.Prompt
{
    /// <summary>
    /// Client for interacting with the backend prompt generation system.
    /// This class allows Unity to fetch prompt templates and generate content
    /// using the backend prompt service.
    /// </summary>
    public class PromptManager : MonoBehaviour
    {
        private static PromptManager _instance;
        public static PromptManager Instance
        {
            get
            {
                if (_instance == null)
                {
                    var go = new GameObject("PromptManager");
                    _instance = go.AddComponent<PromptManager>();
                    DontDestroyOnLoad(go);
                }
                return _instance;
            }
        }

        [SerializeField] private string _baseUrl = "http://localhost:8000";
        [SerializeField] private float _timeoutSeconds = 60f;
        [SerializeField] private bool _enableCaching = true;
        [SerializeField] private bool _enableDebugLogs = true;

        private JsonSerializerSettings _jsonSettings;
        private Dictionary<string, PromptTemplateInfo> _templateCache = new Dictionary<string, PromptTemplateInfo>();
        private Dictionary<string, PromptResponse> _responseCache = new Dictionary<string, PromptResponse>();

        private void Awake()
        {
            if (_instance != null && _instance != this)
            {
                Destroy(gameObject);
                return;
            }

            _instance = this;
            DontDestroyOnLoad(gameObject);
            
            _jsonSettings = new JsonSerializerSettings
            {
                ContractResolver = new CamelCasePropertyNamesContractResolver(),
                NullValueHandling = NullValueHandling.Ignore
            };

            LogDebug("PromptManager initialized");
        }

        #region Public Methods

        /// <summary>
        /// Get a list of all available prompt templates from the server.
        /// </summary>
        /// <returns>List of available template info</returns>
        public async Task<List<PromptTemplateInfo>> GetAvailableTemplatesAsync()
        {
            try
            {
                string url = $"{_baseUrl}/api/v1/prompts/templates";
                string json = await FetchStringAsync(url);
                
                if (string.IsNullOrEmpty(json)) return new List<PromptTemplateInfo>();
                
                var response = JsonConvert.DeserializeObject<List<PromptTemplateInfo>>(json, _jsonSettings);
                
                // Update cache
                if (response != null)
                {
                    foreach (var template in response)
                    {
                        _templateCache[template.Name] = template;
                    }
                }
                
                return response ?? new List<PromptTemplateInfo>();
            }
            catch (Exception ex)
            {
                LogError($"Error fetching templates: {ex.Message}");
                return new List<PromptTemplateInfo>();
            }
        }

        /// <summary>
        /// Get details about a specific prompt template by name.
        /// </summary>
        /// <param name="templateName">Name of the template to retrieve</param>
        /// <returns>Template info or null if not found</returns>
        public async Task<PromptTemplateInfo> GetTemplateAsync(string templateName)
        {
            // Check cache first
            if (_templateCache.TryGetValue(templateName, out var cachedTemplate))
            {
                return cachedTemplate;
            }
            
            try
            {
                string url = $"{_baseUrl}/api/v1/prompts/templates/{templateName}";
                string json = await FetchStringAsync(url);
                
                if (string.IsNullOrEmpty(json)) return null;
                
                var template = JsonConvert.DeserializeObject<PromptTemplateInfo>(json, _jsonSettings);
                
                // Update cache
                if (template != null)
                {
                    _templateCache[template.Name] = template;
                }
                
                return template;
            }
            catch (Exception ex)
            {
                LogError($"Error fetching template '{templateName}': {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Get all templates in a specific category.
        /// </summary>
        /// <param name="category">Category to filter by</param>
        /// <returns>List of templates in the category</returns>
        public async Task<List<PromptTemplateInfo>> GetTemplatesByCategoryAsync(string category)
        {
            try
            {
                string url = $"{_baseUrl}/api/v1/prompts/templates/category/{category}";
                string json = await FetchStringAsync(url);
                
                if (string.IsNullOrEmpty(json)) return new List<PromptTemplateInfo>();
                
                var templates = JsonConvert.DeserializeObject<List<PromptTemplateInfo>>(json, _jsonSettings);
                
                // Update cache
                if (templates != null)
                {
                    foreach (var template in templates)
                    {
                        _templateCache[template.Name] = template;
                    }
                }
                
                return templates ?? new List<PromptTemplateInfo>();
            }
            catch (Exception ex)
            {
                LogError($"Error fetching templates for category '{category}': {ex.Message}");
                return new List<PromptTemplateInfo>();
            }
        }

        /// <summary>
        /// Generate content using a prompt template.
        /// </summary>
        /// <param name="templateName">Name of the template to use</param>
        /// <param name="context">Dictionary of context variables for the template</param>
        /// <param name="entityId">Optional entity ID for context gathering</param>
        /// <param name="contextTypes">Optional list of context types to gather</param>
        /// <param name="useCache">Whether to use cached responses</param>
        /// <returns>Generated content response</returns>
        public async Task<PromptResponse> GenerateAsync(
            string templateName, 
            Dictionary<string, object> context = null,
            string entityId = null,
            List<string> contextTypes = null,
            bool? useCache = null)
        {
            bool useCacheValue = useCache ?? _enableCaching;
            
            // Build cache key if caching is enabled
            string cacheKey = null;
            if (useCacheValue)
            {
                StringBuilder sb = new StringBuilder(templateName);
                sb.Append(":");
                
                if (entityId != null)
                {
                    sb.Append(entityId);
                }
                
                if (context != null)
                {
                    var sortedKeys = new List<string>(context.Keys);
                    sortedKeys.Sort();
                    foreach (var key in sortedKeys)
                    {
                        sb.Append($"|{key}={context[key]}");
                    }
                }
                
                if (contextTypes != null && contextTypes.Count > 0)
                {
                    contextTypes.Sort();
                    sb.Append("|types=");
                    sb.Append(string.Join(",", contextTypes));
                }
                
                cacheKey = sb.ToString();
                
                // Check cache
                if (_responseCache.TryGetValue(cacheKey, out var cachedResponse))
                {
                    LogDebug($"Using cached response for '{templateName}'");
                    return cachedResponse;
                }
            }
            
            try
            {
                string url = $"{_baseUrl}/api/v1/prompts/generate";
                
                var request = new GenerateRequest
                {
                    TemplateName = templateName,
                    AdditionalContext = context ?? new Dictionary<string, object>(),
                    EntityId = entityId,
                    ContextTypes = contextTypes ?? new List<string>(),
                    UseCache = useCacheValue
                };
                
                string requestJson = JsonConvert.SerializeObject(request, _jsonSettings);
                string responseJson = await PostJsonAsync(url, requestJson);
                
                if (string.IsNullOrEmpty(responseJson))
                {
                    return new PromptResponse
                    {
                        Success = false,
                        Content = "Failed to generate content: Empty response",
                        TemplateName = templateName
                    };
                }
                
                var response = JsonConvert.DeserializeObject<PromptResponse>(responseJson, _jsonSettings);
                
                // Update cache
                if (response != null && response.Success && useCacheValue && cacheKey != null)
                {
                    _responseCache[cacheKey] = response;
                }
                
                return response ?? new PromptResponse
                {
                    Success = false,
                    Content = "Failed to parse response",
                    TemplateName = templateName
                };
            }
            catch (Exception ex)
            {
                LogError($"Error generating content with template '{templateName}': {ex.Message}");
                return new PromptResponse
                {
                    Success = false,
                    Content = $"Error: {ex.Message}",
                    TemplateName = templateName
                };
            }
        }

        /// <summary>
        /// Clear the prompt response cache.
        /// </summary>
        public void ClearCache()
        {
            _responseCache.Clear();
            LogDebug("Response cache cleared");
        }

        /// <summary>
        /// Set the base URL for the prompt API.
        /// </summary>
        /// <param name="baseUrl">New base URL</param>
        public void SetBaseUrl(string baseUrl)
        {
            _baseUrl = baseUrl;
            LogDebug($"Base URL set to: {baseUrl}");
        }

        #endregion

        #region Private Methods

        private async Task<string> FetchStringAsync(string url)
        {
            using (UnityWebRequest request = UnityWebRequest.Get(url))
            {
                request.timeout = Mathf.RoundToInt(_timeoutSeconds);
                
                LogDebug($"Fetching: {url}");
                var operation = request.SendWebRequest();
                
                while (!operation.isDone)
                {
                    await Task.Yield();
                }
                
                if (request.result != UnityWebRequest.Result.Success)
                {
                    LogError($"Web request failed: {request.error}");
                    return null;
                }
                
                return request.downloadHandler.text;
            }
        }

        private async Task<string> PostJsonAsync(string url, string jsonData)
        {
            using (UnityWebRequest request = new UnityWebRequest(url, "POST"))
            {
                byte[] bodyRaw = Encoding.UTF8.GetBytes(jsonData);
                request.uploadHandler = new UploadHandlerRaw(bodyRaw);
                request.downloadHandler = new DownloadHandlerBuffer();
                request.timeout = Mathf.RoundToInt(_timeoutSeconds);
                request.SetRequestHeader("Content-Type", "application/json");
                
                LogDebug($"POST request to {url}");
                LogDebug($"Request body: {jsonData}");
                
                var operation = request.SendWebRequest();
                
                while (!operation.isDone)
                {
                    await Task.Yield();
                }
                
                if (request.result != UnityWebRequest.Result.Success)
                {
                    LogError($"POST request failed: {request.error}");
                    LogError($"Response: {request.downloadHandler?.text}");
                    return null;
                }
                
                return request.downloadHandler.text;
            }
        }

        private void LogDebug(string message)
        {
            if (_enableDebugLogs)
            {
                Debug.Log($"[PromptManager] {message}");
            }
        }

        private void LogError(string message)
        {
            Debug.LogError($"[PromptManager] {message}");
        }

        #endregion
    }

    #region Data Models

    [Serializable]
    public class PromptTemplateInfo
    {
        [JsonProperty("name")]
        public string Name { get; set; }
        
        [JsonProperty("description")]
        public string Description { get; set; }
        
        [JsonProperty("version")]
        public string Version { get; set; }
        
        [JsonProperty("category")]
        public string Category { get; set; }
        
        [JsonProperty("tags")]
        public List<string> Tags { get; set; }
        
        [JsonProperty("variableInfo")]
        public Dictionary<string, string> VariableInfo { get; set; }
        
        [JsonProperty("requiredVariables")]
        public List<string> RequiredVariables { get; set; }
    }

    [Serializable]
    public class PromptResponse
    {
        [JsonProperty("success")]
        public bool Success { get; set; }
        
        [JsonProperty("content")]
        public string Content { get; set; }
        
        [JsonProperty("templateName")]
        public string TemplateName { get; set; }
        
        [JsonProperty("tokens")]
        public PromptTokenInfo Tokens { get; set; }
        
        [JsonProperty("metadata")]
        public Dictionary<string, object> Metadata { get; set; }
        
        [JsonProperty("error")]
        public string Error { get; set; }
    }

    [Serializable]
    public class PromptTokenInfo
    {
        [JsonProperty("promptTokens")]
        public int PromptTokens { get; set; }
        
        [JsonProperty("completionTokens")]
        public int CompletionTokens { get; set; }
        
        [JsonProperty("totalTokens")]
        public int TotalTokens { get; set; }
    }

    [Serializable]
    public class GenerateRequest
    {
        [JsonProperty("templateName")]
        public string TemplateName { get; set; }
        
        [JsonProperty("contextTypes")]
        public List<string> ContextTypes { get; set; }
        
        [JsonProperty("entityId")]
        public string EntityId { get; set; }
        
        [JsonProperty("additionalContext")]
        public Dictionary<string, object> AdditionalContext { get; set; }
        
        [JsonProperty("useCache")]
        public bool UseCache { get; set; }
    }

    #endregion
} 