using UnityEngine;
using UnityEngine.UI;
using TMPro;
using System;
using System.Collections.Generic;

namespace VisualDM.UI.Panels
{
    /// <summary>
    /// Panel for customizing character armor and equipment.
    /// This is a Unity implementation of the React ArmorPanel component.
    /// </summary>
    public class ArmorPanel : Components.Panel
    {
        [Header("Armor Panel Settings")]
        [SerializeField] private bool autoRefresh = true;
        
        // Equipment slot enum
        public enum EquipmentSlot
        {
            Head,
            Shoulders,
            Chest,
            Arms,
            Hands,
            Waist,
            Legs,
            Feet,
            Accessory1,
            Accessory2
        }
        
        // UI elements
        private Dictionary<EquipmentSlot, Components.CustomButton> slotButtons = new Dictionary<EquipmentSlot, Components.CustomButton>();
        private Dictionary<string, Toggle> toggles = new Dictionary<string, Toggle>();
        private Dictionary<string, Components.CustomButton> buttons = new Dictionary<string, Components.CustomButton>();
        
        // Equipment item data (simplified for this example)
        private Dictionary<EquipmentSlot, string> equippedItems = new Dictionary<EquipmentSlot, string>();
        
        // Events
        public event Action<EquipmentSlot, string> OnEquipmentChanged;
        public event Action<string, bool> OnToggleChanged;
        public event Action<string> OnButtonClicked;
        
        protected override void Awake()
        {
            base.Awake();
            
            // Set panel title
            SetTitle("Armor & Equipment");
        }
        
        protected override void Start()
        {
            base.Start();
            
            // Build UI
            if (autoRefresh)
            {
                BuildUI();
            }
        }
        
        /// <summary>
        /// Builds the UI elements for armor customization
        /// </summary>
        public void BuildUI()
        {
            // Clear existing content
            ClearContent();
            
            // Add equipment slots section
            AddFeatureSection("Equipment Slots");
            
            // Add equipment slots
            foreach (EquipmentSlot slot in System.Enum.GetValues(typeof(EquipmentSlot)))
            {
                AddEquipmentSlot(slot, GetDefaultItemName(slot));
            }
            
            // Add equipment display options
            AddFeatureSection("Display Options");
            AddToggle("Show Helmet", true);
            AddToggle("Show Cloak", true);
            AddToggle("Show Shoulders", true);
            
            // Add armor sets section
            AddFeatureSection("Armor Sets");
            AddButton("Light Armor Set", "Switch to light armor set");
            AddButton("Medium Armor Set", "Switch to medium armor set");
            AddButton("Heavy Armor Set", "Switch to heavy armor set");
            
            // Add randomize button
            AddFeatureSection("Utilities");
            AddButton("Randomize Equipment", "Randomize all equipment slots");
            AddButton("Clear All Slots", "Remove all equipped items");
        }
        
        /// <summary>
        /// Add a section header for a group of related features
        /// </summary>
        public void AddFeatureSection(string title)
        {
            GameObject sectionGO = new GameObject($"Section_{title}");
            RectTransform sectionRect = sectionGO.AddComponent<RectTransform>();
            sectionRect.sizeDelta = new Vector2(0, 30);
            
            TextMeshProUGUI sectionText = sectionGO.AddComponent<TextMeshProUGUI>();
            sectionText.text = title;
            sectionText.alignment = TextAlignmentOptions.MidlineLeft;
            
            UIThemeManager.Instance.ApplyTextStyle(sectionText, UIThemeManager.TextStyle.Subheader);
            
            // Add to panel
            sectionGO.transform.SetParent(GetContentContainer(), false);
        }
        
        /// <summary>
        /// Add an equipment slot with the current equipped item
        /// </summary>
        public Components.CustomButton AddEquipmentSlot(EquipmentSlot slot, string currentItem = "")
        {
            // Create slot container
            GameObject containerGO = new GameObject($"SlotContainer_{slot}");
            RectTransform containerRect = containerGO.AddComponent<RectTransform>();
            containerRect.sizeDelta = new Vector2(0, 40);
            
            // Add horizontal layout
            HorizontalLayoutGroup layout = containerGO.AddComponent<HorizontalLayoutGroup>();
            layout.spacing = 10;
            layout.padding = new RectOffset(5, 5, 5, 5);
            layout.childAlignment = TextAnchor.MiddleLeft;
            layout.childControlWidth = false;
            layout.childForceExpandWidth = false;
            
            // Create slot label
            GameObject labelGO = new GameObject("Label");
            RectTransform labelRect = labelGO.AddComponent<RectTransform>();
            labelRect.sizeDelta = new Vector2(100, 30);
            
            TextMeshProUGUI labelText = labelGO.AddComponent<TextMeshProUGUI>();
            labelText.text = GetSlotDisplayName(slot);
            labelText.alignment = TextAlignmentOptions.MidlineLeft;
            UIThemeManager.Instance.ApplyTextStyle(labelText, UIThemeManager.TextStyle.Body);
            
            // Create equipment button
            GameObject buttonGO = new GameObject("EquipmentButton");
            RectTransform buttonRect = buttonGO.AddComponent<RectTransform>();
            buttonRect.sizeDelta = new Vector2(200, 30);
            
            Components.CustomButton button = buttonGO.AddComponent<Components.CustomButton>();
            button.SetText(string.IsNullOrEmpty(currentItem) ? "None" : currentItem);
            button.SetAriaLabel($"Select {GetSlotDisplayName(slot)} equipment");
            
            // Store current item if provided
            if (!string.IsNullOrEmpty(currentItem))
            {
                equippedItems[slot] = currentItem;
            }
            
            // Add click listener for equipment selection
            button.OnClick += () => {
                OpenEquipmentSelectionUI(slot);
            };
            
            // Set hierarchy
            labelGO.transform.SetParent(containerGO.transform, false);
            buttonGO.transform.SetParent(containerGO.transform, false);
            
            // Add to panel
            containerGO.transform.SetParent(GetContentContainer(), false);
            
            // Store reference
            slotButtons[slot] = button;
            
            return button;
        }
        
        /// <summary>
        /// Add a toggle option
        /// </summary>
        public Toggle AddToggle(string label, bool defaultValue = false)
        {
            // Create toggle container
            GameObject containerGO = new GameObject($"ToggleContainer_{label}");
            RectTransform containerRect = containerGO.AddComponent<RectTransform>();
            containerRect.sizeDelta = new Vector2(0, 40);
            
            // Add horizontal layout
            HorizontalLayoutGroup layout = containerGO.AddComponent<HorizontalLayoutGroup>();
            layout.spacing = 10;
            layout.padding = new RectOffset(5, 5, 5, 5);
            layout.childAlignment = TextAnchor.MiddleLeft;
            layout.childControlWidth = false;
            layout.childForceExpandWidth = false;
            
            // Create toggle GameObject
            GameObject toggleGO = new GameObject("Toggle");
            RectTransform toggleRect = toggleGO.AddComponent<RectTransform>();
            toggleRect.sizeDelta = new Vector2(20, 20);
            
            Toggle toggle = toggleGO.AddComponent<Toggle>();
            toggle.isOn = defaultValue;
            
            // Add required toggle components
            GameObject backgroundGO = new GameObject("Background");
            RectTransform backgroundRect = backgroundGO.AddComponent<RectTransform>();
            backgroundRect.anchorMin = Vector2.zero;
            backgroundRect.anchorMax = Vector2.one;
            backgroundRect.sizeDelta = Vector2.zero;
            
            Image backgroundImage = backgroundGO.AddComponent<Image>();
            backgroundImage.color = UIThemeManager.Instance.secondaryColor;
            
            GameObject checkmarkGO = new GameObject("Checkmark");
            RectTransform checkmarkRect = checkmarkGO.AddComponent<RectTransform>();
            checkmarkRect.anchorMin = new Vector2(0.1f, 0.1f);
            checkmarkRect.anchorMax = new Vector2(0.9f, 0.9f);
            checkmarkRect.sizeDelta = Vector2.zero;
            
            Image checkmarkImage = checkmarkGO.AddComponent<Image>();
            checkmarkImage.color = UIThemeManager.Instance.accentColor;
            
            // Setup toggle references
            backgroundGO.transform.SetParent(toggleGO.transform, false);
            checkmarkGO.transform.SetParent(toggleGO.transform, false);
            
            toggle.targetGraphic = backgroundImage;
            toggle.graphic = checkmarkImage;
            
            // Add label
            GameObject labelGO = new GameObject("Label");
            RectTransform labelRect = labelGO.AddComponent<RectTransform>();
            labelRect.sizeDelta = new Vector2(150, 30);
            
            TextMeshProUGUI labelText = labelGO.AddComponent<TextMeshProUGUI>();
            labelText.text = label;
            labelText.alignment = TextAlignmentOptions.MidlineLeft;
            UIThemeManager.Instance.ApplyTextStyle(labelText, UIThemeManager.TextStyle.Body);
            
            // Add listener
            toggle.onValueChanged.AddListener((value) => {
                OnToggleChanged?.Invoke(label, value);
            });
            
            // Set hierarchy
            toggleGO.transform.SetParent(containerGO.transform, false);
            labelGO.transform.SetParent(containerGO.transform, false);
            
            // Add to panel
            containerGO.transform.SetParent(GetContentContainer(), false);
            
            // Store reference
            toggles[label] = toggle;
            
            return toggle;
        }
        
        /// <summary>
        /// Add a button
        /// </summary>
        public Components.CustomButton AddButton(string text, string ariaLabel = "")
        {
            // Create button GameObject
            GameObject buttonGO = new GameObject($"Button_{text}");
            RectTransform buttonRect = buttonGO.AddComponent<RectTransform>();
            buttonRect.sizeDelta = new Vector2(0, 40);
            
            // Add custom button component
            Components.CustomButton button = buttonGO.AddComponent<Components.CustomButton>();
            button.SetText(text);
            
            if (!string.IsNullOrEmpty(ariaLabel))
            {
                button.SetAriaLabel(ariaLabel);
            }
            
            // Add click listener
            button.OnClick += () => {
                OnButtonClicked?.Invoke(text);
            };
            
            // Add to panel
            buttonGO.transform.SetParent(GetContentContainer(), false);
            
            // Store reference
            buttons[text] = button;
            
            return button;
        }
        
        /// <summary>
        /// Open equipment selection UI for a specific slot
        /// </summary>
        private void OpenEquipmentSelectionUI(EquipmentSlot slot)
        {
            // This would normally open a popup with equipment options
            // For this example, we'll simulate selecting a random item
            string[] possibleItems = GetPossibleItemsForSlot(slot);
            
            if (possibleItems.Length > 0)
            {
                int randomIndex = UnityEngine.Random.Range(0, possibleItems.Length);
                string selectedItem = possibleItems[randomIndex];
                
                // Update UI and data
                EquipItem(slot, selectedItem);
            }
        }
        
        /// <summary>
        /// Get display name for equipment slot
        /// </summary>
        private string GetSlotDisplayName(EquipmentSlot slot)
        {
            switch (slot)
            {
                case EquipmentSlot.Head: return "Head";
                case EquipmentSlot.Shoulders: return "Shoulders";
                case EquipmentSlot.Chest: return "Chest";
                case EquipmentSlot.Arms: return "Arms";
                case EquipmentSlot.Hands: return "Hands";
                case EquipmentSlot.Waist: return "Waist";
                case EquipmentSlot.Legs: return "Legs";
                case EquipmentSlot.Feet: return "Feet";
                case EquipmentSlot.Accessory1: return "Accessory 1";
                case EquipmentSlot.Accessory2: return "Accessory 2";
                default: return slot.ToString();
            }
        }
        
        /// <summary>
        /// Get sample items for an equipment slot
        /// </summary>
        private string[] GetPossibleItemsForSlot(EquipmentSlot slot)
        {
            switch (slot)
            {
                case EquipmentSlot.Head:
                    return new string[] { "Leather Cap", "Chain Coif", "Plate Helm", "Wizard Hat", "Crown" };
                case EquipmentSlot.Shoulders:
                    return new string[] { "Leather Spaulders", "Chain Shoulders", "Pauldrons", "Mantle", "Epaulets" };
                case EquipmentSlot.Chest:
                    return new string[] { "Leather Jerkin", "Chain Mail", "Breast Plate", "Robe", "Tunic" };
                case EquipmentSlot.Arms:
                    return new string[] { "Leather Bracers", "Chain Bracers", "Vambraces", "Arm Wraps", "Armbands" };
                case EquipmentSlot.Hands:
                    return new string[] { "Leather Gloves", "Chain Gloves", "Gauntlets", "Mittens", "Hand Wraps" };
                case EquipmentSlot.Waist:
                    return new string[] { "Leather Belt", "Chain Belt", "Plate Belt", "Sash", "Girdle" };
                case EquipmentSlot.Legs:
                    return new string[] { "Leather Pants", "Chain Leggings", "Plate Greaves", "Trousers", "Skirt" };
                case EquipmentSlot.Feet:
                    return new string[] { "Leather Boots", "Chain Boots", "Plate Sabatons", "Shoes", "Sandals" };
                case EquipmentSlot.Accessory1:
                case EquipmentSlot.Accessory2:
                    return new string[] { "Ring", "Amulet", "Cloak", "Bracelet", "Earring", "Pendant" };
                default:
                    return new string[0];
            }
        }
        
        /// <summary>
        /// Get default item name for a slot
        /// </summary>
        private string GetDefaultItemName(EquipmentSlot slot)
        {
            switch (slot)
            {
                case EquipmentSlot.Head: return "Leather Cap";
                case EquipmentSlot.Chest: return "Leather Jerkin";
                case EquipmentSlot.Legs: return "Leather Pants";
                case EquipmentSlot.Feet: return "Leather Boots";
                default: return "";
            }
        }
        
        /// <summary>
        /// Equip an item to a slot
        /// </summary>
        public void EquipItem(EquipmentSlot slot, string itemName)
        {
            // Update UI
            if (slotButtons.TryGetValue(slot, out Components.CustomButton button))
            {
                button.SetText(itemName);
            }
            
            // Update data
            equippedItems[slot] = itemName;
            
            // Raise event
            OnEquipmentChanged?.Invoke(slot, itemName);
        }
        
        /// <summary>
        /// Remove an item from a slot
        /// </summary>
        public void UnequipItem(EquipmentSlot slot)
        {
            // Update UI
            if (slotButtons.TryGetValue(slot, out Components.CustomButton button))
            {
                button.SetText("None");
            }
            
            // Update data
            if (equippedItems.ContainsKey(slot))
            {
                equippedItems.Remove(slot);
            }
            
            // Raise event
            OnEquipmentChanged?.Invoke(slot, "");
        }
        
        /// <summary>
        /// Clear all equipment slots
        /// </summary>
        public void ClearAllSlots()
        {
            foreach (EquipmentSlot slot in System.Enum.GetValues(typeof(EquipmentSlot)))
            {
                UnequipItem(slot);
            }
        }
        
        /// <summary>
        /// Apply an armor set to all slots
        /// </summary>
        public void ApplyArmorSet(string setName)
        {
            // Clear existing items
            ClearAllSlots();
            
            // Apply new set based on name
            string prefix = "";
            switch (setName.ToLower())
            {
                case "light armor set":
                    prefix = "Leather";
                    break;
                case "medium armor set":
                    prefix = "Chain";
                    break;
                case "heavy armor set":
                    prefix = "Plate";
                    break;
                default:
                    return;
            }
            
            // Apply to all slots
            EquipItem(EquipmentSlot.Head, $"{prefix} Helm");
            EquipItem(EquipmentSlot.Shoulders, $"{prefix} Shoulders");
            EquipItem(EquipmentSlot.Chest, $"{prefix} Chest");
            EquipItem(EquipmentSlot.Arms, $"{prefix} Arms");
            EquipItem(EquipmentSlot.Hands, $"{prefix} Gloves");
            EquipItem(EquipmentSlot.Waist, $"{prefix} Belt");
            EquipItem(EquipmentSlot.Legs, $"{prefix} Legs");
            EquipItem(EquipmentSlot.Feet, $"{prefix} Boots");
        }
        
        /// <summary>
        /// Randomize all equipment slots
        /// </summary>
        public void RandomizeEquipment()
        {
            foreach (EquipmentSlot slot in System.Enum.GetValues(typeof(EquipmentSlot)))
            {
                OpenEquipmentSelectionUI(slot);
            }
        }
    }
} 