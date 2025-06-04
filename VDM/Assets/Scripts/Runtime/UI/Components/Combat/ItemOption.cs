using System;
using UnityEngine;
using UnityEngine.UI;
using TMPro;
using VDM.DTOs.Game.Character;

namespace VDM.UI.Systems.Combat
{
    /// <summary>
    /// UI component for displaying and selecting item options in combat
    /// </summary>
    public class ItemOption : MonoBehaviour
    {
        [Header("Item Information")]
        [SerializeField] private Image itemIcon;
        [SerializeField] private TextMeshProUGUI itemNameText;
        [SerializeField] private TextMeshProUGUI itemTypeText;
        [SerializeField] private TextMeshProUGUI descriptionText;
        [SerializeField] private TextMeshProUGUI quantityText;
        
        [Header("Item Stats")]
        [SerializeField] private TextMeshProUGUI effectText;
        [SerializeField] private TextMeshProUGUI durationText;
        [SerializeField] private TextMeshProUGUI cooldownText;
        [SerializeField] private Transform itemPropertiesContainer;
        [SerializeField] private GameObject propertyPrefab;
        
        [Header("UI Elements")]
        [SerializeField] private Button selectButton;
        [SerializeField] private Image backgroundImage;
        [SerializeField] private Image selectionHighlight;
        [SerializeField] private Image rarityBorder;
        [SerializeField] private GameObject consumableIndicator;
        
        [Header("Visual States")]
        [SerializeField] private Color normalColor = Color.white;
        [SerializeField] private Color hoverColor = new Color(0.8f, 1f, 0.8f, 1f);
        [SerializeField] private Color selectedColor = new Color(0.6f, 1f, 0.6f, 1f);
        [SerializeField] private Color disabledColor = new Color(0.5f, 0.5f, 0.5f, 0.5f);
        [SerializeField] private Color emptyColor = new Color(1f, 0.5f, 0.5f, 1f);
        
        [Header("Animation")]
        [SerializeField] private float hoverScale = 1.02f;
        [SerializeField] private float animationDuration = 0.15f;
        [SerializeField] private LeanTweenType animationEase = LeanTweenType.easeOutQuad;
        
        // Data
        private ItemModel itemData;
        private bool isSelected = false;
        private bool isEnabled = true;
        private bool hasQuantity = true;
        private Vector3 originalScale;
        
        // Events
        private System.Action onItemSelected;
        
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
        /// Initialize the item option
        /// </summary>
        public void Initialize(ItemModel item, System.Action selectionCallback)
        {
            itemData = item;
            onItemSelected = selectionCallback;
            
            hasQuantity = item.Quantity > 0;
            
            UpdateItemDisplay();
            UpdateItemStats();
            UpdateItemProperties();
            SetEnabled(true);
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
        /// Set enabled state
        /// </summary>
        public void SetEnabled(bool enabled)
        {
            isEnabled = enabled;
            
            if (selectButton != null)
                selectButton.interactable = enabled && hasQuantity;
            
            UpdateVisualState();
        }
        
        /// <summary>
        /// Update item quantity
        /// </summary>
        public void UpdateQuantity(int quantity)
        {
            if (itemData != null)
            {
                itemData.Quantity = quantity;
                hasQuantity = quantity > 0;
                
                if (quantityText != null)
                    quantityText.text = $"x{quantity}";
                
                if (selectButton != null)
                    selectButton.interactable = isEnabled && hasQuantity;
                
                UpdateVisualState();
            }
        }
        
        private void UpdateItemDisplay()
        {
            if (itemData == null) return;
            
            // Set item name
            if (itemNameText != null)
                itemNameText.text = itemData.Name;
            
            // Set item type
            if (itemTypeText != null)
                itemTypeText.text = GetItemTypeDisplayName(itemData.Type);
            
            // Set description
            if (descriptionText != null)
                descriptionText.text = itemData.Description;
            
            // Set quantity
            if (quantityText != null)
            {
                if (itemData.IsStackable)
                {
                    quantityText.gameObject.SetActive(true);
                    quantityText.text = $"x{itemData.Quantity}";
                }
                else
                {
                    quantityText.gameObject.SetActive(false);
                }
            }
            
            // Set item icon
            if (itemIcon != null)
            {
                Sprite icon = Resources.Load<Sprite>($"ItemIcons/{itemData.Type}");
                if (icon != null)
                    itemIcon.sprite = icon;
            }
            
            // Set rarity border
            if (rarityBorder != null)
                rarityBorder.color = GetRarityColor(itemData);
            
            // Show consumable indicator
            if (consumableIndicator != null)
                consumableIndicator.SetActive(itemData.IsConsumable);
        }
        
        private void UpdateItemStats()
        {
            if (itemData == null) return;
            
            // Set effect description
            if (effectText != null)
            {
                string effect = GetItemEffect(itemData);
                effectText.text = effect;
                effectText.gameObject.SetActive(!string.IsNullOrEmpty(effect));
            }
            
            // Set duration (for effects that last)
            if (durationText != null)
            {
                string duration = GetItemDuration(itemData);
                if (!string.IsNullOrEmpty(duration))
                {
                    durationText.gameObject.SetActive(true);
                    durationText.text = $"Duration: {duration}";
                }
                else
                {
                    durationText.gameObject.SetActive(false);
                }
            }
            
            // Set cooldown (if applicable)
            if (cooldownText != null)
            {
                string cooldown = GetItemCooldown(itemData);
                if (!string.IsNullOrEmpty(cooldown))
                {
                    cooldownText.gameObject.SetActive(true);
                    cooldownText.text = $"Cooldown: {cooldown}";
                }
                else
                {
                    cooldownText.gameObject.SetActive(false);
                }
            }
        }
        
        private void UpdateItemProperties()
        {
            if (itemPropertiesContainer == null || itemData?.Properties == null) return;
            
            // Clear existing properties
            foreach (Transform child in itemPropertiesContainer)
            {
                Destroy(child.gameObject);
            }
            
            // Add item properties
            foreach (var property in itemData.Properties)
            {
                if (IsDisplayableProperty(property.Key))
                {
                    CreatePropertyElement(property.Key, property.Value.ToString());
                }
            }
        }
        
        private void CreatePropertyElement(string propertyName, string propertyValue)
        {
            if (propertyPrefab == null) return;
            
            GameObject propertyElement = Instantiate(propertyPrefab, itemPropertiesContainer);
            var propertyText = propertyElement.GetComponentInChildren<TextMeshProUGUI>();
            
            if (propertyText != null)
            {
                propertyText.text = $"{propertyName}: {propertyValue}";
                propertyText.color = GetPropertyColor(propertyName);
            }
        }
        
        private void UpdateVisualState()
        {
            Color targetColor = normalColor;
            
            if (!isEnabled)
            {
                targetColor = disabledColor;
            }
            else if (!hasQuantity)
            {
                targetColor = emptyColor;
            }
            else if (isSelected)
            {
                targetColor = selectedColor;
            }
            
            // Update background color
            if (backgroundImage != null)
                backgroundImage.color = targetColor;
            
            // Update selection highlight
            if (selectionHighlight != null)
                selectionHighlight.gameObject.SetActive(isSelected);
        }
        
        private void AnimateSelection()
        {
            LeanTween.cancel(gameObject);
            LeanTween.scale(gameObject, originalScale * 1.05f, animationDuration)
                .setEase(LeanTweenType.easeOutBack)
                .setLoopPingPong(1);
        }
        
        private void OnSelectClicked()
        {
            if (isEnabled && hasQuantity && itemData != null)
            {
                onItemSelected?.Invoke();
            }
        }
        
        public void OnPointerEnter()
        {
            if (isEnabled && hasQuantity)
            {
                if (backgroundImage != null && !isSelected)
                    backgroundImage.color = hoverColor;
                
                LeanTween.scale(gameObject, originalScale * hoverScale, animationDuration)
                    .setEase(animationEase);
            }
        }
        
        public void OnPointerExit()
        {
            if (isEnabled)
            {
                if (backgroundImage != null && !isSelected)
                {
                    Color targetColor = hasQuantity ? normalColor : emptyColor;
                    backgroundImage.color = targetColor;
                }
                
                LeanTween.scale(gameObject, originalScale, animationDuration)
                    .setEase(animationEase);
            }
        }
        
        #region Helper Methods
        
        private string GetItemTypeDisplayName(ItemType type)
        {
            return type switch
            {
                ItemType.Consumable => "Consumable",
                ItemType.Tool => "Tool",
                ItemType.Material => "Material",
                ItemType.Treasure => "Treasure",
                ItemType.Quest => "Quest Item",
                ItemType.Container => "Container",
                _ => type.ToString()
            };
        }
        
        private string GetItemEffect(ItemModel item)
        {
            // Determine item effect based on type and properties
            return item.Type switch
            {
                ItemType.Consumable when item.Name.ToLower().Contains("potion") => GetPotionEffect(item),
                ItemType.Consumable when item.Name.ToLower().Contains("scroll") => "Casts spell when used",
                ItemType.Tool when item.Name.ToLower().Contains("bomb") => "Explosive damage in area",
                ItemType.Tool when item.Name.ToLower().Contains("trap") => "Places trap for enemies",
                _ => ""
            };
        }
        
        private string GetPotionEffect(ItemModel potion)
        {
            string name = potion.Name.ToLower();
            if (name.Contains("health") || name.Contains("healing"))
                return "Restores health";
            if (name.Contains("mana") || name.Contains("magic"))
                return "Restores mana";
            if (name.Contains("strength"))
                return "Increases strength";
            if (name.Contains("speed"))
                return "Increases movement speed";
            if (name.Contains("poison"))
                return "Causes poison damage";
            
            return "Beneficial effect";
        }
        
        private string GetItemDuration(ItemModel item)
        {
            // Check properties for duration
            if (item.Properties?.ContainsKey("Duration") == true)
                return item.Properties["Duration"].ToString();
            
            // Default durations based on item type
            return item.Type switch
            {
                ItemType.Consumable when item.Name.ToLower().Contains("potion") => "Instant",
                ItemType.Tool when item.Name.ToLower().Contains("bomb") => "Instant",
                _ => ""
            };
        }
        
        private string GetItemCooldown(ItemModel item)
        {
            // Check properties for cooldown
            if (item.Properties?.ContainsKey("Cooldown") == true)
                return item.Properties["Cooldown"].ToString();
            
            // Some items have inherent cooldowns
            if (item.Name.ToLower().Contains("bomb") || item.Name.ToLower().Contains("explosive"))
                return "1 turn";
            
            return "";
        }
        
        private Color GetRarityColor(ItemModel item)
        {
            // Determine rarity color based on item type and value
            if (item.Type == ItemType.Quest)
                return Color.yellow;
            if (item.Value > 1000)
                return Color.magenta; // Legendary
            if (item.Value > 500)
                return Color.blue;    // Rare
            if (item.Value > 100)
                return Color.green;   // Uncommon
            
            return Color.white; // Common
        }
        
        private Color GetPropertyColor(string propertyName)
        {
            return propertyName.ToLower() switch
            {
                "healing" => Color.green,
                "damage" => Color.red,
                "buff" => Color.blue,
                "debuff" => Color.yellow,
                "magical" => Color.magenta,
                _ => Color.white
            };
        }
        
        private bool IsDisplayableProperty(string propertyKey)
        {
            // Filter out internal properties that shouldn't be shown to players
            var hiddenProperties = new[] { "Id", "InternalFlag", "SystemData" };
            return !System.Array.Exists(hiddenProperties, prop => 
                propertyKey.Contains(prop, StringComparison.OrdinalIgnoreCase));
        }
        
        #endregion
        
        #region Public Properties
        
        public ItemModel ItemData => itemData;
        public bool IsSelected => isSelected;
        public bool IsEnabled => isEnabled;
        public bool HasQuantity => hasQuantity;
        
        #endregion
    }
} 