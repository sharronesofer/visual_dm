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
    /// Admin-only chaos monitoring dashboard for comprehensive system oversight
    /// </summary>
    public class ChaosMonitoringPanel : MonoBehaviour
    {
        [Header("Core References")]
        [SerializeField] private ChaosService chaosService;
        [SerializeField] private PressureVisualization pressureVisualization;
        [SerializeField] private ChaosConfigPanel configPanel;

        [Header("Main UI Elements")]
        [SerializeField] private GameObject adminPanel;
        [SerializeField] private Button toggleButton;
        [SerializeField] private Button refreshButton;
        [SerializeField] private Button configButton;
        [SerializeField] private Button emergencyStopButton;

        [Header("Status Display")]
        [SerializeField] private TextMeshProUGUI connectionStatusText;
        [SerializeField] private TextMeshProUGUI globalChaosLevelText;
        [SerializeField] private TextMeshProUGUI systemHealthText;
        [SerializeField] private Slider globalChaosSlider;
        [SerializeField] private Image healthStatusIndicator;

        [Header("Metrics Display")]
        [SerializeField] private TextMeshProUGUI totalEventsText;
        [SerializeField] private TextMeshProUGUI activeEventsText;
        [SerializeField] private TextMeshProUGUI mitigationEffectivenessText;
        [SerializeField] private TextMeshProUGUI lastUpdateText;

        [Header("Event Log")]
        [SerializeField] private ScrollRect eventLogScrollRect;
        [SerializeField] private Transform eventLogContent;
        [SerializeField] private GameObject eventLogEntryPrefab;
        [SerializeField] private int maxLogEntries = 100;

        [Header("Alert System")]
        [SerializeField] private Transform alertContainer;
        [SerializeField] private GameObject alertPrefab;
        [SerializeField] private Button clearAlertsButton;

        [Header("Regional Display")]
        [SerializeField] private Transform regionContainer;
        [SerializeField] private GameObject regionDisplayPrefab;

        [Header("System Pressure Display")]
        [SerializeField] private Transform systemPressureContainer;
        [SerializeField] private GameObject pressureBarPrefab;

        [Header("Color Coding")]
        [SerializeField] private Color healthyColor = Color.green;
        [SerializeField] private Color warningColor = Color.yellow;
        [SerializeField] private Color errorColor = Color.orange;
        [SerializeField] private Color criticalColor = Color.red;
        [SerializeField] private Color offlineColor = Color.gray;

        private bool isVisible = false;
        private bool isInitialized = false;
        private ChaosMetricsDTO currentMetrics;
        private List<ChaosEventDTO> recentEvents = new List<ChaosEventDTO>();
        private List<PressureSourceDTO> currentPressures = new List<PressureSourceDTO>();
        private Dictionary<string, GameObject> regionDisplays = new Dictionary<string, GameObject>();
        private Dictionary<string, GameObject> pressureBars = new Dictionary<string, GameObject>();
        private Dictionary<string, GameObject> alertDisplays = new Dictionary<string, GameObject>();

        // Events
        public event Action<bool> OnPanelToggled;
        public event Action OnRefreshRequested;
        public event Action OnEmergencyStop;

        private void Start()
        {
            InitializePanel();
        }

        private void OnDestroy()
        {
            if (chaosService != null)
            {
                UnsubscribeFromChaosService();
            }
        }

        /// <summary>
        /// Initialize the monitoring panel
        /// </summary>
        private void InitializePanel()
        {
            if (chaosService == null)
            {
                chaosService = FindObjectOfType<ChaosService>();
                if (chaosService == null)
                {
                    Debug.LogError("ChaosMonitoringPanel: ChaosService not found");
                    return;
                }
            }

            // Hide panel initially
            if (adminPanel != null)
                adminPanel.SetActive(false);

            // Setup button listeners
            SetupButtons();

            // Subscribe to chaos service events
            SubscribeToChaosService();

            // Initialize UI components
            InitializeUI();

            isInitialized = true;
            Debug.Log("ChaosMonitoringPanel initialized successfully");
        }

        /// <summary>
        /// Setup button event listeners
        /// </summary>
        private void SetupButtons()
        {
            if (toggleButton != null)
                toggleButton.onClick.AddListener(TogglePanel);

            if (refreshButton != null)
                refreshButton.onClick.AddListener(RefreshData);

            if (configButton != null)
                configButton.onClick.AddListener(OpenConfigPanel);

            if (emergencyStopButton != null)
                emergencyStopButton.onClick.AddListener(TriggerEmergencyStop);

            if (clearAlertsButton != null)
                clearAlertsButton.onClick.AddListener(ClearAllAlerts);
        }

        /// <summary>
        /// Subscribe to chaos service events
        /// </summary>
        private void SubscribeToChaosService()
        {
            chaosService.OnMetricsUpdated += HandleMetricsUpdate;
            chaosService.OnChaosEventTriggered += HandleEventTriggered;
            chaosService.OnPressureUpdated += HandlePressureUpdate;
            chaosService.OnAlertReceived += HandleAlertReceived;
            chaosService.OnConnectionStatusChanged += HandleConnectionStatusChanged;
            chaosService.OnError += HandleError;
        }

        /// <summary>
        /// Unsubscribe from chaos service events
        /// </summary>
        private void UnsubscribeFromChaosService()
        {
            chaosService.OnMetricsUpdated -= HandleMetricsUpdate;
            chaosService.OnChaosEventTriggered -= HandleEventTriggered;
            chaosService.OnPressureUpdated -= HandlePressureUpdate;
            chaosService.OnAlertReceived -= HandleAlertReceived;
            chaosService.OnConnectionStatusChanged -= HandleConnectionStatusChanged;
            chaosService.OnError -= HandleError;
        }

        /// <summary>
        /// Initialize UI elements
        /// </summary>
        private void InitializeUI()
        {
            UpdateConnectionStatus(chaosService.IsConnected);
            UpdateGlobalChaosLevel(0.0f);
            UpdateSystemHealth(SystemStatus.Offline);
            ClearEventLog();
            ClearAlerts();
        }

        /// <summary>
        /// Toggle panel visibility
        /// </summary>
        public void TogglePanel()
        {
            isVisible = !isVisible;
            if (adminPanel != null)
                adminPanel.SetActive(isVisible);

            OnPanelToggled?.Invoke(isVisible);

            if (isVisible)
            {
                RefreshData();
                Debug.Log("ChaosMonitoringPanel: Panel opened");
            }
            else
            {
                Debug.Log("ChaosMonitoringPanel: Panel closed");
            }
        }

        /// <summary>
        /// Refresh all chaos data
        /// </summary>
        public async void RefreshData()
        {
            if (!isInitialized || !chaosService.IsInitialized)
                return;

            OnRefreshRequested?.Invoke();

            try
            {
                // Get current metrics
                var metrics = await chaosService.GetMetricsAsync();
                if (metrics != null)
                {
                    HandleMetricsUpdate(metrics);
                }

                // Get recent events
                var events = await chaosService.GetEventsAsync(50);
                if (events != null)
                {
                    UpdateEventLog(events);
                }

                // Get pressure sources
                var pressures = await chaosService.GetPressureSourcesAsync();
                if (pressures != null)
                {
                    UpdatePressureDisplay(pressures);
                }

                UpdateLastUpdateTime();
                Debug.Log("ChaosMonitoringPanel: Data refreshed successfully");
            }
            catch (Exception ex)
            {
                Debug.LogError($"ChaosMonitoringPanel: Error refreshing data: {ex.Message}");
            }
        }

        /// <summary>
        /// Open the configuration panel
        /// </summary>
        private void OpenConfigPanel()
        {
            if (configPanel != null)
            {
                configPanel.gameObject.SetActive(true);
                configPanel.LoadConfiguration();
            }
            else
            {
                Debug.LogWarning("ChaosMonitoringPanel: Config panel not assigned");
            }
        }

        /// <summary>
        /// Trigger emergency stop
        /// </summary>
        private void TriggerEmergencyStop()
        {
            OnEmergencyStop?.Invoke();
            Debug.LogWarning("ChaosMonitoringPanel: Emergency stop triggered");
            // Here you would implement emergency stop logic
        }

        /// <summary>
        /// Clear all alerts
        /// </summary>
        private void ClearAllAlerts()
        {
            foreach (var alert in alertDisplays.Values)
            {
                if (alert != null)
                    Destroy(alert);
            }
            alertDisplays.Clear();
        }

        // Event Handlers

        private void HandleMetricsUpdate(ChaosMetricsDTO metrics)
        {
            currentMetrics = metrics;
            UpdateMetricsDisplay(metrics);
        }

        private void HandleEventTriggered(ChaosEventDTO chaosEvent)
        {
            recentEvents.Insert(0, chaosEvent);
            if (recentEvents.Count > maxLogEntries)
                recentEvents.RemoveAt(recentEvents.Count - 1);

            AddEventLogEntry(chaosEvent);
        }

        private void HandlePressureUpdate(PressureSourceDTO pressure)
        {
            var existingIndex = currentPressures.FindIndex(p => p.Id == pressure.Id);
            if (existingIndex >= 0)
                currentPressures[existingIndex] = pressure;
            else
                currentPressures.Add(pressure);

            UpdateSinglePressureBar(pressure);
        }

        private void HandleAlertReceived(ChaosAlert alert)
        {
            AddAlertDisplay(alert);
        }

        private void HandleConnectionStatusChanged(bool connected)
        {
            UpdateConnectionStatus(connected);
        }

        private void HandleError(string error)
        {
            Debug.LogError($"ChaosMonitoringPanel: Chaos service error: {error}");
            // Could add error display to UI here
        }

        // UI Update Methods

        private void UpdateConnectionStatus(bool connected)
        {
            if (connectionStatusText != null)
            {
                connectionStatusText.text = connected ? "Connected" : "Disconnected";
                connectionStatusText.color = connected ? healthyColor : errorColor;
            }
        }

        private void UpdateGlobalChaosLevel(float level)
        {
            if (globalChaosLevelText != null)
                globalChaosLevelText.text = $"Global Chaos: {level:F1}%";

            if (globalChaosSlider != null)
                globalChaosSlider.value = level / 100f;
        }

        private void UpdateSystemHealth(SystemStatus status)
        {
            if (systemHealthText != null)
                systemHealthText.text = $"System: {status}";

            if (healthStatusIndicator != null)
            {
                healthStatusIndicator.color = status switch
                {
                    SystemStatus.Healthy => healthyColor,
                    SystemStatus.Warning => warningColor,
                    SystemStatus.Error => errorColor,
                    SystemStatus.Critical => criticalColor,
                    SystemStatus.Offline => offlineColor,
                    _ => offlineColor
                };
            }
        }

        private void UpdateMetricsDisplay(ChaosMetricsDTO metrics)
        {
            UpdateGlobalChaosLevel(metrics.GlobalChaosLevel);
            UpdateSystemHealth(metrics.SystemHealth.OverallStatus);

            if (totalEventsText != null)
                totalEventsText.text = $"Total Events Today: {metrics.TotalEventsToday}";

            if (activeEventsText != null)
                activeEventsText.text = $"Active Events: {metrics.ActiveEvents}";

            if (mitigationEffectivenessText != null)
                mitigationEffectivenessText.text = $"Mitigation Effectiveness: {metrics.AverageMitigationEffectiveness:F1}%";

            UpdateRegionalDisplay(metrics.RegionalChaosLevels);
            UpdateSystemPressureDisplay(metrics.SystemPressures);
        }

        private void UpdateRegionalDisplay(Dictionary<string, float> regionalLevels)
        {
            if (regionContainer == null || regionDisplayPrefab == null) return;

            foreach (var region in regionalLevels)
            {
                if (!regionDisplays.ContainsKey(region.Key))
                {
                    var display = Instantiate(regionDisplayPrefab, regionContainer);
                    regionDisplays[region.Key] = display;
                }

                var displayObject = regionDisplays[region.Key];
                // Update the display with region.Value chaos level
                // This would depend on the prefab structure
            }
        }

        private void UpdateSystemPressureDisplay(Dictionary<string, float> systemPressures)
        {
            if (systemPressureContainer == null || pressureBarPrefab == null) return;

            foreach (var system in systemPressures)
            {
                if (!pressureBars.ContainsKey(system.Key))
                {
                    var bar = Instantiate(pressureBarPrefab, systemPressureContainer);
                    pressureBars[system.Key] = bar;
                }

                var barObject = pressureBars[system.Key];
                // Update the pressure bar with system.Value
                // This would depend on the prefab structure
            }
        }

        private void UpdatePressureDisplay(List<PressureSourceDTO> pressures)
        {
            currentPressures = pressures;
            foreach (var pressure in pressures)
            {
                UpdateSinglePressureBar(pressure);
            }
        }

        private void UpdateSinglePressureBar(PressureSourceDTO pressure)
        {
            if (pressureBars.ContainsKey(pressure.SystemName))
            {
                var barObject = pressureBars[pressure.SystemName];
                // Update individual pressure bar
                // Implementation depends on prefab structure
            }
        }

        private void UpdateEventLog(List<ChaosEventDTO> events)
        {
            recentEvents = events.Take(maxLogEntries).ToList();
            ClearEventLog();

            foreach (var eventItem in recentEvents)
            {
                AddEventLogEntry(eventItem);
            }
        }

        private void AddEventLogEntry(ChaosEventDTO chaosEvent)
        {
            if (eventLogContent == null || eventLogEntryPrefab == null) return;

            var entry = Instantiate(eventLogEntryPrefab, eventLogContent);
            // Configure the entry based on the event
            // This would depend on the prefab structure

            // Scroll to top
            if (eventLogScrollRect != null)
            {
                Canvas.ForceUpdateCanvases();
                eventLogScrollRect.verticalNormalizedPosition = 1f;
            }
        }

        private void AddAlertDisplay(ChaosAlert alert)
        {
            if (alertContainer == null || alertPrefab == null) return;

            if (!alertDisplays.ContainsKey(alert.AlertType))
            {
                var alertDisplay = Instantiate(alertPrefab, alertContainer);
                alertDisplays[alert.AlertType] = alertDisplay;
                // Configure alert display based on alert data
            }
        }

        private void ClearEventLog()
        {
            if (eventLogContent != null)
            {
                foreach (Transform child in eventLogContent)
                {
                    Destroy(child.gameObject);
                }
            }
        }

        private void ClearAlerts()
        {
            foreach (var alert in alertDisplays.Values)
            {
                if (alert != null)
                    Destroy(alert);
            }
            alertDisplays.Clear();
        }

        private void UpdateLastUpdateTime()
        {
            if (lastUpdateText != null)
                lastUpdateText.text = $"Last Update: {DateTime.Now:HH:mm:ss}";
        }

        // Public Properties and Methods

        public bool IsVisible => isVisible;
        public bool IsInitialized => isInitialized;
        public ChaosMetricsDTO CurrentMetrics => currentMetrics;

        /// <summary>
        /// Show or hide the panel
        /// </summary>
        public void SetPanelVisibility(bool visible)
        {
            if (visible != isVisible)
                TogglePanel();
        }

        /// <summary>
        /// Check if user has admin privileges (implement based on your auth system)
        /// </summary>
        public bool HasAdminAccess()
        {
            // Implement admin access check here
            // This should integrate with your existing authentication system
            return true; // Placeholder
        }
    }
} 