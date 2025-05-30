using System;
using TMPro;
using UnityEngine.UI;
using UnityEngine;
using VDM.Runtime.Arc.Models;


namespace VDM.Runtime.Arc.UI
{
    /// <summary>
    /// UI component for displaying individual arc items in arc lists
    /// </summary>
    public class ArcItemUI : MonoBehaviour
    {
        [Header("UI References")]
        [SerializeField] private TextMeshProUGUI arcTitleText;
        [SerializeField] private TextMeshProUGUI arcDescriptionText;
        [SerializeField] private TextMeshProUGUI arcTypeText;
        [SerializeField] private TextMeshProUGUI arcStatusText;
        [SerializeField] private TextMeshProUGUI arcPriorityText;
        [SerializeField] private Slider progressSlider;
        [SerializeField] private TextMeshProUGUI progressText;
        [SerializeField] private Button selectButton;
        [SerializeField] private Image statusIcon;
        [SerializeField] private Image typeIcon;
        [SerializeField] private Image backgroundImage;
        [SerializeField] private Image difficultyIndicator;
        
        [Header("Visual Settings")]
        [SerializeField] private Color pendingColor = Color.gray;
        [SerializeField] private Color activeColor = Color.green;
        [SerializeField] private Color stalledColor = Color.yellow;
        [SerializeField] private Color failedColor = Color.red;
        [SerializeField] private Color completedColor = Color.blue;
        [SerializeField] private Color selectedColor = Color.cyan;
        
        [Header("Type Colors")]
        [SerializeField] private Color globalArcColor = Color.magenta;
        [SerializeField] private Color regionalArcColor = Color.green;
        [SerializeField] private Color characterArcColor = Color.blue;
        [SerializeField] private Color npcArcColor = Color.yellow;
        
        private ArcDTO arc;
        private bool isSelected = false;
        
        // Events
        public event Action<ArcDTO> OnArcClicked;
        
        private void Awake()
        {
            if (selectButton != null)
            {
                selectButton.onClick.AddListener(OnArcSelected);
            }
        }
        
        /// <summary>
        /// Set the arc data for this UI item
        /// </summary>
        /// <param name="arcData">Arc DTO to display</param>
        public void SetArc(ArcDTO arcData)
        {
            arc = arcData;
            UpdateDisplay();
        }
        
        /// <summary>
        /// Update the visual display with current arc data
        /// </summary>
        private void UpdateDisplay()
        {
            if (arc == null) return;
            
            // Update text fields
            if (arcTitleText != null)
            {
                arcTitleText.text = arc.Title ?? "Unknown Arc";
            }
            
            if (arcDescriptionText != null)
            {
                arcDescriptionText.text = TruncateDescription(arc.Description ?? "", 120);
            }
            
            if (arcTypeText != null)
            {
                arcTypeText.text = FormatArcType(arc.Type);
            }
            
            if (arcStatusText != null)
            {
                arcStatusText.text = FormatArcStatus(arc.Status);
            }
            
            if (arcPriorityText != null)
            {
                arcPriorityText.text = FormatArcPriority(arc.Priority);
            }
            
            // Update progress
            UpdateProgress();
            
            // Update difficulty indicator
            UpdateDifficultyIndicator();
            
            // Update visual styling
            UpdateVisualStyling();
        }
        
        /// <summary>
        /// Update arc progress display
        /// </summary>
        private void UpdateProgress()
        {
            if (arc?.Steps == null) return;
            
            int completedSteps = 0;
            int totalSteps = arc.Steps.Count;
            
            foreach (var step in arc.Steps)
            {
                if (step.IsCompleted)
                {
                    completedSteps++;
                }
            }
            
            float progress = totalSteps > 0 ? (float)completedSteps / totalSteps : 0f;
            
            // Update progress slider
            if (progressSlider != null)
            {
                progressSlider.value = progress;
            }
            
            // Update progress text
            if (progressText != null)
            {
                progressText.text = $"{completedSteps}/{totalSteps} Steps";
            }
        }
        
        /// <summary>
        /// Update difficulty indicator
        /// </summary>
        private void UpdateDifficultyIndicator()
        {
            if (difficultyIndicator != null && arc != null)
            {
                // Set difficulty color based on difficulty level
                Color diffColor = arc.Difficulty switch
                {
                    1 => Color.green,
                    2 => Color.yellow,
                    3 => Color.yellow,
                    4 => Color.red,
                    5 => Color.red,
                    _ => Color.gray
                };
                
                difficultyIndicator.color = diffColor;
                
                // Set fill amount based on difficulty (1-5 scale)
                difficultyIndicator.fillAmount = arc.Difficulty / 5f;
            }
        }
        
        /// <summary>
        /// Update visual styling based on arc status and selection
        /// </summary>
        private void UpdateVisualStyling()
        {
            Color statusColor = GetStatusColor();
            Color typeColor = GetTypeColor();
            
            // Update status icon color
            if (statusIcon != null)
            {
                statusIcon.color = statusColor;
            }
            
            // Update type icon color
            if (typeIcon != null)
            {
                typeIcon.color = typeColor;
            }
            
            // Update background color
            if (backgroundImage != null)
            {
                Color bgColor = isSelected ? selectedColor : statusColor;
                bgColor.a = isSelected ? 0.8f : 0.3f;
                backgroundImage.color = bgColor;
            }
            
            // Update text colors
            UpdateTextColors(statusColor, typeColor);
        }
        
        /// <summary>
        /// Get color based on arc status
        /// </summary>
        /// <returns>Status color</returns>
        private Color GetStatusColor()
        {
            return arc?.Status switch
            {
                ArcStatus.Pending => pendingColor,
                ArcStatus.Active => activeColor,
                ArcStatus.Stalled => stalledColor,
                ArcStatus.Failed => failedColor,
                ArcStatus.Completed => completedColor,
                ArcStatus.Abandoned => failedColor,
                _ => Color.gray
            };
        }
        
        /// <summary>
        /// Get color based on arc type
        /// </summary>
        /// <returns>Type color</returns>
        private Color GetTypeColor()
        {
            return arc?.Type switch
            {
                ArcType.Global => globalArcColor,
                ArcType.Regional => regionalArcColor,
                ArcType.Character => characterArcColor,
                ArcType.NPC => npcArcColor,
                _ => Color.white
            };
        }
        
        /// <summary>
        /// Update text colors for better readability
        /// </summary>
        /// <param name="statusColor">Status color</param>
        /// <param name="typeColor">Type color</param>
        private void UpdateTextColors(Color statusColor, Color typeColor)
        {
            Color textColor = IsColorDark(statusColor) ? Color.white : Color.black;
            
            if (arcTitleText != null)
            {
                arcTitleText.color = textColor;
            }
            
            if (arcStatusText != null)
            {
                arcStatusText.color = statusColor;
            }
            
            if (arcTypeText != null)
            {
                arcTypeText.color = typeColor;
            }
            
            if (arcPriorityText != null)
            {
                arcPriorityText.color = GetPriorityColor();
            }
        }
        
        /// <summary>
        /// Get color based on arc priority
        /// </summary>
        /// <returns>Priority color</returns>
        private Color GetPriorityColor()
        {
            return arc?.Priority switch
            {
                ArcPriority.Critical => Color.red,
                ArcPriority.High => Color.yellow,
                ArcPriority.Medium => Color.white,
                ArcPriority.Low => Color.gray,
                _ => Color.white
            };
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
        /// Format arc type for display
        /// </summary>
        /// <param name="arcType">Arc type enum</param>
        /// <returns>Formatted type string</returns>
        private string FormatArcType(ArcType arcType)
        {
            return arcType.ToString().ToUpper();
        }
        
        /// <summary>
        /// Format arc status for display
        /// </summary>
        /// <param name="arcStatus">Arc status enum</param>
        /// <returns>Formatted status string</returns>
        private string FormatArcStatus(ArcStatus arcStatus)
        {
            return arcStatus.ToString().ToUpper();
        }
        
        /// <summary>
        /// Format arc priority for display
        /// </summary>
        /// <param name="arcPriority">Arc priority enum</param>
        /// <returns>Formatted priority string</returns>
        private string FormatArcPriority(ArcPriority arcPriority)
        {
            return arcPriority.ToString().ToUpper();
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
        /// Handle arc item selection
        /// </summary>
        private void OnArcSelected()
        {
            if (arc != null)
            {
                OnArcClicked?.Invoke(arc);
            }
        }
        
        /// <summary>
        /// Get the associated arc
        /// </summary>
        /// <returns>Arc DTO</returns>
        public ArcDTO GetArc()
        {
            return arc;
        }
        
        /// <summary>
        /// Check if this item represents the specified arc
        /// </summary>
        /// <param name="arcId">Arc ID to check</param>
        /// <returns>True if this item represents the arc</returns>
        public bool IsArc(string arcId)
        {
            return arc?.Id == arcId;
        }
        
        /// <summary>
        /// Refresh the display with updated arc data
        /// </summary>
        public void RefreshDisplay()
        {
            UpdateDisplay();
        }
        
        /// <summary>
        /// Get estimated time remaining for arc completion
        /// </summary>
        /// <returns>Time remaining display string</returns>
        public string GetTimeRemainingDisplay()
        {
            if (arc?.EstimatedDurationDays == null) return "Unknown";
            
            if (arc.StartedAt.HasValue)
            {
                var elapsed = DateTime.UtcNow - arc.StartedAt.Value;
                var remaining = TimeSpan.FromDays(arc.EstimatedDurationDays.Value) - elapsed;
                
                if (remaining.TotalDays > 1)
                {
                    return $"{remaining.Days}d {remaining.Hours}h remaining";
                }
                else if (remaining.TotalHours > 0)
                {
                    return $"{remaining.Hours}h {remaining.Minutes}m remaining";
                }
                else
                {
                    return "Overdue";
                }
            }
            
            return $"~{arc.EstimatedDurationDays}d estimated";
        }
    }
} 