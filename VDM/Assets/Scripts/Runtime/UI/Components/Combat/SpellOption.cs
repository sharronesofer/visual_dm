using System;
using UnityEngine;
using UnityEngine.UI;
using TMPro;
using VDM.DTOs.Game.Character;

namespace VDM.UI.Systems.Combat
{
    /// <summary>
    /// UI component for displaying and selecting spell options in combat
    /// </summary>
    public class SpellOption : MonoBehaviour
    {
        [Header("Spell Information")]
        [SerializeField] private Image spellIcon;
        [SerializeField] private TextMeshProUGUI spellNameText;
        [SerializeField] private TextMeshProUGUI spellLevelText;
        [SerializeField] private TextMeshProUGUI spellSchoolText;
        [SerializeField] private TextMeshProUGUI descriptionText;
        
        [Header("Spell Stats")]
        [SerializeField] private TextMeshProUGUI manaCostText;
        [SerializeField] private TextMeshProUGUI castingTimeText;
        [SerializeField] private TextMeshProUGUI rangeText;
        [SerializeField] private TextMeshProUGUI durationText;
        
        [Header("Spell Components")]
        [SerializeField] private Transform componentsContainer;
        [SerializeField] private GameObject componentPrefab;
        [SerializeField] private TextMeshProUGUI materialComponentText;
        
        [Header("UI Elements")]
        [SerializeField] private Button selectButton;
        [SerializeField] private Image backgroundImage;
        [SerializeField] private Image selectionHighlight;
        [SerializeField] private Image schoolBorder;
        
        [Header("Visual States")]
        [SerializeField] private Color normalColor = Color.white;
        [SerializeField] private Color hoverColor = new Color(0.8f, 0.8f, 1f, 1f);
        [SerializeField] private Color selectedColor = new Color(0.6f, 0.8f, 1f, 1f);
        [SerializeField] private Color disabledColor = new Color(0.5f, 0.5f, 0.5f, 0.5f);
        [SerializeField] private Color insufficientManaColor = new Color(1f, 0.5f, 0.5f, 1f);
        
        [Header("Animation")]
        [SerializeField] private float hoverScale = 1.02f;
        [SerializeField] private float animationDuration = 0.15f;
        [SerializeField] private LeanTweenType animationEase = LeanTweenType.easeOutQuad;
        
        // Data
        private SpellModel spellData;
        private bool isSelected = false;
        private bool isEnabled = true;
        private bool hasSufficientMana = true;
        private Vector3 originalScale;
        
        // Events
        private System.Action onSpellSelected;
        
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
        /// Initialize the spell option
        /// </summary>
        public void Initialize(SpellModel spell, System.Action selectionCallback, int availableMana = int.MaxValue)
        {
            spellData = spell;
            onSpellSelected = selectionCallback;
            
            hasSufficientMana = availableMana >= spell.ManaCost;
            
            UpdateSpellDisplay();
            UpdateSpellStats();
            UpdateSpellComponents();
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
                selectButton.interactable = enabled && hasSufficientMana;
            
            UpdateVisualState();
        }
        
        /// <summary>
        /// Update available mana to check if spell can be cast
        /// </summary>
        public void UpdateAvailableMana(int availableMana)
        {
            hasSufficientMana = availableMana >= spellData.ManaCost;
            
            if (selectButton != null)
                selectButton.interactable = isEnabled && hasSufficientMana;
            
            UpdateVisualState();
        }
        
        private void UpdateSpellDisplay()
        {
            if (spellData == null) return;
            
            // Set spell name
            if (spellNameText != null)
                spellNameText.text = spellData.Name;
            
            // Set spell level
            if (spellLevelText != null)
            {
                string levelText = spellData.Level == 0 ? "Cantrip" : $"Level {spellData.Level}";
                spellLevelText.text = levelText;
            }
            
            // Set spell school
            if (spellSchoolText != null)
                spellSchoolText.text = spellData.School.ToString();
            
            // Set description
            if (descriptionText != null)
                descriptionText.text = spellData.Description;
            
            // Set spell icon
            if (spellIcon != null)
            {
                Sprite icon = Resources.Load<Sprite>($"SpellIcons/{spellData.School}");
                if (icon != null)
                    spellIcon.sprite = icon;
            }
            
            // Set school border color
            if (schoolBorder != null)
                schoolBorder.color = GetSchoolColor(spellData.School);
        }
        
        private void UpdateSpellStats()
        {
            if (spellData == null) return;
            
            // Set mana cost
            if (manaCostText != null)
            {
                string costText = spellData.Level == 0 ? "No Cost" : $"{spellData.ManaCost} Mana";
                manaCostText.text = costText;
                manaCostText.color = hasSufficientMana ? Color.white : Color.red;
            }
            
            // Set casting time
            if (castingTimeText != null)
            {
                string timeText = spellData.CastingTime == 1f ? "1 Action" : $"{spellData.CastingTime}s";
                castingTimeText.text = $"Cast: {timeText}";
            }
            
            // Set range
            if (rangeText != null)
            {
                string rangeDisplay = spellData.Range == 0 ? "Self" : 
                                     spellData.Range == 1 ? "Touch" : 
                                     $"{spellData.Range} ft";
                rangeText.text = $"Range: {rangeDisplay}";
            }
            
            // Set duration
            if (durationText != null)
            {
                string durationDisplay = FormatDuration(spellData.Duration);
                durationText.text = $"Duration: {durationDisplay}";
            }
        }
        
        private void UpdateSpellComponents()
        {
            if (componentsContainer == null || spellData?.Components == null) return;
            
            // Clear existing components
            foreach (Transform child in componentsContainer)
            {
                Destroy(child.gameObject);
            }
            
            // Add spell components
            foreach (var component in spellData.Components)
            {
                CreateComponentElement(component.ToString());
            }
            
            // Set material component text
            if (materialComponentText != null)
            {
                if (!string.IsNullOrEmpty(spellData.MaterialComponent))
                {
                    materialComponentText.gameObject.SetActive(true);
                    materialComponentText.text = $"Material: {spellData.MaterialComponent}";
                }
                else
                {
                    materialComponentText.gameObject.SetActive(false);
                }
            }
        }
        
        private void CreateComponentElement(string component)
        {
            if (componentPrefab == null) return;
            
            GameObject componentElement = Instantiate(componentPrefab, componentsContainer);
            var componentText = componentElement.GetComponentInChildren<TextMeshProUGUI>();
            
            if (componentText != null)
            {
                // Show component abbreviations (V = Verbal, S = Somatic, M = Material)
                string abbreviation = component.Substring(0, 1).ToUpper();
                componentText.text = abbreviation;
                componentText.color = GetComponentColor(component);
            }
        }
        
        private void UpdateVisualState()
        {
            Color targetColor = normalColor;
            
            if (!isEnabled)
            {
                targetColor = disabledColor;
            }
            else if (!hasSufficientMana)
            {
                targetColor = insufficientManaColor;
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
            if (isEnabled && hasSufficientMana && spellData != null)
            {
                onSpellSelected?.Invoke();
            }
        }
        
        public void OnPointerEnter()
        {
            if (isEnabled && hasSufficientMana)
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
                {
                    Color targetColor = hasSufficientMana ? normalColor : insufficientManaColor;
                    backgroundImage.color = targetColor;
                }
                
                LeanTween.scale(gameObject, originalScale, animationDuration)
                    .setEase(animationEase);
            }
        }
        
        #region Helper Methods
        
        private Color GetSchoolColor(SpellSchool school)
        {
            return school switch
            {
                SpellSchool.Abjuration => new Color(0.5f, 0.8f, 1f),     // Light blue
                SpellSchool.Conjuration => new Color(0.8f, 0.5f, 1f),    // Purple
                SpellSchool.Divination => new Color(1f, 1f, 0.5f),       // Yellow
                SpellSchool.Enchantment => new Color(1f, 0.5f, 0.8f),    // Pink
                SpellSchool.Evocation => new Color(1f, 0.5f, 0.5f),      // Red
                SpellSchool.Illusion => new Color(0.8f, 0.8f, 0.8f),     // Silver
                SpellSchool.Necromancy => new Color(0.3f, 0.3f, 0.3f),   // Dark gray
                SpellSchool.Transmutation => new Color(0.5f, 1f, 0.5f),  // Green
                _ => Color.white
            };
        }
        
        private Color GetComponentColor(string component)
        {
            return component.ToLower() switch
            {
                "verbal" => Color.cyan,
                "somatic" => Color.yellow,
                "material" => Color.magenta,
                "focus" => Color.green,
                _ => Color.white
            };
        }
        
        private string FormatDuration(string duration)
        {
            if (string.IsNullOrEmpty(duration))
                return "Instantaneous";
            
            // Parse and format duration string
            return duration switch
            {
                "Instantaneous" => "Instant",
                "Concentration, up to 1 minute" => "Conc., 1 min",
                "Concentration, up to 10 minutes" => "Conc., 10 min",
                "Concentration, up to 1 hour" => "Conc., 1 hour",
                _ => duration
            };
        }
        
        #endregion
        
        #region Public Properties
        
        public SpellModel SpellData => spellData;
        public bool IsSelected => isSelected;
        public bool IsEnabled => isEnabled;
        public bool HasSufficientMana => hasSufficientMana;
        
        #endregion
    }
} 