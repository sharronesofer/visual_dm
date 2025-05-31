using UnityEngine;
using System.Collections.Generic;
using System.Linq;
using System;

namespace VDM.UI.Core
{
    /// <summary>
    /// Central UI management system for Visual DM.
    /// Handles panel navigation, state management, and UI coordination.
    /// </summary>
    public class UIManager : MonoBehaviour
    {
        [Header("UI Configuration")]
        [SerializeField] private Canvas mainCanvas;
        [SerializeField] private int baseUILayer = 100;
        [SerializeField] private int modalLayer = 200;
        [SerializeField] private int overlayLayer = 300;
        [SerializeField] private int tooltipLayer = 400;
        
        [Header("Navigation Settings")]
        [SerializeField] private bool enableBackNavigation = true;
        [SerializeField] private KeyCode backNavigationKey = KeyCode.Escape;
        [SerializeField] private int maxNavigationHistory = 10;
        
        // Singleton
        public static UIManager Instance { get; private set; }
        
        // Events
        public event Action<BaseUIPanel> OnPanelOpened;
        public event Action<BaseUIPanel> OnPanelClosed;
        public event Action<string> OnNavigationChanged;
        
        // Panel Management
        private Dictionary<string, BaseUIPanel> registeredPanels = new Dictionary<string, BaseUIPanel>();
        private Dictionary<Type, BaseUIPanel> panelsByType = new Dictionary<Type, BaseUIPanel>();
        private List<BaseUIPanel> activePanels = new List<BaseUIPanel>();
        private Stack<string> navigationHistory = new Stack<string>();
        
        // State
        public BaseUIPanel CurrentPanel { get; private set; }
        public bool HasActivePanels => activePanels.Count > 0;
        public int ActivePanelCount => activePanels.Count;
        
        // Layer Management
        private int currentLayerOffset = 0;
        
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
            
            // Initialize main canvas if not assigned
            if (mainCanvas == null)
            {
                mainCanvas = FindObjectOfType<Canvas>();
                if (mainCanvas == null)
                {
                    Debug.LogError("UIManager: No Canvas found in scene. Please assign a main canvas.");
                }
            }
        }
        
        private void Update()
        {
            // Handle back navigation
            if (enableBackNavigation && Input.GetKeyDown(backNavigationKey))
            {
                HandleBackNavigation();
            }
        }
        
        private void OnDestroy()
        {
            if (Instance == this)
            {
                Instance = null;
            }
        }
        
        #region Panel Registration
        
        /// <summary>
        /// Register a panel with the UI manager.
        /// </summary>
        public void RegisterPanel(BaseUIPanel panel)
        {
            if (panel == null)
            {
                Debug.LogError("UIManager: Cannot register null panel.");
                return;
            }
            
            string panelId = panel.PanelId;
            Type panelType = panel.GetType();
            
            // Register by ID
            if (registeredPanels.ContainsKey(panelId))
            {
                Debug.LogWarning($"UIManager: Panel with ID '{panelId}' is already registered. Replacing.");
                UnregisterPanel(registeredPanels[panelId]);
            }
            
            registeredPanels[panelId] = panel;
            panelsByType[panelType] = panel;
            
            // Subscribe to panel events
            panel.OnPanelOpened += HandlePanelOpened;
            panel.OnPanelClosed += HandlePanelClosed;
            panel.OnPanelDestroyed += HandlePanelDestroyed;
            
            Debug.Log($"UIManager: Registered panel '{panelId}' of type {panelType.Name}");
        }
        
        /// <summary>
        /// Unregister a panel from the UI manager.
        /// </summary>
        public void UnregisterPanel(BaseUIPanel panel)
        {
            if (panel == null) return;
            
            string panelId = panel.PanelId;
            Type panelType = panel.GetType();
            
            // Unsubscribe from events
            panel.OnPanelOpened -= HandlePanelOpened;
            panel.OnPanelClosed -= HandlePanelClosed;
            panel.OnPanelDestroyed -= HandlePanelDestroyed;
            
            // Remove from collections
            registeredPanels.Remove(panelId);
            panelsByType.Remove(panelType);
            activePanels.Remove(panel);
            
            // Remove from navigation history
            var historyArray = navigationHistory.ToArray();
            navigationHistory.Clear();
            foreach (var historyId in historyArray.Reverse())
            {
                if (historyId != panelId)
                {
                    navigationHistory.Push(historyId);
                }
            }
            
            Debug.Log($"UIManager: Unregistered panel '{panelId}'");
        }
        
        #endregion
        
        #region Panel Access
        
        /// <summary>
        /// Get a panel by its ID.
        /// </summary>
        public T GetPanel<T>(string panelId) where T : BaseUIPanel
        {
            if (registeredPanels.TryGetValue(panelId, out BaseUIPanel panel))
            {
                return panel as T;
            }
            return null;
        }
        
        /// <summary>
        /// Get a panel by its type.
        /// </summary>
        public T GetPanel<T>() where T : BaseUIPanel
        {
            if (panelsByType.TryGetValue(typeof(T), out BaseUIPanel panel))
            {
                return panel as T;
            }
            return null;
        }
        
        /// <summary>
        /// Check if a panel is registered.
        /// </summary>
        public bool HasPanel(string panelId)
        {
            return registeredPanels.ContainsKey(panelId);
        }
        
        /// <summary>
        /// Check if a panel type is registered.
        /// </summary>
        public bool HasPanel<T>() where T : BaseUIPanel
        {
            return panelsByType.ContainsKey(typeof(T));
        }
        
        #endregion
        
        #region Panel Navigation
        
        /// <summary>
        /// Show a panel by ID.
        /// </summary>
        public void ShowPanel(string panelId, bool addToHistory = true, bool animate = true)
        {
            if (!registeredPanels.TryGetValue(panelId, out BaseUIPanel panel))
            {
                Debug.LogError($"UIManager: Panel '{panelId}' not found.");
                return;
            }
            
            ShowPanel(panel, addToHistory, animate);
        }
        
        /// <summary>
        /// Show a panel by type.
        /// </summary>
        public void ShowPanel<T>(bool addToHistory = true, bool animate = true) where T : BaseUIPanel
        {
            var panel = GetPanel<T>();
            if (panel == null)
            {
                Debug.LogError($"UIManager: Panel of type '{typeof(T).Name}' not found.");
                return;
            }
            
            ShowPanel(panel, addToHistory, animate);
        }
        
        /// <summary>
        /// Show a specific panel instance.
        /// </summary>
        public void ShowPanel(BaseUIPanel panel, bool addToHistory = true, bool animate = true)
        {
            if (panel == null) return;
            
            // Add to navigation history
            if (addToHistory && CurrentPanel != null)
            {
                AddToNavigationHistory(CurrentPanel.PanelId);
            }
            
            // Set layer order
            SetPanelLayer(panel, UILayer.Base);
            
            // Show the panel
            panel.Show(animate);
            
            CurrentPanel = panel;
            OnNavigationChanged?.Invoke(panel.PanelId);
        }
        
        /// <summary>
        /// Hide a panel by ID.
        /// </summary>
        public void HidePanel(string panelId, bool animate = true)
        {
            if (registeredPanels.TryGetValue(panelId, out BaseUIPanel panel))
            {
                panel.Hide(animate);
            }
        }
        
        /// <summary>
        /// Hide a panel by type.
        /// </summary>
        public void HidePanel<T>(bool animate = true) where T : BaseUIPanel
        {
            var panel = GetPanel<T>();
            panel?.Hide(animate);
        }
        
        /// <summary>
        /// Close a panel by ID.
        /// </summary>
        public void ClosePanel(string panelId, bool animate = true)
        {
            if (registeredPanels.TryGetValue(panelId, out BaseUIPanel panel))
            {
                panel.Close(animate);
            }
        }
        
        /// <summary>
        /// Close a panel by type.
        /// </summary>
        public void ClosePanel<T>(bool animate = true) where T : BaseUIPanel
        {
            var panel = GetPanel<T>();
            panel?.Close(animate);
        }
        
        /// <summary>
        /// Close all active panels.
        /// </summary>
        public void CloseAllPanels(bool animate = true)
        {
            var panelsToClose = new List<BaseUIPanel>(activePanels);
            foreach (var panel in panelsToClose)
            {
                panel.Close(animate);
            }
        }
        
        #endregion
        
        #region Navigation History
        
        /// <summary>
        /// Navigate back to the previous panel.
        /// </summary>
        public void NavigateBack(bool animate = true)
        {
            if (navigationHistory.Count == 0) return;
            
            string previousPanelId = navigationHistory.Pop();
            if (registeredPanels.TryGetValue(previousPanelId, out BaseUIPanel panel))
            {
                ShowPanel(panel, false, animate);
            }
        }
        
        /// <summary>
        /// Handle back navigation input.
        /// </summary>
        private void HandleBackNavigation()
        {
            // Check if any modal is open first
            var modals = activePanels.Where(p => GetPanelLayer(p) >= modalLayer).ToList();
            if (modals.Count > 0)
            {
                // Close the topmost modal
                var topModal = modals.OrderByDescending(p => GetPanelLayer(p)).First();
                topModal.Close();
                return;
            }
            
            // Otherwise navigate back
            NavigateBack();
        }
        
        /// <summary>
        /// Add a panel to navigation history.
        /// </summary>
        private void AddToNavigationHistory(string panelId)
        {
            // Remove if already in history to avoid duplicates
            var historyArray = navigationHistory.ToArray();
            navigationHistory.Clear();
            foreach (var historyId in historyArray.Reverse())
            {
                if (historyId != panelId)
                {
                    navigationHistory.Push(historyId);
                }
            }
            
            // Add to history
            navigationHistory.Push(panelId);
            
            // Limit history size
            if (navigationHistory.Count > maxNavigationHistory)
            {
                var limitedHistory = navigationHistory.Take(maxNavigationHistory).ToArray();
                navigationHistory.Clear();
                foreach (var historyId in limitedHistory.Reverse())
                {
                    navigationHistory.Push(historyId);
                }
            }
        }
        
        /// <summary>
        /// Clear navigation history.
        /// </summary>
        public void ClearNavigationHistory()
        {
            navigationHistory.Clear();
        }
        
        #endregion
        
        #region Layer Management
        
        public enum UILayer
        {
            Base = 0,
            Modal = 1,
            Overlay = 2,
            Tooltip = 3
        }
        
        /// <summary>
        /// Set a panel's layer for proper rendering order.
        /// </summary>
        public void SetPanelLayer(BaseUIPanel panel, UILayer layer)
        {
            int sortOrder = GetLayerSortOrder(layer);
            panel.SetSortOrder(sortOrder);
        }
        
        /// <summary>
        /// Get the sort order for a UI layer.
        /// </summary>
        private int GetLayerSortOrder(UILayer layer)
        {
            switch (layer)
            {
                case UILayer.Base:
                    return baseUILayer + currentLayerOffset++;
                case UILayer.Modal:
                    return modalLayer + currentLayerOffset++;
                case UILayer.Overlay:
                    return overlayLayer + currentLayerOffset++;
                case UILayer.Tooltip:
                    return tooltipLayer + currentLayerOffset++;
                default:
                    return baseUILayer;
            }
        }
        
        /// <summary>
        /// Get a panel's current layer.
        /// </summary>
        private int GetPanelLayer(BaseUIPanel panel)
        {
            if (panel.canvas != null)
            {
                return panel.canvas.sortingOrder;
            }
            return 0;
        }
        
        #endregion
        
        #region Event Handlers
        
        private void HandlePanelOpened(BaseUIPanel panel)
        {
            if (!activePanels.Contains(panel))
            {
                activePanels.Add(panel);
            }
            
            OnPanelOpened?.Invoke(panel);
            Debug.Log($"UIManager: Panel '{panel.PanelId}' opened");
        }
        
        private void HandlePanelClosed(BaseUIPanel panel)
        {
            activePanels.Remove(panel);
            
            // Update current panel if this was the current one
            if (CurrentPanel == panel)
            {
                CurrentPanel = activePanels.LastOrDefault();
            }
            
            OnPanelClosed?.Invoke(panel);
            Debug.Log($"UIManager: Panel '{panel.PanelId}' closed");
        }
        
        private void HandlePanelDestroyed(BaseUIPanel panel)
        {
            UnregisterPanel(panel);
            Debug.Log($"UIManager: Panel '{panel.PanelId}' destroyed");
        }
        
        #endregion
        
        #region Utility
        
        /// <summary>
        /// Get all active panels.
        /// </summary>
        public List<BaseUIPanel> GetActivePanels()
        {
            return new List<BaseUIPanel>(activePanels);
        }
        
        /// <summary>
        /// Get all registered panels.
        /// </summary>
        public List<BaseUIPanel> GetAllPanels()
        {
            return registeredPanels.Values.ToList();
        }
        
        /// <summary>
        /// Reset the UI manager state.
        /// </summary>
        public void Reset()
        {
            CloseAllPanels(false);
            ClearNavigationHistory();
            currentLayerOffset = 0;
            CurrentPanel = null;
        }
        
        #endregion
    }
} 