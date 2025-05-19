using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using VisualDM.Core;
using Newtonsoft.Json.Linq;
using UnityEngine.Networking;
using VisualDM.Net;

namespace VisualDM.UI
{
    /// <summary>
    /// Runtime-generated dashboard UI for monitoring and alerting.
    /// </summary>
    public class MonitoringDashboard : MonoBehaviour
    {
        private Canvas canvas;
        private RectTransform rootPanel;
        private Text fpsText, memoryText, errorText, pingText;
        private Image fpsIndicator, errorIndicator;
        private RectTransform alertLogPanel;
        private List<Text> alertLogEntries = new List<Text>();
        private int maxLogEntries = 10;
        private float updateInterval = 1f;
        private float updateTimer = 0f;
        private Color green = new Color(0.2f, 0.8f, 0.2f);
        private Color yellow = new Color(1f, 0.85f, 0.2f);
        private Color red = new Color(0.9f, 0.2f, 0.2f);
        private int selectedIndex = 0;
        private List<Selectable> selectables = new List<Selectable>();
        private Text thresholdsText;
        private MetricsApiClient apiClient;
        private bool showRealTime = true;
        private List<JObject> historicalMetrics = new List<JObject>();
        private int currentPage = 1;
        private int pageSize = 100;
        private string historicalStartTime = "";
        private string historicalEndTime = "";
        private LineRenderer historicalFpsLine;
        private GameObject historicalChartObj;
        private RectTransform thresholdPanel;
        private CoreField fpsWarningCore, fpsCriticalCore, memWarningCore, memCriticalCore;
        private Button applyThresholdsButton, testAlertButton;
        private Button exportCsvButton, exportPdfButton;
        private bool isAuthenticated = false;
        private string authToken = "";
        private const string MetricsWebSocketKey = "metrics";

        void Start()
        {
            CreateUI();
            MonitoringManager.Instance.SubscribeToAlerts(OnAlertReceived);
            var wsManager = WebSocketManager.Instance;
            if (wsManager != null)
            {
                wsManager.Connect(MetricsWebSocketKey, "ws://localhost:8000/api/v1/ws/metrics/stream", authToken);
                wsManager.Clients[MetricsWebSocketKey].RegisterMessageHandler("metrics_update", OnRealTimeMetricsReceivedJson);
            }
            // Default to real-time view
            showRealTime = true;
            if (!isAuthenticated)
            {
                ShowLoginPanel();
                // Block dashboard interaction until authenticated
                return;
            }
            // Set auth token for API/WebSocket clients
            apiClient.SetAuthToken(authToken);
            RecordAuditLog("DashboardOpened", "User opened monitoring dashboard");
        }

        void OnDestroy()
        {
            if (MonitoringManager.Instance != null)
                MonitoringManager.Instance.UnsubscribeFromAlerts(OnAlertReceived);
        }

        void Update()
        {
            updateTimer += Time.unscaledDeltaTime;
            if (updateTimer >= updateInterval)
            {
                if (showRealTime)
                    UpdateMetrics();
                else
                    UpdateHistoricalMetricsUI();
                updateTimer = 0f;
            }
            HandleKeyboardNavigation();
        }

        private void CreateUI()
        {
            try
            {
                // Canvas
                canvas = new GameObject("MonitoringDashboardCanvas").AddComponent<Canvas>();
                canvas.renderMode = RenderMode.ScreenSpaceOverlay;
                canvas.gameObject.AddComponent<CanvasScaler>().uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
                canvas.gameObject.AddComponent<GraphicRaycaster>();
                DontDestroyOnLoad(canvas.gameObject);

                // Root panel
                rootPanel = new GameObject("RootPanel").AddComponent<RectTransform>();
                rootPanel.SetParent(canvas.transform, false);
                rootPanel.anchorMin = Vector2.zero;
                rootPanel.anchorMax = Vector2.one;
                rootPanel.offsetMin = Vector2.zero;
                rootPanel.offsetMax = Vector2.zero;

                // Top row: KPIs
                var kpiPanel = CreatePanel(rootPanel, new Vector2(0, 0.85f), new Vector2(1, 1), 0);
                float kpiWidth = 0.25f;
                fpsText = CreateKPI(kpiPanel, "FPS", 0, kpiWidth, out fpsIndicator);
                memoryText = CreateKPI(kpiPanel, "Memory", 1, kpiWidth, out _);
                pingText = CreateKPI(kpiPanel, "Ping", 2, kpiWidth, out _);
                errorText = CreateKPI(kpiPanel, "Errors", 3, kpiWidth, out errorIndicator);

                // Middle: Alert log
                alertLogPanel = CreatePanel(rootPanel, new Vector2(0.05f, 0.05f), new Vector2(0.95f, 0.8f), 1);
                var logTitle = CreateText(alertLogPanel, "Alert Log", 18, FontStyle.Bold, TextAnchor.UpperLeft);
                logTitle.rectTransform.anchorMin = new Vector2(0, 0.95f);
                logTitle.rectTransform.anchorMax = new Vector2(1, 1);
                logTitle.rectTransform.offsetMin = new Vector2(0, 0);
                logTitle.rectTransform.offsetMax = new Vector2(0, 0);
                for (int i = 0; i < maxLogEntries; i++)
                {
                    var entry = CreateText(alertLogPanel, "", 14, FontStyle.Normal, TextAnchor.UpperLeft);
                    entry.rectTransform.anchorMin = new Vector2(0, 0.9f - i * 0.09f);
                    entry.rectTransform.anchorMax = new Vector2(1, 0.98f - i * 0.09f);
                    entry.rectTransform.offsetMin = new Vector2(0, 0);
                    entry.rectTransform.offsetMax = Vector2.zero;
                    alertLogEntries.Add(entry);
                }

                // Thresholds display
                thresholdsText = CreateText(rootPanel, "", 14, FontStyle.Italic, TextAnchor.UpperLeft);
                thresholdsText.rectTransform.anchorMin = new Vector2(0.02f, 0.82f);
                thresholdsText.rectTransform.anchorMax = new Vector2(0.98f, 0.85f);
                thresholdsText.rectTransform.offsetMin = Vector2.zero;
                thresholdsText.rectTransform.offsetMax = Vector2.zero;

                // Add a placeholder for historical chart
                historicalChartObj = new GameObject("HistoricalFpsChart");
                historicalChartObj.transform.SetParent(rootPanel, false);
                var chartRect = historicalChartObj.AddComponent<RectTransform>();
                chartRect.anchorMin = new Vector2(0.05f, 0.15f);
                chartRect.anchorMax = new Vector2(0.95f, 0.75f);
                chartRect.offsetMin = Vector2.zero;
                chartRect.offsetMax = Vector2.zero;
                historicalFpsLine = historicalChartObj.AddComponent<LineRenderer>();
                historicalFpsLine.positionCount = 0;
                historicalFpsLine.material = new Material(Shader.Find("Sprites/Default"));
                historicalFpsLine.widthMultiplier = 2f;
                historicalFpsLine.startColor = green;
                historicalFpsLine.endColor = green;
                historicalChartObj.SetActive(false);

                // Threshold configuration panel
                thresholdPanel = CreatePanel(rootPanel, new Vector2(0.7f, 0.82f), new Vector2(0.98f, 0.98f), 2);
                var thresholdTitle = CreateText(thresholdPanel, "Thresholds", 14, FontStyle.Bold, TextAnchor.UpperLeft);
                thresholdTitle.rectTransform.anchorMin = new Vector2(0, 0.8f);
                thresholdTitle.rectTransform.anchorMax = new Vector2(1, 1);
                thresholdTitle.rectTransform.offsetMin = Vector2.zero;
                thresholdTitle.rectTransform.offsetMax = Vector2.zero;
                fpsWarningCore = CreateCoreField(thresholdPanel, "FPS Warning", 0.6f, 0.7f);
                fpsCriticalCore = CreateCoreField(thresholdPanel, "FPS Critical", 0.4f, 0.5f);
                memWarningCore = CreateCoreField(thresholdPanel, "Mem Warn", 0.2f, 0.3f);
                memCriticalCore = CreateCoreField(thresholdPanel, "Mem Crit", 0.0f, 0.1f);
                applyThresholdsButton = CreateButton(thresholdPanel, "Apply", 0.0f, 0.2f, OnApplyThresholdsClicked);
                testAlertButton = CreateButton(thresholdPanel, "Test Alert", 0.8f, 1.0f, OnTestAlertClicked);

                // Export controls
                exportCsvButton = CreateButton(rootPanel, "Export CSV", 0.98f, 1.0f, OnExportCsvClicked);
                exportPdfButton = CreateButton(rootPanel, "Export PDF", 0.95f, 0.98f, OnExportPdfClicked);
                var csvRect = exportCsvButton.GetComponent<RectTransform>();
                csvRect.anchorMin = new Vector2(0.8f, 0.95f);
                csvRect.anchorMax = new Vector2(0.9f, 1.0f);
                csvRect.offsetMin = Vector2.zero;
                csvRect.offsetMax = Vector2.zero;
                var pdfRect = exportPdfButton.GetComponent<RectTransform>();
                pdfRect.anchorMin = new Vector2(0.9f, 0.95f);
                pdfRect.anchorMax = new Vector2(1.0f, 1.0f);
                pdfRect.offsetMin = Vector2.zero;
                pdfRect.offsetMax = Vector2.zero;
            }
            catch (Exception ex)
            {
                VisualDM.Utilities.ErrorHandlingService.Instance.LogException(ex, "Failed to build Monitoring Dashboard UI.", "MonitoringDashboard.CreateUI");
                OnPanelError("Failed to build dashboard UI.", "MonitoringDashboard.CreateUI");
            }
        }

        private RectTransform CreatePanel(Transform parent, Vector2 anchorMin, Vector2 anchorMax, int siblingIndex)
        {
            var go = new GameObject("Panel");
            var rt = go.AddComponent<RectTransform>();
            rt.SetParent(parent, false);
            rt.anchorMin = anchorMin;
            rt.anchorMax = anchorMax;
            rt.offsetMin = Vector2.zero;
            rt.offsetMax = Vector2.zero;
            go.AddComponent<Image>().color = new Color(0.1f, 0.1f, 0.1f, 0.7f);
            go.transform.SetSiblingIndex(siblingIndex);
            return rt;
        }

        private Text CreateKPI(RectTransform parent, string label, int index, float widthFrac, out Image indicator)
        {
            var kpiPanel = CreatePanel(parent, new Vector2(index * widthFrac, 0), new Vector2((index + 1) * widthFrac, 1), index);
            indicator = new GameObject("Indicator").AddComponent<Image>();
            indicator.transform.SetParent(kpiPanel, false);
            indicator.rectTransform.anchorMin = new Vector2(0.05f, 0.2f);
            indicator.rectTransform.anchorMax = new Vector2(0.15f, 0.8f);
            indicator.rectTransform.offsetMin = Vector2.zero;
            indicator.rectTransform.offsetMax = Vector2.zero;
            indicator.color = green;
            var labelText = CreateText(kpiPanel, label, 16, FontStyle.Bold, TextAnchor.UpperLeft);
            labelText.rectTransform.anchorMin = new Vector2(0.2f, 0.6f);
            labelText.rectTransform.anchorMax = new Vector2(1, 1);
            labelText.rectTransform.offsetMin = Vector2.zero;
            labelText.rectTransform.offsetMax = Vector2.zero;
            var valueText = CreateText(kpiPanel, "", 20, FontStyle.Bold, TextAnchor.LowerLeft);
            valueText.rectTransform.anchorMin = new Vector2(0.2f, 0);
            valueText.rectTransform.anchorMax = new Vector2(1, 0.6f);
            valueText.rectTransform.offsetMin = Vector2.zero;
            valueText.rectTransform.offsetMax = Vector2.zero;
            selectables.Add(valueText);
            return valueText;
        }

        private Text CreateText(Transform parent, string text, int fontSize, FontStyle style, TextAnchor anchor)
        {
            var go = new GameObject("Text");
            var txt = go.AddComponent<Text>();
            txt.text = text;
            txt.font = Resources.GetBuiltinResource<Font>("Arial.ttf");
            txt.fontSize = fontSize;
            txt.fontStyle = style;
            txt.alignment = anchor;
            txt.color = Color.white;
            txt.rectTransform.SetParent(parent, false);
            txt.rectTransform.anchorMin = new Vector2(0, 0);
            txt.rectTransform.anchorMax = new Vector2(1, 1);
            txt.rectTransform.offsetMin = Vector2.zero;
            txt.rectTransform.offsetMax = Vector2.zero;
            return txt;
        }

        private CoreField CreateCoreField(Transform parent, string placeholder, float anchorMinY, float anchorMaxY)
        {
            var go = new GameObject(placeholder + "Core");
            var input = go.AddComponent<CoreField>();
            var text = go.AddComponent<Text>();
            text.font = Resources.GetBuiltinResource<Font>("Arial.ttf");
            text.fontSize = 12;
            text.color = Color.black;
            input.textComponent = text;
            var placeholderObj = new GameObject("Placeholder");
            var placeholderText = placeholderObj.AddComponent<Text>();
            placeholderText.text = placeholder;
            placeholderText.font = Resources.GetBuiltinResource<Font>("Arial.ttf");
            placeholderText.fontSize = 12;
            placeholderText.color = Color.gray;
            input.placeholder = placeholderText;
            placeholderObj.transform.SetParent(go.transform, false);
            go.transform.SetParent(parent, false);
            var rt = go.GetComponent<RectTransform>();
            rt.anchorMin = new Vector2(0, anchorMinY);
            rt.anchorMax = new Vector2(0.7f, anchorMaxY);
            rt.offsetMin = Vector2.zero;
            rt.offsetMax = Vector2.zero;
            return input;
        }

        private Button CreateButton(Transform parent, string label, float anchorMinY, float anchorMaxY, Action onClick)
        {
            var go = new GameObject(label + "Button");
            var btn = go.AddComponent<Button>();
            var txt = go.AddComponent<Text>();
            txt.text = label;
            txt.font = Resources.GetBuiltinResource<Font>("Arial.ttf");
            txt.fontSize = 12;
            txt.color = Color.white;
            btn.targetGraphic = txt;
            btn.onClick.AddListener(() => onClick());
            go.transform.SetParent(parent, false);
            var rt = go.GetComponent<RectTransform>();
            rt.anchorMin = new Vector2(0.72f, anchorMinY);
            rt.anchorMax = new Vector2(1, anchorMaxY);
            rt.offsetMin = Vector2.zero;
            rt.offsetMax = Vector2.zero;
            return btn;
        }

        private void UpdateMetrics()
        {
            try
            {
                var metrics = MonitoringManager.Instance.GetRecentMetrics();
                float fps = GetLatestMetric(metrics, "fps");
                float memory = GetLatestMetric(metrics, "memory_mb");
                float ping = GetLatestMetric(metrics, "ping_ms");
                float errors = GetLatestMetric(metrics, "error_count");
                fpsText.text = $"{fps:F1}";
                memoryText.text = $"{memory:F1} MB";
                pingText.text = ping >= 0 ? $"{ping:F0} ms" : "-";
                errorText.text = $"{errors:F0}";
                fpsIndicator.color = fps < 30 ? red : (fps < 50 ? yellow : green);
                errorIndicator.color = errors > 0 ? (errors > 5 ? red : yellow) : green;

                // Update thresholds display
                var thresholds = MonitoringManager.Instance.CurrentAlertThresholds;
                thresholdsText.text = $"Thresholds: FPS < {thresholds.Fps}, Mem > {thresholds.MemoryMB}MB, Ping > {thresholds.PingMs}ms, Errors >= {thresholds.ErrorCount}";
            }
            catch (Exception ex)
            {
                VisualDM.Utilities.ErrorHandlingService.Instance.LogException(ex, "Failed to update dashboard metrics.", "MonitoringDashboard.UpdateMetrics");
                OnPanelError("Metrics update failed.", "MonitoringDashboard.UpdateMetrics");
            }
        }

        private float GetLatestMetric(List<MonitoringManager.Metric> metrics, string name)
        {
            for (int i = metrics.Count - 1; i >= 0; i--)
                if (metrics[i].Name == name)
                    return metrics[i].Value;
            return 0f;
        }

        private void OnAlertReceived(string alertType, string message)
        {
            try
            {
                for (int i = maxLogEntries - 1; i > 0; i--)
                    alertLogEntries[i].text = alertLogEntries[i - 1].text;
                alertLogEntries[0].text = $"[{DateTime.Now:HH:mm:ss}] {alertType}: {message}";
            }
            catch (Exception ex)
            {
                VisualDM.Utilities.ErrorHandlingService.Instance.LogException(ex, "Failed to handle alert.", "MonitoringDashboard.OnAlertReceived");
                OnPanelError("Alert handling failed.", "MonitoringDashboard.OnAlertReceived");
            }
        }

        private void HandleKeyboardNavigation()
        {
            if (selectables.Count == 0) return;
            if (Core.GetKeyDown(KeyCode.Tab))
            {
                selectedIndex = (selectedIndex + 1) % selectables.Count;
                selectables[selectedIndex].color = yellow;
                for (int i = 0; i < selectables.Count; i++)
                    if (i != selectedIndex)
                        selectables[i].color = Color.white;
            }
            if (Core.GetKeyDown(KeyCode.UpArrow))
            {
                selectedIndex = (selectedIndex - 1 + selectables.Count) % selectables.Count;
                selectables[selectedIndex].color = yellow;
                for (int i = 0; i < selectables.Count; i++)
                    if (i != selectedIndex)
                        selectables[i].color = Color.white;
            }
        }

        public override void Initialize(params object[] args)
        {
            try
            {
                // Existing initialization logic
            }
            catch (Exception ex)
            {
                VisualDM.Utilities.ErrorHandlingService.Instance.LogException(ex, "Failed to initialize Monitoring Dashboard.", "MonitoringDashboard.Initialize");
                OnPanelError("Failed to initialize dashboard. Please try again.", "MonitoringDashboard.Initialize");
            }
        }

        private void OnPanelError(string message, string context)
        {
            // Implement user-friendly error handling logic here
            Debug.LogError($"Error in {context}: {message}");
        }

        public void SwitchToRealTimeView()
        {
            showRealTime = true;
            RecordAuditLog("SwitchView", "Switched to real-time view");
        }
        public void SwitchToHistoricalView(string startTime, string endTime)
        {
            showRealTime = false;
            historicalStartTime = startTime;
            historicalEndTime = endTime;
            apiClient.GetHistoricalMetrics(startTime, endTime, currentPage, pageSize, OnHistoricalMetricsReceived, OnHistoricalMetricsError);
            RecordAuditLog("SwitchView", $"Switched to historical view: {startTime} - {endTime}");
        }
        private void OnRealTimeMetricsReceivedJson(string json)
        {
            var metricsJson = JObject.Parse(json);
            OnRealTimeMetricsReceived(metricsJson);
        }
        private void OnRealTimeMetricsReceived(JObject metricsJson)
        {
            // Parse and update UI with real-time metrics
            var metrics = metricsJson["metrics"];
            if (metrics != null)
            {
                float fps = metrics["fps"]?.Value<float>() ?? 0f;
                float memory = metrics["memory_mb"]?.Value<float>() ?? 0f;
                float ping = metrics["ping_ms"]?.Value<float>() ?? -1f;
                float errors = metrics["error_count"]?.Value<float>() ?? 0f;
                fpsText.text = $"{fps:F1}";
                memoryText.text = $"{memory:F1} MB";
                pingText.text = ping >= 0 ? $"{ping:F0} ms" : "-";
                errorText.text = $"{errors:F0}";
                fpsIndicator.color = fps < 30 ? red : (fps < 50 ? yellow : green);
                errorIndicator.color = errors > 0 ? (errors > 5 ? red : yellow) : green;
            }
        }
        private void OnHistoricalMetricsReceived(JObject metricsJson)
        {
            // TODO: Parse and store historical metrics, then update UI
            historicalMetrics.Clear();
            var arr = metricsJson["data"]?["metrics"] as JArray;
            if (arr != null)
            {
                foreach (var item in arr)
                    historicalMetrics.Add(item as JObject);
            }
            UpdateHistoricalMetricsUI();
        }
        private void OnHistoricalMetricsError(string error)
        {
            OnPanelError($"Failed to load historical metrics: {error}", "MonitoringDashboard.HistoricalMetrics");
        }
        private void UpdateHistoricalMetricsUI()
        {
            // Show/hide chart
            if (historicalMetrics.Count == 0)
            {
                historicalChartObj.SetActive(false);
                return;
            }
            historicalChartObj.SetActive(true);
            // Draw a simple line chart for FPS over time
            List<float> fpsValues = new List<float>();
            foreach (var m in historicalMetrics)
            {
                var metrics = m["metrics"];
                if (metrics != null)
                {
                    float fps = metrics["fps"]?.Value<float>() ?? 0f;
                    fpsValues.Add(fps);
                }
            }
            int n = fpsValues.Count;
            historicalFpsLine.positionCount = n;
            float xStep = 600f / Mathf.Max(1, n - 1);
            for (int i = 0; i < n; i++)
            {
                historicalFpsLine.SetPosition(i, new Vector3(i * xStep, fpsValues[i] * 4f, 0));
            }
        }

        private void OnApplyThresholdsClicked()
        {
            float fpsWarn = float.TryParse(fpsWarningCore.text, out var fw) ? fw : 30f;
            float fpsCrit = float.TryParse(fpsCriticalCore.text, out var fc) ? fc : 15f;
            float memWarn = float.TryParse(memWarningCore.text, out var mw) ? mw : 2000f;
            float memCrit = float.TryParse(memCriticalCore.text, out var mc) ? mc : 4000f;
            MonitoringManager.Instance.SetAlertThresholds(fpsWarn, fpsCrit, memWarn, memCrit);
        }

        private void OnTestAlertClicked()
        {
            MonitoringManager.Instance.TriggerTestAlert();
        }

        private void OnExportCsvClicked()
        {
            // TODO: Implement CSV export logic (e.g., call backend or write file)
            Debug.Log("Export CSV clicked");
            RecordAuditLog("Export", "Exported CSV");
        }

        private void OnExportPdfClicked()
        {
            // TODO: Implement PDF export logic (e.g., call backend or write file)
            Debug.Log("Export PDF clicked");
            RecordAuditLog("Export", "Exported PDF");
        }

        private void RecordAuditLog(string action, string description)
        {
            // Implement audit logging logic here
            Debug.Log($"Audit: {action} - {description}");
        }

        private void ShowLoginPanel()
        {
            // Implement login panel logic here
            Debug.Log("Login panel should be shown here");
        }

        // --- Documentation and Automated Tests ---
        private void GenerateUserDocumentation()
        {
            // TODO: Generate user documentation for dashboard features and workflows
            Debug.Log("GenerateUserDocumentation: Not implemented");
        }

        private void RunAutomatedTests()
        {
            // TODO: Trigger automated tests (Unity Test Framework, backend tests, etc.)
            Debug.Log("RunAutomatedTests: Not implemented");
        }
    }
}