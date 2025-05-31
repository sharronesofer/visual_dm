using System.Collections.Generic;
using System.Collections;
using System;
using UnityEngine.UI;
using UnityEngine;
using VDM.Systems.Chaos.Models;
using VDM.Systems.Chaos.Services;
using TMPro;

namespace VDM.Systems.Chaos.Ui.Admin
{
    /// <summary>
    /// Admin configuration panel for chaos system parameters and thresholds
    /// </summary>
    public class ChaosConfigPanel : MonoBehaviour
    {
        [Header("Core References")]
        [SerializeField] private ChaosService chaosService;

        [Header("Main Panel")]
        [SerializeField] private GameObject configPanel;
        [SerializeField] private Button closeButton;
        [SerializeField] private Button saveButton;
        [SerializeField] private Button resetButton;
        [SerializeField] private Button applyButton;

        [Header("Global Settings")]
        [SerializeField] private Toggle enabledToggle;
        [SerializeField] private Slider globalMultiplierSlider;
        [SerializeField] private TextMeshProUGUI globalMultiplierText;
        [SerializeField] private TextMeshProUGUI statusText;

        [Header("System Weights")]
        [SerializeField] private Transform systemWeightsContainer;
        [SerializeField] private GameObject weightSliderPrefab;

        [Header("Thresholds")]
        [SerializeField] private Transform thresholdsContainer;
        [SerializeField] private GameObject thresholdSliderPrefab;

        [Header("Mitigation Factors")]
        [SerializeField] private Transform mitigationContainer;
        [SerializeField] private GameObject mitigationSliderPrefab;

        [Header("Advanced Settings")]
        [SerializeField] private GameObject advancedPanel;
        [SerializeField] private Button advancedToggleButton;
        [SerializeField] private TMP_InputField customConfigInput;
        [SerializeField] private Button importConfigButton;
        [SerializeField] private Button exportConfigButton;

        [Header("Testing Controls")]
        [SerializeField] private GameObject testingPanel;
        [SerializeField] private TMP_Dropdown eventTypeDropdown;
        [SerializeField] private TMP_Dropdown regionDropdown;
        [SerializeField] private Slider intensitySlider;
        [SerializeField] private TextMeshProUGUI intensityText;
        [SerializeField] private Button triggerEventButton;

        [Header("Validation")]
        [SerializeField] private Image validationIndicator;
        [SerializeField] private TextMeshProUGUI validationText;
        [SerializeField] private Color validColor = Color.green;
        [SerializeField] private Color invalidColor = Color.red;
        [SerializeField] private Color warningColor = Color.yellow;

        private ChaosConfigurationDTO currentConfig;
        private ChaosConfigurationDTO originalConfig;
        private Dictionary<string, Slider> systemWeightSliders = new Dictionary<string, Slider>();
        private Dictionary<string, Slider> thresholdSliders = new Dictionary<string, Slider>();
        private Dictionary<string, Slider> mitigationSliders = new Dictionary<string, Slider>();
        private bool isLoading = false;
        private bool hasUnsavedChanges = false;
        private bool showAdvanced = false;

        // Standard system names (these would typically come from configuration)
        private readonly string[] defaultSystems = 
        {
            "Economic", "Political", "Military", "Social", "Environmental", 
            "Diplomatic", "Cultural", "Religious", "Territorial"
        };

        // Standard threshold names
        private readonly string[] defaultThresholds = 
        {
            "Warning", "Critical", "Emergency", "Catastrophic", "GlobalChaos"
        };

        // Standard mitigation factors
        private readonly string[] defaultMitigationFactors = 
        {
            "Diplomacy", "Infrastructure", "Leadership", "QuestCompletion", "PositiveEvents"
        };

        // Event types for testing
        private readonly string[] eventTypes = 
        {
            "Political Upheaval", "Natural Disaster", "Economic Collapse", 
            "War Outbreak", "Resource Scarcity", "Faction Betrayal", "Character Revelation"
        };

        private void Start()
        {
            InitializePanel();
        }

        private void OnDestroy()
        {
            if (chaosService != null)
            {
                chaosService.OnConfigurationUpdated -= HandleConfigurationUpdate;
            }
        }

        /// <summary>
        /// Initialize the configuration panel
        /// </summary>
        private void InitializePanel()
        {
            if (chaosService == null)
            {
                chaosService = FindObjectOfType<ChaosService>();
                if (chaosService == null)
                {
                    Debug.LogError("ChaosConfigPanel: ChaosService not found");
                    return;
                }
            }

            // Hide panel initially
            if (configPanel != null)
                configPanel.SetActive(false);

            // Setup button listeners
            SetupButtons();

            // Subscribe to chaos service events
            chaosService.OnConfigurationUpdated += HandleConfigurationUpdate;

            // Initialize UI components
            InitializeDropdowns();
            InitializeSliders();

            Debug.Log("ChaosConfigPanel initialized successfully");
        }

        /// <summary>
        /// Setup button event listeners
        /// </summary>
        private void SetupButtons()
        {
            if (closeButton != null)
                closeButton.onClick.AddListener(ClosePanel);

            if (saveButton != null)
                saveButton.onClick.AddListener(SaveConfiguration);

            if (resetButton != null)
                resetButton.onClick.AddListener(ResetToDefaults);

            if (applyButton != null)
                applyButton.onClick.AddListener(ApplyConfiguration);

            if (advancedToggleButton != null)
                advancedToggleButton.onClick.AddListener(ToggleAdvancedPanel);

            if (importConfigButton != null)
                importConfigButton.onClick.AddListener(ImportConfiguration);

            if (exportConfigButton != null)
                exportConfigButton.onClick.AddListener(ExportConfiguration);

            if (triggerEventButton != null)
                triggerEventButton.onClick.AddListener(TriggerTestEvent);

            // Setup value change listeners
            if (enabledToggle != null)
                enabledToggle.onValueChanged.AddListener(OnEnabledChanged);

            if (globalMultiplierSlider != null)
                globalMultiplierSlider.onValueChanged.AddListener(OnGlobalMultiplierChanged);

            if (intensitySlider != null)
                intensitySlider.onValueChanged.AddListener(OnIntensityChanged);
        }

        /// <summary>
        /// Initialize dropdown menus
        /// </summary>
        private void InitializeDropdowns()
        {
            // Initialize event type dropdown
            if (eventTypeDropdown != null)
            {
                eventTypeDropdown.options.Clear();
                foreach (var eventType in eventTypes)
                {
                    eventTypeDropdown.options.Add(new TMP_Dropdown.OptionData(eventType));
                }
                eventTypeDropdown.value = 0;
            }

            // Initialize region dropdown (would be populated from actual region data)
            if (regionDropdown != null)
            {
                regionDropdown.options.Clear();
                regionDropdown.options.Add(new TMP_Dropdown.OptionData("Global"));
                regionDropdown.options.Add(new TMP_Dropdown.OptionData("Region_01"));
                regionDropdown.options.Add(new TMP_Dropdown.OptionData("Region_02"));
                regionDropdown.options.Add(new TMP_Dropdown.OptionData("Region_03"));
                regionDropdown.value = 0;
            }
        }

        /// <summary>
        /// Initialize slider controls
        /// </summary>
        private void InitializeSliders()
        {
            CreateSystemWeightSliders();
            CreateThresholdSliders();
            CreateMitigationSliders();
        }

        /// <summary>
        /// Create system weight sliders
        /// </summary>
        private void CreateSystemWeightSliders()
        {
            if (systemWeightsContainer == null || weightSliderPrefab == null) return;

            foreach (var system in defaultSystems)
            {
                var sliderObject = Instantiate(weightSliderPrefab, systemWeightsContainer);
                var slider = sliderObject.GetComponentInChildren<Slider>();
                var label = sliderObject.GetComponentInChildren<TextMeshProUGUI>();

                if (slider != null && label != null)
                {
                    slider.minValue = 0f;
                    slider.maxValue = 2f;
                    slider.value = 1f;
                    label.text = system;

                    systemWeightSliders[system] = slider;
                    slider.onValueChanged.AddListener(value => OnSystemWeightChanged(system, value));
                }
            }
        }

        /// <summary>
        /// Create threshold sliders
        /// </summary>
        private void CreateThresholdSliders()
        {
            if (thresholdsContainer == null || thresholdSliderPrefab == null) return;

            foreach (var threshold in defaultThresholds)
            {
                var sliderObject = Instantiate(thresholdSliderPrefab, thresholdsContainer);
                var slider = sliderObject.GetComponentInChildren<Slider>();
                var label = sliderObject.GetComponentInChildren<TextMeshProUGUI>();

                if (slider != null && label != null)
                {
                    slider.minValue = 0f;
                    slider.maxValue = 100f;
                    slider.value = GetDefaultThreshold(threshold);
                    label.text = threshold;

                    thresholdSliders[threshold] = slider;
                    slider.onValueChanged.AddListener(value => OnThresholdChanged(threshold, value));
                }
            }
        }

        /// <summary>
        /// Create mitigation factor sliders
        /// </summary>
        private void CreateMitigationSliders()
        {
            if (mitigationContainer == null || mitigationSliderPrefab == null) return;

            foreach (var factor in defaultMitigationFactors)
            {
                var sliderObject = Instantiate(mitigationSliderPrefab, mitigationContainer);
                var slider = sliderObject.GetComponentInChildren<Slider>();
                var label = sliderObject.GetComponentInChildren<TextMeshProUGUI>();

                if (slider != null && label != null)
                {
                    slider.minValue = 0f;
                    slider.maxValue = 2f;
                    slider.value = 1f;
                    label.text = factor;

                    mitigationSliders[factor] = slider;
                    slider.onValueChanged.AddListener(value => OnMitigationFactorChanged(factor, value));
                }
            }
        }

        /// <summary>
        /// Load current configuration from chaos service
        /// </summary>
        public async void LoadConfiguration()
        {
            isLoading = true;
            UpdateStatus("Loading configuration...");

            try
            {
                var config = await chaosService.GetConfigurationAsync();
                if (config != null)
                {
                    currentConfig = config;
                    originalConfig = JsonUtility.FromJson<ChaosConfigurationDTO>(JsonUtility.ToJson(config));
                    UpdateUIFromConfig(config);
                    UpdateStatus("Configuration loaded successfully");
                    hasUnsavedChanges = false;
                }
                else
                {
                    UpdateStatus("Failed to load configuration", true);
                    CreateDefaultConfiguration();
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"ChaosConfigPanel: Error loading configuration: {ex.Message}");
                UpdateStatus($"Error: {ex.Message}", true);
                CreateDefaultConfiguration();
            }
            finally
            {
                isLoading = false;
            }
        }

        /// <summary>
        /// Update UI elements from configuration
        /// </summary>
        private void UpdateUIFromConfig(ChaosConfigurationDTO config)
        {
            if (enabledToggle != null)
                enabledToggle.isOn = config.IsEnabled;

            if (globalMultiplierSlider != null)
                globalMultiplierSlider.value = config.GlobalMultiplier;

            UpdateGlobalMultiplierText(config.GlobalMultiplier);

            // Update system weights
            foreach (var weight in config.SystemWeights)
            {
                if (systemWeightSliders.ContainsKey(weight.Key))
                {
                    systemWeightSliders[weight.Key].value = weight.Value;
                }
            }

            // Update thresholds
            foreach (var threshold in config.ThresholdSettings)
            {
                if (thresholdSliders.ContainsKey(threshold.Key))
                {
                    thresholdSliders[threshold.Key].value = threshold.Value;
                }
            }

            // Update mitigation factors
            foreach (var mitigation in config.MitigationFactors)
            {
                if (mitigationSliders.ContainsKey(mitigation.Key))
                {
                    mitigationSliders[mitigation.Key].value = mitigation.Value;
                }
            }

            ValidateConfiguration();
        }

        /// <summary>
        /// Create default configuration
        /// </summary>
        private void CreateDefaultConfiguration()
        {
            currentConfig = new ChaosConfigurationDTO
            {
                Id = Guid.NewGuid().ToString(),
                IsEnabled = true,
                GlobalMultiplier = 1.0f,
                Status = ChaosConfigurationStatus.Active,
                LastModified = DateTime.Now,
                LastModifiedBy = "Admin"
            };

            // Initialize default system weights
            foreach (var system in defaultSystems)
            {
                currentConfig.SystemWeights[system] = 1.0f;
            }

            // Initialize default thresholds
            foreach (var threshold in defaultThresholds)
            {
                currentConfig.ThresholdSettings[threshold] = GetDefaultThreshold(threshold);
            }

            // Initialize default mitigation factors
            foreach (var factor in defaultMitigationFactors)
            {
                currentConfig.MitigationFactors[factor] = 1.0f;
            }

            originalConfig = JsonUtility.FromJson<ChaosConfigurationDTO>(JsonUtility.ToJson(currentConfig));
            UpdateUIFromConfig(currentConfig);
        }

        /// <summary>
        /// Get default threshold value
        /// </summary>
        private float GetDefaultThreshold(string thresholdName)
        {
            return thresholdName switch
            {
                "Warning" => 25f,
                "Critical" => 50f,
                "Emergency" => 75f,
                "Catastrophic" => 90f,
                "GlobalChaos" => 95f,
                _ => 50f
            };
        }

        /// <summary>
        /// Save configuration to chaos service
        /// </summary>
        public async void SaveConfiguration()
        {
            if (currentConfig == null)
            {
                UpdateStatus("No configuration to save", true);
                return;
            }

            UpdateStatus("Saving configuration...");

            try
            {
                currentConfig.LastModified = DateTime.Now;
                currentConfig.LastModifiedBy = "Admin"; // Should use actual user info

                var success = await chaosService.UpdateConfigurationAsync(currentConfig);
                if (success)
                {
                    originalConfig = JsonUtility.FromJson<ChaosConfigurationDTO>(JsonUtility.ToJson(currentConfig));
                    hasUnsavedChanges = false;
                    UpdateStatus("Configuration saved successfully");
                    Debug.Log("ChaosConfigPanel: Configuration saved successfully");
                }
                else
                {
                    UpdateStatus("Failed to save configuration", true);
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"ChaosConfigPanel: Error saving configuration: {ex.Message}");
                UpdateStatus($"Save error: {ex.Message}", true);
            }
        }

        /// <summary>
        /// Apply configuration without saving
        /// </summary>
        public async void ApplyConfiguration()
        {
            if (currentConfig == null)
            {
                UpdateStatus("No configuration to apply", true);
                return;
            }

            UpdateStatus("Applying configuration...");

            try
            {
                currentConfig.Status = ChaosConfigurationStatus.Testing;
                var success = await chaosService.UpdateConfigurationAsync(currentConfig);
                if (success)
                {
                    UpdateStatus("Configuration applied for testing");
                    Debug.Log("ChaosConfigPanel: Configuration applied for testing");
                }
                else
                {
                    UpdateStatus("Failed to apply configuration", true);
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"ChaosConfigPanel: Error applying configuration: {ex.Message}");
                UpdateStatus($"Apply error: {ex.Message}", true);
            }
        }

        /// <summary>
        /// Reset configuration to defaults
        /// </summary>
        public void ResetToDefaults()
        {
            CreateDefaultConfiguration();
            hasUnsavedChanges = true;
            UpdateStatus("Configuration reset to defaults");
        }

        /// <summary>
        /// Validate current configuration
        /// </summary>
        private void ValidateConfiguration()
        {
            if (currentConfig == null) return;

            var issues = new List<string>();

            // Validate thresholds are in ascending order
            var thresholds = currentConfig.ThresholdSettings.Values.OrderBy(v => v).ToArray();
            for (int i = 1; i < thresholds.Length; i++)
            {
                if (thresholds[i] <= thresholds[i - 1])
                {
                    issues.Add("Thresholds must be in ascending order");
                    break;
                }
            }

            // Validate global multiplier
            if (currentConfig.GlobalMultiplier < 0.1f || currentConfig.GlobalMultiplier > 5.0f)
            {
                issues.Add("Global multiplier should be between 0.1 and 5.0");
            }

            // Validate system weights
            var totalWeight = currentConfig.SystemWeights.Values.Sum();
            if (totalWeight < 0.1f)
            {
                issues.Add("Total system weights too low");
            }

            // Update validation display
            UpdateValidationDisplay(issues);
        }

        /// <summary>
        /// Update validation display
        /// </summary>
        private void UpdateValidationDisplay(List<string> issues)
        {
            if (validationIndicator != null && validationText != null)
            {
                if (issues.Count == 0)
                {
                    validationIndicator.color = validColor;
                    validationText.text = "Configuration valid";
                }
                else
                {
                    validationIndicator.color = issues.Any(i => i.Contains("must") || i.Contains("should")) ? invalidColor : warningColor;
                    validationText.text = string.Join("\n", issues);
                }
            }
        }

        // Event Handlers

        private void OnEnabledChanged(bool enabled)
        {
            if (!isLoading && currentConfig != null)
            {
                currentConfig.IsEnabled = enabled;
                hasUnsavedChanges = true;
                ValidateConfiguration();
            }
        }

        private void OnGlobalMultiplierChanged(float value)
        {
            if (!isLoading && currentConfig != null)
            {
                currentConfig.GlobalMultiplier = value;
                UpdateGlobalMultiplierText(value);
                hasUnsavedChanges = true;
                ValidateConfiguration();
            }
        }

        private void OnSystemWeightChanged(string systemName, float value)
        {
            if (!isLoading && currentConfig != null)
            {
                currentConfig.SystemWeights[systemName] = value;
                hasUnsavedChanges = true;
                ValidateConfiguration();
            }
        }

        private void OnThresholdChanged(string thresholdName, float value)
        {
            if (!isLoading && currentConfig != null)
            {
                currentConfig.ThresholdSettings[thresholdName] = value;
                hasUnsavedChanges = true;
                ValidateConfiguration();
            }
        }

        private void OnMitigationFactorChanged(string factorName, float value)
        {
            if (!isLoading && currentConfig != null)
            {
                currentConfig.MitigationFactors[factorName] = value;
                hasUnsavedChanges = true;
                ValidateConfiguration();
            }
        }

        private void OnIntensityChanged(float value)
        {
            if (intensityText != null)
                intensityText.text = $"Intensity: {value:F1}";
        }

        private void HandleConfigurationUpdate(ChaosConfigurationDTO config)
        {
            if (!isLoading)
            {
                currentConfig = config;
                UpdateUIFromConfig(config);
                UpdateStatus("Configuration updated from server");
            }
        }

        // UI Actions

        private void ClosePanel()
        {
            if (hasUnsavedChanges)
            {
                // In a real implementation, you'd show a confirmation dialog
                Debug.LogWarning("ChaosConfigPanel: Closing with unsaved changes");
            }

            if (configPanel != null)
                configPanel.SetActive(false);
        }

        private void ToggleAdvancedPanel()
        {
            showAdvanced = !showAdvanced;
            if (advancedPanel != null)
                advancedPanel.SetActive(showAdvanced);
        }

        private void ImportConfiguration()
        {
            if (!string.IsNullOrEmpty(customConfigInput?.text))
            {
                try
                {
                    var importedConfig = JsonUtility.FromJson<ChaosConfigurationDTO>(customConfigInput.text);
                    currentConfig = importedConfig;
                    UpdateUIFromConfig(currentConfig);
                    hasUnsavedChanges = true;
                    UpdateStatus("Configuration imported successfully");
                }
                catch (Exception ex)
                {
                    UpdateStatus($"Import error: {ex.Message}", true);
                }
            }
        }

        private void ExportConfiguration()
        {
            if (currentConfig != null && customConfigInput != null)
            {
                customConfigInput.text = JsonUtility.ToJson(currentConfig, true);
                UpdateStatus("Configuration exported to text field");
            }
        }

        private async void TriggerTestEvent()
        {
            if (eventTypeDropdown == null || regionDropdown == null || intensitySlider == null)
                return;

            var eventType = eventTypes[eventTypeDropdown.value];
            var regionId = regionDropdown.options[regionDropdown.value].text;
            var intensity = intensitySlider.value;

            UpdateStatus("Triggering test event...");

            try
            {
                var success = await chaosService.TriggerEventAsync(eventType, regionId, intensity);
                if (success)
                {
                    UpdateStatus($"Test event triggered: {eventType}");
                }
                else
                {
                    UpdateStatus("Failed to trigger test event", true);
                }
            }
            catch (Exception ex)
            {
                UpdateStatus($"Test event error: {ex.Message}", true);
            }
        }

        // Utility Methods

        private void UpdateStatus(string message, bool isError = false)
        {
            if (statusText != null)
            {
                statusText.text = message;
                statusText.color = isError ? invalidColor : validColor;
            }
            Debug.Log($"ChaosConfigPanel: {message}");
        }

        private void UpdateGlobalMultiplierText(float value)
        {
            if (globalMultiplierText != null)
                globalMultiplierText.text = $"Global Multiplier: {value:F2}";
        }

        // Public Properties

        public bool HasUnsavedChanges => hasUnsavedChanges;
        public ChaosConfigurationDTO CurrentConfig => currentConfig;
        public bool IsVisible => configPanel?.activeInHierarchy ?? false;
    }
} 