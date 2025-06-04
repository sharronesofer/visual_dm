using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using TMPro;
using VDM.DTOs.Character;

namespace VDM.UI.Systems.Character
{
    /// <summary>
    /// UI panel for background selection during character creation
    /// </summary>
    public class BackgroundSelectionPanel : MonoBehaviour
    {
        [Header("Background List")]
        [SerializeField] private Transform backgroundListParent;
        [SerializeField] private GameObject backgroundOptionPrefab;
        [SerializeField] private ScrollRect backgroundScrollRect;
        
        [Header("Background Details")]
        [SerializeField] private GameObject backgroundDetailsPanel;
        [SerializeField] private Image backgroundImage;
        [SerializeField] private TextMeshProUGUI backgroundNameText;
        [SerializeField] private TextMeshProUGUI backgroundDescriptionText;
        [SerializeField] private TextMeshProUGUI backgroundFlavorText;
        
        [Header("Skills and Equipment")]
        [SerializeField] private Transform skillProficienciesParent;
        [SerializeField] private GameObject skillProficiencyPrefab;
        [SerializeField] private Transform equipmentParent;
        [SerializeField] private GameObject equipmentPrefab;
        [SerializeField] private Transform languagesParent;
        [SerializeField] private GameObject languagePrefab;
        [SerializeField] private Transform toolProficienciesParent;
        [SerializeField] private GameObject toolProficiencyPrefab;
        
        [Header("Background Features")]
        [SerializeField] private Transform featuresParent;
        [SerializeField] private GameObject featurePrefab;
        
        [Header("Personality Traits")]
        [SerializeField] private Transform personalityTraitsParent;
        [SerializeField] private GameObject personalityTraitPrefab;
        [SerializeField] private Transform idealsParent;
        [SerializeField] private GameObject idealPrefab;
        [SerializeField] private Transform bondsParent;
        [SerializeField] private GameObject bondPrefab;
        [SerializeField] private Transform flawsParent;
        [SerializeField] private GameObject flawPrefab;
        
        [Header("Selection")]
        [SerializeField] private Button selectBackgroundButton;
        [SerializeField] private TextMeshProUGUI selectButtonText;
        
        // Data
        private List<BackgroundDTO> availableBackgrounds;
        private BackgroundDTO selectedBackground;
        private List<GameObject> backgroundOptions = new List<GameObject>();
        private List<GameObject> skillProficiencyElements = new List<GameObject>();
        private List<GameObject> equipmentElements = new List<GameObject>();
        private List<GameObject> languageElements = new List<GameObject>();
        private List<GameObject> toolProficiencyElements = new List<GameObject>();
        private List<GameObject> featureElements = new List<GameObject>();
        private List<GameObject> personalityTraitElements = new List<GameObject>();
        private List<GameObject> idealElements = new List<GameObject>();
        private List<GameObject> bondElements = new List<GameObject>();
        private List<GameObject> flawElements = new List<GameObject>();
        
        // Events
        public event Action<BackgroundDTO> OnBackgroundSelected;
        public event Action<bool> OnValidationChanged;
        
        private void Awake()
        {
            if (selectBackgroundButton != null)
                selectBackgroundButton.onClick.AddListener(ConfirmBackgroundSelection);
            
            // Initially hide details panel
            if (backgroundDetailsPanel != null)
                backgroundDetailsPanel.SetActive(false);
            
            UpdateSelectButton();
        }
        
        /// <summary>
        /// Initialize the panel with available backgrounds
        /// </summary>
        public void Initialize(List<BackgroundDTO> backgrounds)
        {
            availableBackgrounds = backgrounds;
            PopulateBackgroundList();
        }
        
        /// <summary>
        /// Update display based on current request
        /// </summary>
        public void UpdateDisplay(CharacterCreationRequestDTO request)
        {
            if (request != null && !string.IsNullOrEmpty(request.BackgroundId))
            {
                // Find and select the background that matches the request
                var backgroundToSelect = availableBackgrounds?.Find(b => b.Id == request.BackgroundId);
                if (backgroundToSelect != null)
                {
                    SelectBackground(backgroundToSelect, false); // Don't trigger event since this is just updating display
                }
            }
        }
        
        private void PopulateBackgroundList()
        {
            ClearBackgroundOptions();
            
            if (availableBackgrounds == null || backgroundListParent == null || backgroundOptionPrefab == null)
                return;
            
            foreach (var background in availableBackgrounds)
            {
                GameObject backgroundOption = Instantiate(backgroundOptionPrefab, backgroundListParent);
                BackgroundOption backgroundOptionComponent = backgroundOption.GetComponent<BackgroundOption>();
                
                if (backgroundOptionComponent != null)
                {
                    backgroundOptionComponent.Initialize(background, () => SelectBackground(background));
                }
                
                backgroundOptions.Add(backgroundOption);
            }
        }
        
        private void SelectBackground(BackgroundDTO background, bool triggerEvent = true)
        {
            selectedBackground = background;
            
            // Update background option selection visuals
            UpdateBackgroundOptionSelection();
            
            // Show background details
            ShowBackgroundDetails(background);
            
            // Update select button
            UpdateSelectButton();
            
            // Trigger validation change
            OnValidationChanged?.Invoke(selectedBackground != null);
            
            if (triggerEvent)
            {
                OnBackgroundSelected?.Invoke(selectedBackground);
            }
        }
        
        private void UpdateBackgroundOptionSelection()
        {
            // Update visual selection of background options
            foreach (var option in backgroundOptions)
            {
                var backgroundOptionComponent = option.GetComponent<BackgroundOption>();
                if (backgroundOptionComponent != null)
                {
                    bool isSelected = backgroundOptionComponent.GetBackground()?.Id == selectedBackground?.Id;
                    backgroundOptionComponent.SetSelected(isSelected);
                }
            }
        }
        
        private void ShowBackgroundDetails(BackgroundDTO background)
        {
            if (background == null)
            {
                if (backgroundDetailsPanel != null)
                    backgroundDetailsPanel.SetActive(false);
                return;
            }
            
            if (backgroundDetailsPanel != null)
                backgroundDetailsPanel.SetActive(true);
            
            // Basic background info
            if (backgroundNameText != null)
                backgroundNameText.text = background.Name;
            if (backgroundDescriptionText != null)
                backgroundDescriptionText.text = background.Description;
            if (backgroundFlavorText != null)
                backgroundFlavorText.text = background.FlavorText;
            
            // Load background image
            if (backgroundImage != null && !string.IsNullOrEmpty(background.ImageUrl))
            {
                LoadBackgroundImage(background.ImageUrl);
            }
            
            // Populate skills and equipment
            PopulateSkillProficiencies(background.SkillProficiencies);
            PopulateEquipment(background.Equipment);
            PopulateLanguages(background.Languages);
            PopulateToolProficiencies(background.ToolProficiencies);
            
            // Populate background features
            PopulateFeatures(background.Features);
            
            // Populate personality options
            PopulatePersonalityTraits(background.PersonalityTraits);
            PopulateIdeals(background.Ideals);
            PopulateBonds(background.Bonds);
            PopulateFlaws(background.Flaws);
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
        
        private void PopulateEquipment(List<string> equipment)
        {
            ClearEquipment();
            
            if (equipment == null || equipmentParent == null || equipmentPrefab == null)
                return;
            
            foreach (var item in equipment)
            {
                GameObject equipmentElement = Instantiate(equipmentPrefab, equipmentParent);
                var textComponent = equipmentElement.GetComponentInChildren<TextMeshProUGUI>();
                if (textComponent != null)
                {
                    textComponent.text = item;
                }
                equipmentElements.Add(equipmentElement);
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
        
        private void PopulateToolProficiencies(List<string> tools)
        {
            ClearToolProficiencies();
            
            if (tools == null || toolProficienciesParent == null || toolProficiencyPrefab == null)
                return;
            
            foreach (var tool in tools)
            {
                GameObject toolElement = Instantiate(toolProficiencyPrefab, toolProficienciesParent);
                var textComponent = toolElement.GetComponentInChildren<TextMeshProUGUI>();
                if (textComponent != null)
                {
                    textComponent.text = tool;
                }
                toolProficiencyElements.Add(toolElement);
            }
        }
        
        private void PopulateFeatures(List<string> features)
        {
            ClearFeatures();
            
            if (features == null || featuresParent == null || featurePrefab == null)
                return;
            
            foreach (var feature in features)
            {
                GameObject featureElement = Instantiate(featurePrefab, featuresParent);
                var textComponent = featureElement.GetComponentInChildren<TextMeshProUGUI>();
                if (textComponent != null)
                {
                    textComponent.text = feature;
                }
                featureElements.Add(featureElement);
            }
        }
        
        private void PopulatePersonalityTraits(List<string> traits)
        {
            ClearPersonalityTraits();
            
            if (traits == null || personalityTraitsParent == null || personalityTraitPrefab == null)
                return;
            
            foreach (var trait in traits)
            {
                GameObject traitElement = Instantiate(personalityTraitPrefab, personalityTraitsParent);
                var textComponent = traitElement.GetComponentInChildren<TextMeshProUGUI>();
                if (textComponent != null)
                {
                    textComponent.text = trait;
                }
                personalityTraitElements.Add(traitElement);
            }
        }
        
        private void PopulateIdeals(List<string> ideals)
        {
            ClearIdeals();
            
            if (ideals == null || idealsParent == null || idealPrefab == null)
                return;
            
            foreach (var ideal in ideals)
            {
                GameObject idealElement = Instantiate(idealPrefab, idealsParent);
                var textComponent = idealElement.GetComponentInChildren<TextMeshProUGUI>();
                if (textComponent != null)
                {
                    textComponent.text = ideal;
                }
                idealElements.Add(idealElement);
            }
        }
        
        private void PopulateBonds(List<string> bonds)
        {
            ClearBonds();
            
            if (bonds == null || bondsParent == null || bondPrefab == null)
                return;
            
            foreach (var bond in bonds)
            {
                GameObject bondElement = Instantiate(bondPrefab, bondsParent);
                var textComponent = bondElement.GetComponentInChildren<TextMeshProUGUI>();
                if (textComponent != null)
                {
                    textComponent.text = bond;
                }
                bondElements.Add(bondElement);
            }
        }
        
        private void PopulateFlaws(List<string> flaws)
        {
            ClearFlaws();
            
            if (flaws == null || flawsParent == null || flawPrefab == null)
                return;
            
            foreach (var flaw in flaws)
            {
                GameObject flawElement = Instantiate(flawPrefab, flawsParent);
                var textComponent = flawElement.GetComponentInChildren<TextMeshProUGUI>();
                if (textComponent != null)
                {
                    textComponent.text = flaw;
                }
                flawElements.Add(flawElement);
            }
        }
        
        private void LoadBackgroundImage(string imageUrl)
        {
            // Try to load from Resources first (for local images)
            Sprite backgroundSprite = Resources.Load<Sprite>(imageUrl);
            if (backgroundSprite != null && backgroundImage != null)
            {
                backgroundImage.sprite = backgroundSprite;
            }
            // TODO: Add support for loading from URL if needed
        }
        
        private void UpdateSelectButton()
        {
            if (selectBackgroundButton != null)
                selectBackgroundButton.interactable = selectedBackground != null;
            
            if (selectButtonText != null)
            {
                if (selectedBackground != null)
                    selectButtonText.text = $"Select {selectedBackground.Name}";
                else
                    selectButtonText.text = "Select a Background";
            }
        }
        
        private void ConfirmBackgroundSelection()
        {
            if (selectedBackground != null)
            {
                OnBackgroundSelected?.Invoke(selectedBackground);
            }
        }
        
        #region Cleanup Methods
        
        private void ClearBackgroundOptions()
        {
            foreach (var option in backgroundOptions)
            {
                if (option != null)
                    DestroyImmediate(option);
            }
            backgroundOptions.Clear();
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
        
        private void ClearEquipment()
        {
            foreach (var element in equipmentElements)
            {
                if (element != null)
                    DestroyImmediate(element);
            }
            equipmentElements.Clear();
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
        
        private void ClearFeatures()
        {
            foreach (var element in featureElements)
            {
                if (element != null)
                    DestroyImmediate(element);
            }
            featureElements.Clear();
        }
        
        private void ClearPersonalityTraits()
        {
            foreach (var element in personalityTraitElements)
            {
                if (element != null)
                    DestroyImmediate(element);
            }
            personalityTraitElements.Clear();
        }
        
        private void ClearIdeals()
        {
            foreach (var element in idealElements)
            {
                if (element != null)
                    DestroyImmediate(element);
            }
            idealElements.Clear();
        }
        
        private void ClearBonds()
        {
            foreach (var element in bondElements)
            {
                if (element != null)
                    DestroyImmediate(element);
            }
            bondElements.Clear();
        }
        
        private void ClearFlaws()
        {
            foreach (var element in flawElements)
            {
                if (element != null)
                    DestroyImmediate(element);
            }
            flawElements.Clear();
        }
        
        #endregion
    }
    
    /// <summary>
    /// Individual background option component
    /// </summary>
    public class BackgroundOption : MonoBehaviour
    {
        [Header("UI Elements")]
        [SerializeField] private Button backgroundButton;
        [SerializeField] private TextMeshProUGUI backgroundNameText;
        [SerializeField] private TextMeshProUGUI backgroundDescriptionText;
        [SerializeField] private Image backgroundIcon;
        [SerializeField] private Image selectionBorder;
        
        [Header("Selection Styling")]
        [SerializeField] private Color normalColor = Color.white;
        [SerializeField] private Color selectedColor = Color.cyan;
        
        private BackgroundDTO background;
        private System.Action onSelected;
        
        private void Awake()
        {
            if (backgroundButton != null)
                backgroundButton.onClick.AddListener(() => onSelected?.Invoke());
        }
        
        public void Initialize(BackgroundDTO backgroundData, System.Action onSelectedCallback)
        {
            background = backgroundData;
            onSelected = onSelectedCallback;
            
            if (backgroundNameText != null)
                backgroundNameText.text = background.Name;
            if (backgroundDescriptionText != null)
                backgroundDescriptionText.text = TruncateDescription(background.Description, 100);
            
            // Load background icon if available
            if (backgroundIcon != null && !string.IsNullOrEmpty(background.ImageUrl))
            {
                Sprite icon = Resources.Load<Sprite>(background.ImageUrl);
                if (icon != null)
                    backgroundIcon.sprite = icon;
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
        
        public BackgroundDTO GetBackground()
        {
            return background;
        }
        
        private string TruncateDescription(string description, int maxLength)
        {
            if (string.IsNullOrEmpty(description) || description.Length <= maxLength)
                return description;
            
            return description.Substring(0, maxLength - 3) + "...";
        }
    }
} 