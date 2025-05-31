using System;
using UnityEngine;
using UnityEngine.UI;
using TMPro;
using VDM.Systems.Loot.Models;
using VDM.Systems.Loot.Services;

namespace VDM.Systems.Loot.Ui
{
    /// <summary>
    /// UI component for displaying a single loot item
    /// </summary>
    public class LootItemUI : MonoBehaviour
    {
        [Header("UI References")]
        [SerializeField] private Image itemIcon;
        [SerializeField] private TextMeshProUGUI itemNameText;
        [SerializeField] private TextMeshProUGUI itemDescriptionText;
        [SerializeField] private TextMeshProUGUI itemValueText;
        [SerializeField] private TextMeshProUGUI itemLevelText;
        [SerializeField] private Image rarityBorder;
        [SerializeField] private Image rarityBackground;
        [SerializeField] private GameObject unidentifiedOverlay;
        [SerializeField] private GameObject magicalGlow;
        [SerializeField] private GameObject cursedIndicator;
        [SerializeField] private Button itemButton;
        [SerializeField] private Button identifyButton;
        [SerializeField] private Button enhanceButton;
        
        [Header("Visual Settings")]
        [SerializeField] private Sprite defaultItemIcon;
        [SerializeField] private Color unidentifiedColor = Color.gray;
        [SerializeField] private float glowIntensity = 1.5f;
        
        // Events
        public event Action<LootItem> OnItemClicked;
        public event Action<LootItem> OnIdentifyRequested;
        public event Action<LootItem> OnEnhanceRequested;
        
        // Private fields
        private LootItem currentItem;
        private bool isInteractable = true;
        
        private void Awake()
        {
            SetupEventListeners();
        }
        
        private void SetupEventListeners()
        {
            if (itemButton != null)
                itemButton.onClick.AddListener(() => OnItemClicked?.Invoke(currentItem));
            
            if (identifyButton != null)
                identifyButton.onClick.AddListener(() => OnIdentifyRequested?.Invoke(currentItem));
            
            if (enhanceButton != null)
                enhanceButton.onClick.AddListener(() => OnEnhanceRequested?.Invoke(currentItem));
        }
        
        /// <summary>
        /// Set the loot item to display
        /// </summary>
        public void SetItem(LootItem item)
        {
            currentItem = item;
            UpdateDisplay();
        }
        
        /// <summary>
        /// Update the visual display based on current item
        /// </summary>
        private void UpdateDisplay()
        {
            if (currentItem == null)
            {
                gameObject.SetActive(false);
                return;
            }
            
            gameObject.SetActive(true);
            
            // Update name
            if (itemNameText != null)
            {
                itemNameText.text = currentItem.GetDisplayName();
                itemNameText.color = currentItem.NameRevealed ? Color.white : unidentifiedColor;
            }
            
            // Update description
            if (itemDescriptionText != null)
            {
                itemDescriptionText.text = currentItem.GetDisplayDescription();
            }
            
            // Update value
            if (itemValueText != null)
            {
                if (currentItem.NameRevealed)
                {
                    itemValueText.text = $"{currentItem.GetAdjustedValue():F0} gold";
                }
                else
                {
                    itemValueText.text = "??? gold";
                }
            }
            
            // Update level
            if (itemLevelText != null)
            {
                itemLevelText.text = $"Level {currentItem.Level}";
            }
            
            // Update rarity colors
            UpdateRarityDisplay();
            
            // Update special indicators
            UpdateSpecialIndicators();
            
            // Update interaction buttons
            UpdateButtons();
        }
        
        /// <summary>
        /// Update rarity-based visual elements
        /// </summary>
        private void UpdateRarityDisplay()
        {
            Color rarityColor = currentItem.GetRarityColor();
            
            if (rarityBorder != null)
            {
                rarityBorder.color = rarityColor;
            }
            
            if (rarityBackground != null)
            {
                Color bgColor = rarityColor;
                bgColor.a = 0.2f; // Semi-transparent background
                rarityBackground.color = bgColor;
            }
        }
        
        /// <summary>
        /// Update special visual indicators
        /// </summary>
        private void UpdateSpecialIndicators()
        {
            // Unidentified overlay
            if (unidentifiedOverlay != null)
            {
                unidentifiedOverlay.SetActive(currentItem.NeedsIdentification());
            }
            
            // Magical glow
            if (magicalGlow != null)
            {
                magicalGlow.SetActive(currentItem.IsMagical && currentItem.NameRevealed);
                
                if (currentItem.IsMagical && magicalGlow.activeInHierarchy)
                {
                    // Animate the glow
                    var glowImage = magicalGlow.GetComponent<Image>();
                    if (glowImage != null)
                    {
                        Color glowColor = currentItem.GetRarityColor();
                        glowColor.a = Mathf.PingPong(Time.time, 0.5f) + 0.3f;
                        glowImage.color = glowColor;
                    }
                }
            }
            
            // Cursed indicator
            if (cursedIndicator != null)
            {
                cursedIndicator.SetActive(currentItem.IsCursed && currentItem.NameRevealed);
            }
        }
        
        /// <summary>
        /// Update interaction buttons based on item state
        /// </summary>
        private void UpdateButtons()
        {
            // Identify button
            if (identifyButton != null)
            {
                identifyButton.gameObject.SetActive(currentItem.NeedsIdentification() && isInteractable);
            }
            
            // Enhance button
            if (enhanceButton != null)
            {
                bool canEnhance = currentItem.NameRevealed && 
                                 !currentItem.IsCursed && 
                                 currentItem.Rarity != "legendary" && 
                                 isInteractable;
                enhanceButton.gameObject.SetActive(canEnhance);
            }
            
            // Main item button
            if (itemButton != null)
            {
                itemButton.interactable = isInteractable;
            }
        }
        
        /// <summary>
        /// Set whether the item UI is interactable
        /// </summary>
        public void SetInteractable(bool interactable)
        {
            isInteractable = interactable;
            UpdateButtons();
        }
        
        /// <summary>
        /// Highlight the item (for selection, hover, etc.)
        /// </summary>
        public void SetHighlighted(bool highlighted)
        {
            if (rarityBorder != null)
            {
                rarityBorder.gameObject.SetActive(highlighted);
            }
        }
        
        /// <summary>
        /// Play an animation when the item is updated
        /// </summary>
        public void PlayUpdateAnimation()
        {
            // Simple scale animation
            LeanTween.scale(gameObject, Vector3.one * 1.1f, 0.1f)
                .setEase(LeanTweenType.easeOutQuad)
                .setOnComplete(() => {
                    LeanTween.scale(gameObject, Vector3.one, 0.1f)
                        .setEase(LeanTweenType.easeInQuad);
                });
        }
        
        /// <summary>
        /// Show a tooltip with detailed item information
        /// </summary>
        public void ShowTooltip()
        {
            if (currentItem == null) return;
            
            string tooltipText = BuildTooltipText();
            
            // Assuming there's a tooltip system available
            // TooltipManager.Instance?.ShowTooltip(tooltipText, transform.position);
            Debug.Log($"Tooltip: {tooltipText}");
        }
        
        /// <summary>
        /// Hide the tooltip
        /// </summary>
        public void HideTooltip()
        {
            // TooltipManager.Instance?.HideTooltip();
        }
        
        /// <summary>
        /// Build detailed tooltip text
        /// </summary>
        private string BuildTooltipText()
        {
            if (currentItem == null) return "";
            
            var tooltip = new System.Text.StringBuilder();
            
            tooltip.AppendLine($"<b>{currentItem.GetDisplayName()}</b>");
            tooltip.AppendLine($"<color=#{ColorUtility.ToHtmlStringRGB(currentItem.GetRarityColor())}>{currentItem.Rarity}</color>");
            tooltip.AppendLine($"Level {currentItem.Level}");
            tooltip.AppendLine();
            
            if (currentItem.NameRevealed)
            {
                tooltip.AppendLine(currentItem.Description);
                tooltip.AppendLine();
                
                // Stats
                if (currentItem.Stats.Count > 0)
                {
                    tooltip.AppendLine("<b>Stats:</b>");
                    foreach (var stat in currentItem.Stats)
                    {
                        tooltip.AppendLine($"  {stat.Key}: +{stat.Value}");
                    }
                    tooltip.AppendLine();
                }
                
                // Effects
                if (currentItem.RevealedEffects.Count > 0)
                {
                    tooltip.AppendLine("<b>Effects:</b>");
                    foreach (var effect in currentItem.RevealedEffects)
                    {
                        tooltip.AppendLine($"  • {effect}");
                    }
                    tooltip.AppendLine();
                }
                
                // Unknown effects hint
                if (currentItem.UnknownEffects.Count > 0)
                {
                    tooltip.AppendLine($"<color=yellow>+{currentItem.UnknownEffects.Count} unknown properties</color>");
                    tooltip.AppendLine();
                }
                
                // Value and weight
                tooltip.AppendLine($"Value: {currentItem.GetAdjustedValue():F0} gold");
                tooltip.AppendLine($"Weight: {currentItem.Weight:F1} lbs");
                
                // Durability
                if (currentItem.MaxDurability > 0)
                {
                    float durabilityPercent = (currentItem.Durability / currentItem.MaxDurability) * 100f;
                    tooltip.AppendLine($"Durability: {durabilityPercent:F0}%");
                }
            }
            else
            {
                tooltip.AppendLine("<color=gray>This item must be identified to reveal its properties.</color>");
            }
            
            return tooltip.ToString();
        }
        
        private void OnDestroy()
        {
            // Clean up event listeners
            if (itemButton != null)
                itemButton.onClick.RemoveAllListeners();
            
            if (identifyButton != null)
                identifyButton.onClick.RemoveAllListeners();
            
            if (enhanceButton != null)
                enhanceButton.onClick.RemoveAllListeners();
        }
    }
} 