using System;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using UnityEngine.UI;

namespace VDM.Motifs
{
    /// <summary>
    /// Runtime motif dashboard for admin/debug visualization and control.
    /// </summary>
    public class MotifDashboardUI : MonoBehaviour
    {
        private Canvas _canvas;
        private RectTransform _panel;
        private Dropdown _scopeFilter, _categoryFilter;
        private Slider _intensityFilter;
        private VerticalLayoutGroup _motifListLayout;
        private Dictionary<int, Motif> _motifMap = new();
        private List<Motif> _motifs = new();
        private MotifCacheManager _cache;

        public void Initialize(MotifCacheManager cache)
        {
            _cache = cache;
            CreateUI();
            RefreshMotifList();
        }

        private void CreateUI()
        {
            // Create Canvas
            _canvas = new GameObject("MotifDashboardCanvas").AddComponent<Canvas>();
            _canvas.renderMode = RenderMode.ScreenSpaceOverlay;
            _canvas.gameObject.AddComponent<CanvasScaler>().uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
            _canvas.gameObject.AddComponent<GraphicRaycaster>();
            DontDestroyOnLoad(_canvas.gameObject);

            // Create main panel
            var panelGO = new GameObject("MotifPanel");
            _panel = panelGO.AddComponent<RectTransform>();
            panelGO.AddComponent<Image>().color = new Color(0,0,0,0.7f);
            _panel.SetParent(_canvas.transform, false);
            _panel.anchorMin = new Vector2(0, 0);
            _panel.anchorMax = new Vector2(0.3f, 1);
            _panel.offsetMin = Vector2.zero;
            _panel.offsetMax = Vector2.zero;

            // Filters
            _scopeFilter = CreateDropdown("Scope", Enum.GetNames(typeof(MotifScope)), _panel, 0);
            _categoryFilter = CreateDropdown("Category", Enum.GetNames(typeof(MotifCategory)), _panel, 1);
            _intensityFilter = CreateSlider("Intensity", 0, 10, _panel, 2);

            // Motif list
            var listGO = new GameObject("MotifList");
            _motifListLayout = listGO.AddComponent<VerticalLayoutGroup>();
            var listRect = listGO.GetComponent<RectTransform>();
            listRect.SetParent(_panel, false);
            listRect.anchorMin = new Vector2(0, 0.2f);
            listRect.anchorMax = new Vector2(1, 1);
            listRect.offsetMin = Vector2.zero;
            listRect.offsetMax = Vector2.zero;
        }

        private Dropdown CreateDropdown(string label, string[] options, RectTransform parent, int order)
        {
            var go = new GameObject(label+"Dropdown");
            var dropdown = go.AddComponent<Dropdown>();
            dropdown.options = options.Select(o => new Dropdown.OptionData(o)).ToList();
            var rect = go.GetComponent<RectTransform>();
            rect.SetParent(parent, false);
            rect.anchorMin = new Vector2(0, 1 - 0.05f * (order+1));
            rect.anchorMax = new Vector2(1, 1 - 0.05f * order);
            rect.offsetMin = Vector2.zero;
            rect.offsetMax = Vector2.zero;
            dropdown.onValueChanged.AddListener(_ => RefreshMotifList());
            return dropdown;
        }

        private Slider CreateSlider(string label, float min, float max, RectTransform parent, int order)
        {
            var go = new GameObject(label+"Slider");
            var slider = go.AddComponent<Slider>();
            slider.minValue = min;
            slider.maxValue = max;
            var rect = go.GetComponent<RectTransform>();
            rect.SetParent(parent, false);
            rect.anchorMin = new Vector2(0, 1 - 0.05f * (order+3));
            rect.anchorMax = new Vector2(1, 1 - 0.05f * (order+2));
            rect.offsetMin = Vector2.zero;
            rect.offsetMax = Vector2.zero;
            slider.onValueChanged.AddListener(_ => RefreshMotifList());
            return slider;
        }

        private async void RefreshMotifList()
        {
            // Fetch motifs (could add async loading indicator)
            _motifs = await _cache.GetMotifsAsync();
            // Filter
            var scope = (MotifScope)_scopeFilter.value;
            var category = (MotifCategory)_categoryFilter.value;
            float intensity = _intensityFilter.value;
            var filtered = _motifs.Where(m => m.Scope == scope && m.Category == category && m.Intensity >= intensity).ToList();
            // Clear old
            foreach (Transform child in _motifListLayout.transform)
                GameObject.Destroy(child.gameObject);
            // Add motif entries
            foreach (var motif in filtered)
                AddMotifEntry(motif);
        }

        private void AddMotifEntry(Motif motif)
        {
            var go = new GameObject($"Motif_{motif.Id}");
            var text = go.AddComponent<Text>();
            text.text = $"{motif.Name} [{motif.Intensity}]";
            text.color = Color.white;
            go.transform.SetParent(_motifListLayout.transform, false);
            // Add manual adjustment tools (sliders/buttons)
            // TODO: Add tree view, heat map overlay, and backend sync
        }
    }
} 