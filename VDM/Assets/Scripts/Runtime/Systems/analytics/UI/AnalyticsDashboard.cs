using VDM.Infrastructure.Core.Core.Ui;
using System.Collections.Generic;
using System.Linq;
using System;
using TMPro;
using UnityEngine.UI;
using UnityEngine;
using VDM.Systems.Analytics.Models;
using VDM.Systems.Analytics.Services;
using VDM.UI.Core;


namespace VDM.Systems.Analytics.Ui
{
    /// <summary>
    /// Advanced analytics dashboard providing real-time monitoring and visualization
    /// </summary>
    public class AnalyticsDashboard : BaseUIComponent
    {
        [Header("Dashboard Panels")]
        [SerializeField] private GameObject performancePanel;
        [SerializeField] private GameObject eventsPanel;
        [SerializeField] private GameObject systemHealthPanel;
        [SerializeField] private GameObject reportsPanel;

        [Header("Performance Monitoring")]
        [SerializeField] private TextMeshProUGUI fpsText;
        [SerializeField] private TextMeshProUGUI memoryText;
        [SerializeField] private TextMeshProUGUI networkLatencyText;
        [SerializeField] private Slider fpsSlider;
        [SerializeField] private Slider memorySlider;
        [SerializeField] private Image performanceStatusIcon;

        [Header("Event Tracking")]
        [SerializeField] private ScrollRect eventScrollView;
        [SerializeField] private Transform eventListContainer;
        [SerializeField] private GameObject eventItemPrefab;
        [SerializeField] private TextMeshProUGUI totalEventsText;
        [SerializeField] private Dropdown eventTypeFilter;

        [Header("System Health")]
        [SerializeField] private Transform systemHealthContainer;
        [SerializeField] private GameObject systemHealthItemPrefab;
        [SerializeField] private TextMeshProUGUI healthSummaryText;
        [SerializeField] private Image overallHealthIcon;

        [Header("Reports")]
        [SerializeField] private Button generateReportButton;
        [SerializeField] private TMP_InputField startDateInput;
        [SerializeField] private TMP_InputField endDateInput;
        [SerializeField] private TextMeshProUGUI reportStatusText;
        [SerializeField] private Transform reportListContainer;
        [SerializeField] private GameObject reportItemPrefab;

        [Header("Controls")]
        [SerializeField] private Button refreshButton;
        [SerializeField] private Toggle autoRefreshToggle;
        [SerializeField] private Button exportDataButton;
        [SerializeField] private Button clearEventsButton;

        [Header("Settings")]
        [SerializeField] private float maxEventsDisplayed = 100;
        [SerializeField] private float autoRefreshInterval = 5.0f;

        // Private fields
        private AnalyticsService analyticsService;
        private List<GameObject> eventItems = new List<GameObject>();
        private List<GameObject> systemHealthItems = new List<GameObject>();
        private List<GameObject> reportItems = new List<GameObject>();
        private AnalyticsEventType? currentEventFilter;
        private float lastAutoRefresh;

        // UI state
        private bool isInitialized;
        private Color healthyColor = Color.green;
        private Color warningColor = Color.yellow;
        private Color criticalColor = Color.red;
        private Color offlineColor = Color.gray;

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

            // Auto-refresh if enabled
            if (autoRefreshToggle.isOn && UnityEngine.Time.time - lastAutoRefresh >= autoRefreshInterval)
            {
                RefreshDashboard();
                lastAutoRefresh = UnityEngine.Time.time;
            }
        }

        /// <summary>
        /// Initialize the analytics dashboard
        /// </summary>
        public override void Initialize()
        {
            if (isInitialized) return;

            analyticsService = AnalyticsService.Instance;
            if (analyticsService == null)
            {
                Debug.LogError("AnalyticsDashboard: AnalyticsService not found!");
                return;
            }

            // Subscribe to analytics events
            AnalyticsService.OnEventRecorded += OnEventRecorded;
            AnalyticsService.OnPerformanceUpdated += OnPerformanceUpdated;
            AnalyticsService.OnSystemHealthUpdated += OnSystemHealthUpdated;
            AnalyticsService.OnDashboardDataUpdated += OnDashboardDataUpdated;

            // Initialize UI components
            InitializeEventTypeFilter();
            InitializeDateInputs();
            
            // Load initial data
            RefreshDashboard();

            isInitialized = true;
            Debug.Log("AnalyticsDashboard initialized successfully");
        }

        private void InitializeControls()
        {
            // Button event handlers
            refreshButton.onClick.AddListener(RefreshDashboard);
            generateReportButton.onClick.AddListener(GenerateReport);
            exportDataButton.onClick.AddListener(ExportData);
            clearEventsButton.onClick.AddListener(ClearEvents);

            // Toggle handlers
            autoRefreshToggle.onValueChanged.AddListener(OnAutoRefreshToggled);

            // Filter handlers
            eventTypeFilter.onValueChanged.AddListener(OnEventFilterChanged);
        }

        private void InitializeEventTypeFilter()
        {
            eventTypeFilter.options.Clear();
            eventTypeFilter.options.Add(new Dropdown.OptionData("All Events"));
            
            foreach (AnalyticsEventType eventType in Enum.GetValues(typeof(AnalyticsEventType)))
            {
                eventTypeFilter.options.Add(new Dropdown.OptionData(eventType.ToString()));
            }
            
            eventTypeFilter.RefreshShownValue();
        }

        private void InitializeDateInputs()
        {
            // Set default date range (last 7 days)
            var endDate = DateTime.Now;
            var startDate = endDate.AddDays(-7);
            
            startDateInput.text = startDate.ToString("yyyy-MM-dd");
            endDateInput.text = endDate.ToString("yyyy-MM-dd");
        }

        private void RefreshDashboard()
        {
            if (!isInitialized) return;

            // Update performance metrics
            UpdatePerformanceDisplay();

            // Update event list
            UpdateEventsList();

            // Update system health
            UpdateSystemHealthDisplay();

            Debug.Log("Dashboard refreshed");
        }

        private void UpdatePerformanceDisplay()
        {
            var metrics = analyticsService.GetCurrentMetrics();
            if (metrics == null) return;

            // Update FPS
            fpsText.text = $"FPS: {metrics.averageFrameRate:F1}";
            fpsSlider.value = Mathf.Clamp01(metrics.averageFrameRate / 60f);

            // Update Memory
            memoryText.text = $"Memory: {metrics.memoryUsage:F1} MB";
            memorySlider.value = Mathf.Clamp01(metrics.memoryUsage / 2048f); // Assume 2GB max

            // Update Network Latency
            networkLatencyText.text = $"Latency: {metrics.networkLatency:F0} ms";

            // Update status icon based on performance
            var overallPerformance = (fpsSlider.value + (1f - memorySlider.value)) / 2f;
            performanceStatusIcon.color = overallPerformance > 0.7f ? healthyColor : 
                                         overallPerformance > 0.4f ? warningColor : criticalColor;
        }

        private void UpdateEventsList()
        {
            var recentEvents = analyticsService.GetRecentEvents((int)maxEventsDisplayed);
            
            // Apply filter
            if (currentEventFilter.HasValue)
            {
                recentEvents = recentEvents.Where(e => e.eventType == currentEventFilter.Value).ToList();
            }

            // Clear existing items
            foreach (var item in eventItems)
            {
                if (item != null) Destroy(item);
            }
            eventItems.Clear();

            // Create new items
            foreach (var analyticsEvent in recentEvents.Take((int)maxEventsDisplayed))
            {
                CreateEventItem(analyticsEvent);
            }

            // Update total count
            totalEventsText.text = $"Total Events: {recentEvents.Count}";
        }

        private void CreateEventItem(AnalyticsEvent analyticsEvent)
        {
            var item = Instantiate(eventItemPrefab, eventListContainer);
            eventItems.Add(item);

            // Get components
            var texts = item.GetComponentsInChildren<TextMeshProUGUI>();
            var icon = item.GetComponentInChildren<Image>();

            if (texts.Length >= 3)
            {
                texts[0].text = analyticsEvent.eventType.ToString();
                texts[1].text = analyticsEvent.timestamp.ToString("HH:mm:ss");
                texts[2].text = $"Session: {analyticsEvent.sessionId?.Substring(0, 8)}...";
            }

            // Color code by event type
            if (icon != null)
            {
                icon.color = GetEventTypeColor(analyticsEvent.eventType);
            }
        }

        private void UpdateSystemHealthDisplay()
        {
            var systemHealth = analyticsService.GetSystemHealth();
            if (systemHealth == null) return;

            // Clear existing items
            foreach (var item in systemHealthItems)
            {
                if (item != null) Destroy(item);
            }
            systemHealthItems.Clear();

            // Create new items
            foreach (var status in systemHealth)
            {
                CreateSystemHealthItem(status);
            }

            // Update summary
            var healthyCounts = systemHealth.Count(s => s.healthLevel == HealthLevel.Healthy);
            var totalSystems = systemHealth.Count;
            healthSummaryText.text = $"{healthyCounts}/{totalSystems} Systems Healthy";

            // Update overall health icon
            var healthRatio = (float)healthyCounts / totalSystems;
            overallHealthIcon.color = healthRatio > 0.8f ? healthyColor :
                                     healthRatio > 0.5f ? warningColor : criticalColor;
        }

        private void CreateSystemHealthItem(SystemHealthStatus status)
        {
            var item = Instantiate(systemHealthItemPrefab, systemHealthContainer);
            systemHealthItems.Add(item);

            // Get components
            var texts = item.GetComponentsInChildren<TextMeshProUGUI>();
            var icon = item.GetComponentInChildren<Image>();

            if (texts.Length >= 3)
            {
                texts[0].text = status.systemName;
                texts[1].text = status.status;
                texts[2].text = $"{status.uptime:F1}%";
            }

            // Set health level color
            if (icon != null)
            {
                icon.color = GetHealthLevelColor(status.healthLevel);
            }
        }

        private Color GetEventTypeColor(AnalyticsEventType eventType)
        {
            // Color coding for different event types
            switch (eventType)
            {
                case AnalyticsEventType.GameStart:
                case AnalyticsEventType.GameEnd:
                    return Color.blue;
                case AnalyticsEventType.CombatEvent:
                    return Color.red;
                case AnalyticsEventType.QuestEvent:
                    return Color.green;
                case AnalyticsEventType.FactionEvent:
                    return Color.magenta;
                default:
                    return Color.white;
            }
        }

        private Color GetHealthLevelColor(HealthLevel healthLevel)
        {
            switch (healthLevel)
            {
                case HealthLevel.Healthy: return healthyColor;
                case HealthLevel.Warning: return warningColor;
                case HealthLevel.Critical: return criticalColor;
                case HealthLevel.Offline: return offlineColor;
                default: return Color.white;
            }
        }

        // Event handlers
        private void OnEventRecorded(AnalyticsEvent analyticsEvent)
        {
            if (!autoRefreshToggle.isOn) return;
            UpdateEventsList();
        }

        private void OnPerformanceUpdated(PerformanceMetrics metrics)
        {
            UpdatePerformanceDisplay();
        }

        private void OnSystemHealthUpdated(List<SystemHealthStatus> healthStatus)
        {
            UpdateSystemHealthDisplay();
        }

        private void OnDashboardDataUpdated(DashboardData dashboardData)
        {
            // Full dashboard refresh with new data
            RefreshDashboard();
        }

        private void OnAutoRefreshToggled(bool isEnabled)
        {
            if (isEnabled)
            {
                lastAutoRefresh = UnityEngine.Time.time;
            }
        }

        private void OnEventFilterChanged(int index)
        {
            if (index == 0)
            {
                currentEventFilter = null; // Show all events
            }
            else
            {
                currentEventFilter = (AnalyticsEventType)(index);
            }
            
            UpdateEventsList();
        }

        private async void GenerateReport()
        {
            if (!DateTime.TryParse(startDateInput.text, out var startDate) ||
                !DateTime.TryParse(endDateInput.text, out var endDate))
            {
                reportStatusText.text = "Invalid date format. Use yyyy-MM-dd";
                return;
            }

            reportStatusText.text = "Generating report...";
            generateReportButton.interactable = false;

            try
            {
                var report = await analyticsService.GenerateReport(startDate, endDate);
                if (report != null)
                {
                    CreateReportItem(report);
                    reportStatusText.text = "Report generated successfully";
                }
                else
                {
                    reportStatusText.text = "Failed to generate report";
                }
            }
            catch (Exception ex)
            {
                reportStatusText.text = $"Error: {ex.Message}";
                Debug.LogError($"Report generation error: {ex}");
            }
            finally
            {
                generateReportButton.interactable = true;
            }
        }

        private void CreateReportItem(AnalyticsReport report)
        {
            var item = Instantiate(reportItemPrefab, reportListContainer);
            reportItems.Add(item);

            var texts = item.GetComponentsInChildren<TextMeshProUGUI>();
            if (texts.Length >= 3)
            {
                texts[0].text = report.title ?? "Analytics Report";
                texts[1].text = $"{report.startDate:yyyy-MM-dd} to {report.endDate:yyyy-MM-dd}";
                texts[2].text = $"Events: {report.eventCounts?.Values.Sum() ?? 0}";
            }

            // Add click handler to view report details
            var button = item.GetComponent<Button>();
            if (button != null)
            {
                button.onClick.AddListener(() => ViewReportDetails(report));
            }
        }

        private void ViewReportDetails(AnalyticsReport report)
        {
            // This would open a detailed report view
            Debug.Log($"Viewing report: {report.reportId}");
            // TODO: Implement detailed report viewer
        }

        private void ExportData()
        {
            // Export current dashboard data
            var data = new
            {
                exportTime = DateTime.UtcNow,
                performanceMetrics = analyticsService.GetCurrentMetrics(),
                recentEvents = analyticsService.GetRecentEvents(100),
                systemHealth = analyticsService.GetSystemHealth()
            };

            var json = JsonUtility.ToJson(data, true);
            Debug.Log("Exporting analytics data...");
            // TODO: Implement actual file export
        }

        private void ClearEvents()
        {
            foreach (var item in eventItems)
            {
                if (item != null) Destroy(item);
            }
            eventItems.Clear();
            totalEventsText.text = "Total Events: 0";
        }

        protected override void OnDestroy()
        {
            base.OnDestroy();
            
            // Unsubscribe from events
            if (analyticsService != null)
            {
                AnalyticsService.OnEventRecorded -= OnEventRecorded;
                AnalyticsService.OnPerformanceUpdated -= OnPerformanceUpdated;
                AnalyticsService.OnSystemHealthUpdated -= OnSystemHealthUpdated;
                AnalyticsService.OnDashboardDataUpdated -= OnDashboardDataUpdated;
            }

            isInitialized = false;
        }
    }
} 