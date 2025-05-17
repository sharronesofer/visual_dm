using UnityEngine;
using UnityEngine.UI;
using TMPro;
using System;

namespace VisualDM.UI
{
    /// <summary>
    /// Base class for all UI components, providing common functionality.
    /// This is similar to a base React component with shared props and methods.
    /// </summary>
    public abstract class UIComponent : MonoBehaviour
    {
        [Header("Common UI Properties")]
        [SerializeField] protected bool interactable = true;
        [SerializeField] protected bool visible = true;
        
        // References to common UI elements
        protected RectTransform rectTransform;
        protected CanvasGroup canvasGroup;
        
        // Events similar to React component lifecycle methods
        public event Action OnMount;
        public event Action OnUnmount;
        public event Action OnUpdate;
        
        protected virtual void Awake()
        {
            // Get required components (similar to React useRef)
            rectTransform = GetComponent<RectTransform>();
            if (rectTransform == null)
                rectTransform = gameObject.AddComponent<RectTransform>();
                
            canvasGroup = GetComponent<CanvasGroup>();
            if (canvasGroup == null)
                canvasGroup = gameObject.AddComponent<CanvasGroup>();
        }
        
        protected virtual void Start()
        {
            // Similar to React's componentDidMount or useEffect with empty dependency array
            UpdateVisibility();
            UpdateInteractability();
            OnMount?.Invoke();
        }
        
        protected virtual void OnDestroy()
        {
            // Similar to React's componentWillUnmount or useEffect cleanup function
            OnUnmount?.Invoke();
        }
        
        protected virtual void Update()
        {
            // Unity's built-in update loop - use carefully similar to how you'd use useEffect
            OnUpdate?.Invoke();
        }
        
        /// <summary>
        /// Set the visibility of this UI component
        /// </summary>
        public virtual void SetVisibility(bool isVisible)
        {
            visible = isVisible;
            UpdateVisibility();
        }
        
        /// <summary>
        /// Set the interactability of this UI component
        /// </summary>
        public virtual void SetInteractability(bool isInteractable)
        {
            interactable = isInteractable;
            UpdateInteractability();
        }
        
        /// <summary>
        /// Updates the visibility state of the component
        /// </summary>
        protected virtual void UpdateVisibility()
        {
            if (canvasGroup != null)
            {
                canvasGroup.alpha = visible ? 1f : 0f;
                canvasGroup.blocksRaycasts = visible;
            }
            else
            {
                gameObject.SetActive(visible);
            }
        }
        
        /// <summary>
        /// Updates the interactability state of the component
        /// </summary>
        protected virtual void UpdateInteractability()
        {
            if (canvasGroup != null)
            {
                canvasGroup.interactable = interactable;
            }
            
            // Update interactability of any child selectable components if needed
            Selectable[] selectables = GetComponentsInChildren<Selectable>();
            foreach (var selectable in selectables)
            {
                selectable.interactable = interactable;
            }
        }
        
        /// <summary>
        /// Set position within parent (similar to CSS positioning)
        /// </summary>
        public virtual void SetPosition(Vector2 position)
        {
            if (rectTransform != null)
            {
                rectTransform.anchoredPosition = position;
            }
        }
        
        /// <summary>
        /// Set size (similar to CSS width/height)
        /// </summary>
        public virtual void SetSize(Vector2 size)
        {
            if (rectTransform != null)
            {
                rectTransform.sizeDelta = size;
            }
        }
        
        /// <summary>
        /// Set anchoring (similar to CSS positioning)
        /// </summary>
        public virtual void SetAnchors(Vector2 min, Vector2 max)
        {
            if (rectTransform != null)
            {
                rectTransform.anchorMin = min;
                rectTransform.anchorMax = max;
            }
        }
        
        /// <summary>
        /// Set padding (similar to CSS padding)
        /// </summary>
        public virtual void SetPadding(float left, float right, float top, float bottom)
        {
            if (rectTransform != null)
            {
                rectTransform.offsetMin = new Vector2(left, bottom);
                rectTransform.offsetMax = new Vector2(-right, -top);
            }
        }
    }
} 