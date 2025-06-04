using System;
using UnityEngine;
using UnityEngine.UI;
using TMPro;
using VDM.DTOs.Economic.Equipment;

namespace VDM.UI.Systems.Equipment
{
    /// <summary>
    /// Display component for items that need repair, showing durability status and repair costs
    /// </summary>
    public class DurabilityItemDisplay : MonoBehaviour
    {
        [Header("Item Display")]
        [SerializeField] private Image itemIcon;
        [SerializeField] private TextMeshProUGUI itemNameText;
        [SerializeField] private TextMeshProUGUI slotText;
        [SerializeField] private Image rarityBorder;
        
        [Header("Durability Display")]
        [SerializeField] private Slider durabilitySlider;
        [SerializeField] private Image durabilityFill;
        [SerializeField] private TextMeshProUGUI durabilityPercentageText;
        [SerializeField] private TextMeshProUGUI durabilityStatusText;
        
        [Header("Repair Information")]
        [SerializeField] private TextMeshProUGUI repairCostText;
        [SerializeField] private Button repairButton;
        [SerializeField] private GameObject cannotRepairIndicator;
        [SerializeField] private TextMeshProUGUI cannotRepairReasonText;
        
        [Header("Visual States")]
        [SerializeField] private Color highDurabilityColor = Color.green;
        [SerializeField] private Color mediumDurabilityColor = Color.yellow;
        [SerializeField] private Color lowDurabilityColor = Color.red;
        [SerializeField] private Color brokenColor = Color.black;
        
        [Header("Priority Indicators")]
        [SerializeField] private GameObject criticalPriorityIndicator;
        [SerializeField] private GameObject highPriorityIndicator;
        [SerializeField] private GameObject mediumPriorityIndicator;
        [SerializeField] private GameObject lowPriorityIndicator;
        
        // Data
        private EquippedItemDTO equippedItem;
        private DurabilityInfo durabilityInfo;
        private RepairInfo repairInfo;
        
        // Events
        public event Action<EquippedItemDTO> OnRepairRequested;
        public event Action<EquippedItemDTO> OnItemSelected;
        
        private void Awake()
        {
            if (repairButton != null)
                repairButton.onClick.AddListener(RequestRepair);
        }
        
        /// <summary>
        /// Initialize the durability display with equipped item data
        /// </summary>
        public void Initialize(EquippedItemDTO item)
        {
            equippedItem = item;
            durabilityInfo = GetDurabilityInfo(item);
            repairInfo = CalculateRepairInfo(item, durabilityInfo);
            
            UpdateDisplay();
        }
        
        /// <summary>
        /// Update the display with current data
        /// </summary>
        public void UpdateDisplay()
        {
            if (equippedItem?.Item == null)
                return;
            
            UpdateItemDisplay();
            UpdateDurabilityDisplay();
            UpdateRepairDisplay();
            UpdatePriorityIndicators();
        }
        
        /// <summary>
        /// Get the repair cost for this item
        /// </summary>
        public int GetRepairCost()
        {
            return repairInfo?.Cost ?? 0;
        }
        
        /// <summary>
        /// Check if this item can be repaired
        /// </summary>
        public bool CanRepair()
        {
            return repairInfo?.CanRepair ?? false;
        }
        
        private void UpdateItemDisplay()
        {
            var item = equippedItem.Item;
            
            // Set item icon
            if (itemIcon != null && !string.IsNullOrEmpty(item.IconId))
            {
                Sprite icon = Resources.Load<Sprite>(item.IconId);
                if (icon != null)
                    itemIcon.sprite = icon;
            }
            
            // Set item name
            if (itemNameText != null)
                itemNameText.text = item.Name;
            
            // Set slot information
            if (slotText != null)
                slotText.text = GetSlotDisplayName(equippedItem.Slot);
            
            // Set rarity border
            if (rarityBorder != null)
                rarityBorder.color = GetRarityColor(item.Rarity);
        }
        
        private void UpdateDurabilityDisplay()
        {
            if (durabilityInfo == null)
                return;
            
            // Update durability slider
            if (durabilitySlider != null)
            {
                durabilitySlider.value = durabilityInfo.Percentage / 100f;
            }
            
            // Update durability fill color
            if (durabilityFill != null)
            {
                durabilityFill.color = GetDurabilityColor(durabilityInfo.Percentage);
            }
            
            // Update percentage text
            if (durabilityPercentageText != null)
            {
                durabilityPercentageText.text = $"{durabilityInfo.Percentage:F0}%";
                durabilityPercentageText.color = GetDurabilityColor(durabilityInfo.Percentage);
            }
            
            // Update status text
            if (durabilityStatusText != null)
            {
                durabilityStatusText.text = GetDurabilityStatusText(durabilityInfo.Percentage);
                durabilityStatusText.color = GetDurabilityColor(durabilityInfo.Percentage);
            }
        }
        
        private void UpdateRepairDisplay()
        {
            if (repairInfo == null)
                return;
            
            // Update repair cost
            if (repairCostText != null)
            {
                if (repairInfo.CanRepair)
                {
                    repairCostText.text = $"{repairInfo.Cost} gold";
                    repairCostText.color = Color.white;
                }
                else
                {
                    repairCostText.text = "Cannot Repair";
                    repairCostText.color = Color.red;
                }
            }
            
            // Update repair button
            if (repairButton != null)
            {
                repairButton.interactable = repairInfo.CanRepair;
                
                var buttonText = repairButton.GetComponentInChildren<TextMeshProUGUI>();
                if (buttonText != null)
                {
                    buttonText.text = repairInfo.CanRepair ? "Repair" : "Cannot Repair";
                }
            }
            
            // Show/hide cannot repair indicator
            if (cannotRepairIndicator != null)
                cannotRepairIndicator.SetActive(!repairInfo.CanRepair);
            
            if (cannotRepairReasonText != null && !repairInfo.CanRepair)
                cannotRepairReasonText.text = repairInfo.CannotRepairReason ?? "Unknown reason";
        }
        
        private void UpdatePriorityIndicators()
        {
            var priority = GetRepairPriority();
            
            // Hide all priority indicators first
            if (criticalPriorityIndicator != null)
                criticalPriorityIndicator.SetActive(false);
            if (highPriorityIndicator != null)
                highPriorityIndicator.SetActive(false);
            if (mediumPriorityIndicator != null)
                mediumPriorityIndicator.SetActive(false);
            if (lowPriorityIndicator != null)
                lowPriorityIndicator.SetActive(false);
            
            // Show appropriate priority indicator
            switch (priority)
            {
                case RepairPriority.Critical:
                    if (criticalPriorityIndicator != null)
                        criticalPriorityIndicator.SetActive(true);
                    break;
                case RepairPriority.High:
                    if (highPriorityIndicator != null)
                        highPriorityIndicator.SetActive(true);
                    break;
                case RepairPriority.Medium:
                    if (mediumPriorityIndicator != null)
                        mediumPriorityIndicator.SetActive(true);
                    break;
                case RepairPriority.Low:
                    if (lowPriorityIndicator != null)
                        lowPriorityIndicator.SetActive(true);
                    break;
            }
        }
        
        private void RequestRepair()
        {
            if (CanRepair())
            {
                OnRepairRequested?.Invoke(equippedItem);
            }
        }
        
        private DurabilityInfo GetDurabilityInfo(EquippedItemDTO item)
        {
            // This would normally come from the item's actual durability data
            // For now, create mock durability info
            
            if (item?.Durability != null)
            {
                return new DurabilityInfo
                {
                    Current = item.Durability.Current,
                    Maximum = item.Durability.Maximum,
                    Percentage = item.Durability.Percentage
                };
            }
            
            // Mock data if no durability information is available
            float mockPercentage = UnityEngine.Random.Range(10f, 60f); // Low durability for repair display
            return new DurabilityInfo
            {
                Current = (int)(mockPercentage),
                Maximum = 100,
                Percentage = mockPercentage
            };
        }
        
        private RepairInfo CalculateRepairInfo(EquippedItemDTO item, DurabilityInfo durability)
        {
            if (item?.Item == null || durability == null)
                return new RepairInfo { CanRepair = false, CannotRepairReason = "Invalid item data" };
            
            // Calculate repair cost based on item value and missing durability
            float missingDurability = 100f - durability.Percentage;
            int baseCost = Mathf.RoundToInt(item.Item.Value * 0.1f); // 10% of item value as base
            int repairCost = Mathf.RoundToInt(baseCost * (missingDurability / 100f));
            
            // Minimum repair cost
            repairCost = Mathf.Max(repairCost, 1);
            
            // Check if item can be repaired
            bool canRepair = true;
            string cannotRepairReason = null;
            
            // Check if item is completely broken
            if (durability.Percentage <= 0)
            {
                canRepair = false;
                cannotRepairReason = "Item is completely destroyed";
            }
            
            // Check if item is already at full durability
            if (durability.Percentage >= 100f)
            {
                canRepair = false;
                cannotRepairReason = "Item does not need repair";
            }
            
            // Check item rarity restrictions (some items might not be repairable)
            if (item.Item.Rarity == ItemRarity.Artifact)
            {
                canRepair = false;
                cannotRepairReason = "Artifact items cannot be repaired by normal means";
            }
            
            return new RepairInfo
            {
                CanRepair = canRepair,
                Cost = repairCost,
                CannotRepairReason = cannotRepairReason
            };
        }
        
        private RepairPriority GetRepairPriority()
        {
            if (durabilityInfo == null)
                return RepairPriority.Low;
            
            // Determine priority based on durability percentage and item importance
            float percentage = durabilityInfo.Percentage;
            var itemType = equippedItem.Item.EquipmentType;
            var slot = equippedItem.Slot;
            
            // Critical priority for very low durability on important items
            if (percentage <= 10f && IsImportantSlot(slot))
                return RepairPriority.Critical;
            
            // High priority for low durability
            if (percentage <= 25f)
                return RepairPriority.High;
            
            // Medium priority for moderate durability loss
            if (percentage <= 50f)
                return RepairPriority.Medium;
            
            // Low priority for minor durability loss
            return RepairPriority.Low;
        }
        
        private bool IsImportantSlot(EquipmentSlot slot)
        {
            return slot == EquipmentSlot.MainHand || 
                   slot == EquipmentSlot.Body || 
                   slot == EquipmentSlot.Head;
        }
        
        private Color GetDurabilityColor(float percentage)
        {
            if (percentage <= 0f)
                return brokenColor;
            else if (percentage <= 25f)
                return lowDurabilityColor;
            else if (percentage <= 75f)
                return mediumDurabilityColor;
            else
                return highDurabilityColor;
        }
        
        private string GetDurabilityStatusText(float percentage)
        {
            if (percentage <= 0f)
                return "Broken";
            else if (percentage <= 10f)
                return "Critical";
            else if (percentage <= 25f)
                return "Poor";
            else if (percentage <= 50f)
                return "Damaged";
            else if (percentage <= 75f)
                return "Worn";
            else if (percentage < 100f)
                return "Good";
            else
                return "Perfect";
        }
        
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
        
        #region Data Classes
        
        private class DurabilityInfo
        {
            public int Current { get; set; }
            public int Maximum { get; set; }
            public float Percentage { get; set; }
        }
        
        private class RepairInfo
        {
            public bool CanRepair { get; set; }
            public int Cost { get; set; }
            public string CannotRepairReason { get; set; }
        }
        
        private enum RepairPriority
        {
            Low,
            Medium,
            High,
            Critical
        }
        
        #endregion
        
        #region Public Properties
        
        public EquippedItemDTO EquippedItem => equippedItem;
        public float DurabilityPercentage => durabilityInfo?.Percentage ?? 100f;
        public RepairPriority Priority => GetRepairPriority();
        
        #endregion
    }
} 