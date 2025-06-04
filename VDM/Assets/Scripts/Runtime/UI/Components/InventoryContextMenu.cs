using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using TMPro;
using VDM.DTOs.Game.Character;

namespace VDM.UI.Systems.Inventory
{
    /// <summary>
    /// Context menu for inventory items with various actions
    /// </summary>
    public class InventoryContextMenu : MonoBehaviour
    {
        [Header("Menu Layout")]
        [SerializeField] private RectTransform menuRect;
        [SerializeField] private CanvasGroup canvasGroup;
        [SerializeField] private Image backgroundImage;
        
        [Header("Menu Items")]
        [SerializeField] private Transform menuItemsContainer;
        [SerializeField] private GameObject menuItemPrefab;
        
        [Header("Animation")]
        [SerializeField] private float fadeInDuration = 0.15f;
        [SerializeField] private float fadeOutDuration = 0.1f;
        [SerializeField] private Vector2 offset = new Vector2(5f, -5f);
        
        [Header("Menu Item Configuration")]
        [SerializeField] private Color normalColor = Color.white;
        [SerializeField] private Color highlightColor = new Color(0.8f, 0.9f, 1f, 1f);
        [SerializeField] private Color disabledColor = new Color(0.5f, 0.5f, 0.5f, 0.5f);
        
        // Data
        private ItemModel currentItem;
        private InventorySlot currentSlot;
        private bool isVisible = false;
        private Camera uiCamera;
        private Canvas parentCanvas;
        
        // Menu actions
        private Dictionary<string, Action> menuActions = new Dictionary<string, Action>();
        private List<GameObject> menuItemElements = new List<GameObject>();
        
        // Events
        private System.Action<ItemModel> onUseItem;
        private System.Action<ItemModel> onEquipItem;
        private System.Action<ItemModel> onDropItem;
        private System.Action<ItemModel, int> onSplitStack;
        private System.Action<ItemModel> onDestroyItem;
        private System.Action<ItemModel> onSellItem;
        private System.Action<ItemModel> onInspectItem;
        private System.Action<ItemModel> onMoveToContainer;
        
        private void Awake()
        {
            // Find UI camera and canvas
            parentCanvas = GetComponentInParent<Canvas>();
            uiCamera = parentCanvas?.worldCamera ?? Camera.main;
            
            // Initially hide menu
            if (canvasGroup != null)
                canvasGroup.alpha = 0f;
            
            gameObject.SetActive(false);
            
            // Set up click detection to close menu
            SetupClickDetection();
        }
        
        /// <summary>
        /// Initialize the context menu with action callbacks
        /// </summary>
        public void Initialize(
            System.Action<ItemModel> useItemCallback,
            System.Action<ItemModel> equipItemCallback,
            System.Action<ItemModel> dropItemCallback,
            System.Action<ItemModel, int> splitStackCallback,
            System.Action<ItemModel> destroyItemCallback,
            System.Action<ItemModel> sellItemCallback,
            System.Action<ItemModel> inspectItemCallback,
            System.Action<ItemModel> moveToContainerCallback)
        {
            onUseItem = useItemCallback;
            onEquipItem = equipItemCallback;
            onDropItem = dropItemCallback;
            onSplitStack = splitStackCallback;
            onDestroyItem = destroyItemCallback;
            onSellItem = sellItemCallback;
            onInspectItem = inspectItemCallback;
            onMoveToContainer = moveToContainerCallback;
        }
        
        /// <summary>
        /// Show context menu for an item at the specified position
        /// </summary>
        public void ShowMenu(ItemModel item, InventorySlot slot, Vector2 screenPosition)
        {
            if (item == null) return;
            
            currentItem = item;
            currentSlot = slot;
            
            gameObject.SetActive(true);
            BuildMenuItems();
            PositionMenu(screenPosition);
            
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
        /// Hide the context menu
        /// </summary>
        public void HideMenu()
        {
            if (!isVisible) return;
            
            isVisible = false;
            
            // Animate fade out
            LeanTween.cancel(gameObject);
            if (canvasGroup != null)
            {
                LeanTween.alphaCanvas(canvasGroup, 0f, fadeOutDuration)
                    .setEase(LeanTweenType.easeInQuad)
                    .setOnComplete(() => 
                    {
                        gameObject.SetActive(false);
                        ClearMenuItems();
                    });
            }
            else
            {
                gameObject.SetActive(false);
                ClearMenuItems();
            }
        }
        
        private void BuildMenuItems()
        {
            ClearMenuItems();
            
            if (currentItem == null || menuItemsContainer == null || menuItemPrefab == null)
                return;
            
            var menuOptions = GetMenuOptions(currentItem);
            
            foreach (var option in menuOptions)
            {
                CreateMenuItem(option.text, option.action, option.enabled, option.color);
            }
            
            // Force layout rebuild
            LayoutRebuilder.ForceRebuildLayoutImmediate(menuRect);
        }
        
        private List<MenuOption> GetMenuOptions(ItemModel item)
        {
            var options = new List<MenuOption>();
            
            // Use Item (for consumables)
            if (item.IsUsable)
            {
                options.Add(new MenuOption
                {
                    text = "Use",
                    action = () => UseItem(),
                    enabled = true,
                    color = normalColor
                });
            }
            
            // Equip Item (for equipment)
            if (item.IsEquippable)
            {
                options.Add(new MenuOption
                {
                    text = "Equip",
                    action = () => EquipItem(),
                    enabled = true,
                    color = normalColor
                });
            }
            
            // Split Stack (for stackable items with quantity > 1)
            if (item.IsStackable && item.Quantity > 1)
            {
                options.Add(new MenuOption
                {
                    text = "Split Stack",
                    action = () => ShowSplitStackDialog(),
                    enabled = true,
                    color = normalColor
                });
            }
            
            // Drop Item
            options.Add(new MenuOption
            {
                text = "Drop",
                action = () => DropItem(),
                enabled = !item.IsQuestItem, // Can't drop quest items
                color = item.IsQuestItem ? disabledColor : normalColor
            });
            
            // Move to Container (if containers exist)
            options.Add(new MenuOption
            {
                text = "Move to Bag",
                action = () => MoveToContainer(),
                enabled = true,
                color = normalColor
            });
            
            // Separator
            options.Add(new MenuOption
            {
                text = "---",
                action = null,
                enabled = false,
                color = disabledColor
            });
            
            // Sell Item (if valuable and not quest item)
            if (item.CanSell && item.Value > 0)
            {
                options.Add(new MenuOption
                {
                    text = $"Sell ({item.Value:N0}g)",
                    action = () => SellItem(),
                    enabled = true,
                    color = new Color(1f, 0.8f, 0f, 1f) // Gold color
                });
            }
            
            // Inspect Item
            options.Add(new MenuOption
            {
                text = "Inspect",
                action = () => InspectItem(),
                enabled = true,
                color = normalColor
            });
            
            // Destroy Item (dangerous action)
            if (!item.IsQuestItem)
            {
                options.Add(new MenuOption
                {
                    text = "Destroy",
                    action = () => ShowDestroyConfirmation(),
                    enabled = true,
                    color = Color.red
                });
            }
            
            return options;
        }
        
        private void CreateMenuItem(string text, Action action, bool enabled, Color color)
        {
            GameObject menuItemGO = Instantiate(menuItemPrefab, menuItemsContainer);
            var menuItem = menuItemGO.GetComponent<ContextMenuItem>();
            
            if (menuItem == null)
            {
                // If no ContextMenuItem component, create basic UI
                var textComponent = menuItemGO.GetComponentInChildren<TextMeshProUGUI>();
                var button = menuItemGO.GetComponent<Button>();
                
                if (textComponent != null)
                {
                    textComponent.text = text;
                    textComponent.color = enabled ? color : disabledColor;
                }
                
                if (button != null && enabled && action != null)
                {
                    button.onClick.AddListener(() =>
                    {
                        action.Invoke();
                        HideMenu();
                    });
                    button.interactable = enabled;
                }
                else if (button != null)
                {
                    button.interactable = false;
                }
            }
            else
            {
                // Use ContextMenuItem component
                menuItem.Initialize(text, action, enabled, color, () => HideMenu());
            }
            
            menuItemElements.Add(menuItemGO);
        }
        
        private void ClearMenuItems()
        {
            foreach (var item in menuItemElements)
            {
                if (item != null)
                    DestroyImmediate(item);
            }
            menuItemElements.Clear();
        }
        
        private void PositionMenu(Vector2 screenPosition)
        {
            if (menuRect == null || parentCanvas == null) return;
            
            // Convert screen position to canvas position
            Vector2 canvasPosition;
            RectTransformUtility.ScreenPointToLocalPointInRectangle(
                parentCanvas.transform as RectTransform,
                screenPosition + offset,
                uiCamera,
                out canvasPosition);
            
            // Get canvas and menu dimensions
            Rect canvasRect = (parentCanvas.transform as RectTransform).rect;
            Vector2 menuSize = menuRect.sizeDelta;
            
            // Clamp position to keep menu within canvas bounds
            float clampedX = Mathf.Clamp(canvasPosition.x,
                -canvasRect.width * 0.5f,
                canvasRect.width * 0.5f - menuSize.x);
            
            float clampedY = Mathf.Clamp(canvasPosition.y,
                -canvasRect.height * 0.5f + menuSize.y,
                canvasRect.height * 0.5f);
            
            // Set menu position
            menuRect.anchoredPosition = new Vector2(clampedX, clampedY);
        }
        
        private void SetupClickDetection()
        {
            // Add a background click detector to close the menu
            if (backgroundImage != null)
            {
                var clickDetector = backgroundImage.gameObject.GetComponent<Button>();
                if (clickDetector == null)
                    clickDetector = backgroundImage.gameObject.AddComponent<Button>();
                
                clickDetector.onClick.AddListener(() => HideMenu());
            }
        }
        
        #region Menu Actions
        
        private void UseItem()
        {
            onUseItem?.Invoke(currentItem);
        }
        
        private void EquipItem()
        {
            onEquipItem?.Invoke(currentItem);
        }
        
        private void DropItem()
        {
            onDropItem?.Invoke(currentItem);
        }
        
        private void MoveToContainer()
        {
            onMoveToContainer?.Invoke(currentItem);
        }
        
        private void SellItem()
        {
            onSellItem?.Invoke(currentItem);
        }
        
        private void InspectItem()
        {
            onInspectItem?.Invoke(currentItem);
        }
        
        private void ShowSplitStackDialog()
        {
            // For now, split stack in half
            int splitAmount = Mathf.Max(1, currentItem.Quantity / 2);
            onSplitStack?.Invoke(currentItem, splitAmount);
        }
        
        private void ShowDestroyConfirmation()
        {
            // In a real implementation, this would show a confirmation dialog
            // For now, just call the destroy action
            onDestroyItem?.Invoke(currentItem);
        }
        
        #endregion
        
        private void Update()
        {
            // Hide menu if user clicks elsewhere
            if (isVisible && Input.GetMouseButtonDown(0))
            {
                Vector2 mousePosition = Input.mousePosition;
                if (!RectTransformUtility.RectangleContainsScreenPoint(menuRect, mousePosition, uiCamera))
                {
                    HideMenu();
                }
            }
        }
        
        #region Public Properties
        
        public bool IsVisible => isVisible;
        public ItemModel CurrentItem => currentItem;
        
        #endregion
        
        #region Helper Classes
        
        private class MenuOption
        {
            public string text;
            public Action action;
            public bool enabled;
            public Color color;
        }
        
        #endregion
    }
    
    /// <summary>
    /// Individual context menu item component
    /// </summary>
    public class ContextMenuItem : MonoBehaviour
    {
        [Header("UI Components")]
        [SerializeField] private TextMeshProUGUI textComponent;
        [SerializeField] private Button buttonComponent;
        [SerializeField] private Image backgroundImage;
        
        [Header("Visual States")]
        [SerializeField] private Color normalBackgroundColor = new Color(0f, 0f, 0f, 0.8f);
        [SerializeField] private Color highlightBackgroundColor = new Color(0.2f, 0.2f, 0.2f, 0.9f);
        
        private Action menuAction;
        private Action closeMenuCallback;
        private bool isEnabled = true;
        
        /// <summary>
        /// Initialize the menu item
        /// </summary>
        public void Initialize(string text, Action action, bool enabled, Color textColor, Action closeCallback)
        {
            menuAction = action;
            closeMenuCallback = closeCallback;
            isEnabled = enabled;
            
            // Set text
            if (textComponent != null)
            {
                textComponent.text = text;
                textComponent.color = textColor;
            }
            
            // Set up button
            if (buttonComponent != null)
            {
                buttonComponent.interactable = enabled && action != null;
                
                if (enabled && action != null)
                {
                    buttonComponent.onClick.AddListener(() =>
                    {
                        action.Invoke();
                        closeCallback?.Invoke();
                    });
                }
            }
            
            // Set initial background
            if (backgroundImage != null)
                backgroundImage.color = normalBackgroundColor;
        }
        
        public void OnPointerEnter()
        {
            if (isEnabled && backgroundImage != null)
                backgroundImage.color = highlightBackgroundColor;
        }
        
        public void OnPointerExit()
        {
            if (backgroundImage != null)
                backgroundImage.color = normalBackgroundColor;
        }
    }
} 