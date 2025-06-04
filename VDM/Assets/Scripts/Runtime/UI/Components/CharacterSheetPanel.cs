using UnityEngine;
using UnityEngine.UI;
using TMPro;
using VDM.UI.Core;
using VDM.Systems.Character.Models;
using VDM.Systems.Character.Services;
using VDM.DTOs.Character;
using System.Collections.Generic;
using System.Linq;

namespace VDM.UI.Systems.Character
{
    /// <summary>
    /// UI panel for displaying character information, stats, and progression
    /// </summary>
    public class CharacterSheetPanel : BaseUIPanel
    {
        [Header("Character Info")]
        [SerializeField] private Image characterPortrait;
        [SerializeField] private TextMeshProUGUI characterNameText;
        [SerializeField] private TextMeshProUGUI characterLevelText;
        [SerializeField] private TextMeshProUGUI characterClassText;
        [SerializeField] private TextMeshProUGUI characterRaceText;
        [SerializeField] private Slider experienceSlider;
        [SerializeField] private TextMeshProUGUI experienceText;
        
        [Header("Core Attributes")]
        [SerializeField] private TextMeshProUGUI strengthText;
        [SerializeField] private TextMeshProUGUI dexterityText;
        [SerializeField] private TextMeshProUGUI constitutionText;
        [SerializeField] private TextMeshProUGUI intelligenceText;
        [SerializeField] private TextMeshProUGUI wisdomText;
        [SerializeField] private TextMeshProUGUI charismaText;
        
        [Header("Combat Stats")]
        [SerializeField] private TextMeshProUGUI healthText;
        [SerializeField] private Slider healthSlider;
        [SerializeField] private TextMeshProUGUI manaText;
        [SerializeField] private Slider manaSlider;
        [SerializeField] private TextMeshProUGUI armorClassText;
        [SerializeField] private TextMeshProUGUI attackBonusText;
        [SerializeField] private TextMeshProUGUI damageText;
        
        [Header("Skills")]
        [SerializeField] private Transform skillsParent;
        [SerializeField] private GameObject skillEntryPrefab;
        [SerializeField] private ScrollRect skillsScrollRect;
        
        [Header("Equipment")]
        [SerializeField] private Transform equipmentSlotsParent;
        [SerializeField] private GameObject equipmentSlotPrefab;
        [SerializeField] private Button equipmentButton;
        
        [Header("Abilities")]
        [SerializeField] private Transform abilitiesParent;
        [SerializeField] private GameObject abilityEntryPrefab;
        [SerializeField] private ScrollRect abilitiesScrollRect;
        
        [Header("Navigation")]
        [SerializeField] private Button statsTabButton;
        [SerializeField] private Button skillsTabButton;
        [SerializeField] private Button equipmentTabButton;
        [SerializeField] private Button abilitiesTabButton;
        [SerializeField] private GameObject statsPanel;
        [SerializeField] private GameObject skillsPanel;
        [SerializeField] private GameObject equipmentPanel;
        [SerializeField] private GameObject abilitiesPanel;
        
        private CharacterService characterService;
        private CharacterModel currentCharacter;
        private List<GameObject> skillEntries = new List<GameObject>();
        private List<GameObject> equipmentSlots = new List<GameObject>();
        private List<GameObject> abilityEntries = new List<GameObject>();
        private CharacterSheetTab currentTab = CharacterSheetTab.Stats;
        
        private enum CharacterSheetTab
        {
            Stats,
            Skills,
            Equipment,
            Abilities
        }
        
        protected override void Awake()
        {
            base.Awake();
            characterService = FindObjectOfType<CharacterService>();
            
            // Setup tab buttons
            if (statsTabButton != null)
                statsTabButton.onClick.AddListener(() => ShowTab(CharacterSheetTab.Stats));
            if (skillsTabButton != null)
                skillsTabButton.onClick.AddListener(() => ShowTab(CharacterSheetTab.Skills));
            if (equipmentTabButton != null)
                equipmentTabButton.onClick.AddListener(() => ShowTab(CharacterSheetTab.Equipment));
            if (abilitiesTabButton != null)
                abilitiesTabButton.onClick.AddListener(() => ShowTab(CharacterSheetTab.Abilities));
            if (equipmentButton != null)
                equipmentButton.onClick.AddListener(OpenEquipmentManager);
        }
        
        private void OnEnable()
        {
            if (characterService != null)
            {
                characterService.OnCharacterChanged += OnCharacterChanged;
                characterService.OnCharacterStatsUpdated += OnCharacterStatsUpdated;
                characterService.OnCharacterLevelUp += OnCharacterLevelUp;
            }
        }
        
        private void OnDisable()
        {
            if (characterService != null)
            {
                characterService.OnCharacterChanged -= OnCharacterChanged;
                characterService.OnCharacterStatsUpdated -= OnCharacterStatsUpdated;
                characterService.OnCharacterLevelUp -= OnCharacterLevelUp;
            }
        }
        
        /// <summary>
        /// Display character information
        /// </summary>
        public void ShowCharacter(CharacterModel character)
        {
            currentCharacter = character;
            UpdateCharacterInfo();
            UpdateCoreAttributes();
            UpdateCombatStats();
            UpdateSkills();
            UpdateEquipment();
            UpdateAbilities();
            ShowTab(CharacterSheetTab.Stats);
        }
        
        /// <summary>
        /// Update basic character information
        /// </summary>
        private void UpdateCharacterInfo()
        {
            if (currentCharacter == null) return;
            
            if (characterNameText != null)
                characterNameText.text = currentCharacter.Name;
            if (characterLevelText != null)
                characterLevelText.text = $"Level {currentCharacter.Level}";
            if (characterClassText != null)
                characterClassText.text = currentCharacter.CharacterClass;
            if (characterRaceText != null)
                characterRaceText.text = currentCharacter.Race;
            
            // Update experience
            if (experienceSlider != null)
            {
                float expProgress = (float)(currentCharacter.Experience - currentCharacter.ExperienceForCurrentLevel) /
                                  (currentCharacter.ExperienceForNextLevel - currentCharacter.ExperienceForCurrentLevel);
                experienceSlider.value = expProgress;
            }
            
            if (experienceText != null)
                experienceText.text = $"{currentCharacter.Experience} / {currentCharacter.ExperienceForNextLevel} XP";
            
            // Update portrait
            if (characterPortrait != null && !string.IsNullOrEmpty(currentCharacter.PortraitPath))
            {
                Sprite portrait = Resources.Load<Sprite>(currentCharacter.PortraitPath);
                if (portrait != null)
                    characterPortrait.sprite = portrait;
            }
        }
        
        /// <summary>
        /// Update core ability scores
        /// </summary>
        private void UpdateCoreAttributes()
        {
            if (currentCharacter?.Attributes == null) return;
            
            if (strengthText != null)
                strengthText.text = $"{currentCharacter.Attributes.Strength} ({GetModifierText(currentCharacter.Attributes.Strength)})";
            if (dexterityText != null)
                dexterityText.text = $"{currentCharacter.Attributes.Dexterity} ({GetModifierText(currentCharacter.Attributes.Dexterity)})";
            if (constitutionText != null)
                constitutionText.text = $"{currentCharacter.Attributes.Constitution} ({GetModifierText(currentCharacter.Attributes.Constitution)})";
            if (intelligenceText != null)
                intelligenceText.text = $"{currentCharacter.Attributes.Intelligence} ({GetModifierText(currentCharacter.Attributes.Intelligence)})";
            if (wisdomText != null)
                wisdomText.text = $"{currentCharacter.Attributes.Wisdom} ({GetModifierText(currentCharacter.Attributes.Wisdom)})";
            if (charismaText != null)
                charismaText.text = $"{currentCharacter.Attributes.Charisma} ({GetModifierText(currentCharacter.Attributes.Charisma)})";
        }
        
        /// <summary>
        /// Update combat-related statistics
        /// </summary>
        private void UpdateCombatStats()
        {
            if (currentCharacter?.CombatStats == null) return;
            
            // Health
            if (healthText != null)
                healthText.text = $"{currentCharacter.CombatStats.CurrentHealth} / {currentCharacter.CombatStats.MaxHealth}";
            if (healthSlider != null)
                healthSlider.value = (float)currentCharacter.CombatStats.CurrentHealth / currentCharacter.CombatStats.MaxHealth;
            
            // Mana
            if (manaText != null)
                manaText.text = $"{currentCharacter.CombatStats.CurrentMana} / {currentCharacter.CombatStats.MaxMana}";
            if (manaSlider != null)
                manaSlider.value = (float)currentCharacter.CombatStats.CurrentMana / currentCharacter.CombatStats.MaxMana;
            
            // Combat stats
            if (armorClassText != null)
                armorClassText.text = currentCharacter.CombatStats.ArmorClass.ToString();
            if (attackBonusText != null)
                attackBonusText.text = $"+{currentCharacter.CombatStats.AttackBonus}";
            if (damageText != null)
                damageText.text = currentCharacter.CombatStats.DamageBonus.ToString();
        }
        
        /// <summary>
        /// Update skills display
        /// </summary>
        private void UpdateSkills()
        {
            ClearSkillEntries();
            
            if (currentCharacter?.Skills == null || skillsParent == null || skillEntryPrefab == null)
                return;
            
            foreach (var skill in currentCharacter.Skills.OrderBy(s => s.Name))
            {
                GameObject skillEntry = Instantiate(skillEntryPrefab, skillsParent);
                SkillEntry skillComponent = skillEntry.GetComponent<SkillEntry>();
                
                if (skillComponent != null)
                {
                    skillComponent.Initialize(skill);
                }
                
                skillEntries.Add(skillEntry);
            }
        }
        
        /// <summary>
        /// Update equipment display
        /// </summary>
        private void UpdateEquipment()
        {
            ClearEquipmentSlots();
            
            if (currentCharacter?.Equipment == null || equipmentSlotsParent == null || equipmentSlotPrefab == null)
                return;
            
            foreach (var equipSlot in currentCharacter.Equipment.EquipmentSlots)
            {
                GameObject slotObject = Instantiate(equipmentSlotPrefab, equipmentSlotsParent);
                EquipmentSlot slotComponent = slotObject.GetComponent<EquipmentSlot>();
                
                if (slotComponent != null)
                {
                    slotComponent.Initialize(equipSlot);
                }
                
                equipmentSlots.Add(slotObject);
            }
        }
        
        /// <summary>
        /// Update abilities display
        /// </summary>
        private void UpdateAbilities()
        {
            ClearAbilityEntries();
            
            if (currentCharacter?.Abilities == null || abilitiesParent == null || abilityEntryPrefab == null)
                return;
            
            foreach (var ability in currentCharacter.Abilities.OrderBy(a => a.Name))
            {
                GameObject abilityEntry = Instantiate(abilityEntryPrefab, abilitiesParent);
                AbilityEntry abilityComponent = abilityEntry.GetComponent<AbilityEntry>();
                
                if (abilityComponent != null)
                {
                    abilityComponent.Initialize(ability);
                }
                
                abilityEntries.Add(abilityEntry);
            }
        }
        
        /// <summary>
        /// Show specific tab
        /// </summary>
        private void ShowTab(CharacterSheetTab tab)
        {
            currentTab = tab;
            
            // Hide all panels
            if (statsPanel != null) statsPanel.SetActive(false);
            if (skillsPanel != null) skillsPanel.SetActive(false);
            if (equipmentPanel != null) equipmentPanel.SetActive(false);
            if (abilitiesPanel != null) abilitiesPanel.SetActive(false);
            
            // Show selected panel
            switch (tab)
            {
                case CharacterSheetTab.Stats:
                    if (statsPanel != null) statsPanel.SetActive(true);
                    break;
                case CharacterSheetTab.Skills:
                    if (skillsPanel != null) skillsPanel.SetActive(true);
                    break;
                case CharacterSheetTab.Equipment:
                    if (equipmentPanel != null) equipmentPanel.SetActive(true);
                    break;
                case CharacterSheetTab.Abilities:
                    if (abilitiesPanel != null) abilitiesPanel.SetActive(true);
                    break;
            }
            
            // Update button states
            UpdateTabButtonStates();
        }
        
        /// <summary>
        /// Update tab button visual states
        /// </summary>
        private void UpdateTabButtonStates()
        {
            SetTabButtonState(statsTabButton, currentTab == CharacterSheetTab.Stats);
            SetTabButtonState(skillsTabButton, currentTab == CharacterSheetTab.Skills);
            SetTabButtonState(equipmentTabButton, currentTab == CharacterSheetTab.Equipment);
            SetTabButtonState(abilitiesTabButton, currentTab == CharacterSheetTab.Abilities);
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
        /// Get ability modifier text with sign
        /// </summary>
        private string GetModifierText(int abilityScore)
        {
            int modifier = (abilityScore - 10) / 2;
            return modifier >= 0 ? $"+{modifier}" : modifier.ToString();
        }
        
        /// <summary>
        /// Clear skill entries
        /// </summary>
        private void ClearSkillEntries()
        {
            foreach (var entry in skillEntries)
            {
                if (entry != null)
                    DestroyImmediate(entry);
            }
            skillEntries.Clear();
        }
        
        /// <summary>
        /// Clear equipment slots
        /// </summary>
        private void ClearEquipmentSlots()
        {
            foreach (var slot in equipmentSlots)
            {
                if (slot != null)
                    DestroyImmediate(slot);
            }
            equipmentSlots.Clear();
        }
        
        /// <summary>
        /// Clear ability entries
        /// </summary>
        private void ClearAbilityEntries()
        {
            foreach (var entry in abilityEntries)
            {
                if (entry != null)
                    DestroyImmediate(entry);
            }
            abilityEntries.Clear();
        }
        
        #region Event Handlers
        
        private void OnCharacterChanged(CharacterModel character)
        {
            ShowCharacter(character);
        }
        
        private void OnCharacterStatsUpdated(CharacterModel character)
        {
            if (character.Id == currentCharacter?.Id)
            {
                UpdateCoreAttributes();
                UpdateCombatStats();
            }
        }
        
        private void OnCharacterLevelUp(CharacterModel character)
        {
            if (character.Id == currentCharacter?.Id)
            {
                UpdateCharacterInfo();
                UpdateCoreAttributes();
                UpdateCombatStats();
                UpdateAbilities();
                
                // Show level up notification
                NotificationSystem.Instance?.ShowNotification(
                    $"{character.Name} reached level {character.Level}!",
                    NotificationType.Success
                );
            }
        }
        
        private void OpenEquipmentManager()
        {
            UIManager.Instance?.ShowPanel("EquipmentManagerPanel");
        }
        
        #endregion
    }
} 