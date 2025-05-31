using System.Collections.Generic;
using System;
using UnityEngine;


namespace VDM.Systems.Llm.Models
{
    /// <summary>
    /// Supported AI model providers
    /// </summary>
    public enum AIProvider
    {
        OpenAI,
        Anthropic,
        Perplexity,
        Groq,
        Local
    }

    /// <summary>
    /// AI request status
    /// </summary>
    public enum RequestStatus
    {
        Pending,
        Processing,
        Completed,
        Failed,
        Cancelled
    }

    /// <summary>
    /// AI model configuration
    /// </summary>
    [Serializable]
    public class AIModelConfig
    {
        public string modelId;
        public string displayName;
        public AIProvider provider;
        public float temperature;
        public int maxTokens;
        public float topP;
        public float frequencyPenalty;
        public float presencePenalty;
        public bool isEnabled;
        public float costPerToken;

        public AIModelConfig()
        {
            temperature = 0.7f;
            maxTokens = 2048;
            topP = 1.0f;
            frequencyPenalty = 0.0f;
            presencePenalty = 0.0f;
            isEnabled = true;
            costPerToken = 0.0001f;
        }
    }

    /// <summary>
    /// AI request data
    /// </summary>
    [Serializable]
    public class AIRequest
    {
        public string requestId;
        public string systemPrompt;
        public string userPrompt;
        public AIModelConfig modelConfig;
        public DateTime createdAt;
        public RequestStatus status;
        public Dictionary<string, object> metadata;

        public AIRequest()
        {
            requestId = Guid.NewGuid().ToString();
            createdAt = DateTime.UtcNow;
            status = RequestStatus.Pending;
            metadata = new Dictionary<string, object>();
        }
    }

    /// <summary>
    /// AI response data
    /// </summary>
    [Serializable]
    public class AIResponse
    {
        public string requestId;
        public string content;
        public int tokensUsed;
        public float processingTime;
        public DateTime completedAt;
        public bool isSuccess;
        public string errorMessage;
        public Dictionary<string, object> metadata;

        public AIResponse()
        {
            completedAt = DateTime.UtcNow;
            metadata = new Dictionary<string, object>();
        }
    }

    /// <summary>
    /// Prompt template for AI content generation
    /// </summary>
    [Serializable]
    public class PromptTemplate
    {
        public string templateId;
        public string name;
        public string description;
        public string systemPrompt;
        public string userPromptTemplate;
        public List<string> requiredParameters;
        public Dictionary<string, string> defaultValues;
        public string category;
        public bool isActive;

        public PromptTemplate()
        {
            templateId = Guid.NewGuid().ToString();
            requiredParameters = new List<string>();
            defaultValues = new Dictionary<string, string>();
            isActive = true;
        }
    }

    /// <summary>
    /// AI generation context for narrative systems
    /// </summary>
    [Serializable]
    public class GenerationContext
    {
        public string worldId;
        public string sessionId;
        public Dictionary<string, object> worldState;
        public List<string> activeCharacters;
        public List<string> activeQuests;
        public List<string> recentEvents;
        public Dictionary<string, float> narrativeWeights;

        public GenerationContext()
        {
            worldState = new Dictionary<string, object>();
            activeCharacters = new List<string>();
            activeQuests = new List<string>();
            recentEvents = new List<string>();
            narrativeWeights = new Dictionary<string, float>();
        }
    }

    /// <summary>
    /// AI monitoring metrics
    /// </summary>
    [Serializable]
    public class AIMetrics
    {
        public int totalRequests;
        public int successfulRequests;
        public int failedRequests;
        public float averageResponseTime;
        public int totalTokensUsed;
        public float totalCost;
        public DateTime lastReset;
        public Dictionary<AIProvider, int> requestsByProvider;
        public Dictionary<string, float> averageResponseTimeByModel;

        public AIMetrics()
        {
            lastReset = DateTime.UtcNow;
            requestsByProvider = new Dictionary<AIProvider, int>();
            averageResponseTimeByModel = new Dictionary<string, float>();
        }
    }

    /// <summary>
    /// Content generation task
    /// </summary>
    [Serializable]
    public class GenerationTask
    {
        public string taskId;
        public string taskType;
        public string description;
        public PromptTemplate template;
        public Dictionary<string, object> parameters;
        public GenerationContext context;
        public RequestStatus status;
        public DateTime createdAt;
        public DateTime? completedAt;
        public AIResponse response;
        public float priority;

        public GenerationTask()
        {
            taskId = Guid.NewGuid().ToString();
            parameters = new Dictionary<string, object>();
            status = RequestStatus.Pending;
            createdAt = DateTime.UtcNow;
            priority = 1.0f;
        }
    }

    /// <summary>
    /// AI model evaluation data
    /// </summary>
    [Serializable]
    public class ModelEvaluation
    {
        public string modelId;
        public string evaluationId;
        public float qualityScore;
        public float speedScore;
        public float costEfficiency;
        public float overallRating;
        public List<string> strengths;
        public List<string> weaknesses;
        public DateTime evaluatedAt;
        public string evaluatorId;

        public ModelEvaluation()
        {
            evaluationId = Guid.NewGuid().ToString();
            strengths = new List<string>();
            weaknesses = new List<string>();
            evaluatedAt = DateTime.UtcNow;
        }
    }

    /// <summary>
    /// AI conversation history
    /// </summary>
    [Serializable]
    public class ConversationHistory
    {
        public string conversationId;
        public List<AIRequest> requests;
        public List<AIResponse> responses;
        public GenerationContext context;
        public DateTime startedAt;
        public DateTime lastActivity;
        public bool isActive;

        public ConversationHistory()
        {
            conversationId = Guid.NewGuid().ToString();
            requests = new List<AIRequest>();
            responses = new List<AIResponse>();
            startedAt = DateTime.UtcNow;
            lastActivity = DateTime.UtcNow;
            isActive = true;
        }
    }

    /// <summary>
    /// Training data for AI model fine-tuning
    /// </summary>
    [Serializable]
    public class TrainingData
    {
        public string datasetId;
        public string name;
        public string description;
        public List<TrainingExample> examples;
        public Dictionary<string, object> metadata;
        public DateTime createdAt;
        public DateTime lastModified;
        public bool isValidated;

        public TrainingData()
        {
            datasetId = Guid.NewGuid().ToString();
            examples = new List<TrainingExample>();
            metadata = new Dictionary<string, object>();
            createdAt = DateTime.UtcNow;
            lastModified = DateTime.UtcNow;
        }
    }

    /// <summary>
    /// Individual training example
    /// </summary>
    [Serializable]
    public class TrainingExample
    {
        public string exampleId;
        public string input;
        public string expectedOutput;
        public string actualOutput;
        public float qualityScore;
        public Dictionary<string, object> metadata;

        public TrainingExample()
        {
            exampleId = Guid.NewGuid().ToString();
            metadata = new Dictionary<string, object>();
        }
    }
} 