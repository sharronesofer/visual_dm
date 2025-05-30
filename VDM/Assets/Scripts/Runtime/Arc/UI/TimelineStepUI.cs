using System;
using TMPro;
using UnityEngine.UI;
using UnityEngine;
using VDM.Runtime.Arc.Models;


namespace VDM.Runtime.Arc.UI
{
    /// <summary>
    /// UI component for displaying individual arc steps in timeline visualization
    /// </summary>
    public class TimelineStepUI : MonoBehaviour
    {
        [Header("UI References")]
        [SerializeField] private TextMeshProUGUI stepTitleText;
        [SerializeField] private TextMeshProUGUI stepDescriptionText;
        [SerializeField] private TextMeshProUGUI stepOrderText;
        [SerializeField] private Slider progressSlider;
        [SerializeField] private TextMeshProUGUI progressText;
        [SerializeField] private Image completionIcon;
        [SerializeField] private Image backgroundImage;
        [SerializeField] private Image connectionLine;
        [SerializeField] private Button stepButton;
        [SerializeField] private Image triggerIndicator;
        
        [Header("Visual Settings")]
        [SerializeField] private Color completedColor = Color.green;
        [SerializeField] private Color activeColor = Color.yellow;
        [SerializeField] private Color pendingColor = Color.gray;
        [SerializeField] private Color blockedColor = Color.red;
        [SerializeField] private Color selectedColor = Color.cyan;
        
        [Header("Icons")]
        [SerializeField] private Sprite completedIcon;
        [SerializeField] private Sprite activeIcon;
        [SerializeField] private Sprite pendingIcon;
        [SerializeField] private Sprite blockedIcon;
        
        [Header("Timeline Settings")]
        [SerializeField] private bool showConnectionLine = true;
        [SerializeField] private float timelineSpacing = 100f;
        
        private ArcStepDTO arcStep;
        private bool isSelected = false;
        private bool isCurrentStep = false;
        
        // Events
        public event Action<ArcStepDTO> OnStepClicked;
        
        private void Awake()
        {
            if (stepButton != null)
            {
                stepButton.onClick.AddListener(OnStepSelected);
            }
        }
        
        /// <summary>
        /// Set the arc step data for this UI component
        /// </summary>
        /// <param name="step">Arc step DTO to display</param>
        /// <param name="stepIndex">Index of this step in the arc</param>
        /// <param name="totalSteps">Total number of steps in the arc</param>
        public void SetArcStep(ArcStepDTO step, int stepIndex, int totalSteps)
        {
            arcStep = step;
            UpdateDisplay();
            UpdateTimelinePosition(stepIndex, totalSteps);
        }
        
        /// <summary>
        /// Update the visual display with current step data
        /// </summary>
        private void UpdateDisplay()
        {
            if (arcStep == null) return;
            
            // Update step title
            if (stepTitleText != null)
            {
                stepTitleText.text = arcStep.Title ?? $"Step {arcStep.Order}";
            }
            
            // Update step description
            if (stepDescriptionText != null)
            {
                stepDescriptionText.text = TruncateDescription(arcStep.Description ?? "", 80);
            }
            
            // Update step order
            if (stepOrderText != null)
            {
                stepOrderText.text = arcStep.Order.ToString();
            }
            
            // Update progress
            UpdateProgress();
            
            // Update trigger indicator
            UpdateTriggerIndicator();
            
            // Update visual styling
            UpdateVisualStyling();
        }
        
        /// <summary>
        /// Update progress display for the step
        /// </summary>
        private void UpdateProgress()
        {
            if (arcStep == null) return;
            
            float progress = arcStep.IsCompleted ? 1f : 0f;
            string progressDisplay = arcStep.IsCompleted ? "Completed" : "Pending";
            
            // If step has duration, calculate time-based progress
            if (arcStep.EstimatedDurationDays.HasValue && arcStep.StartedAt.HasValue && !arcStep.IsCompleted)
            {
                var elapsed = DateTime.UtcNow - arcStep.StartedAt.Value;
                var totalDuration = TimeSpan.FromDays(arcStep.EstimatedDurationDays.Value);
                
                if (totalDuration.TotalDays > 0)
                {
                    progress = Math.Min(1f, (float)(elapsed.TotalDays / totalDuration.TotalDays));
                    progressDisplay = $"{elapsed.Days}d / {totalDuration.Days}d";
                }
            }
            
            // Update progress slider
            if (progressSlider != null)
            {
                progressSlider.value = progress;
            }
            
            // Update progress text
            if (progressText != null)
            {
                progressText.text = progressDisplay;
            }
        }
        
        /// <summary>
        /// Update trigger indicator based on trigger conditions
        /// </summary>
        private void UpdateTriggerIndicator()
        {
            if (triggerIndicator != null)
            {
                bool hasTriggers = arcStep.TriggerConditions != null && arcStep.TriggerConditions.Count > 0;
                triggerIndicator.gameObject.SetActive(hasTriggers);
                
                if (hasTriggers)
                {
                    // Color based on trigger state
                    triggerIndicator.color = arcStep.IsCompleted ? completedColor : activeColor;
                }
            }
        }
        
        /// <summary>
        /// Update visual styling based on step state
        /// </summary>
        private void UpdateVisualStyling()
        {
            Color stepColor = GetStepColor();
            Sprite stepIcon = GetStepIcon();
            
            // Update completion icon
            if (completionIcon != null)
            {
                completionIcon.color = stepColor;
                if (stepIcon != null)
                {
                    completionIcon.sprite = stepIcon;
                }
            }
            
            // Update background color
            if (backgroundImage != null)
            {
                Color bgColor = isSelected ? selectedColor : stepColor;
                bgColor.a = isSelected ? 0.8f : (isCurrentStep ? 0.6f : 0.3f);
                backgroundImage.color = bgColor;
            }
            
            // Update connection line
            if (connectionLine != null && showConnectionLine)
            {
                connectionLine.color = stepColor;
            }
            
            // Update text colors
            UpdateTextColors(stepColor);
        }
        
        /// <summary>
        /// Get color based on step state
        /// </summary>
        /// <returns>Step color</returns>
        private Color GetStepColor()
        {
            if (arcStep.IsCompleted)
            {
                return completedColor;
            }
            
            if (IsStepBlocked())
            {
                return blockedColor;
            }
            
            if (isCurrentStep)
            {
                return activeColor;
            }
            
            return pendingColor;
        }
        
        /// <summary>
        /// Get icon based on step state
        /// </summary>
        /// <returns>Step icon</returns>
        private Sprite GetStepIcon()
        {
            if (arcStep.IsCompleted)
            {
                return completedIcon;
            }
            
            if (IsStepBlocked())
            {
                return blockedIcon;
            }
            
            if (isCurrentStep)
            {
                return activeIcon;
            }
            
            return pendingIcon;
        }
        
        /// <summary>
        /// Check if step is blocked by dependencies or triggers
        /// </summary>
        /// <returns>True if step is blocked</returns>
        private bool IsStepBlocked()
        {
            // Logic would depend on checking prerequisite steps, triggers, etc.
            // For now, simplified check
            return false;
        }
        
        /// <summary>
        /// Update text colors for better readability
        /// </summary>
        /// <param name="baseColor">Base color to derive text colors from</param>
        private void UpdateTextColors(Color baseColor)
        {
            Color textColor = IsColorDark(baseColor) ? Color.white : Color.black;
            
            if (stepTitleText != null)
            {
                stepTitleText.color = isCurrentStep ? activeColor : textColor;
                stepTitleText.fontStyle = isCurrentStep ? FontStyles.Bold : FontStyles.Normal;
            }
            
            if (stepDescriptionText != null)
            {
                stepDescriptionText.color = textColor;
            }
            
            if (stepOrderText != null)
            {
                stepOrderText.color = baseColor;
            }
            
            if (progressText != null)
            {
                progressText.color = baseColor;
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
        /// Update timeline position based on step index
        /// </summary>
        /// <param name="stepIndex">Index of this step</param>
        /// <param name="totalSteps">Total number of steps</param>
        private void UpdateTimelinePosition(int stepIndex, int totalSteps)
        {
            if (totalSteps <= 1) return;
            
            // Calculate position along timeline
            float normalizedPosition = (float)stepIndex / (totalSteps - 1);
            
            // Update transform position (assuming horizontal timeline)
            RectTransform rectTransform = GetComponent<RectTransform>();
            if (rectTransform != null)
            {
                Vector2 anchoredPosition = rectTransform.anchoredPosition;
                anchoredPosition.x = normalizedPosition * timelineSpacing * (totalSteps - 1);
                rectTransform.anchoredPosition = anchoredPosition;
            }
            
            // Hide connection line for last step
            if (connectionLine != null)
            {
                connectionLine.gameObject.SetActive(stepIndex < totalSteps - 1);
            }
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
        /// <param name="selected">Whether this step is selected</param>
        public void SetSelected(bool selected)
        {
            isSelected = selected;
            UpdateVisualStyling();
        }
        
        /// <summary>
        /// Set current step state
        /// </summary>
        /// <param name="isCurrent">Whether this is the current step</param>
        public void SetIsCurrentStep(bool isCurrent)
        {
            isCurrentStep = isCurrent;
            UpdateVisualStyling();
        }
        
        /// <summary>
        /// Handle step selection
        /// </summary>
        private void OnStepSelected()
        {
            if (arcStep != null)
            {
                OnStepClicked?.Invoke(arcStep);
            }
        }
        
        /// <summary>
        /// Get the associated arc step
        /// </summary>
        /// <returns>Arc step DTO</returns>
        public ArcStepDTO GetArcStep()
        {
            return arcStep;
        }
        
        /// <summary>
        /// Check if this step can be activated
        /// </summary>
        /// <returns>True if step can be activated</returns>
        public bool CanActivateStep()
        {
            return !arcStep.IsCompleted && !IsStepBlocked();
        }
        
        /// <summary>
        /// Get estimated time remaining for step completion
        /// </summary>
        /// <returns>Time remaining display string</returns>
        public string GetTimeRemainingDisplay()
        {
            if (arcStep.IsCompleted) return "Completed";
            
            if (arcStep.EstimatedDurationDays.HasValue)
            {
                if (arcStep.StartedAt.HasValue)
                {
                    var elapsed = DateTime.UtcNow - arcStep.StartedAt.Value;
                    var remaining = TimeSpan.FromDays(arcStep.EstimatedDurationDays.Value) - elapsed;
                    
                    if (remaining.TotalDays > 1)
                    {
                        return $"{remaining.Days}d remaining";
                    }
                    else if (remaining.TotalHours > 0)
                    {
                        return $"{remaining.Hours}h remaining";
                    }
                    else
                    {
                        return "Overdue";
                    }
                }
                
                return $"~{arcStep.EstimatedDurationDays}d estimated";
            }
            
            return "No estimate";
        }
        
        /// <summary>
        /// Refresh the display with updated step data
        /// </summary>
        public void RefreshDisplay()
        {
            UpdateDisplay();
        }
        
        /// <summary>
        /// Show/hide connection line to next step
        /// </summary>
        /// <param name="show">Whether to show the connection line</param>
        public void SetConnectionLineVisible(bool show)
        {
            if (connectionLine != null)
            {
                connectionLine.gameObject.SetActive(show && showConnectionLine);
            }
        }
    }
} 