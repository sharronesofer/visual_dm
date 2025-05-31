using System.Collections.Generic;
using System.Linq;
using System;
using UnityEngine;


namespace VDM.Infrastructure.Ui.Ui.Framework
{
    /// <summary>
    /// Screen transition types
    /// </summary>
    public enum ScreenTransition
    {
        None,
        Fade,
        Slide,
        Scale,
        Custom
    }
    
    /// <summary>
    /// Screen layer priorities
    /// </summary>
    public enum ScreenLayer
    {
        Background = 0,
        Main = 100,
        Popup = 200,
        Modal = 300,
        Overlay = 400,
        Debug = 500
    }
    
    /// <summary>
    /// Manages UI screens, navigation, and transitions
    /// </summary>
    public class UIScreenManager : MonoBehaviour
    {
        [Header("Screen Management")]
        [SerializeField] private Canvas mainCanvas;
        [SerializeField] private bool initializeOnAwake = true;
        [SerializeField] private bool enableHistory = true;
        [SerializeField] private int maxHistorySize = 20;
        
        [Header("Default Transitions")]
        [SerializeField] private ScreenTransition defaultTransition = ScreenTransition.Fade;
        [SerializeField] private float defaultTransitionDuration = 0.3f;
        [SerializeField] private bool allowConcurrentTransitions = false;
        
        // Screen registry and management
        private Dictionary<string, BaseUIScreen> registeredScreens = new Dictionary<string, BaseUIScreen>();
        private Dictionary<ScreenLayer, List<BaseUIScreen>> screenLayers = new Dictionary<ScreenLayer, List<BaseUIScreen>>();
        private Stack<string> screenHistory = new Stack<string>();
        
        // Current state
        private BaseUIScreen currentMainScreen;
        private List<BaseUIScreen> activeScreens = new List<BaseUIScreen>();
        private List<BaseUIScreen> transitioning = new List<BaseUIScreen>();
        
        // Events
        public event Action<BaseUIScreen> OnScreenShown;
        public event Action<BaseUIScreen> OnScreenHidden;
        public event Action<BaseUIScreen> OnScreenRegistered;
        public event Action<string> OnScreenUnregistered;
        public event Action<string, string> OnScreenTransition;
        
        // Properties
        public bool IsInitialized { get; private set; }
        public bool IsTransitioning => transitioning.Count > 0;
        public BaseUIScreen CurrentMainScreen => currentMainScreen;
        public IReadOnlyList<BaseUIScreen> ActiveScreens => activeScreens.AsReadOnly();
        public int HistoryCount => screenHistory.Count;
        
        // Singleton instance
        private static UIScreenManager instance;
        public static UIScreenManager Instance
        {
            get
            {
                if (!instance)
                {
                    instance = FindObjectOfType<UIScreenManager>();
                    if (!instance)
                    {
                        var go = new GameObject("UIScreenManager");
                        instance = go.AddComponent<UIScreenManager>();
                        DontDestroyOnLoad(go);
                    }
                }
                return instance;
            }
        }
        
        #region Unity Lifecycle
        
        private void Awake()
        {
            if (instance && instance != this)
            {
                Destroy(gameObject);
                return;
            }
            
            instance = this;
            DontDestroyOnLoad(gameObject);
            
            InitializeLayers();
            
            if (initializeOnAwake)
            {
                Initialize();
            }
        }
        
        private void Start()
        {
            if (!IsInitialized)
            {
                Initialize();
            }
        }
        
        private void Update()
        {
            HandleInput();
        }
        
        #endregion
        
        #region Initialization
        
        /// <summary>
        /// Initialize the screen manager
        /// </summary>
        public void Initialize()
        {
            if (IsInitialized) return;
            
            try
            {
                if (!mainCanvas)
                {
                    mainCanvas = FindObjectOfType<Canvas>();
                }
                
                // Auto-register screens found in the scene
                AutoRegisterScreens();
                
                IsInitialized = true;
                Debug.Log("UI Screen Manager initialized successfully");
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to initialize UI Screen Manager: {ex.Message}");
            }
        }
        
        /// <summary>
        /// Initialize screen layers
        /// </summary>
        private void InitializeLayers()
        {
            foreach (ScreenLayer layer in Enum.GetValues(typeof(ScreenLayer)))
            {
                screenLayers[layer] = new List<BaseUIScreen>();
            }
        }
        
        /// <summary>
        /// Auto-register screens found in the scene
        /// </summary>
        private void AutoRegisterScreens()
        {
            var screens = FindObjectsOfType<BaseUIScreen>();
            foreach (var screen in screens)
            {
                RegisterScreen(screen);
            }
        }
        
        #endregion
        
        #region Screen Registration
        
        /// <summary>
        /// Register a screen with the manager
        /// </summary>
        public void RegisterScreen(BaseUIScreen screen)
        {
            if (!screen)
            {
                Debug.LogError("Cannot register null screen");
                return;
            }
            
            var screenId = screen.ScreenId;
            if (string.IsNullOrEmpty(screenId))
            {
                Debug.LogError($"Screen {screen.name} has no valid screen ID");
                return;
            }
            
            if (registeredScreens.ContainsKey(screenId))
            {
                Debug.LogWarning($"Screen with ID '{screenId}' is already registered. Replacing...");
            }
            
            registeredScreens[screenId] = screen;
            
            // Add to appropriate layer
            var layer = screen.Layer;
            if (!screenLayers[layer].Contains(screen))
            {
                screenLayers[layer].Add(screen);
                
                // Sort by sort order
                screenLayers[layer] = screenLayers[layer].OrderBy(s => s.SortOrder).ToList();
            }
            
            // Set up screen properties
            screen.transform.SetParent(mainCanvas.transform, false);
            screen.ScreenManager = this;
            
            OnScreenRegistered?.Invoke(screen);
            Debug.Log($"Registered screen: {screenId}");
        }
        
        /// <summary>
        /// Unregister a screen from the manager
        /// </summary>
        public void UnregisterScreen(string screenId)
        {
            if (!registeredScreens.TryGetValue(screenId, out var screen))
            {
                Debug.LogWarning($"Screen with ID '{screenId}' is not registered");
                return;
            }
            
            // Hide if currently active
            if (activeScreens.Contains(screen))
            {
                HideScreen(screenId, instant: true);
            }
            
            // Remove from layer
            screenLayers[screen.Layer].Remove(screen);
            
            // Remove from registry
            registeredScreens.Remove(screenId);
            
            OnScreenUnregistered?.Invoke(screenId);
            Debug.Log($"Unregistered screen: {screenId}");
        }
        
        /// <summary>
        /// Get a registered screen by ID
        /// </summary>
        public BaseUIScreen GetScreen(string screenId)
        {
            registeredScreens.TryGetValue(screenId, out var screen);
            return screen;
        }
        
        /// <summary>
        /// Get all registered screens
        /// </summary>
        public List<BaseUIScreen> GetAllScreens()
        {
            return registeredScreens.Values.ToList();
        }
        
        /// <summary>
        /// Get screens by layer
        /// </summary>
        public List<BaseUIScreen> GetScreensByLayer(ScreenLayer layer)
        {
            return screenLayers[layer].ToList();
        }
        
        /// <summary>
        /// Check if a screen is registered
        /// </summary>
        public bool IsScreenRegistered(string screenId)
        {
            return registeredScreens.ContainsKey(screenId);
        }
        
        #endregion
        
        #region Screen Navigation
        
        /// <summary>
        /// Show a screen
        /// </summary>
        public void ShowScreen(string screenId, bool addToHistory = true, ScreenTransition? transition = null, float? duration = null)
        {
            var screen = GetScreen(screenId);
            if (!screen)
            {
                Debug.LogError($"Screen with ID '{screenId}' is not registered");
                return;
            }
            
            ShowScreen(screen, addToHistory, transition, duration);
        }
        
        /// <summary>
        /// Show a screen
        /// </summary>
        public void ShowScreen(BaseUIScreen screen, bool addToHistory = true, ScreenTransition? transition = null, float? duration = null)
        {
            if (!screen)
            {
                Debug.LogError("Cannot show null screen");
                return;
            }
            
            if (activeScreens.Contains(screen))
            {
                Debug.LogWarning($"Screen {screen.ScreenId} is already active");
                return;
            }
            
            if (!allowConcurrentTransitions && IsTransitioning)
            {
                Debug.LogWarning("Cannot show screen while another transition is in progress");
                return;
            }
            
            // Add to history if it's a main screen
            if (addToHistory && enableHistory && screen.Layer == ScreenLayer.Main)
            {
                AddToHistory(screen.ScreenId);
            }
            
            // Handle main screen logic
            if (screen.Layer == ScreenLayer.Main)
            {
                if (currentMainScreen && currentMainScreen != screen)
                {
                    HideScreen(currentMainScreen, false, transition, duration);
                }
                currentMainScreen = screen;
            }
            
            // Show the screen
            StartTransition(screen, true, transition ?? defaultTransition, duration ?? defaultTransitionDuration);
        }
        
        /// <summary>
        /// Hide a screen
        /// </summary>
        public void HideScreen(string screenId, bool instant = false, ScreenTransition? transition = null, float? duration = null)
        {
            var screen = GetScreen(screenId);
            if (!screen)
            {
                Debug.LogError($"Screen with ID '{screenId}' is not registered");
                return;
            }
            
            HideScreen(screen, instant, transition, duration);
        }
        
        /// <summary>
        /// Hide a screen
        /// </summary>
        public void HideScreen(BaseUIScreen screen, bool instant = false, ScreenTransition? transition = null, float? duration = null)
        {
            if (!screen)
            {
                Debug.LogError("Cannot hide null screen");
                return;
            }
            
            if (!activeScreens.Contains(screen))
            {
                Debug.LogWarning($"Screen {screen.ScreenId} is not active");
                return;
            }
            
            if (!allowConcurrentTransitions && IsTransitioning && !instant)
            {
                Debug.LogWarning("Cannot hide screen while another transition is in progress");
                return;
            }
            
            // Clear current main screen if this is it
            if (currentMainScreen == screen)
            {
                currentMainScreen = null;
            }
            
            // Hide the screen
            if (instant)
            {
                screen.Hide(instant: true);
                OnScreenHidden?.Invoke(screen);
                activeScreens.Remove(screen);
            }
            else
            {
                StartTransition(screen, false, transition ?? defaultTransition, duration ?? defaultTransitionDuration);
            }
        }
        
        /// <summary>
        /// Toggle a screen's visibility
        /// </summary>
        public void ToggleScreen(string screenId, ScreenTransition? transition = null, float? duration = null)
        {
            var screen = GetScreen(screenId);
            if (!screen)
            {
                Debug.LogError($"Screen with ID '{screenId}' is not registered");
                return;
            }
            
            if (activeScreens.Contains(screen))
            {
                HideScreen(screen, false, transition, duration);
            }
            else
            {
                ShowScreen(screen, true, transition, duration);
            }
        }
        
        /// <summary>
        /// Navigate back in history
        /// </summary>
        public bool GoBack()
        {
            if (!enableHistory || screenHistory.Count <= 1)
            {
                return false;
            }
            
            // Remove current screen from history
            if (screenHistory.Count > 0)
            {
                screenHistory.Pop();
            }
            
            // Get previous screen
            if (screenHistory.Count > 0)
            {
                var previousScreenId = screenHistory.Pop(); // Remove from history since ShowScreen will add it back
                ShowScreen(previousScreenId, addToHistory: false);
                return true;
            }
            
            return false;
        }
        
        /// <summary>
        /// Clear all active screens
        /// </summary>
        public void ClearAllScreens(bool instant = false)
        {
            var screensToHide = activeScreens.ToList();
            foreach (var screen in screensToHide)
            {
                HideScreen(screen, instant);
            }
            
            currentMainScreen = null;
            
            if (enableHistory)
            {
                screenHistory.Clear();
            }
        }
        
        #endregion
        
        #region Screen Transitions
        
        /// <summary>
        /// Start a screen transition
        /// </summary>
        private void StartTransition(BaseUIScreen screen, bool show, ScreenTransition transition, float duration)
        {
            transitioning.Add(screen);
            
            OnScreenTransition?.Invoke(screen.ScreenId, show ? "show" : "hide");
            
            if (show)
            {
                activeScreens.Add(screen);
                screen.Show(transition == ScreenTransition.None);
                OnScreenShown?.Invoke(screen);
            }
            else
            {
                screen.Hide(transition == ScreenTransition.None);
            }
            
            // Handle transition completion
            if (transition == ScreenTransition.None)
            {
                OnTransitionComplete(screen, show);
            }
            else
            {
                // Start transition coroutine
                StartCoroutine(TransitionCoroutine(screen, show, transition, duration));
            }
        }
        
        /// <summary>
        /// Transition coroutine
        /// </summary>
        private System.Collections.IEnumerator TransitionCoroutine(BaseUIScreen screen, bool show, ScreenTransition transition, float duration)
        {
            // Wait for transition to complete
            yield return new WaitForSeconds(duration);
            
            OnTransitionComplete(screen, show);
        }
        
        /// <summary>
        /// Handle transition completion
        /// </summary>
        private void OnTransitionComplete(BaseUIScreen screen, bool show)
        {
            transitioning.Remove(screen);
            
            if (!show)
            {
                activeScreens.Remove(screen);
                OnScreenHidden?.Invoke(screen);
            }
        }
        
        #endregion
        
        #region History Management
        
        /// <summary>
        /// Add screen to history
        /// </summary>
        private void AddToHistory(string screenId)
        {
            if (screenHistory.Count > 0 && screenHistory.Peek() == screenId)
            {
                return; // Don't add duplicate
            }
            
            screenHistory.Push(screenId);
            
            // Limit history size
            if (screenHistory.Count > maxHistorySize)
            {
                var tempList = screenHistory.ToList();
                tempList.RemoveAt(tempList.Count - 1); // Remove oldest
                screenHistory.Clear();
                for (int i = tempList.Count - 1; i >= 0; i--)
                {
                    screenHistory.Push(tempList[i]);
                }
            }
        }
        
        /// <summary>
        /// Clear navigation history
        /// </summary>
        public void ClearHistory()
        {
            screenHistory.Clear();
        }
        
        /// <summary>
        /// Get current history as array
        /// </summary>
        public string[] GetHistory()
        {
            return screenHistory.ToArray();
        }
        
        #endregion
        
        #region Input Handling
        
        /// <summary>
        /// Handle input for navigation
        /// </summary>
        private void HandleInput()
        {
            if (Input.GetKeyDown(KeyCode.Escape))
            {
                HandleEscapeKey();
            }
        }
        
        /// <summary>
        /// Handle escape key press
        /// </summary>
        private void HandleEscapeKey()
        {
            // Try to close highest priority screen first
            var topScreen = activeScreens
                .Where(s => s.CanCloseWithEscape)
                .OrderByDescending(s => (int)s.Layer)
                .ThenByDescending(s => s.SortOrder)
                .FirstOrDefault();
            
            if (topScreen)
            {
                HideScreen(topScreen);
            }
            else if (enableHistory)
            {
                GoBack();
            }
        }
        
        #endregion
        
        #region Utility
        
        /// <summary>
        /// Get active screens by layer
        /// </summary>
        public List<BaseUIScreen> GetActiveScreensByLayer(ScreenLayer layer)
        {
            return activeScreens.Where(s => s.Layer == layer).ToList();
        }
        
        /// <summary>
        /// Check if any screen is active on a layer
        /// </summary>
        public bool HasActiveScreenOnLayer(ScreenLayer layer)
        {
            return activeScreens.Any(s => s.Layer == layer);
        }
        
        /// <summary>
        /// Get screen count by layer
        /// </summary>
        public int GetScreenCountByLayer(ScreenLayer layer)
        {
            return screenLayers[layer].Count;
        }
        
        /// <summary>
        /// Check if a screen is currently active
        /// </summary>
        public bool IsScreenActive(string screenId)
        {
            var screen = GetScreen(screenId);
            return screen && activeScreens.Contains(screen);
        }
        
        /// <summary>
        /// Get the topmost active screen
        /// </summary>
        public BaseUIScreen GetTopmostActiveScreen()
        {
            return activeScreens
                .OrderByDescending(s => (int)s.Layer)
                .ThenByDescending(s => s.SortOrder)
                .FirstOrDefault();
        }
        
        #endregion
    }
} 