using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

namespace VisualDM.Simulation
{
    public class SimulationDashboard : MonoBehaviour
    {
        private RectTransform panel;
        private Dropdown testRunDropdown;
        private Text summaryText;
        private CoreField searchCore;
        private Button filterButton;
        private RectTransform resultsList;
        private List<SimulationReport> reports = new List<SimulationReport>();

        void Start()
        {
            // Create UI elements at runtime
            var canvas = new GameObject("DashboardCanvas").AddComponent<Canvas>();
            canvas.renderMode = RenderMode.ScreenSpaceOverlay;
            panel = new GameObject("DashboardPanel").AddComponent<RectTransform>();
            panel.SetParent(canvas.transform);
            panel.sizeDelta = new Vector2(600, 800);

            // Test run dropdown
            testRunDropdown = CreateDropdown(panel, "Test Runs", new List<string> { "None" }, new Vector2(0, 350));
            testRunDropdown.onValueChanged.AddListener(OnTestRunSelected);
            // Search input
            searchCore = CreateCoreField(panel, "Search", "", new Vector2(0, 300));
            // Filter button
            filterButton = CreateButton(panel, "Filter", new Vector2(100, 300), OnFilterClicked);
            // Summary text
            summaryText = CreateText(panel, "Summary: No data", new Vector2(0, 250));
            // Results list
            resultsList = new GameObject("ResultsList").AddComponent<RectTransform>();
            resultsList.SetParent(panel);
            resultsList.sizeDelta = new Vector2(550, 400);
            resultsList.anchoredPosition = new Vector2(0, 0);
        }

        public void AddReport(SimulationReport report)
        {
            reports.Add(report);
            testRunDropdown.options.Add(new Dropdown.OptionData(report.ReportName));
        }

        private Dropdown CreateDropdown(Transform parent, string label, List<string> options, Vector2 pos)
        {
            var go = new GameObject(label + "Dropdown");
            go.transform.SetParent(parent);
            var dropdown = go.AddComponent<Dropdown>();
            dropdown.options = options.ConvertAll(o => new Dropdown.OptionData(o));
            go.GetComponent<RectTransform>().anchoredPosition = pos;
            return dropdown;
        }

        private CoreField CreateCoreField(Transform parent, string label, string defaultValue, Vector2 pos)
        {
            var go = new GameObject(label + "Core");
            go.transform.SetParent(parent);
            var input = go.AddComponent<CoreField>();
            input.text = defaultValue;
            go.GetComponent<RectTransform>().anchoredPosition = pos;
            return input;
        }

        private Button CreateButton(Transform parent, string label, Vector2 pos, UnityEngine.Events.UnityAction onClick)
        {
            var go = new GameObject(label + "Button");
            go.transform.SetParent(parent);
            var button = go.AddComponent<Button>();
            button.onClick.AddListener(onClick);
            go.GetComponent<RectTransform>().anchoredPosition = pos;
            var text = CreateText(go.transform, label, Vector2.zero);
            return button;
        }

        private Text CreateText(Transform parent, string content, Vector2 pos)
        {
            var go = new GameObject("Text");
            go.transform.SetParent(parent);
            var text = go.AddComponent<Text>();
            text.text = content;
            text.font = Resources.GetBuiltinResource<Font>("Arial.ttf");
            go.GetComponent<RectTransform>().anchoredPosition = pos;
            return text;
        }

        private void OnTestRunSelected(int index)
        {
            if (index <= 0 || index > reports.Count) return;
            var report = reports[index - 1];
            summaryText.text = $"Summary: {report.ReportName}\nMean DPS: {report.SummaryStats.GetValueOrDefault("MeanDPS", 0):F2}\nOutliers: {string.Join(", ", report.Outliers)}";
            // Clear and repopulate results list
            foreach (Transform child in resultsList) Destroy(child.gameObject);
            foreach (var tc in report.TestCases)
            {
                var t = CreateText(resultsList, $"{tc.Name}", Vector2.zero);
                // Add more details as needed
            }
        }

        private void OnFilterClicked()
        {
            // Example: filter by search input
            string query = searchCore.text.ToLower();
            foreach (Transform child in resultsList)
            {
                var text = child.GetComponent<Text>();
                if (text != null)
                    child.gameObject.SetActive(string.IsNullOrEmpty(query) || text.text.ToLower().Contains(query));
            }
        }
    }
} 