using UnityEngine;
using UnityEngine.UI;
using TMPro;
using System;
using System.Collections.Generic;

namespace VisualDM.UI.Panels
{
    /// <summary>
    /// Panel for randomizing character appearance.
    /// This is a Unity implementation of the React RandomizerPanel component.
    /// </summary>
    public class RandomizerPanel : Components.Panel
    {
        [Header("Randomizer Panel Settings")]
        [SerializeField] private bool autoRefresh = true;
        
        // Random configuration
        [Serializable]
        public class RandomizerConfig
        {
            public bool randomizeRace = true;
            public bool randomizeGender = true;
            public bool randomizeAppearance = true;
            public bool randomizeColors = true;
            public bool randomizeArmor = true;
        }
        
        [SerializeField] private RandomizerConfig config = new RandomizerConfig();
        
        // UI elements
        private Dictionary<string, Toggle> toggles = new Dictionary<string, Toggle>();
        private Components.CustomButton randomizeButton;
        
        // Events
        public event Action<RandomizerConfig> OnRandomize;
        
        protected override void Awake()
        {
            base.Awake();
            
            // Set panel title
            SetTitle("Character Randomizer");
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
        /// Builds the UI elements for the randomizer panel
        /// </summary>
        public void BuildUI()
        {
            // Clear existing content
            ClearContent();
            
            // Create toggles section
            AddFeatureSection("Randomize Options");
            CreateToggles();
            
            // Add spacing
            AddSpacing(20);
            
            // Create randomize button
            CreateRandomizeButton();
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
        /// Add vertical spacing element
        /// </summary>
        public void AddSpacing(float height)
        {
            GameObject spacerGO = new GameObject("Spacer");
            RectTransform spacerRect = spacerGO.AddComponent<RectTransform>();
            spacerRect.sizeDelta = new Vector2(0, height);
            
            // Add to panel
            spacerGO.transform.SetParent(GetContentContainer(), false);
        }
        
        /// <summary>
        /// Create all toggle options for randomization
        /// </summary>
        private void CreateToggles()
        {
            // Create container
            GameObject containerGO = new GameObject("TogglesContainer");
            RectTransform containerRect = containerGO.AddComponent<RectTransform>();
            
            // Add vertical layout
            VerticalLayoutGroup layout = containerGO.AddComponent<VerticalLayoutGroup>();
            layout.spacing = 10;
            layout.padding = new RectOffset(10, 10, 10, 10);
            layout.childAlignment = TextAnchor.UpperLeft;
            layout.childControlHeight = false;
            layout.childForceExpandHeight = false;
            
            // Add toggle options
            AddToggle("Race", "randomizeRace", config.randomizeRace, containerGO.transform);
            AddToggle("Gender", "randomizeGender", config.randomizeGender, containerGO.transform);
            AddToggle("Appearance Features", "randomizeAppearance", config.randomizeAppearance, containerGO.transform);
            AddToggle("Colors", "randomizeColors", config.randomizeColors, containerGO.transform);
            AddToggle("Armor", "randomizeArmor", config.randomizeArmor, containerGO.transform);
            
            // Adjust container height based on children
            float containerHeight = (30 * 5) + layout.padding.vertical + (layout.spacing * 4);
            containerRect.sizeDelta = new Vector2(0, containerHeight);
            
            // Add to panel
            containerGO.transform.SetParent(GetContentContainer(), false);
        }
        
        /// <summary>
        /// Add a toggle option with label
        /// </summary>
        private Toggle AddToggle(string label, string id, bool initialValue, Transform parent)
        {
            // Create container
            GameObject toggleContainerGO = new GameObject($"Toggle_{id}");
            RectTransform toggleContainerRect = toggleContainerGO.AddComponent<RectTransform>();
            toggleContainerRect.sizeDelta = new Vector2(0, 30);
            
            // Add horizontal layout
            HorizontalLayoutGroup layout = toggleContainerGO.AddComponent<HorizontalLayoutGroup>();
            layout.spacing = 10;
            layout.padding = new RectOffset(5, 5, 5, 5);
            layout.childAlignment = TextAnchor.MiddleLeft;
            layout.childControlWidth = false;
            layout.childForceExpandWidth = false;
            
            // Create toggle
            GameObject toggleGO = new GameObject("Toggle");
            RectTransform toggleRect = toggleGO.AddComponent<RectTransform>();
            toggleRect.sizeDelta = new Vector2(20, 20);
            
            Toggle toggle = toggleGO.AddComponent<Toggle>();
            toggle.isOn = initialValue;
            
            // Create toggle background
            GameObject toggleBgGO = new GameObject("Background");
            RectTransform toggleBgRect = toggleBgGO.AddComponent<RectTransform>();
            toggleBgRect.anchorMin = Vector2.zero;
            toggleBgRect.anchorMax = Vector2.one;
            toggleBgRect.sizeDelta = Vector2.zero;
            
            Image toggleBgImage = toggleBgGO.AddComponent<Image>();
            toggleBgImage.color = UIThemeManager.Instance.secondaryColor;
            
            // Create checkmark
            GameObject checkmarkGO = new GameObject("Checkmark");
            RectTransform checkmarkRect = checkmarkGO.AddComponent<RectTransform>();
            checkmarkRect.anchorMin = new Vector2(0.1f, 0.1f);
            checkmarkRect.anchorMax = new Vector2(0.9f, 0.9f);
            checkmarkRect.sizeDelta = Vector2.zero;
            
            Image checkmarkImage = checkmarkGO.AddComponent<Image>();
            checkmarkImage.color = UIThemeManager.Instance.accentColor;
            
            // Create label
            GameObject labelGO = new GameObject("Label");
            RectTransform labelRect = labelGO.AddComponent<RectTransform>();
            labelRect.sizeDelta = new Vector2(200, 20);
            
            TextMeshProUGUI labelText = labelGO.AddComponent<TextMeshProUGUI>();
            labelText.text = $"Randomize {label}";
            labelText.alignment = TextAlignmentOptions.MidlineLeft;
            
            UIThemeManager.Instance.ApplyTextStyle(labelText, UIThemeManager.TextStyle.Body);
            
            // Set up toggle
            toggle.targetGraphic = toggleBgImage;
            toggle.graphic = checkmarkImage;
            
            // Set hierarchy
            toggleBgGO.transform.SetParent(toggleGO.transform, false);
            checkmarkGO.transform.SetParent(toggleBgGO.transform, false);
            toggleGO.transform.SetParent(toggleContainerGO.transform, false);
            labelGO.transform.SetParent(toggleContainerGO.transform, false);
            
            // Add listener
            toggle.onValueChanged.AddListener((isOn) => {
                switch (id) {
                    case "randomizeRace": config.randomizeRace = isOn; break;
                    case "randomizeGender": config.randomizeGender = isOn; break;
                    case "randomizeAppearance": config.randomizeAppearance = isOn; break;
                    case "randomizeColors": config.randomizeColors = isOn; break;
                    case "randomizeArmor": config.randomizeArmor = isOn; break;
                }
            });
            
            // Add to parent
            toggleContainerGO.transform.SetParent(parent, false);
            
            // Store reference
            toggles[id] = toggle;
            
            return toggle;
        }
        
        /// <summary>
        /// Create the randomize button
        /// </summary>
        private void CreateRandomizeButton()
        {
            // Create container with centered alignment
            GameObject containerGO = new GameObject("RandomizeButtonContainer");
            RectTransform containerRect = containerGO.AddComponent<RectTransform>();
            containerRect.sizeDelta = new Vector2(0, 50);
            
            // Add horizontal layout with center alignment
            HorizontalLayoutGroup layout = containerGO.AddComponent<HorizontalLayoutGroup>();
            layout.childAlignment = TextAnchor.MiddleCenter;
            layout.padding = new RectOffset(0, 0, 10, 10);
            
            // Create button
            GameObject buttonGO = new GameObject("RandomizeButton");
            RectTransform buttonRect = buttonGO.AddComponent<RectTransform>();
            buttonRect.sizeDelta = new Vector2(200, 50);
            
            randomizeButton = buttonGO.AddComponent<Components.CustomButton>();
            randomizeButton.SetText("Randomize Character");
            randomizeButton.SetAriaLabel("Randomize character based on selected options");
            randomizeButton.SetStyle(UIThemeManager.ButtonStyle.Primary);
            
            // Add listener
            randomizeButton.OnClick += () => OnRandomize?.Invoke(config);
            
            // Set hierarchy
            buttonGO.transform.SetParent(containerGO.transform, false);
            containerGO.transform.SetParent(GetContentContainer(), false);
        }
        
        /// <summary>
        /// Get the current randomizer configuration
        /// </summary>
        public RandomizerConfig GetConfig()
        {
            return config;
        }
        
        /// <summary>
        /// Set the randomizer configuration
        /// </summary>
        public void SetConfig(RandomizerConfig newConfig)
        {
            config = newConfig;
            
            // Update toggles if they exist
            if (toggles.ContainsKey("randomizeRace")) toggles["randomizeRace"].isOn = config.randomizeRace;
            if (toggles.ContainsKey("randomizeGender")) toggles["randomizeGender"].isOn = config.randomizeGender;
            if (toggles.ContainsKey("randomizeAppearance")) toggles["randomizeAppearance"].isOn = config.randomizeAppearance;
            if (toggles.ContainsKey("randomizeColors")) toggles["randomizeColors"].isOn = config.randomizeColors;
            if (toggles.ContainsKey("randomizeArmor")) toggles["randomizeArmor"].isOn = config.randomizeArmor;
        }
    }
} 