using UnityEngine;
using UnityEngine.UI;
using System;
using System.Collections.Generic;

namespace VisualDM.UI
{
    public class SearchResultsDisplay : MonoBehaviour
    {
        public RectTransform resultsPanel;
        public GameObject resultItemPrefab;
        public Button nextPageButton;
        public Button prevPageButton;
        public Dropdown sortDropdown;
        public RectTransform filterTagsPanel;

        public event Action<int> OnPageChanged;
        public event Action<string> OnSortChanged;

        private int currentPage = 1;
        private int totalPages = 1;
        private List<GameObject> resultItems = new List<GameObject>();

        void Awake()
        {
            if (resultsPanel == null)
                resultsPanel = CreatePanel("ResultsPanel", new Vector2(600, 400));
            if (filterTagsPanel == null)
                filterTagsPanel = CreatePanel("FilterTagsPanel", new Vector2(600, 30));
            if (nextPageButton == null)
                nextPageButton = CreateButton("NextPageButton", "Next");
            if (prevPageButton == null)
                prevPageButton = CreateButton("PrevPageButton", "Prev");
            if (sortDropdown == null)
                sortDropdown = CreateSortDropdown();
            nextPageButton.onClick.AddListener(() => OnPageChanged?.Invoke(currentPage + 1));
            prevPageButton.onClick.AddListener(() => OnPageChanged?.Invoke(currentPage - 1));
            sortDropdown.onValueChanged.AddListener(idx => OnSortChanged?.Invoke(sortDropdown.options[idx].text));
        }

        private RectTransform CreatePanel(string name, Vector2 size)
        {
            var go = new GameObject(name);
            go.transform.SetParent(transform);
            var rect = go.AddComponent<RectTransform>();
            rect.sizeDelta = size;
            return rect;
        }

        private Button CreateButton(string name, string label)
        {
            var go = new GameObject(name);
            go.transform.SetParent(transform);
            var btn = go.AddComponent<Button>();
            var txt = new GameObject("Text").AddComponent<Text>();
            txt.transform.SetParent(go.transform);
            txt.text = label;
            txt.font = Resources.GetBuiltinResource<Font>("Arial.ttf");
            btn.targetGraphic = txt;
            return btn;
        }

        private Dropdown CreateSortDropdown()
        {
            var go = new GameObject("SortDropdown");
            go.transform.SetParent(transform);
            var dropdown = go.AddComponent<Dropdown>();
            dropdown.options = new List<Dropdown.OptionData> {
                new Dropdown.OptionData("Name"),
                new Dropdown.OptionData("Type"),
                new Dropdown.OptionData("Date")
            };
            return dropdown;
        }

        public void DisplayResults(List<string> results, int page, int totalPages)
        {
            foreach (var item in resultItems)
                Destroy(item);
            resultItems.Clear();
            foreach (var result in results)
            {
                var go = Instantiate(resultItemPrefab, resultsPanel);
                var text = go.GetComponentInChildren<Text>();
                if (text != null) text.text = result;
                resultItems.Add(go);
            }
            this.currentPage = page;
            this.totalPages = totalPages;
            prevPageButton.interactable = (page > 1);
            nextPageButton.interactable = (page < totalPages);
        }

        public void DisplayFilterTags(List<string> tags)
        {
            foreach (Transform child in filterTagsPanel)
                Destroy(child.gameObject);
            foreach (var tag in tags)
            {
                var go = new GameObject("Tag");
                go.transform.SetParent(filterTagsPanel);
                var txt = go.AddComponent<Text>();
                txt.text = tag;
                txt.font = Resources.GetBuiltinResource<Font>("Arial.ttf");
            }
        }
    }
} 