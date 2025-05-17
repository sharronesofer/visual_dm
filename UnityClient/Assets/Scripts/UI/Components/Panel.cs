using UnityEngine;
using UnityEngine.UI;
using TMPro;
using System;

namespace VisualDM.UI.Components
{
    /// <summary>
    /// Reusable panel component that can be used for different UI panels.
    /// Similar to React container components.
    /// </summary>
    public class Panel : UIComponent
    {
        [Header("Panel Settings")]
        [SerializeField] private string title = "Panel";
        [SerializeField] private bool showTitle = true;
        [SerializeField] private UIThemeManager.PanelStyle panelStyle = UIThemeManager.PanelStyle.Primary;
        
        [Header("Layout Settings")]
        [SerializeField] private bool useVerticalLayout = true;
        [SerializeField] private float spacing = 10f;
        [SerializeField] private RectOffset padding = new RectOffset(10, 10, 10, 10);
        
        // UI Components
        private Image backgroundImage;
        private TextMeshProUGUI titleText;
        private RectTransform contentContainer;
        
        protected override void Awake()
        {
            base.Awake();
            
            // Get or add image component for background
            backgroundImage = GetComponent<Image>();
            if (backgroundImage == null)
            {
                backgroundImage = gameObject.AddComponent<Image>();
            }
            
            // Setup panel
            SetupPanel();
        }
        
        protected override void Start()
        {
            base.Start();
            
            // Apply theme
            ApplyTheme();
        }
        
        private void SetupPanel()
        {
            // Setup title if needed
            if (showTitle)
            {
                SetupTitleArea();
            }
            
            // Setup content container
            SetupContentContainer();
        }
        
        private void SetupTitleArea()
        {
            // Create title area
            GameObject titleGO = new GameObject("TitleArea");
            titleGO.transform.SetParent(transform, false);
            
            RectTransform titleRect = titleGO.AddComponent<RectTransform>();
            titleRect.anchorMin = new Vector2(0, 1);
            titleRect.anchorMax = new Vector2(1, 1);
            titleRect.pivot = new Vector2(0.5f, 1);
            titleRect.sizeDelta = new Vector2(0, 40);
            titleRect.anchoredPosition = Vector2.zero;
            
            // Add title text
            titleText = titleGO.AddComponent<TextMeshProUGUI>();
            titleText.text = title;
            titleText.alignment = TextAlignmentOptions.Center;
            titleText.verticalAlignment = VerticalAlignmentOptions.Middle;
        }
        
        private void SetupContentContainer()
        {
            // Create content container
            GameObject containerGO = new GameObject("ContentContainer");
            containerGO.transform.SetParent(transform, false);
            
            contentContainer = containerGO.AddComponent<RectTransform>();
            
            // Position based on whether we have a title or not
            if (showTitle)
            {
                contentContainer.anchorMin = new Vector2(0, 0);
                contentContainer.anchorMax = new Vector2(1, 1);
                contentContainer.pivot = new Vector2(0.5f, 0.5f);
                contentContainer.offsetMin = new Vector2(0, 0);
                contentContainer.offsetMax = new Vector2(0, -40); // Account for title height
            }
            else
            {
                contentContainer.anchorMin = Vector2.zero;
                contentContainer.anchorMax = Vector2.one;
                contentContainer.pivot = new Vector2(0.5f, 0.5f);
                contentContainer.offsetMin = Vector2.zero;
                contentContainer.offsetMax = Vector2.zero;
            }
            
            // Add layout group if needed
            if (useVerticalLayout)
            {
                VerticalLayoutGroup layout = containerGO.AddComponent<VerticalLayoutGroup>();
                layout.spacing = spacing;
                layout.padding = padding;
                layout.childAlignment = TextAnchor.UpperCenter;
                layout.childControlHeight = false;
                layout.childControlWidth = true;
                layout.childForceExpandHeight = false;
                layout.childForceExpandWidth = true;
            }
            else
            {
                HorizontalLayoutGroup layout = containerGO.AddComponent<HorizontalLayoutGroup>();
                layout.spacing = spacing;
                layout.padding = padding;
                layout.childAlignment = TextAnchor.UpperCenter;
                layout.childControlHeight = true;
                layout.childControlWidth = false;
                layout.childForceExpandHeight = true;
                layout.childForceExpandWidth = false;
            }
        }
        
        /// <summary>
        /// Apply theme styling to the panel
        /// </summary>
        private void ApplyTheme()
        {
            // Apply panel style
            if (backgroundImage != null)
            {
                UIThemeManager.Instance.ApplyPanelStyle(backgroundImage, panelStyle);
            }
            
            // Apply title style
            if (titleText != null)
            {
                UIThemeManager.Instance.ApplyTextStyle(titleText, UIThemeManager.TextStyle.Header);
            }
        }
        
        #region Public Methods
        
        /// <summary>
        /// Set the panel title
        /// </summary>
        public void SetTitle(string newTitle)
        {
            title = newTitle;
            if (titleText != null)
            {
                titleText.text = newTitle;
            }
        }
        
        /// <summary>
        /// Show or hide the title area
        /// </summary>
        public void SetTitleVisibility(bool visible)
        {
            showTitle = visible;
            
            if (titleText != null)
            {
                titleText.transform.parent.gameObject.SetActive(visible);
            }
            
            // Adjust content container
            if (contentContainer != null)
            {
                if (visible)
                {
                    contentContainer.offsetMax = new Vector2(0, -40); // Account for title height
                }
                else
                {
                    contentContainer.offsetMax = Vector2.zero;
                }
            }
        }
        
        /// <summary>
        /// Set the panel style
        /// </summary>
        public void SetPanelStyle(UIThemeManager.PanelStyle style)
        {
            panelStyle = style;
            ApplyTheme();
        }
        
        /// <summary>
        /// Get the content container transform for adding child elements
        /// </summary>
        public RectTransform GetContentContainer()
        {
            return contentContainer;
        }
        
        /// <summary>
        /// Add a child UI element to the panel
        /// </summary>
        public void AddUIElement(UIComponent element)
        {
            if (element != null && contentContainer != null)
            {
                element.transform.SetParent(contentContainer, false);
            }
        }
        
        /// <summary>
        /// Clear all content from the panel
        /// </summary>
        public void ClearContent()
        {
            if (contentContainer != null)
            {
                foreach (Transform child in contentContainer)
                {
                    Destroy(child.gameObject);
                }
            }
        }
        
        #endregion
    }
} 