using System;
using UnityEngine;

namespace VDM.Infrastructure.Core.Core.Ui
{
    /// <summary>
    /// Base class for UI controllers in Unity frontend
    /// </summary>
    public abstract class UIController : MonoBehaviour
    {
        [Header("UI Controller Settings")]
        [SerializeField] protected bool enableOnStart = true;
        [SerializeField] protected bool hideOnStart = false;

        protected bool isInitialized = false;
        protected bool isVisible = true;

        // Events
        public event Action OnControllerEnabled;
        public event Action OnControllerDisabled;
        public event Action OnControllerShown;
        public event Action OnControllerHidden;

        protected virtual void Awake()
        {
            Initialize();
        }

        protected virtual void Start()
        {
            if (enableOnStart)
            {
                EnableController();
            }

            if (hideOnStart)
            {
                HideController();
            }
        }

        /// <summary>
        /// Initialize the UI controller
        /// </summary>
        protected virtual void Initialize()
        {
            if (isInitialized) return;

            // Perform initialization logic
            OnInitialize();
            
            isInitialized = true;
            Debug.Log($"[{GetType().Name}] UI Controller initialized");
        }

        /// <summary>
        /// Override this method for custom initialization logic
        /// </summary>
        protected virtual void OnInitialize()
        {
            // Override in derived classes
        }

        /// <summary>
        /// Enable the UI controller
        /// </summary>
        public virtual void EnableController()
        {
            if (!isInitialized) Initialize();
            
            gameObject.SetActive(true);
            OnControllerEnabled?.Invoke();
            Debug.Log($"[{GetType().Name}] UI Controller enabled");
        }

        /// <summary>
        /// Disable the UI controller
        /// </summary>
        public virtual void DisableController()
        {
            gameObject.SetActive(false);
            OnControllerDisabled?.Invoke();
            Debug.Log($"[{GetType().Name}] UI Controller disabled");
        }

        /// <summary>
        /// Show the UI controller
        /// </summary>
        public virtual void ShowController()
        {
            isVisible = true;
            SetVisibility(true);
            OnControllerShown?.Invoke();
        }

        /// <summary>
        /// Hide the UI controller
        /// </summary>
        public virtual void HideController()
        {
            isVisible = false;
            SetVisibility(false);
            OnControllerHidden?.Invoke();
        }

        /// <summary>
        /// Toggle visibility of the UI controller
        /// </summary>
        public virtual void ToggleController()
        {
            if (isVisible)
            {
                HideController();
            }
            else
            {
                ShowController();
            }
        }

        /// <summary>
        /// Set the visibility of the UI elements
        /// </summary>
        protected virtual void SetVisibility(bool visible)
        {
            // Override in derived classes to handle specific UI visibility logic
            var canvasGroup = GetComponent<CanvasGroup>();
            if (canvasGroup != null)
            {
                canvasGroup.alpha = visible ? 1f : 0f;
                canvasGroup.interactable = visible;
                canvasGroup.blocksRaycasts = visible;
            }
        }

        /// <summary>
        /// Refresh the UI controller
        /// </summary>
        public virtual void RefreshController()
        {
            // Override in derived classes
        }

        /// <summary>
        /// Cleanup when controller is destroyed
        /// </summary>
        protected virtual void OnDestroy()
        {
            // Override in derived classes for cleanup
        }
    }
} 