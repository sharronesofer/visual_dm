using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

namespace VisualDM.Simulation
{
    public class SimulationUIManager : MonoBehaviour
    {
        private Dropdown archetypeDropdown;
        private InputField levelInput;
        private Button startButton;
        private Button uploadButton;
        private InputField batchSizeInput;
        private Text statusText;
        private FileUploadHandler fileUploadHandler;

        void Start()
        {
            // Create UI elements at runtime
            var canvas = new GameObject("SimulationUICanvas").AddComponent<Canvas>();
            canvas.renderMode = RenderMode.ScreenSpaceOverlay;
            var panel = new GameObject("Panel").AddComponent<RectTransform>();
            panel.SetParent(canvas.transform);
            panel.sizeDelta = new Vector2(400, 600);

            // Archetype dropdown
            archetypeDropdown = CreateDropdown(panel, "Archetype", new List<string> { "Fighter", "Mage", "Rogue" }, new Vector2(0, 200));
            // Level input
            levelInput = CreateInputField(panel, "Level", "1", new Vector2(0, 150));
            // Batch size input
            batchSizeInput = CreateInputField(panel, "Batch Size", "100", new Vector2(0, 100));
            // Start button
            startButton = CreateButton(panel, "Start Simulation", new Vector2(0, 50), OnStartSimulation);
            // Upload button
            uploadButton = CreateButton(panel, "Upload Test Cases", new Vector2(0, 0), OnUploadTestCases);
            // Status text
            statusText = CreateText(panel, "Status: Ready", new Vector2(0, -50));

            // File upload handler
            fileUploadHandler = gameObject.AddComponent<FileUploadHandler>();
            fileUploadHandler.OnFileUploaded += OnFileUploaded;
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

        private InputField CreateInputField(Transform parent, string label, string defaultValue, Vector2 pos)
        {
            var go = new GameObject(label + "Input");
            go.transform.SetParent(parent);
            var input = go.AddComponent<InputField>();
            input.text = defaultValue;
            go.GetComponent<RectTransform>().anchoredPosition = pos;
            return input;
        }

        private Button CreateButton(Transform parent, string label, Vector2 pos, Action onClick)
        {
            var go = new GameObject(label + "Button");
            go.transform.SetParent(parent);
            var button = go.AddComponent<Button>();
            button.onClick.AddListener(() => onClick());
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

        private void OnStartSimulation()
        {
            var archetype = (CharacterArchetype)archetypeDropdown.value;
            int level = int.Parse(levelInput.text);
            int batchSize = int.Parse(batchSizeInput.text);
            var character = TestCaseGenerator.GenerateBuild(archetype, level);
            // Run batch simulation
            statusText.text = "Running...";
            float hitRate = SimulationManager.SimulateBatchAttacks(character, character, 0, batchSize);
            statusText.text = $"Simulation complete. Hit rate: {hitRate:P1}";
        }

        private void OnUploadTestCases()
        {
            fileUploadHandler.OpenFilePicker();
        }

        private void OnFileUploaded(string json)
        {
            var testCases = TestCaseGenerator.LoadCustomTestCases(json);
            statusText.text = $"Loaded {testCases.Count} custom test cases.";
        }
    }

    // File upload handler for runtime drag-and-drop or file picker
    public class FileUploadHandler : MonoBehaviour
    {
        public event Action<string> OnFileUploaded;
        public void OpenFilePicker()
        {
            // Platform-specific file picker logic (stub)
            // In WebGL, use JS interop; in desktop, use native dialogs
            // For now, simulate file upload
            OnFileUploaded?.Invoke("[]");
        }
    }
} 