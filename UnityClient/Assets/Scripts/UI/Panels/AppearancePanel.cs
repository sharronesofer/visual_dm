using UnityEngine;
using UnityEngine.UI;
using TMPro;
using System;
using System.Collections.Generic;

namespace VisualDM.UI.Panels
{
    /// <summary>
    /// Panel for customizing character appearance.
    /// This is a Unity implementation of the React AppearancePanel component.
    /// </summary>
    public class AppearancePanel : Components.Panel
    {
        [Header("Appearance Panel Settings")]
        [SerializeField] private bool autoRefresh = true;
        
        // UI elements
        private Dictionary<string, Slider> sliders = new Dictionary<string, Slider>();
        private Dictionary<string, TMP_Dropdown> dropdowns = new Dictionary<string, TMP_Dropdown>();
        private Dictionary<string, Components.CustomButton> buttons = new Dictionary<string, Components.CustomButton>();
        
        // Events
        public event Action<string, float> OnSliderValueChanged;
        public event Action<string, int> OnDropdownValueChanged;
        public event Action<string> OnButtonClicked;
        
        protected override void Awake()
        {
            base.Awake();
            
            // Set panel title
            SetTitle("Appearance");
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
        /// Builds the UI elements for the appearance customization
        /// </summary>
        public void BuildUI()
        {
            // Clear existing content
            ClearContent();
            
            // Add common appearance options
            AddFeatureSection("Body");
            AddSlider("Height", 0f, 2f, 1f);
            AddSlider("Weight", 0f, 2f, 1f);
            
            AddFeatureSection("Face");
            AddDropdown("Face Shape", new string[] { "Round", "Square", "Oval", "Heart" });
            AddSlider("Face Width", 0f, 1f, 0.5f);
            AddSlider("Face Length", 0f, 1f, 0.5f);
            
            AddFeatureSection("Hair");
            AddDropdown("Hair Style", new string[] { "Short", "Long", "Bald", "Ponytail", "Braided" });
            AddColorPicker("Hair Color");
            
            AddFeatureSection("Eyes");
            AddDropdown("Eye Shape", new string[] { "Round", "Almond", "Narrow", "Wide" });
            AddColorPicker("Eye Color");
            AddSlider("Eye Size", 0.5f, 1.5f, 1f);
            AddSlider("Eye Spacing", 0.5f, 1.5f, 1f);
            
            AddFeatureSection("Nose");
            AddDropdown("Nose Type", new string[] { "Straight", "Roman", "Button", "Snub" });
            AddSlider("Nose Size", 0.5f, 1.5f, 1f);
            
            AddFeatureSection("Mouth");
            AddSlider("Mouth Width", 0.5f, 1.5f, 1f);
            AddSlider("Lip Fullness", 0f, 1f, 0.5f);
            
            // Add randomize button
            AddButton("Randomize", "Randomize all appearance settings");
            
            // Add reset button
            AddButton("Reset to Default", "Reset all appearance settings to default values");
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
        /// Add a slider for numeric value selection
        /// </summary>
        public Slider AddSlider(string label, float min, float max, float defaultValue)
        {
            // Create slider container
            GameObject containerGO = new GameObject($"SliderContainer_{label}");
            RectTransform containerRect = containerGO.AddComponent<RectTransform>();
            containerRect.sizeDelta = new Vector2(0, 40);
            
            // Add horizontal layout
            HorizontalLayoutGroup layout = containerGO.AddComponent<HorizontalLayoutGroup>();
            layout.spacing = 10;
            layout.padding = new RectOffset(5, 5, 5, 5);
            layout.childAlignment = TextAnchor.MiddleLeft;
            layout.childControlWidth = false;
            layout.childForceExpandWidth = false;
            
            // Create label
            GameObject labelGO = new GameObject("Label");
            RectTransform labelRect = labelGO.AddComponent<RectTransform>();
            labelRect.sizeDelta = new Vector2(100, 30);
            
            TextMeshProUGUI labelText = labelGO.AddComponent<TextMeshProUGUI>();
            labelText.text = label;
            labelText.alignment = TextAlignmentOptions.MidlineLeft;
            UIThemeManager.Instance.ApplyTextStyle(labelText, UIThemeManager.TextStyle.Body);
            
            // Create slider
            GameObject sliderGO = new GameObject("Slider");
            RectTransform sliderRect = sliderGO.AddComponent<RectTransform>();
            sliderRect.sizeDelta = new Vector2(150, 20);
            
            Slider slider = sliderGO.AddComponent<Slider>();
            slider.minValue = min;
            slider.maxValue = max;
            slider.value = defaultValue;
            
            // Add required slider components
            GameObject backgroundGO = new GameObject("Background");
            RectTransform backgroundRect = backgroundGO.AddComponent<RectTransform>();
            backgroundRect.anchorMin = Vector2.zero;
            backgroundRect.anchorMax = Vector2.one;
            backgroundRect.sizeDelta = Vector2.zero;
            Image backgroundImage = backgroundGO.AddComponent<Image>();
            backgroundImage.color = new Color(0.2f, 0.2f, 0.2f);
            
            GameObject fillGO = new GameObject("Fill");
            RectTransform fillRect = fillGO.AddComponent<RectTransform>();
            fillRect.anchorMin = Vector2.zero;
            fillRect.anchorMax = new Vector2(0.5f, 1);
            fillRect.sizeDelta = Vector2.zero;
            Image fillImage = fillGO.AddComponent<Image>();
            fillImage.color = UIThemeManager.Instance.accentColor;
            
            GameObject handleGO = new GameObject("Handle");
            RectTransform handleRect = handleGO.AddComponent<RectTransform>();
            handleRect.sizeDelta = new Vector2(20, 20);
            handleRect.anchorMin = new Vector2(0.5f, 0.5f);
            handleRect.anchorMax = new Vector2(0.5f, 0.5f);
            handleRect.pivot = new Vector2(0.5f, 0.5f);
            Image handleImage = handleGO.AddComponent<Image>();
            handleImage.color = Color.white;
            
            // Setup slider references
            backgroundGO.transform.SetParent(sliderGO.transform, false);
            fillGO.transform.SetParent(backgroundGO.transform, false);
            handleGO.transform.SetParent(sliderGO.transform, false);
            
            slider.targetGraphic = handleImage;
            slider.fillRect = fillRect;
            slider.handleRect = handleRect;
            
            // Create value text
            GameObject valueGO = new GameObject("Value");
            RectTransform valueRect = valueGO.AddComponent<RectTransform>();
            valueRect.sizeDelta = new Vector2(50, 30);
            
            TextMeshProUGUI valueText = valueGO.AddComponent<TextMeshProUGUI>();
            valueText.text = defaultValue.ToString("0.00");
            valueText.alignment = TextAlignmentOptions.MidlineRight;
            UIThemeManager.Instance.ApplyTextStyle(valueText, UIThemeManager.TextStyle.Small);
            
            // Add listener to update text
            slider.onValueChanged.AddListener((value) => {
                valueText.text = value.ToString("0.00");
                OnSliderValueChanged?.Invoke(label, value);
            });
            
            // Set hierarchy
            labelGO.transform.SetParent(containerGO.transform, false);
            sliderGO.transform.SetParent(containerGO.transform, false);
            valueGO.transform.SetParent(containerGO.transform, false);
            
            // Add to panel
            containerGO.transform.SetParent(GetContentContainer(), false);
            
            // Store reference
            sliders[label] = slider;
            
            return slider;
        }
        
        /// <summary>
        /// Add a dropdown for option selection
        /// </summary>
        public TMP_Dropdown AddDropdown(string label, string[] options)
        {
            // Create dropdown container
            GameObject containerGO = new GameObject($"DropdownContainer_{label}");
            RectTransform containerRect = containerGO.AddComponent<RectTransform>();
            containerRect.sizeDelta = new Vector2(0, 40);
            
            // Add horizontal layout
            HorizontalLayoutGroup layout = containerGO.AddComponent<HorizontalLayoutGroup>();
            layout.spacing = 10;
            layout.padding = new RectOffset(5, 5, 5, 5);
            layout.childAlignment = TextAnchor.MiddleLeft;
            layout.childControlWidth = false;
            layout.childForceExpandWidth = false;
            
            // Create label
            GameObject labelGO = new GameObject("Label");
            RectTransform labelRect = labelGO.AddComponent<RectTransform>();
            labelRect.sizeDelta = new Vector2(100, 30);
            
            TextMeshProUGUI labelText = labelGO.AddComponent<TextMeshProUGUI>();
            labelText.text = label;
            labelText.alignment = TextAlignmentOptions.MidlineLeft;
            UIThemeManager.Instance.ApplyTextStyle(labelText, UIThemeManager.TextStyle.Body);
            
            // Create dropdown
            GameObject dropdownGO = new GameObject("Dropdown");
            RectTransform dropdownRect = dropdownGO.AddComponent<RectTransform>();
            dropdownRect.sizeDelta = new Vector2(200, 30);
            
            TMP_Dropdown dropdown = dropdownGO.AddComponent<TMP_Dropdown>();
            
            // Add required dropdown components
            Image dropdownImage = dropdownGO.AddComponent<Image>();
            dropdownImage.color = UIThemeManager.Instance.secondaryColor;
            
            // Add options
            List<TMP_Dropdown.OptionData> optionList = new List<TMP_Dropdown.OptionData>();
            foreach (string option in options)
            {
                optionList.Add(new TMP_Dropdown.OptionData(option));
            }
            dropdown.options = optionList;
            
            // Add listener
            dropdown.onValueChanged.AddListener((index) => {
                OnDropdownValueChanged?.Invoke(label, index);
            });
            
            // Set hierarchy
            labelGO.transform.SetParent(containerGO.transform, false);
            dropdownGO.transform.SetParent(containerGO.transform, false);
            
            // Add to panel
            containerGO.transform.SetParent(GetContentContainer(), false);
            
            // Store reference
            dropdowns[label] = dropdown;
            
            return dropdown;
        }
        
        /// <summary>
        /// Add a color picker for selecting colors
        /// </summary>
        public void AddColorPicker(string label)
        {
            // For simplicity, we'll just add a placeholder
            // A real implementation would use a custom color picker component
            
            // Create color picker container
            GameObject containerGO = new GameObject($"ColorPickerContainer_{label}");
            RectTransform containerRect = containerGO.AddComponent<RectTransform>();
            containerRect.sizeDelta = new Vector2(0, 40);
            
            // Add horizontal layout
            HorizontalLayoutGroup layout = containerGO.AddComponent<HorizontalLayoutGroup>();
            layout.spacing = 10;
            layout.padding = new RectOffset(5, 5, 5, 5);
            layout.childAlignment = TextAnchor.MiddleLeft;
            layout.childControlWidth = false;
            layout.childForceExpandWidth = false;
            
            // Create label
            GameObject labelGO = new GameObject("Label");
            RectTransform labelRect = labelGO.AddComponent<RectTransform>();
            labelRect.sizeDelta = new Vector2(100, 30);
            
            TextMeshProUGUI labelText = labelGO.AddComponent<TextMeshProUGUI>();
            labelText.text = label;
            labelText.alignment = TextAlignmentOptions.MidlineLeft;
            UIThemeManager.Instance.ApplyTextStyle(labelText, UIThemeManager.TextStyle.Body);
            
            // Create a placeholder button for color selection
            GameObject buttonGO = new GameObject("ColorButton");
            RectTransform buttonRect = buttonGO.AddComponent<RectTransform>();
            buttonRect.sizeDelta = new Vector2(100, 30);
            
            Button colorButton = buttonGO.AddComponent<Button>();
            Image buttonImage = buttonGO.AddComponent<Image>();
            buttonImage.color = Color.white; // Default color
            
            // Set hierarchy
            labelGO.transform.SetParent(containerGO.transform, false);
            buttonGO.transform.SetParent(containerGO.transform, false);
            
            // Add to panel
            containerGO.transform.SetParent(GetContentContainer(), false);
        }
        
        /// <summary>
        /// Add a button
        /// </summary>
        public Components.CustomButton AddButton(string text, string ariaLabel = "")
        {
            // Create button GameObject
            GameObject buttonGO = new GameObject($"Button_{text}");
            RectTransform buttonRect = buttonGO.AddComponent<RectTransform>();
            buttonRect.sizeDelta = new Vector2(0, 40);
            
            // Add custom button component
            Components.CustomButton button = buttonGO.AddComponent<Components.CustomButton>();
            button.SetText(text);
            
            if (!string.IsNullOrEmpty(ariaLabel))
            {
                button.SetAriaLabel(ariaLabel);
            }
            
            // Add click listener
            button.OnClick += () => {
                OnButtonClicked?.Invoke(text);
            };
            
            // Add to panel
            buttonGO.transform.SetParent(GetContentContainer(), false);
            
            // Store reference
            buttons[text] = button;
            
            return button;
        }
        
        /// <summary>
        /// Get a slider by label
        /// </summary>
        public Slider GetSlider(string label)
        {
            if (sliders.TryGetValue(label, out Slider slider))
            {
                return slider;
            }
            return null;
        }
        
        /// <summary>
        /// Get a dropdown by label
        /// </summary>
        public TMP_Dropdown GetDropdown(string label)
        {
            if (dropdowns.TryGetValue(label, out TMP_Dropdown dropdown))
            {
                return dropdown;
            }
            return null;
        }
        
        /// <summary>
        /// Get a button by text
        /// </summary>
        public Components.CustomButton GetButton(string text)
        {
            if (buttons.TryGetValue(text, out Components.CustomButton button))
            {
                return button;
            }
            return null;
        }
        
        /// <summary>
        /// Set a slider value
        /// </summary>
        public void SetSliderValue(string label, float value)
        {
            Slider slider = GetSlider(label);
            if (slider != null)
            {
                slider.value = value;
            }
        }
        
        /// <summary>
        /// Set a dropdown value
        /// </summary>
        public void SetDropdownValue(string label, int value)
        {
            TMP_Dropdown dropdown = GetDropdown(label);
            if (dropdown != null)
            {
                dropdown.value = value;
            }
        }
    }
} 