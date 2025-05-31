using System;
using TMPro;
using UnityEngine.UI;
using UnityEngine;
using VDM.Systems.Quest.Models;


namespace VDM.Systems.Quest.Ui
{
    /// <summary>
    /// UI component for displaying individual quest items in quest lists
    /// </summary>
    public class QuestItemUI : MonoBehaviour
    {
        [Header("UI References")]
        [SerializeField] private TextMeshProUGUI questTitleText;
        [SerializeField] private TextMeshProUGUI questDescriptionText;
        [SerializeField] private TextMeshProUGUI questStatusText;
        [SerializeField] private TextMeshProUGUI questTypeText;
        [SerializeField] private TextMeshProUGUI questPriorityText;
        [SerializeField] private Slider progressSlider;
        [SerializeField] private TextMeshProUGUI progressText;
        [SerializeField] private Button selectButton;
        [SerializeField] private Image statusIcon;
        [SerializeField] private Image priorityIcon;
        [SerializeField] private Image backgroundImage;
        
        [Header("Visual Settings")]
        [SerializeField] private Color availableColor = Color.green;
        [SerializeField] private Color activeColor = Color.yellow;
        [SerializeField] private Color completedColor = Color.blue;
        [SerializeField] private Color failedColor = Color.red;
        [SerializeField] private Color selectedColor = Color.cyan;
        
        private QuestDTO quest;
        private bool isSelected = false;
        
        // Events
        public event Action<QuestDTO> OnQuestClicked;
        
        private void Awake()
        {
            if (selectButton != null)
            {
                selectButton.onClick.AddListener(OnQuestSelected);
            }
        }
        
        /// <summary>
        /// Set the quest data for this UI item
        /// </summary>
        /// <param name="questData">Quest DTO to display</param>
        public void SetQuest(QuestDTO questData)
        {
            quest = questData;
            UpdateDisplay();
        }
        
        /// <summary>
        /// Update the visual display with current quest data
        /// </summary>
        private void UpdateDisplay()
        {
            if (quest == null) return;
            
            // Update text fields
            if (questTitleText != null)
            {
                questTitleText.text = quest.Title ?? "Unknown Quest";
            }
            
            if (questDescriptionText != null)
            {
                questDescriptionText.text = TruncateDescription(quest.Description ?? "", 100);
            }
            
            if (questStatusText != null)
            {
                questStatusText.text = quest.Status?.ToUpper() ?? "UNKNOWN";
            }
            
            if (questTypeText != null)
            {
                questTypeText.text = quest.Type ?? "General";
            }
            
            if (questPriorityText != null)
            {
                questPriorityText.text = quest.Priority ?? "Medium";
            }
            
            // Update progress
            UpdateProgress();
            
            // Update visual styling
            UpdateVisualStyling();
        }
        
        /// <summary>
        /// Update quest progress display
        /// </summary>
        private void UpdateProgress()
        {
            if (quest?.Steps == null) return;
            
            int completedSteps = 0;
            int totalSteps = quest.Steps.Count;
            
            foreach (var step in quest.Steps)
            {
                if (step.Completed)
                {
                    completedSteps++;
                }
            }
            
            float progress = totalSteps > 0 ? (float)completedSteps / totalSteps : 0f;
            
            if (progressSlider != null)
            {
                progressSlider.value = progress;
            }
            
            if (progressText != null)
            {
                progressText.text = $"{completedSteps}/{totalSteps}";
            }
        }
        
        /// <summary>
        /// Update visual styling based on quest status and selection
        /// </summary>
        private void UpdateVisualStyling()
        {
            Color statusColor = GetStatusColor();
            
            // Update status icon color
            if (statusIcon != null)
            {
                statusIcon.color = statusColor;
            }
            
            // Update priority icon
            if (priorityIcon != null)
            {
                priorityIcon.color = GetPriorityColor();
            }
            
            // Update background color
            if (backgroundImage != null)
            {
                Color bgColor = isSelected ? selectedColor : statusColor;
                bgColor.a = isSelected ? 0.8f : 0.3f;
                backgroundImage.color = bgColor;
            }
            
            // Update text colors
            UpdateTextColors(statusColor);
        }
        
        /// <summary>
        /// Get color based on quest status
        /// </summary>
        /// <returns>Status color</returns>
        private Color GetStatusColor()
        {
            return quest?.Status?.ToLower() switch
            {
                "available" => availableColor,
                "active" => activeColor,
                "in-progress" => activeColor,
                "completed" => completedColor,
                "done" => completedColor,
                "failed" => failedColor,
                "abandoned" => failedColor,
                _ => Color.gray
            };
        }
        
        /// <summary>
        /// Get color based on quest priority
        /// </summary>
        /// <returns>Priority color</returns>
        private Color GetPriorityColor()
        {
            return quest?.Priority?.ToLower() switch
            {
                "urgent" => Color.red,
                "high" => Color.yellow,
                "medium" => Color.white,
                "low" => Color.gray,
                _ => Color.white
            };
        }
        
        /// <summary>
        /// Update text colors for better readability
        /// </summary>
        /// <param name="baseColor">Base color to derive text colors from</param>
        private void UpdateTextColors(Color baseColor)
        {
            Color textColor = IsColorDark(baseColor) ? Color.white : Color.black;
            
            if (questTitleText != null)
            {
                questTitleText.color = textColor;
            }
            
            if (questStatusText != null)
            {
                questStatusText.color = baseColor;
            }
            
            if (questPriorityText != null)
            {
                questPriorityText.color = GetPriorityColor();
            }
        }
        
        /// <summary>
        /// Determine if a color is dark
        /// </summary>
        /// <param name="color">Color to check</param>
        /// <returns>True if color is dark</returns>
        private bool IsColorDark(Color color)
        {
            float brightness = (color.r * 0.299f + color.g * 0.587f + color.b * 0.114f);
            return brightness < 0.5f;
        }
        
        /// <summary>
        /// Truncate description text to specified length
        /// </summary>
        /// <param name="text">Text to truncate</param>
        /// <param name="maxLength">Maximum length</param>
        /// <returns>Truncated text</returns>
        private string TruncateDescription(string text, int maxLength)
        {
            if (string.IsNullOrEmpty(text) || text.Length <= maxLength)
                return text;
            
            return text.Substring(0, maxLength - 3) + "...";
        }
        
        /// <summary>
        /// Set selection state
        /// </summary>
        /// <param name="selected">Whether this item is selected</param>
        public void SetSelected(bool selected)
        {
            isSelected = selected;
            UpdateVisualStyling();
        }
        
        /// <summary>
        /// Handle quest item selection
        /// </summary>
        private void OnQuestSelected()
        {
            if (quest != null)
            {
                OnQuestClicked?.Invoke(quest);
            }
        }
        
        /// <summary>
        /// Get the associated quest
        /// </summary>
        /// <returns>Quest DTO</returns>
        public QuestDTO GetQuest()
        {
            return quest;
        }
        
        /// <summary>
        /// Check if this item represents the specified quest
        /// </summary>
        /// <param name="questId">Quest ID to check</param>
        /// <returns>True if this item represents the quest</returns>
        public bool IsQuest(string questId)
        {
            return quest?.Id == questId;
        }
        
        /// <summary>
        /// Refresh the display with updated quest data
        /// </summary>
        public void RefreshDisplay()
        {
            UpdateDisplay();
        }
    }
} 