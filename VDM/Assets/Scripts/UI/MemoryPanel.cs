using UnityEngine;
using UnityEngine.UI;
using System.Collections.Generic;
using System.Linq;

namespace VDM.Systems.UI {
    public class MemoryPanel : MonoBehaviour {
        private MemoryManager memoryManager;
        private GameObject panel;
        private InputField tagInput;
        private InputField entityInput;
        private InputField minImportanceInput;
        private InputField maxImportanceInput;
        private Button searchButton;
        private RectTransform memoryListContainer;
        private List<GameObject> memoryEntries = new List<GameObject>();

        public void Init(MemoryManager manager) {
            memoryManager = manager;
            CreateUI();
        }

        private void CreateUI() {
            panel = new GameObject("MemoryPanel");
            var canvas = panel.AddComponent<Canvas>();
            canvas.renderMode = RenderMode.ScreenSpaceOverlay;
            panel.AddComponent<CanvasScaler>();
            panel.AddComponent<GraphicRaycaster>();

            var bg = new GameObject("BG");
            bg.transform.SetParent(panel.transform);
            var image = bg.AddComponent<Image>();
            image.color = new Color(0,0,0,0.7f);
            var rect = bg.GetComponent<RectTransform>();
            rect.anchorMin = new Vector2(0.7f, 0.1f);
            rect.anchorMax = new Vector2(0.99f, 0.9f);
            rect.offsetMin = rect.offsetMax = Vector2.zero;

            tagInput = CreateInputField("Tag", new Vector2(0.72f, 0.85f));
            entityInput = CreateInputField("Entity", new Vector2(0.72f, 0.8f));
            minImportanceInput = CreateInputField("MinImp", new Vector2(0.72f, 0.75f));
            maxImportanceInput = CreateInputField("MaxImp", new Vector2(0.72f, 0.7f));
            searchButton = CreateButton("Search", new Vector2(0.72f, 0.65f));
            searchButton.onClick.AddListener(OnSearch);

            var listGO = new GameObject("MemoryList");
            listGO.transform.SetParent(panel.transform);
            memoryListContainer = listGO.AddComponent<RectTransform>();
            memoryListContainer.anchorMin = new Vector2(0.72f, 0.15f);
            memoryListContainer.anchorMax = new Vector2(0.98f, 0.6f);
            memoryListContainer.offsetMin = memoryListContainer.offsetMax = Vector2.zero;
        }

        private InputField CreateInputField(string placeholder, Vector2 anchor) {
            var go = new GameObject(placeholder+"Input");
            go.transform.SetParent(panel.transform);
            var input = go.AddComponent<InputField>();
            var rect = go.GetComponent<RectTransform>();
            rect.anchorMin = anchor;
            rect.anchorMax = anchor + new Vector2(0.2f, 0.05f);
            rect.offsetMin = rect.offsetMax = Vector2.zero;
            var text = new GameObject("Text").AddComponent<Text>();
            text.transform.SetParent(go.transform);
            text.text = "";
            input.textComponent = text;
            var ph = new GameObject("Placeholder").AddComponent<Text>();
            ph.transform.SetParent(go.transform);
            ph.text = placeholder;
            input.placeholder = ph;
            return input;
        }

        private Button CreateButton(string label, Vector2 anchor) {
            var go = new GameObject(label+"Button");
            go.transform.SetParent(panel.transform);
            var btn = go.AddComponent<Button>();
            var rect = go.GetComponent<RectTransform>();
            rect.anchorMin = anchor;
            rect.anchorMax = anchor + new Vector2(0.1f, 0.05f);
            rect.offsetMin = rect.offsetMax = Vector2.zero;
            var txt = new GameObject("Text").AddComponent<Text>();
            txt.transform.SetParent(go.transform);
            txt.text = label;
            btn.targetGraphic = txt;
            return btn;
        }

        private void OnSearch() {
            foreach (var entry in memoryEntries) Destroy(entry);
            memoryEntries.Clear();
            var query = new MemoryQuery {
                EntityId = entityInput.text,
                Tags = string.IsNullOrEmpty(tagInput.text) ? null : new List<string> { tagInput.text },
                MinImportance = float.TryParse(minImportanceInput.text, out var min) ? min : (float?)null,
                MaxImportance = float.TryParse(maxImportanceInput.text, out var max) ? max : (float?)null
            };
            var results = query.Execute(memoryManager).ToList();
            foreach (var mem in results) {
                var go = new GameObject("MemoryEntry");
                go.transform.SetParent(memoryListContainer);
                var txt = go.AddComponent<Text>();
                txt.text = $"[{mem.Type}] {mem.Timestamp}: {mem.Content} (Imp: {mem.CurrentImportance:F2})";
                memoryEntries.Add(go);
            }
        }
    }
} 