using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using UnityEngine;
using Newtonsoft.Json;
using VDM.Systems.Llm.Models;
using VDM.Infrastructure.Services;
using VDM.Infrastructure.Services.Services.Http;


namespace VDM.Systems.Llm.Services
{
    /// <summary>
    /// LLM service for AI integration and content generation
    /// </summary>
    public class LlmService : MonoBehaviour, ISystemService
    {
        [Header("Configuration")]
        [SerializeField] private string baseUrl = "http://localhost:8000/api/llm";
        [SerializeField] private float requestTimeout = 30.0f;
        [SerializeField] private int maxConcurrentRequests = 5;
        [SerializeField] private bool enableMetricsTracking = true;

        [Header("Default Models")]
        [SerializeField] private string defaultNarrativeModel = "gpt-4";
        [SerializeField] private string defaultDialogueModel = "gpt-3.5-turbo";
        [SerializeField] private string defaultDescriptionModel = "gpt-3.5-turbo";

        [Header("Performance")]
        [SerializeField] private bool enableResponseCaching = true;
        [SerializeField] private int cacheMaxEntries = 100;
        [SerializeField] private float cacheTimeoutMinutes = 60.0f;

        // Events for UI components to subscribe to
        public static event Action<AIRequest> OnRequestStarted;
        public static event Action<AIResponse> OnResponseReceived;
        public static event Action<AIMetrics> OnMetricsUpdated;
        public static event Action<List<GenerationTask>> OnTaskQueueUpdated;
        public static event Action<string, string> OnModelStatusChanged;

        // Private fields
        private VDM.Runtime.Core.Services.HttpService httpService;
        private List<AIModelConfig> availableModels;
        private Dictionary<string, PromptTemplate> promptTemplates;
        private Queue<GenerationTask> taskQueue;
        private List<GenerationTask> activeTasks;
        private AIMetrics currentMetrics;
        private Dictionary<string, AIResponse> responseCache;
        private bool isInitialized;

        // Singleton pattern
        public static LlmService Instance { get; private set; }

        private void Awake()
        {
            if (Instance == null)
            {
                Instance = this;
                DontDestroyOnLoad(gameObject);
                Initialize();
            }
            else
            {
                Destroy(gameObject);
            }
        }

        /// <summary>
        /// Initialize the LLM service
        /// </summary>
        public void Initialize()
        {
            if (isInitialized) return;

            httpService = FindObjectOfType<VDM.Runtime.Core.Services.HttpService>();
            if (httpService == null)
            {
                Debug.LogError("LlmService: HttpService not found!");
                return;
            }

            availableModels = new List<AIModelConfig>();
            promptTemplates = new Dictionary<string, PromptTemplate>();
            taskQueue = new Queue<GenerationTask>();
            activeTasks = new List<GenerationTask>();
            currentMetrics = new AIMetrics();
            responseCache = new Dictionary<string, AIResponse>();

            // Load default models and templates
            LoadDefaultModels();
            LoadDefaultPromptTemplates();

            isInitialized = true;
            Debug.Log("LlmService initialized successfully");
        }

        private void Update()
        {
            if (!isInitialized) return;

            // Process task queue
            ProcessTaskQueue();

            // Clean expired cache entries
            if (enableResponseCaching)
            {
                CleanExpiredCacheEntries();
            }
        }

        /// <summary>
        /// Submit an AI generation request
        /// </summary>
        public async Task<AIResponse> SubmitRequest(AIRequest request)
        {
            if (!isInitialized)
            {
                return new AIResponse { isSuccess = false, errorMessage = "LlmService not initialized" };
            }

            // Check cache first
            if (enableResponseCaching)
            {
                var cacheKey = GenerateCacheKey(request);
                if (responseCache.ContainsKey(cacheKey))
                {
                    return responseCache[cacheKey];
                }
            }

            // Notify UI of request start
            OnRequestStarted?.Invoke(request);

            try
            {
                var requestData = new Dictionary<string, object>
                {
                    ["system_prompt"] = request.systemPrompt,
                    ["user_prompt"] = request.userPrompt,
                    ["model_config"] = request.modelConfig,
                    ["metadata"] = request.metadata
                };

                var response = await httpService.PostAsync($"{baseUrl}/generate", requestData);
                
                AIResponse aiResponse;
                if (response.IsSuccess)
                {
                    aiResponse = JsonUtility.FromJson<AIResponse>(response.Data);
                    aiResponse.isSuccess = true;
                    aiResponse.requestId = request.requestId;
                }
                else
                {
                    aiResponse = new AIResponse
                    {
                        requestId = request.requestId,
                        isSuccess = false,
                        errorMessage = response.Error
                    };
                }

                // Cache response
                if (enableResponseCaching && aiResponse.isSuccess)
                {
                    var cacheKey = GenerateCacheKey(request);
                    responseCache[cacheKey] = aiResponse;
                }

                // Update metrics
                UpdateMetrics(request, aiResponse);

                // Notify UI of response
                OnResponseReceived?.Invoke(aiResponse);

                return aiResponse;
            }
            catch (Exception ex)
            {
                var errorResponse = new AIResponse
                {
                    requestId = request.requestId,
                    isSuccess = false,
                    errorMessage = ex.Message
                };

                UpdateMetrics(request, errorResponse);
                OnResponseReceived?.Invoke(errorResponse);
                
                return errorResponse;
            }
        }

        /// <summary>
        /// Generate content using a prompt template
        /// </summary>
        public async Task<AIResponse> GenerateFromTemplate(string templateId, Dictionary<string, object> parameters, AIModelConfig modelConfig = null)
        {
            if (!promptTemplates.ContainsKey(templateId))
            {
                return new AIResponse { isSuccess = false, errorMessage = $"Template '{templateId}' not found" };
            }

            var template = promptTemplates[templateId];
            var processedPrompt = ProcessPromptTemplate(template, parameters);

            var request = new AIRequest
            {
                systemPrompt = template.systemPrompt,
                userPrompt = processedPrompt,
                modelConfig = modelConfig ?? GetDefaultModelForTemplate(template)
            };

            return await SubmitRequest(request);
        }

        /// <summary>
        /// Add a generation task to the queue
        /// </summary>
        public void QueueGenerationTask(GenerationTask task)
        {
            if (!isInitialized) return;

            taskQueue.Enqueue(task);
            OnTaskQueueUpdated?.Invoke(new List<GenerationTask>(taskQueue));
        }

        /// <summary>
        /// Get available AI models
        /// </summary>
        public List<AIModelConfig> GetAvailableModels()
        {
            return new List<AIModelConfig>(availableModels);
        }

        /// <summary>
        /// Get prompt templates by category
        /// </summary>
        public List<PromptTemplate> GetPromptTemplates(string category = null)
        {
            var templates = new List<PromptTemplate>();
            foreach (var template in promptTemplates.Values)
            {
                if (string.IsNullOrEmpty(category) || template.category == category)
                {
                    templates.Add(template);
                }
            }
            return templates;
        }

        /// <summary>
        /// Get current AI metrics
        /// </summary>
        public AIMetrics GetCurrentMetrics()
        {
            return currentMetrics;
        }

        /// <summary>
        /// Get active generation tasks
        /// </summary>
        public List<GenerationTask> GetActiveTasks()
        {
            return new List<GenerationTask>(activeTasks);
        }

        /// <summary>
        /// Get queued generation tasks
        /// </summary>
        public List<GenerationTask> GetQueuedTasks()
        {
            return new List<GenerationTask>(taskQueue);
        }

        /// <summary>
        /// Add or update a prompt template
        /// </summary>
        public void AddPromptTemplate(PromptTemplate template)
        {
            promptTemplates[template.templateId] = template;
        }

        /// <summary>
        /// Remove a prompt template
        /// </summary>
        public bool RemovePromptTemplate(string templateId)
        {
            return promptTemplates.Remove(templateId);
        }

        /// <summary>
        /// Test AI model connection and performance
        /// </summary>
        public async Task<ModelEvaluation> TestModel(AIModelConfig modelConfig)
        {
            var testRequest = new AIRequest
            {
                systemPrompt = "You are a helpful assistant.",
                userPrompt = "Hello, please respond with 'Test successful' to confirm the connection.",
                modelConfig = modelConfig
            };

            var startTime = DateTime.UtcNow;
            var response = await SubmitRequest(testRequest);
            var endTime = DateTime.UtcNow;

            var evaluation = new ModelEvaluation
            {
                modelId = modelConfig.modelId,
                speedScore = CalculateSpeedScore((float)(endTime - startTime).TotalSeconds),
                costEfficiency = CalculateCostEfficiency(response.tokensUsed, modelConfig.costPerToken),
                qualityScore = CalculateQualityScore(response.content, "Test successful"),
                evaluatedAt = DateTime.UtcNow
            };

            evaluation.overallRating = (evaluation.speedScore + evaluation.costEfficiency + evaluation.qualityScore) / 3f;

            return evaluation;
        }

        private void LoadDefaultModels()
        {
            // Add default OpenAI models
            availableModels.Add(new AIModelConfig
            {
                modelId = "gpt-4",
                displayName = "GPT-4",
                provider = AIProvider.OpenAI,
                costPerToken = 0.00003f,
                maxTokens = 8192
            });

            availableModels.Add(new AIModelConfig
            {
                modelId = "gpt-3.5-turbo",
                displayName = "GPT-3.5 Turbo",
                provider = AIProvider.OpenAI,
                costPerToken = 0.000002f,
                maxTokens = 4096
            });

            // Add Anthropic models
            availableModels.Add(new AIModelConfig
            {
                modelId = "claude-3-sonnet-20240229",
                displayName = "Claude 3 Sonnet",
                provider = AIProvider.Anthropic,
                costPerToken = 0.000015f,
                maxTokens = 4096
            });
        }

        private void LoadDefaultPromptTemplates()
        {
            // Narrative generation template
            var narrativeTemplate = new PromptTemplate
            {
                name = "Narrative Generation",
                description = "Generate narrative content for story progression",
                category = "Narrative",
                systemPrompt = "You are a skilled dungeon master creating engaging narrative content for a tabletop RPG.",
                userPromptTemplate = "Generate a narrative description for the following scenario:\n\nContext: {context}\nCharacters: {characters}\nLocation: {location}\nTone: {tone}\n\nProvide vivid, immersive narrative that advances the story.",
                requiredParameters = new List<string> { "context", "characters", "location", "tone" }
            };
            promptTemplates[narrativeTemplate.templateId] = narrativeTemplate;

            // Dialogue generation template
            var dialogueTemplate = new PromptTemplate
            {
                name = "NPC Dialogue",
                description = "Generate dialogue for NPCs",
                category = "Dialogue",
                systemPrompt = "You are creating dialogue for non-player characters in a tabletop RPG.",
                userPromptTemplate = "Generate dialogue for an NPC with the following characteristics:\n\nName: {name}\nPersonality: {personality}\nBackground: {background}\nCurrent situation: {situation}\nSpeaking to: {speaker}\n\nProvide authentic, character-appropriate dialogue.",
                requiredParameters = new List<string> { "name", "personality", "background", "situation", "speaker" }
            };
            promptTemplates[dialogueTemplate.templateId] = dialogueTemplate;

            // Quest generation template
            var questTemplate = new PromptTemplate
            {
                name = "Quest Generation",
                description = "Generate quest content and objectives",
                category = "Quest",
                systemPrompt = "You are designing quests for a tabletop RPG adventure.",
                userPromptTemplate = "Create a quest with the following parameters:\n\nQuest type: {quest_type}\nDifficulty: {difficulty}\nLocation: {location}\nFaction involvement: {faction}\nReward type: {reward_type}\n\nProvide quest title, description, objectives, and potential complications.",
                requiredParameters = new List<string> { "quest_type", "difficulty", "location", "faction", "reward_type" }
            };
            promptTemplates[questTemplate.templateId] = questTemplate;
        }

        private void ProcessTaskQueue()
        {
            // Process tasks if we have capacity
            while (taskQueue.Count > 0 && activeTasks.Count < maxConcurrentRequests)
            {
                var task = taskQueue.Dequeue();
                activeTasks.Add(task);
                ProcessGenerationTask(task);
            }

            // Clean up completed tasks
            activeTasks.RemoveAll(task => task.status == RequestStatus.Completed || task.status == RequestStatus.Failed);

            // Notify UI of queue updates
            OnTaskQueueUpdated?.Invoke(new List<GenerationTask>(taskQueue));
        }

        private async void ProcessGenerationTask(GenerationTask task)
        {
            task.status = RequestStatus.Processing;

            try
            {
                var response = await GenerateFromTemplate(task.template.templateId, task.parameters);
                task.response = response;
                task.status = response.isSuccess ? RequestStatus.Completed : RequestStatus.Failed;
                task.completedAt = DateTime.UtcNow;
            }
            catch (Exception ex)
            {
                task.status = RequestStatus.Failed;
                task.completedAt = DateTime.UtcNow;
                task.response = new AIResponse
                {
                    isSuccess = false,
                    errorMessage = ex.Message
                };
                Debug.LogError($"Task processing error: {ex.Message}");
            }
        }

        private string ProcessPromptTemplate(PromptTemplate template, Dictionary<string, object> parameters)
        {
            var processedPrompt = template.userPromptTemplate;

            // Replace parameters
            foreach (var parameter in parameters)
            {
                var placeholder = "{" + parameter.Key + "}";
                processedPrompt = processedPrompt.Replace(placeholder, parameter.Value?.ToString() ?? "");
            }

            // Apply default values for missing parameters
            foreach (var defaultValue in template.defaultValues)
            {
                var placeholder = "{" + defaultValue.Key + "}";
                if (processedPrompt.Contains(placeholder))
                {
                    processedPrompt = processedPrompt.Replace(placeholder, defaultValue.Value);
                }
            }

            return processedPrompt;
        }

        private AIModelConfig GetDefaultModelForTemplate(PromptTemplate template)
        {
            var modelId = template.category switch
            {
                "Narrative" => defaultNarrativeModel,
                "Dialogue" => defaultDialogueModel,
                _ => defaultDescriptionModel
            };

            return availableModels.Find(m => m.modelId == modelId) ?? availableModels[0];
        }

        private string GenerateCacheKey(AIRequest request)
        {
            var keyData = $"{request.systemPrompt}|{request.userPrompt}|{request.modelConfig.modelId}";
            return Convert.ToBase64String(System.Text.Encoding.UTF8.GetBytes(keyData));
        }

        private void UpdateMetrics(AIRequest request, AIResponse response)
        {
            currentMetrics.totalRequests++;
            
            if (response.isSuccess)
            {
                currentMetrics.successfulRequests++;
                currentMetrics.totalTokensUsed += response.tokensUsed;
                currentMetrics.totalCost += response.tokensUsed * request.modelConfig.costPerToken;
                
                // Update average response time
                var newAverage = (currentMetrics.averageResponseTime * (currentMetrics.successfulRequests - 1) + response.processingTime) / currentMetrics.successfulRequests;
                currentMetrics.averageResponseTime = newAverage;
            }
            else
            {
                currentMetrics.failedRequests++;
            }

            // Update provider statistics
            if (!currentMetrics.requestsByProvider.ContainsKey(request.modelConfig.provider))
            {
                currentMetrics.requestsByProvider[request.modelConfig.provider] = 0;
            }
            currentMetrics.requestsByProvider[request.modelConfig.provider]++;

            OnMetricsUpdated?.Invoke(currentMetrics);
        }

        private float CalculateSpeedScore(float responseTimeSeconds)
        {
            // Lower response time = higher score
            return Mathf.Clamp01(10f / (responseTimeSeconds + 1f));
        }

        private float CalculateCostEfficiency(int tokensUsed, float costPerToken)
        {
            var totalCost = tokensUsed * costPerToken;
            // Lower cost = higher efficiency score
            return Mathf.Clamp01(1f / (totalCost * 1000f + 1f));
        }

        private float CalculateQualityScore(string response, string expected)
        {
            // Simple quality check - in practice this would be more sophisticated
            if (string.IsNullOrEmpty(response)) return 0f;
            if (response.ToLower().Contains(expected.ToLower())) return 1f;
            return 0.5f; // Partial credit for any response
        }

        private void CleanExpiredCacheEntries()
        {
            // Remove cache entries older than timeout
            var expiredKeys = new List<string>();
            var cutoffTime = DateTime.UtcNow.AddMinutes(-cacheTimeoutMinutes);

            foreach (var entry in responseCache)
            {
                if (entry.Value.completedAt < cutoffTime)
                {
                    expiredKeys.Add(entry.Key);
                }
            }

            foreach (var key in expiredKeys)
            {
                responseCache.Remove(key);
            }

            // Maintain cache size limit
            if (responseCache.Count > cacheMaxEntries)
            {
                var entriesToRemove = responseCache.Count - cacheMaxEntries;
                var oldestEntries = new List<KeyValuePair<string, AIResponse>>(responseCache);
                oldestEntries.Sort((a, b) => a.Value.completedAt.CompareTo(b.Value.completedAt));

                for (int i = 0; i < entriesToRemove; i++)
                {
                    responseCache.Remove(oldestEntries[i].Key);
                }
            }
        }

        public void Cleanup()
        {
            isInitialized = false;
            taskQueue?.Clear();
            activeTasks?.Clear();
            responseCache?.Clear();
        }

        private void OnDestroy()
        {
            Cleanup();
        }
    }
} 