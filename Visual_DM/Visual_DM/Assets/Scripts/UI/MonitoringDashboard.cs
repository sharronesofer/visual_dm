using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using VisualDM.Core;

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

        void Start()
        {
            CreateUI();
            MonitoringManager.Instance.SubscribeToAlerts(OnAlertReceived);
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
                UpdateMetrics();
                updateTimer = 0f;
            }
            HandleKeyboardNavigation();
        }

        private void CreateUI()
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

        private void UpdateMetrics()
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

        private float GetLatestMetric(List<MonitoringManager.Metric> metrics, string name)
        {
            for (int i = metrics.Count - 1; i >= 0; i--)
                if (metrics[i].Name == name)
                    return metrics[i].Value;
            return 0f;
        }

        private void OnAlertReceived(string alertType, string message)
        {
            for (int i = maxLogEntries - 1; i > 0; i--)
                alertLogEntries[i].text = alertLogEntries[i - 1].text;
            alertLogEntries[0].text = $"[{DateTime.Now:HH:mm:ss}] {alertType}: {message}";
        }

        private void HandleKeyboardNavigation()
        {
            if (selectables.Count == 0) return;
            if (Input.GetKeyDown(KeyCode.Tab))
            {
                selectedIndex = (selectedIndex + 1) % selectables.Count;
                selectables[selectedIndex].color = yellow;
                for (int i = 0; i < selectables.Count; i++)
                    if (i != selectedIndex)
                        selectables[i].color = Color.white;
            }
            if (Input.GetKeyDown(KeyCode.UpArrow))
            {
                selectedIndex = (selectedIndex - 1 + selectables.Count) % selectables.Count;
                selectables[selectedIndex].color = yellow;
                for (int i = 0; i < selectables.Count; i++)
                    if (i != selectedIndex)
                        selectables[i].color = Color.white;
            }
        }
    }
} 