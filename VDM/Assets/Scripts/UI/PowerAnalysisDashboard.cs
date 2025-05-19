using System;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using UnityEngine.UI;
using VisualDM.Systems.Utilities;
using VisualDM.Timeline.Models;

namespace VisualDM.UI
{
    public class PowerAnalysisDashboard : MonoBehaviour
    {
        // Services
        private FeatDatabaseService _dbService;
        private FeatPowerCalculator _calculator;
        private FeatAnalysisEngine _analysisEngine;
        private FeatAnalysisEngine.FeatAnalysisReport _lastReport;

        // UI Elements
        private RectTransform _rootPanel;
        private Button _analyzeButton;
        private Button _exportButton;
        private Dropdown _categoryDropdown;
        private CoreField _searchField;
        private Dropdown _sortDropdown;
        private Text _summaryText;
        private RectTransform _histogramPanel;
        private RectTransform _flaggedListPanel;
        private RectTransform _featDetailPanel;

        // State
        private List<Feat> _allFeats;
        private List<FeatAnalysisEngine.FeatAnalysisResult> _filteredFlagged;
        private string _selectedCategory = "All";
        private string _searchQuery = "";
        private string _sortMode = "Score";
        private string _selectedFeatId = null;

        public override void Initialize(params object[] args)
        {
            try
            {
                // Initialize services
                _dbService = new FeatDatabaseService(Application.persistentDataPath + "/feats.json");
                _calculator = new FeatPowerCalculator();
                _calculator.RegisterModule(new GenericScoringModule("EffectMagnitude", "EffectValue"));
                _calculator.RegisterModule(new GenericScoringModule("ResourceCost", "ResourceCost"));
                _calculator.RegisterModule(new GenericScoringModule("Cooldown", "Cooldown"));
                _calculator.RegisterModule(new GenericScoringModule("Utility", "Utility"));
                _calculator.RegisterModule(new GenericScoringModule("Synergy", "Synergy"));
                _analysisEngine = new FeatAnalysisEngine(_calculator);
                _allFeats = _dbService.GetAllFeats();
                BuildUI();
            }
            catch (Exception ex)
            {
                VisualDM.Utilities.ErrorHandlingService.Instance.LogException(ex, "Failed to initialize Power Analysis Dashboard.", "PowerAnalysisDashboard.Initialize");
                OnPanelError("Failed to initialize dashboard. Please try again.", "PowerAnalysisDashboard.Initialize");
            }
        }

        void BuildUI()
        {
            try
            {
                // Root panel
                _rootPanel = new GameObject("PowerAnalysisDashboard").AddComponent<RectTransform>();
                _rootPanel.SetParent(this.transform, false);
                _rootPanel.sizeDelta = new Vector2(1200, 800);
                _rootPanel.anchorMin = Vector2.zero;
                _rootPanel.anchorMax = Vector2.one;
                _rootPanel.pivot = new Vector2(0.5f, 0.5f);

                // Analyze button
                _analyzeButton = CreateButton(_rootPanel, "Run Analysis", new Vector2(10, -10), AnalyzeAllFeats);
                // Export button
                _exportButton = CreateButton(_rootPanel, "Export JSON", new Vector2(150, -10), ExportJson);
                // Category dropdown
                _categoryDropdown = CreateDropdown(_rootPanel, new Vector2(300, -10), new List<string> { "All" }.Concat(Enum.GetNames(typeof(FeatCategory))).ToList(), OnCategoryChanged);
                // Search field
                _searchField = CreateCoreField(_rootPanel, new Vector2(500, -10), OnSearchChanged);
                // Sort dropdown
                _sortDropdown = CreateDropdown(_rootPanel, new Vector2(800, -10), new List<string> { "Score", "Name", "Category" }, OnSortChanged);
                // Summary text
                _summaryText = CreateText(_rootPanel, "Summary", new Vector2(10, -50), 600);
                // Histogram panel
                _histogramPanel = CreatePanel(_rootPanel, new Vector2(10, -100), new Vector2(600, 300));
                // Flagged list panel
                _flaggedListPanel = CreatePanel(_rootPanel, new Vector2(650, -100), new Vector2(500, 300));
                // Feat detail panel
                _featDetailPanel = CreatePanel(_rootPanel, new Vector2(10, -420), new Vector2(1140, 350));
            }
            catch (Exception ex)
            {
                VisualDM.Utilities.ErrorHandlingService.Instance.LogException(ex, "Failed to build Power Analysis Dashboard UI.", "PowerAnalysisDashboard.BuildUI");
                OnPanelError("Failed to build dashboard UI.", "PowerAnalysisDashboard.BuildUI");
            }
        }

        void AnalyzeAllFeats()
        {
            try
            {
                _lastReport = _analysisEngine.Analyze(_allFeats);
                UpdateSummary();
                UpdateHistogram();
                UpdateFlaggedList();
                _selectedFeatId = null;
                UpdateFeatDetail();
            }
            catch (Exception ex)
            {
                VisualDM.Utilities.ErrorHandlingService.Instance.LogException(ex, "Failed to analyze feats.", "PowerAnalysisDashboard.AnalyzeAllFeats");
                OnPanelError("Analysis failed. Please try again.", "PowerAnalysisDashboard.AnalyzeAllFeats");
            }
        }

        void UpdateSummary()
        {
            if (_lastReport == null) { _summaryText.text = "No analysis run."; return; }
            _summaryText.text = $"Mean: {_lastReport.Mean:F2}, StdDev: {_lastReport.StdDev:F2}, Flagged: {_lastReport.FlaggedFeats.Count}";
        }

        void UpdateHistogram()
        {
            // Simple bar chart: power score distribution
            foreach (Transform child in _histogramPanel) Destroy(child.gameObject);
            if (_lastReport == null) return;
            var scores = _lastReport.AllScores.Values.ToList();
            if (scores.Count == 0) return;
            int bins = 20;
            float min = scores.Min(), max = scores.Max();
            float binSize = (max - min) / bins;
            int[] counts = new int[bins];
            foreach (var s in scores)
            {
                int idx = Mathf.Clamp((int)((s - min) / binSize), 0, bins - 1);
                counts[idx]++;
            }
            float barWidth = _histogramPanel.rect.width / bins;
            float maxCount = counts.Max();
            for (int i = 0; i < bins; i++)
            {
                var bar = CreatePanel(_histogramPanel, new Vector2(i * barWidth, 0), new Vector2(barWidth - 2, _histogramPanel.rect.height * (counts[i] / (float)maxCount)));
                bar.GetComponent<Image>().color = Color.cyan;
            }
        }

        void UpdateFlaggedList()
        {
            foreach (Transform child in _flaggedListPanel) Destroy(child.gameObject);
            if (_lastReport == null) return;
            _filteredFlagged = _lastReport.FlaggedFeats
                .Where(f => (_selectedCategory == "All" || f.ImbalanceType == _selectedCategory || _allFeats.FirstOrDefault(x => x.Id == f.FeatId)?.Category.ToString() == _selectedCategory)
                    && (string.IsNullOrEmpty(_searchQuery) || (f.FeatName?.IndexOf(_searchQuery, StringComparison.OrdinalIgnoreCase) >= 0)))
                .OrderBy(f => _sortMode == "Score" ? -f.PowerScore : (_sortMode == "Name" ? f.FeatName : f.ImbalanceType))
                .ToList();
            float y = 0;
            foreach (var flagged in _filteredFlagged)
            {
                var btn = CreateButton(_flaggedListPanel, $"{flagged.FeatName} [{flagged.ImbalanceType}] ({flagged.PowerScore:F2})", new Vector2(0, y), () => { _selectedFeatId = flagged.FeatId; UpdateFeatDetail(); });
                btn.GetComponent<Image>().color = flagged.ImbalanceType == "Overpowered" ? Color.red : Color.yellow;
                y -= 30;
            }
        }

        void UpdateFeatDetail()
        {
            foreach (Transform child in _featDetailPanel) Destroy(child.gameObject);
            if (_selectedFeatId == null) return;
            var feat = _allFeats.FirstOrDefault(f => f.Id == _selectedFeatId);
            var flagged = _lastReport?.FlaggedFeats.FirstOrDefault(f => f.FeatId == _selectedFeatId);
            if (feat == null) return;
            float y = 0;
            CreateText(_featDetailPanel, $"Name: {feat.Name}", new Vector2(0, y), 400); y -= 30;
            CreateText(_featDetailPanel, $"Category: {feat.Category}", new Vector2(0, y), 400); y -= 30;
            CreateText(_featDetailPanel, $"Description: {feat.Description}", new Vector2(0, y), 800); y -= 30;
            CreateText(_featDetailPanel, $"Metadata: {string.Join(", ", feat.Metadata.Select(kv => kv.Key + ": " + kv.Value))}", new Vector2(0, y), 1000); y -= 30;
            if (flagged != null)
            {
                CreateText(_featDetailPanel, $"Power Score: {flagged.PowerScore:F2}", new Vector2(0, y), 400); y -= 30;
                CreateText(_featDetailPanel, $"Imbalance: {flagged.ImbalanceType}", new Vector2(0, y), 400); y -= 30;
                CreateText(_featDetailPanel, $"Reasoning: {flagged.Reasoning}", new Vector2(0, y), 1000); y -= 30;
                CreateText(_featDetailPanel, $"Suggestion: {flagged.Suggestion}", new Vector2(0, y), 1000); y -= 30;
            }
        }

        void ExportJson()
        {
            try
            {
                if (_lastReport == null) return;
                var json = _analysisEngine.GenerateJsonReport(_lastReport);
                var path = Application.persistentDataPath + "/feat_analysis_report.json";
                System.IO.File.WriteAllText(path, json);
                Debug.Log($"Exported analysis report to {path}");
            }
            catch (Exception ex)
            {
                VisualDM.Utilities.ErrorHandlingService.Instance.LogException(ex, "Failed to export analysis as JSON.", "PowerAnalysisDashboard.ExportJson");
                OnPanelError("Export failed. Please try again.", "PowerAnalysisDashboard.ExportJson");
            }
        }

        void OnCategoryChanged(int idx)
        {
            try
            {
                _selectedCategory = _categoryDropdown.options[idx].text;
                UpdateFlaggedList();
            }
            catch (Exception ex)
            {
                VisualDM.Utilities.ErrorHandlingService.Instance.LogException(ex, "Failed to change category.", "PowerAnalysisDashboard.OnCategoryChanged");
                OnPanelError("Category change failed.", "PowerAnalysisDashboard.OnCategoryChanged");
            }
        }
        void OnSearchChanged(string value)
        {
            try
            {
                _searchQuery = value;
                UpdateFlaggedList();
            }
            catch (Exception ex)
            {
                VisualDM.Utilities.ErrorHandlingService.Instance.LogException(ex, "Failed to update search query.", "PowerAnalysisDashboard.OnSearchChanged");
                OnPanelError("Search update failed.", "PowerAnalysisDashboard.OnSearchChanged");
            }
        }
        void OnSortChanged(int idx)
        {
            try
            {
                _sortMode = _sortDropdown.options[idx].text;
                UpdateFlaggedList();
            }
            catch (Exception ex)
            {
                VisualDM.Utilities.ErrorHandlingService.Instance.LogException(ex, "Failed to change sort mode.", "PowerAnalysisDashboard.OnSortChanged");
                OnPanelError("Sort change failed.", "PowerAnalysisDashboard.OnSortChanged");
            }
        }

        // --- UI Helpers ---
        Button CreateButton(Transform parent, string text, Vector2 pos, Action onClick)
        {
            var go = new GameObject("Button");
            go.transform.SetParent(parent, false);
            var rt = go.AddComponent<RectTransform>();
            rt.anchoredPosition = pos;
            rt.sizeDelta = new Vector2(130, 28);
            var img = go.AddComponent<Image>();
            img.color = Color.gray;
            var btn = go.AddComponent<Button>();
            btn.onClick.AddListener(() => onClick());
            var txt = CreateText(go.transform, text, Vector2.zero, 120);
            txt.alignment = TextAnchor.MiddleCenter;
            return btn;
        }
        Dropdown CreateDropdown(Transform parent, Vector2 pos, List<string> options, Action<int> onChanged)
        {
            var go = new GameObject("Dropdown");
            go.transform.SetParent(parent, false);
            var rt = go.AddComponent<RectTransform>();
            rt.anchoredPosition = pos;
            rt.sizeDelta = new Vector2(180, 28);
            var dd = go.AddComponent<Dropdown>();
            dd.options = options.Select(o => new Dropdown.OptionData(o)).ToList();
            dd.onValueChanged.AddListener(onChanged);
            return dd;
        }
        CoreField CreateCoreField(Transform parent, Vector2 pos, Action<string> onChanged)
        {
            var go = new GameObject("CoreField");
            go.transform.SetParent(parent, false);
            var rt = go.AddComponent<RectTransform>();
            rt.anchoredPosition = pos;
            rt.sizeDelta = new Vector2(250, 28);
            var input = go.AddComponent<CoreField>();
            input.onValueChanged.AddListener(onChanged);
            return input;
        }
        Text CreateText(Transform parent, string text, Vector2 pos, float width)
        {
            var go = new GameObject("Text");
            go.transform.SetParent(parent, false);
            var rt = go.AddComponent<RectTransform>();
            rt.anchoredPosition = pos;
            rt.sizeDelta = new Vector2(width, 28);
            var txt = go.AddComponent<Text>();
            txt.text = text;
            txt.font = Resources.GetBuiltinResource<Font>("Arial.ttf");
            txt.fontSize = 16;
            txt.color = Color.white;
            txt.alignment = TextAnchor.MiddleLeft;
            return txt;
        }
        RectTransform CreatePanel(Transform parent, Vector2 pos, Vector2 size)
        {
            var go = new GameObject("Panel");
            go.transform.SetParent(parent, false);
            var rt = go.AddComponent<RectTransform>();
            rt.anchoredPosition = pos;
            rt.sizeDelta = size;
            var img = go.AddComponent<Image>();
            img.color = new Color(0.1f, 0.1f, 0.1f, 0.7f);
            return rt;
        }
    }
} 