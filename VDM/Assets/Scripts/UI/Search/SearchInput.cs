using UnityEngine;
using UnityEngine.UI;
using System;
using System.Collections.Generic;

namespace VisualDM.UI
{
    public class SearchCore : MonoBehaviour
    {
        public CoreField inputField;
        public RectTransform suggestionsPanel;
        public GameObject suggestionItemPrefab;
        public event Action<string> OnSearchSubmitted;
        public event Action<string> OnSuggestionSelected;

        private List<string> suggestions = new List<string>();
        private List<GameObject> suggestionItems = new List<GameObject>();
        private int selectedSuggestionIndex = -1;

        void Awake()
        {
            if (inputField == null)
            {
                inputField = CreateCoreField();
            }
            inputField.onValueChanged.AddListener(OnCoreChanged);
            inputField.onEndEdit.AddListener(OnCoreEndEdit);
        }

        private CoreField CreateCoreField()
        {
            var go = new GameObject("SearchCoreField");
            go.transform.SetParent(transform);
            var rect = go.AddComponent<RectTransform>();
            rect.sizeDelta = new Vector2(300, 30);
            var input = go.AddComponent<CoreField>();
            var text = new GameObject("Text").AddComponent<Text>();
            text.transform.SetParent(go.transform);
            text.font = Resources.GetBuiltinResource<Font>("Arial.ttf");
            input.textComponent = text;
            return input;
        }

        private void OnCoreChanged(string value)
        {
            // TODO: Fetch suggestions from backend (WebSocket/REST)
            UpdateSuggestions(new List<string>()); // Placeholder
        }

        private void OnCoreEndEdit(string value)
        {
            if (Core.GetKeyDown(KeyCode.Return))
            {
                OnSearchSubmitted?.Invoke(value);
            }
        }

        private void UpdateSuggestions(List<string> newSuggestions)
        {
            suggestions = newSuggestions;
            foreach (var item in suggestionItems)
                Destroy(item);
            suggestionItems.Clear();
            for (int i = 0; i < suggestions.Count; i++)
            {
                var go = Instantiate(suggestionItemPrefab, suggestionsPanel);
                var text = go.GetComponentInChildren<Text>();
                if (text != null) text.text = suggestions[i];
                int idx = i;
                go.GetComponent<Button>().onClick.AddListener(() => OnSuggestionClicked(idx));
                suggestionItems.Add(go);
            }
            selectedSuggestionIndex = -1;
        }

        private void OnSuggestionClicked(int index)
        {
            inputField.text = suggestions[index];
            OnSuggestionSelected?.Invoke(suggestions[index]);
        }

        void Update()
        {
            if (suggestions.Count == 0) return;
            if (Core.GetKeyDown(KeyCode.DownArrow))
            {
                selectedSuggestionIndex = Mathf.Min(selectedSuggestionIndex + 1, suggestions.Count - 1);
                HighlightSuggestion(selectedSuggestionIndex);
            }
            else if (Core.GetKeyDown(KeyCode.UpArrow))
            {
                selectedSuggestionIndex = Mathf.Max(selectedSuggestionIndex - 1, 0);
                HighlightSuggestion(selectedSuggestionIndex);
            }
            else if (Core.GetKeyDown(KeyCode.Return) && selectedSuggestionIndex >= 0)
            {
                inputField.text = suggestions[selectedSuggestionIndex];
                OnSuggestionSelected?.Invoke(suggestions[selectedSuggestionIndex]);
            }
        }

        private void HighlightSuggestion(int index)
        {
            for (int i = 0; i < suggestionItems.Count; i++)
            {
                var img = suggestionItems[i].GetComponent<Image>();
                if (img != null)
                    img.color = (i == index) ? Color.yellow : Color.white;
            }
        }
    }
} 