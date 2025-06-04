using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using TMPro;
using VDM.DTOs.Character;

namespace VDM.UI.Systems.Character
{
    /// <summary>
    /// UI panel for attribute allocation during character creation
    /// </summary>
    public class AttributeAllocationPanel : MonoBehaviour
    {
        [Header("Allocation Method")]
        [SerializeField] private TMP_Dropdown allocationMethodDropdown;
        [SerializeField] private GameObject pointBuyPanel;
        [SerializeField] private GameObject standardArrayPanel;
        
        [Header("Point Buy System")]
        [SerializeField] private TextMeshProUGUI remainingPointsText;
        [SerializeField] private TextMeshProUGUI totalPointsText;
        [SerializeField] private Transform pointBuyAttributesParent;
        [SerializeField] private GameObject pointBuyAttributePrefab;
        
        [Header("Standard Array System")]
        [SerializeField] private Transform standardArrayAttributesParent;
        [SerializeField] private GameObject standardArrayAttributePrefab;
        [SerializeField] private TextMeshProUGUI standardArrayDescriptionText;
        
        [Header("Attribute Display")]
        [SerializeField] private Transform attributeSummaryParent;
        [SerializeField] private GameObject attributeSummaryPrefab;
        
        [Header("Validation")]
        [SerializeField] private GameObject validationPanel;
        [SerializeField] private TextMeshProUGUI validationText;
        
        // Data
        private PointBuyConfigDTO pointBuyConfig;
        private StandardArrayConfigDTO standardArrayConfig;
        private AttributesDTO currentAttributes;
        private List<int> standardArrayValues;
        private Dictionary<string, int> assignedValues = new Dictionary<string, int>();
        
        // UI Elements
        private List<GameObject> pointBuyElements = new List<GameObject>();
        private List<GameObject> standardArrayElements = new List<GameObject>();
        private List<GameObject> summaryElements = new List<GameObject>();
        
        // State
        private AllocationMethod currentMethod = AllocationMethod.PointBuy;
        private int remainingPoints = 0;
        
        // Events
        public event Action<AttributesDTO> OnAttributesAllocated;
        public event Action<bool> OnValidationChanged;
        
        public enum AllocationMethod
        {
            PointBuy = 0,
            StandardArray = 1
        }
        
        private void Awake()
        {
            // Initialize attributes
            currentAttributes = new AttributesDTO
            {
                Strength = 8,
                Dexterity = 8,
                Constitution = 8,
                Intelligence = 8,
                Wisdom = 8,
                Charisma = 8
            };
            
            // Setup dropdown
            if (allocationMethodDropdown != null)
            {
                allocationMethodDropdown.onValueChanged.AddListener(OnAllocationMethodChanged);
            }
            
            // Hide validation initially
            if (validationPanel != null)
                validationPanel.SetActive(false);
        }
        
        /// <summary>
        /// Initialize the panel with point buy and standard array configs
        /// </summary>
        public void Initialize(PointBuyConfigDTO pointBuy, StandardArrayConfigDTO standardArray)
        {
            pointBuyConfig = pointBuy;
            standardArrayConfig = standardArray;
            
            if (pointBuyConfig != null)
            {
                remainingPoints = pointBuyConfig.TotalPoints;
                standardArrayValues = new List<int>(standardArrayConfig.Values);
            }
            
            SetupAllocationMethod(currentMethod);
            UpdateValidation();
        }
        
        /// <summary>
        /// Update display based on current request
        /// </summary>
        public void UpdateDisplay(CharacterCreationRequestDTO request)
        {
            if (request?.Attributes != null)
            {
                currentAttributes = new AttributesDTO
                {
                    Strength = request.Attributes.Strength,
                    Dexterity = request.Attributes.Dexterity,
                    Constitution = request.Attributes.Constitution,
                    Intelligence = request.Attributes.Intelligence,
                    Wisdom = request.Attributes.Wisdom,
                    Charisma = request.Attributes.Charisma
                };
                
                RefreshUI();
            }
        }
        
        private void OnAllocationMethodChanged(int methodIndex)
        {
            currentMethod = (AllocationMethod)methodIndex;
            SetupAllocationMethod(currentMethod);
        }
        
        private void SetupAllocationMethod(AllocationMethod method)
        {
            // Show/hide panels
            if (pointBuyPanel != null)
                pointBuyPanel.SetActive(method == AllocationMethod.PointBuy);
            if (standardArrayPanel != null)
                standardArrayPanel.SetActive(method == AllocationMethod.StandardArray);
            
            // Reset attributes to base values
            ResetAttributes();
            
            switch (method)
            {
                case AllocationMethod.PointBuy:
                    SetupPointBuySystem();
                    break;
                case AllocationMethod.StandardArray:
                    SetupStandardArraySystem();
                    break;
            }
            
            UpdateAttributeSummary();
            UpdateValidation();
        }
        
        private void ResetAttributes()
        {
            currentAttributes = new AttributesDTO
            {
                Strength = 8,
                Dexterity = 8,
                Constitution = 8,
                Intelligence = 8,
                Wisdom = 8,
                Charisma = 8
            };
            
            assignedValues.Clear();
            if (pointBuyConfig != null)
                remainingPoints = pointBuyConfig.TotalPoints;
        }
        
        #region Point Buy System
        
        private void SetupPointBuySystem()
        {
            ClearPointBuyElements();
            
            if (pointBuyConfig == null || pointBuyAttributesParent == null || pointBuyAttributePrefab == null)
                return;
            
            var attributeNames = new List<string> { "Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma" };
            
            foreach (var attributeName in attributeNames)
            {
                GameObject element = Instantiate(pointBuyAttributePrefab, pointBuyAttributesParent);
                PointBuyAttributeElement component = element.GetComponent<PointBuyAttributeElement>();
                
                if (component != null)
                {
                    int currentValue = GetAttributeValue(attributeName);
                    component.Initialize(attributeName, currentValue, pointBuyConfig, OnPointBuyAttributeChanged);
                }
                
                pointBuyElements.Add(element);
            }
            
            UpdatePointBuyDisplay();
        }
        
        private void OnPointBuyAttributeChanged(string attributeName, int newValue)
        {
            int oldValue = GetAttributeValue(attributeName);
            int pointCost = CalculatePointCost(oldValue, newValue);
            
            if (remainingPoints >= pointCost)
            {
                SetAttributeValue(attributeName, newValue);
                remainingPoints -= pointCost;
                
                UpdatePointBuyDisplay();
                UpdateAttributeSummary();
                UpdateValidation();
                
                OnAttributesAllocated?.Invoke(currentAttributes);
            }
        }
        
        private int CalculatePointCost(int oldValue, int newValue)
        {
            if (pointBuyConfig == null)
                return 0;
            
            int oldCost = 0;
            int newCost = 0;
            
            // Calculate cost for old value
            for (int i = pointBuyConfig.MinValue; i < oldValue; i++)
            {
                oldCost += GetPointCostForValue(i + 1);
            }
            
            // Calculate cost for new value
            for (int i = pointBuyConfig.MinValue; i < newValue; i++)
            {
                newCost += GetPointCostForValue(i + 1);
            }
            
            return newCost - oldCost;
        }
        
        private int GetPointCostForValue(int value)
        {
            if (pointBuyConfig == null)
                return 1;
            
            // Standard D&D 5e point buy costs
            if (value <= 13)
                return 1;
            else if (value == 14)
                return 2;
            else if (value == 15)
                return 2;
            else
                return 3; // For values 16+
        }
        
        private void UpdatePointBuyDisplay()
        {
            if (remainingPointsText != null)
                remainingPointsText.text = remainingPoints.ToString();
            if (totalPointsText != null && pointBuyConfig != null)
                totalPointsText.text = pointBuyConfig.TotalPoints.ToString();
            
            // Update individual attribute elements
            foreach (var element in pointBuyElements)
            {
                var component = element.GetComponent<PointBuyAttributeElement>();
                if (component != null)
                {
                    component.UpdateAvailablePoints(remainingPoints);
                }
            }
        }
        
        #endregion
        
        #region Standard Array System
        
        private void SetupStandardArraySystem()
        {
            ClearStandardArrayElements();
            
            if (standardArrayConfig == null || standardArrayAttributesParent == null || standardArrayAttributePrefab == null)
                return;
            
            if (standardArrayDescriptionText != null)
            {
                standardArrayDescriptionText.text = "Assign the following values to your attributes: " +
                    string.Join(", ", standardArrayConfig.Values);
            }
            
            var attributeNames = new List<string> { "Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma" };
            
            foreach (var attributeName in attributeNames)
            {
                GameObject element = Instantiate(standardArrayAttributePrefab, standardArrayAttributesParent);
                StandardArrayAttributeElement component = element.GetComponent<StandardArrayAttributeElement>();
                
                if (component != null)
                {
                    component.Initialize(attributeName, standardArrayValues, OnStandardArrayAttributeChanged);
                }
                
                standardArrayElements.Add(element);
            }
            
            UpdateStandardArrayDisplay();
        }
        
        private void OnStandardArrayAttributeChanged(string attributeName, int newValue)
        {
            // Remove old value from assigned values
            if (assignedValues.ContainsKey(attributeName))
            {
                int oldValue = assignedValues[attributeName];
                standardArrayValues.Add(oldValue);
                assignedValues.Remove(attributeName);
            }
            
            // Assign new value
            if (newValue > 0 && standardArrayValues.Contains(newValue))
            {
                standardArrayValues.Remove(newValue);
                assignedValues[attributeName] = newValue;
                SetAttributeValue(attributeName, newValue);
            }
            else
            {
                SetAttributeValue(attributeName, 8); // Default value
            }
            
            UpdateStandardArrayDisplay();
            UpdateAttributeSummary();
            UpdateValidation();
            
            OnAttributesAllocated?.Invoke(currentAttributes);
        }
        
        private void UpdateStandardArrayDisplay()
        {
            // Update individual attribute elements
            foreach (var element in standardArrayElements)
            {
                var component = element.GetComponent<StandardArrayAttributeElement>();
                if (component != null)
                {
                    component.UpdateAvailableValues(standardArrayValues);
                }
            }
        }
        
        #endregion
        
        #region Attribute Management
        
        private int GetAttributeValue(string attributeName)
        {
            switch (attributeName.ToLower())
            {
                case "strength": return currentAttributes.Strength;
                case "dexterity": return currentAttributes.Dexterity;
                case "constitution": return currentAttributes.Constitution;
                case "intelligence": return currentAttributes.Intelligence;
                case "wisdom": return currentAttributes.Wisdom;
                case "charisma": return currentAttributes.Charisma;
                default: return 8;
            }
        }
        
        private void SetAttributeValue(string attributeName, int value)
        {
            switch (attributeName.ToLower())
            {
                case "strength": currentAttributes.Strength = value; break;
                case "dexterity": currentAttributes.Dexterity = value; break;
                case "constitution": currentAttributes.Constitution = value; break;
                case "intelligence": currentAttributes.Intelligence = value; break;
                case "wisdom": currentAttributes.Wisdom = value; break;
                case "charisma": currentAttributes.Charisma = value; break;
            }
        }
        
        #endregion
        
        #region UI Updates
        
        private void UpdateAttributeSummary()
        {
            ClearSummaryElements();
            
            if (attributeSummaryParent == null || attributeSummaryPrefab == null)
                return;
            
            var attributes = new Dictionary<string, int>
            {
                { "Strength", currentAttributes.Strength },
                { "Dexterity", currentAttributes.Dexterity },
                { "Constitution", currentAttributes.Constitution },
                { "Intelligence", currentAttributes.Intelligence },
                { "Wisdom", currentAttributes.Wisdom },
                { "Charisma", currentAttributes.Charisma }
            };
            
            foreach (var attribute in attributes)
            {
                GameObject element = Instantiate(attributeSummaryPrefab, attributeSummaryParent);
                var textComponent = element.GetComponentInChildren<TextMeshProUGUI>();
                if (textComponent != null)
                {
                    int modifier = (attribute.Value - 10) / 2;
                    string modifierText = modifier >= 0 ? $"+{modifier}" : modifier.ToString();
                    textComponent.text = $"{attribute.Key}: {attribute.Value} ({modifierText})";
                }
                summaryElements.Add(element);
            }
        }
        
        private void UpdateValidation()
        {
            bool isValid = false;
            string validationMessage = "";
            
            switch (currentMethod)
            {
                case AllocationMethod.PointBuy:
                    isValid = ValidatePointBuy(out validationMessage);
                    break;
                case AllocationMethod.StandardArray:
                    isValid = ValidateStandardArray(out validationMessage);
                    break;
            }
            
            if (validationPanel != null)
                validationPanel.SetActive(!isValid);
            if (validationText != null)
                validationText.text = validationMessage;
            
            OnValidationChanged?.Invoke(isValid);
        }
        
        private bool ValidatePointBuy(out string message)
        {
            if (remainingPoints < 0)
            {
                message = "You have exceeded your point limit!";
                return false;
            }
            
            if (remainingPoints > 0)
            {
                message = $"You have {remainingPoints} points remaining to allocate.";
                return false;
            }
            
            message = "";
            return true;
        }
        
        private bool ValidateStandardArray(out string message)
        {
            if (assignedValues.Count < 6)
            {
                message = $"You must assign values to all attributes. {6 - assignedValues.Count} remaining.";
                return false;
            }
            
            message = "";
            return true;
        }
        
        private void RefreshUI()
        {
            SetupAllocationMethod(currentMethod);
        }
        
        #endregion
        
        #region Cleanup Methods
        
        private void ClearPointBuyElements()
        {
            foreach (var element in pointBuyElements)
            {
                if (element != null)
                    DestroyImmediate(element);
            }
            pointBuyElements.Clear();
        }
        
        private void ClearStandardArrayElements()
        {
            foreach (var element in standardArrayElements)
            {
                if (element != null)
                    DestroyImmediate(element);
            }
            standardArrayElements.Clear();
        }
        
        private void ClearSummaryElements()
        {
            foreach (var element in summaryElements)
            {
                if (element != null)
                    DestroyImmediate(element);
            }
            summaryElements.Clear();
        }
        
        #endregion
    }
    
    /// <summary>
    /// Point buy attribute element component
    /// </summary>
    public class PointBuyAttributeElement : MonoBehaviour
    {
        [Header("UI Elements")]
        [SerializeField] private TextMeshProUGUI attributeNameText;
        [SerializeField] private TextMeshProUGUI currentValueText;
        [SerializeField] private Button decreaseButton;
        [SerializeField] private Button increaseButton;
        [SerializeField] private TextMeshProUGUI pointCostText;
        
        private string attributeName;
        private int currentValue;
        private PointBuyConfigDTO config;
        private System.Action<string, int> onValueChanged;
        
        private void Awake()
        {
            if (decreaseButton != null)
                decreaseButton.onClick.AddListener(() => ChangeValue(-1));
            if (increaseButton != null)
                increaseButton.onClick.AddListener(() => ChangeValue(1));
        }
        
        public void Initialize(string name, int value, PointBuyConfigDTO pointBuyConfig, System.Action<string, int> valueChangedCallback)
        {
            attributeName = name;
            currentValue = value;
            config = pointBuyConfig;
            onValueChanged = valueChangedCallback;
            
            UpdateDisplay();
        }
        
        public void UpdateAvailablePoints(int remainingPoints)
        {
            // Update button interactability based on available points
            if (decreaseButton != null)
                decreaseButton.interactable = currentValue > config.MinValue;
            
            if (increaseButton != null)
            {
                int nextValue = currentValue + 1;
                int cost = GetCostForNextValue();
                increaseButton.interactable = nextValue <= config.MaxValue && remainingPoints >= cost;
            }
        }
        
        private void ChangeValue(int delta)
        {
            int newValue = currentValue + delta;
            if (newValue >= config.MinValue && newValue <= config.MaxValue)
            {
                onValueChanged?.Invoke(attributeName, newValue);
                currentValue = newValue;
                UpdateDisplay();
            }
        }
        
        private void UpdateDisplay()
        {
            if (attributeNameText != null)
                attributeNameText.text = attributeName;
            if (currentValueText != null)
                currentValueText.text = currentValue.ToString();
            if (pointCostText != null)
                pointCostText.text = $"Cost: {GetCostForNextValue()}";
        }
        
        private int GetCostForNextValue()
        {
            int nextValue = currentValue + 1;
            if (nextValue <= 13)
                return 1;
            else if (nextValue == 14 || nextValue == 15)
                return 2;
            else
                return 3;
        }
    }
    
    /// <summary>
    /// Standard array attribute element component
    /// </summary>
    public class StandardArrayAttributeElement : MonoBehaviour
    {
        [Header("UI Elements")]
        [SerializeField] private TextMeshProUGUI attributeNameText;
        [SerializeField] private TMP_Dropdown valueDropdown;
        
        private string attributeName;
        private List<int> availableValues;
        private System.Action<string, int> onValueChanged;
        
        private void Awake()
        {
            if (valueDropdown != null)
                valueDropdown.onValueChanged.AddListener(OnDropdownValueChanged);
        }
        
        public void Initialize(string name, List<int> values, System.Action<string, int> valueChangedCallback)
        {
            attributeName = name;
            availableValues = new List<int>(values);
            onValueChanged = valueChangedCallback;
            
            if (attributeNameText != null)
                attributeNameText.text = attributeName;
            
            UpdateDropdown();
        }
        
        public void UpdateAvailableValues(List<int> values)
        {
            availableValues = new List<int>(values);
            UpdateDropdown();
        }
        
        private void UpdateDropdown()
        {
            if (valueDropdown == null)
                return;
            
            valueDropdown.ClearOptions();
            
            List<string> options = new List<string> { "Select..." };
            foreach (int value in availableValues)
            {
                options.Add(value.ToString());
            }
            
            valueDropdown.AddOptions(options);
        }
        
        private void OnDropdownValueChanged(int index)
        {
            if (index > 0 && index <= availableValues.Count)
            {
                int selectedValue = availableValues[index - 1];
                onValueChanged?.Invoke(attributeName, selectedValue);
            }
            else
            {
                onValueChanged?.Invoke(attributeName, 0); // Deselect
            }
        }
    }
} 