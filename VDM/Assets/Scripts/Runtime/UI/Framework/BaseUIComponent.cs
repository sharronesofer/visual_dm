using System.Collections.Generic;
using System;
using TMPro;
using UnityEngine.UI;
using UnityEngine;


namespace VDM.Runtime.UI.Framework
{
    /// <summary>
    /// Base class for all UI components providing common functionality
    /// </summary>
    public abstract class BaseUIComponent : MonoBehaviour
    {
        [Header("Base UI Component")]
        [SerializeField] protected bool initializeOnAwake = true;
        [SerializeField] protected bool showOnStart = false;
        [SerializeField] protected CanvasGroup canvasGroup;
        [SerializeField] protected RectTransform rectTransform;
        
        // State management
        public bool IsInitialized { get; private set; }
        public bool IsVisible { get; private set; }
        public bool IsInteractable { get; private set; } = true;
        
        // Events
        public event Action OnInitialized;
        public event Action OnShown;
        public event Action OnHidden;
        public event Action OnDestroyed;
        
        // Component cache
        protected Dictionary<Type, Component> componentCache = new Dictionary<Type, Component>();
        
        #region Unity Lifecycle
        
        protected virtual void Awake()
        {
            CacheComponents();
            
            if (initializeOnAwake)
            {
                Initialize();
            }
        }
        
        protected virtual void Start()
        {
            if (showOnStart)
            {
                Show();
            }
            else
            {
                Hide(instant: true);
            }
        }
        
        protected virtual void OnDestroy()
        {
            OnDestroyed?.Invoke();
            CleanupInternal();
        }
        
        #endregion
        
        #region Component Management
        
        /// <summary>
        /// Cache commonly used components for performance
        /// </summary>
        protected virtual void CacheComponents()
        {
            if (!rectTransform)
                rectTransform = GetComponent<RectTransform>();
            
            if (!canvasGroup)
                canvasGroup = GetComponent<CanvasGroup>();
        }
        
        /// <summary>
        /// Get a cached component of type T
        /// </summary>
        protected T GetCachedComponent<T>() where T : Component
        {
            var type = typeof(T);
            if (componentCache.TryGetValue(type, out var component))
            {
                return component as T;
            }
            
            component = GetComponent<T>();
            if (component)
            {
                componentCache[type] = component;
            }
            
            return component as T;
        }
        
        /// <summary>
        /// Get a cached component of type T in children
        /// </summary>
        protected T GetCachedComponentInChildren<T>() where T : Component
        {
            var type = typeof(T);
            var key = $"{type.Name}_Child";
            
            if (componentCache.TryGetValue(type, out var component))
            {
                return component as T;
            }
            
            component = GetComponentInChildren<T>();
            if (component)
            {
                componentCache[type] = component;
            }
            
            return component as T;
        }
        
        #endregion
        
        #region Initialization
        
        /// <summary>
        /// Initialize the UI component
        /// </summary>
        public virtual void Initialize()
        {
            if (IsInitialized) return;
            
            try
            {
                OnInitialize();
                IsInitialized = true;
                OnInitialized?.Invoke();
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to initialize UI component {name}: {ex.Message}");
            }
        }
        
        /// <summary>
        /// Override this method to implement custom initialization logic
        /// </summary>
        protected virtual void OnInitialize()
        {
            // Override in derived classes
        }
        
        #endregion
        
        #region Visibility Management
        
        /// <summary>
        /// Show the UI component
        /// </summary>
        public virtual void Show(bool instant = false)
        {
            if (!IsInitialized)
            {
                Initialize();
            }
            
            gameObject.SetActive(true);
            
            if (instant)
            {
                ShowInstant();
            }
            else
            {
                ShowAnimated();
            }
        }
        
        /// <summary>
        /// Hide the UI component
        /// </summary>
        public virtual void Hide(bool instant = false)
        {
            if (instant)
            {
                HideInstant();
            }
            else
            {
                HideAnimated();
            }
        }
        
        /// <summary>
        /// Toggle visibility of the UI component
        /// </summary>
        public virtual void Toggle(bool instant = false)
        {
            if (IsVisible)
            {
                Hide(instant);
            }
            else
            {
                Show(instant);
            }
        }
        
        /// <summary>
        /// Show component instantly without animation
        /// </summary>
        protected virtual void ShowInstant()
        {
            if (canvasGroup)
            {
                canvasGroup.alpha = 1f;
                canvasGroup.interactable = IsInteractable;
                canvasGroup.blocksRaycasts = true;
            }
            
            IsVisible = true;
            OnShow();
            OnShown?.Invoke();
        }
        
        /// <summary>
        /// Hide component instantly without animation
        /// </summary>
        protected virtual void HideInstant()
        {
            if (canvasGroup)
            {
                canvasGroup.alpha = 0f;
                canvasGroup.interactable = false;
                canvasGroup.blocksRaycasts = false;
            }
            
            IsVisible = false;
            OnHide();
            OnHidden?.Invoke();
            
            gameObject.SetActive(false);
        }
        
        /// <summary>
        /// Show component with animation
        /// </summary>
        protected virtual void ShowAnimated()
        {
            // Default implementation - override for custom animations
            ShowInstant();
        }
        
        /// <summary>
        /// Hide component with animation
        /// </summary>
        protected virtual void HideAnimated()
        {
            // Default implementation - override for custom animations
            HideInstant();
        }
        
        /// <summary>
        /// Called when component is shown
        /// </summary>
        protected virtual void OnShow()
        {
            // Override in derived classes
        }
        
        /// <summary>
        /// Called when component is hidden
        /// </summary>
        protected virtual void OnHide()
        {
            // Override in derived classes
        }
        
        #endregion
        
        #region Interactability
        
        /// <summary>
        /// Set the interactable state of the component
        /// </summary>
        public virtual void SetInteractable(bool interactable)
        {
            IsInteractable = interactable;
            
            if (canvasGroup)
            {
                canvasGroup.interactable = interactable;
            }
            
            OnInteractabilityChanged(interactable);
        }
        
        /// <summary>
        /// Called when interactability changes
        /// </summary>
        protected virtual void OnInteractabilityChanged(bool interactable)
        {
            // Override in derived classes
        }
        
        #endregion
        
        #region Animation Helpers
        
        /// <summary>
        /// Fade in the component
        /// </summary>
        protected virtual void FadeIn(float duration = 0.3f, Action onComplete = null)
        {
            if (!canvasGroup) return;
            
            gameObject.SetActive(true);
            canvasGroup.interactable = false;
            canvasGroup.blocksRaycasts = false;
            
            // Use LeanTween or DOTween if available, otherwise use coroutine
            StartCoroutine(FadeCoroutine(0f, 1f, duration, () =>
            {
                canvasGroup.interactable = IsInteractable;
                canvasGroup.blocksRaycasts = true;
                IsVisible = true;
                OnShow();
                OnShown?.Invoke();
                onComplete?.Invoke();
            }));
        }
        
        /// <summary>
        /// Fade out the component
        /// </summary>
        protected virtual void FadeOut(float duration = 0.3f, Action onComplete = null)
        {
            if (!canvasGroup) return;
            
            canvasGroup.interactable = false;
            canvasGroup.blocksRaycasts = false;
            
            StartCoroutine(FadeCoroutine(canvasGroup.alpha, 0f, duration, () =>
            {
                IsVisible = false;
                OnHide();
                OnHidden?.Invoke();
                gameObject.SetActive(false);
                onComplete?.Invoke();
            }));
        }
        
        /// <summary>
        /// Coroutine for fading animation
        /// </summary>
        private System.Collections.IEnumerator FadeCoroutine(float from, float to, float duration, Action onComplete)
        {
            float elapsed = 0f;
            
            while (elapsed < duration)
            {
                elapsed += Time.deltaTime;
                float t = Mathf.Clamp01(elapsed / duration);
                canvasGroup.alpha = Mathf.Lerp(from, to, EaseInOut(t));
                yield return null;
            }
            
            canvasGroup.alpha = to;
            onComplete?.Invoke();
        }
        
        /// <summary>
        /// Ease in-out function for smooth animations
        /// </summary>
        protected virtual float EaseInOut(float t)
        {
            return t * t * (3f - 2f * t);
        }
        
        #endregion
        
        #region Layout Helpers
        
        /// <summary>
        /// Set the anchor and position of the RectTransform
        /// </summary>
        protected virtual void SetAnchor(Vector2 anchorMin, Vector2 anchorMax, Vector2 anchoredPosition)
        {
            if (!rectTransform) return;
            
            rectTransform.anchorMin = anchorMin;
            rectTransform.anchorMax = anchorMax;
            rectTransform.anchoredPosition = anchoredPosition;
        }
        
        /// <summary>
        /// Set the size of the RectTransform
        /// </summary>
        protected virtual void SetSize(Vector2 size)
        {
            if (!rectTransform) return;
            
            rectTransform.sizeDelta = size;
        }
        
        /// <summary>
        /// Fill the parent completely
        /// </summary>
        protected virtual void FillParent()
        {
            if (!rectTransform) return;
            
            rectTransform.anchorMin = Vector2.zero;
            rectTransform.anchorMax = Vector2.one;
            rectTransform.offsetMin = Vector2.zero;
            rectTransform.offsetMax = Vector2.zero;
        }
        
        #endregion
        
        #region Utility
        
        /// <summary>
        /// Find a child component by name
        /// </summary>
        protected T FindChildComponent<T>(string childName) where T : Component
        {
            var childTransform = transform.Find(childName);
            return childTransform ? childTransform.GetComponent<T>() : null;
        }
        
        /// <summary>
        /// Get or add a component
        /// </summary>
        protected T GetOrAddComponent<T>() where T : Component
        {
            var component = GetComponent<T>();
            if (!component)
            {
                component = gameObject.AddComponent<T>();
            }
            return component;
        }
        
        /// <summary>
        /// Safe destroy GameObject
        /// </summary>
        protected virtual void SafeDestroy(GameObject obj)
        {
            if (obj)
            {
                if (Application.isPlaying)
                {
                    Destroy(obj);
                }
                else
                {
                    DestroyImmediate(obj);
                }
            }
        }
        
        #endregion
        
        #region Cleanup
        
        /// <summary>
        /// Internal cleanup called on destroy
        /// </summary>
        private void CleanupInternal()
        {
            componentCache.Clear();
            OnCleanup();
        }
        
        /// <summary>
        /// Override this method to implement custom cleanup logic
        /// </summary>
        protected virtual void OnCleanup()
        {
            // Override in derived classes
        }
        
        #endregion
    }
} 