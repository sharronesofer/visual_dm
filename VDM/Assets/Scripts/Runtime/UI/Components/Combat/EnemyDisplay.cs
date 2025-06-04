using System;
using UnityEngine;
using UnityEngine.UI;
using TMPro;
using VDM.DTOs.Game.Character;

namespace VDM.UI.Systems.Combat
{
    /// <summary>
    /// UI component for displaying enemy information during combat
    /// </summary>
    public class EnemyDisplay : MonoBehaviour
    {
        [Header("Enemy Information")]
        [SerializeField] private Image enemyPortrait;
        [SerializeField] private TextMeshProUGUI enemyNameText;
        [SerializeField] private TextMeshProUGUI enemyLevelText;
        [SerializeField] private TextMeshProUGUI enemyTypeText;
        
        [Header("Health and Status")]
        [SerializeField] private Slider healthSlider;
        [SerializeField] private TextMeshProUGUI healthText;
        [SerializeField] private Transform statusEffectsContainer;
        [SerializeField] private GameObject statusEffectPrefab;
        
        [Header("Combat State")]
        [SerializeField] private Image selectionHighlight;
        [SerializeField] private Image turnIndicator;
        [SerializeField] private GameObject deadOverlay;
        [SerializeField] private Button targetButton;
        
        [Header("Visual Feedback")]
        [SerializeField] private Color normalColor = Color.white;
        [SerializeField] private Color selectedColor = Color.cyan;
        [SerializeField] private Color targetableColor = Color.yellow;
        [SerializeField] private Color deadColor = Color.red;
        [SerializeField] private Color currentTurnColor = Color.green;
        
        [Header("Animation")]
        [SerializeField] private float hoverScale = 1.05f;
        [SerializeField] private float animationDuration = 0.2f;
        [SerializeField] private LeanTweenType animationEase = LeanTweenType.easeOutQuad;
        
        // Data
        private EnemyModel enemyData;
        private bool isSelected = false;
        private bool isTargetable = false;
        private bool isDead = false;
        private bool isCurrentTurn = false;
        private Vector3 originalScale;
        
        // Events
        private System.Action<EnemyModel> onEnemySelected;
        
        private void Awake()
        {
            originalScale = transform.localScale;
            
            // Setup button interaction
            if (targetButton != null)
            {
                targetButton.onClick.AddListener(OnTargetClicked);
            }
            
            // Initial state
            SetSelected(false);
            SetTargetable(false);
            SetDead(false);
            SetCurrentTurn(false);
        }
        
        /// <summary>
        /// Initialize the enemy display
        /// </summary>
        public void Initialize(EnemyModel enemy, System.Action<EnemyModel> selectionCallback)
        {
            enemyData = enemy;
            onEnemySelected = selectionCallback;
            
            UpdateEnemyInfo();
            UpdateHealthDisplay();
            UpdateStatusEffects();
        }
        
        /// <summary>
        /// Update enemy data
        /// </summary>
        public void UpdateEnemy(EnemyModel enemy)
        {
            enemyData = enemy;
            UpdateEnemyInfo();
            UpdateHealthDisplay();
            UpdateStatusEffects();
            
            // Update dead state
            SetDead(enemy.Health <= 0);
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
        /// Set targetable state
        /// </summary>
        public void SetTargetable(bool targetable)
        {
            isTargetable = targetable;
            UpdateVisualState();
            
            if (targetButton != null)
                targetButton.interactable = targetable && !isDead;
        }
        
        /// <summary>
        /// Set dead state
        /// </summary>
        public void SetDead(bool dead)
        {
            isDead = dead;
            
            if (deadOverlay != null)
                deadOverlay.SetActive(dead);
            
            if (targetButton != null)
                targetButton.interactable = !dead && isTargetable;
            
            UpdateVisualState();
        }
        
        /// <summary>
        /// Set current turn indicator
        /// </summary>
        public void SetCurrentTurn(bool currentTurn)
        {
            isCurrentTurn = currentTurn;
            
            if (turnIndicator != null)
                turnIndicator.gameObject.SetActive(currentTurn);
            
            UpdateVisualState();
        }
        
        /// <summary>
        /// Show damage number animation
        /// </summary>
        public void ShowDamage(int damage)
        {
            // Create floating damage text
            GameObject damageText = new GameObject("DamageText");
            damageText.transform.SetParent(transform);
            damageText.transform.localPosition = Vector3.zero;
            
            var textComponent = damageText.AddComponent<TextMeshProUGUI>();
            textComponent.text = damage.ToString();
            textComponent.color = Color.red;
            textComponent.fontSize = 24;
            textComponent.fontStyle = FontStyles.Bold;
            textComponent.alignment = TextAlignmentOptions.Center;
            
            // Animate damage text
            LeanTween.moveLocalY(damageText, 50f, 1f)
                .setEase(LeanTweenType.easeOutQuad);
            LeanTween.alphaCanvas(damageText.GetComponent<CanvasGroup>() ?? damageText.AddComponent<CanvasGroup>(), 0f, 1f)
                .setDelay(0.5f)
                .setOnComplete(() => Destroy(damageText));
        }
        
        /// <summary>
        /// Show healing number animation
        /// </summary>
        public void ShowHealing(int healing)
        {
            // Create floating healing text
            GameObject healingText = new GameObject("HealingText");
            healingText.transform.SetParent(transform);
            healingText.transform.localPosition = Vector3.zero;
            
            var textComponent = healingText.AddComponent<TextMeshProUGUI>();
            textComponent.text = $"+{healing}";
            textComponent.color = Color.green;
            textComponent.fontSize = 24;
            textComponent.fontStyle = FontStyles.Bold;
            textComponent.alignment = TextAlignmentOptions.Center;
            
            // Animate healing text
            LeanTween.moveLocalY(healingText, 50f, 1f)
                .setEase(LeanTweenType.easeOutQuad);
            LeanTween.alphaCanvas(healingText.GetComponent<CanvasGroup>() ?? healingText.AddComponent<CanvasGroup>(), 0f, 1f)
                .setDelay(0.5f)
                .setOnComplete(() => Destroy(healingText));
        }
        
        private void UpdateEnemyInfo()
        {
            if (enemyData == null) return;
            
            // Set enemy name
            if (enemyNameText != null)
                enemyNameText.text = enemyData.Name;
            
            // Set enemy level
            if (enemyLevelText != null)
                enemyLevelText.text = $"Level {enemyData.Level}";
            
            // Set enemy type
            if (enemyTypeText != null)
                enemyTypeText.text = enemyData.Type.ToString();
            
            // Set portrait
            if (enemyPortrait != null)
            {
                // Load enemy portrait from resources
                Sprite portrait = Resources.Load<Sprite>($"EnemyPortraits/{enemyData.Type}");
                if (portrait != null)
                    enemyPortrait.sprite = portrait;
            }
        }
        
        private void UpdateHealthDisplay()
        {
            if (enemyData == null) return;
            
            // Update health slider
            if (healthSlider != null)
            {
                float healthPercentage = (float)enemyData.Health / enemyData.MaxHealth;
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
            
            // Update health text
            if (healthText != null)
                healthText.text = $"{enemyData.Health}/{enemyData.MaxHealth}";
        }
        
        private void UpdateStatusEffects()
        {
            if (statusEffectsContainer == null || enemyData == null) return;
            
            // Clear existing status effects
            foreach (Transform child in statusEffectsContainer)
            {
                Destroy(child.gameObject);
            }
            
            // Add current status effects
            if (enemyData.Stats != null)
            {
                foreach (var stat in enemyData.Stats)
                {
                    if (stat.Key.Contains("Effect") || stat.Key.Contains("Status"))
                    {
                        CreateStatusEffect(stat.Key, stat.Value.ToString());
                    }
                }
            }
        }
        
        private void CreateStatusEffect(string effectName, string value)
        {
            if (statusEffectPrefab == null) return;
            
            GameObject statusEffect = Instantiate(statusEffectPrefab, statusEffectsContainer);
            var statusText = statusEffect.GetComponentInChildren<TextMeshProUGUI>();
            if (statusText != null)
            {
                statusText.text = effectName;
            }
            
            // Add tooltip for status effect details
            var tooltip = statusEffect.GetComponent<Button>();
            if (tooltip != null)
            {
                tooltip.onClick.AddListener(() =>
                {
                    Debug.Log($"Status Effect: {effectName} - {value}");
                });
            }
        }
        
        private void UpdateVisualState()
        {
            Color targetColor = normalColor;
            
            if (isDead)
            {
                targetColor = deadColor;
            }
            else if (isCurrentTurn)
            {
                targetColor = currentTurnColor;
            }
            else if (isSelected)
            {
                targetColor = selectedColor;
            }
            else if (isTargetable)
            {
                targetColor = targetableColor;
            }
            
            // Update selection highlight
            if (selectionHighlight != null)
            {
                selectionHighlight.color = targetColor;
                selectionHighlight.gameObject.SetActive(isSelected || isTargetable || isCurrentTurn);
            }
            
            // Update turn indicator
            if (turnIndicator != null)
            {
                turnIndicator.color = currentTurnColor;
            }
        }
        
        private void AnimateSelection()
        {
            LeanTween.cancel(gameObject);
            LeanTween.scale(gameObject, originalScale * 1.1f, animationDuration)
                .setEase(LeanTweenType.easeOutBack)
                .setLoopPingPong(1);
        }
        
        private void OnTargetClicked()
        {
            if (enemyData != null && !isDead)
            {
                onEnemySelected?.Invoke(enemyData);
            }
        }
        
        public void OnPointerEnter()
        {
            if (!isDead && isTargetable)
            {
                LeanTween.scale(gameObject, originalScale * hoverScale, animationDuration)
                    .setEase(animationEase);
            }
        }
        
        public void OnPointerExit()
        {
            if (!isDead)
            {
                LeanTween.scale(gameObject, originalScale, animationDuration)
                    .setEase(animationEase);
            }
        }
        
        #region Public Properties
        
        public EnemyModel EnemyData => enemyData;
        public bool IsSelected => isSelected;
        public bool IsTargetable => isTargetable;
        public bool IsDead => isDead;
        public bool IsCurrentTurn => isCurrentTurn;
        
        #endregion
    }
} 