using UnityEngine;
using UnityEngine.UI;
using System;
using System.Collections;

namespace VDM.UI.Core
{
    /// <summary>
    /// Base class for all UI panels in the Visual DM system.
    /// Provides common functionality for panel lifecycle, animations, and state management.
    /// </summary>
    public abstract class BaseUIPanel : MonoBehaviour
    {
        [Header("Panel Configuration")]
        [SerializeField] protected bool startVisible = false;
        [SerializeField] protected bool destroyOnClose = false;
        [SerializeField] protected bool blockInput = true;
        
        [Header("Animation Settings")]
        [SerializeField] protected float fadeInDuration = 0.3f;
        [SerializeField] protected float fadeOutDuration = 0.3f;
        [SerializeField] protected AnimationCurve fadeCurve = AnimationCurve.EaseInOut(0, 0, 1, 1);
        
        // Events
        public event Action<BaseUIPanel> OnPanelOpened;
        public event Action<BaseUIPanel> OnPanelClosed;
        public event Action<BaseUIPanel> OnPanelDestroyed;
        
        // State
        public bool IsVisible { get; private set; }
        public bool IsAnimating { get; private set; }
        public string PanelId { get; protected set; }
        
        // Components
        protected CanvasGroup canvasGroup;
        protected GraphicRaycaster graphicRaycaster;
        protected Canvas canvas;
        
        // Coroutines
        private Coroutine animationCoroutine;
        
        protected virtual void Awake()
        {
            // Generate unique panel ID if not set
            if (string.IsNullOrEmpty(PanelId))
            {
                PanelId = GetType().Name + "_" + GetInstanceID();
            }
            
            // Get or add required components
            canvasGroup = GetComponent<CanvasGroup>();
            if (canvasGroup == null)
            {
                canvasGroup = gameObject.AddComponent<CanvasGroup>();
            }
            
            graphicRaycaster = GetComponent<GraphicRaycaster>();
            if (graphicRaycaster == null)
            {
                graphicRaycaster = gameObject.AddComponent<GraphicRaycaster>();
            }
            
            canvas = GetComponent<Canvas>();
            
            // Initialize panel state
            SetVisibility(startVisible, false);
        }
        
        protected virtual void Start()
        {
            OnPanelInitialized();
        }
        
        protected virtual void OnDestroy()
        {
            OnPanelDestroyed?.Invoke(this);
        }
        
        /// <summary>
        /// Called when the panel is first initialized. Override for custom initialization logic.
        /// </summary>
        protected virtual void OnPanelInitialized() { }
        
        /// <summary>
        /// Called when the panel is about to be shown. Override for custom show logic.
        /// </summary>
        protected virtual void OnPanelShowing() { }
        
        /// <summary>
        /// Called when the panel has finished showing. Override for custom logic.
        /// </summary>
        protected virtual void OnPanelShown() { }
        
        /// <summary>
        /// Called when the panel is about to be hidden. Override for custom hide logic.
        /// </summary>
        protected virtual void OnPanelHiding() { }
        
        /// <summary>
        /// Called when the panel has finished hiding. Override for custom logic.
        /// </summary>
        protected virtual void OnPanelHidden() { }
        
        /// <summary>
        /// Show the panel with optional animation.
        /// </summary>
        public virtual void Show(bool animate = true)
        {
            if (IsVisible || IsAnimating) return;
            
            OnPanelShowing();
            SetVisibility(true, animate);
        }
        
        /// <summary>
        /// Hide the panel with optional animation.
        /// </summary>
        public virtual void Hide(bool animate = true)
        {
            if (!IsVisible || IsAnimating) return;
            
            OnPanelHiding();
            SetVisibility(false, animate);
        }
        
        /// <summary>
        /// Toggle panel visibility.
        /// </summary>
        public virtual void Toggle(bool animate = true)
        {
            if (IsVisible)
                Hide(animate);
            else
                Show(animate);
        }
        
        /// <summary>
        /// Close the panel and optionally destroy it.
        /// </summary>
        public virtual void Close(bool animate = true)
        {
            if (!IsVisible && !IsAnimating) return;
            
            if (animate)
            {
                Hide(animate);
                if (destroyOnClose)
                {
                    StartCoroutine(DestroyAfterAnimation());
                }
            }
            else
            {
                SetVisibility(false, false);
                if (destroyOnClose)
                {
                    Destroy(gameObject);
                }
            }
        }
        
        /// <summary>
        /// Set panel visibility with optional animation.
        /// </summary>
        protected virtual void SetVisibility(bool visible, bool animate)
        {
            if (animationCoroutine != null)
            {
                StopCoroutine(animationCoroutine);
                animationCoroutine = null;
            }
            
            IsVisible = visible;
            gameObject.SetActive(true);
            
            if (animate && Application.isPlaying)
            {
                animationCoroutine = StartCoroutine(AnimateVisibility(visible));
            }
            else
            {
                // Set immediate values
                canvasGroup.alpha = visible ? 1f : 0f;
                canvasGroup.interactable = visible && !blockInput;
                canvasGroup.blocksRaycasts = visible;
                
                if (!visible)
                {
                    gameObject.SetActive(false);
                }
                
                // Trigger completion events
                if (visible)
                {
                    OnPanelShown();
                    OnPanelOpened?.Invoke(this);
                }
                else
                {
                    OnPanelHidden();
                    OnPanelClosed?.Invoke(this);
                }
            }
        }
        
        /// <summary>
        /// Animate panel visibility changes.
        /// </summary>
        protected virtual IEnumerator AnimateVisibility(bool visible)
        {
            IsAnimating = true;
            
            float duration = visible ? fadeInDuration : fadeOutDuration;
            float startAlpha = canvasGroup.alpha;
            float targetAlpha = visible ? 1f : 0f;
            float elapsedTime = 0f;
            
            // Set interactability during animation
            canvasGroup.interactable = false;
            canvasGroup.blocksRaycasts = visible;
            
            while (elapsedTime < duration)
            {
                elapsedTime += Time.unscaledDeltaTime;
                float progress = elapsedTime / duration;
                float curveValue = fadeCurve.Evaluate(progress);
                
                canvasGroup.alpha = Mathf.Lerp(startAlpha, targetAlpha, curveValue);
                
                yield return null;
            }
            
            // Ensure final values
            canvasGroup.alpha = targetAlpha;
            canvasGroup.interactable = visible && !blockInput;
            
            if (!visible)
            {
                gameObject.SetActive(false);
            }
            
            IsAnimating = false;
            animationCoroutine = null;
            
            // Trigger completion events
            if (visible)
            {
                OnPanelShown();
                OnPanelOpened?.Invoke(this);
            }
            else
            {
                OnPanelHidden();
                OnPanelClosed?.Invoke(this);
            }
        }
        
        /// <summary>
        /// Coroutine to destroy panel after animation completes.
        /// </summary>
        protected virtual IEnumerator DestroyAfterAnimation()
        {
            while (IsAnimating)
            {
                yield return null;
            }
            
            Destroy(gameObject);
        }
        
        /// <summary>
        /// Set the panel's sort order for layering.
        /// </summary>
        public virtual void SetSortOrder(int sortOrder)
        {
            if (canvas != null)
            {
                canvas.sortingOrder = sortOrder;
            }
        }
        
        /// <summary>
        /// Enable or disable input blocking.
        /// </summary>
        public virtual void SetInputBlocking(bool block)
        {
            blockInput = block;
            if (IsVisible && !IsAnimating)
            {
                canvasGroup.interactable = !block;
            }
        }
    }
} 