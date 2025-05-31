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
    /// Real-time pressure visualization with charts and graphs for admin monitoring
    /// </summary>
    public class PressureVisualization : MonoBehaviour
    {
        [Header("Core References")]
        [SerializeField] private ChaosService chaosService;

        [Header("Chart Containers")]
        [SerializeField] private RectTransform lineChartContainer;
        [SerializeField] private RectTransform pieChartContainer;
        [SerializeField] private RectTransform barChartContainer;
        [SerializeField] private RectTransform heatmapContainer;

        [Header("Line Chart Settings")]
        [SerializeField] private GameObject lineChartPrefab;
        [SerializeField] private Color[] systemColors = new Color[10];
        [SerializeField] private int maxDataPoints = 100;
        [SerializeField] private float chartUpdateInterval = 2.0f;

        [Header("Pressure Bars")]
        [SerializeField] private Transform pressureBarContainer;
        [SerializeField] private GameObject pressureBarPrefab;
        [SerializeField] private float barHeight = 20f;
        [SerializeField] private float barSpacing = 5f;

        [Header("Regional Heatmap")]
        [SerializeField] private Transform heatmapGrid;
        [SerializeField] private GameObject heatmapCellPrefab;
        [SerializeField] private int heatmapGridSize = 10;

        [Header("Trend Analysis")]
        [SerializeField] private TextMeshProUGUI trendAnalysisText;
        [SerializeField] private Image trendArrowImage;
        [SerializeField] private Color increasingColor = Color.red;
        [SerializeField] private Color decreasingColor = Color.green;
        [SerializeField] private Color stableColor = Color.yellow;

        [Header("Time Controls")]
        [SerializeField] private Dropdown timeRangeDropdown;
        [SerializeField] private Button pauseButton;
        [SerializeField] private Button playButton;
        [SerializeField] private TextMeshProUGUI timeDisplayText;

        private Dictionary<string, LineChartData> lineChartData = new Dictionary<string, LineChartData>();
        private Dictionary<string, GameObject> pressureBars = new Dictionary<string, GameObject>();
        private Dictionary<string, GameObject> heatmapCells = new Dictionary<string, GameObject>();
        private List<ChaosDataPoint> historicalData = new List<ChaosDataPoint>();
        
        private bool isPlaying = true;
        private bool isInitialized = false;
        private float lastUpdateTime = 0f;
        private TimeRange selectedTimeRange = TimeRange.LastHour;

        // Chart data structures
        private class LineChartData
        {
            public List<Vector2> dataPoints = new List<Vector2>();
            public LineRenderer lineRenderer;
            public Color color;
            public string systemName;
        }

        private enum TimeRange
        {
            LastMinute,
            LastHour,
            LastDay,
            LastWeek
        }

        private void Start()
        {
            InitializeVisualization();
        }

        private void Update()
        {
            if (isInitialized && isPlaying && Time.time - lastUpdateTime > chartUpdateInterval)
            {
                UpdateCharts();
                lastUpdateTime = Time.time;
            }
        }

        private void OnDestroy()
        {
            if (chaosService != null)
            {
                chaosService.OnPressureUpdated -= HandlePressureUpdate;
                chaosService.OnMetricsUpdated -= HandleMetricsUpdate;
            }
        }

        /// <summary>
        /// Initialize the visualization system
        /// </summary>
        private void InitializeVisualization()
        {
            if (chaosService == null)
            {
                chaosService = FindObjectOfType<ChaosService>();
                if (chaosService == null)
                {
                    Debug.LogError("PressureVisualization: ChaosService not found");
                    return;
                }
            }

            // Subscribe to events
            chaosService.OnPressureUpdated += HandlePressureUpdate;
            chaosService.OnMetricsUpdated += HandleMetricsUpdate;

            // Setup UI controls
            SetupTimeControls();
            InitializeCharts();
            InitializeHeatmap();

            isInitialized = true;
            Debug.Log("PressureVisualization initialized successfully");
        }

        /// <summary>
        /// Setup time control UI elements
        /// </summary>
        private void SetupTimeControls()
        {
            if (timeRangeDropdown != null)
            {
                timeRangeDropdown.options.Clear();
                timeRangeDropdown.options.Add(new Dropdown.OptionData("Last Minute"));
                timeRangeDropdown.options.Add(new Dropdown.OptionData("Last Hour"));
                timeRangeDropdown.options.Add(new Dropdown.OptionData("Last Day"));
                timeRangeDropdown.options.Add(new Dropdown.OptionData("Last Week"));
                timeRangeDropdown.value = 1; // Default to Last Hour
                timeRangeDropdown.onValueChanged.AddListener(OnTimeRangeChanged);
            }

            if (pauseButton != null)
                pauseButton.onClick.AddListener(PauseVisualization);

            if (playButton != null)
                playButton.onClick.AddListener(PlayVisualization);

            UpdateTimeDisplay();
        }

        /// <summary>
        /// Initialize chart components
        /// </summary>
        private void InitializeCharts()
        {
            // Clear existing charts
            ClearCharts();

            // Initialize system colors if not set
            if (systemColors.Length == 0 || systemColors[0] == Color.clear)
            {
                systemColors = new Color[]
                {
                    Color.red, Color.blue, Color.green, Color.yellow, Color.cyan,
                    Color.magenta, Color.white, Color.gray, new Color(1f, 0.5f, 0f), new Color(0.5f, 0f, 1f)
                };
            }
        }

        /// <summary>
        /// Initialize the regional heatmap
        /// </summary>
        private void InitializeHeatmap()
        {
            if (heatmapGrid == null || heatmapCellPrefab == null) return;

            // Clear existing heatmap
            foreach (Transform child in heatmapGrid)
            {
                Destroy(child.gameObject);
            }
            heatmapCells.Clear();

            // Create heatmap grid
            for (int x = 0; x < heatmapGridSize; x++)
            {
                for (int y = 0; y < heatmapGridSize; y++)
                {
                    var cell = Instantiate(heatmapCellPrefab, heatmapGrid);
                    var cellKey = $"{x},{y}";
                    heatmapCells[cellKey] = cell;

                    // Position the cell
                    var rectTransform = cell.GetComponent<RectTransform>();
                    if (rectTransform != null)
                    {
                        rectTransform.anchoredPosition = new Vector2(x * 25f, y * 25f);
                    }
                }
            }
        }

        /// <summary>
        /// Update all charts with current data
        /// </summary>
        private async void UpdateCharts()
        {
            try
            {
                // Get recent pressure data
                var pressures = await chaosService.GetPressureSourcesAsync();
                if (pressures != null)
                {
                    UpdatePressureBars(pressures);
                    UpdateLineCharts(pressures);
                }

                // Get metrics for regional heatmap
                var metrics = await chaosService.GetMetricsAsync();
                if (metrics != null)
                {
                    UpdateRegionalHeatmap(metrics.RegionalChaosLevels);
                    UpdateTrendAnalysis(metrics);
                }

                UpdateTimeDisplay();
            }
            catch (Exception ex)
            {
                Debug.LogError($"PressureVisualization: Error updating charts: {ex.Message}");
            }
        }

        /// <summary>
        /// Update pressure bar charts
        /// </summary>
        private void UpdatePressureBars(List<PressureSourceDTO> pressures)
        {
            if (pressureBarContainer == null || pressureBarPrefab == null) return;

            // Remove bars for systems that no longer exist
            var currentSystems = pressures.Select(p => p.SystemName).ToHashSet();
            var toRemove = pressureBars.Keys.Where(key => !currentSystems.Contains(key)).ToList();
            foreach (var key in toRemove)
            {
                if (pressureBars[key] != null)
                    Destroy(pressureBars[key]);
                pressureBars.Remove(key);
            }

            // Update or create bars for each system
            for (int i = 0; i < pressures.Count; i++)
            {
                var pressure = pressures[i];
                var systemName = pressure.SystemName;

                if (!pressureBars.ContainsKey(systemName))
                {
                    var bar = Instantiate(pressureBarPrefab, pressureBarContainer);
                    pressureBars[systemName] = bar;

                    // Position the bar
                    var rectTransform = bar.GetComponent<RectTransform>();
                    if (rectTransform != null)
                    {
                        rectTransform.anchoredPosition = new Vector2(0, -(i * (barHeight + barSpacing)));
                    }
                }

                UpdateSinglePressureBar(pressureBars[systemName], pressure);
            }
        }

        /// <summary>
        /// Update a single pressure bar
        /// </summary>
        private void UpdateSinglePressureBar(GameObject barObject, PressureSourceDTO pressure)
        {
            // Update bar fill based on pressure percentage
            var fillImage = barObject.GetComponentInChildren<Image>();
            if (fillImage != null)
            {
                var percentage = pressure.MaxPressure > 0 ? pressure.CurrentPressure / pressure.MaxPressure : 0f;
                fillImage.fillAmount = percentage;

                // Color based on pressure level
                fillImage.color = percentage switch
                {
                    >= 0.8f => increasingColor,
                    >= 0.6f => stableColor,
                    _ => decreasingColor
                };
            }

            // Update text labels
            var texts = barObject.GetComponentsInChildren<TextMeshProUGUI>();
            if (texts.Length >= 2)
            {
                texts[0].text = pressure.SystemName;
                texts[1].text = $"{pressure.CurrentPressure:F1}/{pressure.MaxPressure:F1}";
            }

            // Update trend indicator
            var trendImage = barObject.transform.Find("TrendArrow")?.GetComponent<Image>();
            if (trendImage != null)
            {
                trendImage.color = pressure.Trend switch
                {
                    PressureTrend.Increasing => increasingColor,
                    PressureTrend.Decreasing => decreasingColor,
                    PressureTrend.Critical => Color.red,
                    _ => stableColor
                };

                // Rotate arrow based on trend
                var rotation = pressure.Trend switch
                {
                    PressureTrend.Increasing => 0f,
                    PressureTrend.Decreasing => 180f,
                    PressureTrend.Critical => 0f,
                    _ => 90f
                };
                trendImage.transform.rotation = Quaternion.Euler(0, 0, rotation);
            }
        }

        /// <summary>
        /// Update line charts with historical pressure data
        /// </summary>
        private void UpdateLineCharts(List<PressureSourceDTO> pressures)
        {
            if (lineChartContainer == null) return;

            var currentTime = Time.time;

            foreach (var pressure in pressures)
            {
                var systemName = pressure.SystemName;

                // Create line chart data if it doesn't exist
                if (!lineChartData.ContainsKey(systemName))
                {
                    var chartData = new LineChartData
                    {
                        systemName = systemName,
                        color = systemColors[lineChartData.Count % systemColors.Length]
                    };

                    // Create line renderer
                    var lineObject = new GameObject($"LineChart_{systemName}");
                    lineObject.transform.SetParent(lineChartContainer);
                    chartData.lineRenderer = lineObject.AddComponent<LineRenderer>();
                    chartData.lineRenderer.material = new Material(Shader.Find("Sprites/Default"));
                    chartData.lineRenderer.color = chartData.color;
                    chartData.lineRenderer.widthMultiplier = 2f;
                    chartData.lineRenderer.useWorldSpace = false;

                    lineChartData[systemName] = chartData;
                }

                var chart = lineChartData[systemName];

                // Add new data point
                var dataPoint = new Vector2(currentTime, pressure.CurrentPressure);
                chart.dataPoints.Add(dataPoint);

                // Remove old data points based on time range
                var cutoffTime = GetCutoffTime();
                chart.dataPoints.RemoveAll(point => point.x < cutoffTime);

                // Limit data points to prevent performance issues
                if (chart.dataPoints.Count > maxDataPoints)
                {
                    chart.dataPoints.RemoveAt(0);
                }

                // Update line renderer
                UpdateLineRenderer(chart);
            }
        }

        /// <summary>
        /// Update line renderer with current data points
        /// </summary>
        private void UpdateLineRenderer(LineChartData chartData)
        {
            if (chartData.lineRenderer == null || chartData.dataPoints.Count < 2) return;

            var points = chartData.dataPoints.ToArray();
            chartData.lineRenderer.positionCount = points.Length;

            // Normalize points to fit within the chart container
            var containerRect = lineChartContainer.rect;
            var minTime = points.Min(p => p.x);
            var maxTime = points.Max(p => p.x);
            var minPressure = 0f;
            var maxPressure = points.Max(p => p.y);

            for (int i = 0; i < points.Length; i++)
            {
                var normalizedX = containerRect.width * ((points[i].x - minTime) / (maxTime - minTime));
                var normalizedY = containerRect.height * (points[i].y / maxPressure);
                chartData.lineRenderer.SetPosition(i, new Vector3(normalizedX, normalizedY, 0));
            }
        }

        /// <summary>
        /// Update regional chaos heatmap
        /// </summary>
        private void UpdateRegionalHeatmap(Dictionary<string, float> regionalLevels)
        {
            if (heatmapCells.Count == 0) return;

            // For demonstration, we'll map regional data to grid positions
            // In a real implementation, you'd have actual regional coordinates
            var regions = regionalLevels.Keys.ToArray();
            var maxChaos = regionalLevels.Values.Max();

            for (int i = 0; i < Math.Min(regions.Length, heatmapCells.Count); i++)
            {
                var regionId = regions[i];
                var chaosLevel = regionalLevels[regionId];
                var cellKey = heatmapCells.Keys.ElementAt(i);
                var cell = heatmapCells[cellKey];

                var image = cell.GetComponent<Image>();
                if (image != null)
                {
                    var intensity = maxChaos > 0 ? chaosLevel / maxChaos : 0f;
                    image.color = Color.Lerp(decreasingColor, increasingColor, intensity);
                }

                // Add tooltip or label
                var text = cell.GetComponentInChildren<TextMeshProUGUI>();
                if (text != null)
                {
                    text.text = $"{chaosLevel:F1}";
                }
            }
        }

        /// <summary>
        /// Update trend analysis display
        /// </summary>
        private void UpdateTrendAnalysis(ChaosMetricsDTO metrics)
        {
            if (trendAnalysisText == null) return;

            var analysis = AnalyzeTrends(metrics);
            trendAnalysisText.text = analysis.summary;

            if (trendArrowImage != null)
            {
                trendArrowImage.color = analysis.overallTrend switch
                {
                    PressureTrend.Increasing => increasingColor,
                    PressureTrend.Decreasing => decreasingColor,
                    PressureTrend.Critical => Color.red,
                    _ => stableColor
                };

                var rotation = analysis.overallTrend switch
                {
                    PressureTrend.Increasing => 0f,
                    PressureTrend.Decreasing => 180f,
                    PressureTrend.Critical => 0f,
                    _ => 90f
                };
                trendArrowImage.transform.rotation = Quaternion.Euler(0, 0, rotation);
            }
        }

        /// <summary>
        /// Analyze current trends
        /// </summary>
        private (string summary, PressureTrend overallTrend) AnalyzeTrends(ChaosMetricsDTO metrics)
        {
            var summary = $"Global Chaos: {metrics.GlobalChaosLevel:F1}%\n";
            summary += $"Active Events: {metrics.ActiveEvents}\n";
            summary += $"System Health: {metrics.SystemHealth.OverallStatus}";

            var overallTrend = PressureTrend.Stable;

            // Analyze overall trend based on multiple factors
            if (metrics.GlobalChaosLevel > 80f || metrics.SystemHealth.OverallStatus == SystemStatus.Critical)
                overallTrend = PressureTrend.Critical;
            else if (metrics.ActiveEvents > 5 || metrics.GlobalChaosLevel > 60f)
                overallTrend = PressureTrend.Increasing;
            else if (metrics.ActiveEvents == 0 && metrics.GlobalChaosLevel < 20f)
                overallTrend = PressureTrend.Decreasing;

            return (summary, overallTrend);
        }

        // Event Handlers

        private void HandlePressureUpdate(PressureSourceDTO pressure)
        {
            // Real-time pressure updates are handled in UpdateCharts()
            // This could be used for immediate visual feedback
        }

        private void HandleMetricsUpdate(ChaosMetricsDTO metrics)
        {
            // Real-time metrics updates
            UpdateTrendAnalysis(metrics);
        }

        // UI Control Handlers

        private void OnTimeRangeChanged(int value)
        {
            selectedTimeRange = (TimeRange)value;
            ClearCharts();
            Debug.Log($"PressureVisualization: Time range changed to {selectedTimeRange}");
        }

        private void PauseVisualization()
        {
            isPlaying = false;
            if (pauseButton != null) pauseButton.gameObject.SetActive(false);
            if (playButton != null) playButton.gameObject.SetActive(true);
            Debug.Log("PressureVisualization: Paused");
        }

        private void PlayVisualization()
        {
            isPlaying = true;
            if (pauseButton != null) pauseButton.gameObject.SetActive(true);
            if (playButton != null) playButton.gameObject.SetActive(false);
            Debug.Log("PressureVisualization: Resumed");
        }

        // Utility Methods

        private float GetCutoffTime()
        {
            var currentTime = Time.time;
            return selectedTimeRange switch
            {
                TimeRange.LastMinute => currentTime - 60f,
                TimeRange.LastHour => currentTime - 3600f,
                TimeRange.LastDay => currentTime - 86400f,
                TimeRange.LastWeek => currentTime - 604800f,
                _ => currentTime - 3600f
            };
        }

        private void UpdateTimeDisplay()
        {
            if (timeDisplayText != null)
            {
                timeDisplayText.text = $"Time: {DateTime.Now:HH:mm:ss}";
            }
        }

        private void ClearCharts()
        {
            foreach (var chart in lineChartData.Values)
            {
                if (chart.lineRenderer != null)
                    Destroy(chart.lineRenderer.gameObject);
            }
            lineChartData.Clear();
        }

        // Public Methods

        public void RefreshVisualization()
        {
            UpdateCharts();
        }

        public void SetTimeRange(TimeRange timeRange)
        {
            selectedTimeRange = timeRange;
            if (timeRangeDropdown != null)
                timeRangeDropdown.value = (int)timeRange;
            ClearCharts();
        }

        public bool IsPlaying => isPlaying;
        public TimeRange CurrentTimeRange => selectedTimeRange;
    }
} 