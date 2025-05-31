using UnityEngine;
using UnityEngine.UI;
using System;
using System.Collections;
using System.Collections.Generic;
using TMPro;

namespace VDM.UI.Core
{
    /// <summary>
    /// Loading system for Visual DM.
    /// Handles loading screens, progress indicators, and async operation feedback.
    /// </summary>
    public class LoadingSystem : MonoBehaviour
    {
        [Header("Loading Configuration")]
        [SerializeField] private GameObject loadingPrefab;
        [SerializeField] private Transform loadingContainer;
        [SerializeField] private bool blockInputDuringLoading = true;
        [SerializeField] private float minDisplayTime = 0.5f;
        
        [Header("Default Loading Settings")]
        [SerializeField] private string defaultLoadingText = "Loading...";
        [SerializeField] private Color overlayColor = new Color(0, 0, 0, 0.7f);
        
        // Singleton
        public static LoadingSystem Instance { get; private set; }
        
        // Events
        public event Action<LoadingOperation> OnLoadingStarted;
        public event Action<LoadingOperation> OnLoadingCompleted;
        public event Action<LoadingOperation, float> OnLoadingProgressChanged;
        
        // State
        private Dictionary<string, LoadingOperation> activeOperations = new Dictionary<string, LoadingOperation>();
        private LoadingOverlay currentOverlay;
        private int operationCounter = 0;
        
        public bool IsLoading => activeOperations.Count > 0;
        public int ActiveOperationCount => activeOperations.Count;
        
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
        }
        
        private void OnDestroy()
        {
            if (Instance == this)
            {
                Instance = null;
            }
        }
        
        #region Public API
        
        /// <summary>
        /// Start a simple loading operation.
        /// </summary>
        public LoadingOperation StartLoading(string message = null)
        {
            return StartLoading(new LoadingConfig
            {
                message = message ?? defaultLoadingText,
                showProgress = false,
                allowCancel = false
            });
        }
        
        /// <summary>
        /// Start a loading operation with progress tracking.
        /// </summary>
        public LoadingOperation StartLoadingWithProgress(string message = null, bool allowCancel = false)
        {
            return StartLoading(new LoadingConfig
            {
                message = message ?? defaultLoadingText,
                showProgress = true,
                allowCancel = allowCancel
            });
        }
        
        /// <summary>
        /// Start a loading operation with full configuration.
        /// </summary>
        public LoadingOperation StartLoading(LoadingConfig config)
        {
            string operationId = GenerateOperationId();
            var operation = new LoadingOperation(operationId, config);
            
            activeOperations[operationId] = operation;
            
            // Show overlay if this is the first operation
            if (activeOperations.Count == 1)
            {
                ShowLoadingOverlay();
            }
            
            // Update overlay with current operation
            UpdateLoadingOverlay();
            
            OnLoadingStarted?.Invoke(operation);
            return operation;
        }
        
        /// <summary>
        /// Update progress for a loading operation.
        /// </summary>
        public void UpdateProgress(string operationId, float progress, string message = null)
        {
            if (!activeOperations.TryGetValue(operationId, out LoadingOperation operation)) return;
            
            operation.UpdateProgress(progress, message);
            UpdateLoadingOverlay();
            
            OnLoadingProgressChanged?.Invoke(operation, progress);
        }
        
        /// <summary>
        /// Complete a loading operation.
        /// </summary>
        public void CompleteLoading(string operationId)
        {
            if (!activeOperations.TryGetValue(operationId, out LoadingOperation operation)) return;
            
            operation.Complete();
            activeOperations.Remove(operationId);
            
            // Hide overlay if no more operations
            if (activeOperations.Count == 0)
            {
                HideLoadingOverlay();
            }
            else
            {
                UpdateLoadingOverlay();
            }
            
            OnLoadingCompleted?.Invoke(operation);
        }
        
        /// <summary>
        /// Cancel a loading operation.
        /// </summary>
        public void CancelLoading(string operationId)
        {
            if (!activeOperations.TryGetValue(operationId, out LoadingOperation operation)) return;
            
            if (operation.Config.allowCancel)
            {
                operation.Cancel();
                activeOperations.Remove(operationId);
                
                // Hide overlay if no more operations
                if (activeOperations.Count == 0)
                {
                    HideLoadingOverlay();
                }
                else
                {
                    UpdateLoadingOverlay();
                }
                
                OnLoadingCompleted?.Invoke(operation);
            }
        }
        
        /// <summary>
        /// Cancel all active loading operations.
        /// </summary>
        public void CancelAllLoading()
        {
            var operationsToCancel = new List<string>(activeOperations.Keys);
            foreach (var operationId in operationsToCancel)
            {
                CancelLoading(operationId);
            }
        }
        
        #endregion
        
        #region Overlay Management
        
        /// <summary>
        /// Show the loading overlay.
        /// </summary>
        private void ShowLoadingOverlay()
        {
            if (currentOverlay != null) return;
            
            if (loadingPrefab == null)
            {
                CreateDefaultLoadingOverlay();
            }
            else
            {
                CreateLoadingOverlay();
            }
            
            // Set layer order
            if (UIManager.Instance != null)
            {
                UIManager.Instance.SetPanelLayer(currentOverlay, UIManager.UILayer.Overlay);
            }
            
            currentOverlay.Show();
        }
        
        /// <summary>
        /// Hide the loading overlay.
        /// </summary>
        private void HideLoadingOverlay()
        {
            if (currentOverlay == null) return;
            
            StartCoroutine(HideLoadingOverlayCoroutine());
        }
        
        /// <summary>
        /// Hide loading overlay with minimum display time.
        /// </summary>
        private IEnumerator HideLoadingOverlayCoroutine()
        {
            if (currentOverlay == null) yield break;
            
            // Ensure minimum display time
            float displayTime = Time.time - currentOverlay.StartTime;
            if (displayTime < minDisplayTime)
            {
                yield return new WaitForSeconds(minDisplayTime - displayTime);
            }
            
            currentOverlay.Hide();
            
            // Wait for hide animation
            yield return new WaitForSeconds(0.3f);
            
            if (currentOverlay != null)
            {
                Destroy(currentOverlay.gameObject);
                currentOverlay = null;
            }
        }
        
        /// <summary>
        /// Update the loading overlay with current operation info.
        /// </summary>
        private void UpdateLoadingOverlay()
        {
            if (currentOverlay == null) return;
            
            // Get the most recent operation
            LoadingOperation currentOperation = null;
            foreach (var operation in activeOperations.Values)
            {
                if (currentOperation == null || operation.StartTime > currentOperation.StartTime)
                {
                    currentOperation = operation;
                }
            }
            
            if (currentOperation != null)
            {
                currentOverlay.UpdateDisplay(currentOperation);
            }
        }
        
        /// <summary>
        /// Create loading overlay from prefab.
        /// </summary>
        private void CreateLoadingOverlay()
        {
            GameObject overlayObject = Instantiate(loadingPrefab, loadingContainer != null ? loadingContainer : transform);
            currentOverlay = overlayObject.GetComponent<LoadingOverlay>();
            
            if (currentOverlay == null)
            {
                currentOverlay = overlayObject.AddComponent<LoadingOverlay>();
            }
            
            currentOverlay.Initialize();
        }
        
        /// <summary>
        /// Create a default loading overlay.
        /// </summary>
        private void CreateDefaultLoadingOverlay()
        {
            // Create overlay GameObject
            GameObject overlayObject = new GameObject("LoadingOverlay");
            overlayObject.transform.SetParent(loadingContainer != null ? loadingContainer : transform);
            
            // Add Canvas component
            Canvas canvas = overlayObject.AddComponent<Canvas>();
            canvas.sortingOrder = 300; // Overlay layer
            
            // Add CanvasGroup for fading
            CanvasGroup canvasGroup = overlayObject.AddComponent<CanvasGroup>();
            
            // Add background image
            Image backgroundImage = overlayObject.AddComponent<Image>();
            backgroundImage.color = overlayColor;
            
            // Set to full screen
            RectTransform rectTransform = overlayObject.GetComponent<RectTransform>();
            rectTransform.anchorMin = Vector2.zero;
            rectTransform.anchorMax = Vector2.one;
            rectTransform.offsetMin = Vector2.zero;
            rectTransform.offsetMax = Vector2.zero;
            
            // Add LoadingOverlay component
            currentOverlay = overlayObject.AddComponent<LoadingOverlay>();
            currentOverlay.Initialize();
        }
        
        #endregion
        
        #region Utility
        
        /// <summary>
        /// Generate a unique operation ID.
        /// </summary>
        private string GenerateOperationId()
        {
            return $"loading_operation_{++operationCounter}_{Time.time}";
        }
        
        /// <summary>
        /// Get all active loading operations.
        /// </summary>
        public List<LoadingOperation> GetActiveOperations()
        {
            return new List<LoadingOperation>(activeOperations.Values);
        }
        
        #endregion
    }
    
    /// <summary>
    /// Configuration for loading operations.
    /// </summary>
    [System.Serializable]
    public class LoadingConfig
    {
        public string message = "Loading...";
        public bool showProgress = false;
        public bool allowCancel = false;
        public Sprite customIcon = null;
        public Color backgroundColor = new Color(0, 0, 0, 0.7f);
        public Action onCancelled = null;
    }
    
    /// <summary>
    /// Represents a loading operation.
    /// </summary>
    public class LoadingOperation
    {
        public string Id { get; private set; }
        public LoadingConfig Config { get; private set; }
        public float Progress { get; private set; }
        public string CurrentMessage { get; private set; }
        public bool IsCompleted { get; private set; }
        public bool IsCancelled { get; private set; }
        public float StartTime { get; private set; }
        
        public LoadingOperation(string id, LoadingConfig config)
        {
            Id = id;
            Config = config;
            CurrentMessage = config.message;
            Progress = 0f;
            StartTime = Time.time;
        }
        
        public void UpdateProgress(float progress, string message = null)
        {
            Progress = Mathf.Clamp01(progress);
            if (!string.IsNullOrEmpty(message))
            {
                CurrentMessage = message;
            }
        }
        
        public void Complete()
        {
            Progress = 1f;
            IsCompleted = true;
        }
        
        public void Cancel()
        {
            IsCancelled = true;
            Config.onCancelled?.Invoke();
        }
    }
    
    /// <summary>
    /// Loading overlay UI component.
    /// </summary>
    public class LoadingOverlay : BaseUIPanel
    {
        [Header("Loading Components")]
        [SerializeField] private TextMeshProUGUI messageText;
        [SerializeField] private Slider progressSlider;
        [SerializeField] private TextMeshProUGUI progressText;
        [SerializeField] private Image loadingIcon;
        [SerializeField] private Button cancelButton;
        [SerializeField] private GameObject progressContainer;
        
        // Animation
        private Coroutine spinCoroutine;
        
        public float StartTime { get; private set; }
        
        protected override void Awake()
        {
            base.Awake();
            StartTime = Time.time;
        }
        
        /// <summary>
        /// Initialize the loading overlay.
        /// </summary>
        public void Initialize()
        {
            // Create default UI if components not assigned
            if (messageText == null)
            {
                CreateDefaultUI();
            }
            
            // Start loading icon animation
            if (loadingIcon != null)
            {
                StartLoadingAnimation();
            }
        }
        
        /// <summary>
        /// Update the display with loading operation info.
        /// </summary>
        public void UpdateDisplay(LoadingOperation operation)
        {
            if (operation == null) return;
            
            // Update message
            if (messageText != null)
            {
                messageText.text = operation.CurrentMessage;
            }
            
            // Update progress
            if (operation.Config.showProgress)
            {
                if (progressContainer != null)
                {
                    progressContainer.SetActive(true);
                }
                
                if (progressSlider != null)
                {
                    progressSlider.value = operation.Progress;
                }
                
                if (progressText != null)
                {
                    progressText.text = $"{Mathf.RoundToInt(operation.Progress * 100)}%";
                }
            }
            else
            {
                if (progressContainer != null)
                {
                    progressContainer.SetActive(false);
                }
            }
            
            // Update cancel button
            if (cancelButton != null)
            {
                cancelButton.gameObject.SetActive(operation.Config.allowCancel);
                cancelButton.onClick.RemoveAllListeners();
                cancelButton.onClick.AddListener(() => LoadingSystem.Instance.CancelLoading(operation.Id));
            }
            
            // Update icon
            if (loadingIcon != null && operation.Config.customIcon != null)
            {
                loadingIcon.sprite = operation.Config.customIcon;
            }
        }
        
        /// <summary>
        /// Create default UI elements.
        /// </summary>
        private void CreateDefaultUI()
        {
            // Create content container
            GameObject contentContainer = new GameObject("LoadingContent");
            contentContainer.transform.SetParent(transform);
            
            RectTransform contentRect = contentContainer.AddComponent<RectTransform>();
            contentRect.anchorMin = new Vector2(0.5f, 0.5f);
            contentRect.anchorMax = new Vector2(0.5f, 0.5f);
            contentRect.anchoredPosition = Vector2.zero;
            contentRect.sizeDelta = new Vector2(300, 150);
            
            // Create message text
            GameObject messageObject = new GameObject("MessageText");
            messageObject.transform.SetParent(contentContainer.transform);
            
            messageText = messageObject.AddComponent<TextMeshProUGUI>();
            messageText.text = "Loading...";
            messageText.fontSize = 18;
            messageText.color = Color.white;
            messageText.alignment = TextAlignmentOptions.Center;
            
            RectTransform messageRect = messageObject.GetComponent<RectTransform>();
            messageRect.anchorMin = Vector2.zero;
            messageRect.anchorMax = Vector2.one;
            messageRect.offsetMin = Vector2.zero;
            messageRect.offsetMax = Vector2.zero;
        }
        
        /// <summary>
        /// Start loading icon animation.
        /// </summary>
        private void StartLoadingAnimation()
        {
            if (spinCoroutine != null)
            {
                StopCoroutine(spinCoroutine);
            }
            
            spinCoroutine = StartCoroutine(SpinLoadingIcon());
        }
        
        /// <summary>
        /// Spin the loading icon.
        /// </summary>
        private IEnumerator SpinLoadingIcon()
        {
            while (loadingIcon != null && gameObject.activeInHierarchy)
            {
                loadingIcon.transform.Rotate(0, 0, -90 * Time.deltaTime);
                yield return null;
            }
        }
        
        protected override void OnDestroy()
        {
            base.OnDestroy();
            
            if (spinCoroutine != null)
            {
                StopCoroutine(spinCoroutine);
            }
        }
    }
} 