using TMPro;
using UnityEngine.UI;
using UnityEngine;
using VDM.Runtime.Quest.Models;


namespace VDM.Runtime.Quest.UI
{
    /// <summary>
    /// UI component for displaying individual quest steps
    /// </summary>
    public class QuestStepUI : MonoBehaviour
    {
        [Header("UI References")]
        [SerializeField] private TextMeshProUGUI stepDescriptionText;
        [SerializeField] private TextMeshProUGUI stepTypeText;
        [SerializeField] private TextMeshProUGUI progressText;
        [SerializeField] private Slider progressSlider;
        [SerializeField] private Image completionIcon;
        [SerializeField] private Image backgroundImage;
        [SerializeField] private Toggle completionToggle;
        
        [Header("Visual Settings")]
        [SerializeField] private Color completedColor = Color.green;
        [SerializeField] private Color inProgressColor = Color.yellow;
        [SerializeField] private Color pendingColor = Color.gray;
        [SerializeField] private Color optionalColor = Color.blue;
        
        [Header("Icons")]
        [SerializeField] private Sprite completedIcon;
        [SerializeField] private Sprite inProgressIcon;
        [SerializeField] private Sprite pendingIcon;
        [SerializeField] private Sprite optionalIcon;
        
        private QuestStepDTO questStep;
        
        private void Awake()
        {
            if (completionToggle != null)
            {
                completionToggle.onValueChanged.AddListener(OnCompletionToggled);
            }
        }
        
        /// <summary>
        /// Set the quest step data for this UI component
        /// </summary>
        /// <param name="step">Quest step DTO to display</param>
        public void SetQuestStep(QuestStepDTO step)
        {
            questStep = step;
            UpdateDisplay();
        }
        
        /// <summary>
        /// Update the visual display with current step data
        /// </summary>
        private void UpdateDisplay()
        {
            if (questStep == null) return;
            
            // Update step description
            if (stepDescriptionText != null)
            {
                string description = questStep.Description ?? "Unknown Step";
                if (questStep.IsOptional)
                {
                    description = "[Optional] " + description;
                }
                stepDescriptionText.text = description;
            }
            
            // Update step type
            if (stepTypeText != null)
            {
                stepTypeText.text = FormatStepType(questStep.Type);
            }
            
            // Update progress
            UpdateProgress();
            
            // Update completion state
            UpdateCompletionState();
            
            // Update visual styling
            UpdateVisualStyling();
        }
        
        /// <summary>
        /// Update progress display for the step
        /// </summary>
        private void UpdateProgress()
        {
            if (questStep == null) return;
            
            // Calculate progress based on current/required count
            float progress = 0f;
            string progressDisplay = "";
            
            if (questStep.RequiredCount > 0)
            {
                progress = (float)questStep.CurrentCount / questStep.RequiredCount;
                progressDisplay = $"{questStep.CurrentCount}/{questStep.RequiredCount}";
            }
            else if (questStep.Quantity > 0)
            {
                // Use quantity as fallback
                int currentProgress = questStep.Completed ? questStep.Quantity : 0;
                progress = questStep.Completed ? 1f : 0f;
                progressDisplay = $"{currentProgress}/{questStep.Quantity}";
            }
            else
            {
                // Simple completion check
                progress = questStep.Completed ? 1f : 0f;
                progressDisplay = questStep.Completed ? "Completed" : "Pending";
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
        /// Update completion state controls
        /// </summary>
        private void UpdateCompletionState()
        {
            if (completionToggle != null)
            {
                completionToggle.SetIsOnWithoutNotify(questStep.Completed);
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
                Color bgColor = stepColor;
                bgColor.a = 0.2f;
                backgroundImage.color = bgColor;
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
            if (questStep.IsOptional)
            {
                return optionalColor;
            }
            
            if (questStep.Completed)
            {
                return completedColor;
            }
            
            if (questStep.CurrentCount > 0 && questStep.RequiredCount > 0)
            {
                return inProgressColor;
            }
            
            return pendingColor;
        }
        
        /// <summary>
        /// Get icon based on step state
        /// </summary>
        /// <returns>Step icon</returns>
        private Sprite GetStepIcon()
        {
            if (questStep.IsOptional)
            {
                return optionalIcon;
            }
            
            if (questStep.Completed)
            {
                return completedIcon;
            }
            
            if (questStep.CurrentCount > 0 && questStep.RequiredCount > 0)
            {
                return inProgressIcon;
            }
            
            return pendingIcon;
        }
        
        /// <summary>
        /// Update text colors for better readability
        /// </summary>
        /// <param name="baseColor">Base color to derive text colors from</param>
        private void UpdateTextColors(Color baseColor)
        {
            Color textColor = IsColorDark(baseColor) ? Color.white : Color.black;
            
            if (stepDescriptionText != null)
            {
                stepDescriptionText.color = questStep.Completed ? completedColor : textColor;
            }
            
            if (stepTypeText != null)
            {
                stepTypeText.color = baseColor;
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
        /// Format step type for display
        /// </summary>
        /// <param name="stepType">Raw step type</param>
        /// <returns>Formatted step type</returns>
        private string FormatStepType(string stepType)
        {
            return stepType?.Replace("_", " ").ToUpper() ?? "GENERAL";
        }
        
        /// <summary>
        /// Handle completion toggle changes
        /// </summary>
        /// <param name="isCompleted">New completion state</param>
        private void OnCompletionToggled(bool isCompleted)
        {
            if (questStep != null)
            {
                questStep.Completed = isCompleted;
                if (isCompleted && questStep.RequiredCount > 0)
                {
                    questStep.CurrentCount = questStep.RequiredCount;
                }
                UpdateDisplay();
                
                // TODO: Notify parent quest log of step completion change
                Debug.Log($"Quest step {questStep.Id} completion toggled to {isCompleted}");
            }
        }
        
        /// <summary>
        /// Get the associated quest step
        /// </summary>
        /// <returns>Quest step DTO</returns>
        public QuestStepDTO GetQuestStep()
        {
            return questStep;
        }
        
        /// <summary>
        /// Set step as current/active step
        /// </summary>
        /// <param name="isCurrent">Whether this is the current step</param>
        public void SetIsCurrentStep(bool isCurrent)
        {
            if (backgroundImage != null)
            {
                Color bgColor = backgroundImage.color;
                bgColor.a = isCurrent ? 0.5f : 0.2f;
                backgroundImage.color = bgColor;
            }
            
            // Add visual indicator for current step
            if (isCurrent && !questStep.Completed)
            {
                // Could add a pulsing animation or special border
                if (stepDescriptionText != null)
                {
                    stepDescriptionText.fontStyle = FontStyles.Bold;
                }
            }
            else
            {
                if (stepDescriptionText != null)
                {
                    stepDescriptionText.fontStyle = FontStyles.Normal;
                }
            }
        }
        
        /// <summary>
        /// Refresh the display with updated step data
        /// </summary>
        public void RefreshDisplay()
        {
            UpdateDisplay();
        }
    }
} 