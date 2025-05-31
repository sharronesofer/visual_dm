using VDM.Infrastructure.Core.Core.Ui;
using System.Collections.Generic;
using System.Linq;
using System;
using UnityEngine.UI;
using UnityEngine;
using TMPro;
using VDM.Systems.Llm.Models;
using VDM.Systems.Llm.Services;
using VDM.UI.Core;

namespace VDM.Systems.Llm.Ui
{
    /// <summary>
    /// AI Integration Dashboard providing comprehensive AI management and monitoring
    /// </summary>
    public class AiIntegrationDashboard : BaseUIComponent
    {
        [Header("Dashboard Tabs")]
        [SerializeField] private Button modelsTab;
        [SerializeField] private Button promptsTab;
        [SerializeField] private Button generationTab;
        [SerializeField] private Button metricsTab;
        [SerializeField] private Button testingTab;

        [Header("Tab Panels")]
        [SerializeField] private GameObject modelsPanel;
        [SerializeField] private GameObject promptsPanel;
        [SerializeField] private GameObject generationPanel;
        [SerializeField] private GameObject metricsPanel;
        [SerializeField] private GameObject testingPanel;

        [Header("Models Management")]
        [SerializeField] private Transform modelsListContainer;
        [SerializeField] private GameObject modelItemPrefab;
        [SerializeField] private Button addModelButton;
        [SerializeField] private Button refreshModelsButton;
        [SerializeField] private TextMeshProUGUI modelsStatusText;

        [Header("Model Configuration")]
        [SerializeField] private TMP_InputField modelIdInput;
        [SerializeField] private TMP_InputField displayNameInput;
        [SerializeField] private TMP_Dropdown providerDropdown;
        [SerializeField] private Slider temperatureSlider;
        [SerializeField] private TMP_InputField maxTokensInput;
        [SerializeField] private Toggle enabledToggle;
        [SerializeField] private Button saveModelButton;

        [Header("Prompt Templates")]
        [SerializeField] private Transform promptsListContainer;
        [SerializeField] private GameObject promptItemPrefab;
        [SerializeField] private Button createPromptButton;
        [SerializeField] private Dropdown promptCategoryFilter;

        [Header("Prompt Editor")]
        [SerializeField] private TMP_InputField promptNameInput;
        [SerializeField] private TMP_InputField promptDescriptionInput;
        [SerializeField] private TMP_InputField systemPromptInput;
        [SerializeField] private TMP_InputField userPromptInput;
        [SerializeField] private TMP_InputField requiredParamsInput;
        [SerializeField] private Button savePromptButton;
        [SerializeField] private Button testPromptButton;

        [Header("Content Generation")]
        [SerializeField] private Transform activeTasksContainer;
        [SerializeField] private Transform queuedTasksContainer;
        [SerializeField] private GameObject taskItemPrefab;
        [SerializeField] private Button clearCompletedButton;
        [SerializeField] private TextMeshProUGUI taskQueueStatusText;

        [Header("AI Metrics")]
        [SerializeField] private TextMeshProUGUI totalRequestsText;
        [SerializeField] private TextMeshProUGUI successRateText;
        [SerializeField] private TextMeshProUGUI avgResponseTimeText;
        [SerializeField] private TextMeshProUGUI totalCostText;
        [SerializeField] private TextMeshProUGUI tokensUsedText;
        [SerializeField] private Transform providerStatsContainer;
        [SerializeField] private GameObject providerStatPrefab;

        [Header("Model Testing")]
        [SerializeField] private TMP_Dropdown testModelDropdown;
        [SerializeField] private TMP_InputField testPromptInput;
        [SerializeField] private Button runTestButton;
        [SerializeField] private TextMeshProUGUI testResultText;
        [SerializeField] private Transform evaluationContainer;
        [SerializeField] private GameObject evaluationItemPrefab;

        [Header("Settings")]
        [SerializeField] private float refreshInterval = 2.0f;
        [SerializeField] private int maxDisplayedTasks = 50;

        // Private fields
        private LlmService llmService;
        private List<GameObject> modelItems = new List<GameObject>();
        private List<GameObject> promptItems = new List<GameObject>();
        private List<GameObject> taskItems = new List<GameObject>();
        private List<GameObject> providerStatItems = new List<GameObject>();
        private List<GameObject> evaluationItems = new List<GameObject>();
        
        private AIModelConfig selectedModel;
        private PromptTemplate selectedPrompt;
        private string currentTab = "models";
        private float lastRefreshTime;
        private bool isInitialized;

        protected override void Awake()
        {
            base.Awake();
            InitializeControls();
        }

        private void Start()
        {
            Initialize();
        }

        private void Update()
        {
            if (!isInitialized) return;

            // Auto-refresh active data
            if (Time.time - lastRefreshTime >= refreshInterval)
            {
                RefreshCurrentTab();
                lastRefreshTime = Time.time;
            }
        }

        /// <summary>
        /// Initialize the AI integration dashboard
        /// </summary>
        public override void Initialize()
        {
            if (isInitialized) return;

            llmService = LlmService.Instance;
            if (llmService == null)
            {
                Debug.LogError("AiIntegrationDashboard: LlmService not found!");
                return;
            }

            // Subscribe to LLM service events
            LlmService.OnRequestStarted += OnRequestStarted;
            LlmService.OnResponseReceived += OnResponseReceived;
            LlmService.OnMetricsUpdated += OnMetricsUpdated;
            LlmService.OnTaskQueueUpdated += OnTaskQueueUpdated;

            // Initialize UI components
            InitializeDropdowns();
            InitializeTabSystem();
            
            // Load initial data
            ShowTab("models");
            RefreshCurrentTab();

            isInitialized = true;
            Debug.Log("AiIntegrationDashboard initialized successfully");
        }

        private void InitializeControls()
        {
            // Tab buttons
            modelsTab.onClick.AddListener(() => ShowTab("models"));
            promptsTab.onClick.AddListener(() => ShowTab("prompts"));
            generationTab.onClick.AddListener(() => ShowTab("generation"));
            metricsTab.onClick.AddListener(() => ShowTab("metrics"));
            testingTab.onClick.AddListener(() => ShowTab("testing"));

            // Models panel
            addModelButton.onClick.AddListener(AddNewModel);
            refreshModelsButton.onClick.AddListener(RefreshModels);
            saveModelButton.onClick.AddListener(SaveModelConfiguration);

            // Prompts panel
            createPromptButton.onClick.AddListener(CreateNewPrompt);
            savePromptButton.onClick.AddListener(SavePromptTemplate);
            testPromptButton.onClick.AddListener(TestPromptTemplate);
            promptCategoryFilter.onValueChanged.AddListener(OnPromptCategoryChanged);

            // Generation panel
            clearCompletedButton.onClick.AddListener(ClearCompletedTasks);

            // Testing panel
            runTestButton.onClick.AddListener(RunModelTest);

            // Slider events
            temperatureSlider.onValueChanged.AddListener(OnTemperatureChanged);
        }

        private void InitializeDropdowns()
        {
            // Provider dropdown
            providerDropdown.options.Clear();
            foreach (AIProvider provider in Enum.GetValues(typeof(AIProvider)))
            {
                providerDropdown.options.Add(new TMP_Dropdown.OptionData(provider.ToString()));
            }
            providerDropdown.RefreshShownValue();

            // Prompt category filter
            promptCategoryFilter.options.Clear();
            promptCategoryFilter.options.Add(new Dropdown.OptionData("All Categories"));
            promptCategoryFilter.options.Add(new Dropdown.OptionData("Narrative"));
            promptCategoryFilter.options.Add(new Dropdown.OptionData("Dialogue"));
            promptCategoryFilter.options.Add(new Dropdown.OptionData("Quest"));
            promptCategoryFilter.options.Add(new Dropdown.OptionData("Description"));
            promptCategoryFilter.RefreshShownValue();
        }

        private void InitializeTabSystem()
        {
            // Set up tab colors
            var tabs = new[] { modelsTab, promptsTab, generationTab, metricsTab, testingTab };
            foreach (var tab in tabs)
            {
                var colors = tab.colors;
                colors.normalColor = Color.gray;
                colors.selectedColor = Color.white;
                tab.colors = colors;
            }
        }

        private void ShowTab(string tabName)
        {
            currentTab = tabName;

            // Hide all panels
            modelsPanel.SetActive(false);
            promptsPanel.SetActive(false);
            generationPanel.SetActive(false);
            metricsPanel.SetActive(false);
            testingPanel.SetActive(false);

            // Reset tab button colors
            var tabs = new[] { modelsTab, promptsTab, generationTab, metricsTab, testingTab };
            foreach (var tab in tabs)
            {
                tab.GetComponent<Image>().color = Color.gray;
            }

            // Show selected panel and highlight tab
            switch (tabName)
            {
                case "models":
                    modelsPanel.SetActive(true);
                    modelsTab.GetComponent<Image>().color = Color.white;
                    RefreshModels();
                    break;
                case "prompts":
                    promptsPanel.SetActive(true);
                    promptsTab.GetComponent<Image>().color = Color.white;
                    RefreshPrompts();
                    break;
                case "generation":
                    generationPanel.SetActive(true);
                    generationTab.GetComponent<Image>().color = Color.white;
                    RefreshGenerationTasks();
                    break;
                case "metrics":
                    metricsPanel.SetActive(true);
                    metricsTab.GetComponent<Image>().color = Color.white;
                    RefreshMetrics();
                    break;
                case "testing":
                    testingPanel.SetActive(true);
                    testingTab.GetComponent<Image>().color = Color.white;
                    RefreshTestingPanel();
                    break;
            }
        }

        private void RefreshCurrentTab()
        {
            switch (currentTab)
            {
                case "models": RefreshModels(); break;
                case "prompts": RefreshPrompts(); break;
                case "generation": RefreshGenerationTasks(); break;
                case "metrics": RefreshMetrics(); break;
                case "testing": RefreshTestingPanel(); break;
            }
        }

        private void RefreshModels()
        {
            var models = llmService.GetAvailableModels();
            
            // Clear existing items
            foreach (var item in modelItems)
            {
                if (item != null) Destroy(item);
            }
            modelItems.Clear();

            // Create new items
            foreach (var model in models)
            {
                CreateModelItem(model);
            }

            modelsStatusText.text = $"{models.Count} models available";
        }

        private void CreateModelItem(AIModelConfig model)
        {
            var item = Instantiate(modelItemPrefab, modelsListContainer);
            modelItems.Add(item);

            var texts = item.GetComponentsInChildren<TextMeshProUGUI>();
            var button = item.GetComponent<Button>();
            var toggle = item.GetComponentInChildren<Toggle>();

            if (texts.Length >= 4)
            {
                texts[0].text = model.displayName ?? model.modelId;
                texts[1].text = model.provider.ToString();
                texts[2].text = $"Max Tokens: {model.maxTokens}";
                texts[3].text = $"Cost: ${model.costPerToken:F6}/token";
            }

            if (toggle != null)
            {
                toggle.isOn = model.isEnabled;
                toggle.onValueChanged.AddListener((enabled) => {
                    model.isEnabled = enabled;
                    // Save model changes would go here
                });
            }

            if (button != null)
            {
                button.onClick.AddListener(() => SelectModel(model));
            }
        }

        private void SelectModel(AIModelConfig model)
        {
            selectedModel = model;
            
            // Populate configuration fields
            modelIdInput.text = model.modelId;
            displayNameInput.text = model.displayName;
            providerDropdown.value = (int)model.provider;
            temperatureSlider.value = model.temperature;
            maxTokensInput.text = model.maxTokens.ToString();
            enabledToggle.isOn = model.isEnabled;
        }

        private void RefreshPrompts()
        {
            var category = promptCategoryFilter.value == 0 ? null : promptCategoryFilter.options[promptCategoryFilter.value].text;
            var prompts = llmService.GetPromptTemplates(category);
            
            // Clear existing items
            foreach (var item in promptItems)
            {
                if (item != null) Destroy(item);
            }
            promptItems.Clear();

            // Create new items
            foreach (var prompt in prompts)
            {
                CreatePromptItem(prompt);
            }
        }

        private void CreatePromptItem(PromptTemplate prompt)
        {
            var item = Instantiate(promptItemPrefab, promptsListContainer);
            promptItems.Add(item);

            var texts = item.GetComponentsInChildren<TextMeshProUGUI>();
            var button = item.GetComponent<Button>();

            if (texts.Length >= 3)
            {
                texts[0].text = prompt.name;
                texts[1].text = prompt.category;
                texts[2].text = prompt.description;
            }

            if (button != null)
            {
                button.onClick.AddListener(() => SelectPrompt(prompt));
            }
        }

        private void SelectPrompt(PromptTemplate prompt)
        {
            selectedPrompt = prompt;
            
            // Populate prompt editor fields
            promptNameInput.text = prompt.name;
            promptDescriptionInput.text = prompt.description;
            systemPromptInput.text = prompt.systemPrompt;
            userPromptInput.text = prompt.userPromptTemplate;
            requiredParamsInput.text = string.Join(", ", prompt.requiredParameters);
        }

        private void RefreshGenerationTasks()
        {
            var activeTasks = llmService.GetActiveTasks();
            var queuedTasks = llmService.GetQueuedTasks();
            
            // Clear existing items
            foreach (var item in taskItems)
            {
                if (item != null) Destroy(item);
            }
            taskItems.Clear();

            // Create active task items
            foreach (var task in activeTasks.Take(maxDisplayedTasks))
            {
                CreateTaskItem(task, activeTasksContainer, true);
            }

            // Create queued task items
            foreach (var task in queuedTasks.Take(maxDisplayedTasks))
            {
                CreateTaskItem(task, queuedTasksContainer, false);
            }

            taskQueueStatusText.text = $"Active: {activeTasks.Count}, Queued: {queuedTasks.Count}";
        }

        private void CreateTaskItem(GenerationTask task, Transform container, bool isActive)
        {
            var item = Instantiate(taskItemPrefab, container);
            taskItems.Add(item);

            var texts = item.GetComponentsInChildren<TextMeshProUGUI>();
            var statusIcon = item.GetComponentInChildren<Image>();

            if (texts.Length >= 3)
            {
                texts[0].text = task.taskType;
                texts[1].text = task.status.ToString();
                texts[2].text = task.createdAt.ToString("HH:mm:ss");
            }

            // Set status color
            if (statusIcon != null)
            {
                statusIcon.color = task.status switch
                {
                    RequestStatus.Pending => Color.yellow,
                    RequestStatus.Processing => Color.blue,
                    RequestStatus.Completed => Color.green,
                    RequestStatus.Failed => Color.red,
                    RequestStatus.Cancelled => Color.gray,
                    _ => Color.white
                };
            }
        }

        private void RefreshMetrics()
        {
            var metrics = llmService.GetCurrentMetrics();
            if (metrics == null) return;

            // Update metric displays
            totalRequestsText.text = $"Total Requests: {metrics.totalRequests}";
            successRateText.text = $"Success Rate: {(metrics.totalRequests > 0 ? (float)metrics.successfulRequests / metrics.totalRequests * 100 : 0):F1}%";
            avgResponseTimeText.text = $"Avg Response Time: {metrics.averageResponseTime:F2}s";
            totalCostText.text = $"Total Cost: ${metrics.totalCost:F4}";
            tokensUsedText.text = $"Tokens Used: {metrics.totalTokensUsed:N0}";

            // Update provider statistics
            RefreshProviderStats(metrics);
        }

        private void RefreshProviderStats(AIMetrics metrics)
        {
            // Clear existing items
            foreach (var item in providerStatItems)
            {
                if (item != null) Destroy(item);
            }
            providerStatItems.Clear();

            // Create provider stat items
            foreach (var providerStat in metrics.requestsByProvider)
            {
                var item = Instantiate(providerStatPrefab, providerStatsContainer);
                providerStatItems.Add(item);

                var texts = item.GetComponentsInChildren<TextMeshProUGUI>();
                if (texts.Length >= 2)
                {
                    texts[0].text = providerStat.Key.ToString();
                    texts[1].text = $"{providerStat.Value} requests";
                }
            }
        }

        private void RefreshTestingPanel()
        {
            var models = llmService.GetAvailableModels();
            
            // Update test model dropdown
            testModelDropdown.options.Clear();
            foreach (var model in models)
            {
                testModelDropdown.options.Add(new TMP_Dropdown.OptionData(model.displayName ?? model.modelId));
            }
            testModelDropdown.RefreshShownValue();
        }

        // Event handlers
        private void OnRequestStarted(AIRequest request)
        {
            if (currentTab == "generation")
            {
                RefreshGenerationTasks();
            }
        }

        private void OnResponseReceived(AIResponse response)
        {
            if (currentTab == "generation")
            {
                RefreshGenerationTasks();
            }
            if (currentTab == "metrics")
            {
                RefreshMetrics();
            }
        }

        private void OnMetricsUpdated(AIMetrics metrics)
        {
            if (currentTab == "metrics")
            {
                RefreshMetrics();
            }
        }

        private void OnTaskQueueUpdated(List<GenerationTask> tasks)
        {
            if (currentTab == "generation")
            {
                RefreshGenerationTasks();
            }
        }

        // UI action handlers
        private void AddNewModel()
        {
            selectedModel = new AIModelConfig();
            SelectModel(selectedModel);
        }

        private void SaveModelConfiguration()
        {
            if (selectedModel == null) return;

            // Update model from UI fields
            selectedModel.modelId = modelIdInput.text;
            selectedModel.displayName = displayNameInput.text;
            selectedModel.provider = (AIProvider)providerDropdown.value;
            selectedModel.temperature = temperatureSlider.value;
            selectedModel.isEnabled = enabledToggle.isOn;

            if (int.TryParse(maxTokensInput.text, out var maxTokens))
            {
                selectedModel.maxTokens = maxTokens;
            }

            Debug.Log($"Saved model configuration: {selectedModel.displayName}");
            RefreshModels();
        }

        private void CreateNewPrompt()
        {
            selectedPrompt = new PromptTemplate
            {
                name = "New Template",
                category = "Custom",
                description = "Enter description here"
            };
            SelectPrompt(selectedPrompt);
        }

        private void SavePromptTemplate()
        {
            if (selectedPrompt == null) return;

            // Update prompt from UI fields
            selectedPrompt.name = promptNameInput.text;
            selectedPrompt.description = promptDescriptionInput.text;
            selectedPrompt.systemPrompt = systemPromptInput.text;
            selectedPrompt.userPromptTemplate = userPromptInput.text;
            
            var paramsList = requiredParamsInput.text.Split(',');
            selectedPrompt.requiredParameters.Clear();
            foreach (var param in paramsList)
            {
                var trimmed = param.Trim();
                if (!string.IsNullOrEmpty(trimmed))
                {
                    selectedPrompt.requiredParameters.Add(trimmed);
                }
            }

            llmService.AddPromptTemplate(selectedPrompt);
            Debug.Log($"Saved prompt template: {selectedPrompt.name}");
            RefreshPrompts();
        }

        private async void TestPromptTemplate()
        {
            if (selectedPrompt == null) return;

            testResultText.text = "Testing prompt template...";

            try
            {
                var testParams = new Dictionary<string, object>();
                foreach (var param in selectedPrompt.requiredParameters)
                {
                    testParams[param] = $"test_{param}";
                }

                var response = await llmService.GenerateFromTemplate(selectedPrompt.templateId, testParams);
                testResultText.text = response.isSuccess ? 
                    $"Test successful!\nResponse: {response.content?.Substring(0, Math.Min(100, response.content.Length ?? 0))}..." :
                    $"Test failed: {response.errorMessage}";
            }
            catch (Exception ex)
            {
                testResultText.text = $"Test error: {ex.Message}";
            }
        }

        private void ClearCompletedTasks()
        {
            // This would clear completed tasks from the display
            RefreshGenerationTasks();
        }

        private async void RunModelTest()
        {
            var models = llmService.GetAvailableModels();
            if (testModelDropdown.value >= models.Count) return;

            var selectedTestModel = models[testModelDropdown.value];
            testResultText.text = "Testing model...";

            try
            {
                var evaluation = await llmService.TestModel(selectedTestModel);
                CreateEvaluationItem(evaluation);
                testResultText.text = $"Test completed. Overall rating: {evaluation.overallRating:F2}/1.0";
            }
            catch (Exception ex)
            {
                testResultText.text = $"Test failed: {ex.Message}";
            }
        }

        private void CreateEvaluationItem(ModelEvaluation evaluation)
        {
            var item = Instantiate(evaluationItemPrefab, evaluationContainer);
            evaluationItems.Add(item);

            var texts = item.GetComponentsInChildren<TextMeshProUGUI>();
            if (texts.Length >= 5)
            {
                texts[0].text = evaluation.modelId;
                texts[1].text = $"Speed: {evaluation.speedScore:F2}";
                texts[2].text = $"Cost: {evaluation.costEfficiency:F2}";
                texts[3].text = $"Quality: {evaluation.qualityScore:F2}";
                texts[4].text = $"Overall: {evaluation.overallRating:F2}";
            }
        }

        private void OnTemperatureChanged(float value)
        {
            if (selectedModel != null)
            {
                selectedModel.temperature = value;
            }
        }

        private void OnPromptCategoryChanged(int index)
        {
            RefreshPrompts();
        }

        protected override void OnDestroy()
        {
            base.OnDestroy();
            
            // Unsubscribe from events
            if (llmService != null)
            {
                LlmService.OnRequestStarted -= OnRequestStarted;
                LlmService.OnResponseReceived -= OnResponseReceived;
                LlmService.OnMetricsUpdated -= OnMetricsUpdated;
                LlmService.OnTaskQueueUpdated -= OnTaskQueueUpdated;
            }

            isInitialized = false;
        }
    }
} 