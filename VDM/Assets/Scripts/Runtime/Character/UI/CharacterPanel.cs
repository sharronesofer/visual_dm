using System.Collections.Generic;
using System;
using TMPro;
using UnityEngine.UI;
using UnityEngine;
using VDM.Runtime.Character.Models;
using VDM.Runtime.Character.Services;
using VDM.Runtime.UI.Core;


namespace VDM.Runtime.Character.UI
{
    /// <summary>
    /// Main character display and interaction panel
    /// Provides comprehensive character information display and basic interaction controls
    /// </summary>
    public class CharacterPanel : UIPanel
    {
        [Header("Character Info Display")]
        [SerializeField] private TextMeshProUGUI characterNameText;
        [SerializeField] private TextMeshProUGUI levelText;
        [SerializeField] private TextMeshProUGUI classText;
        [SerializeField] private TextMeshProUGUI raceText;
        [SerializeField] private TextMeshProUGUI backgroundText;
        [SerializeField] private Image characterPortrait;
        
        [Header("Character Stats")]
        [SerializeField] private TextMeshProUGUI hpText;
        [SerializeField] private Slider hpSlider;
        [SerializeField] private TextMeshProUGUI mpText;
        [SerializeField] private Slider mpSlider;
        [SerializeField] private TextMeshProUGUI experienceText;
        [SerializeField] private Slider experienceSlider;
        
        [Header("Attributes")]
        [SerializeField] private TextMeshProUGUI strengthText;
        [SerializeField] private TextMeshProUGUI dexterityText;
        [SerializeField] private TextMeshProUGUI constitutionText;
        [SerializeField] private TextMeshProUGUI intelligenceText;
        [SerializeField] private TextMeshProUGUI wisdomText;
        [SerializeField] private TextMeshProUGUI charismaText;
        
        [Header("Skills Section")]
        [SerializeField] private Transform skillsContainer;
        [SerializeField] private GameObject skillItemPrefab;
        
        [Header("Abilities Section")]
        [SerializeField] private Transform abilitiesContainer;
        [SerializeField] private GameObject abilityItemPrefab;
        
        [Header("Action Buttons")]
        [SerializeField] private Button editButton;
        [SerializeField] private Button progressionButton;
        [SerializeField] private Button inventoryButton;
        [SerializeField] private Button relationshipsButton;
        
        [Header("Character Details")]
        [SerializeField] private TextMeshProUGUI descriptionText;
        [SerializeField] private TextMeshProUGUI personalityText;
        [SerializeField] private TextMeshProUGUI goalsText;
        [SerializeField] private TextMeshProUGUI notesText;

        // Services and data
        private CharacterService _characterService;
        private CharacterResponseDTO _currentCharacter;
        private List<GameObject> _skillItems = new List<GameObject>();
        private List<GameObject> _abilityItems = new List<GameObject>();

        // Events
        public event Action<CharacterResponseDTO> OnCharacterSelected;
        public event Action<CharacterResponseDTO> OnEditRequested;
        public event Action<CharacterResponseDTO> OnProgressionRequested;
        public event Action<CharacterResponseDTO> OnInventoryRequested;
        public event Action<CharacterResponseDTO> OnRelationshipsRequested;

        protected override void Awake()
        {
            base.Awake();
            
            // Find character service
            _characterService = FindObjectOfType<CharacterService>();
            
            // Setup button listeners
            if (editButton != null)
                editButton.onClick.AddListener(() => OnEditRequested?.Invoke(_currentCharacter));
            
            if (progressionButton != null)
                progressionButton.onClick.AddListener(() => OnProgressionRequested?.Invoke(_currentCharacter));
            
            if (inventoryButton != null)
                inventoryButton.onClick.AddListener(() => OnInventoryRequested?.Invoke(_currentCharacter));
            
            if (relationshipsButton != null)
                relationshipsButton.onClick.AddListener(() => OnRelationshipsRequested?.Invoke(_currentCharacter));
        }

        protected override void OnEnable()
        {
            base.OnEnable();
            
            if (_characterService != null)
            {
                _characterService.OnCharacterUpdated += HandleCharacterUpdated;
                _characterService.OnCharacterLevelUp += HandleCharacterLevelUp;
                _characterService.OnCharacterSkillIncreased += HandleCharacterSkillIncreased;
                _characterService.OnCharacterAbilityGained += HandleCharacterAbilityGained;
            }
        }

        protected override void OnDisable()
        {
            base.OnDisable();
            
            if (_characterService != null)
            {
                _characterService.OnCharacterUpdated -= HandleCharacterUpdated;
                _characterService.OnCharacterLevelUp -= HandleCharacterLevelUp;
                _characterService.OnCharacterSkillIncreased -= HandleCharacterSkillIncreased;
                _characterService.OnCharacterAbilityGained -= HandleCharacterAbilityGained;
            }
        }

        /// <summary>
        /// Display character information in the panel
        /// </summary>
        public void DisplayCharacter(CharacterResponseDTO character)
        {
            if (character == null)
            {
                ClearDisplay();
                return;
            }

            _currentCharacter = character;
            UpdateCharacterDisplay();
            OnCharacterSelected?.Invoke(character);
        }

        /// <summary>
        /// Load and display character by ID
        /// </summary>
        public void LoadCharacter(string characterId)
        {
            if (_characterService == null)
            {
                Debug.LogError("[CharacterPanel] CharacterService not found!");
                return;
            }

            _characterService.GetCharacter(characterId, (success, character) =>
            {
                if (success && character != null)
                {
                    DisplayCharacter(character);
                }
                else
                {
                    Debug.LogError($"[CharacterPanel] Failed to load character {characterId}");
                    ClearDisplay();
                }
            });
        }

        private void UpdateCharacterDisplay()
        {
            if (_currentCharacter == null) return;

            // Basic character info
            SetTextSafe(characterNameText, _currentCharacter.CharacterName);
            SetTextSafe(levelText, $"Level {_currentCharacter.Level}");
            SetTextSafe(classText, _currentCharacter.CharacterClass);
            SetTextSafe(raceText, _currentCharacter.Race);
            SetTextSafe(backgroundText, _currentCharacter.Background);

            // Character stats
            UpdateStatsDisplay();

            // Attributes
            UpdateAttributesDisplay();

            // Skills and abilities
            UpdateSkillsDisplay();
            UpdateAbilitiesDisplay();

            // Character details
            UpdateDetailsDisplay();

            // Enable action buttons
            SetButtonsInteractable(true);
        }

        private void UpdateStatsDisplay()
        {
            if (_currentCharacter.DerivedStats == null) return;

            var stats = _currentCharacter.DerivedStats;

            // Health
            SetTextSafe(hpText, $"{stats.CurrentHp}/{stats.MaxHp}");
            SetSliderValue(hpSlider, stats.CurrentHp, stats.MaxHp);

            // Mana/Magic Points
            SetTextSafe(mpText, $"{stats.CurrentMp}/{stats.MaxMp}");
            SetSliderValue(mpSlider, stats.CurrentMp, stats.MaxMp);

            // Experience
            int currentXp = _currentCharacter.Experience;
            int nextLevelXp = CalculateNextLevelXp(_currentCharacter.Level);
            SetTextSafe(experienceText, $"{currentXp}/{nextLevelXp} XP");
            SetSliderValue(experienceSlider, currentXp, nextLevelXp);
        }

        private void UpdateAttributesDisplay()
        {
            if (_currentCharacter.Attributes == null) return;

            var attrs = _currentCharacter.Attributes;
            SetTextSafe(strengthText, $"STR: {attrs.Strength}");
            SetTextSafe(dexterityText, $"DEX: {attrs.Dexterity}");
            SetTextSafe(constitutionText, $"CON: {attrs.Constitution}");
            SetTextSafe(intelligenceText, $"INT: {attrs.Intelligence}");
            SetTextSafe(wisdomText, $"WIS: {attrs.Wisdom}");
            SetTextSafe(charismaText, $"CHA: {attrs.Charisma}");
        }

        private void UpdateSkillsDisplay()
        {
            // Clear existing skill items
            ClearSkillItems();

            if (_currentCharacter.Skills == null || skillsContainer == null || skillItemPrefab == null)
                return;

            // Create skill items
            foreach (var skill in _currentCharacter.Skills)
            {
                GameObject skillItem = Instantiate(skillItemPrefab, skillsContainer);
                _skillItems.Add(skillItem);

                // Setup skill item (assuming it has TextMeshProUGUI components)
                var skillText = skillItem.GetComponentInChildren<TextMeshProUGUI>();
                if (skillText != null)
                {
                    skillText.text = $"{skill.Key}: {skill.Value}";
                }
            }
        }

        private void UpdateAbilitiesDisplay()
        {
            // Clear existing ability items
            ClearAbilityItems();

            if (_currentCharacter.Abilities == null || abilitiesContainer == null || abilityItemPrefab == null)
                return;

            // Create ability items
            foreach (var ability in _currentCharacter.Abilities)
            {
                GameObject abilityItem = Instantiate(abilityItemPrefab, abilitiesContainer);
                _abilityItems.Add(abilityItem);

                // Setup ability item
                var abilityText = abilityItem.GetComponentInChildren<TextMeshProUGUI>();
                if (abilityText != null)
                {
                    abilityText.text = ability;
                }
            }
        }

        private void UpdateDetailsDisplay()
        {
            if (_currentCharacter.Narrative != null)
            {
                SetTextSafe(descriptionText, _currentCharacter.Narrative.Description);
                SetTextSafe(goalsText, string.Join(", ", _currentCharacter.Narrative.Goals));
            }

            if (_currentCharacter.Personality != null)
            {
                SetTextSafe(personalityText, _currentCharacter.Personality.Description);
            }

            if (_currentCharacter.Metadata != null && _currentCharacter.Metadata.ContainsKey("notes"))
            {
                SetTextSafe(notesText, _currentCharacter.Metadata["notes"].ToString());
            }
        }

        private void ClearDisplay()
        {
            _currentCharacter = null;

            // Clear text fields
            SetTextSafe(characterNameText, "No Character Selected");
            SetTextSafe(levelText, "");
            SetTextSafe(classText, "");
            SetTextSafe(raceText, "");
            SetTextSafe(backgroundText, "");
            SetTextSafe(hpText, "");
            SetTextSafe(mpText, "");
            SetTextSafe(experienceText, "");
            SetTextSafe(descriptionText, "");
            SetTextSafe(personalityText, "");
            SetTextSafe(goalsText, "");
            SetTextSafe(notesText, "");

            // Clear attribute texts
            SetTextSafe(strengthText, "");
            SetTextSafe(dexterityText, "");
            SetTextSafe(constitutionText, "");
            SetTextSafe(intelligenceText, "");
            SetTextSafe(wisdomText, "");
            SetTextSafe(charismaText, "");

            // Clear sliders
            SetSliderValue(hpSlider, 0, 1);
            SetSliderValue(mpSlider, 0, 1);
            SetSliderValue(experienceSlider, 0, 1);

            // Clear skills and abilities
            ClearSkillItems();
            ClearAbilityItems();

            // Disable action buttons
            SetButtonsInteractable(false);
        }

        private void ClearSkillItems()
        {
            foreach (var item in _skillItems)
            {
                if (item != null)
                    DestroyImmediate(item);
            }
            _skillItems.Clear();
        }

        private void ClearAbilityItems()
        {
            foreach (var item in _abilityItems)
            {
                if (item != null)
                    DestroyImmediate(item);
            }
            _abilityItems.Clear();
        }

        private void SetButtonsInteractable(bool interactable)
        {
            if (editButton != null) editButton.interactable = interactable;
            if (progressionButton != null) progressionButton.interactable = interactable;
            if (inventoryButton != null) inventoryButton.interactable = interactable;
            if (relationshipsButton != null) relationshipsButton.interactable = interactable;
        }

        #region Event Handlers

        private void HandleCharacterUpdated(CharacterResponseDTO character)
        {
            if (_currentCharacter != null && character.Id == _currentCharacter.Id)
            {
                DisplayCharacter(character);
            }
        }

        private void HandleCharacterLevelUp(CharacterResponseDTO character)
        {
            if (_currentCharacter != null && character.Id == _currentCharacter.Id)
            {
                DisplayCharacter(character);
                
                // Show level up notification
                ShowNotification($"{character.CharacterName} reached level {character.Level}!", NotificationType.Success);
            }
        }

        private void HandleCharacterSkillIncreased(CharacterResponseDTO character, string skillName)
        {
            if (_currentCharacter != null && character.Id == _currentCharacter.Id)
            {
                DisplayCharacter(character);
                
                // Show skill increase notification
                ShowNotification($"{character.CharacterName} improved {skillName}!", NotificationType.Info);
            }
        }

        private void HandleCharacterAbilityGained(CharacterResponseDTO character, string abilityName)
        {
            if (_currentCharacter != null && character.Id == _currentCharacter.Id)
            {
                DisplayCharacter(character);
                
                // Show ability gained notification
                ShowNotification($"{character.CharacterName} gained {abilityName}!", NotificationType.Success);
            }
        }

        #endregion

        #region Utility Methods

        private void SetTextSafe(TextMeshProUGUI textComponent, string text)
        {
            if (textComponent != null)
                textComponent.text = text ?? "";
        }

        private void SetSliderValue(Slider slider, float current, float max)
        {
            if (slider != null && max > 0)
            {
                slider.value = current / max;
            }
        }

        private int CalculateNextLevelXp(int currentLevel)
        {
            // Simple XP calculation - can be made more complex based on game rules
            return currentLevel * 1000;
        }

        private void ShowNotification(string message, NotificationType type)
        {
            // TODO: Implement notification system
            Debug.Log($"[CharacterPanel] {type}: {message}");
        }

        #endregion
    }

    public enum NotificationType
    {
        Info,
        Success,
        Warning,
        Error
    }
} 