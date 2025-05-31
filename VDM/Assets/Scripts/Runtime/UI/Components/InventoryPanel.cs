using UnityEngine;
using UnityEngine.UI;
using TMPro;
using VDM.UI.Core;
using VDM.Systems.Inventory.Models;
using VDM.Systems.Character.Models;
using VDM.Systems.Inventory.Services;
using System.Collections.Generic;
using System.Linq;

namespace VDM.UI.Systems.Inventory
{
    /// <summary>
    /// UI panel for inventory management and item operations
    /// </summary>
    public class InventoryPanel : BaseUIPanel
    {
        [Header("Inventory Info")]
        [SerializeField] private TextMeshProUGUI inventoryTitleText;
        [SerializeField] private TextMeshProUGUI weightText;
        [SerializeField] private Slider weightSlider;
        [SerializeField] private TextMeshProUGUI currencyText;
        
        [Header("Category Tabs")]
        [SerializeField] private Button allItemsTabButton;
        [SerializeField] private Button weaponsTabButton;
        [SerializeField] private Button armorTabButton;
        [SerializeField] private Button consumablesTabButton;
        [SerializeField] private Button questItemsTabButton;
        [SerializeField] private Button miscTabButton;
        
        [Header("Item Grid")]
        [SerializeField] private ScrollRect itemScrollRect;
        [SerializeField] private Transform itemGridParent;
        [SerializeField] private GameObject itemSlotPrefab;
        [SerializeField] private GridLayoutGroup itemGridLayout;
        
        [Header("Item Details")]
        [SerializeField] private GameObject itemDetailsPanel;
        [SerializeField] private Image itemIcon;
        [SerializeField] private TextMeshProUGUI itemNameText;
        [SerializeField] private TextMeshProUGUI itemTypeText;
        [SerializeField] private TextMeshProUGUI itemDescriptionText;
        [SerializeField] private TextMeshProUGUI itemValueText;
        [SerializeField] private TextMeshProUGUI itemWeightText;
        [SerializeField] private TextMeshProUGUI itemQuantityText;
        [SerializeField] private TextMeshProUGUI itemStatsText;
        
        [Header("Item Actions")]
        [SerializeField] private Button useItemButton;
        [SerializeField] private Button equipItemButton;
        [SerializeField] private Button dropItemButton;
        [SerializeField] private Button sellItemButton;
        [SerializeField] private Button splitStackButton;
        
        [Header("Sorting & Filtering")]
        [SerializeField] private TMP_Dropdown sortDropdown;
        [SerializeField] private TMP_InputField searchInputField;
        [SerializeField] private Button sortAscendingButton;
        [SerializeField] private Button sortDescendingButton;
        
        [Header("Quick Actions")]
        [SerializeField] private Button sortAllButton;
        [SerializeField] private Button sellJunkButton;
        [SerializeField] private Button repairAllButton;
        
        private InventoryService inventoryService;
        private CharacterModel currentCharacter;
        private List<GameObject> itemSlots = new List<GameObject>();
        private ItemModel selectedItem;
        private InventoryCategory currentCategory = InventoryCategory.All;
        private SortCriteria currentSortCriteria = SortCriteria.Name;
        private bool sortAscending = true;
        private string searchFilter = "";
        
        private enum InventoryCategory
        {
            All,
            Weapons,
            Armor,
            Consumables,
            QuestItems,
            Miscellaneous
        }
        
        private enum SortCriteria
        {
            Name,
            Type,
            Value,
            Weight,
            Quantity,
            Rarity
        }
        
        protected override void Awake()
        {
            base.Awake();
            inventoryService = FindObjectOfType<InventoryService>();
            
            // Setup tab buttons
            if (allItemsTabButton != null)
                allItemsTabButton.onClick.AddListener(() => ShowCategory(InventoryCategory.All));
            if (weaponsTabButton != null)
                weaponsTabButton.onClick.AddListener(() => ShowCategory(InventoryCategory.Weapons));
            if (armorTabButton != null)
                armorTabButton.onClick.AddListener(() => ShowCategory(InventoryCategory.Armor));
            if (consumablesTabButton != null)
                consumablesTabButton.onClick.AddListener(() => ShowCategory(InventoryCategory.Consumables));
            if (questItemsTabButton != null)
                questItemsTabButton.onClick.AddListener(() => ShowCategory(InventoryCategory.QuestItems));
            if (miscTabButton != null)
                miscTabButton.onClick.AddListener(() => ShowCategory(InventoryCategory.Miscellaneous));
            
            // Setup action buttons
            if (useItemButton != null)
                useItemButton.onClick.AddListener(UseSelectedItem);
            if (equipItemButton != null)
                equipItemButton.onClick.AddListener(EquipSelectedItem);
            if (dropItemButton != null)
                dropItemButton.onClick.AddListener(DropSelectedItem);
            if (sellItemButton != null)
                sellItemButton.onClick.AddListener(SellSelectedItem);
            if (splitStackButton != null)
                splitStackButton.onClick.AddListener(SplitSelectedStack);
            
            // Setup sorting and filtering
            if (sortDropdown != null)
                sortDropdown.onValueChanged.AddListener(OnSortCriteriaChanged);
            if (searchInputField != null)
                searchInputField.onValueChanged.AddListener(OnSearchFilterChanged);
            if (sortAscendingButton != null)
                sortAscendingButton.onClick.AddListener(() => SetSortOrder(true));
            if (sortDescendingButton != null)
                sortDescendingButton.onClick.AddListener(() => SetSortOrder(false));
            
            // Setup quick actions
            if (sortAllButton != null)
                sortAllButton.onClick.AddListener(SortAllItems);
            if (sellJunkButton != null)
                sellJunkButton.onClick.AddListener(SellAllJunk);
            if (repairAllButton != null)
                repairAllButton.onClick.AddListener(RepairAllItems);
        }
        
        protected override void OnEnable()
        {
            base.OnEnable();
            if (inventoryService != null)
            {
                inventoryService.OnInventoryChanged += OnInventoryChanged;
                inventoryService.OnItemAdded += OnItemAdded;
                inventoryService.OnItemRemoved += OnItemRemoved;
                inventoryService.OnItemUsed += OnItemUsed;
            }
        }
        
        protected override void OnDisable()
        {
            base.OnDisable();
            if (inventoryService != null)
            {
                inventoryService.OnInventoryChanged -= OnInventoryChanged;
                inventoryService.OnItemAdded -= OnItemAdded;
                inventoryService.OnItemRemoved -= OnItemRemoved;
                inventoryService.OnItemUsed -= OnItemUsed;
            }
        }
        
        /// <summary>
        /// Show inventory for a specific character
        /// </summary>
        public void ShowInventory(CharacterModel character)
        {
            currentCharacter = character;
            UpdateInventoryInfo();
            RefreshItemGrid();
            ShowCategory(InventoryCategory.All);
            
            if (itemDetailsPanel != null)
                itemDetailsPanel.SetActive(false);
        }
        
        /// <summary>
        /// Update inventory information display
        /// </summary>
        private void UpdateInventoryInfo()
        {
            if (currentCharacter?.Inventory == null) return;
            
            var inventory = currentCharacter.Inventory;
            
            if (inventoryTitleText != null)
                inventoryTitleText.text = $"{currentCharacter.Name}'s Inventory";
            
            if (weightText != null)
                weightText.text = $"Weight: {inventory.CurrentWeight:F1} / {inventory.MaxWeight:F1}";
            
            if (weightSlider != null)
                weightSlider.value = inventory.CurrentWeight / inventory.MaxWeight;
            
            if (currencyText != null)
                currencyText.text = $"Gold: {inventory.Currency:N0}";
        }
        
        /// <summary>
        /// Show items for a specific category
        /// </summary>
        private void ShowCategory(InventoryCategory category)
        {
            currentCategory = category;
            RefreshItemGrid();
            UpdateTabButtonStates();
        }
        
        /// <summary>
        /// Refresh the item grid display
        /// </summary>
        private void RefreshItemGrid()
        {
            ClearItemSlots();
            
            if (currentCharacter?.Inventory?.Items == null || itemGridParent == null || itemSlotPrefab == null)
                return;
            
            var filteredItems = GetFilteredAndSortedItems();
            
            foreach (var item in filteredItems)
            {
                GameObject itemSlot = Instantiate(itemSlotPrefab, itemGridParent);
                InventorySlot slotComponent = itemSlot.GetComponent<InventorySlot>();
                
                if (slotComponent != null)
                {
                    slotComponent.Initialize(item, OnItemSelected, OnItemDoubleClicked);
                }
                
                itemSlots.Add(itemSlot);
            }
        }
        
        /// <summary>
        /// Get filtered and sorted items based on current settings
        /// </summary>
        private List<ItemModel> GetFilteredAndSortedItems()
        {
            if (currentCharacter?.Inventory?.Items == null)
                return new List<ItemModel>();
            
            var items = currentCharacter.Inventory.Items.AsEnumerable();
            
            // Apply category filter
            items = currentCategory switch
            {
                InventoryCategory.Weapons => items.Where(i => i.Type == ItemType.Weapon),
                InventoryCategory.Armor => items.Where(i => i.Type == ItemType.Armor),
                InventoryCategory.Consumables => items.Where(i => i.Type == ItemType.Consumable),
                InventoryCategory.QuestItems => items.Where(i => i.Type == ItemType.Quest),
                InventoryCategory.Miscellaneous => items.Where(i => i.Type == ItemType.Miscellaneous),
                _ => items
            };
            
            // Apply search filter
            if (!string.IsNullOrEmpty(searchFilter))
            {
                items = items.Where(i => i.Name.ToLower().Contains(searchFilter.ToLower()) ||
                                        i.Description.ToLower().Contains(searchFilter.ToLower()));
            }
            
            // Apply sorting
            items = currentSortCriteria switch
            {
                SortCriteria.Name => sortAscending ? items.OrderBy(i => i.Name) : items.OrderByDescending(i => i.Name),
                SortCriteria.Type => sortAscending ? items.OrderBy(i => i.Type) : items.OrderByDescending(i => i.Type),
                SortCriteria.Value => sortAscending ? items.OrderBy(i => i.Value) : items.OrderByDescending(i => i.Value),
                SortCriteria.Weight => sortAscending ? items.OrderBy(i => i.Weight) : items.OrderByDescending(i => i.Weight),
                SortCriteria.Quantity => sortAscending ? items.OrderBy(i => i.Quantity) : items.OrderByDescending(i => i.Quantity),
                SortCriteria.Rarity => sortAscending ? items.OrderBy(i => i.Rarity) : items.OrderByDescending(i => i.Rarity),
                _ => items.OrderBy(i => i.Name)
            };
            
            return items.ToList();
        }
        
        /// <summary>
        /// Show details for selected item
        /// </summary>
        private void ShowItemDetails(ItemModel item)
        {
            selectedItem = item;
            
            if (itemDetailsPanel == null) return;
            
            itemDetailsPanel.SetActive(true);
            
            if (itemNameText != null)
                itemNameText.text = item.Name;
            if (itemTypeText != null)
                itemTypeText.text = item.Type.ToString();
            if (itemDescriptionText != null)
                itemDescriptionText.text = item.Description;
            if (itemValueText != null)
                itemValueText.text = $"Value: {item.Value:N0} gold";
            if (itemWeightText != null)
                itemWeightText.text = $"Weight: {item.Weight:F1}";
            if (itemQuantityText != null)
                itemQuantityText.text = $"Quantity: {item.Quantity}";
            
            // Update item icon
            if (itemIcon != null && !string.IsNullOrEmpty(item.IconPath))
            {
                Sprite icon = Resources.Load<Sprite>(item.IconPath);
                if (icon != null)
                    itemIcon.sprite = icon;
            }
            
            // Update stats text
            if (itemStatsText != null)
                itemStatsText.text = GetItemStatsText(item);
            
            UpdateActionButtons();
        }
        
        /// <summary>
        /// Get formatted stats text for an item
        /// </summary>
        private string GetItemStatsText(ItemModel item)
        {
            var stats = new List<string>();
            
            if (item.Stats != null)
            {
                if (item.Stats.Damage > 0)
                    stats.Add($"Damage: {item.Stats.Damage}");
                if (item.Stats.ArmorClass > 0)
                    stats.Add($"AC: {item.Stats.ArmorClass}");
                if (item.Stats.StrengthBonus != 0)
                    stats.Add($"STR: {item.Stats.StrengthBonus:+0;-0}");
                if (item.Stats.DexterityBonus != 0)
                    stats.Add($"DEX: {item.Stats.DexterityBonus:+0;-0}");
                if (item.Stats.ConstitutionBonus != 0)
                    stats.Add($"CON: {item.Stats.ConstitutionBonus:+0;-0}");
                if (item.Stats.IntelligenceBonus != 0)
                    stats.Add($"INT: {item.Stats.IntelligenceBonus:+0;-0}");
                if (item.Stats.WisdomBonus != 0)
                    stats.Add($"WIS: {item.Stats.WisdomBonus:+0;-0}");
                if (item.Stats.CharismaBonus != 0)
                    stats.Add($"CHA: {item.Stats.CharismaBonus:+0;-0}");
            }
            
            return string.Join("\n", stats);
        }
        
        /// <summary>
        /// Update action button states
        /// </summary>
        private void UpdateActionButtons()
        {
            if (selectedItem == null) return;
            
            if (useItemButton != null)
                useItemButton.interactable = selectedItem.IsUsable;
            if (equipItemButton != null)
                equipItemButton.interactable = selectedItem.IsEquippable;
            if (dropItemButton != null)
                dropItemButton.interactable = !selectedItem.IsQuestItem;
            if (sellItemButton != null)
                sellItemButton.interactable = selectedItem.CanSell;
            if (splitStackButton != null)
                splitStackButton.interactable = selectedItem.IsStackable && selectedItem.Quantity > 1;
        }
        
        /// <summary>
        /// Update tab button visual states
        /// </summary>
        private void UpdateTabButtonStates()
        {
            SetTabButtonState(allItemsTabButton, currentCategory == InventoryCategory.All);
            SetTabButtonState(weaponsTabButton, currentCategory == InventoryCategory.Weapons);
            SetTabButtonState(armorTabButton, currentCategory == InventoryCategory.Armor);
            SetTabButtonState(consumablesTabButton, currentCategory == InventoryCategory.Consumables);
            SetTabButtonState(questItemsTabButton, currentCategory == InventoryCategory.QuestItems);
            SetTabButtonState(miscTabButton, currentCategory == InventoryCategory.Miscellaneous);
        }
        
        /// <summary>
        /// Set visual state for tab button
        /// </summary>
        private void SetTabButtonState(Button button, bool isActive)
        {
            if (button == null) return;
            
            ColorBlock colors = button.colors;
            colors.normalColor = isActive ? Color.white : Color.gray;
            button.colors = colors;
        }
        
        /// <summary>
        /// Clear all item slots
        /// </summary>
        private void ClearItemSlots()
        {
            foreach (var slot in itemSlots)
            {
                if (slot != null)
                    DestroyImmediate(slot);
            }
            itemSlots.Clear();
        }
        
        #region Event Handlers
        
        private void OnItemSelected(ItemModel item)
        {
            ShowItemDetails(item);
        }
        
        private void OnItemDoubleClicked(ItemModel item)
        {
            if (item.IsUsable)
                UseItem(item);
            else if (item.IsEquippable)
                EquipItem(item);
        }
        
        private void OnSortCriteriaChanged(int index)
        {
            currentSortCriteria = (SortCriteria)index;
            RefreshItemGrid();
        }
        
        private void OnSearchFilterChanged(string filter)
        {
            searchFilter = filter;
            RefreshItemGrid();
        }
        
        private void SetSortOrder(bool ascending)
        {
            sortAscending = ascending;
            RefreshItemGrid();
        }
        
        private void OnInventoryChanged(InventoryModel inventory)
        {
            UpdateInventoryInfo();
            RefreshItemGrid();
        }
        
        private void OnItemAdded(ItemModel item)
        {
            RefreshItemGrid();
            NotificationSystem.Instance?.ShowNotification(
                $"Added {item.Name} to inventory",
                NotificationType.Info
            );
        }
        
        private void OnItemRemoved(ItemModel item)
        {
            RefreshItemGrid();
            if (selectedItem?.Id == item.Id)
            {
                selectedItem = null;
                if (itemDetailsPanel != null)
                    itemDetailsPanel.SetActive(false);
            }
        }
        
        private void OnItemUsed(ItemModel item)
        {
            RefreshItemGrid();
            NotificationSystem.Instance?.ShowNotification(
                $"Used {item.Name}",
                NotificationType.Success
            );
        }
        
        #endregion
        
        #region Action Methods
        
        private void UseSelectedItem()
        {
            if (selectedItem != null)
                UseItem(selectedItem);
        }
        
        private void EquipSelectedItem()
        {
            if (selectedItem != null)
                EquipItem(selectedItem);
        }
        
        private void DropSelectedItem()
        {
            if (selectedItem != null)
                DropItem(selectedItem);
        }
        
        private void SellSelectedItem()
        {
            if (selectedItem != null)
                SellItem(selectedItem);
        }
        
        private void SplitSelectedStack()
        {
            if (selectedItem != null)
                SplitStack(selectedItem);
        }
        
        private void UseItem(ItemModel item)
        {
            inventoryService?.UseItem(item.Id);
        }
        
        private void EquipItem(ItemModel item)
        {
            inventoryService?.EquipItem(item.Id);
        }
        
        private void DropItem(ItemModel item)
        {
            ModalSystem.Instance?.ShowConfirmation(
                "Drop Item",
                $"Are you sure you want to drop {item.Name}?",
                () => inventoryService?.DropItem(item.Id),
                null
            );
        }
        
        private void SellItem(ItemModel item)
        {
            ModalSystem.Instance?.ShowConfirmation(
                "Sell Item",
                $"Sell {item.Name} for {item.Value} gold?",
                () => inventoryService?.SellItem(item.Id),
                null
            );
        }
        
        private void SplitStack(ItemModel item)
        {
            // Show split stack dialog
            // Implementation depends on split stack dialog structure
        }
        
        private void SortAllItems()
        {
            inventoryService?.SortInventory();
            RefreshItemGrid();
        }
        
        private void SellAllJunk()
        {
            ModalSystem.Instance?.ShowConfirmation(
                "Sell Junk",
                "Sell all junk items?",
                () => inventoryService?.SellJunkItems(),
                null
            );
        }
        
        private void RepairAllItems()
        {
            inventoryService?.RepairAllItems();
        }
        
        #endregion
    }
} 