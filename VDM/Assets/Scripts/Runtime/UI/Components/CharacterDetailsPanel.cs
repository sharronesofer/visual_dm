using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using TMPro;
using VDM.DTOs.Character;

namespace VDM.Systems.Character.UI
{
    /// <summary>
    /// UI panel for character details and personality traits during character creation
    /// </summary>
    public class CharacterDetailsPanel : MonoBehaviour
    {
        [Header("Character Information")]
        [SerializeField] private TMP_InputField characterNameInput;
        [SerializeField] private TMP_InputField characterDescriptionInput;
        [SerializeField] private TMP_InputField characterBackstoryInput;
        [SerializeField] private Button portraitSelectButton;
        [SerializeField] private Image characterPortrait;
        [SerializeField] private TextMeshProUGUI portraitButtonText;
        
        [Header("Portrait Selection")]
        [SerializeField] private GameObject portraitSelectionPanel;
        [SerializeField] private Transform portraitOptionsParent;
        [SerializeField] private GameObject portraitOptionPrefab;
        [SerializeField] private Button portraitConfirmButton;
        [SerializeField] private Button portraitCancelButton;
        [SerializeField] private ScrollRect portraitScrollRect;
        
        [Header("Personality Traits")]
        [SerializeField] private TMP_Dropdown personalityTraitDropdown;
        [SerializeField] private TMP_Dropdown idealDropdown;
        [SerializeField] private TMP_Dropdown bondDropdown;
        [SerializeField] private TMP_Dropdown flawDropdown;
        
        [Header("Custom Trait Input")]
        [SerializeField] private GameObject customTraitPanel;
        [SerializeField] private TMP_InputField customPersonalityTraitInput;
        [SerializeField] private TMP_InputField customIdealInput;
        [SerializeField] private TMP_InputField customBondInput;
        [SerializeField] private TMP_InputField customFlawInput;
        [SerializeField] private Toggle useCustomTraitsToggle;
        
        [Header("Character Summary")]
        [SerializeField] private Transform characterSummaryParent;
        [SerializeField] private TextMeshProUGUI characterSummaryText;
        [SerializeField] private Button generateRandomTraitsButton;
        
        [Header("Validation")]
        [SerializeField] private GameObject validationPanel;
        [SerializeField] private TextMeshProUGUI validationText;
        
        // Data
        private string selectedPortraitUrl;
        private List<string> availablePortraits;
        private List<GameObject> portraitOptions = new List<GameObject>();
        private BackgroundDTO currentBackground; // For trait options
        private TraitSelectionDTO currentTraits;
        
        // Portrait data
        private readonly List<string> defaultPortraits = new List<string>
        {
            "Portraits/Human_Male_1", "Portraits/Human_Female_1",
            "Portraits/Elf_Male_1", "Portraits/Elf_Female_1",
            "Portraits/Dwarf_Male_1", "Portraits/Dwarf_Female_1",
            "Portraits/Halfling_Male_1", "Portraits/Halfling_Female_1"
        };
        
        // Events
        public event Action<string, string, string, string, TraitSelectionDTO> OnDetailsCompleted;
        public event Action<bool> OnValidationChanged;
        
        private void Awake()
        {
            SetupEventListeners();
            availablePortraits = new List<string>(defaultPortraits);
            currentTraits = new TraitSelectionDTO();
            
            // Hide validation and portrait selection initially
            if (validationPanel != null)
                validationPanel.SetActive(false);
            if (portraitSelectionPanel != null)
                portraitSelectionPanel.SetActive(false);
            if (customTraitPanel != null)
                customTraitPanel.SetActive(false);
        }
        
        private void SetupEventListeners()
        {
            // Portrait selection
            if (portraitSelectButton != null)
                portraitSelectButton.onClick.AddListener(ShowPortraitSelection);
            if (portraitConfirmButton != null)
                portraitConfirmButton.onClick.AddListener(ConfirmPortraitSelection);
            if (portraitCancelButton != null)
                portraitCancelButton.onClick.AddListener(HidePortraitSelection);
            
            // Custom traits toggle
            if (useCustomTraitsToggle != null)
                useCustomTraitsToggle.onValueChanged.AddListener(OnCustomTraitsToggled);
            
            // Random traits generation
            if (generateRandomTraitsButton != null)
                generateRandomTraitsButton.onClick.AddListener(GenerateRandomTraits);
            
            // Input field listeners
            if (characterNameInput != null)
                characterNameInput.onValueChanged.AddListener(OnInputChanged);
            if (characterDescriptionInput != null)
                characterDescriptionInput.onValueChanged.AddListener(OnInputChanged);
            if (characterBackstoryInput != null)
                characterBackstoryInput.onValueChanged.AddListener(OnInputChanged);
            
            // Trait dropdown listeners
            if (personalityTraitDropdown != null)
                personalityTraitDropdown.onValueChanged.AddListener(OnPersonalityTraitChanged);
            if (idealDropdown != null)
                idealDropdown.onValueChanged.AddListener(OnIdealChanged);
            if (bondDropdown != null)
                bondDropdown.onValueChanged.AddListener(OnBondChanged);
            if (flawDropdown != null)
                flawDropdown.onValueChanged.AddListener(OnFlawChanged);
        }
        
        /// <summary>
        /// Initialize the panel
        /// </summary>
        public void Initialize()
        {
            PopulatePortraitOptions();
            UpdateCharacterSummary();
            UpdateValidation();
        }
        
        /// <summary>
        /// Update display based on current request
        /// </summary>
        public void UpdateDisplay(CharacterCreationRequestDTO request)
        {
            if (request == null) return;
            
            // Update input fields
            if (characterNameInput != null)
                characterNameInput.text = request.Name ?? "";
            if (characterDescriptionInput != null)
                characterDescriptionInput.text = request.Description ?? "";
            if (characterBackstoryInput != null)
                characterBackstoryInput.text = request.Backstory ?? "";
            
            // Update portrait
            if (!string.IsNullOrEmpty(request.PortraitUrl))
            {
                selectedPortraitUrl = request.PortraitUrl;
                LoadPortrait(selectedPortraitUrl);
            }
            
            // Update personality traits
            if (request.PersonalityTraits != null)
            {
                currentTraits = new TraitSelectionDTO
                {
                    PersonalityTrait = request.PersonalityTraits.GetValueOrDefault("PersonalityTrait", ""),
                    Ideal = request.PersonalityTraits.GetValueOrDefault("Ideal", ""),
                    Bond = request.PersonalityTraits.GetValueOrDefault("Bond", ""),
                    Flaw = request.PersonalityTraits.GetValueOrDefault("Flaw", "")
                };
                
                UpdateTraitSelections();
            }
            
            UpdateCharacterSummary();
            UpdateValidation();
        }
        
        /// <summary>
        /// Set background data for trait options
        /// </summary>
        public void SetBackgroundData(BackgroundDTO background)
        {
            currentBackground = background;
            PopulateTraitDropdowns();
        }
        
        #region Portrait Selection
        
        private void PopulatePortraitOptions()
        {
            ClearPortraitOptions();
            
            if (portraitOptionsParent == null || portraitOptionPrefab == null)
                return;
            
            foreach (var portraitPath in availablePortraits)
            {
                GameObject portraitOption = Instantiate(portraitOptionPrefab, portraitOptionsParent);
                PortraitOption optionComponent = portraitOption.GetComponent<PortraitOption>();
                
                if (optionComponent != null)
                {
                    optionComponent.Initialize(portraitPath, () => SelectPortrait(portraitPath));
                }
                
                portraitOptions.Add(portraitOption);
            }
        }
        
        private void ShowPortraitSelection()
        {
            if (portraitSelectionPanel != null)
                portraitSelectionPanel.SetActive(true);
        }
        
        private void HidePortraitSelection()
        {
            if (portraitSelectionPanel != null)
                portraitSelectionPanel.SetActive(false);
        }
        
        private void SelectPortrait(string portraitPath)
        {
            selectedPortraitUrl = portraitPath;
            LoadPortrait(portraitPath);
            
            // Update portrait options selection
            foreach (var option in portraitOptions)
            {
                var optionComponent = option.GetComponent<PortraitOption>();
                if (optionComponent != null)
                {
                    optionComponent.SetSelected(optionComponent.GetPortraitPath() == portraitPath);
                }
            }
        }
        
        private void ConfirmPortraitSelection()
        {
            HidePortraitSelection();
            UpdateValidation();
            TriggerDetailsCompleted();
        }
        
        private void LoadPortrait(string portraitPath)
        {
            if (characterPortrait == null) return;
            
            Sprite portraitSprite = Resources.Load<Sprite>(portraitPath);
            if (portraitSprite != null)
            {
                characterPortrait.sprite = portraitSprite;
                if (portraitButtonText != null)
                    portraitButtonText.text = "Change Portrait";
            }
        }
        
        #endregion
        
        #region Personality Traits
        
        private void PopulateTraitDropdowns()
        {
            if (currentBackground == null) return;
            
            // Populate personality trait dropdown
            if (personalityTraitDropdown != null && currentBackground.PersonalityTraits != null)
            {
                PopulateDropdown(personalityTraitDropdown, currentBackground.PersonalityTraits, "Select a personality trait...");
            }
            
            // Populate ideal dropdown
            if (idealDropdown != null && currentBackground.Ideals != null)
            {
                PopulateDropdown(idealDropdown, currentBackground.Ideals, "Select an ideal...");
            }
            
            // Populate bond dropdown
            if (bondDropdown != null && currentBackground.Bonds != null)
            {
                PopulateDropdown(bondDropdown, currentBackground.Bonds, "Select a bond...");
            }
            
            // Populate flaw dropdown
            if (flawDropdown != null && currentBackground.Flaws != null)
            {
                PopulateDropdown(flawDropdown, currentBackground.Flaws, "Select a flaw...");
            }
        }
        
        private void PopulateDropdown(TMP_Dropdown dropdown, List<string> options, string placeholder)
        {
            dropdown.ClearOptions();
            
            List<string> dropdownOptions = new List<string> { placeholder };
            dropdownOptions.AddRange(options);
            dropdownOptions.Add("Custom...");
            
            dropdown.AddOptions(dropdownOptions);
        }
        
        private void OnPersonalityTraitChanged(int index)
        {
            if (personalityTraitDropdown != null && index > 0)
            {
                if (index == personalityTraitDropdown.options.Count - 1) // Custom option
                {
                    currentTraits.PersonalityTrait = ""; // Will be filled by custom input
                }
                else
                {
                    currentTraits.PersonalityTrait = personalityTraitDropdown.options[index].text;
                }
                UpdateValidation();
                TriggerDetailsCompleted();
            }
        }
        
        private void OnIdealChanged(int index)
        {
            if (idealDropdown != null && index > 0)
            {
                if (index == idealDropdown.options.Count - 1) // Custom option
                {
                    currentTraits.Ideal = ""; // Will be filled by custom input
                }
                else
                {
                    currentTraits.Ideal = idealDropdown.options[index].text;
                }
                UpdateValidation();
                TriggerDetailsCompleted();
            }
        }
        
        private void OnBondChanged(int index)
        {
            if (bondDropdown != null && index > 0)
            {
                if (index == bondDropdown.options.Count - 1) // Custom option
                {
                    currentTraits.Bond = ""; // Will be filled by custom input
                }
                else
                {
                    currentTraits.Bond = bondDropdown.options[index].text;
                }
                UpdateValidation();
                TriggerDetailsCompleted();
            }
        }
        
        private void OnFlawChanged(int index)
        {
            if (flawDropdown != null && index > 0)
            {
                if (index == flawDropdown.options.Count - 1) // Custom option
                {
                    currentTraits.Flaw = ""; // Will be filled by custom input
                }
                else
                {
                    currentTraits.Flaw = flawDropdown.options[index].text;
                }
                UpdateValidation();
                TriggerDetailsCompleted();
            }
        }
        
        private void OnCustomTraitsToggled(bool useCustom)
        {
            if (customTraitPanel != null)
                customTraitPanel.SetActive(useCustom);
            
            if (useCustom)
            {
                // Clear dropdown selections and use custom inputs
                if (personalityTraitDropdown != null)
                    personalityTraitDropdown.value = 0;
                if (idealDropdown != null)
                    idealDropdown.value = 0;
                if (bondDropdown != null)
                    bondDropdown.value = 0;
                if (flawDropdown != null)
                    flawDropdown.value = 0;
                
                UpdateCustomTraits();
            }
        }
        
        private void UpdateCustomTraits()
        {
            if (useCustomTraitsToggle != null && useCustomTraitsToggle.isOn)
            {
                if (customPersonalityTraitInput != null)
                    currentTraits.PersonalityTrait = customPersonalityTraitInput.text;
                if (customIdealInput != null)
                    currentTraits.Ideal = customIdealInput.text;
                if (customBondInput != null)
                    currentTraits.Bond = customBondInput.text;
                if (customFlawInput != null)
                    currentTraits.Flaw = customFlawInput.text;
                
                UpdateValidation();
                TriggerDetailsCompleted();
            }
        }
        
        private void GenerateRandomTraits()
        {
            if (currentBackground == null) return;
            
            // Random selection from background options
            if (currentBackground.PersonalityTraits?.Count > 0)
            {
                int randomIndex = UnityEngine.Random.Range(0, currentBackground.PersonalityTraits.Count);
                currentTraits.PersonalityTrait = currentBackground.PersonalityTraits[randomIndex];
            }
            
            if (currentBackground.Ideals?.Count > 0)
            {
                int randomIndex = UnityEngine.Random.Range(0, currentBackground.Ideals.Count);
                currentTraits.Ideal = currentBackground.Ideals[randomIndex];
            }
            
            if (currentBackground.Bonds?.Count > 0)
            {
                int randomIndex = UnityEngine.Random.Range(0, currentBackground.Bonds.Count);
                currentTraits.Bond = currentBackground.Bonds[randomIndex];
            }
            
            if (currentBackground.Flaws?.Count > 0)
            {
                int randomIndex = UnityEngine.Random.Range(0, currentBackground.Flaws.Count);
                currentTraits.Flaw = currentBackground.Flaws[randomIndex];
            }
            
            UpdateTraitSelections();
            UpdateValidation();
            TriggerDetailsCompleted();
        }
        
        private void UpdateTraitSelections()
        {
            // Update dropdown selections to match current traits
            if (personalityTraitDropdown != null)
                SetDropdownValue(personalityTraitDropdown, currentTraits.PersonalityTrait);
            if (idealDropdown != null)
                SetDropdownValue(idealDropdown, currentTraits.Ideal);
            if (bondDropdown != null)
                SetDropdownValue(bondDropdown, currentTraits.Bond);
            if (flawDropdown != null)
                SetDropdownValue(flawDropdown, currentTraits.Flaw);
        }
        
        private void SetDropdownValue(TMP_Dropdown dropdown, string value)
        {
            if (string.IsNullOrEmpty(value)) return;
            
            for (int i = 0; i < dropdown.options.Count; i++)
            {
                if (dropdown.options[i].text == value)
                {
                    dropdown.value = i;
                    return;
                }
            }
        }
        
        #endregion
        
        #region Validation and Updates
        
        private void OnInputChanged(string value)
        {
            UpdateCharacterSummary();
            UpdateValidation();
            TriggerDetailsCompleted();
        }
        
        private void UpdateCharacterSummary()
        {
            if (characterSummaryText == null) return;
            
            string name = characterNameInput?.text ?? "Unnamed Character";
            string description = characterDescriptionInput?.text ?? "";
            
            string summary = $"Name: {name}";
            if (!string.IsNullOrEmpty(description))
                summary += $"\nDescription: {description}";
            if (!string.IsNullOrEmpty(currentTraits.PersonalityTrait))
                summary += $"\nPersonality: {currentTraits.PersonalityTrait}";
            if (!string.IsNullOrEmpty(currentTraits.Ideal))
                summary += $"\nIdeal: {currentTraits.Ideal}";
            
            characterSummaryText.text = summary;
        }
        
        private void UpdateValidation()
        {
            bool isValid = true;
            string validationMessage = "";
            
            // Check required fields
            if (string.IsNullOrEmpty(characterNameInput?.text))
            {
                isValid = false;
                validationMessage = "Character name is required.";
            }
            else if (string.IsNullOrEmpty(currentTraits.PersonalityTrait))
            {
                isValid = false;
                validationMessage = "Please select or enter a personality trait.";
            }
            else if (string.IsNullOrEmpty(currentTraits.Ideal))
            {
                isValid = false;
                validationMessage = "Please select or enter an ideal.";
            }
            else if (string.IsNullOrEmpty(currentTraits.Bond))
            {
                isValid = false;
                validationMessage = "Please select or enter a bond.";
            }
            else if (string.IsNullOrEmpty(currentTraits.Flaw))
            {
                isValid = false;
                validationMessage = "Please select or enter a flaw.";
            }
            
            if (validationPanel != null)
                validationPanel.SetActive(!isValid);
            if (validationText != null)
                validationText.text = validationMessage;
            
            OnValidationChanged?.Invoke(isValid);
        }
        
        private void TriggerDetailsCompleted()
        {
            if (IsValid())
            {
                OnDetailsCompleted?.Invoke(
                    characterNameInput?.text ?? "",
                    characterDescriptionInput?.text ?? "",
                    characterBackstoryInput?.text ?? "",
                    selectedPortraitUrl ?? "",
                    currentTraits
                );
            }
        }
        
        private bool IsValid()
        {
            return !string.IsNullOrEmpty(characterNameInput?.text) &&
                   !string.IsNullOrEmpty(currentTraits.PersonalityTrait) &&
                   !string.IsNullOrEmpty(currentTraits.Ideal) &&
                   !string.IsNullOrEmpty(currentTraits.Bond) &&
                   !string.IsNullOrEmpty(currentTraits.Flaw);
        }
        
        #endregion
        
        #region Cleanup Methods
        
        private void ClearPortraitOptions()
        {
            foreach (var option in portraitOptions)
            {
                if (option != null)
                    DestroyImmediate(option);
            }
            portraitOptions.Clear();
        }
        
        #endregion
    }
    
    /// <summary>
    /// Individual portrait option component
    /// </summary>
    public class PortraitOption : MonoBehaviour
    {
        [Header("UI Elements")]
        [SerializeField] private Button portraitButton;
        [SerializeField] private Image portraitImage;
        [SerializeField] private Image selectionBorder;
        
        [Header("Selection Styling")]
        [SerializeField] private Color normalColor = Color.white;
        [SerializeField] private Color selectedColor = Color.cyan;
        
        private string portraitPath;
        private System.Action onSelected;
        
        private void Awake()
        {
            if (portraitButton != null)
                portraitButton.onClick.AddListener(() => onSelected?.Invoke());
        }
        
        public void Initialize(string path, System.Action onSelectedCallback)
        {
            portraitPath = path;
            onSelected = onSelectedCallback;
            
            // Load portrait image
            if (portraitImage != null)
            {
                Sprite portraitSprite = Resources.Load<Sprite>(portraitPath);
                if (portraitSprite != null)
                    portraitImage.sprite = portraitSprite;
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
        
        public string GetPortraitPath()
        {
            return portraitPath;
        }
    }
} 