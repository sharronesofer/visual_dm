using UnityEngine;
using UnityEngine.UI;
using System.Collections.Generic;
using TMPro;

namespace VDM.UI.Themes
{
    /// <summary>
    /// Theme management system for Visual DM.
    /// Handles dark/light themes and visual styling across the entire UI.
    /// </summary>
    public class ThemeManager : MonoBehaviour
    {
        [Header("Theme Configuration")]
        [SerializeField] private List<UITheme> availableThemes = new List<UITheme>();
        [SerializeField] private string defaultThemeName = "Dark";
        [SerializeField] private bool applyThemeOnStart = true;
        [SerializeField] private bool saveThemePreference = true;
        
        [Header("Auto-Discovery")]
        [SerializeField] private bool autoDiscoverThemeableComponents = true;
        [SerializeField] private bool includeInactiveObjects = false;
        
        // Singleton
        public static ThemeManager Instance { get; private set; }
        
        // Events
        public System.Action<UITheme> OnThemeChanged;
        public System.Action<UITheme> OnThemeApplied;
        
        // State
        private UITheme currentTheme;
        private List<IThemeable> themeableComponents = new List<IThemeable>();
        private Dictionary<string, UITheme> themesByName = new Dictionary<string, UITheme>();
        
        // Constants
        private const string THEME_PREFERENCE_KEY = "VDM_SelectedTheme";
        
        public UITheme CurrentTheme => currentTheme;
        public List<UITheme> AvailableThemes => new List<UITheme>(availableThemes);
        
        private void Awake()
        {
            // Singleton pattern
            if (Instance != null && Instance != this)
            {
                Destroy(gameObject);
                return;
            }
            
            Instance = this;
            DontDestroyOnLoad(gameObject);
            
            // Initialize themes
            InitializeThemes();
        }
        
        private void Start()
        {
            if (applyThemeOnStart)
            {
                ApplyDefaultTheme();
            }
        }
        
        /// <summary>
        /// Initialize theme system and discover themeable components.
        /// </summary>
        private void InitializeThemes()
        {
            // Create default themes if none are configured
            if (availableThemes.Count == 0)
            {
                CreateDefaultThemes();
            }
            
            // Build theme lookup dictionary
            themesByName.Clear();
            foreach (var theme in availableThemes)
            {
                if (!string.IsNullOrEmpty(theme.themeName))
                {
                    themesByName[theme.themeName] = theme;
                }
            }
            
            // Discover themeable components
            if (autoDiscoverThemeableComponents)
            {
                DiscoverThemeableComponents();
            }
        }
        
        /// <summary>
        /// Create default light and dark themes.
        /// </summary>
        private void CreateDefaultThemes()
        {
            // Dark Theme
            var darkTheme = new UITheme
            {
                themeName = "Dark",
                displayName = "Dark Theme",
                backgroundColor = new Color(0.1f, 0.1f, 0.1f, 1f),
                primaryColor = new Color(0.2f, 0.6f, 1f, 1f),
                secondaryColor = new Color(0.3f, 0.3f, 0.3f, 1f),
                accentColor = new Color(1f, 0.6f, 0.2f, 1f),
                textColor = new Color(0.9f, 0.9f, 0.9f, 1f),
                textColorSecondary = new Color(0.7f, 0.7f, 0.7f, 1f),
                buttonColor = new Color(0.25f, 0.25f, 0.25f, 1f),
                buttonHoverColor = new Color(0.35f, 0.35f, 0.35f, 1f),
                buttonPressedColor = new Color(0.15f, 0.15f, 0.15f, 1f),
                panelColor = new Color(0.15f, 0.15f, 0.15f, 0.95f),
                borderColor = new Color(0.4f, 0.4f, 0.4f, 1f),
                shadowColor = new Color(0f, 0f, 0f, 0.5f)
            };
            
            // Light Theme
            var lightTheme = new UITheme
            {
                themeName = "Light",
                displayName = "Light Theme",
                backgroundColor = new Color(0.95f, 0.95f, 0.95f, 1f),
                primaryColor = new Color(0.2f, 0.6f, 1f, 1f),
                secondaryColor = new Color(0.7f, 0.7f, 0.7f, 1f),
                accentColor = new Color(1f, 0.6f, 0.2f, 1f),
                textColor = new Color(0.1f, 0.1f, 0.1f, 1f),
                textColorSecondary = new Color(0.3f, 0.3f, 0.3f, 1f),
                buttonColor = new Color(0.9f, 0.9f, 0.9f, 1f),
                buttonHoverColor = new Color(0.8f, 0.8f, 0.8f, 1f),
                buttonPressedColor = new Color(0.7f, 0.7f, 0.7f, 1f),
                panelColor = new Color(1f, 1f, 1f, 0.95f),
                borderColor = new Color(0.6f, 0.6f, 0.6f, 1f),
                shadowColor = new Color(0f, 0f, 0f, 0.3f)
            };
            
            availableThemes.Add(darkTheme);
            availableThemes.Add(lightTheme);
        }
        
        /// <summary>
        /// Discover all themeable components in the scene.
        /// </summary>
        private void DiscoverThemeableComponents()
        {
            themeableComponents.Clear();
            
            // Find all IThemeable components
            var themeableObjects = FindObjectsOfType<MonoBehaviour>(includeInactiveObjects);
            foreach (var obj in themeableObjects)
            {
                if (obj is IThemeable themeable)
                {
                    themeableComponents.Add(themeable);
                }
            }
            
            // Find all UI components that can be themed
            DiscoverUIComponents();
        }
        
        /// <summary>
        /// Discover standard UI components that can be themed.
        /// </summary>
        private void DiscoverUIComponents()
        {
            // Find Images
            var images = FindObjectsOfType<Image>(includeInactiveObjects);
            foreach (var image in images)
            {
                var themeableImage = image.GetComponent<ThemeableImage>();
                if (themeableImage == null)
                {
                    themeableImage = image.gameObject.AddComponent<ThemeableImage>();
                }
                themeableComponents.Add(themeableImage);
            }
            
            // Find Text components
            var texts = FindObjectsOfType<TextMeshProUGUI>(includeInactiveObjects);
            foreach (var text in texts)
            {
                var themeableText = text.GetComponent<ThemeableText>();
                if (themeableText == null)
                {
                    themeableText = text.gameObject.AddComponent<ThemeableText>();
                }
                themeableComponents.Add(themeableText);
            }
            
            // Find Buttons
            var buttons = FindObjectsOfType<Button>(includeInactiveObjects);
            foreach (var button in buttons)
            {
                var themeableButton = button.GetComponent<ThemeableButton>();
                if (themeableButton == null)
                {
                    themeableButton = button.gameObject.AddComponent<ThemeableButton>();
                }
                themeableComponents.Add(themeableButton);
            }
        }
        
        /// <summary>
        /// Apply the default theme.
        /// </summary>
        private void ApplyDefaultTheme()
        {
            string themeName = defaultThemeName;
            
            // Load saved theme preference
            if (saveThemePreference && PlayerPrefs.HasKey(THEME_PREFERENCE_KEY))
            {
                themeName = PlayerPrefs.GetString(THEME_PREFERENCE_KEY);
            }
            
            ApplyTheme(themeName);
        }
        
        /// <summary>
        /// Apply a theme by name.
        /// </summary>
        public void ApplyTheme(string themeName)
        {
            if (themesByName.TryGetValue(themeName, out UITheme theme))
            {
                ApplyTheme(theme);
            }
            else
            {
                Debug.LogWarning($"ThemeManager: Theme '{themeName}' not found.");
            }
        }
        
        /// <summary>
        /// Apply a specific theme.
        /// </summary>
        public void ApplyTheme(UITheme theme)
        {
            if (theme == null)
            {
                Debug.LogError("ThemeManager: Cannot apply null theme.");
                return;
            }
            
            var previousTheme = currentTheme;
            currentTheme = theme;
            
            // Apply theme to all themeable components
            foreach (var component in themeableComponents)
            {
                if (component != null)
                {
                    component.ApplyTheme(theme);
                }
            }
            
            // Save theme preference
            if (saveThemePreference)
            {
                PlayerPrefs.SetString(THEME_PREFERENCE_KEY, theme.themeName);
                PlayerPrefs.Save();
            }
            
            // Trigger events
            if (previousTheme != theme)
            {
                OnThemeChanged?.Invoke(theme);
            }
            OnThemeApplied?.Invoke(theme);
            
            Debug.Log($"ThemeManager: Applied theme '{theme.themeName}'");
        }
        
        /// <summary>
        /// Toggle between light and dark themes.
        /// </summary>
        public void ToggleTheme()
        {
            if (currentTheme == null) return;
            
            string targetTheme = currentTheme.themeName == "Dark" ? "Light" : "Dark";
            ApplyTheme(targetTheme);
        }
        
        /// <summary>
        /// Register a themeable component.
        /// </summary>
        public void RegisterThemeableComponent(IThemeable component)
        {
            if (component != null && !themeableComponents.Contains(component))
            {
                themeableComponents.Add(component);
                
                // Apply current theme to new component
                if (currentTheme != null)
                {
                    component.ApplyTheme(currentTheme);
                }
            }
        }
        
        /// <summary>
        /// Unregister a themeable component.
        /// </summary>
        public void UnregisterThemeableComponent(IThemeable component)
        {
            themeableComponents.Remove(component);
        }
        
        /// <summary>
        /// Get a theme by name.
        /// </summary>
        public UITheme GetTheme(string themeName)
        {
            themesByName.TryGetValue(themeName, out UITheme theme);
            return theme;
        }
        
        /// <summary>
        /// Add a new theme.
        /// </summary>
        public void AddTheme(UITheme theme)
        {
            if (theme == null || string.IsNullOrEmpty(theme.themeName)) return;
            
            if (!availableThemes.Contains(theme))
            {
                availableThemes.Add(theme);
            }
            
            themesByName[theme.themeName] = theme;
        }
        
        /// <summary>
        /// Remove a theme.
        /// </summary>
        public void RemoveTheme(string themeName)
        {
            if (themesByName.TryGetValue(themeName, out UITheme theme))
            {
                availableThemes.Remove(theme);
                themesByName.Remove(themeName);
            }
        }
        
        /// <summary>
        /// Refresh all themeable components.
        /// </summary>
        public void RefreshTheme()
        {
            if (currentTheme != null)
            {
                ApplyTheme(currentTheme);
            }
        }
        
        /// <summary>
        /// Rediscover themeable components.
        /// </summary>
        public void RediscoverComponents()
        {
            DiscoverThemeableComponents();
            RefreshTheme();
        }
    }
    
    /// <summary>
    /// Interface for components that can be themed.
    /// </summary>
    public interface IThemeable
    {
        void ApplyTheme(UITheme theme);
    }
    
    /// <summary>
    /// UI Theme configuration.
    /// </summary>
    [System.Serializable]
    public class UITheme
    {
        [Header("Theme Info")]
        public string themeName = "Default";
        public string displayName = "Default Theme";
        public string description = "";
        
        [Header("Core Colors")]
        public Color backgroundColor = Color.white;
        public Color primaryColor = Color.blue;
        public Color secondaryColor = Color.gray;
        public Color accentColor = Color.yellow;
        
        [Header("Text Colors")]
        public Color textColor = Color.black;
        public Color textColorSecondary = Color.gray;
        
        [Header("Button Colors")]
        public Color buttonColor = Color.white;
        public Color buttonHoverColor = Color.gray;
        public Color buttonPressedColor = Color.darkGray;
        
        [Header("Panel Colors")]
        public Color panelColor = Color.white;
        public Color borderColor = Color.gray;
        public Color shadowColor = Color.black;
        
        [Header("State Colors")]
        public Color successColor = Color.green;
        public Color warningColor = Color.yellow;
        public Color errorColor = Color.red;
        public Color infoColor = Color.blue;
        
        [Header("Typography")]
        public TMP_FontAsset primaryFont;
        public TMP_FontAsset secondaryFont;
        public float baseFontSize = 14f;
        
        [Header("Spacing")]
        public float baseSpacing = 8f;
        public float basePadding = 16f;
        public float baseMargin = 8f;
        
        [Header("Effects")]
        public float cornerRadius = 4f;
        public float shadowOffset = 2f;
        public float shadowBlur = 4f;
    }
    
    /// <summary>
    /// Themeable Image component.
    /// </summary>
    public class ThemeableImage : MonoBehaviour, IThemeable
    {
        [Header("Theme Settings")]
        [SerializeField] private ThemeColorType colorType = ThemeColorType.Panel;
        [SerializeField] private bool useThemeColor = true;
        
        private Image image;
        
        private void Awake()
        {
            image = GetComponent<Image>();
            
            // Register with theme manager
            if (ThemeManager.Instance != null)
            {
                ThemeManager.Instance.RegisterThemeableComponent(this);
            }
        }
        
        private void OnDestroy()
        {
            // Unregister from theme manager
            if (ThemeManager.Instance != null)
            {
                ThemeManager.Instance.UnregisterThemeableComponent(this);
            }
        }
        
        public void ApplyTheme(UITheme theme)
        {
            if (!useThemeColor || image == null || theme == null) return;
            
            Color themeColor = GetThemeColor(theme, colorType);
            image.color = themeColor;
        }
        
        private Color GetThemeColor(UITheme theme, ThemeColorType type)
        {
            return type switch
            {
                ThemeColorType.Background => theme.backgroundColor,
                ThemeColorType.Primary => theme.primaryColor,
                ThemeColorType.Secondary => theme.secondaryColor,
                ThemeColorType.Accent => theme.accentColor,
                ThemeColorType.Panel => theme.panelColor,
                ThemeColorType.Button => theme.buttonColor,
                ThemeColorType.Border => theme.borderColor,
                ThemeColorType.Success => theme.successColor,
                ThemeColorType.Warning => theme.warningColor,
                ThemeColorType.Error => theme.errorColor,
                ThemeColorType.Info => theme.infoColor,
                _ => theme.backgroundColor
            };
        }
    }
    
    /// <summary>
    /// Themeable Text component.
    /// </summary>
    public class ThemeableText : MonoBehaviour, IThemeable
    {
        [Header("Theme Settings")]
        [SerializeField] private ThemeTextType textType = ThemeTextType.Primary;
        [SerializeField] private bool useThemeColor = true;
        [SerializeField] private bool useThemeFont = false;
        
        private TextMeshProUGUI text;
        
        private void Awake()
        {
            text = GetComponent<TextMeshProUGUI>();
            
            // Register with theme manager
            if (ThemeManager.Instance != null)
            {
                ThemeManager.Instance.RegisterThemeableComponent(this);
            }
        }
        
        private void OnDestroy()
        {
            // Unregister from theme manager
            if (ThemeManager.Instance != null)
            {
                ThemeManager.Instance.UnregisterThemeableComponent(this);
            }
        }
        
        public void ApplyTheme(UITheme theme)
        {
            if (text == null || theme == null) return;
            
            if (useThemeColor)
            {
                Color themeColor = textType == ThemeTextType.Primary ? theme.textColor : theme.textColorSecondary;
                text.color = themeColor;
            }
            
            if (useThemeFont)
            {
                TMP_FontAsset themeFont = textType == ThemeTextType.Primary ? theme.primaryFont : theme.secondaryFont;
                if (themeFont != null)
                {
                    text.font = themeFont;
                }
            }
        }
    }
    
    /// <summary>
    /// Themeable Button component.
    /// </summary>
    public class ThemeableButton : MonoBehaviour, IThemeable
    {
        [Header("Theme Settings")]
        [SerializeField] private bool useThemeColors = true;
        
        private Button button;
        
        private void Awake()
        {
            button = GetComponent<Button>();
            
            // Register with theme manager
            if (ThemeManager.Instance != null)
            {
                ThemeManager.Instance.RegisterThemeableComponent(this);
            }
        }
        
        private void OnDestroy()
        {
            // Unregister from theme manager
            if (ThemeManager.Instance != null)
            {
                ThemeManager.Instance.UnregisterThemeableComponent(this);
            }
        }
        
        public void ApplyTheme(UITheme theme)
        {
            if (!useThemeColors || button == null || theme == null) return;
            
            ColorBlock colors = button.colors;
            colors.normalColor = theme.buttonColor;
            colors.highlightedColor = theme.buttonHoverColor;
            colors.pressedColor = theme.buttonPressedColor;
            colors.selectedColor = theme.buttonHoverColor;
            button.colors = colors;
        }
    }
    
    /// <summary>
    /// Theme color types.
    /// </summary>
    public enum ThemeColorType
    {
        Background,
        Primary,
        Secondary,
        Accent,
        Panel,
        Button,
        Border,
        Success,
        Warning,
        Error,
        Info
    }
    
    /// <summary>
    /// Theme text types.
    /// </summary>
    public enum ThemeTextType
    {
        Primary,
        Secondary
    }
} 