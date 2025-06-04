using System;
using UnityEngine;
using UnityEngine.UI;
using TMPro;

namespace VDM.UI.Systems.Combat
{
    /// <summary>
    /// UI component for displaying individual combat log entries
    /// </summary>
    public class CombatLogEntry : MonoBehaviour
    {
        [Header("Log Entry Components")]
        [SerializeField] private TextMeshProUGUI timestampText;
        [SerializeField] private TextMeshProUGUI messageText;
        [SerializeField] private Image backgroundImage;
        [SerializeField] private Image iconImage;
        [SerializeField] private Button expandButton;
        
        [Header("Visual Settings")]
        [SerializeField] private Color defaultBackgroundColor = new Color(0.1f, 0.1f, 0.1f, 0.8f);
        [SerializeField] private Color damageColor = new Color(1f, 0.3f, 0.3f, 1f);
        [SerializeField] private Color healingColor = new Color(0.3f, 1f, 0.3f, 1f);
        [SerializeField] private Color combatActionColor = new Color(1f, 1f, 0.3f, 1f);
        [SerializeField] private Color systemMessageColor = new Color(0.7f, 0.7f, 1f, 1f);
        [SerializeField] private Color criticalColor = new Color(1f, 0.5f, 0f, 1f);
        
        [Header("Animation")]
        [SerializeField] private float fadeInDuration = 0.3f;
        [SerializeField] private float expandDuration = 0.2f;
        [SerializeField] private LeanTweenType fadeEase = LeanTweenType.easeOutQuad;
        
        // Data
        private CombatLogData logData;
        private bool isExpanded = false;
        private string fullMessage;
        private string shortMessage;
        private CanvasGroup canvasGroup;
        
        private void Awake()
        {
            // Get or add canvas group for fade animations
            canvasGroup = GetComponent<CanvasGroup>();
            if (canvasGroup == null)
                canvasGroup = gameObject.AddComponent<CanvasGroup>();
            
            // Setup expand button
            if (expandButton != null)
                expandButton.onClick.AddListener(ToggleExpanded);
            
            // Start invisible for fade-in effect
            canvasGroup.alpha = 0f;
        }
        
        /// <summary>
        /// Initialize the combat log entry
        /// </summary>
        public void Initialize(CombatLogData data)
        {
            logData = data;
            
            SetupContent();
            SetupVisuals();
            AnimateIn();
        }
        
        /// <summary>
        /// Toggle expanded view of the log entry
        /// </summary>
        public void ToggleExpanded()
        {
            isExpanded = !isExpanded;
            UpdateMessageDisplay();
            AnimateExpansion();
        }
        
        private void SetupContent()
        {
            if (logData == null) return;
            
            // Set timestamp
            if (timestampText != null)
            {
                string timeFormat = DateTime.Now.ToString("HH:mm:ss");
                timestampText.text = timeFormat;
            }
            
            // Prepare message content
            PrepareMessages();
            
            // Set initial message display
            UpdateMessageDisplay();
            
            // Set icon based on log type
            if (iconImage != null)
            {
                Sprite icon = GetLogTypeIcon(logData.Type);
                if (icon != null)
                    iconImage.sprite = icon;
            }
        }
        
        private void SetupVisuals()
        {
            if (logData == null) return;
            
            // Set background color based on log type
            if (backgroundImage != null)
                backgroundImage.color = GetLogTypeColor(logData.Type);
            
            // Set text color
            if (messageText != null)
                messageText.color = GetTextColor(logData.Type);
        }
        
        private void PrepareMessages()
        {
            if (logData == null) return;
            
            fullMessage = logData.Message;
            
            // Create shortened version if message is too long
            const int maxShortLength = 80;
            if (fullMessage.Length > maxShortLength)
            {
                shortMessage = fullMessage.Substring(0, maxShortLength) + "...";
                
                // Show expand button if there's more content
                if (expandButton != null)
                    expandButton.gameObject.SetActive(true);
            }
            else
            {
                shortMessage = fullMessage;
                
                // Hide expand button if not needed
                if (expandButton != null)
                    expandButton.gameObject.SetActive(false);
            }
        }
        
        private void UpdateMessageDisplay()
        {
            if (messageText == null) return;
            
            string displayMessage = isExpanded ? fullMessage : shortMessage;
            
            // Add additional details if expanded
            if (isExpanded && logData.Details != null && logData.Details.Count > 0)
            {
                displayMessage += "\n";
                foreach (string detail in logData.Details)
                {
                    displayMessage += $"• {detail}\n";
                }
            }
            
            messageText.text = displayMessage;
            
            // Update expand button text
            if (expandButton != null)
            {
                var buttonText = expandButton.GetComponentInChildren<TextMeshProUGUI>();
                if (buttonText != null)
                    buttonText.text = isExpanded ? "▲" : "▼";
            }
        }
        
        private void AnimateIn()
        {
            // Fade in animation
            LeanTween.alphaCanvas(canvasGroup, 1f, fadeInDuration)
                .setEase(fadeEase);
            
            // Slide in from right
            RectTransform rectTransform = GetComponent<RectTransform>();
            if (rectTransform != null)
            {
                Vector3 startPos = rectTransform.anchoredPosition;
                startPos.x += 200f;
                rectTransform.anchoredPosition = startPos;
                
                LeanTween.moveX(rectTransform, startPos.x - 200f, fadeInDuration)
                    .setEase(fadeEase);
            }
        }
        
        private void AnimateExpansion()
        {
            // Animate layout rebuild for expansion
            LayoutRebuilder.ForceRebuildLayoutImmediate(GetComponent<RectTransform>());
        }
        
        private Color GetLogTypeColor(CombatLogType type)
        {
            return type switch
            {
                CombatLogType.Damage => damageColor,
                CombatLogType.Healing => healingColor,
                CombatLogType.CombatAction => combatActionColor,
                CombatLogType.SystemMessage => systemMessageColor,
                CombatLogType.Critical => criticalColor,
                _ => defaultBackgroundColor
            };
        }
        
        private Color GetTextColor(CombatLogType type)
        {
            // Most log types use white text for readability
            return type switch
            {
                CombatLogType.Critical => Color.white,
                _ => Color.white
            };
        }
        
        private Sprite GetLogTypeIcon(CombatLogType type)
        {
            string iconPath = type switch
            {
                CombatLogType.Damage => "Icons/Combat/Damage",
                CombatLogType.Healing => "Icons/Combat/Healing",
                CombatLogType.CombatAction => "Icons/Combat/Action",
                CombatLogType.SystemMessage => "Icons/Combat/System",
                CombatLogType.Critical => "Icons/Combat/Critical",
                _ => "Icons/Combat/General"
            };
            
            return Resources.Load<Sprite>(iconPath);
        }
        
        /// <summary>
        /// Add highlight effect for important messages
        /// </summary>
        public void Highlight()
        {
            if (backgroundImage != null)
            {
                Color originalColor = backgroundImage.color;
                Color highlightColor = new Color(originalColor.r * 1.3f, originalColor.g * 1.3f, originalColor.b * 1.3f, originalColor.a);
                
                LeanTween.color(backgroundImage.rectTransform, highlightColor, 0.2f)
                    .setEase(LeanTweenType.easeOutQuad)
                    .setLoopPingPong(2)
                    .setOnComplete(() => backgroundImage.color = originalColor);
            }
        }
        
        /// <summary>
        /// Fade out animation for entry removal
        /// </summary>
        public void FadeOut(System.Action onComplete = null)
        {
            LeanTween.alphaCanvas(canvasGroup, 0f, fadeInDuration)
                .setEase(fadeEase)
                .setOnComplete(() =>
                {
                    onComplete?.Invoke();
                    Destroy(gameObject);
                });
        }
        
        private void OnDestroy()
        {
            // Cancel any running animations
            LeanTween.cancel(gameObject);
        }
        
        #region Public Properties
        
        public CombatLogData LogData => logData;
        public bool IsExpanded => isExpanded;
        
        #endregion
    }
    
    /// <summary>
    /// Data structure for combat log entries
    /// </summary>
    [System.Serializable]
    public class CombatLogData
    {
        public CombatLogType Type;
        public string Message;
        public System.Collections.Generic.List<string> Details;
        public DateTime Timestamp;
        public string ActorName;
        public string TargetName;
        public int? DamageAmount;
        public int? HealingAmount;
        
        public CombatLogData(CombatLogType type, string message)
        {
            Type = type;
            Message = message;
            Timestamp = DateTime.Now;
            Details = new System.Collections.Generic.List<string>();
        }
    }
    
    /// <summary>
    /// Types of combat log entries
    /// </summary>
    public enum CombatLogType
    {
        CombatAction,
        Damage,
        Healing,
        SystemMessage,
        Critical,
        StatusEffect,
        TurnStart,
        TurnEnd
    }
} 