using System;
using System.Collections.Generic;
using System.Threading;
using Cysharp.Threading.Tasks;
using UnityEngine;
using UnityEngine.UI;
using TMPro;
using VisualDM.Core;

namespace VisualDM.UI
{
    /// <summary>
    /// Main UI Manager that orchestrates all UI panels and components.
    /// This is equivalent to a top-level React component or App component.
    /// </summary>
    public class UIManager : MonoBehaviour
    {
        [Header("References")]
        [SerializeField] private Canvas mainCanvas;
        [SerializeField] private RectTransform uiContainer;
        [SerializeField] private Components.NavigationSidebar navigationSidebar;
        
        [Header("Panels")]
        [SerializeField] private Panels.AppearancePanel appearancePanel;
        [SerializeField] private Panels.ArmorPanel armorPanel;
        [SerializeField] private Panels.PresetsPanel presetsPanel;
        [SerializeField] private Panels.RandomizerPanel randomizerPanel;
        
        [Header("Theme")]
        [SerializeField] private UIThemeManager themeManager;
        
        // Current active panel
        private Components.Panel activePanel;
        
        // State manager for UI state
        private UIStateManager stateManager;
        
        // Event for character changes
        public event Action<object> OnCharacterChanged;
        
        // Dictionary to store active panels
        private Dictionary<Components.NavigationSidebar.CustomizationSection, Components.Panel> panels = 
            new Dictionary<Components.NavigationSidebar.CustomizationSection, Components.Panel>();
        
        // Singleton instance
        private static UIManager _instance;
        public static UIManager Instance
        {
            get
            {
                return _instance;
            }
        }
        
        private void Awake()
        {
            // Set up singleton
            if (_instance != null && _instance != this)
            {
                Destroy(gameObject);
                return;
            }
            
            _instance = this;
            
            // Create main canvas if not assigned
            if (mainCanvas == null)
            {
                GameObject canvasGO = new GameObject("MainCanvas");
                mainCanvas = canvasGO.AddComponent<Canvas>();
                mainCanvas.renderMode = RenderMode.ScreenSpaceOverlay;
                
                // Add canvas scaler
                CanvasScaler scaler = canvasGO.AddComponent<CanvasScaler>();
                scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
                scaler.referenceResolution = new Vector2(1920, 1080);
                scaler.matchWidthOrHeight = 0.5f;
                
                // Add graphic raycaster
                canvasGO.AddComponent<GraphicRaycaster>();
            }
            
            // Create UI container if not assigned
            if (uiContainer == null)
            {
                GameObject containerGO = new GameObject("UIContainer");
                containerGO.transform.SetParent(mainCanvas.transform, false);
                
                uiContainer = containerGO.AddComponent<RectTransform>();
                uiContainer.anchorMin = Vector2.zero;
                uiContainer.anchorMax = Vector2.one;
                uiContainer.sizeDelta = Vector2.zero;
            }
            
            // Initialize state manager
            stateManager = UIStateManager.Instance;
            
            // Hide all panels by default
            if (appearancePanel) appearancePanel.SetVisible(false);
            if (armorPanel) armorPanel.SetVisible(false);
            if (presetsPanel) presetsPanel.SetVisible(false);
            if (randomizerPanel) randomizerPanel.SetVisible(false);
        }
        
        private void Start()
        {
            // Register to navigation events
            if (navigationSidebar)
            {
                navigationSidebar.OnSectionChanged += HandleSectionChanged;
            }
            
            // Register to panel events
            if (appearancePanel)
            {
                appearancePanel.OnFeatureChanged += (featureType, value) => {
                    // Handle appearance feature changes
                    Debug.Log($"Appearance feature changed: {featureType} = {value}");
                    OnCharacterChanged?.Invoke(new { Type = "appearance", Feature = featureType, Value = value });
                };
            }
            
            if (armorPanel)
            {
                armorPanel.OnEquipmentChanged += (slot, itemId) => {
                    // Handle armor changes
                    Debug.Log($"Equipment changed: {slot} = {itemId}");
                    OnCharacterChanged?.Invoke(new { Type = "armor", Slot = slot, ItemId = itemId });
                };
            }
            
            if (presetsPanel)
            {
                presetsPanel.OnPresetSelected += (presetName) => {
                    // Handle preset selection
                    Debug.Log($"Preset selected: {presetName}");
                    OnCharacterChanged?.Invoke(new { Type = "preset", Name = presetName });
                };
                
                presetsPanel.OnPresetSaved += (presetName) => {
                    // Handle preset saving
                    Debug.Log($"Preset saved: {presetName}");
                    // Save current character configuration
                };
            }
            
            if (randomizerPanel)
            {
                randomizerPanel.OnRandomize += (config) => {
                    // Handle randomization
                    Debug.Log($"Randomize character with config: Race={config.randomizeRace}, Gender={config.randomizeGender}, etc.");
                    OnCharacterChanged?.Invoke(new { Type = "randomize", Config = config });
                };
            }
            
            // Show default panel (Appearance)
            ShowPanel(Components.NavigationSidebar.CustomizationSection.Appearance);
        }
        
        /// <summary>
        /// Set the main canvas reference
        /// </summary>
        public void SetCanvas(Canvas canvas)
        {
            mainCanvas = canvas;
            
            // If UI container is not set, create it
            if (uiContainer == null && mainCanvas != null)
            {
                GameObject containerGO = new GameObject("UIContainer");
                containerGO.transform.SetParent(mainCanvas.transform, false);
                
                uiContainer = containerGO.AddComponent<RectTransform>();
                uiContainer.anchorMin = Vector2.zero;
                uiContainer.anchorMax = Vector2.one;
                uiContainer.sizeDelta = Vector2.zero;
                
                // Move existing UI components to the container if needed
                if (navigationSidebar != null)
                {
                    navigationSidebar.transform.SetParent(uiContainer, false);
                }
                
                if (appearancePanel != null)
                {
                    appearancePanel.transform.SetParent(uiContainer, false);
                }
                
                if (armorPanel != null)
                {
                    armorPanel.transform.SetParent(uiContainer, false);
                }
                
                if (presetsPanel != null)
                {
                    presetsPanel.transform.SetParent(uiContainer, false);
                }
                
                if (randomizerPanel != null)
                {
                    randomizerPanel.transform.SetParent(uiContainer, false);
                }
            }
        }
        
        /// <summary>
        /// Handle navigation section change
        /// </summary>
        private void HandleSectionChanged(Components.NavigationSidebar.CustomizationSection section)
        {
            ShowPanel(section);
        }
        
        /// <summary>
        /// Show the panel corresponding to the selected section
        /// </summary>
        public void ShowPanel(Components.NavigationSidebar.CustomizationSection section)
        {
            // Hide current active panel
            if (activePanel)
            {
                activePanel.SetVisible(false);
            }
            
            // Show selected panel
            switch (section)
            {
                case Components.NavigationSidebar.CustomizationSection.Appearance:
                    activePanel = appearancePanel;
                    break;
                case Components.NavigationSidebar.CustomizationSection.Armor:
                    activePanel = armorPanel;
                    break;
                case Components.NavigationSidebar.CustomizationSection.Presets:
                    activePanel = presetsPanel;
                    break;
                case Components.NavigationSidebar.CustomizationSection.Randomizer:
                    activePanel = randomizerPanel;
                    break;
                default:
                    activePanel = appearancePanel;
                    break;
            }
            
            if (activePanel)
            {
                activePanel.SetVisible(true);
            }
            
            // Update navigation sidebar
            if (navigationSidebar)
            {
                navigationSidebar.SetCurrentSection(section);
            }
        }
        
        /// <summary>
        /// Register a function to the character changed event
        /// </summary>
        public void RegisterCharacterChangeListener(Action<object> listener)
        {
            OnCharacterChanged += listener;
        }
        
        /// <summary>
        /// Unregister a function from the character changed event
        /// </summary>
        public void UnregisterCharacterChangeListener(Action<object> listener)
        {
            OnCharacterChanged -= listener;
        }
        
        /// <summary>
        /// API to update character appearance programmatically (from external code)
        /// </summary>
        public void UpdateCharacterAppearance(string featureType, object value)
        {
            // Update UI if needed
            if (appearancePanel && appearancePanel.gameObject.activeSelf)
            {
                appearancePanel.UpdateFeatureUI(featureType, value);
            }
            
            // Notify listeners
            OnCharacterChanged?.Invoke(new { Type = "appearance", Feature = featureType, Value = value });
        }
        
        /// <summary>
        /// API to update character armor programmatically (from external code)
        /// </summary>
        public void UpdateCharacterArmor(Panels.ArmorPanel.EquipmentSlot slot, string itemId)
        {
            // Update UI if needed
            if (armorPanel && armorPanel.gameObject.activeSelf)
            {
                armorPanel.UpdateSlotUI(slot, itemId);
            }
            
            // Notify listeners
            OnCharacterChanged?.Invoke(new { Type = "armor", Slot = slot, ItemId = itemId });
        }
        
        /// <summary>
        /// Set theme colors programmatically
        /// </summary>
        public void SetTheme(UIThemeManager newTheme)
        {
            themeManager = newTheme;
            
            // Apply theme settings to all UI components
            if (appearancePanel) appearancePanel.RefreshTheme();
            if (armorPanel) armorPanel.RefreshTheme();
            if (presetsPanel) presetsPanel.RefreshTheme();
            if (randomizerPanel) randomizerPanel.RefreshTheme();
            if (navigationSidebar) navigationSidebar.RefreshTheme();
        }
    }
    
    /// <summary>
    /// Base class for UI panels
    /// </summary>
    public abstract class UIPanel : MonoBehaviour
    {
        [SerializeField] private string _panelId;
        [SerializeField] private float _showDuration = 0.3f;
        [SerializeField] private float _hideDuration = 0.2f;
        
        private bool _isInitialized;
        
        public string PanelId => _panelId;
        public bool IsVisible { get; private set; }
        
        /// <summary>
        /// Initialize the panel
        /// </summary>
        public virtual void Initialize()
        {
            if (_isInitialized) return;
            
            // Set initial state
            IsVisible = false;
            
            _isInitialized = true;
        }
        
        /// <summary>
        /// Show the panel with animation
        /// </summary>
        public virtual async UniTask ShowAsync(CancellationToken cancellationToken = default)
        {
            IsVisible = true;
            
            // Override this to add custom show animations
            await UniTask.Delay(TimeSpan.FromSeconds(_showDuration), cancellationToken: cancellationToken);
        }
        
        /// <summary>
        /// Hide the panel with animation
        /// </summary>
        public virtual async UniTask HideAsync(CancellationToken cancellationToken = default)
        {
            IsVisible = false;
            
            // Override this to add custom hide animations
            await UniTask.Delay(TimeSpan.FromSeconds(_hideDuration), cancellationToken: cancellationToken);
            
            if (!cancellationToken.IsCancellationRequested)
            {
                gameObject.SetActive(false);
            }
        }
    }
    
    /// <summary>
    /// Settings for UI system
    /// </summary>
    [CreateAssetMenu(fileName = "UISettings", menuName = "VisualDM/UI Settings")]
    public class UISettings : ScriptableObject
    {
        [Tooltip("Default transition duration")]
        public float DefaultTransitionDuration = 0.3f;
        
        [Tooltip("Animation curve for transitions")]
        public AnimationCurve TransitionCurve = AnimationCurve.EaseInOut(0, 0, 1, 1);
    }
    
    #region Events
    
    public class UIPanelShownEvent
    {
        public string PanelId { get; set; }
    }
    
    #endregion
} 