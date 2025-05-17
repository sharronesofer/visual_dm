using UnityEngine;
using UnityEngine.UI;
using System;
using System.Collections.Generic;

namespace VisualDM.UI.Search
{
    public class SearchInput : MonoBehaviour
    {
        public InputField inputField;
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
                inputField = CreateInputField();
            }
            inputField.onValueChanged.AddListener(OnInputChanged);
            inputField.onEndEdit.AddListener(OnInputEndEdit);
        }

        private InputField CreateInputField()
        {
            var go = new GameObject("SearchInputField");
            go.transform.SetParent(transform);
            var rect = go.AddComponent<RectTransform>();
            rect.sizeDelta = new Vector2(300, 30);
            var input = go.AddComponent<InputField>();
            var text = new GameObject("Text").AddComponent<Text>();
            text.transform.SetParent(go.transform);
            text.font = Resources.GetBuiltinResource<Font>("Arial.ttf");
            input.textComponent = text;
            return input;
        }

        private void OnInputChanged(string value)
        {
            // TODO: Fetch suggestions from backend (WebSocket/REST)
            UpdateSuggestions(new List<string>()); // Placeholder
        }

        private void OnInputEndEdit(string value)
        {
            if (Input.GetKeyDown(KeyCode.Return))
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
            if (Input.GetKeyDown(KeyCode.DownArrow))
            {
                selectedSuggestionIndex = Mathf.Min(selectedSuggestionIndex + 1, suggestions.Count - 1);
                HighlightSuggestion(selectedSuggestionIndex);
            }
            else if (Input.GetKeyDown(KeyCode.UpArrow))
            {
                selectedSuggestionIndex = Mathf.Max(selectedSuggestionIndex - 1, 0);
                HighlightSuggestion(selectedSuggestionIndex);
            }
            else if (Input.GetKeyDown(KeyCode.Return) && selectedSuggestionIndex >= 0)
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