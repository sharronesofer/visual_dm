using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using TMPro;
using VisualDM.Core.DTOs;

namespace VDM.UI.Systems.Character
{
    /// <summary>
    /// UI panel for race selection during character creation
    /// </summary>
    public class RaceSelectionPanel : MonoBehaviour
    {
        [Header("Race List")]
        [SerializeField] private Transform raceListParent;
        [SerializeField] private GameObject raceOptionPrefab;
        [SerializeField] private ScrollRect raceScrollRect;
        
        [Header("Race Details")]
        [SerializeField] private GameObject raceDetailsPanel;
        [SerializeField] private Image raceImage;
        [SerializeField] private TextMeshProUGUI raceNameText;
        [SerializeField] private TextMeshProUGUI raceDescriptionText;
        [SerializeField] private TextMeshProUGUI raceFlavorText;
        [SerializeField] private TextMeshProUGUI raceSizeText;
        [SerializeField] private TextMeshProUGUI raceSpeedText;
        
        [Header("Attribute Bonuses")]
        [SerializeField] private Transform attributeBonusesParent;
        [SerializeField] private GameObject attributeBonusPrefab;
        
        [Header("Racial Traits")]
        [SerializeField] private Transform racialTraitsParent;
        [SerializeField] private GameObject racialTraitPrefab;
        
        [Header("Skills and Languages")]
        [SerializeField] private Transform skillProficienciesParent;
        [SerializeField] private GameObject skillProficiencyPrefab;
        [SerializeField] private Transform languagesParent;
        [SerializeField] private GameObject languagePrefab;
        
        [Header("Selection")]
        [SerializeField] private Button selectRaceButton;
        [SerializeField] private TextMeshProUGUI selectButtonText;
        
        // Data
        private List<RaceDTO> availableRaces;
        private RaceDTO selectedRace;
        private List<GameObject> raceOptions = new List<GameObject>();
        private List<GameObject> attributeBonusElements = new List<GameObject>();
        private List<GameObject> racialTraitElements = new List<GameObject>();
        private List<GameObject> skillProficiencyElements = new List<GameObject>();
        private List<GameObject> languageElements = new List<GameObject>();
        
        // Events
        public event Action<RaceDTO> OnRaceSelected;
        public event Action<bool> OnValidationChanged;
        
        private void Awake()
        {
            if (selectRaceButton != null)
                selectRaceButton.onClick.AddListener(ConfirmRaceSelection);
            
            // Initially hide details panel
            if (raceDetailsPanel != null)
                raceDetailsPanel.SetActive(false);
            
            UpdateSelectButton();
        }
        
        /// <summary>
        /// Initialize the panel with available races
        /// </summary>
        public void Initialize(List<RaceDTO> races)
        {
            availableRaces = races;
            PopulateRaceList();
        }
        
        /// <summary>
        /// Update display based on current request
        /// </summary>
        public void UpdateDisplay(CharacterCreationRequestDTO request)
        {
            if (request != null && !string.IsNullOrEmpty(request.RaceId))
            {
                // Find and select the race that matches the request
                var raceToSelect = availableRaces?.Find(r => r.Id == request.RaceId);
                if (raceToSelect != null)
                {
                    SelectRace(raceToSelect, false); // Don't trigger event since this is just updating display
                }
            }
        }
        
        private void PopulateRaceList()
        {
            ClearRaceOptions();
            
            if (availableRaces == null || raceListParent == null || raceOptionPrefab == null)
                return;
            
            foreach (var race in availableRaces)
            {
                GameObject raceOption = Instantiate(raceOptionPrefab, raceListParent);
                RaceOption raceOptionComponent = raceOption.GetComponent<RaceOption>();
                
                if (raceOptionComponent != null)
                {
                    raceOptionComponent.Initialize(race, () => SelectRace(race));
                }
                
                raceOptions.Add(raceOption);
            }
        }
        
        private void SelectRace(RaceDTO race, bool triggerEvent = true)
        {
            selectedRace = race;
            
            // Update race option selection visuals
            UpdateRaceOptionSelection();
            
            // Show race details
            ShowRaceDetails(race);
            
            // Update select button
            UpdateSelectButton();
            
            // Trigger validation change
            OnValidationChanged?.Invoke(selectedRace != null);
            
            if (triggerEvent)
            {
                OnRaceSelected?.Invoke(selectedRace);
            }
        }
        
        private void UpdateRaceOptionSelection()
        {
            // Update visual selection of race options
            foreach (var option in raceOptions)
            {
                var raceOptionComponent = option.GetComponent<RaceOption>();
                if (raceOptionComponent != null)
                {
                    bool isSelected = raceOptionComponent.GetRace()?.Id == selectedRace?.Id;
                    raceOptionComponent.SetSelected(isSelected);
                }
            }
        }
        
        private void ShowRaceDetails(RaceDTO race)
        {
            if (race == null)
            {
                if (raceDetailsPanel != null)
                    raceDetailsPanel.SetActive(false);
                return;
            }
            
            if (raceDetailsPanel != null)
                raceDetailsPanel.SetActive(true);
            
            // Basic race info
            if (raceNameText != null)
                raceNameText.text = race.Name;
            if (raceDescriptionText != null)
                raceDescriptionText.text = race.Description;
            if (raceFlavorText != null)
                raceFlavorText.text = race.FlavorText;
            
            // Size and speed
            if (raceSizeText != null)
                raceSizeText.text = GetSizeText(race.Size);
            if (raceSpeedText != null)
                raceSpeedText.text = $"{race.Speed} feet";
            
            // Load race image
            if (raceImage != null && !string.IsNullOrEmpty(race.ImageUrl))
            {
                LoadRaceImage(race.ImageUrl);
            }
            
            // Populate attribute bonuses
            PopulateAttributeBonuses(race.AttributeBonuses);
            
            // Populate racial traits
            PopulateRacialTraits(race.RacialTraits);
            
            // Populate skill proficiencies
            PopulateSkillProficiencies(race.SkillProficiencies);
            
            // Populate languages
            PopulateLanguages(race.Languages);
        }
        
        private void PopulateAttributeBonuses(AttributeBonusesDTO bonuses)
        {
            ClearAttributeBonuses();
            
            if (bonuses == null || attributeBonusesParent == null || attributeBonusPrefab == null)
                return;
            
            var attributeNames = new Dictionary<string, int>
            {
                { "Strength", bonuses.Strength },
                { "Dexterity", bonuses.Dexterity },
                { "Constitution", bonuses.Constitution },
                { "Intelligence", bonuses.Intelligence },
                { "Wisdom", bonuses.Wisdom },
                { "Charisma", bonuses.Charisma }
            };
            
            foreach (var attribute in attributeNames)
            {
                if (attribute.Value > 0)
                {
                    GameObject bonusElement = Instantiate(attributeBonusPrefab, attributeBonusesParent);
                    var textComponent = bonusElement.GetComponentInChildren<TextMeshProUGUI>();
                    if (textComponent != null)
                    {
                        textComponent.text = $"{attribute.Key}: +{attribute.Value}";
                    }
                    attributeBonusElements.Add(bonusElement);
                }
            }
        }
        
        private void PopulateRacialTraits(List<string> traits)
        {
            ClearRacialTraits();
            
            if (traits == null || racialTraitsParent == null || racialTraitPrefab == null)
                return;
            
            foreach (var trait in traits)
            {
                GameObject traitElement = Instantiate(racialTraitPrefab, racialTraitsParent);
                var textComponent = traitElement.GetComponentInChildren<TextMeshProUGUI>();
                if (textComponent != null)
                {
                    textComponent.text = trait;
                }
                racialTraitElements.Add(traitElement);
            }
        }
        
        private void PopulateSkillProficiencies(List<string> skills)
        {
            ClearSkillProficiencies();
            
            if (skills == null || skillProficienciesParent == null || skillProficiencyPrefab == null)
                return;
            
            foreach (var skill in skills)
            {
                GameObject skillElement = Instantiate(skillProficiencyPrefab, skillProficienciesParent);
                var textComponent = skillElement.GetComponentInChildren<TextMeshProUGUI>();
                if (textComponent != null)
                {
                    textComponent.text = skill;
                }
                skillProficiencyElements.Add(skillElement);
            }
        }
        
        private void PopulateLanguages(List<string> languages)
        {
            ClearLanguages();
            
            if (languages == null || languagesParent == null || languagePrefab == null)
                return;
            
            foreach (var language in languages)
            {
                GameObject languageElement = Instantiate(languagePrefab, languagesParent);
                var textComponent = languageElement.GetComponentInChildren<TextMeshProUGUI>();
                if (textComponent != null)
                {
                    textComponent.text = language;
                }
                languageElements.Add(languageElement);
            }
        }
        
        private void LoadRaceImage(string imageUrl)
        {
            // Try to load from Resources first (for local images)
            Sprite raceSprite = Resources.Load<Sprite>(imageUrl);
            if (raceSprite != null && raceImage != null)
            {
                raceImage.sprite = raceSprite;
            }
            // TODO: Add support for loading from URL if needed
        }
        
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
        
        private void UpdateSelectButton()
        {
            if (selectRaceButton != null)
                selectRaceButton.interactable = selectedRace != null;
            
            if (selectButtonText != null)
            {
                if (selectedRace != null)
                    selectButtonText.text = $"Select {selectedRace.Name}";
                else
                    selectButtonText.text = "Select a Race";
            }
        }
        
        private void ConfirmRaceSelection()
        {
            if (selectedRace != null)
            {
                OnRaceSelected?.Invoke(selectedRace);
            }
        }
        
        #region Cleanup Methods
        
        private void ClearRaceOptions()
        {
            foreach (var option in raceOptions)
            {
                if (option != null)
                    DestroyImmediate(option);
            }
            raceOptions.Clear();
        }
        
        private void ClearAttributeBonuses()
        {
            foreach (var element in attributeBonusElements)
            {
                if (element != null)
                    DestroyImmediate(element);
            }
            attributeBonusElements.Clear();
        }
        
        private void ClearRacialTraits()
        {
            foreach (var element in racialTraitElements)
            {
                if (element != null)
                    DestroyImmediate(element);
            }
            racialTraitElements.Clear();
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
        
        #endregion
    }
    
    /// <summary>
    /// Individual race option component
    /// </summary>
    public class RaceOption : MonoBehaviour
    {
        [Header("UI Elements")]
        [SerializeField] private Button raceButton;
        [SerializeField] private TextMeshProUGUI raceNameText;
        [SerializeField] private TextMeshProUGUI raceDescriptionText;
        [SerializeField] private Image raceIcon;
        [SerializeField] private Image selectionBorder;
        
        [Header("Selection Styling")]
        [SerializeField] private Color normalColor = Color.white;
        [SerializeField] private Color selectedColor = Color.cyan;
        
        private RaceDTO race;
        private System.Action onSelected;
        
        private void Awake()
        {
            if (raceButton != null)
                raceButton.onClick.AddListener(() => onSelected?.Invoke());
        }
        
        public void Initialize(RaceDTO raceData, System.Action onSelectedCallback)
        {
            race = raceData;
            onSelected = onSelectedCallback;
            
            if (raceNameText != null)
                raceNameText.text = race.Name;
            if (raceDescriptionText != null)
                raceDescriptionText.text = TruncateDescription(race.Description, 100);
            
            // Load race icon if available
            if (raceIcon != null && !string.IsNullOrEmpty(race.ImageUrl))
            {
                Sprite icon = Resources.Load<Sprite>(race.ImageUrl);
                if (icon != null)
                    raceIcon.sprite = icon;
            }
            
            SetSelected(false);
        }
        
        public void SetSelected(bool isSelected)
        {
            if (selectionBorder != null)
            {
                selectionBorder.color = isSelected ? selectedColor : normalColor;
                selectionBorder.gameObject.SetActive(isSelected);
            }
        }
        
        public RaceDTO GetRace()
        {
            return race;
        }
        
        private string TruncateDescription(string description, int maxLength)
        {
            if (string.IsNullOrEmpty(description) || description.Length <= maxLength)
                return description;
            
            return description.Substring(0, maxLength - 3) + "...";
        }
    }
} 