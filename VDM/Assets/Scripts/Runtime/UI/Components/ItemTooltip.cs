using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using TMPro;
using VDM.DTOs.Game.Character;

namespace VDM.UI.Systems.Inventory
{
    /// <summary>
    /// Tooltip component for displaying detailed item information
    /// </summary>
    public class ItemTooltip : MonoBehaviour
    {
        [Header("Tooltip Layout")]
        [SerializeField] private RectTransform tooltipRect;
        [SerializeField] private Image backgroundImage;
        [SerializeField] private CanvasGroup canvasGroup;
        
        [Header("Item Header")]
        [SerializeField] private Image itemIcon;
        [SerializeField] private TextMeshProUGUI itemNameText;
        [SerializeField] private TextMeshProUGUI itemTypeText;
        [SerializeField] private Image rarityBorder;
        
        [Header("Item Stats")]
        [SerializeField] private Transform statsContainer;
        [SerializeField] private GameObject statPrefab;
        [SerializeField] private TextMeshProUGUI damageText;
        [SerializeField] private TextMeshProUGUI armorClassText;
        [SerializeField] private TextMeshProUGUI attributeBonusesText;
        
        [Header("Item Information")]
        [SerializeField] private TextMeshProUGUI descriptionText;
        [SerializeField] private TextMeshProUGUI valueText;
        [SerializeField] private TextMeshProUGUI weightText;
        [SerializeField] private TextMeshProUGUI quantityText;
        
        [Header("Item Properties")]
        [SerializeField] private Transform propertiesContainer;
        [SerializeField] private GameObject propertyPrefab;
        [SerializeField] private TextMeshProUGUI usabilityText;
        [SerializeField] private TextMeshProUGUI requirementsText;
        
        [Header("Animation")]
        [SerializeField] private float fadeInDuration = 0.2f;
        [SerializeField] private float fadeOutDuration = 0.15f;
        [SerializeField] private Vector2 offset = new Vector2(10f, -10f);
        
        [Header("Visual Configuration")]
        [SerializeField] private Color[] rarityColors = new Color[]
        {
            Color.white,        // Common
            Color.green,        // Uncommon
            Color.blue,         // Rare
            new Color(0.5f, 0f, 0.5f), // Epic (Purple)
            Color.yellow,       // Legendary
            Color.red           // Artifact
        };
        
        // Data
        private ItemModel currentItem;
        private Camera uiCamera;
        private Canvas parentCanvas;
        private bool isVisible = false;
        
        // UI Elements
        private List<GameObject> dynamicStatElements = new List<GameObject>();
        private List<GameObject> dynamicPropertyElements = new List<GameObject>();
        
        private void Awake()
        {
            // Find UI camera and canvas
            parentCanvas = GetComponentInParent<Canvas>();
            uiCamera = parentCanvas?.worldCamera ?? Camera.main;
            
            // Initially hide tooltip
            if (canvasGroup != null)
                canvasGroup.alpha = 0f;
            
            gameObject.SetActive(false);
        }
        
        /// <summary>
        /// Show tooltip for an item at the specified screen position
        /// </summary>
        public void ShowTooltip(ItemModel item, Vector2 screenPosition)
        {
            if (item == null) return;
            
            currentItem = item;
            gameObject.SetActive(true);
            
            UpdateTooltipContent();
            PositionTooltip(screenPosition);
            
            // Animate fade in
            LeanTween.cancel(gameObject);
            if (canvasGroup != null)
            {
                LeanTween.alphaCanvas(canvasGroup, 1f, fadeInDuration)
                    .setEase(LeanTweenType.easeOutQuad);
            }
            
            isVisible = true;
        }
        
        /// <summary>
        /// Hide the tooltip
        /// </summary>
        public void HideTooltip()
        {
            if (!isVisible) return;
            
            isVisible = false;
            
            // Animate fade out
            LeanTween.cancel(gameObject);
            if (canvasGroup != null)
            {
                LeanTween.alphaCanvas(canvasGroup, 0f, fadeOutDuration)
                    .setEase(LeanTweenType.easeInQuad)
                    .setOnComplete(() => gameObject.SetActive(false));
            }
            else
            {
                gameObject.SetActive(false);
            }
        }
        
        /// <summary>
        /// Update tooltip position to follow mouse
        /// </summary>
        public void UpdateTooltipPosition(Vector2 screenPosition)
        {
            if (isVisible)
            {
                PositionTooltip(screenPosition);
            }
        }
        
        private void UpdateTooltipContent()
        {
            if (currentItem == null) return;
            
            UpdateHeader();
            UpdateStats();
            UpdateInformation();
            UpdateProperties();
            UpdateUsability();
            
            // Force layout rebuild
            LayoutRebuilder.ForceRebuildLayoutImmediate(tooltipRect);
        }
        
        private void UpdateHeader()
        {
            // Set item name
            if (itemNameText != null)
                itemNameText.text = currentItem.Name;
            
            // Set item type
            if (itemTypeText != null)
                itemTypeText.text = GetItemTypeDisplayName(currentItem.Type);
            
            // Set item icon
            if (itemIcon != null)
            {
                // Load item icon from resources
                Sprite icon = Resources.Load<Sprite>($"ItemIcons/{currentItem.Type}");
                if (icon != null)
                    itemIcon.sprite = icon;
            }
            
            // Set rarity border
            if (rarityBorder != null)
            {
                Color rarityColor = GetRarityColor(currentItem);
                rarityBorder.color = rarityColor;
                
                // Also update name color
                if (itemNameText != null)
                    itemNameText.color = rarityColor;
            }
        }
        
        private void UpdateStats()
        {
            ClearDynamicStats();
            
            if (currentItem.Stats == null) return;
            
            // Show damage for weapons
            if (currentItem.Stats.Damage > 0 && damageText != null)
            {
                damageText.gameObject.SetActive(true);
                damageText.text = $"Damage: {currentItem.Stats.Damage}";
            }
            else if (damageText != null)
            {
                damageText.gameObject.SetActive(false);
            }
            
            // Show armor class for armor
            if (currentItem.Stats.ArmorClass > 0 && armorClassText != null)
            {
                armorClassText.gameObject.SetActive(true);
                armorClassText.text = $"Armor Class: +{currentItem.Stats.ArmorClass}";
            }
            else if (armorClassText != null)
            {
                armorClassText.gameObject.SetActive(false);
            }
            
            // Show attribute bonuses
            UpdateAttributeBonuses();
            
            // Create dynamic stat elements for other properties
            if (statsContainer != null && statPrefab != null)
            {
                CreateDynamicStats();
            }
        }
        
        private void UpdateAttributeBonuses()
        {
            if (attributeBonusesText == null || currentItem.Stats == null) return;
            
            var bonuses = new List<string>();
            
            if (currentItem.Stats.StrengthBonus != 0)
                bonuses.Add($"STR: {FormatBonus(currentItem.Stats.StrengthBonus)}");
            if (currentItem.Stats.DexterityBonus != 0)
                bonuses.Add($"DEX: {FormatBonus(currentItem.Stats.DexterityBonus)}");
            if (currentItem.Stats.ConstitutionBonus != 0)
                bonuses.Add($"CON: {FormatBonus(currentItem.Stats.ConstitutionBonus)}");
            if (currentItem.Stats.IntelligenceBonus != 0)
                bonuses.Add($"INT: {FormatBonus(currentItem.Stats.IntelligenceBonus)}");
            if (currentItem.Stats.WisdomBonus != 0)
                bonuses.Add($"WIS: {FormatBonus(currentItem.Stats.WisdomBonus)}");
            if (currentItem.Stats.CharismaBonus != 0)
                bonuses.Add($"CHA: {FormatBonus(currentItem.Stats.CharismaBonus)}");
            
            if (bonuses.Count > 0)
            {
                attributeBonusesText.gameObject.SetActive(true);
                attributeBonusesText.text = string.Join(", ", bonuses);
            }
            else
            {
                attributeBonusesText.gameObject.SetActive(false);
            }
        }
        
        private void CreateDynamicStats()
        {
            // Create additional stat entries from item properties
            if (currentItem.Properties != null)
            {
                foreach (var property in currentItem.Properties)
                {
                    if (IsStatProperty(property.Key))
                    {
                        GameObject statGO = Instantiate(statPrefab, statsContainer);
                        var statText = statGO.GetComponent<TextMeshProUGUI>();
                        if (statText != null)
                        {
                            statText.text = $"{property.Key}: {property.Value}";
                        }
                        dynamicStatElements.Add(statGO);
                    }
                }
            }
        }
        
        private void UpdateInformation()
        {
            // Set description
            if (descriptionText != null)
            {
                descriptionText.text = !string.IsNullOrEmpty(currentItem.Description) ? 
                    currentItem.Description : "No description available.";
            }
            
            // Set value
            if (valueText != null)
            {
                if (currentItem.Value > 0)
                {
                    valueText.gameObject.SetActive(true);
                    valueText.text = $"Value: {currentItem.Value:N0} gold";
                }
                else
                {
                    valueText.gameObject.SetActive(false);
                }
            }
            
            // Set weight
            if (weightText != null)
            {
                if (currentItem.Weight > 0)
                {
                    weightText.gameObject.SetActive(true);
                    weightText.text = $"Weight: {currentItem.Weight:F1} lbs";
                }
                else
                {
                    weightText.gameObject.SetActive(false);
                }
            }
            
            // Set quantity for stackable items
            if (quantityText != null)
            {
                if (currentItem.IsStackable && currentItem.Quantity > 1)
                {
                    quantityText.gameObject.SetActive(true);
                    quantityText.text = $"Quantity: {currentItem.Quantity}";
                }
                else
                {
                    quantityText.gameObject.SetActive(false);
                }
            }
        }
        
        private void UpdateProperties()
        {
            ClearDynamicProperties();
            
            if (propertiesContainer == null || propertyPrefab == null || currentItem.Properties == null)
                return;
            
            // Create property elements for non-stat properties
            foreach (var property in currentItem.Properties)
            {
                if (!IsStatProperty(property.Key))
                {
                    GameObject propertyGO = Instantiate(propertyPrefab, propertiesContainer);
                    var propertyText = propertyGO.GetComponent<TextMeshProUGUI>();
                    if (propertyText != null)
                    {
                        propertyText.text = $"{property.Key}: {property.Value}";
                    }
                    dynamicPropertyElements.Add(propertyGO);
                }
            }
        }
        
        private void UpdateUsability()
        {
            if (usabilityText == null) return;
            
            var usabilityInfo = new List<string>();
            
            if (currentItem.IsUsable)
                usabilityInfo.Add("Right-click to use");
            if (currentItem.IsEquippable)
                usabilityInfo.Add("Double-click to equip");
            if (currentItem.IsStackable)
                usabilityInfo.Add("Stackable");
            if (currentItem.IsQuestItem)
                usabilityInfo.Add("Quest Item");
            
            if (usabilityInfo.Count > 0)
            {
                usabilityText.gameObject.SetActive(true);
                usabilityText.text = string.Join(" • ", usabilityInfo);
            }
            else
            {
                usabilityText.gameObject.SetActive(false);
            }
            
            // Update requirements
            if (requirementsText != null)
            {
                // Placeholder for item requirements (level, class, etc.)
                requirementsText.gameObject.SetActive(false);
            }
        }
        
        private void PositionTooltip(Vector2 screenPosition)
        {
            if (tooltipRect == null || parentCanvas == null) return;
            
            // Convert screen position to canvas position
            Vector2 canvasPosition;
            RectTransformUtility.ScreenPointToLocalPointInRectangle(
                parentCanvas.transform as RectTransform,
                screenPosition + offset,
                uiCamera,
                out canvasPosition);
            
            // Get canvas and tooltip dimensions
            Rect canvasRect = (parentCanvas.transform as RectTransform).rect;
            Vector2 tooltipSize = tooltipRect.sizeDelta;
            
            // Clamp position to keep tooltip within canvas bounds
            float clampedX = Mathf.Clamp(canvasPosition.x, 
                -canvasRect.width * 0.5f, 
                canvasRect.width * 0.5f - tooltipSize.x);
            
            float clampedY = Mathf.Clamp(canvasPosition.y, 
                -canvasRect.height * 0.5f + tooltipSize.y, 
                canvasRect.height * 0.5f);
            
            // Set tooltip position
            tooltipRect.anchoredPosition = new Vector2(clampedX, clampedY);
        }
        
        private void ClearDynamicStats()
        {
            foreach (var element in dynamicStatElements)
            {
                if (element != null)
                    DestroyImmediate(element);
            }
            dynamicStatElements.Clear();
        }
        
        private void ClearDynamicProperties()
        {
            foreach (var element in dynamicPropertyElements)
            {
                if (element != null)
                    DestroyImmediate(element);
            }
            dynamicPropertyElements.Clear();
        }
        
        private Color GetRarityColor(ItemModel item)
        {
            // Placeholder rarity system - would be enhanced with actual rarity enum
            switch (item.Type)
            {
                case ItemType.Quest:
                    return rarityColors.Length > 4 ? rarityColors[4] : Color.yellow; // Legendary
                case ItemType.Treasure:
                    return rarityColors.Length > 2 ? rarityColors[2] : Color.blue; // Rare
                case ItemType.Weapon:
                case ItemType.Armor:
                    return rarityColors.Length > 1 ? rarityColors[1] : Color.green; // Uncommon
                default:
                    return rarityColors.Length > 0 ? rarityColors[0] : Color.white; // Common
            }
        }
        
        private string GetItemTypeDisplayName(ItemType type)
        {
            return type switch
            {
                ItemType.Weapon => "Weapon",
                ItemType.Armor => "Armor",
                ItemType.Consumable => "Consumable",
                ItemType.Tool => "Tool",
                ItemType.Treasure => "Treasure",
                ItemType.Quest => "Quest Item",
                ItemType.Material => "Material",
                ItemType.Container => "Container",
                _ => type.ToString()
            };
        }
        
        private string FormatBonus(int bonus)
        {
            return bonus >= 0 ? $"+{bonus}" : bonus.ToString();
        }
        
        private bool IsStatProperty(string propertyKey)
        {
            // Define which properties are considered stats vs general properties
            var statKeys = new HashSet<string>
            {
                "damage", "armor", "resistance", "bonus", "enhancement",
                "critical", "speed", "range", "durability"
            };
            
            return statKeys.Contains(propertyKey.ToLower());
        }
        
        #region Public Properties
        
        public bool IsVisible => isVisible;
        public ItemModel CurrentItem => currentItem;
        
        #endregion
    }
} 