using UnityEngine;
using UnityEngine.UI;
using System;
using System.Collections.Generic;
using TMPro;

namespace VDM.UI.Core
{
    /// <summary>
    /// Modal dialog system for Visual DM.
    /// Handles confirmation dialogs, alerts, and custom modal content.
    /// </summary>
    public class ModalSystem : MonoBehaviour
    {
        [Header("Modal Configuration")]
        [SerializeField] private GameObject modalPrefab;
        [SerializeField] private Transform modalContainer;
        [SerializeField] private bool blockInputBehindModal = true;
        [SerializeField] private Color overlayColor = new Color(0, 0, 0, 0.5f);
        
        [Header("Animation Settings")]
        [SerializeField] private float fadeInDuration = 0.3f;
        [SerializeField] private float fadeOutDuration = 0.2f;
        [SerializeField] private AnimationCurve scaleCurve = AnimationCurve.EaseInOut(0, 0.8f, 1, 1);
        
        // Singleton
        public static ModalSystem Instance { get; private set; }
        
        // Events
        public event Action<Modal> OnModalOpened;
        public event Action<Modal> OnModalClosed;
        
        // State
        private List<Modal> activeModals = new List<Modal>();
        private GameObject overlayObject;
        private CanvasGroup overlayCanvasGroup;
        
        public bool HasActiveModals => activeModals.Count > 0;
        public int ActiveModalCount => activeModals.Count;
        
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
            
            // Create overlay if it doesn't exist
            CreateOverlay();
        }
        
        private void OnDestroy()
        {
            if (Instance == this)
            {
                Instance = null;
            }
        }
        
        /// <summary>
        /// Create the modal overlay background.
        /// </summary>
        private void CreateOverlay()
        {
            if (overlayObject != null) return;
            
            // Create overlay GameObject
            overlayObject = new GameObject("ModalOverlay");
            overlayObject.transform.SetParent(transform);
            
            // Add Canvas component
            Canvas overlayCanvas = overlayObject.AddComponent<Canvas>();
            overlayCanvas.sortingOrder = 190; // Just below modal layer
            
            // Add CanvasGroup for fading
            overlayCanvasGroup = overlayObject.AddComponent<CanvasGroup>();
            overlayCanvasGroup.alpha = 0f;
            overlayCanvasGroup.blocksRaycasts = false;
            
            // Add Image component for background
            Image overlayImage = overlayObject.AddComponent<Image>();
            overlayImage.color = overlayColor;
            
            // Set to full screen
            RectTransform rectTransform = overlayObject.GetComponent<RectTransform>();
            rectTransform.anchorMin = Vector2.zero;
            rectTransform.anchorMax = Vector2.one;
            rectTransform.offsetMin = Vector2.zero;
            rectTransform.offsetMax = Vector2.zero;
            
            overlayObject.SetActive(false);
        }
        
        #region Modal Creation
        
        /// <summary>
        /// Show a simple alert modal.
        /// </summary>
        public Modal ShowAlert(string title, string message, Action onConfirm = null)
        {
            var config = new ModalConfig
            {
                title = title,
                message = message,
                buttons = new List<ModalButton>
                {
                    new ModalButton("OK", onConfirm, true)
                }
            };
            
            return ShowModal(config);
        }
        
        /// <summary>
        /// Show a confirmation modal with Yes/No buttons.
        /// </summary>
        public Modal ShowConfirmation(string title, string message, Action onConfirm = null, Action onCancel = null)
        {
            var config = new ModalConfig
            {
                title = title,
                message = message,
                buttons = new List<ModalButton>
                {
                    new ModalButton("Cancel", onCancel, false),
                    new ModalButton("Confirm", onConfirm, true)
                }
            };
            
            return ShowModal(config);
        }
        
        /// <summary>
        /// Show a custom modal with specified configuration.
        /// </summary>
        public Modal ShowModal(ModalConfig config)
        {
            if (modalPrefab == null)
            {
                Debug.LogError("ModalSystem: Modal prefab not assigned.");
                return null;
            }
            
            // Instantiate modal
            GameObject modalObject = Instantiate(modalPrefab, modalContainer != null ? modalContainer : transform);
            Modal modal = modalObject.GetComponent<Modal>();
            
            if (modal == null)
            {
                modal = modalObject.AddComponent<Modal>();
            }
            
            // Configure modal
            modal.Initialize(config);
            modal.OnModalClosed += HandleModalClosed;
            
            // Add to active modals
            activeModals.Add(modal);
            
            // Show overlay if this is the first modal
            if (activeModals.Count == 1)
            {
                ShowOverlay();
            }
            
            // Set layer order
            if (UIManager.Instance != null)
            {
                UIManager.Instance.SetPanelLayer(modal, UIManager.UILayer.Modal);
            }
            
            // Show modal
            modal.Show();
            
            OnModalOpened?.Invoke(modal);
            return modal;
        }
        
        #endregion
        
        #region Modal Management
        
        /// <summary>
        /// Close a specific modal.
        /// </summary>
        public void CloseModal(Modal modal)
        {
            if (modal == null || !activeModals.Contains(modal)) return;
            
            modal.Close();
        }
        
        /// <summary>
        /// Close the topmost modal.
        /// </summary>
        public void CloseTopModal()
        {
            if (activeModals.Count == 0) return;
            
            Modal topModal = activeModals[activeModals.Count - 1];
            CloseModal(topModal);
        }
        
        /// <summary>
        /// Close all active modals.
        /// </summary>
        public void CloseAllModals()
        {
            var modalsToClose = new List<Modal>(activeModals);
            foreach (var modal in modalsToClose)
            {
                modal.Close();
            }
        }
        
        /// <summary>
        /// Handle modal closed event.
        /// </summary>
        private void HandleModalClosed(Modal modal)
        {
            activeModals.Remove(modal);
            
            // Hide overlay if no more modals
            if (activeModals.Count == 0)
            {
                HideOverlay();
            }
            
            OnModalClosed?.Invoke(modal);
        }
        
        #endregion
        
        #region Overlay Management
        
        /// <summary>
        /// Show the modal overlay.
        /// </summary>
        private void ShowOverlay()
        {
            if (overlayObject == null) return;
            
            overlayObject.SetActive(true);
            overlayCanvasGroup.blocksRaycasts = blockInputBehindModal;
            
            // Animate overlay fade in
            StartCoroutine(AnimateOverlay(true));
        }
        
        /// <summary>
        /// Hide the modal overlay.
        /// </summary>
        private void HideOverlay()
        {
            if (overlayObject == null) return;
            
            // Animate overlay fade out
            StartCoroutine(AnimateOverlay(false));
        }
        
        /// <summary>
        /// Animate overlay visibility.
        /// </summary>
        private System.Collections.IEnumerator AnimateOverlay(bool show)
        {
            float duration = show ? fadeInDuration : fadeOutDuration;
            float startAlpha = overlayCanvasGroup.alpha;
            float targetAlpha = show ? 1f : 0f;
            float elapsedTime = 0f;
            
            while (elapsedTime < duration)
            {
                elapsedTime += Time.unscaledDeltaTime;
                float progress = elapsedTime / duration;
                overlayCanvasGroup.alpha = Mathf.Lerp(startAlpha, targetAlpha, progress);
                yield return null;
            }
            
            overlayCanvasGroup.alpha = targetAlpha;
            
            if (!show)
            {
                overlayObject.SetActive(false);
                overlayCanvasGroup.blocksRaycasts = false;
            }
        }
        
        #endregion
    }
    
    /// <summary>
    /// Configuration for modal dialogs.
    /// </summary>
    [System.Serializable]
    public class ModalConfig
    {
        public string title = "";
        public string message = "";
        public List<ModalButton> buttons = new List<ModalButton>();
        public bool closeOnOverlayClick = true;
        public bool showCloseButton = true;
        public Sprite icon = null;
        public GameObject customContent = null;
    }
    
    /// <summary>
    /// Configuration for modal buttons.
    /// </summary>
    [System.Serializable]
    public class ModalButton
    {
        public string text;
        public Action callback;
        public bool isPrimary;
        public bool closesModal;
        
        public ModalButton(string text, Action callback = null, bool isPrimary = false, bool closesModal = true)
        {
            this.text = text;
            this.callback = callback;
            this.isPrimary = isPrimary;
            this.closesModal = closesModal;
        }
    }
    
    /// <summary>
    /// Individual modal dialog component.
    /// </summary>
    public class Modal : BaseUIPanel
    {
        [Header("Modal Components")]
        [SerializeField] private TextMeshProUGUI titleText;
        [SerializeField] private TextMeshProUGUI messageText;
        [SerializeField] private Image iconImage;
        [SerializeField] private Button closeButton;
        [SerializeField] private Transform buttonContainer;
        [SerializeField] private GameObject buttonPrefab;
        [SerializeField] private Transform customContentContainer;
        
        // Events
        public event Action<Modal> OnModalClosed;
        
        // Configuration
        private ModalConfig config;
        private List<Button> createdButtons = new List<Button>();
        
        /// <summary>
        /// Initialize the modal with configuration.
        /// </summary>
        public void Initialize(ModalConfig config)
        {
            this.config = config;
            SetupModal();
        }
        
        /// <summary>
        /// Setup modal content based on configuration.
        /// </summary>
        private void SetupModal()
        {
            if (config == null) return;
            
            // Set title
            if (titleText != null)
            {
                titleText.text = config.title;
                titleText.gameObject.SetActive(!string.IsNullOrEmpty(config.title));
            }
            
            // Set message
            if (messageText != null)
            {
                messageText.text = config.message;
                messageText.gameObject.SetActive(!string.IsNullOrEmpty(config.message));
            }
            
            // Set icon
            if (iconImage != null)
            {
                iconImage.sprite = config.icon;
                iconImage.gameObject.SetActive(config.icon != null);
            }
            
            // Setup close button
            if (closeButton != null)
            {
                closeButton.gameObject.SetActive(config.showCloseButton);
                closeButton.onClick.RemoveAllListeners();
                closeButton.onClick.AddListener(() => Close());
            }
            
            // Setup custom content
            if (customContentContainer != null && config.customContent != null)
            {
                Instantiate(config.customContent, customContentContainer);
            }
            
            // Create buttons
            CreateButtons();
        }
        
        /// <summary>
        /// Create buttons based on configuration.
        /// </summary>
        private void CreateButtons()
        {
            if (buttonContainer == null || buttonPrefab == null) return;
            
            // Clear existing buttons
            foreach (var button in createdButtons)
            {
                if (button != null)
                {
                    DestroyImmediate(button.gameObject);
                }
            }
            createdButtons.Clear();
            
            // Create new buttons
            foreach (var buttonConfig in config.buttons)
            {
                GameObject buttonObject = Instantiate(buttonPrefab, buttonContainer);
                Button button = buttonObject.GetComponent<Button>();
                
                if (button != null)
                {
                    // Set button text
                    TextMeshProUGUI buttonText = button.GetComponentInChildren<TextMeshProUGUI>();
                    if (buttonText != null)
                    {
                        buttonText.text = buttonConfig.text;
                    }
                    
                    // Setup button callback
                    button.onClick.RemoveAllListeners();
                    button.onClick.AddListener(() =>
                    {
                        buttonConfig.callback?.Invoke();
                        if (buttonConfig.closesModal)
                        {
                            Close();
                        }
                    });
                    
                    // Apply primary button styling if needed
                    if (buttonConfig.isPrimary)
                    {
                        // Add primary button styling here
                        // This could be done through a theme system
                    }
                    
                    createdButtons.Add(button);
                }
            }
        }
        
        protected virtual void OnPanelClosed()
        {
            base.OnPanelClosed();
            OnModalClosed?.Invoke(this);
        }
        
        protected override void OnDestroy()
        {
            base.OnDestroy();
            
            // Clean up created buttons
            foreach (var button in createdButtons)
            {
                if (button != null)
                {
                    DestroyImmediate(button.gameObject);
                }
            }
            createdButtons.Clear();
        }
    }
} 