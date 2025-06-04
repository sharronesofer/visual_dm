using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using TMPro;
using VDM.DTOs.Character;

namespace VDM.UI.Systems.Character
{
    /// <summary>
    /// UI panel for final character review and creation confirmation
    /// </summary>
    public class CharacterReviewPanel : MonoBehaviour
    {
        [Header("Character Overview")]
        [SerializeField] private Image characterPortrait;
        [SerializeField] private TextMeshProUGUI characterNameText;
        [SerializeField] private TextMeshProUGUI characterDescriptionText;
        [SerializeField] private TextMeshProUGUI characterBackstoryText;
        
        [Header("Race Information")]
        [SerializeField] private TextMeshProUGUI raceNameText;
        [SerializeField] private TextMeshProUGUI raceSizeText;
        [SerializeField] private TextMeshProUGUI raceSpeedText;
        [SerializeField] private Transform raceTraitsParent;
        [SerializeField] private GameObject raceTraitPrefab;
        
        [Header("Attributes")]
        [SerializeField] private Transform attributesParent;
        [SerializeField] private GameObject attributePrefab;
        [SerializeField] private TextMeshProUGUI attributeSummaryText;
        
        [Header("Background Information")]
        [SerializeField] private TextMeshProUGUI backgroundNameText;
        [SerializeField] private TextMeshProUGUI backgroundDescriptionText;
        [SerializeField] private Transform backgroundFeaturesParent;
        [SerializeField] private GameObject backgroundFeaturePrefab;
        
        [Header("Skills and Proficiencies")]
        [SerializeField] private Transform skillProficienciesParent;
        [SerializeField] private GameObject skillProficiencyPrefab;
        [SerializeField] private Transform languagesParent;
        [SerializeField] private GameObject languagePrefab;
        [SerializeField] private Transform toolProficienciesParent;
        [SerializeField] private GameObject toolProficiencyPrefab;
        
        [Header("Personality Traits")]
        [SerializeField] private TextMeshProUGUI personalityTraitText;
        [SerializeField] private TextMeshProUGUI idealText;
        [SerializeField] private TextMeshProUGUI bondText;
        [SerializeField] private TextMeshProUGUI flawText;
        
        [Header("Equipment")]
        [SerializeField] private Transform equipmentParent;
        [SerializeField] private GameObject equipmentPrefab;
        
        [Header("Character Stats")]
        [SerializeField] private TextMeshProUGUI hitPointsText;
        [SerializeField] private TextMeshProUGUI armorClassText;
        [SerializeField] private TextMeshProUGUI initiativeText;
        [SerializeField] private TextMeshProUGUI speedText;
        [SerializeField] private TextMeshProUGUI proficiencyBonusText;
        
        [Header("Actions")]
        [SerializeField] private Button createCharacterButton;
        [SerializeField] private Button editCharacterButton;
        [SerializeField] private Button exportCharacterButton;
        [SerializeField] private TextMeshProUGUI createButtonText;
        
        [Header("Validation")]
        [SerializeField] private GameObject validationPanel;
        [SerializeField] private TextMeshProUGUI validationText;
        
        // Data
        private CharacterCreationRequestDTO currentRequest;
        private RaceDTO selectedRace;
        private BackgroundDTO selectedBackground;
        private List<RaceDTO> availableRaces;
        private List<BackgroundDTO> availableBackgrounds;
        
        // UI Elements
        private List<GameObject> raceTraitElements = new List<GameObject>();
        private List<GameObject> attributeElements = new List<GameObject>();
        private List<GameObject> backgroundFeatureElements = new List<GameObject>();
        private List<GameObject> skillProficiencyElements = new List<GameObject>();
        private List<GameObject> languageElements = new List<GameObject>();
        private List<GameObject> toolProficiencyElements = new List<GameObject>();
        private List<GameObject> equipmentElements = new List<GameObject>();
        
        // Events
        public event Action OnCreateCharacter;
        public event Action<bool> OnValidationChanged;
        
        private void Awake()
        {
            SetupEventListeners();
            
            // Hide validation initially
            if (validationPanel != null)
                validationPanel.SetActive(false);
        }
        
        private void SetupEventListeners()
        {
            if (createCharacterButton != null)
                createCharacterButton.onClick.AddListener(() => OnCreateCharacter?.Invoke());
            if (editCharacterButton != null)
                editCharacterButton.onClick.AddListener(GoBackToEdit);
            if (exportCharacterButton != null)
                exportCharacterButton.onClick.AddListener(ExportCharacterData);
        }
        
        /// <summary>
        /// Initialize the panel
        /// </summary>
        public void Initialize()
        {
            UpdateValidation();
        }
        
        /// <summary>
        /// Update display with complete character data
        /// </summary>
        public void UpdateDisplay(CharacterCreationRequestDTO request, List<RaceDTO> races, List<BackgroundDTO> backgrounds)
        {
            currentRequest = request;
            availableRaces = races;
            availableBackgrounds = backgrounds;
            
            if (request == null) return;
            
            // Find selected race and background
            selectedRace = availableRaces?.Find(r => r.Id == request.RaceId);
            selectedBackground = availableBackgrounds?.Find(b => b.Id == request.BackgroundId);
            
            // Update all display sections
            UpdateCharacterOverview();
            UpdateRaceInformation();
            UpdateAttributes();
            UpdateBackgroundInformation();
            UpdateSkillsAndProficiencies();
            UpdatePersonalityTraits();
            UpdateEquipment();
            UpdateCharacterStats();
            UpdateValidation();
        }
        
        #region Display Updates
        
        private void UpdateCharacterOverview()
        {
            if (characterNameText != null)
                characterNameText.text = currentRequest.Name ?? "Unnamed Character";
            if (characterDescriptionText != null)
                characterDescriptionText.text = currentRequest.Description ?? "";
            if (characterBackstoryText != null)
                characterBackstoryText.text = currentRequest.Backstory ?? "";
            
            // Load character portrait
            if (characterPortrait != null && !string.IsNullOrEmpty(currentRequest.PortraitUrl))
            {
                Sprite portraitSprite = Resources.Load<Sprite>(currentRequest.PortraitUrl);
                if (portraitSprite != null)
                    characterPortrait.sprite = portraitSprite;
            }
        }
        
        private void UpdateRaceInformation()
        {
            if (selectedRace == null) return;
            
            if (raceNameText != null)
                raceNameText.text = selectedRace.Name;
            if (raceSizeText != null)
                raceSizeText.text = GetSizeText(selectedRace.Size);
            if (raceSpeedText != null)
                raceSpeedText.text = $"{selectedRace.Speed} feet";
            
            // Populate racial traits
            ClearRaceTraits();
            if (selectedRace.RacialTraits != null && raceTraitsParent != null && raceTraitPrefab != null)
            {
                foreach (var trait in selectedRace.RacialTraits)
                {
                    GameObject traitElement = Instantiate(raceTraitPrefab, raceTraitsParent);
                    var textComponent = traitElement.GetComponentInChildren<TextMeshProUGUI>();
                    if (textComponent != null)
                        textComponent.text = trait;
                    raceTraitElements.Add(traitElement);
                }
            }
        }
        
        private void UpdateAttributes()
        {
            if (currentRequest.Attributes == null) return;
            
            ClearAttributes();
            
            var attributes = new Dictionary<string, int>
            {
                { "Strength", currentRequest.Attributes.Strength },
                { "Dexterity", currentRequest.Attributes.Dexterity },
                { "Constitution", currentRequest.Attributes.Constitution },
                { "Intelligence", currentRequest.Attributes.Intelligence },
                { "Wisdom", currentRequest.Attributes.Wisdom },
                { "Charisma", currentRequest.Attributes.Charisma }
            };
            
            string summaryText = "";
            
            if (attributesParent != null && attributePrefab != null)
            {
                foreach (var attribute in attributes)
                {
                    GameObject attributeElement = Instantiate(attributePrefab, attributesParent);
                    var textComponent = attributeElement.GetComponentInChildren<TextMeshProUGUI>();
                    if (textComponent != null)
                    {
                        int modifier = (attribute.Value - 10) / 2;
                        string modifierText = modifier >= 0 ? $"+{modifier}" : modifier.ToString();
                        textComponent.text = $"{attribute.Key}: {attribute.Value} ({modifierText})";
                        
                        if (!string.IsNullOrEmpty(summaryText))
                            summaryText += ", ";
                        summaryText += $"{attribute.Key}: {attribute.Value}";
                    }
                    attributeElements.Add(attributeElement);
                }
            }
            
            if (attributeSummaryText != null)
                attributeSummaryText.text = summaryText;
        }
        
        private void UpdateBackgroundInformation()
        {
            if (selectedBackground == null) return;
            
            if (backgroundNameText != null)
                backgroundNameText.text = selectedBackground.Name;
            if (backgroundDescriptionText != null)
                backgroundDescriptionText.text = selectedBackground.Description;
            
            // Populate background features
            ClearBackgroundFeatures();
            if (selectedBackground.Features != null && backgroundFeaturesParent != null && backgroundFeaturePrefab != null)
            {
                foreach (var feature in selectedBackground.Features)
                {
                    GameObject featureElement = Instantiate(backgroundFeaturePrefab, backgroundFeaturesParent);
                    var textComponent = featureElement.GetComponentInChildren<TextMeshProUGUI>();
                    if (textComponent != null)
                        textComponent.text = feature;
                    backgroundFeatureElements.Add(featureElement);
                }
            }
        }
        
        private void UpdateSkillsAndProficiencies()
        {
            // Clear existing elements
            ClearSkillProficiencies();
            ClearLanguages();
            ClearToolProficiencies();
            
            // Combine skills from race and background
            var allSkills = new List<string>();
            if (selectedRace?.SkillProficiencies != null)
                allSkills.AddRange(selectedRace.SkillProficiencies);
            if (selectedBackground?.SkillProficiencies != null)
                allSkills.AddRange(selectedBackground.SkillProficiencies);
            
            // Populate skill proficiencies
            if (allSkills.Count > 0 && skillProficienciesParent != null && skillProficiencyPrefab != null)
            {
                foreach (var skill in allSkills)
                {
                    GameObject skillElement = Instantiate(skillProficiencyPrefab, skillProficienciesParent);
                    var textComponent = skillElement.GetComponentInChildren<TextMeshProUGUI>();
                    if (textComponent != null)
                        textComponent.text = skill;
                    skillProficiencyElements.Add(skillElement);
                }
            }
            
            // Combine languages from race and background
            var allLanguages = new List<string>();
            if (selectedRace?.Languages != null)
                allLanguages.AddRange(selectedRace.Languages);
            if (selectedBackground?.Languages != null)
                allLanguages.AddRange(selectedBackground.Languages);
            
            // Populate languages
            if (allLanguages.Count > 0 && languagesParent != null && languagePrefab != null)
            {
                foreach (var language in allLanguages)
                {
                    GameObject languageElement = Instantiate(languagePrefab, languagesParent);
                    var textComponent = languageElement.GetComponentInChildren<TextMeshProUGUI>();
                    if (textComponent != null)
                        textComponent.text = language;
                    languageElements.Add(languageElement);
                }
            }
            
            // Populate tool proficiencies
            if (selectedBackground?.ToolProficiencies != null && toolProficienciesParent != null && toolProficiencyPrefab != null)
            {
                foreach (var tool in selectedBackground.ToolProficiencies)
                {
                    GameObject toolElement = Instantiate(toolProficiencyPrefab, toolProficienciesParent);
                    var textComponent = toolElement.GetComponentInChildren<TextMeshProUGUI>();
                    if (textComponent != null)
                        textComponent.text = tool;
                    toolProficiencyElements.Add(toolElement);
                }
            }
        }
        
        private void UpdatePersonalityTraits()
        {
            if (currentRequest.PersonalityTraits == null) return;
            
            if (personalityTraitText != null)
                personalityTraitText.text = currentRequest.PersonalityTraits.GetValueOrDefault("PersonalityTrait", "");
            if (idealText != null)
                idealText.text = currentRequest.PersonalityTraits.GetValueOrDefault("Ideal", "");
            if (bondText != null)
                bondText.text = currentRequest.PersonalityTraits.GetValueOrDefault("Bond", "");
            if (flawText != null)
                flawText.text = currentRequest.PersonalityTraits.GetValueOrDefault("Flaw", "");
        }
        
        private void UpdateEquipment()
        {
            if (selectedBackground?.Equipment == null) return;
            
            ClearEquipment();
            
            if (equipmentParent != null && equipmentPrefab != null)
            {
                foreach (var item in selectedBackground.Equipment)
                {
                    GameObject equipmentElement = Instantiate(equipmentPrefab, equipmentParent);
                    var textComponent = equipmentElement.GetComponentInChildren<TextMeshProUGUI>();
                    if (textComponent != null)
                        textComponent.text = item;
                    equipmentElements.Add(equipmentElement);
                }
            }
        }
        
        private void UpdateCharacterStats()
        {
            if (currentRequest.Attributes == null) return;
            
            // Calculate basic stats
            int constitution = currentRequest.Attributes.Constitution;
            int dexterity = currentRequest.Attributes.Dexterity;
            int constitutionModifier = (constitution - 10) / 2;
            int dexterityModifier = (dexterity - 10) / 2;
            
            // Hit Points (base class HP + CON modifier)
            int hitPoints = 8 + constitutionModifier; // Assuming average starting HP
            if (hitPointsText != null)
                hitPointsText.text = hitPoints.ToString();
            
            // Armor Class (10 + DEX modifier, base)
            int armorClass = 10 + dexterityModifier;
            if (armorClassText != null)
                armorClassText.text = armorClass.ToString();
            
            // Initiative (DEX modifier)
            string initiativeModifier = dexterityModifier >= 0 ? $"+{dexterityModifier}" : dexterityModifier.ToString();
            if (initiativeText != null)
                initiativeText.text = initiativeModifier;
            
            // Speed (from race)
            if (speedText != null && selectedRace != null)
                speedText.text = $"{selectedRace.Speed} ft";
            
            // Proficiency Bonus (level 1)
            if (proficiencyBonusText != null)
                proficiencyBonusText.text = "+2";
        }
        
        #endregion
        
        #region Validation
        
        private void UpdateValidation()
        {
            bool isValid = ValidateCharacter(out string validationMessage);
            
            if (validationPanel != null)
                validationPanel.SetActive(!isValid);
            if (validationText != null)
                validationText.text = validationMessage;
            
            if (createCharacterButton != null)
                createCharacterButton.interactable = isValid;
            
            OnValidationChanged?.Invoke(isValid);
        }
        
        private bool ValidateCharacter(out string message)
        {
            if (currentRequest == null)
            {
                message = "No character data available.";
                return false;
            }
            
            if (string.IsNullOrEmpty(currentRequest.Name))
            {
                message = "Character name is required.";
                return false;
            }
            
            if (string.IsNullOrEmpty(currentRequest.RaceId))
            {
                message = "Race selection is required.";
                return false;
            }
            
            if (currentRequest.Attributes == null)
            {
                message = "Attribute allocation is required.";
                return false;
            }
            
            if (string.IsNullOrEmpty(currentRequest.BackgroundId))
            {
                message = "Background selection is required.";
                return false;
            }
            
            if (currentRequest.PersonalityTraits == null || currentRequest.PersonalityTraits.Count == 0)
            {
                message = "Personality traits are required.";
                return false;
            }
            
            message = "";
            return true;
        }
        
        #endregion
        
        #region Actions
        
        private void GoBackToEdit()
        {
            // This would trigger navigation back to previous steps
            // Implementation depends on parent wizard structure
            Debug.Log("Edit character requested - should navigate back to previous steps");
        }
        
        private void ExportCharacterData()
        {
            if (currentRequest == null) return;
            
            // Export character data to JSON for external use
            string characterJson = JsonUtility.ToJson(currentRequest, true);
            Debug.Log($"Character Data Export:\n{characterJson}");
            
            // TODO: Add actual file export functionality
            // This could save to a file, copy to clipboard, etc.
        }
        
        #endregion
        
        #region Utility Methods
        
        private string GetSizeText(int size)
        {
            switch (size)
            {
                case 0: return "Small";
                case 1: return "Medium";
                case 2: return "Large";
                default: return "Medium";
            }
        }
        
        #endregion
        
        #region Cleanup Methods
        
        private void ClearRaceTraits()
        {
            foreach (var element in raceTraitElements)
            {
                if (element != null)
                    DestroyImmediate(element);
            }
            raceTraitElements.Clear();
        }
        
        private void ClearAttributes()
        {
            foreach (var element in attributeElements)
            {
                if (element != null)
                    DestroyImmediate(element);
            }
            attributeElements.Clear();
        }
        
        private void ClearBackgroundFeatures()
        {
            foreach (var element in backgroundFeatureElements)
            {
                if (element != null)
                    DestroyImmediate(element);
            }
            backgroundFeatureElements.Clear();
        }
        
        private void ClearSkillProficiencies()
        {
            foreach (var element in skillProficiencyElements)
            {
                if (element != null)
                    DestroyImmediate(element);
            }
            skillProficiencyElements.Clear();
        }
        
        private void ClearLanguages()
        {
            foreach (var element in languageElements)
            {
                if (element != null)
                    DestroyImmediate(element);
            }
            languageElements.Clear();
        }
        
        private void ClearToolProficiencies()
        {
            foreach (var element in toolProficiencyElements)
            {
                if (element != null)
                    DestroyImmediate(element);
            }
            toolProficiencyElements.Clear();
        }
        
        private void ClearEquipment()
        {
            foreach (var element in equipmentElements)
            {
                if (element != null)
                    DestroyImmediate(element);
            }
            equipmentElements.Clear();
        }
        
        #endregion
    }
} 