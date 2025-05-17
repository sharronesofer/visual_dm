using UnityEngine;
using UnityEngine.UI;
using UnityEngine.EventSystems;
using TMPro;
using System;

namespace VisualDM.UI.Components
{
    /// <summary>
    /// Custom button component that mimics React's button behavior and styling.
    /// </summary>
    public class CustomButton : UIComponent, IPointerEnterHandler, IPointerExitHandler
    {
        [Header("Button Settings")]
        [SerializeField] private string buttonText = "Button";
        [SerializeField] private UIThemeManager.ButtonStyle buttonStyle = UIThemeManager.ButtonStyle.Primary;
        [SerializeField] private bool isSelected = false;
        
        [Header("Accessibility")]
        [SerializeField] private string ariaLabel = "";
        
        // UI Components
        private Button button;
        private Image backgroundImage;
        private TextMeshProUGUI textComponent;
        
        // Events
        public event Action OnClick;
        
        protected override void Awake()
        {
            base.Awake();
            
            // Get or add button component
            button = GetComponent<Button>();
            if (button == null)
            {
                button = gameObject.AddComponent<Button>();
            }
            
            // Get or add image component for background
            backgroundImage = GetComponent<Image>();
            if (backgroundImage == null)
            {
                backgroundImage = gameObject.AddComponent<Image>();
            }
            
            // Set up text component
            SetupTextComponent();
            
            // Add click listener
            button.onClick.AddListener(HandleClick);
        }
        
        protected override void Start()
        {
            base.Start();
            
            // Apply theme
            ApplyTheme();
            
            // Apply accessibility attributes
            ApplyAccessibility();
        }
        
        private void SetupTextComponent()
        {
            // Check if there's already a text component
            textComponent = GetComponentInChildren<TextMeshProUGUI>();
            
            if (textComponent == null)
            {
                // Create text game object
                GameObject textGO = new GameObject("ButtonText");
                textGO.transform.SetParent(transform, false);
                
                // Add text component
                textComponent = textGO.AddComponent<TextMeshProUGUI>();
                
                // Setup text rect transform
                RectTransform textRect = textComponent.rectTransform;
                textRect.anchorMin = Vector2.zero;
                textRect.anchorMax = Vector2.one;
                textRect.sizeDelta = Vector2.zero;
                textRect.offsetMin = new Vector2(10, 5);
                textRect.offsetMax = new Vector2(-10, -5);
            }
            
            // Set initial text
            textComponent.text = buttonText;
            textComponent.alignment = TextAlignmentOptions.Center;
        }
        
        /// <summary>
        /// Apply theme styling to the button
        /// </summary>
        private void ApplyTheme()
        {
            if (backgroundImage != null && textComponent != null)
            {
                UIThemeManager.ButtonStyle style = isSelected ? UIThemeManager.ButtonStyle.Selected : buttonStyle;
                UIThemeManager.Instance.ApplyButtonStyle(button, style);
                UIThemeManager.Instance.ApplyTextStyle(textComponent, UIThemeManager.TextStyle.Body);
            }
        }
        
        /// <summary>
        /// Apply accessibility features
        /// </summary>
        private void ApplyAccessibility()
        {
            // Add accessibility features similar to aria-label in React
            if (string.IsNullOrEmpty(ariaLabel))
            {
                ariaLabel = buttonText;
            }
            
            // In a real implementation, you'd integrate with Unity's UI Accessibility Plugin
            // or a custom accessibility system
        }
        
        /// <summary>
        /// Handle button click
        /// </summary>
        private void HandleClick()
        {
            OnClick?.Invoke();
        }
        
        #region Public Methods
        
        /// <summary>
        /// Set the button text
        /// </summary>
        public void SetText(string text)
        {
            buttonText = text;
            if (textComponent != null)
            {
                textComponent.text = text;
            }
        }
        
        /// <summary>
        /// Set the selected state of the button
        /// </summary>
        public void SetSelected(bool selected)
        {
            isSelected = selected;
            ApplyTheme();
        }
        
        /// <summary>
        /// Set the button style
        /// </summary>
        public void SetStyle(UIThemeManager.ButtonStyle style)
        {
            buttonStyle = style;
            ApplyTheme();
        }
        
        /// <summary>
        /// Set the aria label for accessibility
        /// </summary>
        public void SetAriaLabel(string label)
        {
            ariaLabel = label;
            ApplyAccessibility();
        }
        
        #endregion
        
        #region IPointerHandlers
        
        public void OnPointerEnter(PointerEventData eventData)
        {
            // Handle hover state (if needed beyond Unity's built-in functionality)
        }
        
        public void OnPointerExit(PointerEventData eventData)
        {
            // Handle exit hover state (if needed beyond Unity's built-in functionality)
        }
        
        #endregion
        
        protected override void UpdateInteractability()
        {
            base.UpdateInteractability();
            
            if (button != null)
            {
                button.interactable = interactable;
            }
        }
    }
} 