using System;
using UnityEngine;
using UnityEngine.UI;
using TMPro;
using VDM.Systems.Combat.Models;

namespace VDM.UI.Systems.Combat
{
    /// <summary>
    /// UI component for selecting combat targets
    /// </summary>
    public class TargetButton : MonoBehaviour
    {
        [Header("Target Information")]
        [SerializeField] private Image targetPortrait;
        [SerializeField] private TextMeshProUGUI targetNameText;
        [SerializeField] private TextMeshProUGUI targetStatusText;
        [SerializeField] private Slider healthSlider;
        [SerializeField] private TextMeshProUGUI healthText;
        
        [Header("Target Indicators")]
        [SerializeField] private Image targetTypeIcon;
        [SerializeField] private GameObject allyIndicator;
        [SerializeField] private GameObject enemyIndicator;
        [SerializeField] private GameObject selfIndicator;
        [SerializeField] private GameObject deadIndicator;
        
        [Header("UI Elements")]
        [SerializeField] private Button selectButton;
        [SerializeField] private Image backgroundImage;
        [SerializeField] private Image selectionHighlight;
        [SerializeField] private Image validTargetBorder;
        
        [Header("Visual States")]
        [SerializeField] private Color normalColor = Color.white;
        [SerializeField] private Color hoverColor = Color.cyan;
        [SerializeField] private Color selectedColor = Color.green;
        [SerializeField] private Color allyColor = Color.blue;
        [SerializeField] private Color enemyColor = Color.red;
        [SerializeField] private Color selfColor = Color.yellow;
        [SerializeField] private Color deadColor = Color.gray;
        [SerializeField] private Color invalidTargetColor = new Color(0.5f, 0.5f, 0.5f, 0.5f);
        
        [Header("Animation")]
        [SerializeField] private float hoverScale = 1.05f;
        [SerializeField] private float animationDuration = 0.15f;
        [SerializeField] private LeanTweenType animationEase = LeanTweenType.easeOutQuad;
        [SerializeField] private float pulseSpeed = 2f;
        
        // Data
        private CombatCharacter targetData;
        private TargetType targetType;
        private bool isSelected = false;
        private bool isValidTarget = true;
        private bool isDead = false;
        private Vector3 originalScale;
        
        // Events
        private System.Action onTargetSelected;
        
        private void Awake()
        {
            originalScale = transform.localScale;
            
            // Setup button interaction
            if (selectButton != null)
            {
                selectButton.onClick.AddListener(OnSelectClicked);
            }
            
            UpdateVisualState();
        }
        
        /// <summary>
        /// Initialize the target button
        /// </summary>
        public void Initialize(CombatCharacter target, System.Action selectionCallback)
        {
            targetData = target;
            onTargetSelected = selectionCallback;
            
            DetermineTargetType();
            UpdateTargetDisplay();
            UpdateTargetStatus();
            SetValidTarget(true);
        }
        
        /// <summary>
        /// Set selection state
        /// </summary>
        public void SetSelected(bool selected)
        {
            isSelected = selected;
            UpdateVisualState();
            
            if (selected)
            {
                AnimateSelection();
            }
        }
        
        /// <summary>
        /// Set whether this is a valid target for the current action
        /// </summary>
        public void SetValidTarget(bool valid)
        {
            isValidTarget = valid;
            
            if (selectButton != null)
                selectButton.interactable = valid && !isDead;
            
            UpdateVisualState();
        }
        
        /// <summary>
        /// Update target's health and status
        /// </summary>
        public void UpdateTarget(CombatCharacter updatedTarget)
        {
            targetData = updatedTarget;
            UpdateTargetDisplay();
            UpdateTargetStatus();
        }
        
        private void DetermineTargetType()
        {
            if (targetData == null) return;
            
            // Determine if target is ally, enemy, or self
            if (targetData.IsPlayerCharacter)
            {
                targetType = TargetType.Self;
            }
            else if (targetData.IsAlly)
            {
                targetType = TargetType.Ally;
            }
            else
            {
                targetType = TargetType.Enemy;
            }
        }
        
        private void UpdateTargetDisplay()
        {
            if (targetData == null) return;
            
            // Set target name
            if (targetNameText != null)
                targetNameText.text = targetData.Name;
            
            // Set portrait
            if (targetPortrait != null)
            {
                string portraitPath = GetPortraitPath(targetData);
                Sprite portrait = Resources.Load<Sprite>(portraitPath);
                if (portrait != null)
                    targetPortrait.sprite = portrait;
            }
            
            // Update health display
            if (healthSlider != null && targetData.MaxHealth > 0)
            {
                float healthPercentage = (float)targetData.CurrentHealth / targetData.MaxHealth;
                healthSlider.value = healthPercentage;
                
                // Color code health bar
                var fillImage = healthSlider.fillRect.GetComponent<Image>();
                if (fillImage != null)
                {
                    if (healthPercentage > 0.5f)
                        fillImage.color = Color.green;
                    else if (healthPercentage > 0.25f)
                        fillImage.color = Color.yellow;
                    else
                        fillImage.color = Color.red;
                }
            }
            
            // Set health text
            if (healthText != null)
                healthText.text = $"{targetData.CurrentHealth}/{targetData.MaxHealth}";
            
            // Show appropriate indicators
            UpdateTargetIndicators();
        }
        
        private void UpdateTargetStatus()
        {
            if (targetData == null) return;
            
            isDead = targetData.CurrentHealth <= 0;
            
            // Update status text
            if (targetStatusText != null)
            {
                if (isDead)
                {
                    targetStatusText.text = "Dead";
                    targetStatusText.color = deadColor;
                }
                else if (targetData.StatusEffects?.Count > 0)
                {
                    // Show primary status effect
                    targetStatusText.text = targetData.StatusEffects[0].Name;
                    targetStatusText.color = GetStatusEffectColor(targetData.StatusEffects[0]);
                }
                else
                {
                    targetStatusText.text = "Healthy";
                    targetStatusText.color = Color.white;
                }
            }
            
            // Show dead indicator
            if (deadIndicator != null)
                deadIndicator.SetActive(isDead);
            
            // Update button interactability
            if (selectButton != null)
                selectButton.interactable = isValidTarget && !isDead;
            
            UpdateVisualState();
        }
        
        private void UpdateTargetIndicators()
        {
            // Hide all indicators first
            if (allyIndicator != null) allyIndicator.SetActive(false);
            if (enemyIndicator != null) enemyIndicator.SetActive(false);
            if (selfIndicator != null) selfIndicator.SetActive(false);
            
            // Show appropriate indicator
            switch (targetType)
            {
                case TargetType.Ally:
                    if (allyIndicator != null) allyIndicator.SetActive(true);
                    break;
                case TargetType.Enemy:
                    if (enemyIndicator != null) enemyIndicator.SetActive(true);
                    break;
                case TargetType.Self:
                    if (selfIndicator != null) selfIndicator.SetActive(true);
                    break;
            }
            
            // Set target type icon color
            if (targetTypeIcon != null)
                targetTypeIcon.color = GetTargetTypeColor();
        }
        
        private void UpdateVisualState()
        {
            Color targetColor = normalColor;
            
            if (isDead)
            {
                targetColor = deadColor;
            }
            else if (!isValidTarget)
            {
                targetColor = invalidTargetColor;
            }
            else if (isSelected)
            {
                targetColor = selectedColor;
            }
            else
            {
                targetColor = GetTargetTypeColor();
            }
            
            // Update background color
            if (backgroundImage != null)
                backgroundImage.color = targetColor;
            
            // Update selection highlight
            if (selectionHighlight != null)
                selectionHighlight.gameObject.SetActive(isSelected);
            
            // Update valid target border
            if (validTargetBorder != null)
            {
                validTargetBorder.gameObject.SetActive(isValidTarget && !isDead);
                if (isValidTarget && !isDead)
                {
                    // Pulse the border to indicate it's targetable
                    StartPulsing();
                }
                else
                {
                    StopPulsing();
                }
            }
        }
        
        private void AnimateSelection()
        {
            LeanTween.cancel(gameObject);
            LeanTween.scale(gameObject, originalScale * 1.1f, animationDuration)
                .setEase(LeanTweenType.easeOutBack)
                .setLoopPingPong(1);
        }
        
        private void StartPulsing()
        {
            if (validTargetBorder != null)
            {
                LeanTween.cancel(validTargetBorder.gameObject);
                LeanTween.alpha(validTargetBorder.rectTransform, 0.3f, 1f / pulseSpeed)
                    .setEase(LeanTweenType.easeInOutSine)
                    .setLoopPingPong();
            }
        }
        
        private void StopPulsing()
        {
            if (validTargetBorder != null)
            {
                LeanTween.cancel(validTargetBorder.gameObject);
                validTargetBorder.color = new Color(validTargetBorder.color.r, validTargetBorder.color.g, validTargetBorder.color.b, 1f);
            }
        }
        
        private void OnSelectClicked()
        {
            if (isValidTarget && !isDead && targetData != null)
            {
                onTargetSelected?.Invoke();
            }
        }
        
        public void OnPointerEnter()
        {
            if (isValidTarget && !isDead)
            {
                if (backgroundImage != null && !isSelected)
                    backgroundImage.color = hoverColor;
                
                LeanTween.scale(gameObject, originalScale * hoverScale, animationDuration)
                    .setEase(animationEase);
            }
        }
        
        public void OnPointerExit()
        {
            if (isValidTarget && !isDead)
            {
                if (backgroundImage != null && !isSelected)
                    backgroundImage.color = GetTargetTypeColor();
                
                LeanTween.scale(gameObject, originalScale, animationDuration)
                    .setEase(animationEase);
            }
        }
        
        #region Helper Methods
        
        private Color GetTargetTypeColor()
        {
            if (isDead) return deadColor;
            
            return targetType switch
            {
                TargetType.Ally => allyColor,
                TargetType.Enemy => enemyColor,
                TargetType.Self => selfColor,
                _ => normalColor
            };
        }
        
        private string GetPortraitPath(CombatCharacter character)
        {
            if (character.IsPlayerCharacter)
                return "Portraits/Player";
            
            // For enemies, use their type or name
            return $"Portraits/Enemies/{character.Name.Replace(" ", "")}";
        }
        
        private Color GetStatusEffectColor(StatusEffect effect)
        {
            return effect.EffectType switch
            {
                StatusEffectType.Buff => Color.green,
                StatusEffectType.Debuff => Color.red,
                StatusEffectType.Poison => Color.magenta,
                StatusEffectType.Blessing => Color.yellow,
                _ => Color.white
            };
        }
        
        #endregion
        
        private void OnDestroy()
        {
            // Clean up any running animations
            LeanTween.cancel(gameObject);
            if (validTargetBorder != null)
                LeanTween.cancel(validTargetBorder.gameObject);
        }
        
        #region Public Properties
        
        public CombatCharacter TargetData => targetData;
        public TargetType TargetType => targetType;
        public bool IsSelected => isSelected;
        public bool IsValidTarget => isValidTarget;
        public bool IsDead => isDead;
        
        #endregion
    }
    
    /// <summary>
    /// Target type enumeration for UI display
    /// </summary>
    public enum TargetType
    {
        Self,
        Ally,
        Enemy,
        Any
    }
    
    /// <summary>
    /// Status effect types for visual indication
    /// </summary>
    public enum StatusEffectType
    {
        Buff,
        Debuff,
        Poison,
        Blessing,
        Neutral
    }
} 