using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using TMPro;
using VDM.DTOs.Economic.Equipment;

namespace VDM.UI.Systems.Equipment
{
    /// <summary>
    /// Side-by-side equipment comparison display with stat difference highlighting
    /// </summary>
    public class EquipmentComparisonDisplay : MonoBehaviour
    {
        [Header("Layout")]
        [SerializeField] private Transform leftItemPanel;
        [SerializeField] private Transform rightItemPanel;
        [SerializeField] private GameObject comparisonHeaderPanel;
        [SerializeField] private TextMeshProUGUI comparisonTitleText;
        
        [Header("Item Display Prefabs")]
        [SerializeField] private GameObject itemInfoPrefab;
        [SerializeField] private GameObject statComparisonPrefab;
        [SerializeField] private GameObject propertyComparisonPrefab;
        
        [Header("Comparison Colors")]
        [SerializeField] private Color betterStatColor = Color.green;
        [SerializeField] private Color worseStatColor = Color.red;
        [SerializeField] private Color equalStatColor = Color.white;
        [SerializeField] private Color newPropertyColor = Color.cyan;
        [SerializeField] private Color lostPropertyColor = Color.red;
        
        [Header("Visual Elements")]
        [SerializeField] private GameObject recommendationPanel;
        [SerializeField] private TextMeshProUGUI recommendationText;
        [SerializeField] private Image recommendationIcon;
        [SerializeField] private Sprite upgradeIcon;
        [SerializeField] private Sprite downgradeIcon;
        [SerializeField] private Sprite sideGradeIcon;
        
        // Data
        private EquipmentItemDTO currentItem;
        private EquipmentItemDTO comparisonItem;
        
        // UI Elements
        private List<GameObject> leftElements = new List<GameObject>();
        private List<GameObject> rightElements = new List<GameObject>();
        private List<GameObject> comparisonElements = new List<GameObject>();
        
        public enum ComparisonResult
        {
            Upgrade,
            Downgrade,
            SideGrade,
            Unclear
        }
        
        /// <summary>
        /// Show comparison between current equipped item and potential new item
        /// </summary>
        public void ShowComparison(EquipmentItemDTO current, EquipmentItemDTO comparison)
        {
            currentItem = current;
            comparisonItem = comparison;
            
            ClearComparison();
            PopulateComparison();
            AnalyzeComparison();
        }
        
        /// <summary>
        /// Hide the comparison display
        /// </summary>
        public void HideComparison()
        {
            ClearComparison();
            gameObject.SetActive(false);
        }
        
        private void PopulateComparison()
        {
            if (currentItem == null || comparisonItem == null)
                return;
            
            // Set title
            if (comparisonTitleText != null)
                comparisonTitleText.text = $"Compare: {currentItem.Name} vs {comparisonItem.Name}";
            
            // Create item info displays
            CreateItemInfoDisplay(currentItem, leftItemPanel, leftElements);
            CreateItemInfoDisplay(comparisonItem, rightItemPanel, rightElements);
            
            // Create stat comparisons
            CreateStatComparisons();
            
            // Create property comparisons
            CreatePropertyComparisons();
            
            gameObject.SetActive(true);
        }
        
        private void CreateItemInfoDisplay(EquipmentItemDTO item, Transform parent, List<GameObject> elementList)
        {
            if (itemInfoPrefab == null || parent == null)
                return;
            
            GameObject infoGO = Instantiate(itemInfoPrefab, parent);
            var itemDisplay = infoGO.GetComponent<ItemInfoDisplay>();
            
            if (itemDisplay != null)
            {
                itemDisplay.Initialize(item);
            }
            else
            {
                // Fallback: set up basic item info display
                SetupBasicItemInfo(infoGO, item);
            }
            
            elementList.Add(infoGO);
        }
        
        private void SetupBasicItemInfo(GameObject infoGO, EquipmentItemDTO item)
        {
            // Find and set basic item information
            var nameText = infoGO.GetComponentInChildren<TextMeshProUGUI>();
            if (nameText != null)
            {
                nameText.text = $"{item.Name}\n{item.EquipmentType} - {item.Rarity}\nLevel {item.LevelRequirement}";
            }
            
            var iconImage = infoGO.GetComponentInChildren<Image>();
            if (iconImage != null && !string.IsNullOrEmpty(item.IconId))
            {
                Sprite icon = Resources.Load<Sprite>(item.IconId);
                if (icon != null)
                    iconImage.sprite = icon;
            }
        }
        
        private void CreateStatComparisons()
        {
            if (statComparisonPrefab == null)
                return;
            
            // Get all stats from both items
            var allStats = new HashSet<string>(currentItem.AttributeBonuses.Keys);
            foreach (var stat in comparisonItem.AttributeBonuses.Keys)
            {
                allStats.Add(stat);
            }
            
            // Create comparison for each stat
            foreach (var statName in allStats)
            {
                int currentValue = currentItem.AttributeBonuses.GetValueOrDefault(statName, 0);
                int comparisonValue = comparisonItem.AttributeBonuses.GetValueOrDefault(statName, 0);
                
                CreateStatComparison(statName, currentValue, comparisonValue);
            }
            
            // Compare basic properties
            CreateBasicPropertyComparisons();
        }
        
        private void CreateStatComparison(string statName, int currentValue, int comparisonValue)
        {
            if (statComparisonPrefab == null)
                return;
            
            GameObject comparisonGO = Instantiate(statComparisonPrefab, transform);
            var statComparison = comparisonGO.GetComponent<StatComparisonDisplay>();
            
            if (statComparison != null)
            {
                statComparison.Initialize(statName, currentValue, comparisonValue, GetStatComparisonColor(currentValue, comparisonValue));
            }
            else
            {
                // Fallback: setup basic stat comparison
                SetupBasicStatComparison(comparisonGO, statName, currentValue, comparisonValue);
            }
            
            comparisonElements.Add(comparisonGO);
        }
        
        private void SetupBasicStatComparison(GameObject comparisonGO, string statName, int currentValue, int comparisonValue)
        {
            var textComponents = comparisonGO.GetComponentsInChildren<TextMeshProUGUI>();
            
            if (textComponents.Length >= 3)
            {
                textComponents[0].text = statName;
                textComponents[1].text = currentValue.ToString();
                textComponents[2].text = comparisonValue.ToString();
                
                // Color the comparison value
                int difference = comparisonValue - currentValue;
                Color comparisonColor = GetStatComparisonColor(currentValue, comparisonValue);
                textComponents[2].color = comparisonColor;
                
                // Add difference indicator
                if (difference != 0)
                {
                    string diffText = difference > 0 ? $"(+{difference})" : $"({difference})";
                    textComponents[2].text += $" {diffText}";
                }
            }
        }
        
        private void CreateBasicPropertyComparisons()
        {
            // Compare value
            CreateStatComparison("Value", currentItem.Value, comparisonItem.Value);
            
            // Compare weight
            CreateWeightComparison();
            
            // Compare level requirement
            CreateStatComparison("Required Level", currentItem.LevelRequirement, comparisonItem.LevelRequirement);
            
            // Compare durability (if applicable)
            // This would be implemented based on actual durability system
        }
        
        private void CreateWeightComparison()
        {
            if (statComparisonPrefab == null)
                return;
            
            GameObject comparisonGO = Instantiate(statComparisonPrefab, transform);
            var textComponents = comparisonGO.GetComponentsInChildren<TextMeshProUGUI>();
            
            if (textComponents.Length >= 3)
            {
                textComponents[0].text = "Weight";
                textComponents[1].text = $"{currentItem.Weight:F1} lbs";
                textComponents[2].text = $"{comparisonItem.Weight:F1} lbs";
                
                // Lower weight is better
                Color comparisonColor = GetWeightComparisonColor(currentItem.Weight, comparisonItem.Weight);
                textComponents[2].color = comparisonColor;
                
                float difference = comparisonItem.Weight - currentItem.Weight;
                if (Math.Abs(difference) > 0.1f)
                {
                    string diffText = difference > 0 ? $"(+{difference:F1})" : $"({difference:F1})";
                    textComponents[2].text += $" {diffText}";
                }
            }
            
            comparisonElements.Add(comparisonGO);
        }
        
        private void CreatePropertyComparisons()
        {
            if (propertyComparisonPrefab == null)
                return;
            
            // Compare special properties like enchantments, set bonuses, etc.
            CompareEnchantments();
            CompareClassRestrictions();
            CompareSpecialProperties();
        }
        
        private void CompareEnchantments()
        {
            // Compare enchantment slots
            int currentSlots = currentItem.EnchantmentSlots;
            int comparisonSlots = comparisonItem.EnchantmentSlots;
            
            if (currentSlots > 0 || comparisonSlots > 0)
            {
                CreateStatComparison("Enchantment Slots", currentSlots, comparisonSlots);
            }
            
            int currentUsedSlots = currentItem.UsedEnchantmentSlots;
            int comparisonUsedSlots = comparisonItem.UsedEnchantmentSlots;
            
            if (currentUsedSlots > 0 || comparisonUsedSlots > 0)
            {
                CreateStatComparison("Used Enchantments", currentUsedSlots, comparisonUsedSlots);
            }
        }
        
        private void CompareClassRestrictions()
        {
            // Show class restrictions if they differ
            var currentRestrictions = currentItem.ClassRestrictions ?? new List<string>();
            var comparisonRestrictions = comparisonItem.ClassRestrictions ?? new List<string>();
            
            if (currentRestrictions.Count > 0 || comparisonRestrictions.Count > 0)
            {
                CreatePropertyComparison("Class Restrictions", 
                    string.Join(", ", currentRestrictions),
                    string.Join(", ", comparisonRestrictions));
            }
        }
        
        private void CompareSpecialProperties()
        {
            // Compare any custom properties
            var currentProperties = currentItem.CustomProperties ?? new Dictionary<string, object>();
            var comparisonProperties = comparisonItem.CustomProperties ?? new Dictionary<string, object>();
            
            var allPropertyKeys = new HashSet<string>(currentProperties.Keys);
            foreach (var key in comparisonProperties.Keys)
            {
                allPropertyKeys.Add(key);
            }
            
            foreach (var propertyKey in allPropertyKeys)
            {
                string currentValue = currentProperties.ContainsKey(propertyKey) ? currentProperties[propertyKey]?.ToString() ?? "" : "";
                string comparisonValue = comparisonProperties.ContainsKey(propertyKey) ? comparisonProperties[propertyKey]?.ToString() ?? "" : "";
                
                if (!string.IsNullOrEmpty(currentValue) || !string.IsNullOrEmpty(comparisonValue))
                {
                    CreatePropertyComparison(propertyKey, currentValue, comparisonValue);
                }
            }
        }
        
        private void CreatePropertyComparison(string propertyName, string currentValue, string comparisonValue)
        {
            if (propertyComparisonPrefab == null)
                return;
            
            GameObject comparisonGO = Instantiate(propertyComparisonPrefab, transform);
            var textComponents = comparisonGO.GetComponentsInChildren<TextMeshProUGUI>();
            
            if (textComponents.Length >= 3)
            {
                textComponents[0].text = propertyName;
                textComponents[1].text = string.IsNullOrEmpty(currentValue) ? "None" : currentValue;
                textComponents[2].text = string.IsNullOrEmpty(comparisonValue) ? "None" : comparisonValue;
                
                // Color based on whether property is gained or lost
                if (string.IsNullOrEmpty(currentValue) && !string.IsNullOrEmpty(comparisonValue))
                {
                    textComponents[2].color = newPropertyColor;
                }
                else if (!string.IsNullOrEmpty(currentValue) && string.IsNullOrEmpty(comparisonValue))
                {
                    textComponents[2].color = lostPropertyColor;
                }
                else if (currentValue != comparisonValue)
                {
                    textComponents[2].color = newPropertyColor;
                }
            }
            
            comparisonElements.Add(comparisonGO);
        }
        
        private void AnalyzeComparison()
        {
            if (recommendationPanel == null)
                return;
            
            ComparisonResult result = DetermineComparisonResult();
            
            recommendationPanel.SetActive(true);
            
            switch (result)
            {
                case ComparisonResult.Upgrade:
                    if (recommendationText != null)
                        recommendationText.text = "Recommended: This item is an upgrade!";
                    if (recommendationIcon != null && upgradeIcon != null)
                        recommendationIcon.sprite = upgradeIcon;
                    break;
                
                case ComparisonResult.Downgrade:
                    if (recommendationText != null)
                        recommendationText.text = "Not Recommended: This item is a downgrade.";
                    if (recommendationIcon != null && downgradeIcon != null)
                        recommendationIcon.sprite = downgradeIcon;
                    break;
                
                case ComparisonResult.SideGrade:
                    if (recommendationText != null)
                        recommendationText.text = "Side Grade: Different strengths and weaknesses.";
                    if (recommendationIcon != null && sideGradeIcon != null)
                        recommendationIcon.sprite = sideGradeIcon;
                    break;
                
                case ComparisonResult.Unclear:
                    if (recommendationText != null)
                        recommendationText.text = "Unclear: Consider your build and preferences.";
                    if (recommendationIcon != null && sideGradeIcon != null)
                        recommendationIcon.sprite = sideGradeIcon;
                    break;
            }
        }
        
        private ComparisonResult DetermineComparisonResult()
        {
            int improvements = 0;
            int downgrades = 0;
            int totalComparisons = 0;
            
            // Analyze attribute bonuses
            var allStats = new HashSet<string>(currentItem.AttributeBonuses.Keys);
            foreach (var stat in comparisonItem.AttributeBonuses.Keys)
            {
                allStats.Add(stat);
            }
            
            foreach (var statName in allStats)
            {
                int currentValue = currentItem.AttributeBonuses.GetValueOrDefault(statName, 0);
                int comparisonValue = comparisonItem.AttributeBonuses.GetValueOrDefault(statName, 0);
                
                if (currentValue != comparisonValue)
                {
                    totalComparisons++;
                    if (comparisonValue > currentValue)
                        improvements++;
                    else
                        downgrades++;
                }
            }
            
            // Consider rarity
            if (comparisonItem.Rarity > currentItem.Rarity)
                improvements++;
            else if (comparisonItem.Rarity < currentItem.Rarity)
                downgrades++;
            totalComparisons++;
            
            // Consider value (higher value generally indicates better item)
            if (comparisonItem.Value > currentItem.Value * 1.2f) // 20% threshold
                improvements++;
            else if (comparisonItem.Value < currentItem.Value * 0.8f)
                downgrades++;
            totalComparisons++;
            
            // Determine result
            if (totalComparisons == 0)
                return ComparisonResult.Unclear;
            
            float improvementRatio = (float)improvements / totalComparisons;
            float downgradeRatio = (float)downgrades / totalComparisons;
            
            if (improvementRatio >= 0.7f)
                return ComparisonResult.Upgrade;
            else if (downgradeRatio >= 0.7f)
                return ComparisonResult.Downgrade;
            else if (Math.Abs(improvementRatio - downgradeRatio) <= 0.2f)
                return ComparisonResult.SideGrade;
            else
                return ComparisonResult.Unclear;
        }
        
        private Color GetStatComparisonColor(int currentValue, int comparisonValue)
        {
            if (comparisonValue > currentValue)
                return betterStatColor;
            else if (comparisonValue < currentValue)
                return worseStatColor;
            else
                return equalStatColor;
        }
        
        private Color GetWeightComparisonColor(float currentWeight, float comparisonWeight)
        {
            // Lower weight is better
            if (comparisonWeight < currentWeight)
                return betterStatColor;
            else if (comparisonWeight > currentWeight)
                return worseStatColor;
            else
                return equalStatColor;
        }
        
        private void ClearComparison()
        {
            // Clear all generated elements
            foreach (var element in leftElements)
            {
                if (element != null)
                    DestroyImmediate(element);
            }
            leftElements.Clear();
            
            foreach (var element in rightElements)
            {
                if (element != null)
                    DestroyImmediate(element);
            }
            rightElements.Clear();
            
            foreach (var element in comparisonElements)
            {
                if (element != null)
                    DestroyImmediate(element);
            }
            comparisonElements.Clear();
            
            if (recommendationPanel != null)
                recommendationPanel.SetActive(false);
        }
        
        #region Public Properties
        
        public EquipmentItemDTO CurrentItem => currentItem;
        public EquipmentItemDTO ComparisonItem => comparisonItem;
        public bool IsComparing => currentItem != null && comparisonItem != null;
        
        #endregion
    }
    
    /// <summary>
    /// Helper component for individual stat comparisons
    /// </summary>
    public class StatComparisonDisplay : MonoBehaviour
    {
        [SerializeField] private TextMeshProUGUI statNameText;
        [SerializeField] private TextMeshProUGUI currentValueText;
        [SerializeField] private TextMeshProUGUI comparisonValueText;
        [SerializeField] private Image comparisonArrow;
        [SerializeField] private Sprite upArrow;
        [SerializeField] private Sprite downArrow;
        [SerializeField] private Sprite equalArrow;
        
        public void Initialize(string statName, int currentValue, int comparisonValue, Color comparisonColor)
        {
            if (statNameText != null)
                statNameText.text = statName;
            if (currentValueText != null)
                currentValueText.text = currentValue.ToString();
            if (comparisonValueText != null)
            {
                comparisonValueText.text = comparisonValue.ToString();
                comparisonValueText.color = comparisonColor;
                
                int difference = comparisonValue - currentValue;
                if (difference != 0)
                {
                    string diffText = difference > 0 ? $"(+{difference})" : $"({difference})";
                    comparisonValueText.text += $" {diffText}";
                }
            }
            
            // Set arrow indicator
            if (comparisonArrow != null)
            {
                if (comparisonValue > currentValue && upArrow != null)
                    comparisonArrow.sprite = upArrow;
                else if (comparisonValue < currentValue && downArrow != null)
                    comparisonArrow.sprite = downArrow;
                else if (equalArrow != null)
                    comparisonArrow.sprite = equalArrow;
            }
        }
    }
    
    /// <summary>
    /// Helper component for basic item info display
    /// </summary>
    public class ItemInfoDisplay : MonoBehaviour
    {
        [SerializeField] private Image itemIcon;
        [SerializeField] private TextMeshProUGUI itemNameText;
        [SerializeField] private TextMeshProUGUI itemTypeText;
        [SerializeField] private TextMeshProUGUI itemLevelText;
        [SerializeField] private Image rarityBorder;
        
        public void Initialize(EquipmentItemDTO item)
        {
            if (itemIcon != null && !string.IsNullOrEmpty(item.IconId))
            {
                Sprite icon = Resources.Load<Sprite>(item.IconId);
                if (icon != null)
                    itemIcon.sprite = icon;
            }
            
            if (itemNameText != null)
                itemNameText.text = item.Name;
            if (itemTypeText != null)
                itemTypeText.text = $"{item.EquipmentType}";
            if (itemLevelText != null)
                itemLevelText.text = $"Level {item.LevelRequirement}";
            
            if (rarityBorder != null)
                rarityBorder.color = GetRarityColor(item.Rarity);
        }
        
        private Color GetRarityColor(ItemRarity rarity)
        {
            return rarity switch
            {
                ItemRarity.Common => Color.white,
                ItemRarity.Uncommon => Color.green,
                ItemRarity.Rare => Color.blue,
                ItemRarity.Epic => new Color(0.5f, 0f, 0.5f),
                ItemRarity.Legendary => Color.yellow,
                ItemRarity.Artifact => Color.red,
                _ => Color.white
            };
        }
    }
} 