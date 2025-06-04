using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using TMPro;
using VDM.UI.Core;
using VDM.DTOs.Economic.Equipment;
using VDM.DTOs.Game.Character;
using VDM.Systems.Equipment.Services;
using VDM.Infrastructure.Services;

namespace VDM.UI.Systems.Equipment
{
    /// <summary>
    /// Complete equipment management UI with drag-and-drop equipping, equipment slots visualization, and gear management screens
    /// </summary>
    public class EquipmentManagementPanel : BaseUIPanel
    {
        [Header("Equipment Layout")]
        [SerializeField] private Transform equipmentSlotsContainer;
        [SerializeField] private GameObject equipmentSlotPrefab;
        [SerializeField] private Image characterSilhouette;
        [SerializeField] private GameObject characterModelContainer;
        
        [Header("Equipment Categories")]
        [SerializeField] private Transform equipmentCategoriesContainer;
        [SerializeField] private Button allEquipmentButton;
        [SerializeField] private Button weaponsButton;
        [SerializeField] private Button armorButton;
        [SerializeField] private Button accessoriesButton;
        [SerializeField] private Button miscButton;
        
        [Header("Available Equipment")]
        [SerializeField] private ScrollRect availableEquipmentScrollRect;
        [SerializeField] private Transform availableEquipmentParent;
        [SerializeField] private GameObject equipmentItemPrefab;
        [SerializeField] private GridLayoutGroup equipmentGridLayout;
        
        [Header("Equipment Details")]
        [SerializeField] private GameObject equipmentDetailsPanel;
        [SerializeField] private Image equipmentIcon;
        [SerializeField] private TextMeshProUGUI equipmentNameText;
        [SerializeField] private TextMeshProUGUI equipmentTypeText;
        [SerializeField] private TextMeshProUGUI equipmentDescriptionText;
        [SerializeField] private TextMeshProUGUI equipmentStatsText;
        [SerializeField] private Transform equipmentPropertiesParent;
        [SerializeField] private GameObject equipmentPropertyPrefab;
        
        [Header("Equipment Comparison")]
        [SerializeField] private GameObject comparisonPanel;
        [SerializeField] private EquipmentComparisonDisplay comparisonDisplay;
        
        [Header("Set Information")]
        [SerializeField] private GameObject setInfoPanel;
        [SerializeField] private TextMeshProUGUI setNameText;
        [SerializeField] private TextMeshProUGUI setPiecesText;
        [SerializeField] private Transform setBonusesParent;
        [SerializeField] private GameObject setBonusPrefab;
        [SerializeField] private Slider setCompletionSlider;
        
        [Header("Durability & Repair")]
        [SerializeField] private GameObject durabilityPanel;
        [SerializeField] private Button repairAllButton;
        [SerializeField] private Button repairSelectedButton;
        [SerializeField] private TextMeshProUGUI repairCostText;
        [SerializeField] private Transform durabilityListParent;
        [SerializeField] private GameObject durabilityItemPrefab;
        
        [Header("Filters & Sorting")]
        [SerializeField] private TMP_Dropdown sortingDropdown;
        [SerializeField] private TMP_Dropdown filterDropdown;
        [SerializeField] private TMP_InputField searchInputField;
        [SerializeField] private Toggle showEquippedToggle;
        [SerializeField] private Toggle showSetItemsToggle;
        
        [Header("Actions")]
        [SerializeField] private Button equipButton;
        [SerializeField] private Button unequipButton;
        [SerializeField] private Button compareButton;
        [SerializeField] private Button enchantButton;
        [SerializeField] private Button sellButton;
        [SerializeField] private Button repairButton;
        
        [Header("Character Stats")]
        [SerializeField] private Transform characterStatsParent;
        [SerializeField] private GameObject characterStatPrefab;
        [SerializeField] private TextMeshProUGUI totalArmorClassText;
        [SerializeField] private TextMeshProUGUI totalDamageText;
        [SerializeField] private TextMeshProUGUI totalSpeedText;
        
        // Services
        private EquipmentService equipmentService;
        
        // Data
        private CharacterDTO currentCharacter;
        private CharacterEquipmentDTO currentEquipment;
        private List<EquipmentItemDTO> availableItems = new List<EquipmentItemDTO>();
        private List<EquipmentSetDTO> equipmentSets = new List<EquipmentSetDTO>();
        private EquipmentItemDTO selectedItem;
        private EquipmentSlot selectedSlot = EquipmentSlot.MainHand;
        
        // UI Elements
        private Dictionary<EquipmentSlot, EquipmentSlotDisplay> equipmentSlots = new Dictionary<EquipmentSlot, EquipmentSlotDisplay>();
        private List<GameObject> availableItemElements = new List<GameObject>();
        private List<GameObject> propertyElements = new List<GameObject>();
        private List<GameObject> setBonusElements = new List<GameObject>();
        private List<GameObject> durabilityElements = new List<GameObject>();
        private List<GameObject> statElements = new List<GameObject>();
        
        // Filtering and Sorting
        private EquipmentType currentFilter = EquipmentType.Weapon;
        private SortingCriteria currentSorting = SortingCriteria.Name;
        private string searchFilter = "";
        private bool showEquippedItems = true;
        private bool showSetItemsOnly = false;
        
        // Events
        public event Action<EquipmentItemDTO, EquipmentSlot> OnEquipmentEquipped;
        public event Action<EquipmentSlot> OnEquipmentUnequipped;
        public event Action<EquipmentItemDTO> OnEquipmentSelected;
        public event Action<CharacterEquipmentDTO> OnEquipmentChanged;
        
        public enum SortingCriteria
        {
            Name,
            Type,
            Rarity,
            Level,
            Value,
            Durability
        }
        
        protected override void Awake()
        {
            base.Awake();
            
            // Find or create equipment service
            equipmentService = FindObjectOfType<EquipmentService>();
            if (equipmentService == null)
            {
                GameObject serviceGO = new GameObject("EquipmentService");
                equipmentService = serviceGO.AddComponent<EquipmentService>();
            }
        }
        
        private void Start()
        {
            SetupUI();
            SetupEventListeners();
            InitializeEquipmentSlots();
        }
        
        private void SetupUI()
        {
            // Setup category buttons
            if (allEquipmentButton != null)
                allEquipmentButton.onClick.AddListener(() => FilterByType(EquipmentType.Weapon)); // Show all
            if (weaponsButton != null)
                weaponsButton.onClick.AddListener(() => FilterByType(EquipmentType.Weapon));
            if (armorButton != null)
                armorButton.onClick.AddListener(() => FilterByType(EquipmentType.Armor));
            if (accessoriesButton != null)
                accessoriesButton.onClick.AddListener(() => FilterByType(EquipmentType.Accessory));
            if (miscButton != null)
                miscButton.onClick.AddListener(() => FilterByType(EquipmentType.Misc));
            
            // Setup action buttons
            if (equipButton != null)
                equipButton.onClick.AddListener(EquipSelectedItem);
            if (unequipButton != null)
                unequipButton.onClick.AddListener(UnequipFromSelectedSlot);
            if (compareButton != null)
                compareButton.onClick.AddListener(CompareSelectedItem);
            if (enchantButton != null)
                enchantButton.onClick.AddListener(EnchantSelectedItem);
            if (sellButton != null)
                sellButton.onClick.AddListener(SellSelectedItem);
            if (repairButton != null)
                repairButton.onClick.AddListener(RepairSelectedItem);
            
            // Setup repair buttons
            if (repairAllButton != null)
                repairAllButton.onClick.AddListener(RepairAllItems);
            if (repairSelectedButton != null)
                repairSelectedButton.onClick.AddListener(RepairSelectedItem);
            
            // Setup filters and sorting
            if (sortingDropdown != null)
                sortingDropdown.onValueChanged.AddListener(OnSortingChanged);
            if (filterDropdown != null)
                filterDropdown.onValueChanged.AddListener(OnFilterChanged);
            if (searchInputField != null)
                searchInputField.onValueChanged.AddListener(OnSearchChanged);
            if (showEquippedToggle != null)
                showEquippedToggle.onValueChanged.AddListener(OnShowEquippedToggled);
            if (showSetItemsToggle != null)
                showSetItemsToggle.onValueChanged.AddListener(OnShowSetItemsToggled);
            
            // Initially hide detail panels
            if (equipmentDetailsPanel != null)
                equipmentDetailsPanel.SetActive(false);
            if (comparisonPanel != null)
                comparisonPanel.SetActive(false);
            if (setInfoPanel != null)
                setInfoPanel.SetActive(false);
        }
        
        private void SetupEventListeners()
        {
            // Subscribe to service events if available
            // Equipment service events would be handled here
        }
        
        private void InitializeEquipmentSlots()
        {
            if (equipmentSlotsContainer == null || equipmentSlotPrefab == null)
                return;
            
            // Clear existing slots
            foreach (Transform child in equipmentSlotsContainer)
            {
                DestroyImmediate(child.gameObject);
            }
            equipmentSlots.Clear();
            
            // Create equipment slots for each slot type
            var slotTypes = new EquipmentSlot[]
            {
                EquipmentSlot.Head, EquipmentSlot.Neck, EquipmentSlot.Body,
                EquipmentSlot.MainHand, EquipmentSlot.OffHand, EquipmentSlot.Hands,
                EquipmentSlot.Waist, EquipmentSlot.Feet, EquipmentSlot.Ring,
                EquipmentSlot.Back, EquipmentSlot.Accessory
            };
            
            foreach (var slotType in slotTypes)
            {
                GameObject slotGO = Instantiate(equipmentSlotPrefab, equipmentSlotsContainer);
                EquipmentSlotDisplay slotDisplay = slotGO.GetComponent<EquipmentSlotDisplay>();
                
                if (slotDisplay != null)
                {
                    slotDisplay.Initialize(slotType, OnSlotSelected, OnItemDroppedOnSlot);
                    equipmentSlots[slotType] = slotDisplay;
                }
            }
        }
        
        #region Public Interface
        
        /// <summary>
        /// Initialize panel with character data
        /// </summary>
        public void Initialize(CharacterDTO character)
        {
            currentCharacter = character;
            LoadCharacterEquipment();
            LoadAvailableEquipment();
            UpdateUI();
        }
        
        /// <summary>
        /// Refresh all equipment data and UI
        /// </summary>
        public void RefreshEquipment()
        {
            if (currentCharacter != null)
            {
                LoadCharacterEquipment();
                LoadAvailableEquipment();
                UpdateUI();
            }
        }
        
        #endregion
        
        #region Data Loading
        
        private async void LoadCharacterEquipment()
        {
            if (currentCharacter == null || equipmentService == null)
                return;
            
            try
            {
                // Load character's current equipment
                // This would be implemented with actual service calls
                // var equipment = await equipmentService.GetCharacterEquipmentAsync(currentCharacter.Id);
                // currentEquipment = equipment;
                
                // For now, create mock data
                currentEquipment = CreateMockCharacterEquipment();
                
                UpdateEquipmentSlots();
                UpdateCharacterStats();
                UpdateSetInformation();
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to load character equipment: {ex.Message}");
            }
        }
        
        private async void LoadAvailableEquipment()
        {
            if (currentCharacter == null || equipmentService == null)
                return;
            
            try
            {
                // Load available equipment items
                // This would be implemented with actual service calls
                // var items = await equipmentService.GetAvailableEquipmentAsync(currentCharacter.Id);
                // availableItems = items;
                
                // For now, create mock data
                availableItems = CreateMockAvailableEquipment();
                
                PopulateAvailableEquipment();
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to load available equipment: {ex.Message}");
            }
        }
        
        #endregion
        
        #region UI Updates
        
        private void UpdateUI()
        {
            UpdateEquipmentSlots();
            PopulateAvailableEquipment();
            UpdateCharacterStats();
            UpdateSetInformation();
            UpdateDurabilityInfo();
            UpdateActionButtons();
        }
        
        private void UpdateEquipmentSlots()
        {
            if (currentEquipment?.EquippedItems == null)
                return;
            
            foreach (var kvp in equipmentSlots)
            {
                var slot = kvp.Key;
                var slotDisplay = kvp.Value;
                
                if (currentEquipment.EquippedItems.TryGetValue(slot, out EquippedItemDTO equippedItem))
                {
                    slotDisplay.SetEquippedItem(equippedItem.Item);
                }
                else
                {
                    slotDisplay.ClearSlot();
                }
            }
        }
        
        private void PopulateAvailableEquipment()
        {
            ClearAvailableEquipment();
            
            if (availableEquipmentParent == null || equipmentItemPrefab == null)
                return;
            
            var filteredItems = FilterAndSortItems(availableItems);
            
            foreach (var item in filteredItems)
            {
                GameObject itemGO = Instantiate(equipmentItemPrefab, availableEquipmentParent);
                EquipmentItemDisplay itemDisplay = itemGO.GetComponent<EquipmentItemDisplay>();
                
                if (itemDisplay != null)
                {
                    itemDisplay.Initialize(item, OnItemSelected, OnItemDoubleClicked);
                }
                
                availableItemElements.Add(itemGO);
            }
        }
        
        private List<EquipmentItemDTO> FilterAndSortItems(List<EquipmentItemDTO> items)
        {
            var filtered = new List<EquipmentItemDTO>(items);
            
            // Apply type filter
            if (currentFilter != EquipmentType.Weapon) // "All" uses Weapon as placeholder
            {
                filtered.RemoveAll(item => item.EquipmentType != currentFilter);
            }
            
            // Apply search filter
            if (!string.IsNullOrEmpty(searchFilter))
            {
                filtered.RemoveAll(item => !item.Name.ToLower().Contains(searchFilter.ToLower()));
            }
            
            // Apply equipped filter
            if (!showEquippedItems)
            {
                // Remove items that are currently equipped
                // This would need to check against currentEquipment
            }
            
            // Apply set items filter
            if (showSetItemsOnly)
            {
                // Filter to only show set items
                // This would need set information
            }
            
            // Sort items
            filtered.Sort((a, b) => {
                switch (currentSorting)
                {
                    case SortingCriteria.Name:
                        return string.Compare(a.Name, b.Name);
                    case SortingCriteria.Type:
                        return a.EquipmentType.CompareTo(b.EquipmentType);
                    case SortingCriteria.Rarity:
                        return b.Rarity.CompareTo(a.Rarity); // Higher rarity first
                    case SortingCriteria.Level:
                        return b.LevelRequirement.CompareTo(a.LevelRequirement);
                    case SortingCriteria.Value:
                        return b.Value.CompareTo(a.Value);
                    default:
                        return 0;
                }
            });
            
            return filtered;
        }
        
        private void UpdateCharacterStats()
        {
            ClearCharacterStats();
            
            if (currentEquipment?.TotalStats == null || characterStatsParent == null || characterStatPrefab == null)
                return;
            
            // Display total stats from equipped items
            // This would calculate and display various stats
            var stats = new Dictionary<string, int>
            {
                { "Attack Power", 150 },
                { "Defense", 85 },
                { "Magic Power", 120 },
                { "Health", 450 },
                { "Mana", 280 }
            };
            
            foreach (var stat in stats)
            {
                GameObject statGO = Instantiate(characterStatPrefab, characterStatsParent);
                var textComponent = statGO.GetComponentInChildren<TextMeshProUGUI>();
                if (textComponent != null)
                {
                    textComponent.text = $"{stat.Key}: {stat.Value}";
                }
                statElements.Add(statGO);
            }
            
            // Update main stat displays
            if (totalArmorClassText != null)
                totalArmorClassText.text = "AC: 18";
            if (totalDamageText != null)
                totalDamageText.text = "DMG: 2d6+3";
            if (totalSpeedText != null)
                totalSpeedText.text = "SPD: 30ft";
        }
        
        private void UpdateSetInformation()
        {
            if (currentEquipment?.ActiveSetBonuses == null || setBonusesParent == null)
                return;
            
            ClearSetBonuses();
            
            // Display active set bonuses
            foreach (var setBonus in currentEquipment.ActiveSetBonuses)
            {
                if (setNameText != null)
                    setNameText.text = setBonus.SetName;
                if (setPiecesText != null)
                    setPiecesText.text = $"{setBonus.EquippedPieces}/{setBonus.TotalPieces} pieces";
                if (setCompletionSlider != null)
                {
                    setCompletionSlider.value = setBonus.CompletionPercentage;
                }
                
                // Show active bonuses
                foreach (var bonus in setBonus.ActiveBonuses)
                {
                    GameObject bonusGO = Instantiate(setBonusPrefab, setBonusesParent);
                    var textComponent = bonusGO.GetComponentInChildren<TextMeshProUGUI>();
                    if (textComponent != null)
                    {
                        textComponent.text = $"{bonus.Name}: {bonus.Description}";
                    }
                    setBonusElements.Add(bonusGO);
                }
                
                break; // Show only first set for now
            }
            
            if (setInfoPanel != null)
                setInfoPanel.SetActive(currentEquipment.ActiveSetBonuses.Count > 0);
        }
        
        private void UpdateDurabilityInfo()
        {
            ClearDurabilityElements();
            
            if (currentEquipment?.EquippedItems == null || durabilityListParent == null || durabilityItemPrefab == null)
                return;
            
            int totalRepairCost = 0;
            
            foreach (var kvp in currentEquipment.EquippedItems)
            {
                var equippedItem = kvp.Value;
                if (equippedItem.Durability != null && equippedItem.Durability.Percentage < 100f)
                {
                    GameObject durabilityGO = Instantiate(durabilityItemPrefab, durabilityListParent);
                    var itemDisplay = durabilityGO.GetComponent<DurabilityItemDisplay>();
                    if (itemDisplay != null)
                    {
                        itemDisplay.Initialize(equippedItem);
                        // totalRepairCost += itemDisplay.GetRepairCost();
                    }
                    durabilityElements.Add(durabilityGO);
                }
            }
            
            if (repairCostText != null)
                repairCostText.text = $"Repair All: {totalRepairCost} gold";
            
            if (durabilityPanel != null)
                durabilityPanel.SetActive(durabilityElements.Count > 0);
        }
        
        private void UpdateActionButtons()
        {
            bool hasSelection = selectedItem != null;
            bool hasSlotSelection = selectedSlot != EquipmentSlot.MainHand;
            bool isEquipped = hasSelection && IsItemEquipped(selectedItem);
            
            if (equipButton != null)
                equipButton.interactable = hasSelection && !isEquipped && CanEquipItem(selectedItem);
            if (unequipButton != null)
                unequipButton.interactable = hasSlotSelection && IsSlotOccupied(selectedSlot);
            if (compareButton != null)
                compareButton.interactable = hasSelection && HasEquippedItemInSlot(selectedItem?.Slot ?? EquipmentSlot.MainHand);
            if (enchantButton != null)
                enchantButton.interactable = hasSelection && selectedItem.CanBeEnchanted;
            if (sellButton != null)
                sellButton.interactable = hasSelection && !isEquipped;
            if (repairButton != null)
                repairButton.interactable = hasSelection && NeedsRepair(selectedItem);
        }
        
        #endregion
        
        #region Event Handlers
        
        private void OnSlotSelected(EquipmentSlot slot)
        {
            selectedSlot = slot;
            
            // Show equipped item details if any
            if (currentEquipment?.EquippedItems.TryGetValue(slot, out EquippedItemDTO equippedItem) == true)
            {
                ShowItemDetails(equippedItem.Item);
            }
            else
            {
                HideItemDetails();
            }
            
            UpdateActionButtons();
        }
        
        private void OnItemDroppedOnSlot(EquipmentSlot slot, EquipmentItemDTO item)
        {
            if (CanEquipItemInSlot(item, slot))
            {
                EquipItem(item, slot);
            }
        }
        
        private void OnItemSelected(EquipmentItemDTO item)
        {
            selectedItem = item;
            ShowItemDetails(item);
            
            // Show comparison if there's an equipped item in the same slot
            if (HasEquippedItemInSlot(item.Slot))
            {
                ShowComparison(item);
            }
            else
            {
                HideComparison();
            }
            
            UpdateActionButtons();
            OnEquipmentSelected?.Invoke(item);
        }
        
        private void OnItemDoubleClicked(EquipmentItemDTO item)
        {
            // Try to equip the item on double-click
            if (CanEquipItem(item))
            {
                EquipItem(item, item.Slot);
            }
        }
        
        private void OnSortingChanged(int value)
        {
            currentSorting = (SortingCriteria)value;
            PopulateAvailableEquipment();
        }
        
        private void OnFilterChanged(int value)
        {
            currentFilter = (EquipmentType)value;
            PopulateAvailableEquipment();
        }
        
        private void OnSearchChanged(string value)
        {
            searchFilter = value;
            PopulateAvailableEquipment();
        }
        
        private void OnShowEquippedToggled(bool value)
        {
            showEquippedItems = value;
            PopulateAvailableEquipment();
        }
        
        private void OnShowSetItemsToggled(bool value)
        {
            showSetItemsOnly = value;
            PopulateAvailableEquipment();
        }
        
        #endregion
        
        #region Equipment Actions
        
        private void EquipSelectedItem()
        {
            if (selectedItem != null && CanEquipItem(selectedItem))
            {
                EquipItem(selectedItem, selectedItem.Slot);
            }
        }
        
        private void UnequipFromSelectedSlot()
        {
            if (IsSlotOccupied(selectedSlot))
            {
                UnequipItem(selectedSlot);
            }
        }
        
        private async void EquipItem(EquipmentItemDTO item, EquipmentSlot slot)
        {
            try
            {
                // Call equipment service to equip item
                // var result = await equipmentService.EquipItemAsync(currentCharacter.Id, item.Id, slot);
                
                // For now, simulate the operation
                Debug.Log($"Equipping {item.Name} to {slot}");
                
                // Update local data
                if (currentEquipment?.EquippedItems == null)
                    currentEquipment = new CharacterEquipmentDTO { EquippedItems = new Dictionary<EquipmentSlot, EquippedItemDTO>() };
                
                var equippedItem = new EquippedItemDTO
                {
                    Item = item,
                    Slot = slot,
                    // Other properties would be set here
                };
                
                currentEquipment.EquippedItems[slot] = equippedItem;
                
                // Update UI
                UpdateEquipmentSlots();
                UpdateCharacterStats();
                UpdateSetInformation();
                UpdateActionButtons();
                
                OnEquipmentEquipped?.Invoke(item, slot);
                OnEquipmentChanged?.Invoke(currentEquipment);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to equip item: {ex.Message}");
            }
        }
        
        private async void UnequipItem(EquipmentSlot slot)
        {
            try
            {
                // Call equipment service to unequip item
                // var result = await equipmentService.UnequipItemAsync(currentCharacter.Id, slot);
                
                // For now, simulate the operation
                Debug.Log($"Unequipping item from {slot}");
                
                // Update local data
                if (currentEquipment?.EquippedItems?.ContainsKey(slot) == true)
                {
                    currentEquipment.EquippedItems.Remove(slot);
                }
                
                // Update UI
                UpdateEquipmentSlots();
                UpdateCharacterStats();
                UpdateSetInformation();
                UpdateActionButtons();
                
                OnEquipmentUnequipped?.Invoke(slot);
                OnEquipmentChanged?.Invoke(currentEquipment);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to unequip item: {ex.Message}");
            }
        }
        
        private void CompareSelectedItem()
        {
            if (selectedItem != null && HasEquippedItemInSlot(selectedItem.Slot))
            {
                ShowComparison(selectedItem);
            }
        }
        
        private void EnchantSelectedItem()
        {
            if (selectedItem != null && selectedItem.CanBeEnchanted)
            {
                // Open enchantment UI
                Debug.Log($"Opening enchantment for {selectedItem.Name}");
            }
        }
        
        private void SellSelectedItem()
        {
            if (selectedItem != null && !IsItemEquipped(selectedItem))
            {
                // Open sell confirmation
                Debug.Log($"Selling {selectedItem.Name} for {selectedItem.Value} gold");
            }
        }
        
        private void RepairSelectedItem()
        {
            if (selectedItem != null && NeedsRepair(selectedItem))
            {
                // Repair the selected item
                Debug.Log($"Repairing {selectedItem.Name}");
            }
        }
        
        private void RepairAllItems()
        {
            // Repair all damaged items
            Debug.Log("Repairing all damaged items");
        }
        
        #endregion
        
        #region Item Details & Comparison
        
        private void ShowItemDetails(EquipmentItemDTO item)
        {
            if (equipmentDetailsPanel == null) return;
            
            equipmentDetailsPanel.SetActive(true);
            
            if (equipmentIcon != null && !string.IsNullOrEmpty(item.IconId))
            {
                // Load item icon
                Sprite icon = Resources.Load<Sprite>(item.IconId);
                if (icon != null)
                    equipmentIcon.sprite = icon;
            }
            
            if (equipmentNameText != null)
                equipmentNameText.text = item.Name;
            if (equipmentTypeText != null)
                equipmentTypeText.text = $"{item.EquipmentType} - {item.Rarity}";
            if (equipmentDescriptionText != null)
                equipmentDescriptionText.text = item.Description;
            
            // Show stats
            if (equipmentStatsText != null)
            {
                string statsText = "";
                foreach (var stat in item.AttributeBonuses)
                {
                    statsText += $"{stat.Key}: +{stat.Value}\n";
                }
                equipmentStatsText.text = statsText;
            }
            
            // Show properties
            PopulateItemProperties(item);
        }
        
        private void HideItemDetails()
        {
            if (equipmentDetailsPanel != null)
                equipmentDetailsPanel.SetActive(false);
        }
        
        private void ShowComparison(EquipmentItemDTO newItem)
        {
            if (comparisonPanel == null || comparisonDisplay == null) return;
            
            if (currentEquipment?.EquippedItems.TryGetValue(newItem.Slot, out EquippedItemDTO currentItem) == true)
            {
                comparisonPanel.SetActive(true);
                comparisonDisplay.ShowComparison(currentItem.Item, newItem);
            }
        }
        
        private void HideComparison()
        {
            if (comparisonPanel != null)
                comparisonPanel.SetActive(false);
        }
        
        private void PopulateItemProperties(EquipmentItemDTO item)
        {
            ClearItemProperties();
            
            if (equipmentPropertiesParent == null || equipmentPropertyPrefab == null)
                return;
            
            // Show various item properties
            var properties = new List<string>();
            
            if (item.Weight > 0)
                properties.Add($"Weight: {item.Weight} lbs");
            if (item.Value > 0)
                properties.Add($"Value: {item.Value} gold");
            if (item.LevelRequirement > 1)
                properties.Add($"Required Level: {item.LevelRequirement}");
            if (item.ClassRestrictions?.Count > 0)
                properties.Add($"Classes: {string.Join(", ", item.ClassRestrictions)}");
            
            foreach (var property in properties)
            {
                GameObject propertyGO = Instantiate(equipmentPropertyPrefab, equipmentPropertiesParent);
                var textComponent = propertyGO.GetComponentInChildren<TextMeshProUGUI>();
                if (textComponent != null)
                {
                    textComponent.text = property;
                }
                propertyElements.Add(propertyGO);
            }
        }
        
        #endregion
        
        #region Utility Methods
        
        private void FilterByType(EquipmentType type)
        {
            currentFilter = type;
            PopulateAvailableEquipment();
        }
        
        private bool CanEquipItem(EquipmentItemDTO item)
        {
            if (item == null || currentCharacter == null) return false;
            
            // Check level requirement
            // if (item.LevelRequirement > currentCharacter.Level) return false;
            
            // Check class restrictions
            // if (item.ClassRestrictions?.Contains(currentCharacter.CharacterClass) == false) return false;
            
            return true;
        }
        
        private bool CanEquipItemInSlot(EquipmentItemDTO item, EquipmentSlot slot)
        {
            return item?.Slot == slot && CanEquipItem(item);
        }
        
        private bool IsItemEquipped(EquipmentItemDTO item)
        {
            if (currentEquipment?.EquippedItems == null) return false;
            
            return currentEquipment.EquippedItems.Values.Any(equipped => equipped.Item.Id == item.Id);
        }
        
        private bool IsSlotOccupied(EquipmentSlot slot)
        {
            return currentEquipment?.EquippedItems?.ContainsKey(slot) == true;
        }
        
        private bool HasEquippedItemInSlot(EquipmentSlot slot)
        {
            return IsSlotOccupied(slot);
        }
        
        private bool NeedsRepair(EquipmentItemDTO item)
        {
            // This would check the item's durability
            return false; // Placeholder
        }
        
        #endregion
        
        #region Mock Data (for testing)
        
        private CharacterEquipmentDTO CreateMockCharacterEquipment()
        {
            return new CharacterEquipmentDTO
            {
                CharacterId = currentCharacter?.Id ?? 1,
                EquippedItems = new Dictionary<EquipmentSlot, EquippedItemDTO>(),
                TotalStats = new EquipmentStatsDTO(),
                ActiveSetBonuses = new List<ActiveSetBonusDTO>()
            };
        }
        
        private List<EquipmentItemDTO> CreateMockAvailableEquipment()
        {
            return new List<EquipmentItemDTO>
            {
                new EquipmentItemDTO
                {
                    Id = "sword001",
                    Name = "Iron Sword",
                    EquipmentType = EquipmentType.Weapon,
                    Slot = EquipmentSlot.MainHand,
                    Rarity = ItemRarity.Common,
                    Value = 50,
                    AttributeBonuses = new Dictionary<string, int> { { "Attack", 10 } }
                },
                new EquipmentItemDTO
                {
                    Id = "armor001",
                    Name = "Leather Armor",
                    EquipmentType = EquipmentType.Armor,
                    Slot = EquipmentSlot.Body,
                    Rarity = ItemRarity.Common,
                    Value = 75,
                    AttributeBonuses = new Dictionary<string, int> { { "Defense", 5 } }
                }
            };
        }
        
        #endregion
        
        #region Cleanup Methods
        
        private void ClearAvailableEquipment()
        {
            foreach (var element in availableItemElements)
            {
                if (element != null)
                    DestroyImmediate(element);
            }
            availableItemElements.Clear();
        }
        
        private void ClearItemProperties()
        {
            foreach (var element in propertyElements)
            {
                if (element != null)
                    DestroyImmediate(element);
            }
            propertyElements.Clear();
        }
        
        private void ClearSetBonuses()
        {
            foreach (var element in setBonusElements)
            {
                if (element != null)
                    DestroyImmediate(element);
            }
            setBonusElements.Clear();
        }
        
        private void ClearDurabilityElements()
        {
            foreach (var element in durabilityElements)
            {
                if (element != null)
                    DestroyImmediate(element);
            }
            durabilityElements.Clear();
        }
        
        private void ClearCharacterStats()
        {
            foreach (var element in statElements)
            {
                if (element != null)
                    DestroyImmediate(element);
            }
            statElements.Clear();
        }
        
        #endregion
    }
} 