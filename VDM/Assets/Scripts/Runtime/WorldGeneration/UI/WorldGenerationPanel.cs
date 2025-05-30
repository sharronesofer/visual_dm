using System.Collections.Generic;
using System.Linq;
using System;
using TMPro;
using UnityEngine.UI;
using UnityEngine;
using VDM.Runtime.WorldGeneration.Models;
using VDM.Runtime.WorldGeneration.Services;


namespace VDM.Runtime.WorldGeneration.UI
{
    /// <summary>
    /// UI panel for world generation controls and monitoring
    /// </summary>
    public class WorldGenerationPanel : MonoBehaviour
    {
        [Header("UI References")]
        [SerializeField] private TMP_Dropdown templateDropdown;
        [SerializeField] private TMP_InputField worldNameInput;
        [SerializeField] private TMP_InputField worldDescriptionInput;
        [SerializeField] private Slider biomeDiversitySlider;
        [SerializeField] private TMP_Text biomeDiversityLabel;
        [SerializeField] private Slider settlementDensitySlider;
        [SerializeField] private TMP_Text settlementDensityLabel;
        [SerializeField] private Slider resourceAbundanceSlider;
        [SerializeField] private TMP_Text resourceAbundanceLabel;
        [SerializeField] private Button generateButton;
        [SerializeField] private Button cancelButton;
        [SerializeField] private ProgressBar progressBar;
        [SerializeField] private TMP_Text statusText;
        [SerializeField] private TMP_Text progressText;
        [SerializeField] private ScrollRect logScrollRect;
        [SerializeField] private TMP_Text logText;

        [Header("Continent Management")]
        [SerializeField] private Transform continentListParent;
        [SerializeField] private GameObject continentItemPrefab;
        [SerializeField] private Button addContinentButton;
        [SerializeField] private Button refreshContinentsButton;

        [Header("Biome Display")]
        [SerializeField] private Transform biomeListParent;
        [SerializeField] private GameObject biomeItemPrefab;

        [Header("Configuration")]
        [SerializeField] private bool enableRealTimeUpdates = true;
        [SerializeField] private float updateInterval = 1f;

        // Services
        private WorldGenerationService worldGenService;
        private WorldGenerationWebSocketHandler webSocketHandler;

        // State
        private List<WorldTemplate> availableTemplates = new List<WorldTemplate>();
        private List<ContinentModel> continents = new List<ContinentModel>();
        private List<BiomeModel> biomes = new List<BiomeModel>();
        private WorldGenerationProgress currentProgress;
        private bool isGenerating = false;

        // Events
        public event Action<WorldGenerationResult> OnWorldGenerationComplete;
        public event Action<string> OnWorldGenerationError;

        private void Awake()
        {
            worldGenService = FindObjectOfType<WorldGenerationService>();
            webSocketHandler = FindObjectOfType<WorldGenerationWebSocketHandler>();

            if (worldGenService == null)
            {
                Debug.LogError("WorldGenerationPanel requires WorldGenerationService");
            }

            if (webSocketHandler == null)
            {
                Debug.LogError("WorldGenerationPanel requires WorldGenerationWebSocketHandler");
            }
        }

        private void Start()
        {
            InitializeUI();
            SetupEventHandlers();
            LoadInitialData();
        }

        private void OnDestroy()
        {
            CleanupEventHandlers();
        }

        #region Initialization

        private void InitializeUI()
        {
            // Setup sliders
            biomeDiversitySlider.onValueChanged.AddListener(OnBiomeDiversityChanged);
            settlementDensitySlider.onValueChanged.AddListener(OnSettlementDensityChanged);
            resourceAbundanceSlider.onValueChanged.AddListener(OnResourceAbundanceChanged);

            // Setup buttons
            generateButton.onClick.AddListener(OnGenerateButtonClicked);
            cancelButton.onClick.AddListener(OnCancelButtonClicked);
            addContinentButton.onClick.AddListener(OnAddContinentButtonClicked);
            refreshContinentsButton.onClick.AddListener(OnRefreshContinentsButtonClicked);

            // Setup dropdown
            templateDropdown.onValueChanged.AddListener(OnTemplateChanged);

            // Initialize values
            UpdateSliderLabels();
            SetGenerationState(false);
        }

        private void SetupEventHandlers()
        {
            if (webSocketHandler != null)
            {
                webSocketHandler.OnProgressUpdate += OnProgressUpdate;
                webSocketHandler.OnGenerationComplete += OnGenerationComplete;
                webSocketHandler.OnGenerationError += OnGenerationError;
                webSocketHandler.OnContinentCreated += OnContinentCreated;
                webSocketHandler.OnRegionGenerated += OnRegionGenerated;
            }
        }

        private void CleanupEventHandlers()
        {
            if (webSocketHandler != null)
            {
                webSocketHandler.OnProgressUpdate -= OnProgressUpdate;
                webSocketHandler.OnGenerationComplete -= OnGenerationComplete;
                webSocketHandler.OnGenerationError -= OnGenerationError;
                webSocketHandler.OnContinentCreated -= OnContinentCreated;
                webSocketHandler.OnRegionGenerated -= OnRegionGenerated;
            }
        }

        private async void LoadInitialData()
        {
            if (worldGenService == null) return;

            try
            {
                // Load templates
                var templatesResponse = await worldGenService.GetTemplatesAsync();
                if (templatesResponse.success)
                {
                    availableTemplates = templatesResponse.data;
                    PopulateTemplateDropdown();
                }

                // Load biomes
                var biomesResponse = await worldGenService.GetBiomesAsync();
                if (biomesResponse.success)
                {
                    biomes = biomesResponse.data;
                    PopulateBiomeList();
                }

                // Load continents
                await RefreshContinents();
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error loading initial data: {ex.Message}");
                AddLogEntry($"Error loading data: {ex.Message}", LogLevel.Error);
            }
        }

        #endregion

        #region UI Event Handlers

        private void OnBiomeDiversityChanged(float value)
        {
            biomeDiversityLabel.text = $"Biome Diversity: {value:F1}";
        }

        private void OnSettlementDensityChanged(float value)
        {
            settlementDensityLabel.text = $"Settlement Density: {value:F1}";
        }

        private void OnResourceAbundanceChanged(float value)
        {
            resourceAbundanceLabel.text = $"Resource Abundance: {value:F1}";
        }

        private void OnTemplateChanged(int index)
        {
            if (index >= 0 && index < availableTemplates.Count)
            {
                var template = availableTemplates[index];
                ApplyTemplate(template);
            }
        }

        private async void OnGenerateButtonClicked()
        {
            if (isGenerating) return;

            try
            {
                var config = CreateGenerationConfig();
                await StartWorldGeneration(config);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error starting world generation: {ex.Message}");
                AddLogEntry($"Generation error: {ex.Message}", LogLevel.Error);
            }
        }

        private void OnCancelButtonClicked()
        {
            if (isGenerating)
            {
                CancelGeneration();
            }
        }

        private async void OnAddContinentButtonClicked()
        {
            try
            {
                var continent = new ContinentModel
                {
                    name = $"New Continent {continents.Count + 1}",
                    description = "A newly created continent",
                    boundaryData = new List<Vector2>(),
                    metadata = new Dictionary<string, object>()
                };

                var response = await worldGenService.CreateContinentAsync(continent);
                if (response.success)
                {
                    AddLogEntry($"Created continent: {response.data.name}", LogLevel.Info);
                    await RefreshContinents();
                }
                else
                {
                    AddLogEntry($"Failed to create continent: {string.Join(", ", response.errors)}", LogLevel.Error);
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error creating continent: {ex.Message}");
                AddLogEntry($"Error creating continent: {ex.Message}", LogLevel.Error);
            }
        }

        private async void OnRefreshContinentsButtonClicked()
        {
            await RefreshContinents();
        }

        #endregion

        #region WebSocket Event Handlers

        private void OnProgressUpdate(WorldGenerationProgress progress)
        {
            currentProgress = progress;
            UpdateProgressDisplay();
        }

        private void OnGenerationComplete(WorldGenerationResult result)
        {
            SetGenerationState(false);
            AddLogEntry($"World generation completed: {result.worldName}", LogLevel.Success);
            OnWorldGenerationComplete?.Invoke(result);
        }

        private void OnGenerationError(string error)
        {
            SetGenerationState(false);
            AddLogEntry($"Generation error: {error}", LogLevel.Error);
            OnWorldGenerationError?.Invoke(error);
        }

        private void OnContinentCreated(ContinentModel continent)
        {
            if (!continents.Any(c => c.id == continent.id))
            {
                continents.Add(continent);
                RefreshContinentList();
                AddLogEntry($"Continent created: {continent.name}", LogLevel.Info);
            }
        }

        private void OnRegionGenerated(string continentId, int regionCount)
        {
            AddLogEntry($"Generated {regionCount} regions for continent {continentId}", LogLevel.Info);
        }

        #endregion

        #region World Generation

        private async System.Threading.Tasks.Task StartWorldGeneration(WorldGenerationConfig config)
        {
            SetGenerationState(true);
            AddLogEntry("Starting world generation...", LogLevel.Info);

            var response = await worldGenService.GenerateWorldAsync(config);
            if (!response.success)
            {
                SetGenerationState(false);
                AddLogEntry($"Failed to start generation: {string.Join(", ", response.errors)}", LogLevel.Error);
            }
        }

        private void CancelGeneration()
        {
            // Implementation would depend on backend support for cancellation
            SetGenerationState(false);
            AddLogEntry("Generation cancelled", LogLevel.Warning);
        }

        private WorldGenerationConfig CreateGenerationConfig()
        {
            return new WorldGenerationConfig
            {
                worldName = worldNameInput.text,
                worldDescription = worldDescriptionInput.text,
                biomeGenerationParams = new BiomeGenerationParams
                {
                    diversity = biomeDiversitySlider.value,
                    resourceAbundance = resourceAbundanceSlider.value
                },
                settlementGenerationParams = new SettlementGenerationParams
                {
                    density = settlementDensitySlider.value
                },
                templateId = GetSelectedTemplateId(),
                metadata = new Dictionary<string, object>()
            };
        }

        private string GetSelectedTemplateId()
        {
            var selectedIndex = templateDropdown.value;
            return selectedIndex >= 0 && selectedIndex < availableTemplates.Count 
                ? availableTemplates[selectedIndex].id 
                : null;
        }

        #endregion

        #region UI Updates

        private void SetGenerationState(bool generating)
        {
            isGenerating = generating;
            generateButton.interactable = !generating;
            cancelButton.interactable = generating;
            
            if (!generating)
            {
                progressBar.SetProgress(0f);
                statusText.text = "Ready";
                progressText.text = "";
            }
        }

        private void UpdateProgressDisplay()
        {
            if (currentProgress == null) return;

            progressBar.SetProgress(currentProgress.overallProgress);
            statusText.text = currentProgress.currentStage;
            progressText.text = $"{currentProgress.overallProgress:P0} - {currentProgress.currentStage}";

            if (!string.IsNullOrEmpty(currentProgress.details))
            {
                AddLogEntry(currentProgress.details, LogLevel.Info);
            }
        }

        private void UpdateSliderLabels()
        {
            OnBiomeDiversityChanged(biomeDiversitySlider.value);
            OnSettlementDensityChanged(settlementDensitySlider.value);
            OnResourceAbundanceChanged(resourceAbundanceSlider.value);
        }

        private void PopulateTemplateDropdown()
        {
            templateDropdown.ClearOptions();
            var options = new List<string> { "Custom" };
            options.AddRange(availableTemplates.Select(t => t.name));
            templateDropdown.AddOptions(options);
        }

        private void ApplyTemplate(WorldTemplate template)
        {
            worldNameInput.text = template.name;
            worldDescriptionInput.text = template.description;
            
            // Apply template parameters if available
            if (template.parameters != null)
            {
                if (template.parameters.ContainsKey("biomeDiversity"))
                {
                    biomeDiversitySlider.value = Convert.ToSingle(template.parameters["biomeDiversity"]);
                }
                if (template.parameters.ContainsKey("settlementDensity"))
                {
                    settlementDensitySlider.value = Convert.ToSingle(template.parameters["settlementDensity"]);
                }
                if (template.parameters.ContainsKey("resourceAbundance"))
                {
                    resourceAbundanceSlider.value = Convert.ToSingle(template.parameters["resourceAbundance"]);
                }
            }

            UpdateSliderLabels();
        }

        #endregion

        #region Data Management

        private async System.Threading.Tasks.Task RefreshContinents()
        {
            try
            {
                var response = await worldGenService.GetContinentsAsync();
                if (response.success)
                {
                    continents = response.data;
                    RefreshContinentList();
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error refreshing continents: {ex.Message}");
                AddLogEntry($"Error refreshing continents: {ex.Message}", LogLevel.Error);
            }
        }

        private void RefreshContinentList()
        {
            // Clear existing items
            foreach (Transform child in continentListParent)
            {
                Destroy(child.gameObject);
            }

            // Create new items
            foreach (var continent in continents)
            {
                var item = Instantiate(continentItemPrefab, continentListParent);
                var continentItem = item.GetComponent<ContinentListItem>();
                if (continentItem != null)
                {
                    continentItem.Initialize(continent, OnContinentSelected, OnContinentDeleted);
                }
            }
        }

        private void PopulateBiomeList()
        {
            // Clear existing items
            foreach (Transform child in biomeListParent)
            {
                Destroy(child.gameObject);
            }

            // Create new items
            foreach (var biome in biomes)
            {
                var item = Instantiate(biomeItemPrefab, biomeListParent);
                var biomeItem = item.GetComponent<BiomeListItem>();
                if (biomeItem != null)
                {
                    biomeItem.Initialize(biome);
                }
            }
        }

        #endregion

        #region Continent Management

        private void OnContinentSelected(ContinentModel continent)
        {
            // Handle continent selection - could open detail panel
            Debug.Log($"Selected continent: {continent.name}");
        }

        private async void OnContinentDeleted(ContinentModel continent)
        {
            try
            {
                var response = await worldGenService.DeleteContinentAsync(continent.id);
                if (response.success)
                {
                    AddLogEntry($"Deleted continent: {continent.name}", LogLevel.Info);
                    await RefreshContinents();
                }
                else
                {
                    AddLogEntry($"Failed to delete continent: {string.Join(", ", response.errors)}", LogLevel.Error);
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error deleting continent: {ex.Message}");
                AddLogEntry($"Error deleting continent: {ex.Message}", LogLevel.Error);
            }
        }

        #endregion

        #region Logging

        private enum LogLevel
        {
            Info,
            Warning,
            Error,
            Success
        }

        private void AddLogEntry(string message, LogLevel level)
        {
            var timestamp = DateTime.Now.ToString("HH:mm:ss");
            var levelText = level.ToString().ToUpper();
            var colorCode = GetLogColor(level);
            
            var logEntry = $"<color={colorCode}>[{timestamp}] {levelText}: {message}</color>\n";
            logText.text += logEntry;

            // Auto-scroll to bottom
            Canvas.ForceUpdateCanvases();
            logScrollRect.verticalNormalizedPosition = 0f;
        }

        private string GetLogColor(LogLevel level)
        {
            return level switch
            {
                LogLevel.Info => "#FFFFFF",
                LogLevel.Warning => "#FFFF00",
                LogLevel.Error => "#FF0000",
                LogLevel.Success => "#00FF00",
                _ => "#FFFFFF"
            };
        }

        #endregion

        #region Public Interface

        /// <summary>
        /// Show the world generation panel
        /// </summary>
        public void Show()
        {
            gameObject.SetActive(true);
        }

        /// <summary>
        /// Hide the world generation panel
        /// </summary>
        public void Hide()
        {
            gameObject.SetActive(false);
        }

        /// <summary>
        /// Get current generation status
        /// </summary>
        public bool IsGenerating => isGenerating;

        /// <summary>
        /// Get current progress
        /// </summary>
        public WorldGenerationProgress CurrentProgress => currentProgress;

        #endregion
    }

    /// <summary>
    /// Simple progress bar component
    /// </summary>
    [System.Serializable]
    public class ProgressBar
    {
        [SerializeField] private Slider slider;
        [SerializeField] private Image fillImage;
        [SerializeField] private TMP_Text percentageText;

        public void SetProgress(float progress)
        {
            progress = Mathf.Clamp01(progress);
            
            if (slider != null)
                slider.value = progress;
            
            if (percentageText != null)
                percentageText.text = $"{progress:P0}";
        }
    }
} 