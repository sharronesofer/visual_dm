using UnityEngine;
using UnityEngine.UI;
using System.Collections.Generic;

namespace VDM.UI.Components
{
    /// <summary>
    /// Responsive layout component that adjusts UI elements based on screen size and orientation.
    /// Provides breakpoint-based responsive design for Unity UI.
    /// </summary>
    public class ResponsiveLayout : MonoBehaviour
    {
        [Header("Responsive Settings")]
        [SerializeField] private bool enableResponsiveLayout = true;
        [SerializeField] private bool updateOnScreenChange = true;
        [SerializeField] private float updateInterval = 0.1f;
        
        [Header("Breakpoints")]
        [SerializeField] private List<ResponsiveBreakpoint> breakpoints = new List<ResponsiveBreakpoint>();
        
        [Header("Layout Components")]
        [SerializeField] private List<ResponsiveElement> responsiveElements = new List<ResponsiveElement>();
        
        // State
        private Vector2 lastScreenSize;
        private ScreenOrientation lastOrientation;
        private ResponsiveBreakpoint currentBreakpoint;
        private float lastUpdateTime;
        
        // Events
        public System.Action<ResponsiveBreakpoint> OnBreakpointChanged;
        public System.Action<Vector2> OnScreenSizeChanged;
        
        private void Awake()
        {
            // Initialize default breakpoints if none are set
            if (breakpoints.Count == 0)
            {
                InitializeDefaultBreakpoints();
            }
            
            // Sort breakpoints by width
            breakpoints.Sort((a, b) => a.minWidth.CompareTo(b.minWidth));
        }
        
        private void Start()
        {
            // Initial layout update
            UpdateLayout(true);
        }
        
        private void Update()
        {
            if (!enableResponsiveLayout || !updateOnScreenChange) return;
            
            // Check if enough time has passed since last update
            if (Time.time - lastUpdateTime < updateInterval) return;
            
            // Check for screen size or orientation changes
            Vector2 currentScreenSize = new Vector2(Screen.width, Screen.height);
            ScreenOrientation currentOrientation = Screen.orientation;
            
            if (currentScreenSize != lastScreenSize || currentOrientation != lastOrientation)
            {
                UpdateLayout();
                lastScreenSize = currentScreenSize;
                lastOrientation = currentOrientation;
                lastUpdateTime = Time.time;
                
                OnScreenSizeChanged?.Invoke(currentScreenSize);
            }
        }
        
        /// <summary>
        /// Initialize default responsive breakpoints.
        /// </summary>
        private void InitializeDefaultBreakpoints()
        {
            breakpoints = new List<ResponsiveBreakpoint>
            {
                new ResponsiveBreakpoint
                {
                    name = "Mobile",
                    minWidth = 0,
                    maxWidth = 768,
                    scaleFactor = 1.0f,
                    layoutType = LayoutType.Vertical
                },
                new ResponsiveBreakpoint
                {
                    name = "Tablet",
                    minWidth = 769,
                    maxWidth = 1024,
                    scaleFactor = 1.1f,
                    layoutType = LayoutType.Mixed
                },
                new ResponsiveBreakpoint
                {
                    name = "Desktop",
                    minWidth = 1025,
                    maxWidth = 1920,
                    scaleFactor = 1.2f,
                    layoutType = LayoutType.Horizontal
                },
                new ResponsiveBreakpoint
                {
                    name = "Large Desktop",
                    minWidth = 1921,
                    maxWidth = int.MaxValue,
                    scaleFactor = 1.3f,
                    layoutType = LayoutType.Horizontal
                }
            };
        }
        
        /// <summary>
        /// Update the layout based on current screen size.
        /// </summary>
        public void UpdateLayout(bool forceUpdate = false)
        {
            if (!enableResponsiveLayout && !forceUpdate) return;
            
            // Determine current breakpoint
            ResponsiveBreakpoint newBreakpoint = GetCurrentBreakpoint();
            
            // Check if breakpoint changed
            bool breakpointChanged = currentBreakpoint == null || 
                                   currentBreakpoint.name != newBreakpoint.name;
            
            if (breakpointChanged || forceUpdate)
            {
                currentBreakpoint = newBreakpoint;
                ApplyBreakpoint(currentBreakpoint);
                
                if (breakpointChanged)
                {
                    OnBreakpointChanged?.Invoke(currentBreakpoint);
                }
            }
            
            // Update responsive elements
            UpdateResponsiveElements();
        }
        
        /// <summary>
        /// Get the current breakpoint based on screen width.
        /// </summary>
        private ResponsiveBreakpoint GetCurrentBreakpoint()
        {
            int screenWidth = Screen.width;
            
            for (int i = breakpoints.Count - 1; i >= 0; i--)
            {
                var breakpoint = breakpoints[i];
                if (screenWidth >= breakpoint.minWidth && screenWidth <= breakpoint.maxWidth)
                {
                    return breakpoint;
                }
            }
            
            // Return the first breakpoint as fallback
            return breakpoints.Count > 0 ? breakpoints[0] : new ResponsiveBreakpoint();
        }
        
        /// <summary>
        /// Apply the current breakpoint settings.
        /// </summary>
        private void ApplyBreakpoint(ResponsiveBreakpoint breakpoint)
        {
            // Apply canvas scaler settings
            CanvasScaler canvasScaler = GetComponentInParent<CanvasScaler>();
            if (canvasScaler != null)
            {
                canvasScaler.scaleFactor = breakpoint.scaleFactor;
            }
            
            // Apply layout group settings
            ApplyLayoutGroupSettings(breakpoint);
        }
        
        /// <summary>
        /// Apply layout group settings based on breakpoint.
        /// </summary>
        private void ApplyLayoutGroupSettings(ResponsiveBreakpoint breakpoint)
        {
            // Find layout groups in children
            var layoutGroups = GetComponentsInChildren<LayoutGroup>();
            
            foreach (var layoutGroup in layoutGroups)
            {
                if (layoutGroup is HorizontalLayoutGroup horizontalLayout)
                {
                    // Adjust horizontal layout based on breakpoint
                    if (breakpoint.layoutType == LayoutType.Vertical)
                    {
                        // Convert to vertical layout for small screens
                        ConvertToVerticalLayout(horizontalLayout);
                    }
                }
                else if (layoutGroup is VerticalLayoutGroup verticalLayout)
                {
                    // Adjust vertical layout based on breakpoint
                    if (breakpoint.layoutType == LayoutType.Horizontal)
                    {
                        // Convert to horizontal layout for large screens
                        ConvertToHorizontalLayout(verticalLayout);
                    }
                }
                else if (layoutGroup is GridLayoutGroup gridLayout)
                {
                    // Adjust grid layout based on breakpoint
                    AdjustGridLayout(gridLayout, breakpoint);
                }
            }
        }
        
        /// <summary>
        /// Convert horizontal layout to vertical layout.
        /// </summary>
        private void ConvertToVerticalLayout(HorizontalLayoutGroup horizontalLayout)
        {
            GameObject parent = horizontalLayout.gameObject;
            
            // Store settings
            var padding = horizontalLayout.padding;
            var spacing = horizontalLayout.spacing;
            var childAlignment = horizontalLayout.childAlignment;
            var childControlWidth = horizontalLayout.childControlWidth;
            var childControlHeight = horizontalLayout.childControlHeight;
            var childForceExpandWidth = horizontalLayout.childForceExpandWidth;
            var childForceExpandHeight = horizontalLayout.childForceExpandHeight;
            
            // Remove horizontal layout
            DestroyImmediate(horizontalLayout);
            
            // Add vertical layout
            var verticalLayout = parent.AddComponent<VerticalLayoutGroup>();
            verticalLayout.padding = padding;
            verticalLayout.spacing = spacing;
            verticalLayout.childAlignment = childAlignment;
            verticalLayout.childControlWidth = childControlWidth;
            verticalLayout.childControlHeight = childControlHeight;
            verticalLayout.childForceExpandWidth = childForceExpandWidth;
            verticalLayout.childForceExpandHeight = childForceExpandHeight;
        }
        
        /// <summary>
        /// Convert vertical layout to horizontal layout.
        /// </summary>
        private void ConvertToHorizontalLayout(VerticalLayoutGroup verticalLayout)
        {
            GameObject parent = verticalLayout.gameObject;
            
            // Store settings
            var padding = verticalLayout.padding;
            var spacing = verticalLayout.spacing;
            var childAlignment = verticalLayout.childAlignment;
            var childControlWidth = verticalLayout.childControlWidth;
            var childControlHeight = verticalLayout.childControlHeight;
            var childForceExpandWidth = verticalLayout.childForceExpandWidth;
            var childForceExpandHeight = verticalLayout.childForceExpandHeight;
            
            // Remove vertical layout
            DestroyImmediate(verticalLayout);
            
            // Add horizontal layout
            var horizontalLayout = parent.AddComponent<HorizontalLayoutGroup>();
            horizontalLayout.padding = padding;
            horizontalLayout.spacing = spacing;
            horizontalLayout.childAlignment = childAlignment;
            horizontalLayout.childControlWidth = childControlWidth;
            horizontalLayout.childControlHeight = childControlHeight;
            horizontalLayout.childForceExpandWidth = childForceExpandWidth;
            horizontalLayout.childForceExpandHeight = childForceExpandHeight;
        }
        
        /// <summary>
        /// Adjust grid layout based on breakpoint.
        /// </summary>
        private void AdjustGridLayout(GridLayoutGroup gridLayout, ResponsiveBreakpoint breakpoint)
        {
            // Adjust cell size based on screen size
            float screenWidth = Screen.width;
            float availableWidth = screenWidth - gridLayout.padding.left - gridLayout.padding.right;
            
            // Calculate optimal cell count based on breakpoint
            int cellCount = breakpoint.layoutType switch
            {
                LayoutType.Vertical => 1,
                LayoutType.Mixed => 2,
                LayoutType.Horizontal => Mathf.Max(3, Mathf.FloorToInt(availableWidth / 200f)),
                _ => 2
            };
            
            // Calculate cell size
            float cellWidth = (availableWidth - (gridLayout.spacing.x * (cellCount - 1))) / cellCount;
            gridLayout.cellSize = new Vector2(cellWidth, gridLayout.cellSize.y);
        }
        
        /// <summary>
        /// Update all responsive elements.
        /// </summary>
        private void UpdateResponsiveElements()
        {
            foreach (var element in responsiveElements)
            {
                if (element != null && element.targetTransform != null)
                {
                    ApplyResponsiveElement(element);
                }
            }
        }
        
        /// <summary>
        /// Apply responsive settings to an element.
        /// </summary>
        private void ApplyResponsiveElement(ResponsiveElement element)
        {
            if (currentBreakpoint == null) return;
            
            RectTransform rectTransform = element.targetTransform;
            
            // Find matching responsive setting for current breakpoint
            ResponsiveElementSetting setting = null;
            foreach (var s in element.settings)
            {
                if (s.breakpointName == currentBreakpoint.name)
                {
                    setting = s;
                    break;
                }
            }
            
            // Apply default setting if no specific setting found
            if (setting == null && element.settings.Count > 0)
            {
                setting = element.settings[0];
            }
            
            if (setting == null) return;
            
            // Apply size
            if (setting.overrideSize)
            {
                rectTransform.sizeDelta = setting.size;
            }
            
            // Apply position
            if (setting.overridePosition)
            {
                rectTransform.anchoredPosition = setting.position;
            }
            
            // Apply anchors
            if (setting.overrideAnchors)
            {
                rectTransform.anchorMin = setting.anchorMin;
                rectTransform.anchorMax = setting.anchorMax;
            }
            
            // Apply visibility
            if (setting.overrideVisibility)
            {
                element.targetTransform.gameObject.SetActive(setting.isVisible);
            }
        }
        
        /// <summary>
        /// Add a responsive element to be managed.
        /// </summary>
        public void AddResponsiveElement(ResponsiveElement element)
        {
            if (!responsiveElements.Contains(element))
            {
                responsiveElements.Add(element);
            }
        }
        
        /// <summary>
        /// Remove a responsive element from management.
        /// </summary>
        public void RemoveResponsiveElement(ResponsiveElement element)
        {
            responsiveElements.Remove(element);
        }
        
        /// <summary>
        /// Get the current breakpoint.
        /// </summary>
        public ResponsiveBreakpoint GetCurrentBreakpointInfo()
        {
            return currentBreakpoint;
        }
        
        /// <summary>
        /// Force a layout update.
        /// </summary>
        public void ForceUpdate()
        {
            UpdateLayout(true);
        }
    }
    
    /// <summary>
    /// Responsive breakpoint configuration.
    /// </summary>
    [System.Serializable]
    public class ResponsiveBreakpoint
    {
        public string name = "Default";
        public int minWidth = 0;
        public int maxWidth = int.MaxValue;
        public float scaleFactor = 1.0f;
        public LayoutType layoutType = LayoutType.Mixed;
    }
    
    /// <summary>
    /// Layout types for responsive design.
    /// </summary>
    public enum LayoutType
    {
        Vertical,
        Horizontal,
        Mixed
    }
    
    /// <summary>
    /// Responsive element configuration.
    /// </summary>
    [System.Serializable]
    public class ResponsiveElement
    {
        public RectTransform targetTransform;
        public List<ResponsiveElementSetting> settings = new List<ResponsiveElementSetting>();
    }
    
    /// <summary>
    /// Settings for a responsive element at a specific breakpoint.
    /// </summary>
    [System.Serializable]
    public class ResponsiveElementSetting
    {
        public string breakpointName = "Default";
        
        [Header("Size")]
        public bool overrideSize = false;
        public Vector2 size = Vector2.zero;
        
        [Header("Position")]
        public bool overridePosition = false;
        public Vector2 position = Vector2.zero;
        
        [Header("Anchors")]
        public bool overrideAnchors = false;
        public Vector2 anchorMin = Vector2.zero;
        public Vector2 anchorMax = Vector2.one;
        
        [Header("Visibility")]
        public bool overrideVisibility = false;
        public bool isVisible = true;
    }
} 