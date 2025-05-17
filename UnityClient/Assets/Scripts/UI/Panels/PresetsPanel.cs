using UnityEngine;
using UnityEngine.UI;
using TMPro;
using System;
using System.Collections.Generic;

namespace VisualDM.UI.Panels
{
    /// <summary>
    /// Panel for managing character presets.
    /// This is a Unity implementation of the React PresetsPanel component.
    /// </summary>
    public class PresetsPanel : Components.Panel
    {
        [Header("Presets Panel Settings")]
        [SerializeField] private bool autoRefresh = true;
        
        // UI elements
        private List<Components.CustomButton> presetButtons = new List<Components.CustomButton>();
        private TMP_InputField presetNameInput;
        
        // Events
        public event Action<string> OnPresetSelected;
        public event Action<string> OnPresetSaved;
        public event Action<string> OnPresetDeleted;
        
        protected override void Awake()
        {
            base.Awake();
            
            // Set panel title
            SetTitle("Character Presets");
        }
        
        protected override void Start()
        {
            base.Start();
            
            // Build UI
            if (autoRefresh)
            {
                BuildUI();
            }
        }
        
        /// <summary>
        /// Builds the UI elements for the presets panel
        /// </summary>
        public void BuildUI()
        {
            // Clear existing content
            ClearContent();
            
            // Add saved presets section
            AddFeatureSection("Saved Presets");
            
            // Create scrollable list of presets
            CreatePresetsScrollList();
            
            // Add save new preset section
            AddFeatureSection("Save New Preset");
            
            // Create save preset UI
            CreateSavePresetUI();
        }
        
        /// <summary>
        /// Add a section header for a group of related features
        /// </summary>
        public void AddFeatureSection(string title)
        {
            GameObject sectionGO = new GameObject($"Section_{title}");
            RectTransform sectionRect = sectionGO.AddComponent<RectTransform>();
            sectionRect.sizeDelta = new Vector2(0, 30);
            
            TextMeshProUGUI sectionText = sectionGO.AddComponent<TextMeshProUGUI>();
            sectionText.text = title;
            sectionText.alignment = TextAlignmentOptions.MidlineLeft;
            
            UIThemeManager.Instance.ApplyTextStyle(sectionText, UIThemeManager.TextStyle.Subheader);
            
            // Add to panel
            sectionGO.transform.SetParent(GetContentContainer(), false);
        }
        
        /// <summary>
        /// Create scrollable list for character presets
        /// </summary>
        private void CreatePresetsScrollList()
        {
            // Create scroll view container
            GameObject scrollViewGO = new GameObject("PresetsScrollView");
            RectTransform scrollViewRect = scrollViewGO.AddComponent<RectTransform>();
            scrollViewRect.sizeDelta = new Vector2(0, 200);
            
            ScrollRect scrollRect = scrollViewGO.AddComponent<ScrollRect>();
            Image scrollViewImage = scrollViewGO.AddComponent<Image>();
            scrollViewImage.color = UIThemeManager.Instance.backgroundSecondaryColor;
            
            // Create viewport
            GameObject viewportGO = new GameObject("Viewport");
            RectTransform viewportRect = viewportGO.AddComponent<RectTransform>();
            viewportRect.anchorMin = Vector2.zero;
            viewportRect.anchorMax = Vector2.one;
            viewportRect.sizeDelta = Vector2.zero;
            viewportRect.pivot = new Vector2(0, 1);
            
            Image viewportImage = viewportGO.AddComponent<Image>();
            viewportImage.color = Color.clear;
            Mask viewportMask = viewportGO.AddComponent<Mask>();
            viewportMask.showMaskGraphic = false;
            
            // Create content container
            GameObject contentGO = new GameObject("Content");
            RectTransform contentRect = contentGO.AddComponent<RectTransform>();
            contentRect.anchorMin = new Vector2(0, 1);
            contentRect.anchorMax = new Vector2(1, 1);
            contentRect.sizeDelta = new Vector2(0, 300); // This will be updated as content is added
            contentRect.pivot = new Vector2(0, 1);
            
            // Add vertical layout group
            VerticalLayoutGroup contentLayout = contentGO.AddComponent<VerticalLayoutGroup>();
            contentLayout.spacing = 5;
            contentLayout.padding = new RectOffset(10, 10, 10, 10);
            contentLayout.childAlignment = TextAnchor.UpperCenter;
            contentLayout.childControlHeight = false;
            contentLayout.childControlWidth = true;
            contentLayout.childForceExpandHeight = false;
            contentLayout.childForceExpandWidth = true;
            
            // Set up hierarchy
            viewportGO.transform.SetParent(scrollViewGO.transform, false);
            contentGO.transform.SetParent(viewportGO.transform, false);
            
            // Set up scroll rect references
            scrollRect.viewport = viewportRect;
            scrollRect.content = contentRect;
            scrollRect.horizontal = false;
            scrollRect.vertical = true;
            
            // Add to panel
            scrollViewGO.transform.SetParent(GetContentContainer(), false);
            
            // Add sample presets
            AddPresetButton("Warrior Preset", contentGO.transform);
            AddPresetButton("Mage Preset", contentGO.transform);
            AddPresetButton("Rogue Preset", contentGO.transform);
            AddPresetButton("Paladin Preset", contentGO.transform);
            AddPresetButton("Custom Character 1", contentGO.transform);
            
            // Update content height based on children
            float contentHeight = (55 * 5) + contentLayout.padding.vertical + (contentLayout.spacing * 4);
            contentRect.sizeDelta = new Vector2(0, contentHeight);
        }
        
        /// <summary>
        /// Add a preset button to the list
        /// </summary>
        private Components.CustomButton AddPresetButton(string presetName, Transform parent)
        {
            // Create container
            GameObject containerGO = new GameObject($"PresetContainer_{presetName}");
            RectTransform containerRect = containerGO.AddComponent<RectTransform>();
            containerRect.sizeDelta = new Vector2(0, 50);
            
            // Add horizontal layout
            HorizontalLayoutGroup layout = containerGO.AddComponent<HorizontalLayoutGroup>();
            layout.spacing = 10;
            layout.padding = new RectOffset(5, 5, 5, 5);
            layout.childAlignment = TextAnchor.MiddleLeft;
            layout.childControlWidth = false;
            layout.childForceExpandWidth = false;
            
            // Create preset button
            GameObject buttonGO = new GameObject("PresetButton");
            RectTransform buttonRect = buttonGO.AddComponent<RectTransform>();
            buttonRect.sizeDelta = new Vector2(200, 40);
            
            Components.CustomButton button = buttonGO.AddComponent<Components.CustomButton>();
            button.SetText(presetName);
            button.SetAriaLabel($"Load {presetName}");
            
            // Create delete button
            GameObject deleteButtonGO = new GameObject("DeleteButton");
            RectTransform deleteButtonRect = deleteButtonGO.AddComponent<RectTransform>();
            deleteButtonRect.sizeDelta = new Vector2(40, 40);
            
            Components.CustomButton deleteButton = deleteButtonGO.AddComponent<Components.CustomButton>();
            deleteButton.SetText("X");
            deleteButton.SetAriaLabel($"Delete {presetName}");
            deleteButton.SetStyle(UIThemeManager.ButtonStyle.Secondary);
            
            // Add listeners
            button.OnClick += () => OnPresetSelected?.Invoke(presetName);
            deleteButton.OnClick += () => {
                OnPresetDeleted?.Invoke(presetName);
                Destroy(containerGO);
            };
            
            // Set hierarchy
            buttonGO.transform.SetParent(containerGO.transform, false);
            deleteButtonGO.transform.SetParent(containerGO.transform, false);
            containerGO.transform.SetParent(parent, false);
            
            // Store reference
            presetButtons.Add(button);
            
            return button;
        }
        
        /// <summary>
        /// Create UI for saving new presets
        /// </summary>
        private void CreateSavePresetUI()
        {
            // Create container
            GameObject containerGO = new GameObject("SavePresetContainer");
            RectTransform containerRect = containerGO.AddComponent<RectTransform>();
            containerRect.sizeDelta = new Vector2(0, 50);
            
            // Add horizontal layout
            HorizontalLayoutGroup layout = containerGO.AddComponent<HorizontalLayoutGroup>();
            layout.spacing = 10;
            layout.padding = new RectOffset(5, 5, 5, 5);
            layout.childAlignment = TextAnchor.MiddleLeft;
            layout.childControlWidth = false;
            layout.childForceExpandWidth = false;
            
            // Create input field
            GameObject inputGO = new GameObject("PresetNameInput");
            RectTransform inputRect = inputGO.AddComponent<RectTransform>();
            inputRect.sizeDelta = new Vector2(200, 40);
            
            Image inputBg = inputGO.AddComponent<Image>();
            inputBg.color = UIThemeManager.Instance.secondaryColor;
            
            presetNameInput = inputGO.AddComponent<TMP_InputField>();
            
            // Create input field text
            GameObject textGO = new GameObject("Text");
            RectTransform textRect = textGO.AddComponent<RectTransform>();
            textRect.anchorMin = Vector2.zero;
            textRect.anchorMax = Vector2.one;
            textRect.sizeDelta = Vector2.zero;
            textRect.offsetMin = new Vector2(10, 0);
            textRect.offsetMax = new Vector2(-10, 0);
            
            TextMeshProUGUI inputText = textGO.AddComponent<TextMeshProUGUI>();
            inputText.alignment = TextAlignmentOptions.MidlineLeft;
            UIThemeManager.Instance.ApplyTextStyle(inputText, UIThemeManager.TextStyle.Body);
            
            // Create placeholder text
            GameObject placeholderGO = new GameObject("Placeholder");
            RectTransform placeholderRect = placeholderGO.AddComponent<RectTransform>();
            placeholderRect.anchorMin = Vector2.zero;
            placeholderRect.anchorMax = Vector2.one;
            placeholderRect.sizeDelta = Vector2.zero;
            placeholderRect.offsetMin = new Vector2(10, 0);
            placeholderRect.offsetMax = new Vector2(-10, 0);
            
            TextMeshProUGUI placeholderText = placeholderGO.AddComponent<TextMeshProUGUI>();
            placeholderText.text = "New preset name...";
            placeholderText.alignment = TextAlignmentOptions.MidlineLeft;
            UIThemeManager.Instance.ApplyTextStyle(placeholderText, UIThemeManager.TextStyle.Body);
            placeholderText.color = new Color(placeholderText.color.r, placeholderText.color.g, placeholderText.color.b, 0.5f);
            
            // Set up input field
            presetNameInput.textComponent = inputText;
            presetNameInput.placeholder = placeholderText;
            
            // Create save button
            GameObject saveButtonGO = new GameObject("SaveButton");
            RectTransform saveButtonRect = saveButtonGO.AddComponent<RectTransform>();
            saveButtonRect.sizeDelta = new Vector2(80, 40);
            
            Components.CustomButton saveButton = saveButtonGO.AddComponent<Components.CustomButton>();
            saveButton.SetText("Save");
            saveButton.SetAriaLabel("Save current character as preset");
            
            // Add listener to save button
            saveButton.OnClick += () => {
                if (!string.IsNullOrEmpty(presetNameInput.text))
                {
                    string presetName = presetNameInput.text;
                    OnPresetSaved?.Invoke(presetName);
                    
                    // Add new preset to list
                    if (scrollRect && scrollRect.content)
                    {
                        AddPresetButton(presetName, scrollRect.content);
                    }
                    
                    // Clear input
                    presetNameInput.text = "";
                }
            };
            
            // Set hierarchy
            textGO.transform.SetParent(inputGO.transform, false);
            placeholderGO.transform.SetParent(inputGO.transform, false);
            inputGO.transform.SetParent(containerGO.transform, false);
            saveButtonGO.transform.SetParent(containerGO.transform, false);
            
            // Add to panel
            containerGO.transform.SetParent(GetContentContainer(), false);
        }
        
        /// <summary>
        /// Get reference to the scroll rect
        /// </summary>
        private ScrollRect scrollRect
        {
            get
            {
                Transform scrollViewTransform = GetContentContainer().Find("PresetsScrollView");
                if (scrollViewTransform)
                {
                    return scrollViewTransform.GetComponent<ScrollRect>();
                }
                return null;
            }
        }
        
        /// <summary>
        /// Add a new preset to the list
        /// </summary>
        public void AddPreset(string presetName)
        {
            if (scrollRect && scrollRect.content)
            {
                AddPresetButton(presetName, scrollRect.content);
                
                // Update content height
                VerticalLayoutGroup layout = scrollRect.content.GetComponent<VerticalLayoutGroup>();
                if (layout)
                {
                    float contentHeight = (55 * presetButtons.Count) + layout.padding.vertical + (layout.spacing * (presetButtons.Count - 1));
                    scrollRect.content.sizeDelta = new Vector2(0, contentHeight);
                }
            }
        }
        
        /// <summary>
        /// Remove a preset from the list
        /// </summary>
        public void RemovePreset(string presetName)
        {
            // Find and remove preset button
            for (int i = presetButtons.Count - 1; i >= 0; i--)
            {
                Components.CustomButton button = presetButtons[i];
                
                if (button && button.gameObject)
                {
                    TextMeshProUGUI textComponent = button.GetComponentInChildren<TextMeshProUGUI>();
                    if (textComponent && textComponent.text == presetName)
                    {
                        Transform container = button.transform.parent;
                        presetButtons.RemoveAt(i);
                        Destroy(container.gameObject);
                        break;
                    }
                }
            }
            
            // Update content height
            if (scrollRect && scrollRect.content)
            {
                VerticalLayoutGroup layout = scrollRect.content.GetComponent<VerticalLayoutGroup>();
                if (layout)
                {
                    float contentHeight = (55 * presetButtons.Count) + layout.padding.vertical + (layout.spacing * (presetButtons.Count - 1));
                    scrollRect.content.sizeDelta = new Vector2(0, Mathf.Max(contentHeight, 50));
                }
            }
        }
    }
} 