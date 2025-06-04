using System;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.EventSystems;
using TMPro;
using VDM.DTOs.Economic.Equipment;

namespace VDM.UI.Systems.Equipment
{
    /// <summary>
    /// Display component for individual equipment items with drag-and-drop support
    /// </summary>
    public class EquipmentItemDisplay : MonoBehaviour, IDragHandler, IBeginDragHandler, IEndDragHandler, IPointerClickHandler, IPointerEnterHandler, IPointerExitHandler
    {
        [Header("Item Visuals")]
        [SerializeField] private Image itemIcon;
        [SerializeField] private TextMeshProUGUI itemNameText;
        [SerializeField] private TextMeshProUGUI itemTypeText;
        [SerializeField] private TextMeshProUGUI itemLevelText;
        [SerializeField] private Image rarityBorder;
        [SerializeField] private Image backgroundImage;
        
        [Header("Item Information")]
        [SerializeField] private GameObject valuePanel;
        [SerializeField] private TextMeshProUGUI valueText;
        [SerializeField] private GameObject levelRequirementPanel;
        [SerializeField] private TextMeshProUGUI levelRequirementText;
        [SerializeField] private GameObject weightPanel;
        [SerializeField] private TextMeshProUGUI weightText;
        
        [Header("Item States")]
        [SerializeField] private GameObject equippedIndicator;
        [SerializeField] private GameObject setItemIndicator;
        [SerializeField] private GameObject enchantedIndicator;
        [SerializeField] private GameObject newItemIndicator;
        [SerializeField] private GameObject comparisonArrow;
        
        [Header("Durability")]
        [SerializeField] private GameObject durabilityPanel;
        [SerializeField] private Slider durabilitySlider;
        [SerializeField] private Image durabilityFill;
        
        [Header("Visual States")]
        [SerializeField] private Color normalColor = Color.white;
        [SerializeField] private Color highlightColor = new Color(1f, 1f, 0.8f, 1f);
        [SerializeField] private Color selectedColor = new Color(0.8f, 1f, 0.8f, 1f);
        [SerializeField] private Color dragColor = new Color(1f, 1f, 1f, 0.7f);
        [SerializeField] private Color equippedColor = new Color(0.9f, 0.9f, 0.9f, 1f);
        
        [Header("Animation")]
        [SerializeField] private float hoverScale = 1.05f;
        [SerializeField] private float animationDuration = 0.1f;
        [SerializeField] private LeanTweenType animationEase = LeanTweenType.easeOutQuad;
        
        [Header("Drag Settings")]
        [SerializeField] private float dragSensitivity = 10f;
        [SerializeField] private bool returnToPositionOnFailedDrop = true;
        
        // Data
        private EquipmentItemDTO itemData;
        private bool isSelected = false;
        private bool isHighlighted = false;
        private bool isDragging = false;
        private bool isEquipped = false;
        
        // Events
        private System.Action<EquipmentItemDTO> onItemSelected;
        private System.Action<EquipmentItemDTO> onItemDoubleClicked;
        
        // Drag variables
        private Vector3 originalPosition;
        private Vector3 originalScale;
        private Transform originalParent;
        private Canvas dragCanvas;
        private GraphicRaycaster dragRaycaster;
        private CanvasGroup canvasGroup;
        private float lastClickTime = 0f;
        private const float doubleClickTime = 0.3f;
        
        private void Awake()
        {
            originalScale = transform.localScale;
            
            // Get or add CanvasGroup for drag transparency
            canvasGroup = GetComponent<CanvasGroup>();
            if (canvasGroup == null)
                canvasGroup = gameObject.AddComponent<CanvasGroup>();
            
            // Initially hide optional panels
            HideOptionalPanels();
        }
        
        /// <summary>
        /// Initialize the item display with item data and callbacks
        /// </summary>
        public void Initialize(EquipmentItemDTO item, System.Action<EquipmentItemDTO> selectedCallback, System.Action<EquipmentItemDTO> doubleClickCallback)
        {
            itemData = item;
            onItemSelected = selectedCallback;
            onItemDoubleClicked = doubleClickCallback;
            
            UpdateItemDisplay();
        }
        
        /// <summary>
        /// Set the equipped state of this item
        /// </summary>
        public void SetEquipped(bool equipped)
        {
            isEquipped = equipped;
            UpdateItemDisplay();
        }
        
        /// <summary>
        /// Set the selected state of this item
        /// </summary>
        public void SetSelected(bool selected)
        {
            isSelected = selected;
            UpdateVisualState();
        }
        
        /// <summary>
        /// Get the item data
        /// </summary>
        public EquipmentItemDTO GetItem()
        {
            return itemData;
        }
        
        #region Event Handlers
        
        public void OnPointerClick(PointerEventData eventData)
        {
            float timeSinceLastClick = Time.time - lastClickTime;
            lastClickTime = Time.time;
            
            if (timeSinceLastClick <= doubleClickTime)
            {
                // Double click
                onItemDoubleClicked?.Invoke(itemData);
            }
            else
            {
                // Single click
                onItemSelected?.Invoke(itemData);
            }
        }
        
        public void OnPointerEnter(PointerEventData eventData)
        {
            if (!isDragging)
            {
                SetHighlighted(true);
                AnimateHover(true);
            }
        }
        
        public void OnPointerExit(PointerEventData eventData)
        {
            if (!isDragging)
            {
                SetHighlighted(false);
                AnimateHover(false);
            }
        }
        
        public void OnBeginDrag(PointerEventData eventData)
        {
            isDragging = true;
            originalPosition = transform.position;
            originalParent = transform.parent;
            
            // Move to drag canvas
            SetupDragCanvas();
            
            // Set transparency during drag
            canvasGroup.alpha = dragColor.a;
            canvasGroup.blocksRaycasts = false;
            
            // Visual feedback
            UpdateVisualState();
            
            // Animate drag start
            LeanTween.scale(gameObject, originalScale * 0.9f, animationDuration)
                .setEase(animationEase);
        }
        
        public void OnDrag(PointerEventData eventData)
        {
            if (isDragging)
            {
                transform.position = eventData.position;
            }
        }
        
        public void OnEndDrag(PointerEventData eventData)
        {
            isDragging = false;
            
            // Check if dropped on a valid target
            bool droppedSuccessfully = CheckDropTarget(eventData);
            
            if (!droppedSuccessfully && returnToPositionOnFailedDrop)
            {
                // Return to original position
                ReturnToOriginalPosition();
            }
            
            // Restore transparency and interaction
            canvasGroup.alpha = 1f;
            canvasGroup.blocksRaycasts = true;
            
            // Return to original parent if not successfully dropped
            if (!droppedSuccessfully)
            {
                transform.SetParent(originalParent);
            }
            
            // Update visual state
            UpdateVisualState();
            
            // Animate drag end
            LeanTween.scale(gameObject, originalScale, animationDuration)
                .setEase(animationEase);
        }
        
        #endregion
        
        #region Visual Updates
        
        private void UpdateItemDisplay()
        {
            if (itemData == null) return;
            
            // Set item icon
            if (itemIcon != null && !string.IsNullOrEmpty(itemData.IconId))
            {
                Sprite icon = Resources.Load<Sprite>(itemData.IconId);
                if (icon != null)
                    itemIcon.sprite = icon;
            }
            
            // Set item name
            if (itemNameText != null)
                itemNameText.text = itemData.Name;
            
            // Set item type
            if (itemTypeText != null)
                itemTypeText.text = $"{itemData.EquipmentType}";
            
            // Set item level
            if (itemLevelText != null)
                itemLevelText.text = $"Lvl {itemData.LevelRequirement}";
            
            // Set rarity border
            if (rarityBorder != null)
                rarityBorder.color = GetRarityColor(itemData.Rarity);
            
            // Update value display
            if (valuePanel != null && valueText != null)
            {
                valuePanel.SetActive(itemData.Value > 0);
                valueText.text = $"{itemData.Value}g";
            }
            
            // Update level requirement
            if (levelRequirementPanel != null && levelRequirementText != null)
            {
                levelRequirementPanel.SetActive(itemData.LevelRequirement > 1);
                levelRequirementText.text = $"Req: {itemData.LevelRequirement}";
            }
            
            // Update weight
            if (weightPanel != null && weightText != null)
            {
                weightPanel.SetActive(itemData.Weight > 0);
                weightText.text = $"{itemData.Weight:F1} lbs";
            }
            
            // Update state indicators
            UpdateStateIndicators();
            UpdateDurabilityDisplay();
            UpdateVisualState();
        }
        
        private void UpdateStateIndicators()
        {
            if (itemData == null) return;
            
            // Equipped indicator
            if (equippedIndicator != null)
                equippedIndicator.SetActive(isEquipped);
            
            // Set item indicator (placeholder logic)
            bool isSetItem = !string.IsNullOrEmpty(itemData.Material);
            if (setItemIndicator != null)
                setItemIndicator.SetActive(isSetItem);
            
            // Enchanted indicator
            bool isEnchanted = itemData.UsedEnchantmentSlots > 0;
            if (enchantedIndicator != null)
                enchantedIndicator.SetActive(isEnchanted);
            
            // New item indicator (placeholder logic)
            if (newItemIndicator != null)
                newItemIndicator.SetActive(false); // Would be based on item acquisition time
            
            // Comparison arrow (shown when comparing)
            if (comparisonArrow != null)
                comparisonArrow.SetActive(false);
        }
        
        private void UpdateDurabilityDisplay()
        {
            if (itemData == null)
            {
                if (durabilityPanel != null)
                    durabilityPanel.SetActive(false);
                return;
            }
            
            // Check if item has durability (placeholder logic)
            bool hasDurability = itemData.EquipmentType == EquipmentType.Weapon || itemData.EquipmentType == EquipmentType.Armor;
            
            if (durabilityPanel != null)
                durabilityPanel.SetActive(hasDurability);
            
            if (hasDurability && durabilitySlider != null)
            {
                // Placeholder durability value
                float durabilityPercentage = UnityEngine.Random.Range(0.5f, 1f);
                durabilitySlider.value = durabilityPercentage;
                
                if (durabilityFill != null)
                {
                    Color durabilityColor = Color.green;
                    if (durabilityPercentage < 0.25f)
                        durabilityColor = Color.red;
                    else if (durabilityPercentage < 0.75f)
                        durabilityColor = Color.yellow;
                    
                    durabilityFill.color = durabilityColor;
                }
            }
        }
        
        private void UpdateVisualState()
        {
            Color targetColor = normalColor;
            
            if (isDragging)
            {
                targetColor = dragColor;
            }
            else if (isSelected)
            {
                targetColor = selectedColor;
            }
            else if (isHighlighted)
            {
                targetColor = highlightColor;
            }
            else if (isEquipped)
            {
                targetColor = equippedColor;
            }
            
            if (backgroundImage != null)
                backgroundImage.color = targetColor;
        }
        
        private void SetHighlighted(bool highlighted)
        {
            isHighlighted = highlighted;
            UpdateVisualState();
        }
        
        #endregion
        
        #region Animation
        
        private void AnimateHover(bool hovering)
        {
            LeanTween.cancel(gameObject);
            
            Vector3 targetScale = hovering ? originalScale * hoverScale : originalScale;
            
            LeanTween.scale(gameObject, targetScale, animationDuration)
                .setEase(animationEase);
        }
        
        private void ReturnToOriginalPosition()
        {
            LeanTween.move(gameObject, originalPosition, animationDuration * 2f)
                .setEase(LeanTweenType.easeOutBack);
        }
        
        #endregion
        
        #region Drag Support
        
        private void SetupDragCanvas()
        {
            // Find or create a canvas for dragging
            dragCanvas = FindDragCanvas();
            if (dragCanvas != null)
            {
                transform.SetParent(dragCanvas.transform);
                transform.SetAsLastSibling(); // Ensure it's on top
            }
        }
        
        private Canvas FindDragCanvas()
        {
            // Look for a canvas marked for dragging
            Canvas[] canvases = FindObjectsOfType<Canvas>();
            foreach (var canvas in canvases)
            {
                if (canvas.sortingOrder > 100) // Higher sort order for drag operations
                    return canvas;
            }
            
            // Use the first found canvas as fallback
            return canvases.Length > 0 ? canvases[0] : null;
        }
        
        private bool CheckDropTarget(PointerEventData eventData)
        {
            // Check if we're over a valid drop target
            if (eventData.pointerEnter != null)
            {
                var dropTarget = eventData.pointerEnter.GetComponent<EquipmentSlotDisplay>();
                if (dropTarget != null)
                {
                    // The slot will handle the actual drop logic
                    return true;
                }
            }
            
            return false;
        }
        
        #endregion
        
        #region Utility Methods
        
        private void HideOptionalPanels()
        {
            if (valuePanel != null)
                valuePanel.SetActive(false);
            if (levelRequirementPanel != null)
                levelRequirementPanel.SetActive(false);
            if (weightPanel != null)
                weightPanel.SetActive(false);
            if (durabilityPanel != null)
                durabilityPanel.SetActive(false);
            if (equippedIndicator != null)
                equippedIndicator.SetActive(false);
            if (setItemIndicator != null)
                setItemIndicator.SetActive(false);
            if (enchantedIndicator != null)
                enchantedIndicator.SetActive(false);
            if (newItemIndicator != null)
                newItemIndicator.SetActive(false);
            if (comparisonArrow != null)
                comparisonArrow.SetActive(false);
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
        
        public EquipmentItemDTO ItemData => itemData;
        public bool IsSelected => isSelected;
        public bool IsHighlighted => isHighlighted;
        public bool IsDragging => isDragging;
        public bool IsEquipped => isEquipped;
        
        #endregion
    }
} 