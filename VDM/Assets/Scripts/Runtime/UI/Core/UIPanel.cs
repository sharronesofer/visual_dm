using System;
using UnityEngine.UI;
using UnityEngine;


namespace VDM.Runtime.UI.Core
{
    /// <summary>
    /// Base class for all UI panels in the VDM system
    /// Provides common functionality for panel management, lifecycle, and responsive behavior
    /// </summary>
    public abstract class UIPanel : MonoBehaviour
    {
        [Header("UI Panel Base Configuration")]
        [SerializeField] protected bool showOnStart = false;
        [SerializeField] protected bool hideOnClickOutside = false;
        [SerializeField] protected bool useTransitions = true;
        [SerializeField] protected float transitionDuration = 0.3f;

        [Header("Panel References")]
        [SerializeField] protected CanvasGroup canvasGroup;
        [SerializeField] protected Button closeButton;
        [SerializeField] protected GameObject loadingIndicator;

        // Panel state
        protected bool _isVisible = false;
        protected bool _isTransitioning = false;
        protected bool _isInitialized = false;

        // Events
        public event Action<UIPanel> OnPanelShown;
        public event Action<UIPanel> OnPanelHidden;
        public event Action<UIPanel> OnPanelInitialized;
        public event Action<UIPanel, string> OnPanelError;

        #region Unity Lifecycle

        protected virtual void Awake()
        {
            InitializePanel();
        }

        protected virtual void Start()
        {
            if (showOnStart)
            {
                Show();
            }
            else
            {
                Hide(false); // Hide without animation
            }
        }

        protected virtual void OnEnable()
        {
            // Subscribe to UI events if needed
            SubscribeToUIEvents();
        }

        protected virtual void OnDisable()
        {
            // Unsubscribe from UI events
            UnsubscribeFromUIEvents();
        }

        protected virtual void OnDestroy()
        {
            CleanupPanel();
        }

        #endregion

        #region Panel Lifecycle

        /// <summary>
        /// Initialize the panel
        /// </summary>
        protected virtual void InitializePanel()
        {
            if (_isInitialized) return;

            try
            {
                // Setup canvas group if not assigned
                if (canvasGroup == null)
                {
                    canvasGroup = GetComponent<CanvasGroup>();
                    if (canvasGroup == null)
                    {
                        canvasGroup = gameObject.AddComponent<CanvasGroup>();
                    }
                }

                // Setup close button if assigned
                if (closeButton != null)
                {
                    closeButton.onClick.AddListener(() => Hide());
                }

                // Initialize panel-specific components
                InitializePanelComponents();

                _isInitialized = true;
                OnPanelInitialized?.Invoke(this);
            }
            catch (Exception e)
            {
                HandlePanelError($"Failed to initialize panel: {e.Message}", e);
            }
        }

        /// <summary>
        /// Clean up the panel
        /// </summary>
        protected virtual void CleanupPanel()
        {
            // Cleanup close button
            if (closeButton != null)
            {
                closeButton.onClick.RemoveAllListeners();
            }

            // Cleanup panel-specific components
            CleanupPanelComponents();
        }

        #endregion

        #region Show/Hide

        /// <summary>
        /// Show the panel
        /// </summary>
        public virtual void Show(bool animated = true)
        {
            if (_isVisible || _isTransitioning) return;

            try
            {
                gameObject.SetActive(true);
                _isVisible = true;

                if (animated && useTransitions)
                {
                    ShowAnimated();
                }
                else
                {
                    ShowImmediate();
                }

                OnPanelShown?.Invoke(this);
                OnShown();
            }
            catch (Exception e)
            {
                HandlePanelError($"Failed to show panel: {e.Message}", e);
            }
        }

        /// <summary>
        /// Hide the panel
        /// </summary>
        public virtual void Hide(bool animated = true)
        {
            if (!_isVisible || _isTransitioning) return;

            try
            {
                _isVisible = false;

                if (animated && useTransitions)
                {
                    HideAnimated();
                }
                else
                {
                    HideImmediate();
                }

                OnPanelHidden?.Invoke(this);
                OnHidden();
            }
            catch (Exception e)
            {
                HandlePanelError($"Failed to hide panel: {e.Message}", e);
            }
        }

        /// <summary>
        /// Toggle panel visibility
        /// </summary>
        public virtual void Toggle(bool animated = true)
        {
            if (_isVisible)
                Hide(animated);
            else
                Show(animated);
        }

        #endregion

        #region Animation Methods

        /// <summary>
        /// Show panel with animation
        /// </summary>
        protected virtual void ShowAnimated()
        {
            if (canvasGroup == null)
            {
                ShowImmediate();
                return;
            }

            _isTransitioning = true;
            canvasGroup.alpha = 0f;
            canvasGroup.interactable = false;
            canvasGroup.blocksRaycasts = true;

            // Simple fade in - can be overridden for more complex animations
            LeanTween.value(gameObject, 0f, 1f, transitionDuration)
                .setOnUpdate((float value) => {
                    if (canvasGroup != null)
                        canvasGroup.alpha = value;
                })
                .setOnComplete(() => {
                    if (canvasGroup != null)
                    {
                        canvasGroup.interactable = true;
                    }
                    _isTransitioning = false;
                });
        }

        /// <summary>
        /// Hide panel with animation
        /// </summary>
        protected virtual void HideAnimated()
        {
            if (canvasGroup == null)
            {
                HideImmediate();
                return;
            }

            _isTransitioning = true;
            canvasGroup.interactable = false;

            // Simple fade out - can be overridden for more complex animations
            LeanTween.value(gameObject, canvasGroup.alpha, 0f, transitionDuration)
                .setOnUpdate((float value) => {
                    if (canvasGroup != null)
                        canvasGroup.alpha = value;
                })
                .setOnComplete(() => {
                    if (canvasGroup != null)
                    {
                        canvasGroup.blocksRaycasts = false;
                    }
                    gameObject.SetActive(false);
                    _isTransitioning = false;
                });
        }

        /// <summary>
        /// Show panel immediately without animation
        /// </summary>
        protected virtual void ShowImmediate()
        {
            if (canvasGroup != null)
            {
                canvasGroup.alpha = 1f;
                canvasGroup.interactable = true;
                canvasGroup.blocksRaycasts = true;
            }
        }

        /// <summary>
        /// Hide panel immediately without animation
        /// </summary>
        protected virtual void HideImmediate()
        {
            if (canvasGroup != null)
            {
                canvasGroup.alpha = 0f;
                canvasGroup.interactable = false;
                canvasGroup.blocksRaycasts = false;
            }
            gameObject.SetActive(false);
        }

        #endregion

        #region Loading State

        /// <summary>
        /// Show loading indicator
        /// </summary>
        public virtual void ShowLoading()
        {
            if (loadingIndicator != null)
            {
                loadingIndicator.SetActive(true);
            }
            
            if (canvasGroup != null)
            {
                canvasGroup.interactable = false;
            }
        }

        /// <summary>
        /// Hide loading indicator
        /// </summary>
        public virtual void HideLoading()
        {
            if (loadingIndicator != null)
            {
                loadingIndicator.SetActive(false);
            }
            
            if (canvasGroup != null && _isVisible)
            {
                canvasGroup.interactable = true;
            }
        }

        #endregion

        #region Abstract/Virtual Methods

        /// <summary>
        /// Initialize panel-specific components
        /// Override in derived classes
        /// </summary>
        protected virtual void InitializePanelComponents()
        {
            // Override in derived classes
        }

        /// <summary>
        /// Cleanup panel-specific components
        /// Override in derived classes
        /// </summary>
        protected virtual void CleanupPanelComponents()
        {
            // Override in derived classes
        }

        /// <summary>
        /// Called when panel is shown
        /// Override in derived classes
        /// </summary>
        protected virtual void OnShown()
        {
            // Override in derived classes
        }

        /// <summary>
        /// Called when panel is hidden
        /// Override in derived classes
        /// </summary>
        protected virtual void OnHidden()
        {
            // Override in derived classes
        }

        /// <summary>
        /// Subscribe to UI events
        /// Override in derived classes
        /// </summary>
        protected virtual void SubscribeToUIEvents()
        {
            // Override in derived classes
        }

        /// <summary>
        /// Unsubscribe from UI events
        /// Override in derived classes
        /// </summary>
        protected virtual void UnsubscribeFromUIEvents()
        {
            // Override in derived classes
        }

        #endregion

        #region Properties

        /// <summary>
        /// Check if the panel is currently visible
        /// </summary>
        public bool IsVisible => _isVisible;

        /// <summary>
        /// Check if the panel is currently transitioning
        /// </summary>
        public bool IsTransitioning => _isTransitioning;

        /// <summary>
        /// Check if the panel is initialized
        /// </summary>
        public bool IsInitialized => _isInitialized;

        /// <summary>
        /// Get the panel name (for identification)
        /// </summary>
        public virtual string PanelName => GetType().Name;

        #endregion

        #region Error Handling

        /// <summary>
        /// Handle panel errors
        /// </summary>
        protected virtual void HandlePanelError(string message, Exception exception = null)
        {
            string fullMessage = $"[{PanelName}] {message}";
            
            if (exception != null)
            {
                Debug.LogError($"{fullMessage}\nException: {exception}");
            }
            else
            {
                Debug.LogError(fullMessage);
            }

            OnPanelError?.Invoke(this, fullMessage);
        }

        #endregion

        #region Utility Methods

        /// <summary>
        /// Set panel interactable state
        /// </summary>
        public virtual void SetInteractable(bool interactable)
        {
            if (canvasGroup != null)
            {
                canvasGroup.interactable = interactable;
            }
        }

        /// <summary>
        /// Set panel alpha
        /// </summary>
        public virtual void SetAlpha(float alpha)
        {
            if (canvasGroup != null)
            {
                canvasGroup.alpha = Mathf.Clamp01(alpha);
            }
        }

        /// <summary>
        /// Force panel to refresh its state
        /// </summary>
        public virtual void RefreshPanel()
        {
            // Override in derived classes for specific refresh logic
        }

        #endregion
    }
} 