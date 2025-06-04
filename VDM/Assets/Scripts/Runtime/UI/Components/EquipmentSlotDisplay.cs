using System;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.EventSystems;
using TMPro;
using VDM.DTOs.Economic.Equipment;

namespace VDM.UI.Systems.Equipment
{
    /// <summary>
    /// Individual equipment slot with drag-and-drop support and visual feedback
    /// </summary>
    public class EquipmentSlotDisplay : MonoBehaviour, IDropHandler, IPointerClickHandler, IPointerEnterHandler, IPointerExitHandler
    {
        [Header("Slot Appearance")]
        [SerializeField] private Image slotIcon;
        [SerializeField] private Image slotBackground;
        [SerializeField] private Image itemIcon;
        [SerializeField] private TextMeshProUGUI slotNameText;
        [SerializeField] private GameObject emptySlotIndicator;
        [SerializeField] private GameObject occupiedSlotIndicator;
        
        [Header("Visual States")]
        [SerializeField] private Color normalColor = Color.white;
        [SerializeField] private Color highlightColor = Color.yellow;
        [SerializeField] private Color selectedColor = Color.green;
        [SerializeField] private Color canDropColor = Color.cyan;
        [SerializeField] private Color cannotDropColor = Color.red;
        [SerializeField] private Color emptySlotColor = Color.gray;
        
        [Header("Durability Display")]
        [SerializeField] private GameObject durabilityPanel;
        [SerializeField] private Slider durabilitySlider;
        [SerializeField] private Image durabilityFill;
        [SerializeField] private Color durabilityHighColor = Color.green;
        [SerializeField] private Color durabilityMediumColor = Color.yellow;
        [SerializeField] private Color durabilityLowColor = Color.red;
        
        [Header("Enhancement Indicators")]
        [SerializeField] private GameObject enchantedIndicator;
        [SerializeField] private GameObject setItemIndicator;
        [SerializeField] private GameObject rarityBorder;
        [SerializeField] private TextMeshProUGUI enhancementLevelText;
        
        [Header("Animation")]
        [SerializeField] private float animationDuration = 0.2f;
        [SerializeField] private AnimationCurve scaleCurve = AnimationCurve.EaseInOut(0, 1, 1, 1.1f);
        
        // Data
        private EquipmentSlot slotType;
        private EquipmentItemDTO equippedItem;
        private bool isSelected = false;
        private bool isHighlighted = false;
        private bool isDragTarget = false;
        
        // Events
        private System.Action<EquipmentSlot> onSlotSelected;
        private System.Action<EquipmentSlot, EquipmentItemDTO> onItemDropped;
        
        // Animation
        private Vector3 originalScale;
        
        private void Awake()
        {
            originalScale = transform.localScale;
            
            // Initially hide item-specific UI
            if (itemIcon != null)
                itemIcon.gameObject.SetActive(false);
            if (durabilityPanel != null)
                durabilityPanel.SetActive(false);
            if (enchantedIndicator != null)
                enchantedIndicator.SetActive(false);
            if (setItemIndicator != null)
                setItemIndicator.SetActive(false);
            if (rarityBorder != null)
                rarityBorder.SetActive(false);
        }
        
        /// <summary>
        /// Initialize the equipment slot
        /// </summary>
        public void Initialize(EquipmentSlot slot, System.Action<EquipmentSlot> slotSelectedCallback, System.Action<EquipmentSlot, EquipmentItemDTO> itemDroppedCallback)
        {
            slotType = slot;
            onSlotSelected = slotSelectedCallback;
            onItemDropped = itemDroppedCallback;
            
            // Set slot name and icon
            if (slotNameText != null)
                slotNameText.text = GetSlotDisplayName(slot);
            
            if (slotIcon != null)
                slotIcon.sprite = GetSlotIcon(slot);
            
            UpdateSlotVisuals();
        }
        
        /// <summary>
        /// Set an equipped item in this slot
        /// </summary>
        public void SetEquippedItem(EquipmentItemDTO item)
        {
            equippedItem = item;
            UpdateSlotVisuals();
            UpdateItemVisuals();
            UpdateDurabilityDisplay();
            UpdateEnhancementIndicators();
        }
        
        /// <summary>
        /// Clear the slot of any equipped item
        /// </summary>
        public void ClearSlot()
        {
            equippedItem = null;
            UpdateSlotVisuals();
            HideItemVisuals();
        }
        
        /// <summary>
        /// Set the selected state of this slot
        /// </summary>
        public void SetSelected(bool selected)
        {
            isSelected = selected;
            UpdateSlotVisuals();
            
            if (selected)
            {
                AnimateSelection();
            }
        }
        
        /// <summary>
        /// Set the highlight state of this slot
        /// </summary>
        public void SetHighlighted(bool highlighted)
        {
            isHighlighted = highlighted;
            UpdateSlotVisuals();
        }
        
        #region Event Handlers
        
        public void OnPointerClick(PointerEventData eventData)
        {
            onSlotSelected?.Invoke(slotType);
        }
        
        public void OnPointerEnter(PointerEventData eventData)
        {
            SetHighlighted(true);
            
            // Show tooltip if there's an equipped item
            if (equippedItem != null)
            {
                ShowItemTooltip();
            }
        }
        
        public void OnPointerExit(PointerEventData eventData)
        {
            SetHighlighted(false);
            HideItemTooltip();
        }
        
        public void OnDrop(PointerEventData eventData)
        {
            // Get the dragged item
            var draggedItem = GetDraggedItem(eventData);
            if (draggedItem != null && CanAcceptItem(draggedItem))
            {
                onItemDropped?.Invoke(slotType, draggedItem);
                AnimateItemDrop();
            }
            
            isDragTarget = false;
            UpdateSlotVisuals();
        }
        
        #endregion
        
        #region Visual Updates
        
        private void UpdateSlotVisuals()
        {
            Color targetColor = normalColor;
            
            if (isDragTarget)
            {
                // Check if we can accept the current drag
                var draggedItem = GetCurrentDraggedItem();
                targetColor = CanAcceptItem(draggedItem) ? canDropColor : cannotDropColor;
            }
            else if (isSelected)
            {
                targetColor = selectedColor;
            }
            else if (isHighlighted)
            {
                targetColor = highlightColor;
            }
            else if (equippedItem == null)
            {
                targetColor = emptySlotColor;
            }
            
            if (slotBackground != null)
                slotBackground.color = targetColor;
            
            // Show/hide empty slot indicator
            if (emptySlotIndicator != null)
                emptySlotIndicator.SetActive(equippedItem == null);
            if (occupiedSlotIndicator != null)
                occupiedSlotIndicator.SetActive(equippedItem != null);
        }
        
        private void UpdateItemVisuals()
        {
            if (equippedItem == null)
            {
                HideItemVisuals();
                return;
            }
            
            // Show item icon
            if (itemIcon != null)
            {
                itemIcon.gameObject.SetActive(true);
                
                // Load item icon sprite
                if (!string.IsNullOrEmpty(equippedItem.IconId))
                {
                    Sprite itemSprite = Resources.Load<Sprite>(equippedItem.IconId);
                    if (itemSprite != null)
                        itemIcon.sprite = itemSprite;
                }
            }
            
            // Update rarity border
            if (rarityBorder != null)
            {
                rarityBorder.SetActive(true);
                Image borderImage = rarityBorder.GetComponent<Image>();
                if (borderImage != null)
                {
                    borderImage.color = GetRarityColor(equippedItem.Rarity);
                }
            }
        }
        
        private void HideItemVisuals()
        {
            if (itemIcon != null)
                itemIcon.gameObject.SetActive(false);
            if (durabilityPanel != null)
                durabilityPanel.SetActive(false);
            if (enchantedIndicator != null)
                enchantedIndicator.SetActive(false);
            if (setItemIndicator != null)
                setItemIndicator.SetActive(false);
            if (rarityBorder != null)
                rarityBorder.SetActive(false);
        }
        
        private void UpdateDurabilityDisplay()
        {
            if (equippedItem == null || durabilityPanel == null)
            {
                if (durabilityPanel != null)
                    durabilityPanel.SetActive(false);
                return;
            }
            
            // Check if this item has durability information
            // This would be implemented based on the actual durability system
            bool hasDurability = true; // Placeholder
            float durabilityPercentage = 0.75f; // Placeholder
            
            if (hasDurability)
            {
                durabilityPanel.SetActive(true);
                
                if (durabilitySlider != null)
                    durabilitySlider.value = durabilityPercentage;
                
                if (durabilityFill != null)
                {
                    Color durabilityColor = durabilityHighColor;
                    if (durabilityPercentage < 0.25f)
                        durabilityColor = durabilityLowColor;
                    else if (durabilityPercentage < 0.75f)
                        durabilityColor = durabilityMediumColor;
                    
                    durabilityFill.color = durabilityColor;
                }
            }
            else
            {
                durabilityPanel.SetActive(false);
            }
        }
        
        private void UpdateEnhancementIndicators()
        {
            if (equippedItem == null)
                return;
            
            // Show enchantment indicator
            bool isEnchanted = equippedItem.UsedEnchantmentSlots > 0;
            if (enchantedIndicator != null)
                enchantedIndicator.SetActive(isEnchanted);
            
            // Show set item indicator
            bool isSetItem = !string.IsNullOrEmpty(equippedItem.Material); // Placeholder for set detection
            if (setItemIndicator != null)
                setItemIndicator.SetActive(isSetItem);
            
            // Show enhancement level
            if (enhancementLevelText != null)
            {
                int enhancementLevel = equippedItem.UsedEnchantmentSlots;
                if (enhancementLevel > 0)
                {
                    enhancementLevelText.gameObject.SetActive(true);
                    enhancementLevelText.text = $"+{enhancementLevel}";
                }
                else
                {
                    enhancementLevelText.gameObject.SetActive(false);
                }
            }
        }
        
        #endregion
        
        #region Animations
        
        private void AnimateSelection()
        {
            LeanTween.cancel(gameObject);
            LeanTween.scale(gameObject, originalScale * 1.1f, animationDuration)
                .setEase(scaleCurve)
                .setLoopPingPong(1);
        }
        
        private void AnimateItemDrop()
        {
            LeanTween.cancel(gameObject);
            LeanTween.scale(gameObject, originalScale * 1.2f, animationDuration * 0.5f)
                .setEase(LeanTweenType.easeOutBack)
                .setOnComplete(() => {
                    LeanTween.scale(gameObject, originalScale, animationDuration * 0.5f)
                        .setEase(LeanTweenType.easeInBack);
                });
        }
        
        #endregion
        
        #region Drag and Drop Support
        
        private EquipmentItemDTO GetDraggedItem(PointerEventData eventData)
        {
            // Get the item being dragged from the drag source
            var draggedObject = eventData.pointerDrag;
            if (draggedObject != null)
            {
                var itemDisplay = draggedObject.GetComponent<EquipmentItemDisplay>();
                if (itemDisplay != null)
                {
                    return itemDisplay.GetItem();
                }
            }
            return null;
        }
        
        private EquipmentItemDTO GetCurrentDraggedItem()
        {
            // This would get the currently dragged item if any
            // Implementation depends on the drag system
            return null;
        }
        
        private bool CanAcceptItem(EquipmentItemDTO item)
        {
            if (item == null)
                return false;
            
            // Check if the item can be equipped in this slot
            return item.Slot == slotType;
        }
        
        #endregion
        
        #region Tooltip Support
        
        private void ShowItemTooltip()
        {
            if (equippedItem == null)
                return;
            
            // This would show a tooltip with item details
            // Implementation would depend on the tooltip system
            Debug.Log($"Showing tooltip for {equippedItem.Name}");
        }
        
        private void HideItemTooltip()
        {
            // Hide the tooltip
            Debug.Log("Hiding item tooltip");
        }
        
        #endregion
        
        #region Utility Methods
        
        private string GetSlotDisplayName(EquipmentSlot slot)
        {
            return slot switch
            {
                EquipmentSlot.Head => "Head",
                EquipmentSlot.Neck => "Neck",
                EquipmentSlot.Body => "Body",
                EquipmentSlot.MainHand => "Main Hand",
                EquipmentSlot.OffHand => "Off Hand",
                EquipmentSlot.Hands => "Hands",
                EquipmentSlot.Waist => "Waist",
                EquipmentSlot.Feet => "Feet",
                EquipmentSlot.Ring => "Ring",
                EquipmentSlot.Back => "Back",
                EquipmentSlot.Accessory => "Accessory",
                _ => slot.ToString()
            };
        }
        
        private Sprite GetSlotIcon(EquipmentSlot slot)
        {
            // Load appropriate slot icon from resources
            string iconPath = slot switch
            {
                EquipmentSlot.Head => "Icons/Slots/head_slot",
                EquipmentSlot.Neck => "Icons/Slots/neck_slot",
                EquipmentSlot.Body => "Icons/Slots/body_slot",
                EquipmentSlot.MainHand => "Icons/Slots/mainhand_slot",
                EquipmentSlot.OffHand => "Icons/Slots/offhand_slot",
                EquipmentSlot.Hands => "Icons/Slots/hands_slot",
                EquipmentSlot.Waist => "Icons/Slots/waist_slot",
                EquipmentSlot.Feet => "Icons/Slots/feet_slot",
                EquipmentSlot.Ring => "Icons/Slots/ring_slot",
                EquipmentSlot.Back => "Icons/Slots/back_slot",
                EquipmentSlot.Accessory => "Icons/Slots/accessory_slot",
                _ => "Icons/Slots/default_slot"
            };
            
            return Resources.Load<Sprite>(iconPath);
        }
        
        private Color GetRarityColor(ItemRarity rarity)
        {
            return rarity switch
            {
                ItemRarity.Common => Color.white,
                ItemRarity.Uncommon => Color.green,
                ItemRarity.Rare => Color.blue,
                ItemRarity.Epic => new Color(0.5f, 0f, 0.5f), // Purple
                ItemRarity.Legendary => Color.yellow,
                ItemRarity.Artifact => Color.red,
                _ => Color.white
            };
        }
        
        #endregion
        
        #region Public Properties
        
        public EquipmentSlot SlotType => slotType;
        public EquipmentItemDTO EquippedItem => equippedItem;
        public bool IsEmpty => equippedItem == null;
        public bool IsSelected => isSelected;
        
        #endregion
    }
} 