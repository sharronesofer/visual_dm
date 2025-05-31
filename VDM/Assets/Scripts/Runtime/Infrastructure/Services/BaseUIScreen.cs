using VDM.Infrastructure.Core.Core.Ui;
using System;
using UnityEngine;


namespace VDM.Infrastructure.Ui.Ui.Framework
{
    /// <summary>
    /// Base class for all UI screens
    /// </summary>
    public abstract class BaseUIScreen : BaseUIComponent
    {
        [Header("Screen Configuration")]
        [SerializeField] protected string screenId;
        [SerializeField] protected ScreenLayer layer = ScreenLayer.Main;
        [SerializeField] protected int sortOrder = 0;
        [SerializeField] protected bool canCloseWithEscape = true;
        [SerializeField] protected bool persistBetweenScenes = false;
        [SerializeField] protected bool preloadOnAwake = false;
        
        [Header("Screen Transitions")]
        [SerializeField] protected ScreenTransition showTransition = ScreenTransition.Fade;
        [SerializeField] protected ScreenTransition hideTransition = ScreenTransition.Fade;
        [SerializeField] protected float showDuration = 0.3f;
        [SerializeField] protected float hideDuration = 0.3f;
        
        // Screen properties
        public string ScreenId => !string.IsNullOrEmpty(screenId) ? screenId : name;
        public ScreenLayer Layer => layer;
        public int SortOrder => sortOrder;
        public bool CanCloseWithEscape => canCloseWithEscape;
        public bool PersistBetweenScenes => persistBetweenScenes;
        
        // Screen manager reference
        public UIScreenManager ScreenManager { get; set; }
        
        // Screen-specific events
        public event Action<BaseUIScreen> OnScreenOpened;
        public event Action<BaseUIScreen> OnScreenClosed;
        public event Action<BaseUIScreen> OnScreenActivated;
        public event Action<BaseUIScreen> OnScreenDeactivated;
        
        // Navigation state
        public bool IsScreenActive => ScreenManager && ScreenManager.IsScreenActive(ScreenId);
        
        #region Unity Lifecycle
        
        protected override void Awake()
        {
            base.Awake();
            
            // Validate screen ID
            if (string.IsNullOrEmpty(screenId))
            {
                screenId = name;
                Debug.LogWarning($"Screen {name} has no screen ID set, using GameObject name instead");
            }
            
            // Set up persistence
            if (persistBetweenScenes)
            {
                DontDestroyOnLoad(gameObject);
            }
            
            // Preload if needed
            if (preloadOnAwake && !IsInitialized)
            {
                Initialize();
            }
        }
        
        protected override void Start()
        {
            base.Start();
            
            // Auto-register with screen manager
            if (ScreenManager)
            {
                ScreenManager.RegisterScreen(this);
            }
            else
            {
                var manager = UIScreenManager.Instance;
                if (manager)
                {
                    manager.RegisterScreen(this);
                }
            }
        }
        
        protected override void OnDestroy()
        {
            // Unregister from screen manager
            if (ScreenManager)
            {
                ScreenManager.UnregisterScreen(ScreenId);
            }
            
            base.OnDestroy();
        }
        
        #endregion
        
        #region Screen Lifecycle
        
        /// <summary>
        /// Called when the screen is about to be shown
        /// </summary>
        protected virtual void OnScreenWillShow()
        {
            // Override in derived classes
        }
        
        /// <summary>
        /// Called when the screen has been shown
        /// </summary>
        protected virtual void OnScreenDidShow()
        {
            OnScreenOpened?.Invoke(this);
            OnScreenActivated?.Invoke(this);
        }
        
        /// <summary>
        /// Called when the screen is about to be hidden
        /// </summary>
        protected virtual void OnScreenWillHide()
        {
            // Override in derived classes
        }
        
        /// <summary>
        /// Called when the screen has been hidden
        /// </summary>
        protected virtual void OnScreenDidHide()
        {
            OnScreenClosed?.Invoke(this);
            OnScreenDeactivated?.Invoke(this);
        }
        
        #endregion
        
        #region Screen Control
        
        /// <summary>
        /// Show this screen through the screen manager
        /// </summary>
        public virtual void ShowScreen(bool addToHistory = true)
        {
            if (ScreenManager)
            {
                ScreenManager.ShowScreen(this, addToHistory, showTransition, showDuration);
            }
            else
            {
                Show();
            }
        }
        
        /// <summary>
        /// Hide this screen through the screen manager
        /// </summary>
        public virtual void HideScreen(bool instant = false)
        {
            if (ScreenManager)
            {
                ScreenManager.HideScreen(this, instant, hideTransition, hideDuration);
            }
            else
            {
                Hide(instant);
            }
        }
        
        /// <summary>
        /// Toggle this screen's visibility
        /// </summary>
        public virtual void ToggleScreen()
        {
            if (IsScreenActive)
            {
                HideScreen();
            }
            else
            {
                ShowScreen();
            }
        }
        
        /// <summary>
        /// Close this screen (same as hide but triggers close events)
        /// </summary>
        public virtual void CloseScreen()
        {
            OnScreenWillClose();
            HideScreen();
        }
        
        /// <summary>
        /// Called when the screen is about to close
        /// </summary>
        protected virtual void OnScreenWillClose()
        {
            // Override in derived classes
        }
        
        #endregion
        
        #region Navigation
        
        /// <summary>
        /// Navigate to another screen
        /// </summary>
        protected virtual void NavigateToScreen(string targetScreenId, bool hideCurrentScreen = true, bool addToHistory = true)
        {
            if (ScreenManager)
            {
                if (hideCurrentScreen && layer == ScreenLayer.Main)
                {
                    // Main screens typically replace each other
                    ScreenManager.ShowScreen(targetScreenId, addToHistory);
                }
                else
                {
                    // Other layers can coexist
                    ScreenManager.ShowScreen(targetScreenId, addToHistory);
                    if (hideCurrentScreen)
                    {
                        HideScreen();
                    }
                }
            }
        }
        
        /// <summary>
        /// Navigate back in history
        /// </summary>
        protected virtual bool NavigateBack()
        {
            if (ScreenManager && ScreenManager.HistoryCount > 1)
            {
                return ScreenManager.GoBack();
            }
            return false;
        }
        
        /// <summary>
        /// Show a popup screen over this one
        /// </summary>
        protected virtual void ShowPopup(string popupScreenId)
        {
            if (ScreenManager)
            {
                ScreenManager.ShowScreen(popupScreenId, false);
            }
        }
        
        /// <summary>
        /// Show a modal dialog over this screen
        /// </summary>
        protected virtual void ShowModal(string modalScreenId)
        {
            if (ScreenManager)
            {
                ScreenManager.ShowScreen(modalScreenId, false);
            }
        }
        
        #endregion
        
        #region Animation Overrides
        
        /// <summary>
        /// Show component with custom screen transition
        /// </summary>
        protected override void ShowAnimated()
        {
            OnScreenWillShow();
            
            switch (showTransition)
            {
                case ScreenTransition.None:
                    ShowInstant();
                    break;
                    
                case ScreenTransition.Fade:
                    FadeIn(showDuration, () => OnScreenDidShow());
                    break;
                    
                case ScreenTransition.Slide:
                    SlideIn(showDuration, () => OnScreenDidShow());
                    break;
                    
                case ScreenTransition.Scale:
                    ScaleIn(showDuration, () => OnScreenDidShow());
                    break;
                    
                case ScreenTransition.Custom:
                    ShowCustomTransition(() => OnScreenDidShow());
                    break;
                    
                default:
                    FadeIn(showDuration, () => OnScreenDidShow());
                    break;
            }
        }
        
        /// <summary>
        /// Hide component with custom screen transition
        /// </summary>
        protected override void HideAnimated()
        {
            OnScreenWillHide();
            
            switch (hideTransition)
            {
                case ScreenTransition.None:
                    HideInstant();
                    break;
                    
                case ScreenTransition.Fade:
                    FadeOut(hideDuration, () => OnScreenDidHide());
                    break;
                    
                case ScreenTransition.Slide:
                    SlideOut(hideDuration, () => OnScreenDidHide());
                    break;
                    
                case ScreenTransition.Scale:
                    ScaleOut(hideDuration, () => OnScreenDidHide());
                    break;
                    
                case ScreenTransition.Custom:
                    HideCustomTransition(() => OnScreenDidHide());
                    break;
                    
                default:
                    FadeOut(hideDuration, () => OnScreenDidHide());
                    break;
            }
        }
        
        /// <summary>
        /// Override show instant to include screen lifecycle
        /// </summary>
        protected override void ShowInstant()
        {
            OnScreenWillShow();
            base.ShowInstant();
            OnScreenDidShow();
        }
        
        /// <summary>
        /// Override hide instant to include screen lifecycle
        /// </summary>
        protected override void HideInstant()
        {
            OnScreenWillHide();
            base.HideInstant();
            OnScreenDidHide();
        }
        
        #endregion
        
        #region Custom Transitions
        
        /// <summary>
        /// Slide in transition
        /// </summary>
        protected virtual void SlideIn(float duration, Action onComplete = null)
        {
            if (!rectTransform) return;
            
            gameObject.SetActive(true);
            var startPos = rectTransform.anchoredPosition;
            var targetPos = startPos;
            
            // Start from off-screen (left side)
            startPos.x = -rectTransform.rect.width;
            rectTransform.anchoredPosition = startPos;
            
            if (canvasGroup)
            {
                canvasGroup.alpha = 1f;
                canvasGroup.interactable = false;
                canvasGroup.blocksRaycasts = false;
            }
            
            StartCoroutine(SlideCoroutine(startPos, targetPos, duration, () =>
            {
                if (canvasGroup)
                {
                    canvasGroup.interactable = IsInteractable;
                    canvasGroup.blocksRaycasts = true;
                }
                
                SetVisibleState(true);
                onComplete?.Invoke();
            }));
        }
        
        /// <summary>
        /// Slide out transition
        /// </summary>
        protected virtual void SlideOut(float duration, Action onComplete = null)
        {
            if (!rectTransform) return;
            
            var startPos = rectTransform.anchoredPosition;
            var targetPos = startPos;
            targetPos.x = rectTransform.rect.width; // Slide to right side
            
            if (canvasGroup)
            {
                canvasGroup.interactable = false;
                canvasGroup.blocksRaycasts = false;
            }
            
            StartCoroutine(SlideCoroutine(startPos, targetPos, duration, () =>
            {
                SetVisibleState(false);
                gameObject.SetActive(false);
                onComplete?.Invoke();
            }));
        }
        
        /// <summary>
        /// Scale in transition
        /// </summary>
        protected virtual void ScaleIn(float duration, Action onComplete = null)
        {
            if (!rectTransform) return;
            
            gameObject.SetActive(true);
            rectTransform.localScale = Vector3.zero;
            
            if (canvasGroup)
            {
                canvasGroup.alpha = 1f;
                canvasGroup.interactable = false;
                canvasGroup.blocksRaycasts = false;
            }
            
            StartCoroutine(ScaleCoroutine(Vector3.zero, Vector3.one, duration, () =>
            {
                if (canvasGroup)
                {
                    canvasGroup.interactable = IsInteractable;
                    canvasGroup.blocksRaycasts = true;
                }
                
                SetVisibleState(true);
                onComplete?.Invoke();
            }));
        }
        
        /// <summary>
        /// Scale out transition
        /// </summary>
        protected virtual void ScaleOut(float duration, Action onComplete = null)
        {
            if (!rectTransform) return;
            
            if (canvasGroup)
            {
                canvasGroup.interactable = false;
                canvasGroup.blocksRaycasts = false;
            }
            
            StartCoroutine(ScaleCoroutine(Vector3.one, Vector3.zero, duration, () =>
            {
                SetVisibleState(false);
                gameObject.SetActive(false);
                onComplete?.Invoke();
            }));
        }
        
        /// <summary>
        /// Custom show transition - override in derived classes
        /// </summary>
        protected virtual void ShowCustomTransition(Action onComplete = null)
        {
            // Override in derived classes for custom transitions
            ShowInstant();
            onComplete?.Invoke();
        }
        
        /// <summary>
        /// Custom hide transition - override in derived classes
        /// </summary>
        protected virtual void HideCustomTransition(Action onComplete = null)
        {
            // Override in derived classes for custom transitions
            HideInstant();
            onComplete?.Invoke();
        }
        
        #endregion
        
        #region Animation Coroutines
        
        /// <summary>
        /// Slide animation coroutine
        /// </summary>
        private System.Collections.IEnumerator SlideCoroutine(Vector2 from, Vector2 to, float duration, Action onComplete)
        {
            float elapsed = 0f;
            
            while (elapsed < duration)
            {
                elapsed += UnityEngine.Time.deltaTime;
                float t = Mathf.Clamp01(elapsed / duration);
                rectTransform.anchoredPosition = Vector2.Lerp(from, to, EaseInOut(t));
                yield return null;
            }
            
            rectTransform.anchoredPosition = to;
            onComplete?.Invoke();
        }
        
        /// <summary>
        /// Scale animation coroutine
        /// </summary>
        private System.Collections.IEnumerator ScaleCoroutine(Vector3 from, Vector3 to, float duration, Action onComplete)
        {
            float elapsed = 0f;
            
            while (elapsed < duration)
            {
                elapsed += UnityEngine.Time.deltaTime;
                float t = Mathf.Clamp01(elapsed / duration);
                rectTransform.localScale = Vector3.Lerp(from, to, EaseInOut(t));
                yield return null;
            }
            
            rectTransform.localScale = to;
            onComplete?.Invoke();
        }
        
        #endregion
        
        #region Utility
        
        /// <summary>
        /// Set screen configuration
        /// </summary>
        public void SetScreenConfig(string id, ScreenLayer screenLayer, int order = 0)
        {
            screenId = id;
            layer = screenLayer;
            sortOrder = order;
        }
        
        /// <summary>
        /// Set transition configuration
        /// </summary>
        public void SetTransitionConfig(ScreenTransition show, ScreenTransition hide, float showDur = 0.3f, float hideDur = 0.3f)
        {
            showTransition = show;
            hideTransition = hide;
            showDuration = showDur;
            hideDuration = hideDur;
        }
        
        /// <summary>
        /// Check if this screen can be shown (override for custom logic)
        /// </summary>
        public virtual bool CanShow()
        {
            return true;
        }
        
        /// <summary>
        /// Check if this screen can be hidden (override for custom logic)
        /// </summary>
        public virtual bool CanHide()
        {
            return true;
        }
        
        /// <summary>
        /// Get screen info for debugging
        /// </summary>
        public virtual string GetScreenInfo()
        {
            return $"Screen: {ScreenId}, Layer: {layer}, Order: {sortOrder}, Active: {IsScreenActive}, Visible: {IsVisible}";
        }
        
        #endregion
    }
} 