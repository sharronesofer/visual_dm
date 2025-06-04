using System;
using System.Collections;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.EventSystems;
using TMPro;
using VDM.DTOs.Game.Character;

namespace VDM.UI.Systems.Inventory
{
    /// <summary>
    /// Individual inventory slot with drag-and-drop support, stacking, and visual feedback
    /// </summary>
    public class InventorySlot : MonoBehaviour, IDragHandler, IBeginDragHandler, IEndDragHandler, 
        IDropHandler, IPointerClickHandler, IPointerEnterHandler, IPointerExitHandler
    {
        [Header("Slot Appearance")]
        [SerializeField] private Image slotBackground;
        [SerializeField] private Image itemIcon;
        [SerializeField] private TextMeshProUGUI quantityText;
        [SerializeField] private Image rarityBorder;
        [SerializeField] private GameObject emptySlotIndicator;
        [SerializeField] private GameObject stackableIndicator;
        
        [Header("Visual States")]
        [SerializeField] private Color normalColor = Color.white;
        [SerializeField] private Color highlightColor = new Color(1f, 1f, 0.8f, 1f);
        [SerializeField] private Color selectedColor = new Color(0.8f, 1f, 0.8f, 1f);
        [SerializeField] private Color canDropColor = Color.cyan;
        [SerializeField] private Color cannotDropColor = Color.red;
        [SerializeField] private Color emptyColor = new Color(0.7f, 0.7f, 0.7f, 0.5f);
        
        [Header("Drag Settings")]
        [SerializeField] private float dragSensitivity = 10f;
        [SerializeField] private bool returnToPositionOnFailedDrop = true;
        
        [Header("Animation")]
        [SerializeField] private float hoverScale = 1.05f;
        [SerializeField] private float animationDuration = 0.1f;
        
        // Data
        private ItemModel itemData;
        private int slotIndex;
        private bool isEmpty = true;
        private bool isSelected = false;
        private bool isHighlighted = false;
        private bool isDragging = false;
        
        // Events
        private System.Action<InventorySlot> onSlotSelected;
        private System.Action<InventorySlot> onSlotDoubleClicked;
        private System.Action<InventorySlot, InventorySlot> onItemMoved;
        private System.Action<ItemModel> onShowTooltip;
        private System.Action onHideTooltip;
        
        // Drag variables
        private Vector3 originalPosition;
        private Vector3 originalScale;
        private Transform originalParent;
        private Canvas dragCanvas;
        private CanvasGroup canvasGroup;
        private float lastClickTime = 0f;
        private const float doubleClickTime = 0.3f;
        
        // Animation coroutines
        private Coroutine currentAnimation;
        
        private void Awake()
        {
            originalScale = transform.localScale;
            
            // Get or add CanvasGroup for drag transparency
            canvasGroup = GetComponent<CanvasGroup>();
            if (canvasGroup == null)
                canvasGroup = gameObject.AddComponent<CanvasGroup>();
            
            UpdateVisualState();
        }
        
        /// <summary>
        /// Initialize the inventory slot
        /// </summary>
        public void Initialize(int index, System.Action<InventorySlot> selectedCallback, 
            System.Action<InventorySlot> doubleClickCallback, 
            System.Action<InventorySlot, InventorySlot> itemMovedCallback,
            System.Action<ItemModel> showTooltipCallback,
            System.Action hideTooltipCallback)
        {
            slotIndex = index;
            onSlotSelected = selectedCallback;
            onSlotDoubleClicked = doubleClickCallback;
            onItemMoved = itemMovedCallback;
            onShowTooltip = showTooltipCallback;
            onHideTooltip = hideTooltipCallback;
            
            SetItem(null);
        }
        
        /// <summary>
        /// Set an item in this slot
        /// </summary>
        public void SetItem(ItemModel item)
        {
            itemData = item;
            isEmpty = item == null;
            
            UpdateItemDisplay();
            UpdateVisualState();
        }
        
        /// <summary>
        /// Set the selected state of this slot
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
        /// Get the item in this slot
        /// </summary>
        public ItemModel GetItem()
        {
            return itemData;
        }
        
        /// <summary>
        /// Check if this slot is empty
        /// </summary>
        public bool IsEmpty()
        {
            return isEmpty;
        }
        
        /// <summary>
        /// Check if this slot can accept an item (for stacking or empty slot)
        /// </summary>
        public bool CanAcceptItem(ItemModel item)
        {
            if (item == null) return false;
            
            // If empty, can accept any item
            if (isEmpty) return true;
            
            // If same item and stackable, can accept
            if (itemData != null && item.Id == itemData.Id && item.IsStackable)
                return true;
            
            return false;
        }
        
        #region Event Handlers
        
        public void OnPointerClick(PointerEventData eventData)
        {
            float timeSinceLastClick = Time.time - lastClickTime;
            lastClickTime = Time.time;
            
            if (timeSinceLastClick <= doubleClickTime)
            {
                // Double click
                onSlotDoubleClicked?.Invoke(this);
            }
            else
            {
                // Single click
                onSlotSelected?.Invoke(this);
            }
        }
        
        public void OnPointerEnter(PointerEventData eventData)
        {
            if (!isDragging)
            {
                SetHighlighted(true);
                AnimateHover(true);
                
                // Show tooltip if there's an item
                if (itemData != null)
                {
                    onShowTooltip?.Invoke(itemData);
                }
            }
        }
        
        public void OnPointerExit(PointerEventData eventData)
        {
            if (!isDragging)
            {
                SetHighlighted(false);
                AnimateHover(false);
                onHideTooltip?.Invoke();
            }
        }
        
        public void OnBeginDrag(PointerEventData eventData)
        {
            if (isEmpty) return;
            
            isDragging = true;
            originalPosition = transform.position;
            originalParent = transform.parent;
            
            // Move to drag canvas
            SetupDragCanvas();
            
            // Set transparency during drag
            canvasGroup.alpha = 0.7f;
            canvasGroup.blocksRaycasts = false;
            
            // Hide tooltip
            onHideTooltip?.Invoke();
            
            // Visual feedback
            UpdateVisualState();
            
            // Animate drag start
            StartCoroutineAnimation(AnimateScale(originalScale * 0.9f, animationDuration));
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
            if (!isDragging) return;
            
            isDragging = false;
            canvasGroup.alpha = 1f;
            canvasGroup.blocksRaycasts = true;
            
            // Check if we dropped on a valid target
            if (!CheckDropTarget(eventData))
            {
                // Return to original position if drop failed
                if (returnToPositionOnFailedDrop)
                {
                    ReturnToOriginalPosition();
                }
            }
            else
            {
                // Handle successful drop
                InventorySlot targetSlot = GetDraggedSlot(eventData);
                if (targetSlot != null && targetSlot != this)
                {
                    onItemMoved?.Invoke(this, targetSlot);
                }
            }
            
            // Reset parent and position
            transform.SetParent(originalParent);
            UpdateVisualState();
            
            // Animate return to normal size
            StartCoroutineAnimation(AnimateScale(originalScale, animationDuration));
        }
        
        public void OnDrop(PointerEventData eventData)
        {
            // Get the dragged slot
            var draggedSlot = GetDraggedSlot(eventData);
            if (draggedSlot != null && draggedSlot != this)
            {
                // Handle item movement
                onItemMoved?.Invoke(draggedSlot, this);
            }
        }
        
        #endregion
        
        #region Visual Updates
        
        private void UpdateItemDisplay()
        {
            if (isEmpty || itemData == null)
            {
                // Show empty slot
                if (itemIcon != null)
                    itemIcon.gameObject.SetActive(false);
                if (quantityText != null)
                    quantityText.gameObject.SetActive(false);
                if (rarityBorder != null)
                    rarityBorder.gameObject.SetActive(false);
                if (emptySlotIndicator != null)
                    emptySlotIndicator.SetActive(true);
                if (stackableIndicator != null)
                    stackableIndicator.SetActive(false);
            }
            else
            {
                // Show item
                if (emptySlotIndicator != null)
                    emptySlotIndicator.SetActive(false);
                
                // Set item icon
                if (itemIcon != null)
                {
                    itemIcon.gameObject.SetActive(true);
                    // Load item icon from resources (placeholder implementation)
                    // In a real implementation, this would load from the item's icon path
                    Sprite icon = Resources.Load<Sprite>($"ItemIcons/{itemData.Type}");
                    if (icon != null)
                        itemIcon.sprite = icon;
                }
                
                // Set quantity text for stackable items
                if (quantityText != null)
                {
                    if (itemData.IsStackable && itemData.Quantity > 1)
                    {
                        quantityText.gameObject.SetActive(true);
                        quantityText.text = itemData.Quantity.ToString();
                    }
                    else
                    {
                        quantityText.gameObject.SetActive(false);
                    }
                }
                
                // Set rarity border (placeholder - would need actual rarity system)
                if (rarityBorder != null)
                {
                    rarityBorder.gameObject.SetActive(true);
                    rarityBorder.color = GetRarityColor(itemData);
                }
                
                // Show stackable indicator
                if (stackableIndicator != null)
                    stackableIndicator.SetActive(itemData.IsStackable);
            }
        }
        
        private void UpdateVisualState()
        {
            Color targetColor = normalColor;
            
            if (isEmpty)
            {
                targetColor = emptyColor;
            }
            else if (isDragging)
            {
                targetColor = selectedColor;
            }
            else if (isSelected)
            {
                targetColor = selectedColor;
            }
            else if (isHighlighted)
            {
                targetColor = highlightColor;
            }
            
            if (slotBackground != null)
                slotBackground.color = targetColor;
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
            if (hovering)
            {
                Vector3 targetScale = originalScale * hoverScale;
                StartCoroutineAnimation(AnimateScale(targetScale, animationDuration));
            }
            else
            {
                StartCoroutineAnimation(AnimateScale(originalScale, animationDuration));
            }
        }
        
        private void AnimateSelection()
        {
            StartCoroutineAnimation(AnimateSelectionPulse());
        }
        
        private void ReturnToOriginalPosition()
        {
            StartCoroutineAnimation(AnimatePosition(originalPosition, animationDuration * 2f));
        }
        
        private void StartCoroutineAnimation(IEnumerator animation)
        {
            if (currentAnimation != null)
            {
                StopCoroutine(currentAnimation);
            }
            currentAnimation = StartCoroutine(animation);
        }
        
        private IEnumerator AnimateScale(Vector3 targetScale, float duration)
        {
            Vector3 startScale = transform.localScale;
            float elapsed = 0f;
            
            while (elapsed < duration)
            {
                elapsed += Time.deltaTime;
                float t = elapsed / duration;
                // Ease out quad approximation
                t = 1f - (1f - t) * (1f - t);
                transform.localScale = Vector3.Lerp(startScale, targetScale, t);
                yield return null;
            }
            
            transform.localScale = targetScale;
        }
        
        private IEnumerator AnimatePosition(Vector3 targetPosition, float duration)
        {
            Vector3 startPosition = transform.position;
            float elapsed = 0f;
            
            while (elapsed < duration)
            {
                elapsed += Time.deltaTime;
                float t = elapsed / duration;
                // Ease out back approximation
                float c1 = 1.70158f;
                float c3 = c1 + 1f;
                t = 1f + c3 * Mathf.Pow(t - 1f, 3f) + c1 * Mathf.Pow(t - 1f, 2f);
                transform.position = Vector3.Lerp(startPosition, targetPosition, t);
                yield return null;
            }
            
            transform.position = targetPosition;
        }
        
        private IEnumerator AnimateSelectionPulse()
        {
            Vector3 startScale = originalScale;
            Vector3 pulseScale = originalScale * 1.1f;
            
            // Scale up
            yield return StartCoroutine(AnimateScale(pulseScale, animationDuration * 0.5f));
            // Scale back down
            yield return StartCoroutine(AnimateScale(startScale, animationDuration * 0.5f));
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
                var dropTarget = eventData.pointerEnter.GetComponent<InventorySlot>();
                if (dropTarget != null)
                {
                    // The drop target will handle the actual drop logic
                    return true;
                }
            }
            
            return false;
        }
        
        private InventorySlot GetDraggedSlot(PointerEventData eventData)
        {
            // Get the slot being dragged from the drag source
            var draggedObject = eventData.pointerDrag;
            if (draggedObject != null)
            {
                return draggedObject.GetComponent<InventorySlot>();
            }
            return null;
        }
        
        #endregion
        
        #region Utility Methods
        
        private Color GetRarityColor(ItemModel item)
        {
            // Placeholder rarity color system
            // In a real implementation, this would be based on actual item rarity
            switch (item.Type)
            {
                case ItemType.Quest:
                    return Color.yellow;
                case ItemType.Treasure:
                    return new Color(1f, 0.5f, 0f); // Orange
                case ItemType.Weapon:
                case ItemType.Armor:
                    return Color.blue;
                default:
                    return Color.white;
            }
        }
        
        #endregion
        
        #region Public Properties
        
        public int SlotIndex => slotIndex;
        public bool IsSelected => isSelected;
        public bool IsHighlighted => isHighlighted;
        public bool IsDragging => isDragging;
        
        #endregion
    }
} 