using UnityEngine;
using UnityEngine.UI;
using System;
using System.Collections;
using System.Collections.Generic;
using TMPro;

namespace VDM.UI.Core
{
    /// <summary>
    /// Notification system for Visual DM.
    /// Handles toast messages, alerts, and temporary notifications.
    /// </summary>
    public class NotificationSystem : MonoBehaviour
    {
        [Header("Notification Configuration")]
        [SerializeField] private GameObject notificationPrefab;
        [SerializeField] private Transform notificationContainer;
        [SerializeField] private int maxNotifications = 5;
        [SerializeField] private float defaultDuration = 3f;
        [SerializeField] private float stackSpacing = 10f;
        
        [Header("Animation Settings")]
        [SerializeField] private float slideInDuration = 0.3f;
        [SerializeField] private float slideOutDuration = 0.2f;
        [SerializeField] private AnimationCurve slideCurve = AnimationCurve.EaseInOut(0, 0, 1, 1);
        
        [Header("Notification Types")]
        [SerializeField] private NotificationTypeConfig[] notificationTypes;
        
        // Singleton
        public static NotificationSystem Instance { get; private set; }
        
        // Events
        public event Action<Notification> OnNotificationShown;
        public event Action<Notification> OnNotificationDismissed;
        
        // State
        private List<Notification> activeNotifications = new List<Notification>();
        private Queue<NotificationData> notificationQueue = new Queue<NotificationData>();
        private bool isProcessingQueue = false;
        
        public int ActiveNotificationCount => activeNotifications.Count;
        public bool HasActiveNotifications => activeNotifications.Count > 0;
        
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
            
            // Initialize notification types if not set
            if (notificationTypes == null || notificationTypes.Length == 0)
            {
                InitializeDefaultNotificationTypes();
            }
        }
        
        private void OnDestroy()
        {
            if (Instance == this)
            {
                Instance = null;
            }
        }
        
        /// <summary>
        /// Initialize default notification type configurations.
        /// </summary>
        private void InitializeDefaultNotificationTypes()
        {
            notificationTypes = new NotificationTypeConfig[]
            {
                new NotificationTypeConfig
                {
                    type = NotificationType.Info,
                    backgroundColor = new Color(0.2f, 0.6f, 1f, 0.9f),
                    textColor = Color.white,
                    iconSprite = null,
                    defaultDuration = 3f
                },
                new NotificationTypeConfig
                {
                    type = NotificationType.Success,
                    backgroundColor = new Color(0.2f, 0.8f, 0.2f, 0.9f),
                    textColor = Color.white,
                    iconSprite = null,
                    defaultDuration = 2f
                },
                new NotificationTypeConfig
                {
                    type = NotificationType.Warning,
                    backgroundColor = new Color(1f, 0.8f, 0.2f, 0.9f),
                    textColor = Color.black,
                    iconSprite = null,
                    defaultDuration = 4f
                },
                new NotificationTypeConfig
                {
                    type = NotificationType.Error,
                    backgroundColor = new Color(0.9f, 0.2f, 0.2f, 0.9f),
                    textColor = Color.white,
                    iconSprite = null,
                    defaultDuration = 5f
                }
            };
        }
        
        #region Public API
        
        /// <summary>
        /// Show an info notification.
        /// </summary>
        public Notification ShowInfo(string message, float duration = -1f)
        {
            return ShowNotification(message, NotificationType.Info, duration);
        }
        
        /// <summary>
        /// Show a success notification.
        /// </summary>
        public Notification ShowSuccess(string message, float duration = -1f)
        {
            return ShowNotification(message, NotificationType.Success, duration);
        }
        
        /// <summary>
        /// Show a warning notification.
        /// </summary>
        public Notification ShowWarning(string message, float duration = -1f)
        {
            return ShowNotification(message, NotificationType.Warning, duration);
        }
        
        /// <summary>
        /// Show an error notification.
        /// </summary>
        public Notification ShowError(string message, float duration = -1f)
        {
            return ShowNotification(message, NotificationType.Error, duration);
        }
        
        /// <summary>
        /// Show a notification with specified type.
        /// </summary>
        public Notification ShowNotification(string message, NotificationType type = NotificationType.Info, float duration = -1f)
        {
            var data = new NotificationData
            {
                message = message,
                type = type,
                duration = duration > 0 ? duration : GetDefaultDuration(type),
                timestamp = DateTime.Now
            };
            
            return ShowNotification(data);
        }
        
        /// <summary>
        /// Show a notification with full configuration.
        /// </summary>
        public Notification ShowNotification(NotificationData data)
        {
            // Add to queue if we're at max capacity
            if (activeNotifications.Count >= maxNotifications)
            {
                notificationQueue.Enqueue(data);
                ProcessNotificationQueue();
                return null;
            }
            
            return CreateAndShowNotification(data);
        }
        
        /// <summary>
        /// Dismiss a specific notification.
        /// </summary>
        public void DismissNotification(Notification notification)
        {
            if (notification == null || !activeNotifications.Contains(notification)) return;
            
            StartCoroutine(DismissNotificationCoroutine(notification));
        }
        
        /// <summary>
        /// Dismiss all active notifications.
        /// </summary>
        public void DismissAllNotifications()
        {
            var notificationsToDismiss = new List<Notification>(activeNotifications);
            foreach (var notification in notificationsToDismiss)
            {
                DismissNotification(notification);
            }
        }
        
        /// <summary>
        /// Clear the notification queue.
        /// </summary>
        public void ClearQueue()
        {
            notificationQueue.Clear();
        }
        
        #endregion
        
        #region Notification Management
        
        /// <summary>
        /// Create and show a notification.
        /// </summary>
        private Notification CreateAndShowNotification(NotificationData data)
        {
            if (notificationPrefab == null)
            {
                Debug.LogError("NotificationSystem: Notification prefab not assigned.");
                return null;
            }
            
            // Instantiate notification
            GameObject notificationObject = Instantiate(notificationPrefab, notificationContainer != null ? notificationContainer : transform);
            Notification notification = notificationObject.GetComponent<Notification>();
            
            if (notification == null)
            {
                notification = notificationObject.AddComponent<Notification>();
            }
            
            // Configure notification
            notification.Initialize(data, GetNotificationTypeConfig(data.type));
            notification.OnNotificationDismissed += HandleNotificationDismissed;
            
            // Add to active notifications
            activeNotifications.Add(notification);
            
            // Position notification
            PositionNotifications();
            
            // Set layer order
            if (UIManager.Instance != null)
            {
                UIManager.Instance.SetPanelLayer(notification, UIManager.UILayer.Overlay);
            }
            
            // Show notification
            notification.Show();
            
            // Auto-dismiss after duration
            if (data.duration > 0)
            {
                StartCoroutine(AutoDismissNotification(notification, data.duration));
            }
            
            OnNotificationShown?.Invoke(notification);
            return notification;
        }
        
        /// <summary>
        /// Handle notification dismissed event.
        /// </summary>
        private void HandleNotificationDismissed(Notification notification)
        {
            activeNotifications.Remove(notification);
            PositionNotifications();
            ProcessNotificationQueue();
            OnNotificationDismissed?.Invoke(notification);
        }
        
        /// <summary>
        /// Position all active notifications.
        /// </summary>
        private void PositionNotifications()
        {
            for (int i = 0; i < activeNotifications.Count; i++)
            {
                var notification = activeNotifications[i];
                if (notification != null)
                {
                    // Position from top to bottom
                    RectTransform rectTransform = notification.GetComponent<RectTransform>();
                    if (rectTransform != null)
                    {
                        float yOffset = -i * (rectTransform.rect.height + stackSpacing);
                        rectTransform.anchoredPosition = new Vector2(rectTransform.anchoredPosition.x, yOffset);
                    }
                }
            }
        }
        
        /// <summary>
        /// Process queued notifications.
        /// </summary>
        private void ProcessNotificationQueue()
        {
            if (isProcessingQueue || notificationQueue.Count == 0) return;
            if (activeNotifications.Count >= maxNotifications) return;
            
            isProcessingQueue = true;
            
            while (notificationQueue.Count > 0 && activeNotifications.Count < maxNotifications)
            {
                var data = notificationQueue.Dequeue();
                CreateAndShowNotification(data);
            }
            
            isProcessingQueue = false;
        }
        
        /// <summary>
        /// Auto-dismiss a notification after specified duration.
        /// </summary>
        private IEnumerator AutoDismissNotification(Notification notification, float duration)
        {
            yield return new WaitForSeconds(duration);
            
            if (notification != null && activeNotifications.Contains(notification))
            {
                DismissNotification(notification);
            }
        }
        
        /// <summary>
        /// Dismiss notification with animation.
        /// </summary>
        private IEnumerator DismissNotificationCoroutine(Notification notification)
        {
            if (notification == null) yield break;
            
            // Animate dismissal
            notification.Hide();
            
            // Wait for animation to complete
            yield return new WaitForSeconds(slideOutDuration);
            
            // Destroy notification
            if (notification != null)
            {
                Destroy(notification.gameObject);
            }
        }
        
        #endregion
        
        #region Utility
        
        /// <summary>
        /// Get notification type configuration.
        /// </summary>
        private NotificationTypeConfig GetNotificationTypeConfig(NotificationType type)
        {
            foreach (var config in notificationTypes)
            {
                if (config.type == type)
                {
                    return config;
                }
            }
            
            // Return default if not found
            return notificationTypes[0];
        }
        
        /// <summary>
        /// Get default duration for notification type.
        /// </summary>
        private float GetDefaultDuration(NotificationType type)
        {
            var config = GetNotificationTypeConfig(type);
            return config.defaultDuration > 0 ? config.defaultDuration : defaultDuration;
        }
        
        #endregion
    }
    
    /// <summary>
    /// Types of notifications.
    /// </summary>
    public enum NotificationType
    {
        Info,
        Success,
        Warning,
        Error
    }
    
    /// <summary>
    /// Configuration for notification types.
    /// </summary>
    [System.Serializable]
    public class NotificationTypeConfig
    {
        public NotificationType type;
        public Color backgroundColor = Color.white;
        public Color textColor = Color.black;
        public Sprite iconSprite;
        public float defaultDuration = 3f;
    }
    
    /// <summary>
    /// Data for a notification.
    /// </summary>
    [System.Serializable]
    public class NotificationData
    {
        public string message;
        public NotificationType type = NotificationType.Info;
        public float duration = 3f;
        public DateTime timestamp;
        public Sprite customIcon;
        public Action onClicked;
        public bool allowDismiss = true;
    }
    
    /// <summary>
    /// Individual notification component.
    /// </summary>
    public class Notification : BaseUIPanel
    {
        [Header("Notification Components")]
        [SerializeField] private TextMeshProUGUI messageText;
        [SerializeField] private Image backgroundImage;
        [SerializeField] private Image iconImage;
        [SerializeField] private Button dismissButton;
        [SerializeField] private Button notificationButton;
        
        // Events
        public event Action<Notification> OnNotificationDismissed;
        
        // Configuration
        private NotificationData data;
        private NotificationTypeConfig typeConfig;
        
        /// <summary>
        /// Initialize the notification.
        /// </summary>
        public void Initialize(NotificationData data, NotificationTypeConfig typeConfig)
        {
            this.data = data;
            this.typeConfig = typeConfig;
            SetupNotification();
        }
        
        /// <summary>
        /// Setup notification appearance and behavior.
        /// </summary>
        private void SetupNotification()
        {
            if (data == null || typeConfig == null) return;
            
            // Set message
            if (messageText != null)
            {
                messageText.text = data.message;
                messageText.color = typeConfig.textColor;
            }
            
            // Set background
            if (backgroundImage != null)
            {
                backgroundImage.color = typeConfig.backgroundColor;
            }
            
            // Set icon
            if (iconImage != null)
            {
                Sprite iconToUse = data.customIcon != null ? data.customIcon : typeConfig.iconSprite;
                iconImage.sprite = iconToUse;
                iconImage.gameObject.SetActive(iconToUse != null);
            }
            
            // Setup dismiss button
            if (dismissButton != null)
            {
                dismissButton.gameObject.SetActive(data.allowDismiss);
                dismissButton.onClick.RemoveAllListeners();
                dismissButton.onClick.AddListener(() => DismissNotification());
            }
            
            // Setup notification click
            if (notificationButton != null)
            {
                notificationButton.onClick.RemoveAllListeners();
                if (data.onClicked != null)
                {
                    notificationButton.onClick.AddListener(() => data.onClicked.Invoke());
                }
            }
        }
        
        /// <summary>
        /// Dismiss this notification.
        /// </summary>
        public void DismissNotification()
        {
            OnNotificationDismissed?.Invoke(this);
        }
        
        protected virtual void OnPanelClosed()
        {
            base.OnPanelClosed();
            OnNotificationDismissed?.Invoke(this);
        }
    }
} 