using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using TMPro;
using VDM.UI.Core;
using VDM.Core.Services;
using VDM.Core.DTOs;
using VDM.Infrastructure.Services;

namespace VDM.UI.Systems.Character
{
    /// <summary>
    /// Complete character creation wizard that guides players through the character creation process
    /// </summary>
    public class CharacterCreationWizard : BaseUIPanel
    {
        [Header("Wizard Structure")]
        [SerializeField] private Transform stepsContainer;
        [SerializeField] private List<GameObject> stepPanels = new List<GameObject>();
        
        [Header("Step Indicators")]
        [SerializeField] private Transform stepIndicatorsContainer;
        [SerializeField] private GameObject stepIndicatorPrefab;
        [SerializeField] private List<StepIndicator> stepIndicators = new List<StepIndicator>();
        
        [Header("Navigation")]
        [SerializeField] private Button previousButton;
        [SerializeField] private Button nextButton;
        [SerializeField] private Button cancelButton;
        [SerializeField] private TextMeshProUGUI currentStepText;
        [SerializeField] private Slider progressSlider;
        
        [Header("Step Panels")]
        [SerializeField] private RaceSelectionPanel raceSelectionPanel;
        [SerializeField] private AttributeAllocationPanel attributeAllocationPanel;
        [SerializeField] private BackgroundSelectionPanel backgroundSelectionPanel;
        [SerializeField] private CharacterDetailsPanel characterDetailsPanel;
        [SerializeField] private CharacterReviewPanel characterReviewPanel;
        
        [Header("Validation")]
        [SerializeField] private GameObject validationErrorPanel;
        [SerializeField] private TextMeshProUGUI validationErrorText;
        [SerializeField] private Button validationOkButton;
        
        [Header("Loading")]
        [SerializeField] private GameObject loadingPanel;
        [SerializeField] private TextMeshProUGUI loadingText;
        [SerializeField] private Slider loadingProgressBar;
        
        // Services
        private CharacterCreationService characterCreationService;
        
        // Current creation data
        private CharacterCreationRequestDTO currentRequest;
        private CharacterCreationProgressDTO progress;
        private List<RaceDTO> availableRaces;
        private List<BackgroundDTO> availableBackgrounds;
        private PointBuyConfigDTO pointBuyConfig;
        private StandardArrayConfigDTO standardArrayConfig;
        
        // Current step management
        private int currentStepIndex = 0;
        private readonly string[] stepNames = {
            "Race Selection",
            "Attribute Allocation", 
            "Background Selection",
            "Character Details",
            "Review & Create"
        };
        
        // Events
        public event Action<CharacterDTO> OnCharacterCreated;
        public event Action OnCharacterCreationCancelled;
        public event Action<int> OnStepChanged;
        
        protected override void Awake()
        {
            base.Awake();
            
            // Initialize character creation request
            currentRequest = new CharacterCreationRequestDTO();
            progress = new CharacterCreationProgressDTO();
            
            // Find or get character creation service
            characterCreationService = FindObjectOfType<CharacterCreationService>();
            if (characterCreationService == null)
            {
                Debug.LogError("CharacterCreationService not found! Please ensure it exists in the scene.");
            }
        }
        
        private void Start()
        {
            SetupUI();
            SetupEventListeners();
            LoadInitialData();
        }
        
        private void SetupUI()
        {
            // Setup navigation buttons
            if (previousButton != null)
                previousButton.onClick.AddListener(GoToPreviousStep);
            if (nextButton != null)
                nextButton.onClick.AddListener(GoToNextStep);
            if (cancelButton != null)
                cancelButton.onClick.AddListener(CancelCharacterCreation);
            if (validationOkButton != null)
                validationOkButton.onClick.AddListener(HideValidationError);
            
            // Initialize step indicators
            SetupStepIndicators();
            
            // Show first step
            ShowStep(0);
            UpdateNavigationButtons();
        }
        
        private void SetupEventListeners()
        {
            // Subscribe to step panel events
            if (raceSelectionPanel != null)
            {
                raceSelectionPanel.OnRaceSelected += OnRaceSelected;
                raceSelectionPanel.OnValidationChanged += OnStepValidationChanged;
            }
            
            if (attributeAllocationPanel != null)
            {
                attributeAllocationPanel.OnAttributesAllocated += OnAttributesAllocated;
                attributeAllocationPanel.OnValidationChanged += OnStepValidationChanged;
            }
            
            if (backgroundSelectionPanel != null)
            {
                backgroundSelectionPanel.OnBackgroundSelected += OnBackgroundSelected;
                backgroundSelectionPanel.OnValidationChanged += OnStepValidationChanged;
            }
            
            if (characterDetailsPanel != null)
            {
                characterDetailsPanel.OnDetailsCompleted += OnDetailsCompleted;
                characterDetailsPanel.OnValidationChanged += OnStepValidationChanged;
            }
            
            if (characterReviewPanel != null)
            {
                characterReviewPanel.OnCreateCharacter += OnCreateCharacter;
                characterReviewPanel.OnValidationChanged += OnStepValidationChanged;
            }
            
            // Subscribe to service events
            if (characterCreationService != null)
            {
                characterCreationService.OnCharacterCreated += OnCharacterCreationCompleted;
                characterCreationService.OnError += OnCharacterCreationError;
            }
        }
        
        private async void LoadInitialData()
        {
            ShowLoading("Loading character creation data...");
            
            try
            {
                if (characterCreationService != null)
                {
                    // Load races and backgrounds
                    var racesResponse = await characterCreationService.GetAvailableRacesAsync();
                    var backgroundsResponse = await characterCreationService.GetAvailableBackgroundsAsync();
                    var pointBuyResponse = await characterCreationService.GetPointBuyConfigAsync();
                    var standardArrayResponse = await characterCreationService.GetStandardArrayConfigAsync();
                    
                    availableRaces = racesResponse.Races;
                    availableBackgrounds = backgroundsResponse.Backgrounds;
                    pointBuyConfig = pointBuyResponse;
                    standardArrayConfig = standardArrayResponse;
                    
                    // Initialize step panels with data
                    InitializeStepPanels();
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to load character creation data: {ex.Message}");
                ShowValidationError($"Failed to load character creation data: {ex.Message}");
            }
            finally
            {
                HideLoading();
            }
        }
        
        private void InitializeStepPanels()
        {
            // Initialize race selection
            if (raceSelectionPanel != null && availableRaces != null)
            {
                raceSelectionPanel.Initialize(availableRaces);
            }
            
            // Initialize attribute allocation
            if (attributeAllocationPanel != null && pointBuyConfig != null && standardArrayConfig != null)
            {
                attributeAllocationPanel.Initialize(pointBuyConfig, standardArrayConfig);
            }
            
            // Initialize background selection
            if (backgroundSelectionPanel != null && availableBackgrounds != null)
            {
                backgroundSelectionPanel.Initialize(availableBackgrounds);
            }
            
            // Initialize character details
            if (characterDetailsPanel != null)
            {
                characterDetailsPanel.Initialize();
            }
            
            // Initialize review panel
            if (characterReviewPanel != null)
            {
                characterReviewPanel.Initialize();
            }
        }
        
        private void SetupStepIndicators()
        {
            if (stepIndicatorsContainer == null || stepIndicatorPrefab == null)
                return;
            
            // Clear existing indicators
            foreach (Transform child in stepIndicatorsContainer)
            {
                DestroyImmediate(child.gameObject);
            }
            stepIndicators.Clear();
            
            // Create step indicators
            for (int i = 0; i < stepNames.Length; i++)
            {
                GameObject indicatorObj = Instantiate(stepIndicatorPrefab, stepIndicatorsContainer);
                StepIndicator indicator = indicatorObj.GetComponent<StepIndicator>();
                
                if (indicator != null)
                {
                    indicator.Initialize(i + 1, stepNames[i]);
                    stepIndicators.Add(indicator);
                }
            }
        }
        
        #region Step Navigation
        
        public void ShowStep(int stepIndex)
        {
            if (stepIndex < 0 || stepIndex >= stepPanels.Count)
                return;
            
            // Hide all step panels
            foreach (var panel in stepPanels)
            {
                if (panel != null)
                    panel.SetActive(false);
            }
            
            // Show current step panel
            if (stepPanels[stepIndex] != null)
                stepPanels[stepIndex].SetActive(true);
            
            // Update step indicator
            UpdateStepIndicators(stepIndex);
            
            // Update current step info
            currentStepIndex = stepIndex;
            progress.CurrentStep = stepIndex;
            
            if (currentStepText != null)
                currentStepText.text = stepNames[stepIndex];
            
            if (progressSlider != null)
                progressSlider.value = (float)stepIndex / (stepNames.Length - 1);
            
            // Update navigation buttons
            UpdateNavigationButtons();
            
            // Notify step change
            OnStepChanged?.Invoke(stepIndex);
            
            // Update step panel with current data
            UpdateCurrentStepPanel();
        }
        
        private void UpdateCurrentStepPanel()
        {
            switch (currentStepIndex)
            {
                case 0: // Race Selection
                    if (raceSelectionPanel != null)
                        raceSelectionPanel.UpdateDisplay(currentRequest);
                    break;
                    
                case 1: // Attribute Allocation
                    if (attributeAllocationPanel != null)
                        attributeAllocationPanel.UpdateDisplay(currentRequest);
                    break;
                    
                case 2: // Background Selection
                    if (backgroundSelectionPanel != null)
                        backgroundSelectionPanel.UpdateDisplay(currentRequest);
                    break;
                    
                case 3: // Character Details
                    if (characterDetailsPanel != null)
                        characterDetailsPanel.UpdateDisplay(currentRequest);
                    break;
                    
                case 4: // Review & Create
                    if (characterReviewPanel != null)
                        characterReviewPanel.UpdateDisplay(currentRequest, availableRaces, availableBackgrounds);
                    break;
            }
        }
        
        private void UpdateStepIndicators(int currentStep)
        {
            for (int i = 0; i < stepIndicators.Count; i++)
            {
                if (stepIndicators[i] != null)
                {
                    if (i < currentStep)
                        stepIndicators[i].SetState(StepIndicator.StepState.Completed);
                    else if (i == currentStep)
                        stepIndicators[i].SetState(StepIndicator.StepState.Current);
                    else
                        stepIndicators[i].SetState(StepIndicator.StepState.Pending);
                }
            }
        }
        
        private void UpdateNavigationButtons()
        {
            if (previousButton != null)
                previousButton.interactable = currentStepIndex > 0;
            
            if (nextButton != null)
            {
                bool canProceed = CanProceedToNextStep();
                nextButton.interactable = canProceed && currentStepIndex < stepNames.Length - 1;
                
                // Update button text
                var buttonText = nextButton.GetComponentInChildren<TextMeshProUGUI>();
                if (buttonText != null)
                {
                    if (currentStepIndex == stepNames.Length - 1)
                        buttonText.text = "Create Character";
                    else
                        buttonText.text = "Next";
                }
            }
        }
        
        private bool CanProceedToNextStep()
        {
            switch (currentStepIndex)
            {
                case 0: return progress.RaceSelected;
                case 1: return progress.AttributesAllocated;
                case 2: return progress.BackgroundSelected;
                case 3: return progress.DetailsCompleted;
                case 4: return progress.ReadyToCreate;
                default: return false;
            }
        }
        
        private void GoToPreviousStep()
        {
            if (currentStepIndex > 0)
            {
                ShowStep(currentStepIndex - 1);
            }
        }
        
        private void GoToNextStep()
        {
            if (currentStepIndex < stepNames.Length - 1 && CanProceedToNextStep())
            {
                ShowStep(currentStepIndex + 1);
            }
            else if (currentStepIndex == stepNames.Length - 1)
            {
                // Create character
                CreateCharacter();
            }
        }
        
        #endregion
        
        #region Step Event Handlers
        
        private void OnRaceSelected(RaceDTO selectedRace)
        {
            currentRequest.RaceId = selectedRace.Id;
            progress.RaceSelected = true;
            
            // Apply racial attribute bonuses to the attributes if they exist
            if (currentRequest.Attributes != null && selectedRace.AttributeBonuses != null)
            {
                currentRequest.Attributes = selectedRace.AttributeBonuses.ApplyTo(currentRequest.Attributes);
            }
            
            UpdateNavigationButtons();
            Debug.Log($"Race selected: {selectedRace.Name}");
        }
        
        private void OnAttributesAllocated(AttributesDTO attributes)
        {
            currentRequest.Attributes = attributes;
            progress.AttributesAllocated = true;
            UpdateNavigationButtons();
            Debug.Log("Attributes allocated successfully");
        }
        
        private void OnBackgroundSelected(BackgroundDTO selectedBackground)
        {
            currentRequest.BackgroundId = selectedBackground.Id;
            progress.BackgroundSelected = true;
            UpdateNavigationButtons();
            Debug.Log($"Background selected: {selectedBackground.Name}");
        }
        
        private void OnDetailsCompleted(string name, string description, string backstory, string portraitUrl, TraitSelectionDTO traits)
        {
            currentRequest.Name = name;
            currentRequest.Description = description;
            currentRequest.Backstory = backstory;
            currentRequest.PortraitUrl = portraitUrl;
            
            // Handle personality traits
            if (traits != null)
            {
                currentRequest.PersonalityTraits = new Dictionary<string, string>
                {
                    { "PersonalityTrait", traits.PersonalityTrait },
                    { "Ideal", traits.Ideal },
                    { "Bond", traits.Bond },
                    { "Flaw", traits.Flaw }
                };
            }
            
            progress.DetailsCompleted = true;
            progress.ReadyToCreate = true;
            UpdateNavigationButtons();
            Debug.Log("Character details completed");
        }
        
        private void OnStepValidationChanged(bool isValid)
        {
            UpdateNavigationButtons();
        }
        
        private async void OnCreateCharacter()
        {
            await CreateCharacter();
        }
        
        #endregion
        
        #region Character Creation
        
        private async System.Threading.Tasks.Task CreateCharacter()
        {
            if (characterCreationService == null)
            {
                ShowValidationError("Character creation service not available");
                return;
            }
            
            ShowLoading("Creating your character...");
            
            try
            {
                // Set player ID if not already set
                if (string.IsNullOrEmpty(currentRequest.PlayerId))
                {
                    currentRequest.PlayerId = "player_001"; // This should come from authentication system
                }
                
                // Validate character before creation
                var validationResponse = await characterCreationService.ValidateCharacterAsync(currentRequest);
                
                if (!validationResponse.IsValid)
                {
                    ShowValidationError($"Character validation failed:\n{string.Join("\n", validationResponse.Errors)}");
                    return;
                }
                
                // Create character
                var creationResponse = await characterCreationService.CreateCharacterAsync(currentRequest);
                
                if (creationResponse.Success)
                {
                    OnCharacterCreated?.Invoke(creationResponse.Character);
                    Hide();
                }
                else
                {
                    ShowValidationError($"Character creation failed:\n{creationResponse.Message}");
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Character creation error: {ex.Message}");
                ShowValidationError($"Character creation failed: {ex.Message}");
            }
            finally
            {
                HideLoading();
            }
        }
        
        private void OnCharacterCreationCompleted(CharacterDTO character)
        {
            OnCharacterCreated?.Invoke(character);
            Hide();
        }
        
        private void OnCharacterCreationError(string error)
        {
            ShowValidationError($"Character creation error: {error}");
        }
        
        #endregion
        
        #region UI Controls
        
        private void CancelCharacterCreation()
        {
            OnCharacterCreationCancelled?.Invoke();
            Hide();
        }
        
        private void ShowValidationError(string message)
        {
            if (validationErrorPanel != null)
                validationErrorPanel.SetActive(true);
            if (validationErrorText != null)
                validationErrorText.text = message;
        }
        
        private void HideValidationError()
        {
            if (validationErrorPanel != null)
                validationErrorPanel.SetActive(false);
        }
        
        private void ShowLoading(string message)
        {
            if (loadingPanel != null)
                loadingPanel.SetActive(true);
            if (loadingText != null)
                loadingText.text = message;
        }
        
        private void HideLoading()
        {
            if (loadingPanel != null)
                loadingPanel.SetActive(false);
        }
        
        #endregion
        
        #region Public Interface
        
        /// <summary>
        /// Start a new character creation process
        /// </summary>
        public void StartCharacterCreation(string playerId = null)
        {
            // Reset creation data
            currentRequest = new CharacterCreationRequestDTO();
            progress = new CharacterCreationProgressDTO();
            
            if (!string.IsNullOrEmpty(playerId))
                currentRequest.PlayerId = playerId;
            
            // Show first step
            ShowStep(0);
            Show();
        }
        
        /// <summary>
        /// Get current character creation progress
        /// </summary>
        public CharacterCreationProgressDTO GetProgress()
        {
            return progress;
        }
        
        /// <summary>
        /// Get current character creation request data
        /// </summary>
        public CharacterCreationRequestDTO GetCurrentRequest()
        {
            return currentRequest;
        }
        
        #endregion
        
        private void OnDestroy()
        {
            // Unsubscribe from events
            if (characterCreationService != null)
            {
                characterCreationService.OnCharacterCreated -= OnCharacterCreationCompleted;
                characterCreationService.OnError -= OnCharacterCreationError;
            }
        }
    }
}

/// <summary>
/// Step indicator component for the character creation wizard
/// </summary>
[System.Serializable]
public class StepIndicator : MonoBehaviour
{
    [Header("UI Elements")]
    [SerializeField] private TextMeshProUGUI stepNumberText;
    [SerializeField] private TextMeshProUGUI stepNameText;
    [SerializeField] private Image stepIcon;
    [SerializeField] private Image backgroundImage;
    
    [Header("State Colors")]
    [SerializeField] private Color pendingColor = Color.gray;
    [SerializeField] private Color currentColor = Color.blue;
    [SerializeField] private Color completedColor = Color.green;
    
    public enum StepState
    {
        Pending,
        Current,
        Completed
    }
    
    public void Initialize(int stepNumber, string stepName)
    {
        if (stepNumberText != null)
            stepNumberText.text = stepNumber.ToString();
        if (stepNameText != null)
            stepNameText.text = stepName;
        
        SetState(StepState.Pending);
    }
    
    public void SetState(StepState state)
    {
        Color stateColor = pendingColor;
        
        switch (state)
        {
            case StepState.Pending:
                stateColor = pendingColor;
                break;
            case StepState.Current:
                stateColor = currentColor;
                break;
            case StepState.Completed:
                stateColor = completedColor;
                break;
        }
        
        if (backgroundImage != null)
            backgroundImage.color = stateColor;
        if (stepIcon != null)
            stepIcon.color = stateColor;
    }
} 