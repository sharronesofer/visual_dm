using UnityEngine;
using UnityEngine.UI;
using TMPro;
using System;
using System.Collections.Generic;

namespace VisualDM.UI.Components
{
    /// <summary>
    /// NavigationSidebar provides navigation between customization categories.
    /// This is a Unity implementation of the React NavigationSidebar component.
    /// </summary>
    public class NavigationSidebar : UIComponent
    {
        // Enum to represent the customization sections
        public enum CustomizationSection
        {
            Appearance,
            Armor,
            Presets,
            Randomizer
        }
        
        [Header("Navigation Settings")]
        [SerializeField] private CustomizationSection currentSection = CustomizationSection.Appearance;
        
        [Header("UI References")]
        [SerializeField] private TextMeshProUGUI titleText;
        [SerializeField] private Transform buttonContainer;
        
        // Dictionary to store navigation buttons
        private Dictionary<CustomizationSection, Button> navigationButtons = new Dictionary<CustomizationSection, Button>();
        
        // State hook for current section
        private UIStateManager.StateHook<CustomizationSection> sectionState;
        
        // Event for section change
        public event Action<CustomizationSection> OnSectionChanged;
        
        protected override void Awake()
        {
            base.Awake();
            
            // Initialize state hook
            sectionState = UIStateManager.UseState(this, "NavigationSidebar_CurrentSection", currentSection);
            sectionState.Subscribe(OnStateChanged);
        }
        
        protected override void Start()
        {
            base.Start();
            
            // Create title if not assigned
            if (titleText == null)
            {
                GameObject titleGO = new GameObject("Title");
                titleGO.transform.SetParent(transform, false);
                titleText = titleGO.AddComponent<TextMeshProUGUI>();
                
                RectTransform titleRect = titleText.rectTransform;
                titleRect.anchorMin = new Vector2(0, 1);
                titleRect.anchorMax = new Vector2(1, 1);
                titleRect.pivot = new Vector2(0.5f, 1);
                titleRect.sizeDelta = new Vector2(0, 30);
                titleRect.anchoredPosition = new Vector2(0, 0);
            }
            
            // Apply theme to title
            UIThemeManager.Instance.ApplyTextStyle(titleText, UIThemeManager.TextStyle.Header);
            titleText.text = "Customize";
            
            // Create button container if not assigned
            if (buttonContainer == null)
            {
                GameObject containerGO = new GameObject("ButtonContainer");
                containerGO.transform.SetParent(transform, false);
                buttonContainer = containerGO.transform;
                
                RectTransform containerRect = containerGO.AddComponent<RectTransform>();
                containerRect.anchorMin = new Vector2(0, 0);
                containerRect.anchorMax = new Vector2(1, 1);
                containerRect.pivot = new Vector2(0.5f, 0.5f);
                containerRect.offsetMin = new Vector2(0, 40);
                containerRect.offsetMax = new Vector2(0, -10);
                
                // Add vertical layout group
                VerticalLayoutGroup layout = containerGO.AddComponent<VerticalLayoutGroup>();
                layout.spacing = 12;
                layout.padding = new RectOffset(0, 0, 0, 0);
                layout.childAlignment = TextAnchor.UpperCenter;
                layout.childControlHeight = false;
                layout.childControlWidth = true;
                layout.childForceExpandHeight = false;
                layout.childForceExpandWidth = true;
            }
            
            // Create navigation buttons
            CreateNavigationButtons();
            
            // Set initial selection
            SetSection(sectionState.Value);
        }
        
        private void CreateNavigationButtons()
        {
            // Clear any existing buttons
            foreach (Transform child in buttonContainer)
            {
                Destroy(child.gameObject);
            }
            navigationButtons.Clear();
            
            // Create a button for each section
            CreateNavigationButton(CustomizationSection.Appearance, "Appearance");
            CreateNavigationButton(CustomizationSection.Armor, "Armor");
            CreateNavigationButton(CustomizationSection.Presets, "Presets");
            CreateNavigationButton(CustomizationSection.Randomizer, "Randomizer");
        }
        
        private void CreateNavigationButton(CustomizationSection section, string label)
        {
            // Create button GameObject
            GameObject buttonGO = new GameObject($"Button_{section}");
            buttonGO.transform.SetParent(buttonContainer, false);
            
            // Add required components
            RectTransform buttonRect = buttonGO.AddComponent<RectTransform>();
            buttonRect.sizeDelta = new Vector2(0, 40);
            
            Button button = buttonGO.AddComponent<Button>();
            
            // Add visual components
            Image buttonImage = buttonGO.AddComponent<Image>();
            
            // Add text
            GameObject textGO = new GameObject("Text");
            textGO.transform.SetParent(buttonGO.transform, false);
            
            TextMeshProUGUI buttonText = textGO.AddComponent<TextMeshProUGUI>();
            buttonText.text = label;
            buttonText.alignment = TextAlignmentOptions.Center;
            
            RectTransform textRect = buttonText.rectTransform;
            textRect.anchorMin = Vector2.zero;
            textRect.anchorMax = Vector2.one;
            textRect.sizeDelta = Vector2.zero;
            
            // Set button colors
            ColorBlock colors = button.colors;
            colors.normalColor = UIThemeManager.Instance.backgroundPrimaryColor;
            colors.highlightedColor = UIThemeManager.Instance.secondaryColor;
            colors.selectedColor = UIThemeManager.Instance.secondaryColor;
            colors.pressedColor = UIThemeManager.Instance.secondaryColor;
            button.colors = colors;
            
            // Apply theme
            UIThemeManager.Instance.ApplyTextStyle(buttonText, UIThemeManager.TextStyle.Body);
            
            // Add listener
            button.onClick.AddListener(() => SetSection(section));
            
            // Store in dictionary
            navigationButtons[section] = button;
        }
        
        /// <summary>
        /// Set the current navigation section
        /// </summary>
        public void SetSection(CustomizationSection section)
        {
            currentSection = section;
            sectionState.Value = section;
            
            // Update UI to match state
            UpdateButtonStates();
            
            // Notify listeners
            OnSectionChanged?.Invoke(section);
        }
        
        private void OnStateChanged(CustomizationSection newSection)
        {
            if (currentSection != newSection)
            {
                currentSection = newSection;
                UpdateButtonStates();
            }
        }
        
        private void UpdateButtonStates()
        {
            // Update button visuals to reflect current selection
            foreach (var kvp in navigationButtons)
            {
                CustomizationSection section = kvp.Key;
                Button button = kvp.Value;
                
                // Set the visual state of the button
                bool isSelected = (section == currentSection);
                
                // Update button appearance
                Image buttonImage = button.GetComponent<Image>();
                TextMeshProUGUI buttonText = button.GetComponentInChildren<TextMeshProUGUI>();
                
                if (isSelected)
                {
                    buttonImage.color = UIThemeManager.Instance.secondaryColor;
                    if (buttonText != null)
                    {
                        buttonText.color = UIThemeManager.Instance.textPrimaryColor;
                    }
                }
                else
                {
                    buttonImage.color = UIThemeManager.Instance.backgroundPrimaryColor;
                    if (buttonText != null)
                    {
                        buttonText.color = UIThemeManager.Instance.textPrimaryColor;
                    }
                }
            }
        }
        
        /// <summary>
        /// Get the current section
        /// </summary>
        public CustomizationSection GetCurrentSection()
        {
            return currentSection;
        }
    }
} 