using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using VisualDM.World;
using VisualDM.Systems.Economy;

namespace VisualDM.UI
{
    public class EconomyDashboardPanel : MonoBehaviour
    {
        private RectTransform _rootPanel;
        private Dropdown _regionDropdown;
        private Text _marketSummaryText;
        private RectTransform _priceTrendPanel;
        private RectTransform _tradePanel;
        private Button _tradeButton;
        private InputField _tradeAmountField;
        private Dropdown _resourceDropdown;
        private EconomySystem _economySystem;
        private string _selectedRegion;
        private string _selectedResource;

        public void Initialize(EconomySystem economySystem)
        {
            _economySystem = economySystem;
            BuildUI();
            UpdateRegionDropdown();
        }

        void BuildUI()
        {
            _rootPanel = new GameObject("EconomyDashboardPanel").AddComponent<RectTransform>();
            _rootPanel.SetParent(this.transform, false);
            _rootPanel.sizeDelta = new Vector2(900, 600);
            _rootPanel.anchorMin = Vector2.zero;
            _rootPanel.anchorMax = Vector2.one;
            _rootPanel.pivot = new Vector2(0.5f, 0.5f);

            _regionDropdown = CreateDropdown(_rootPanel, new Vector2(10, -10), new List<string>(), OnRegionChanged);
            _marketSummaryText = CreateText(_rootPanel, "Market Summary", new Vector2(10, -50), 600);
            _priceTrendPanel = CreatePanel(_rootPanel, new Vector2(10, -100), new Vector2(400, 200));
            _tradePanel = CreatePanel(_rootPanel, new Vector2(450, -100), new Vector2(400, 200));
            _resourceDropdown = CreateDropdown(_tradePanel, new Vector2(10, -10), new List<string>(), OnResourceChanged);
            _tradeAmountField = CreateInputField(_tradePanel, new Vector2(10, -50));
            _tradeButton = CreateButton(_tradePanel, "Trade", new Vector2(10, -90), OnTradeClicked);
        }

        void UpdateRegionDropdown()
        {
            var regions = new List<string>(_economySystem.GetAllRegionIds());
            _regionDropdown.ClearOptions();
            _regionDropdown.AddOptions(regions);
            if (regions.Count > 0)
            {
                _selectedRegion = regions[0];
                UpdateMarketSummary();
                UpdateResourceDropdown();
            }
        }

        void UpdateMarketSummary()
        {
            var summary = _economySystem.GetMarketSummary(_selectedRegion);
            _marketSummaryText.text = summary;
            // TODO: Draw price trends in _priceTrendPanel
        }

        void UpdateResourceDropdown()
        {
            var resources = new List<string>(_economySystem.GetRegionResourceNames(_selectedRegion));
            _resourceDropdown.ClearOptions();
            _resourceDropdown.AddOptions(resources);
            if (resources.Count > 0)
                _selectedResource = resources[0];
        }

        void OnRegionChanged(int idx)
        {
            _selectedRegion = _regionDropdown.options[idx].text;
            UpdateMarketSummary();
            UpdateResourceDropdown();
        }

        void OnResourceChanged(int idx)
        {
            _selectedResource = _resourceDropdown.options[idx].text;
        }

        void OnTradeClicked()
        {
            if (float.TryParse(_tradeAmountField.text, out float amt) && amt > 0)
            {
                _economySystem.PlayerTrade(_selectedRegion, _selectedResource, amt);
                UpdateMarketSummary();
            }
        }

        Dropdown CreateDropdown(Transform parent, Vector2 pos, List<string> options, Action<int> onChanged)
        {
            var go = new GameObject("Dropdown");
            var rect = go.AddComponent<RectTransform>();
            go.transform.SetParent(parent, false);
            rect.anchoredPosition = pos;
            var dd = go.AddComponent<Dropdown>();
            dd.AddOptions(options);
            dd.onValueChanged.AddListener(onChanged.Invoke);
            return dd;
        }
        Text CreateText(Transform parent, string text, Vector2 pos, float width)
        {
            var go = new GameObject("Text");
            var rect = go.AddComponent<RectTransform>();
            go.transform.SetParent(parent, false);
            rect.anchoredPosition = pos;
            rect.sizeDelta = new Vector2(width, 30);
            var t = go.AddComponent<Text>();
            t.text = text;
            t.font = Resources.GetBuiltinResource<Font>("Arial.ttf");
            t.color = Color.white;
            return t;
        }
        RectTransform CreatePanel(Transform parent, Vector2 pos, Vector2 size)
        {
            var go = new GameObject("Panel");
            var rect = go.AddComponent<RectTransform>();
            go.transform.SetParent(parent, false);
            rect.anchoredPosition = pos;
            rect.sizeDelta = size;
            go.AddComponent<Image>().color = new Color(0.1f, 0.1f, 0.1f, 0.8f);
            return rect;
        }
        InputField CreateInputField(Transform parent, Vector2 pos)
        {
            var go = new GameObject("InputField");
            var rect = go.AddComponent<RectTransform>();
            go.transform.SetParent(parent, false);
            rect.anchoredPosition = pos;
            rect.sizeDelta = new Vector2(100, 30);
            var input = go.AddComponent<InputField>();
            input.text = "1";
            return input;
        }
        Button CreateButton(Transform parent, string text, Vector2 pos, Action onClick)
        {
            var go = new GameObject("Button");
            var rect = go.AddComponent<RectTransform>();
            go.transform.SetParent(parent, false);
            rect.anchoredPosition = pos;
            rect.sizeDelta = new Vector2(100, 30);
            var btn = go.AddComponent<Button>();
            var txt = new GameObject("ButtonText").AddComponent<Text>();
            txt.transform.SetParent(go.transform, false);
            txt.text = text;
            txt.font = Resources.GetBuiltinResource<Font>("Arial.ttf");
            txt.color = Color.black;
            txt.rectTransform.anchorMin = Vector2.zero;
            txt.rectTransform.anchorMax = Vector2.one;
            txt.rectTransform.offsetMin = Vector2.zero;
            txt.rectTransform.offsetMax = Vector2.zero;
            btn.onClick.AddListener(() => onClick());
            return btn;
        }
    }
} 