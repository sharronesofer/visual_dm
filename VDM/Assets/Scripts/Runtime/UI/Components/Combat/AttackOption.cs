using System;
using UnityEngine;
using UnityEngine.UI;
using TMPro;
using VDM.DTOs.Game.Character;

namespace VDM.UI.Systems.Combat
{
    /// <summary>
    /// UI component for displaying and selecting attack options in combat
    /// </summary>
    public class AttackOption : MonoBehaviour
    {
        [Header("Weapon Information")]
        [SerializeField] private Image weaponIcon;
        [SerializeField] private TextMeshProUGUI weaponNameText;
        [SerializeField] private TextMeshProUGUI weaponTypeText;
        [SerializeField] private TextMeshProUGUI damageText;
        [SerializeField] private TextMeshProUGUI rangeText;
        
        [Header("Attack Stats")]
        [SerializeField] private TextMeshProUGUI attackBonusText;
        [SerializeField] private TextMeshProUGUI criticalRangeText;
        [SerializeField] private Transform weaponPropertiesContainer;
        [SerializeField] private GameObject propertyPrefab;
        
        [Header("UI Elements")]
        [SerializeField] private Button selectButton;
        [SerializeField] private Image backgroundImage;
        [SerializeField] private Image selectionHighlight;
        
        [Header("Visual States")]
        [SerializeField] private Color normalColor = Color.white;
        [SerializeField] private Color hoverColor = new Color(1f, 1f, 0.8f, 1f);
        [SerializeField] private Color selectedColor = new Color(0.8f, 1f, 0.8f, 1f);
        [SerializeField] private Color disabledColor = new Color(0.5f, 0.5f, 0.5f, 0.5f);
        
        [Header("Animation")]
        [SerializeField] private float hoverScale = 1.02f;
        [SerializeField] private float animationDuration = 0.1f;
        [SerializeField] private LeanTweenType animationEase = LeanTweenType.easeOutQuad;
        
        // Data
        private WeaponModel weaponData;
        private bool isSelected = false;
        private bool isEnabled = true;
        private Vector3 originalScale;
        
        // Events
        private System.Action onAttackSelected;
        
        private void Awake()
        {
            originalScale = transform.localScale;
            
            // Setup button interaction
            if (selectButton != null)
            {
                selectButton.onClick.AddListener(OnSelectClicked);
            }
            
            UpdateVisualState();
        }
        
        /// <summary>
        /// Initialize the attack option
        /// </summary>
        public void Initialize(WeaponModel weapon, System.Action selectionCallback)
        {
            weaponData = weapon;
            onAttackSelected = selectionCallback;
            
            UpdateWeaponDisplay();
            UpdateAttackStats();
            UpdateWeaponProperties();
            SetEnabled(true);
        }
        
        /// <summary>
        /// Set selection state
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
        /// Set enabled state
        /// </summary>
        public void SetEnabled(bool enabled)
        {
            isEnabled = enabled;
            
            if (selectButton != null)
                selectButton.interactable = enabled;
            
            UpdateVisualState();
        }
        
        private void UpdateWeaponDisplay()
        {
            if (weaponData == null) return;
            
            // Set weapon name
            if (weaponNameText != null)
                weaponNameText.text = weaponData.Name;
            
            // Set weapon type
            if (weaponTypeText != null)
                weaponTypeText.text = weaponData.Type.ToString();
            
            // Set damage
            if (damageText != null)
                damageText.text = $"Damage: 1d{GetWeaponDamageDie(weaponData.Type)} + {weaponData.Damage}";
            
            // Set range
            if (rangeText != null)
            {
                string rangeDisplay = weaponData.Range > 5 ? $"{weaponData.Range} ft" : "Melee";
                rangeText.text = $"Range: {rangeDisplay}";
            }
            
            // Set weapon icon
            if (weaponIcon != null)
            {
                Sprite icon = Resources.Load<Sprite>($"WeaponIcons/{weaponData.Type}");
                if (icon != null)
                    weaponIcon.sprite = icon;
            }
        }
        
        private void UpdateAttackStats()
        {
            if (weaponData == null) return;
            
            // Set attack bonus (placeholder - would be calculated based on character stats)
            if (attackBonusText != null)
            {
                int attackBonus = CalculateAttackBonus();
                attackBonusText.text = $"Attack: +{attackBonus}";
            }
            
            // Set critical range
            if (criticalRangeText != null)
            {
                string critRange = GetCriticalRange(weaponData.Type);
                criticalRangeText.text = $"Crit: {critRange}";
            }
        }
        
        private void UpdateWeaponProperties()
        {
            if (weaponPropertiesContainer == null || weaponData?.Properties == null) return;
            
            // Clear existing properties
            foreach (Transform child in weaponPropertiesContainer)
            {
                Destroy(child.gameObject);
            }
            
            // Add weapon properties
            foreach (string property in weaponData.Properties)
            {
                CreatePropertyElement(property);
            }
        }
        
        private void CreatePropertyElement(string property)
        {
            if (propertyPrefab == null) return;
            
            GameObject propertyElement = Instantiate(propertyPrefab, weaponPropertiesContainer);
            var propertyText = propertyElement.GetComponentInChildren<TextMeshProUGUI>();
            
            if (propertyText != null)
            {
                propertyText.text = property;
                propertyText.color = GetPropertyColor(property);
            }
        }
        
        private void UpdateVisualState()
        {
            Color targetColor = normalColor;
            
            if (!isEnabled)
            {
                targetColor = disabledColor;
            }
            else if (isSelected)
            {
                targetColor = selectedColor;
            }
            
            // Update background color
            if (backgroundImage != null)
                backgroundImage.color = targetColor;
            
            // Update selection highlight
            if (selectionHighlight != null)
                selectionHighlight.gameObject.SetActive(isSelected);
        }
        
        private void AnimateSelection()
        {
            LeanTween.cancel(gameObject);
            LeanTween.scale(gameObject, originalScale * 1.05f, animationDuration)
                .setEase(LeanTweenType.easeOutBack)
                .setLoopPingPong(1);
        }
        
        private void OnSelectClicked()
        {
            if (isEnabled && weaponData != null)
            {
                onAttackSelected?.Invoke();
            }
        }
        
        public void OnPointerEnter()
        {
            if (isEnabled)
            {
                if (backgroundImage != null && !isSelected)
                    backgroundImage.color = hoverColor;
                
                LeanTween.scale(gameObject, originalScale * hoverScale, animationDuration)
                    .setEase(animationEase);
            }
        }
        
        public void OnPointerExit()
        {
            if (isEnabled)
            {
                if (backgroundImage != null && !isSelected)
                    backgroundImage.color = normalColor;
                
                LeanTween.scale(gameObject, originalScale, animationDuration)
                    .setEase(animationEase);
            }
        }
        
        #region Helper Methods
        
        private int GetWeaponDamageDie(WeaponType weaponType)
        {
            return weaponType switch
            {
                WeaponType.Dagger => 4,
                WeaponType.Sword => 8,
                WeaponType.Axe => 10,
                WeaponType.Mace => 6,
                WeaponType.Bow => 8,
                WeaponType.Crossbow => 10,
                WeaponType.Staff => 6,
                WeaponType.Wand => 4,
                WeaponType.Thrown => 6,
                _ => 6
            };
        }
        
        private int CalculateAttackBonus()
        {
            // Placeholder calculation - would use character stats
            int baseAttackBonus = 3; // Character level + proficiency
            int abilityModifier = 2; // STR or DEX modifier
            int weaponEnhancement = 0; // Magic weapon bonus
            
            return baseAttackBonus + abilityModifier + weaponEnhancement;
        }
        
        private string GetCriticalRange(WeaponType weaponType)
        {
            // Most weapons crit on 20, some have extended ranges
            return weaponType switch
            {
                WeaponType.Sword => "19-20", // Longswords often have improved crit
                WeaponType.Dagger => "19-20", // Rapiers and finesse weapons
                _ => "20"
            };
        }
        
        private Color GetPropertyColor(string property)
        {
            // Color code weapon properties
            return property.ToLower() switch
            {
                "magic" => Color.magenta,
                "silver" => Color.cyan,
                "finesse" => Color.yellow,
                "versatile" => Color.green,
                "reach" => Color.blue,
                "thrown" => Color.orange,
                _ => Color.white
            };
        }
        
        #endregion
        
        #region Public Properties
        
        public WeaponModel WeaponData => weaponData;
        public bool IsSelected => isSelected;
        public bool IsEnabled => isEnabled;
        
        #endregion
    }
} 