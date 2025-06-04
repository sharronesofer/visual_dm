using System;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using UnityEngine.UI;
using TMPro;
using VDM.DTOs.Game.Character;
using VDM.UI.Systems.Inventory;

namespace VDM.UI.Components
{
    /// <summary>
    /// Complete inventory management system with grid layout, drag-and-drop, sorting, and filtering
    /// </summary>
    public class InventoryPanel : BaseUIPanel
    {
        [Header("Inventory Layout")]
        [SerializeField] private Transform inventoryGridContainer;
        [SerializeField] private GameObject inventorySlotPrefab;
        [SerializeField] private ScrollRect inventoryScrollRect;
        [SerializeField] private GridLayoutGroup inventoryGrid;
        
        [Header("Inventory Information")]
        [SerializeField] private TextMeshProUGUI currentWeightText;
        [SerializeField] private TextMeshProUGUI maxWeightText;
        [SerializeField] private Slider weightBar;
        [SerializeField] private TextMeshProUGUI currencyText;
        [SerializeField] private TextMeshProUGUI slotsUsedText;
        
        [Header("Filtering & Sorting")]
        [SerializeField] private TMP_Dropdown sortDropdown;
        [SerializeField] private TMP_Dropdown filterDropdown;
        [SerializeField] private TMP_InputField searchField;
        [SerializeField] private Button resetFiltersButton;
        
        [Header("Inventory Actions")]
        [SerializeField] private Button sortAllButton;
        [SerializeField] private Button stackAllButton;
        [SerializeField] private Button sellAllJunkButton;
        [SerializeField] private Button expandInventoryButton;
        
        [Header("Bag Management")]
        [SerializeField] private Transform bagTabsContainer;
        [SerializeField] private GameObject bagTabPrefab;
        [SerializeField] private TextMeshProUGUI currentBagText;
        
        [Header("UI Components")]
        [SerializeField] private ItemTooltip itemTooltip;
        [SerializeField] private InventoryContextMenu contextMenu;
        [SerializeField] private Transform tooltipParent;
        
        [Header("Inventory Settings")]
        [SerializeField] private int defaultGridWidth = 8;
        [SerializeField] private int defaultGridHeight = 10;
        [SerializeField] private Vector2 slotSize = new Vector2(64f, 64f);
        [SerializeField] private Vector2 slotSpacing = new Vector2(4f, 4f);
        
        [Header("Visual Feedback")]
        [SerializeField] private Color weightNormalColor = Color.green;
        [SerializeField] private Color weightWarningColor = Color.yellow;
        [SerializeField] private Color weightCriticalColor = Color.red;
        [SerializeField] private float weightWarningThreshold = 0.8f;
        [SerializeField] private float weightCriticalThreshold = 0.95f;
        
        // Data
        private InventoryModel currentInventory;
        private List<InventorySlot> inventorySlots = new List<InventorySlot>();
        private List<ItemModel> allItems = new List<ItemModel>();
        private List<ItemModel> filteredItems = new List<ItemModel>();
        private InventorySlot selectedSlot;
        
        // State
        private int currentBagIndex = 0;
        private bool isInitialized = false;
        private SortOrder currentSortOrder = SortOrder.Name;
        private ItemFilter currentFilter = ItemFilter.All;
        private string currentSearchTerm = "";
        
        // Events
        public System.Action<ItemModel> OnItemUsed;
        public System.Action<ItemModel> OnItemEquipped;
        public System.Action<ItemModel> OnItemDropped;
        public System.Action<ItemModel> OnItemSold;
        public System.Action<ItemModel> OnItemDestroyed;
        public System.Action<float> OnWeightChanged;
        
        #region Unity Lifecycle
        
        protected override void Awake()
        {
            base.Awake();
            InitializeUI();
        }
        
        protected override void Start()
        {
            base.Start();
            SetupEventListeners();
            LoadMockData();
        }
        
        private void Update()
        {
            // Update tooltip position to follow mouse
            if (itemTooltip != null && itemTooltip.IsVisible)
            {
                itemTooltip.UpdateTooltipPosition(Input.mousePosition);
            }
            
            // Handle right-click for context menu
            if (Input.GetMouseButtonDown(1) && selectedSlot != null && !selectedSlot.IsEmpty())
            {
                if (contextMenu != null)
                {
                    contextMenu.ShowMenu(selectedSlot.GetItem(), selectedSlot, Input.mousePosition);
                }
            }
        }
        
        #endregion
        
        #region Initialization
        
        private void InitializeUI()
        {
            CreateInventoryGrid();
            SetupSortingOptions();
            SetupFilteringOptions();
            SetupTooltipAndContextMenu();
            
            isInitialized = true;
        }
        
        private void CreateInventoryGrid()
        {
            if (inventoryGrid != null)
            {
                inventoryGrid.cellSize = slotSize;
                inventoryGrid.spacing = slotSpacing;
                inventoryGrid.constraintCount = defaultGridWidth;
            }
            
            // Create inventory slots
            int totalSlots = defaultGridWidth * defaultGridHeight;
            for (int i = 0; i < totalSlots; i++)
            {
                CreateInventorySlot(i);
            }
        }
        
        private void CreateInventorySlot(int index)
        {
            GameObject slotGO = Instantiate(inventorySlotPrefab, inventoryGridContainer);
            var slot = slotGO.GetComponent<InventorySlot>();
            
            if (slot != null)
            {
                slot.Initialize(
                    index,
                    OnSlotSelected,
                    OnSlotDoubleClicked,
                    OnItemMoved,
                    OnShowTooltip,
                    OnHideTooltip
                );
                
                inventorySlots.Add(slot);
            }
        }
        
        private void SetupSortingOptions()
        {
            if (sortDropdown != null)
            {
                sortDropdown.options.Clear();
                var sortOptions = new List<string>
                {
                    "Name", "Type", "Value", "Weight", "Quantity", "Recently Added"
                };
                
                foreach (string option in sortOptions)
                {
                    sortDropdown.options.Add(new TMP_Dropdown.OptionData(option));
                }
                
                sortDropdown.value = 0;
                sortDropdown.onValueChanged.AddListener(OnSortChanged);
            }
        }
        
        private void SetupFilteringOptions()
        {
            if (filterDropdown != null)
            {
                filterDropdown.options.Clear();
                var filterOptions = new List<string>
                {
                    "All Items", "Weapons", "Armor", "Consumables", "Tools", "Materials", "Treasures", "Quest Items"
                };
                
                foreach (string option in filterOptions)
                {
                    filterDropdown.options.Add(new TMP_Dropdown.OptionData(option));
                }
                
                filterDropdown.value = 0;
                filterDropdown.onValueChanged.AddListener(OnFilterChanged);
            }
        }
        
        private void SetupTooltipAndContextMenu()
        {
            // Initialize tooltip
            if (itemTooltip == null && tooltipParent != null)
            {
                // Try to find existing tooltip
                itemTooltip = tooltipParent.GetComponentInChildren<ItemTooltip>();
            }
            
            // Initialize context menu
            if (contextMenu != null)
            {
                contextMenu.Initialize(
                    OnUseItem,
                    OnEquipItem,
                    OnDropItem,
                    OnSplitStack,
                    OnDestroyItem,
                    OnSellItem,
                    OnInspectItem,
                    OnMoveToContainer
                );
            }
        }
        
        private void SetupEventListeners()
        {
            // Search field
            if (searchField != null)
                searchField.onValueChanged.AddListener(OnSearchChanged);
            
            // Action buttons
            if (sortAllButton != null)
                sortAllButton.onClick.AddListener(SortAllItems);
            if (stackAllButton != null)
                stackAllButton.onClick.AddListener(StackAllItems);
            if (sellAllJunkButton != null)
                sellAllJunkButton.onClick.AddListener(SellAllJunk);
            if (expandInventoryButton != null)
                expandInventoryButton.onClick.AddListener(ExpandInventory);
            if (resetFiltersButton != null)
                resetFiltersButton.onClick.AddListener(ResetFilters);
        }
        
        #endregion
        
        #region Data Management
        
        public void SetInventoryData(InventoryModel inventory)
        {
            currentInventory = inventory;
            allItems = inventory?.Items ?? new List<ItemModel>();
            
            RefreshInventoryDisplay();
            UpdateInventoryInfo();
        }
        
        private void LoadMockData()
        {
            // Create mock inventory for testing
            var mockInventory = new InventoryModel
            {
                Id = "player_inventory",
                CharacterId = "player",
                Currency = 1250,
                CurrentWeight = 45.5f,
                MaxWeight = 100f,
                MaxSlots = defaultGridWidth * defaultGridHeight
            };
            
            // Add some mock items
            mockInventory.Items.AddRange(CreateMockItems());
            
            SetInventoryData(mockInventory);
        }
        
        private List<ItemModel> CreateMockItems()
        {
            var items = new List<ItemModel>();
            
            // Weapons
            items.Add(new ItemModel
            {
                Id = "sword_001",
                Name = "Iron Sword",
                Description = "A sturdy iron sword with a sharp edge.",
                Type = ItemType.Weapon,
                Quantity = 1,
                Weight = 3,
                Value = 150,
                Stats = new ItemAttributesDTO { Damage = 8 }
            });
            
            // Consumables
            items.Add(new ItemModel
            {
                Id = "potion_health",
                Name = "Health Potion",
                Description = "Restores 50 health points when consumed.",
                Type = ItemType.Consumable,
                Quantity = 5,
                Weight = 1,
                Value = 25,
                IsConsumable = true
            });
            
            // Materials
            items.Add(new ItemModel
            {
                Id = "iron_ore",
                Name = "Iron Ore",
                Description = "Raw iron ore that can be smelted.",
                Type = ItemType.Material,
                Quantity = 12,
                Weight = 2,
                Value = 5
            });
            
            // Armor
            items.Add(new ItemModel
            {
                Id = "leather_armor",
                Name = "Leather Armor",
                Description = "Basic leather armor providing light protection.",
                Type = ItemType.Armor,
                Quantity = 1,
                Weight = 8,
                Value = 200,
                Stats = new ItemAttributesDTO { ArmorClass = 3 }
            });
            
            // Quest item
            items.Add(new ItemModel
            {
                Id = "ancient_key",
                Name = "Ancient Key",
                Description = "A mysterious key with strange markings.",
                Type = ItemType.Quest,
                Quantity = 1,
                Weight = 0,
                Value = 0
            });
            
            return items;
        }
        
        #endregion
        
        #region Display Management
        
        private void RefreshInventoryDisplay()
        {
            ApplyFiltersAndSort();
            UpdateSlotContents();
        }
        
        private void ApplyFiltersAndSort()
        {
            filteredItems = allItems.ToList();
            
            // Apply search filter
            if (!string.IsNullOrEmpty(currentSearchTerm))
            {
                filteredItems = filteredItems.Where(item => 
                    item.Name.ToLower().Contains(currentSearchTerm.ToLower()) ||
                    item.Description.ToLower().Contains(currentSearchTerm.ToLower())
                ).ToList();
            }
            
            // Apply type filter
            if (currentFilter != ItemFilter.All)
            {
                ItemType filterType = GetItemTypeFromFilter(currentFilter);
                filteredItems = filteredItems.Where(item => item.Type == filterType).ToList();
            }
            
            // Apply sorting
            filteredItems = SortItems(filteredItems, currentSortOrder);
        }
        
        private List<ItemModel> SortItems(List<ItemModel> items, SortOrder sortOrder)
        {
            return sortOrder switch
            {
                SortOrder.Name => items.OrderBy(i => i.Name).ToList(),
                SortOrder.Type => items.OrderBy(i => i.Type).ThenBy(i => i.Name).ToList(),
                SortOrder.Value => items.OrderByDescending(i => i.Value).ToList(),
                SortOrder.Weight => items.OrderBy(i => i.Weight).ToList(),
                SortOrder.Quantity => items.OrderByDescending(i => i.Quantity).ToList(),
                SortOrder.RecentlyAdded => items.OrderByDescending(i => i.Id).ToList(),
                _ => items
            };
        }
        
        private void UpdateSlotContents()
        {
            // Clear all slots first
            foreach (var slot in inventorySlots)
            {
                slot.SetItem(null);
            }
            
            // Fill slots with filtered items
            for (int i = 0; i < filteredItems.Count && i < inventorySlots.Count; i++)
            {
                inventorySlots[i].SetItem(filteredItems[i]);
            }
        }
        
        private void UpdateInventoryInfo()
        {
            if (currentInventory == null) return;
            
            // Update weight display
            if (currentWeightText != null)
                currentWeightText.text = $"{currentInventory.CurrentWeight:F1}";
            if (maxWeightText != null)
                maxWeightText.text = $"{currentInventory.MaxWeight:F1}";
            
            // Update weight bar
            if (weightBar != null)
            {
                float weightPercentage = currentInventory.CurrentWeight / currentInventory.MaxWeight;
                weightBar.value = weightPercentage;
                
                // Update weight bar color based on percentage
                var handleImage = weightBar.fillRect.GetComponent<Image>();
                if (handleImage != null)
                {
                    if (weightPercentage >= weightCriticalThreshold)
                        handleImage.color = weightCriticalColor;
                    else if (weightPercentage >= weightWarningThreshold)
                        handleImage.color = weightWarningColor;
                    else
                        handleImage.color = weightNormalColor;
                }
            }
            
            // Update currency
            if (currencyText != null)
                currencyText.text = $"{currentInventory.Currency:N0}";
            
            // Update slots used
            if (slotsUsedText != null)
            {
                int usedSlots = allItems.Count;
                slotsUsedText.text = $"{usedSlots}/{currentInventory.MaxSlots}";
            }
        }
        
        #endregion
        
        #region Event Handlers
        
        private void OnSlotSelected(InventorySlot slot)
        {
            // Deselect previous slot
            if (selectedSlot != null)
                selectedSlot.SetSelected(false);
            
            // Select new slot
            selectedSlot = slot;
            slot.SetSelected(true);
        }
        
        private void OnSlotDoubleClicked(InventorySlot slot)
        {
            if (slot.IsEmpty()) return;
            
            var item = slot.GetItem();
            if (item.IsEquippable)
            {
                OnEquipItem(item);
            }
            else if (item.IsUsable)
            {
                OnUseItem(item);
            }
        }
        
        private void OnItemMoved(InventorySlot fromSlot, InventorySlot toSlot)
        {
            if (fromSlot == null || toSlot == null) return;
            
            var fromItem = fromSlot.GetItem();
            var toItem = toSlot.GetItem();
            
            if (fromItem == null) return;
            
            // Handle stacking if items are the same and stackable
            if (toItem != null && toItem.Id == fromItem.Id && fromItem.IsStackable)
            {
                // Stack items
                toItem.Quantity += fromItem.Quantity;
                fromSlot.SetItem(null);
                toSlot.SetItem(toItem);
            }
            else if (toSlot.CanAcceptItem(fromItem))
            {
                // Swap items
                fromSlot.SetItem(toItem);
                toSlot.SetItem(fromItem);
            }
            
            // Update display
            RefreshInventoryDisplay();
        }
        
        private void OnShowTooltip(ItemModel item)
        {
            if (itemTooltip != null)
            {
                itemTooltip.ShowTooltip(item, Input.mousePosition);
            }
        }
        
        private void OnHideTooltip()
        {
            if (itemTooltip != null)
            {
                itemTooltip.HideTooltip();
            }
        }
        
        private void OnSortChanged(int value)
        {
            currentSortOrder = (SortOrder)value;
            RefreshInventoryDisplay();
        }
        
        private void OnFilterChanged(int value)
        {
            currentFilter = (ItemFilter)value;
            RefreshInventoryDisplay();
        }
        
        private void OnSearchChanged(string searchTerm)
        {
            currentSearchTerm = searchTerm;
            RefreshInventoryDisplay();
        }
        
        #endregion
        
        #region Item Actions
        
        private void OnUseItem(ItemModel item)
        {
            if (item.IsUsable)
            {
                if (item.IsStackable && item.Quantity > 1)
                {
                    item.Quantity--;
                }
                else
                {
                    allItems.Remove(item);
                }
                
                OnItemUsed?.Invoke(item);
                RefreshInventoryDisplay();
                UpdateInventoryInfo();
            }
        }
        
        private void OnEquipItem(ItemModel item)
        {
            if (item.IsEquippable)
            {
                OnItemEquipped?.Invoke(item);
                // Item remains in inventory until equipped
            }
        }
        
        private void OnDropItem(ItemModel item)
        {
            allItems.Remove(item);
            currentInventory.CurrentWeight -= item.Weight * item.Quantity;
            
            OnItemDropped?.Invoke(item);
            RefreshInventoryDisplay();
            UpdateInventoryInfo();
        }
        
        private void OnSplitStack(ItemModel item, int splitAmount)
        {
            if (item.IsStackable && item.Quantity > splitAmount)
            {
                // Create new item with split amount
                var newItem = new ItemModel
                {
                    Id = System.Guid.NewGuid().ToString(),
                    Name = item.Name,
                    Description = item.Description,
                    Type = item.Type,
                    Quantity = splitAmount,
                    Weight = item.Weight,
                    Value = item.Value,
                    IsConsumable = item.IsConsumable,
                    Properties = new Dictionary<string, object>(item.Properties),
                    Stats = item.Stats
                };
                
                // Reduce original stack
                item.Quantity -= splitAmount;
                
                // Add new item to inventory
                allItems.Add(newItem);
                
                RefreshInventoryDisplay();
                UpdateInventoryInfo();
            }
        }
        
        private void OnDestroyItem(ItemModel item)
        {
            allItems.Remove(item);
            currentInventory.CurrentWeight -= item.Weight * item.Quantity;
            
            OnItemDestroyed?.Invoke(item);
            RefreshInventoryDisplay();
            UpdateInventoryInfo();
        }
        
        private void OnSellItem(ItemModel item)
        {
            if (item.CanSell && item.Value > 0)
            {
                // Add currency
                currentInventory.Currency += item.Value * item.Quantity;
                
                // Remove item
                allItems.Remove(item);
                currentInventory.CurrentWeight -= item.Weight * item.Quantity;
                
                OnItemSold?.Invoke(item);
                RefreshInventoryDisplay();
                UpdateInventoryInfo();
            }
        }
        
        private void OnInspectItem(ItemModel item)
        {
            // Show detailed item inspection (could open a separate panel)
            Debug.Log($"Inspecting item: {item.Name}");
        }
        
        private void OnMoveToContainer(ItemModel item)
        {
            // Move item to different bag/container
            Debug.Log($"Moving item to container: {item.Name}");
        }
        
        #endregion
        
        #region Inventory Actions
        
        private void SortAllItems()
        {
            RefreshInventoryDisplay();
        }
        
        private void StackAllItems()
        {
            // Group stackable items and combine stacks
            var stackableGroups = allItems
                .Where(i => i.IsStackable)
                .GroupBy(i => i.Id)
                .Where(g => g.Count() > 1);
            
            foreach (var group in stackableGroups)
            {
                var firstItem = group.First();
                var totalQuantity = group.Sum(i => i.Quantity);
                
                // Remove all but the first item
                var itemsToRemove = group.Skip(1).ToList();
                foreach (var item in itemsToRemove)
                {
                    allItems.Remove(item);
                }
                
                // Update first item quantity
                firstItem.Quantity = totalQuantity;
            }
            
            RefreshInventoryDisplay();
            UpdateInventoryInfo();
        }
        
        private void SellAllJunk()
        {
            // Define junk items (low value, common items)
            var junkItems = allItems.Where(i => 
                i.CanSell && 
                i.Value <= 10 && 
                i.Type == ItemType.Material
            ).ToList();
            
            int totalValue = junkItems.Sum(i => i.Value * i.Quantity);
            float totalWeight = junkItems.Sum(i => i.Weight * i.Quantity);
            
            // Remove junk items
            foreach (var item in junkItems)
            {
                allItems.Remove(item);
            }
            
            // Add currency
            currentInventory.Currency += totalValue;
            currentInventory.CurrentWeight -= totalWeight;
            
            RefreshInventoryDisplay();
            UpdateInventoryInfo();
            
            Debug.Log($"Sold {junkItems.Count} junk items for {totalValue} gold");
        }
        
        private void ExpandInventory()
        {
            // Increase inventory slots (would typically cost currency)
            int expansionCost = 500;
            if (currentInventory.Currency >= expansionCost)
            {
                currentInventory.Currency -= expansionCost;
                currentInventory.MaxSlots += 10;
                
                // Add new slots to UI
                for (int i = 0; i < 10; i++)
                {
                    CreateInventorySlot(inventorySlots.Count);
                }
                
                UpdateInventoryInfo();
                Debug.Log("Inventory expanded by 10 slots");
            }
            else
            {
                Debug.Log("Not enough gold to expand inventory");
            }
        }
        
        private void ResetFilters()
        {
            currentSortOrder = SortOrder.Name;
            currentFilter = ItemFilter.All;
            currentSearchTerm = "";
            
            if (sortDropdown != null) sortDropdown.value = 0;
            if (filterDropdown != null) filterDropdown.value = 0;
            if (searchField != null) searchField.text = "";
            
            RefreshInventoryDisplay();
        }
        
        #endregion
        
        #region Utility Methods
        
        private ItemType GetItemTypeFromFilter(ItemFilter filter)
        {
            return filter switch
            {
                ItemFilter.Weapons => ItemType.Weapon,
                ItemFilter.Armor => ItemType.Armor,
                ItemFilter.Consumables => ItemType.Consumable,
                ItemFilter.Tools => ItemType.Tool,
                ItemFilter.Materials => ItemType.Material,
                ItemFilter.Treasures => ItemType.Treasure,
                ItemFilter.QuestItems => ItemType.Quest,
                _ => ItemType.Weapon
            };
        }
        
        #endregion
        
        #region Public Methods
        
        public void AddItem(ItemModel item)
        {
            if (item == null) return;
            
            // Check for existing stackable item
            var existingItem = allItems.FirstOrDefault(i => 
                i.Id == item.Id && i.IsStackable);
            
            if (existingItem != null)
            {
                existingItem.Quantity += item.Quantity;
            }
            else
            {
                allItems.Add(item);
            }
            
            // Update weight
            currentInventory.CurrentWeight += item.Weight * item.Quantity;
            
            RefreshInventoryDisplay();
            UpdateInventoryInfo();
            OnWeightChanged?.Invoke(currentInventory.CurrentWeight);
        }
        
        public bool RemoveItem(string itemId, int quantity = 1)
        {
            var item = allItems.FirstOrDefault(i => i.Id == itemId);
            if (item == null) return false;
            
            if (item.Quantity > quantity)
            {
                item.Quantity -= quantity;
                currentInventory.CurrentWeight -= item.Weight * quantity;
            }
            else
            {
                currentInventory.CurrentWeight -= item.Weight * item.Quantity;
                allItems.Remove(item);
            }
            
            RefreshInventoryDisplay();
            UpdateInventoryInfo();
            OnWeightChanged?.Invoke(currentInventory.CurrentWeight);
            return true;
        }
        
        public ItemModel GetItem(string itemId)
        {
            return allItems.FirstOrDefault(i => i.Id == itemId);
        }
        
        public bool HasItem(string itemId, int quantity = 1)
        {
            var item = allItems.FirstOrDefault(i => i.Id == itemId);
            return item != null && item.Quantity >= quantity;
        }
        
        public int GetItemCount(string itemId)
        {
            var item = allItems.FirstOrDefault(i => i.Id == itemId);
            return item?.Quantity ?? 0;
        }
        
        public List<ItemModel> GetAllItems()
        {
            return allItems.ToList();
        }
        
        public List<ItemModel> GetItemsByType(ItemType type)
        {
            return allItems.Where(i => i.Type == type).ToList();
        }
        
        #endregion
        
        #region Enums
        
        private enum SortOrder
        {
            Name = 0,
            Type = 1,
            Value = 2,
            Weight = 3,
            Quantity = 4,
            RecentlyAdded = 5
        }
        
        private enum ItemFilter
        {
            All = 0,
            Weapons = 1,
            Armor = 2,
            Consumables = 3,
            Tools = 4,
            Materials = 5,
            Treasures = 6,
            QuestItems = 7
        }
        
        #endregion
    }
} 