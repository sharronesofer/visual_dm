using System.Collections.Generic;
using System.Linq;
using System;
using TMPro;
using UnityEngine.UI;
using UnityEngine;
using VDM.Runtime.Core.UI;
using VDM.Runtime.Arc.Models;
using VDM.Runtime.Arc.Services;


namespace VDM.Runtime.Arc.UI
{
    /// <summary>
    /// Comprehensive Arc Visualization UI with timeline, progression tracking, and narrative flow
    /// </summary>
    public class ArcVisualizationUI : MonoBehaviour
    {
        [Header("UI References")]
        [SerializeField] private GameObject arcVisualizationPanel;
        [SerializeField] private Transform arcListContainer;
        [SerializeField] private GameObject arcItemPrefab;
        [SerializeField] private ScrollRect arcScrollRect;
        
        [Header("Arc Details")]
        [SerializeField] private GameObject arcDetailsPanel;
        [SerializeField] private TextMeshProUGUI arcTitleText;
        [SerializeField] private TextMeshProUGUI arcDescriptionText;
        [SerializeField] private TextMeshProUGUI arcTypeText;
        [SerializeField] private TextMeshProUGUI arcStatusText;
        [SerializeField] private TextMeshProUGUI arcPriorityText;
        [SerializeField] private TextMeshProUGUI arcProgressText;
        [SerializeField] private Slider arcProgressSlider;
        
        [Header("Arc Timeline")]
        [SerializeField] private GameObject timelinePanel;
        [SerializeField] private Transform timelineContainer;
        [SerializeField] private GameObject timelineStepPrefab;
        [SerializeField] private ScrollRect timelineScrollRect;
        [SerializeField] private Button timelineToggleButton;
        
        [Header("Step Visualization")]
        [SerializeField] private Transform stepsContainer;
        [SerializeField] private GameObject stepVisualizationPrefab;
        [SerializeField] private Button stepViewToggleButton;
        
        [Header("Filtering and Controls")]
        [SerializeField] private TMP_InputField searchInputField;
        [SerializeField] private TMP_Dropdown typeFilterDropdown;
        [SerializeField] private TMP_Dropdown statusFilterDropdown;
        [SerializeField] private TMP_Dropdown priorityFilterDropdown;
        [SerializeField] private Button clearFiltersButton;
        [SerializeField] private Button refreshButton;
        
        [Header("Arc Analytics")]
        [SerializeField] private GameObject analyticsPanel;
        [SerializeField] private TextMeshProUGUI totalArcsText;
        [SerializeField] private TextMeshProUGUI activeArcsText;
        [SerializeField] private TextMeshProUGUI completedArcsText;
        [SerializeField] private TextMeshProUGUI failedArcsText;
        [SerializeField] private Button analyticsToggleButton;
        
        [Header("Arc Management")]
        [SerializeField] private Button createArcButton;
        [SerializeField] private Button generateArcButton;
        [SerializeField] private Button editArcButton;
        [SerializeField] private Button deleteArcButton;
        
        [Header("Integration Display")]
        [SerializeField] private GameObject integrationPanel;
        [SerializeField] private Transform questLinksContainer;
        [SerializeField] private Transform characterLinksContainer;
        [SerializeField] private GameObject linkItemPrefab;
        
        // Services
        private ArcService arcService;
        private ArcWebSocketHandler webSocketHandler;
        
        // Data
        private List<ArcModel> allArcs = new List<ArcModel>();
        private List<ArcModel> filteredArcs = new List<ArcModel>();
        private ArcModel selectedArc;
        private ArcAnalyticsModel arcAnalytics;
        
        // UI State
        private Dictionary<string, GameObject> arcItemInstances = new Dictionary<string, GameObject>();
        private Dictionary<int, GameObject> stepInstances = new Dictionary<int, GameObject>();
        private bool timelineViewActive = false;
        private bool analyticsViewActive = false;
        private bool isInitialized = false;
        
        // Events
        public event Action<ArcModel> OnArcSelected;
        public event Action<ArcModel> OnArcCreated;
        public event Action<ArcModel> OnArcUpdated;
        public event Action<ArcModel> OnArcDeleted;
        public event Action<ArcModel, ArcStepModel> OnStepSelected;
        
        #region Unity Lifecycle
        
        private void Start()
        {
            InitializeComponent();
        }
        
        private void OnDestroy()
        {
            if (webSocketHandler != null)
            {
                UnsubscribeFromEvents();
            }
        }
        
        #endregion
        
        #region Initialization
        
        private async void InitializeComponent()
        {
            try
            {
                // Initialize services
                arcService = new ArcService();
                webSocketHandler = new ArcWebSocketHandler();
                
                // Setup UI events
                SetupUIEvents();
                
                // Setup filter dropdowns
                SetupFilterDropdowns();
                
                // Subscribe to WebSocket events
                SubscribeToEvents();
                
                // Initial data load
                await LoadArcs();
                
                // Initialize UI panels
                SetupUIPanels();
                
                isInitialized = true;
                Debug.Log("Arc Visualization UI initialized successfully");
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to initialize Arc Visualization UI: {ex.Message}");
            }
        }
        
        private void SetupUIEvents()
        {
            // Search and filtering
            if (searchInputField != null)
                searchInputField.onValueChanged.AddListener(OnSearchChanged);
            
            if (typeFilterDropdown != null)
                typeFilterDropdown.onValueChanged.AddListener(OnTypeFilterChanged);
            
            if (statusFilterDropdown != null)
                statusFilterDropdown.onValueChanged.AddListener(OnStatusFilterChanged);
            
            if (priorityFilterDropdown != null)
                priorityFilterDropdown.onValueChanged.AddListener(OnPriorityFilterChanged);
            
            if (clearFiltersButton != null)
                clearFiltersButton.onClick.AddListener(ClearFilters);
            
            if (refreshButton != null)
                refreshButton.onClick.AddListener(async () => await LoadArcs());
            
            // View toggles
            if (timelineToggleButton != null)
                timelineToggleButton.onClick.AddListener(ToggleTimelineView);
            
            if (stepViewToggleButton != null)
                stepViewToggleButton.onClick.AddListener(ToggleStepView);
            
            if (analyticsToggleButton != null)
                analyticsToggleButton.onClick.AddListener(ToggleAnalyticsView);
            
            // Arc management
            if (createArcButton != null)
                createArcButton.onClick.AddListener(ShowCreateArcDialog);
            
            if (generateArcButton != null)
                generateArcButton.onClick.AddListener(ShowGenerateArcDialog);
            
            if (editArcButton != null)
                editArcButton.onClick.AddListener(EditSelectedArc);
            
            if (deleteArcButton != null)
                deleteArcButton.onClick.AddListener(DeleteSelectedArc);
        }
        
        private void SetupFilterDropdowns()
        {
            // Type filter
            if (typeFilterDropdown != null)
            {
                typeFilterDropdown.options.Clear();
                typeFilterDropdown.options.Add(new TMP_Dropdown.OptionData("All Types"));
                typeFilterDropdown.options.Add(new TMP_Dropdown.OptionData("Global"));
                typeFilterDropdown.options.Add(new TMP_Dropdown.OptionData("Regional"));
                typeFilterDropdown.options.Add(new TMP_Dropdown.OptionData("Character"));
                typeFilterDropdown.options.Add(new TMP_Dropdown.OptionData("NPC"));
                typeFilterDropdown.value = 0;
            }
            
            // Status filter
            if (statusFilterDropdown != null)
            {
                statusFilterDropdown.options.Clear();
                statusFilterDropdown.options.Add(new TMP_Dropdown.OptionData("All Status"));
                statusFilterDropdown.options.Add(new TMP_Dropdown.OptionData("Pending"));
                statusFilterDropdown.options.Add(new TMP_Dropdown.OptionData("Active"));
                statusFilterDropdown.options.Add(new TMP_Dropdown.OptionData("Stalled"));
                statusFilterDropdown.options.Add(new TMP_Dropdown.OptionData("Completed"));
                statusFilterDropdown.options.Add(new TMP_Dropdown.OptionData("Failed"));
                statusFilterDropdown.options.Add(new TMP_Dropdown.OptionData("Abandoned"));
                statusFilterDropdown.value = 0;
            }
            
            // Priority filter
            if (priorityFilterDropdown != null)
            {
                priorityFilterDropdown.options.Clear();
                priorityFilterDropdown.options.Add(new TMP_Dropdown.OptionData("All Priorities"));
                priorityFilterDropdown.options.Add(new TMP_Dropdown.OptionData("Low"));
                priorityFilterDropdown.options.Add(new TMP_Dropdown.OptionData("Medium"));
                priorityFilterDropdown.options.Add(new TMP_Dropdown.OptionData("High"));
                priorityFilterDropdown.options.Add(new TMP_Dropdown.OptionData("Urgent"));
                priorityFilterDropdown.value = 0;
            }
        }
        
        private void SetupUIPanels()
        {
            if (timelinePanel != null)
                timelinePanel.SetActive(false);
            
            if (analyticsPanel != null)
                analyticsPanel.SetActive(false);
        }
        
        #endregion
        
        #region Data Loading
        
        private async System.Threading.Tasks.Task LoadArcs()
        {
            try
            {
                var arcs = await arcService.GetArcsAsync();
                
                allArcs.Clear();
                allArcs.AddRange(arcs);
                
                ApplyFilters();
                UpdateArcStats();
                
                Debug.Log($"Loaded {allArcs.Count} arcs");
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to load arcs: {ex.Message}");
            }
        }
        
        private async System.Threading.Tasks.Task LoadArcAnalytics(string arcId)
        {
            try
            {
                arcAnalytics = await arcService.GetAnalyticsAsync(arcId);
                UpdateAnalyticsDisplay();
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to load arc analytics: {ex.Message}");
            }
        }
        
        #endregion
        
        #region Filtering and Search
        
        private void ApplyFilters()
        {
            filteredArcs.Clear();
            
            var searchTerm = searchInputField?.text?.ToLower() ?? "";
            var typeFilter = GetSelectedTypeFilter();
            var statusFilter = GetSelectedStatusFilter();
            var priorityFilter = GetSelectedPriorityFilter();
            
            foreach (var arc in allArcs)
            {
                // Search filter
                if (!string.IsNullOrEmpty(searchTerm))
                {
                    if (!arc.Title.ToLower().Contains(searchTerm) && 
                        !arc.Description.ToLower().Contains(searchTerm))
                        continue;
                }
                
                // Type filter
                if (typeFilter.HasValue && arc.ArcType != typeFilter.Value)
                    continue;
                
                // Status filter
                if (statusFilter.HasValue && arc.Status != statusFilter.Value)
                    continue;
                
                // Priority filter
                if (priorityFilter.HasValue && arc.Priority != priorityFilter.Value)
                    continue;
                
                filteredArcs.Add(arc);
            }
            
            // Sort by priority and creation date
            filteredArcs = filteredArcs.OrderBy(a => GetPriorityOrder(a.Priority))
                                     .ThenByDescending(a => a.CreatedAt)
                                     .ToList();
            
            UpdateArcList();
        }
        
        private ArcType? GetSelectedTypeFilter()
        {
            if (typeFilterDropdown == null || typeFilterDropdown.value == 0)
                return null;
            
            var selectedText = typeFilterDropdown.options[typeFilterDropdown.value].text;
            return Enum.TryParse<ArcType>(selectedText, true, out var result) ? result : null;
        }
        
        private ArcStatus? GetSelectedStatusFilter()
        {
            if (statusFilterDropdown == null || statusFilterDropdown.value == 0)
                return null;
            
            var selectedText = statusFilterDropdown.options[statusFilterDropdown.value].text;
            return Enum.TryParse<ArcStatus>(selectedText, true, out var result) ? result : null;
        }
        
        private ArcPriority? GetSelectedPriorityFilter()
        {
            if (priorityFilterDropdown == null || priorityFilterDropdown.value == 0)
                return null;
            
            var selectedText = priorityFilterDropdown.options[priorityFilterDropdown.value].text;
            return Enum.TryParse<ArcPriority>(selectedText, true, out var result) ? result : null;
        }
        
        private int GetPriorityOrder(ArcPriority priority)
        {
            return priority switch
            {
                ArcPriority.Urgent => 0,
                ArcPriority.High => 1,
                ArcPriority.Medium => 2,
                ArcPriority.Low => 3,
                _ => 4
            };
        }
        
        #endregion
        
        #region UI Updates
        
        private void UpdateArcList()
        {
            if (arcListContainer == null || arcItemPrefab == null)
                return;
            
            // Clear existing items
            foreach (var item in arcItemInstances.Values)
            {
                if (item != null)
                    Destroy(item);
            }
            arcItemInstances.Clear();
            
            // Create new items
            foreach (var arc in filteredArcs)
            {
                CreateArcListItem(arc);
            }
            
            // Update scroll rect
            if (arcScrollRect != null)
            {
                Canvas.ForceUpdateCanvases();
                arcScrollRect.verticalNormalizedPosition = 1f;
            }
        }
        
        private void CreateArcListItem(ArcModel arc)
        {
            var itemObject = Instantiate(arcItemPrefab, arcListContainer);
            arcItemInstances[arc.Id] = itemObject;
            
            var arcItem = itemObject.GetComponent<ArcListItem>();
            if (arcItem != null)
            {
                arcItem.Initialize(arc);
                arcItem.OnSelected += () => SelectArc(arc);
            }
            else
            {
                // Fallback manual setup
                SetupArcItemManually(itemObject, arc);
            }
        }
        
        private void SetupArcItemManually(GameObject itemObject, ArcModel arc)
        {
            var titleText = itemObject.GetComponentInChildren<TextMeshProUGUI>();
            if (titleText != null)
                titleText.text = arc.Title;
            
            var button = itemObject.GetComponent<Button>();
            if (button != null)
                button.onClick.AddListener(() => SelectArc(arc));
        }
        
        private void UpdateArcDetails()
        {
            if (arcDetailsPanel == null || selectedArc == null)
                return;
            
            arcDetailsPanel.SetActive(true);
            
            // Update basic info
            if (arcTitleText != null)
                arcTitleText.text = selectedArc.Title;
            
            if (arcDescriptionText != null)
                arcDescriptionText.text = selectedArc.Description;
            
            if (arcTypeText != null)
                arcTypeText.text = $"Type: {selectedArc.ArcType}";
            
            if (arcStatusText != null)
                arcStatusText.text = $"Status: {selectedArc.Status}";
            
            if (arcPriorityText != null)
                arcPriorityText.text = $"Priority: {selectedArc.Priority}";
            
            if (arcProgressText != null)
                arcProgressText.text = $"Progress: {selectedArc.CompletionPercentage:F1}%";
            
            if (arcProgressSlider != null)
                arcProgressSlider.value = selectedArc.CompletionPercentage / 100f;
            
            // Update steps visualization
            UpdateStepVisualization();
            
            // Update timeline if active
            if (timelineViewActive)
                UpdateTimelineDisplay();
            
            // Update integration display
            UpdateIntegrationDisplay();
            
            // Update management buttons
            UpdateManagementButtons();
        }
        
        private void UpdateStepVisualization()
        {
            if (stepsContainer == null || stepVisualizationPrefab == null || selectedArc?.Steps == null)
                return;
            
            // Clear existing steps
            foreach (var step in stepInstances.Values)
            {
                if (step != null)
                    Destroy(step);
            }
            stepInstances.Clear();
            
            // Create step visualizations
            foreach (var step in selectedArc.Steps.OrderBy(s => s.OrderIndex))
            {
                CreateStepVisualization(step);
            }
        }
        
        private void CreateStepVisualization(ArcStepModel step)
        {
            var stepObject = Instantiate(stepVisualizationPrefab, stepsContainer);
            stepInstances[step.Id] = stepObject;
            
            var stepViz = stepObject.GetComponent<ArcStepVisualization>();
            if (stepViz != null)
            {
                stepViz.Initialize(step);
                stepViz.OnStepSelected += () => OnStepSelected?.Invoke(selectedArc, step);
            }
            else
            {
                // Fallback manual setup
                SetupStepVisualizationManually(stepObject, step);
            }
        }
        
        private void SetupStepVisualizationManually(GameObject stepObject, ArcStepModel step)
        {
            var titleText = stepObject.GetComponentInChildren<TextMeshProUGUI>();
            if (titleText != null)
            {
                var statusIcon = GetStepStatusIcon(step.Status);
                titleText.text = $"{statusIcon} {step.Title}";
            }
            
            var button = stepObject.GetComponent<Button>();
            if (button != null)
                button.onClick.AddListener(() => OnStepSelected?.Invoke(selectedArc, step));
        }
        
        private string GetStepStatusIcon(ArcStepStatus status)
        {
            return status switch
            {
                ArcStepStatus.Completed => "✓",
                ArcStepStatus.Active => "▶",
                ArcStepStatus.Available => "○",
                ArcStepStatus.Failed => "✗",
                ArcStepStatus.Skipped => "→",
                _ => "○"
            };
        }
        
        private void UpdateTimelineDisplay()
        {
            if (!timelineViewActive || timelineContainer == null || timelineStepPrefab == null || selectedArc?.Steps == null)
                return;
            
            // Clear existing timeline items
            foreach (Transform child in timelineContainer)
            {
                Destroy(child.gameObject);
            }
            
            // Create timeline items
            var sortedSteps = selectedArc.Steps.OrderBy(s => s.OrderIndex).ToList();
            for (int i = 0; i < sortedSteps.Count; i++)
            {
                var step = sortedSteps[i];
                var timelineItem = Instantiate(timelineStepPrefab, timelineContainer);
                
                var timelineViz = timelineItem.GetComponent<ArcTimelineItem>();
                if (timelineViz != null)
                {
                    timelineViz.Initialize(step, i, sortedSteps.Count);
                    timelineViz.OnStepClicked += () => OnStepSelected?.Invoke(selectedArc, step);
                }
            }
        }
        
        private void UpdateIntegrationDisplay()
        {
            if (integrationPanel == null || selectedArc == null)
                return;
            
            // Update quest links
            UpdateQuestLinks();
            
            // Update character links
            UpdateCharacterLinks();
        }
        
        private void UpdateQuestLinks()
        {
            if (questLinksContainer == null || linkItemPrefab == null)
                return;
            
            // Clear existing links
            foreach (Transform child in questLinksContainer)
            {
                Destroy(child.gameObject);
            }
            
            // Create quest link items
            if (selectedArc.QuestIds != null)
            {
                foreach (var questId in selectedArc.QuestIds)
                {
                    var linkItem = Instantiate(linkItemPrefab, questLinksContainer);
                    var linkText = linkItem.GetComponentInChildren<TextMeshProUGUI>();
                    if (linkText != null)
                        linkText.text = $"Quest: {questId}";
                }
            }
        }
        
        private void UpdateCharacterLinks()
        {
            if (characterLinksContainer == null || linkItemPrefab == null)
                return;
            
            // Clear existing links
            foreach (Transform child in characterLinksContainer)
            {
                Destroy(child.gameObject);
            }
            
            // Create character link item
            if (!string.IsNullOrEmpty(selectedArc.CharacterId))
            {
                var linkItem = Instantiate(linkItemPrefab, characterLinksContainer);
                var linkText = linkItem.GetComponentInChildren<TextMeshProUGUI>();
                if (linkText != null)
                    linkText.text = $"Character: {selectedArc.CharacterId}";
            }
        }
        
        private void UpdateManagementButtons()
        {
            var hasSelection = selectedArc != null;
            
            if (editArcButton != null)
                editArcButton.interactable = hasSelection;
            
            if (deleteArcButton != null)
                deleteArcButton.interactable = hasSelection && selectedArc.Status != ArcStatus.Completed;
        }
        
        private void UpdateArcStats()
        {
            var total = allArcs.Count;
            var active = allArcs.Count(a => a.Status == ArcStatus.Active);
            var completed = allArcs.Count(a => a.Status == ArcStatus.Completed);
            var failed = allArcs.Count(a => a.Status == ArcStatus.Failed);
            
            if (totalArcsText != null)
                totalArcsText.text = $"Total: {total}";
            
            if (activeArcsText != null)
                activeArcsText.text = $"Active: {active}";
            
            if (completedArcsText != null)
                completedArcsText.text = $"Completed: {completed}";
            
            if (failedArcsText != null)
                failedArcsText.text = $"Failed: {failed}";
        }
        
        private void UpdateAnalyticsDisplay()
        {
            if (!analyticsViewActive || arcAnalytics == null)
                return;
            
            // Implementation for analytics display would go here
            // This could include charts, graphs, and detailed metrics
        }
        
        #endregion
        
        #region Arc Actions
        
        private void SelectArc(ArcModel arc)
        {
            selectedArc = arc;
            UpdateArcDetails();
            OnArcSelected?.Invoke(arc);
            
            // Load analytics for selected arc
            if (analyticsViewActive)
            {
                _ = LoadArcAnalytics(arc.Id);
            }
        }
        
        private void ShowCreateArcDialog()
        {
            // This would open a dialog for creating new arcs
            Debug.Log("Show create arc dialog");
        }
        
        private void ShowGenerateArcDialog()
        {
            // This would open a dialog for AI-generated arcs
            Debug.Log("Show generate arc dialog");
        }
        
        private void EditSelectedArc()
        {
            if (selectedArc == null)
                return;
            
            // This would open an edit dialog for the selected arc
            Debug.Log($"Edit arc: {selectedArc.Title}");
        }
        
        private async void DeleteSelectedArc()
        {
            if (selectedArc == null)
                return;
            
            try
            {
                var success = await arcService.DeleteArcAsync(selectedArc.Id);
                if (success)
                {
                    OnArcDeleted?.Invoke(selectedArc);
                    Debug.Log($"Arc deleted: {selectedArc.Title}");
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to delete arc: {ex.Message}");
            }
        }
        
        #endregion
        
        #region View Toggles
        
        private void ToggleTimelineView()
        {
            timelineViewActive = !timelineViewActive;
            
            if (timelinePanel != null)
                timelinePanel.SetActive(timelineViewActive);
            
            if (timelineViewActive && selectedArc != null)
                UpdateTimelineDisplay();
            
            // Update button text
            if (timelineToggleButton != null)
            {
                var buttonText = timelineToggleButton.GetComponentInChildren<TextMeshProUGUI>();
                if (buttonText != null)
                    buttonText.text = timelineViewActive ? "Hide Timeline" : "Show Timeline";
            }
        }
        
        private void ToggleStepView()
        {
            // This could toggle between different step visualization modes
            Debug.Log("Toggle step view");
        }
        
        private void ToggleAnalyticsView()
        {
            analyticsViewActive = !analyticsViewActive;
            
            if (analyticsPanel != null)
                analyticsPanel.SetActive(analyticsViewActive);
            
            if (analyticsViewActive && selectedArc != null)
            {
                _ = LoadArcAnalytics(selectedArc.Id);
            }
            
            // Update button text
            if (analyticsToggleButton != null)
            {
                var buttonText = analyticsToggleButton.GetComponentInChildren<TextMeshProUGUI>();
                if (buttonText != null)
                    buttonText.text = analyticsViewActive ? "Hide Analytics" : "Show Analytics";
            }
        }
        
        #endregion
        
        #region Event Handlers
        
        private void OnSearchChanged(string searchTerm)
        {
            ApplyFilters();
        }
        
        private void OnTypeFilterChanged(int value)
        {
            ApplyFilters();
        }
        
        private void OnStatusFilterChanged(int value)
        {
            ApplyFilters();
        }
        
        private void OnPriorityFilterChanged(int value)
        {
            ApplyFilters();
        }
        
        private void ClearFilters()
        {
            if (searchInputField != null)
                searchInputField.text = "";
            
            if (typeFilterDropdown != null)
                typeFilterDropdown.value = 0;
            
            if (statusFilterDropdown != null)
                statusFilterDropdown.value = 0;
            
            if (priorityFilterDropdown != null)
                priorityFilterDropdown.value = 0;
            
            ApplyFilters();
        }
        
        #endregion
        
        #region WebSocket Events
        
        private void SubscribeToEvents()
        {
            if (webSocketHandler != null)
            {
                webSocketHandler.OnArcCreated += HandleArcCreated;
                webSocketHandler.OnArcUpdated += HandleArcUpdated;
                webSocketHandler.OnArcDeleted += HandleArcDeleted;
                webSocketHandler.OnArcStarted += HandleArcStarted;
                webSocketHandler.OnArcCompleted += HandleArcCompleted;
                webSocketHandler.OnStepUpdated += HandleStepUpdated;
                webSocketHandler.OnProgressionUpdated += HandleProgressionUpdated;
            }
        }
        
        private void UnsubscribeFromEvents()
        {
            if (webSocketHandler != null)
            {
                webSocketHandler.OnArcCreated -= HandleArcCreated;
                webSocketHandler.OnArcUpdated -= HandleArcUpdated;
                webSocketHandler.OnArcDeleted -= HandleArcDeleted;
                webSocketHandler.OnArcStarted -= HandleArcStarted;
                webSocketHandler.OnArcCompleted -= HandleArcCompleted;
                webSocketHandler.OnStepUpdated -= HandleStepUpdated;
                webSocketHandler.OnProgressionUpdated -= HandleProgressionUpdated;
            }
        }
        
        private void HandleArcCreated(ArcModel arc)
        {
            allArcs.Add(arc);
            ApplyFilters();
            UpdateArcStats();
            OnArcCreated?.Invoke(arc);
        }
        
        private void HandleArcUpdated(ArcModel arc)
        {
            var existingArc = allArcs.FirstOrDefault(a => a.Id == arc.Id);
            if (existingArc != null)
            {
                var index = allArcs.IndexOf(existingArc);
                allArcs[index] = arc;
                
                if (selectedArc?.Id == arc.Id)
                {
                    selectedArc = arc;
                    UpdateArcDetails();
                }
                
                ApplyFilters();
                UpdateArcStats();
                OnArcUpdated?.Invoke(arc);
            }
        }
        
        private void HandleArcDeleted(string arcId)
        {
            allArcs.RemoveAll(a => a.Id == arcId);
            
            if (selectedArc?.Id == arcId)
            {
                selectedArc = null;
                if (arcDetailsPanel != null)
                    arcDetailsPanel.SetActive(false);
            }
            
            ApplyFilters();
            UpdateArcStats();
        }
        
        private void HandleArcStarted(ArcModel arc)
        {
            HandleArcUpdated(arc);
        }
        
        private void HandleArcCompleted(ArcModel arc)
        {
            HandleArcUpdated(arc);
        }
        
        private void HandleStepUpdated(string arcId, ArcStepModel step)
        {
            var arc = allArcs.FirstOrDefault(a => a.Id == arcId);
            if (arc != null)
            {
                var existingStep = arc.Steps.FirstOrDefault(s => s.Id == step.Id);
                if (existingStep != null)
                {
                    var stepIndex = arc.Steps.IndexOf(existingStep);
                    arc.Steps[stepIndex] = step;
                    
                    if (selectedArc?.Id == arcId)
                    {
                        UpdateStepVisualization();
                        if (timelineViewActive)
                            UpdateTimelineDisplay();
                    }
                }
            }
        }
        
        private void HandleProgressionUpdated(ArcProgressionModel progression)
        {
            var arc = allArcs.FirstOrDefault(a => a.Id == progression.ArcId);
            if (arc != null)
            {
                arc.CompletionPercentage = progression.CompletionPercentage;
                arc.CurrentStepIndex = progression.CurrentStep;
                
                if (selectedArc?.Id == progression.ArcId)
                {
                    UpdateArcDetails();
                }
            }
        }
        
        #endregion
        
        #region Public Interface
        
        /// <summary>
        /// Show the arc visualization UI
        /// </summary>
        public void Show()
        {
            if (arcVisualizationPanel != null)
                arcVisualizationPanel.SetActive(true);
        }
        
        /// <summary>
        /// Hide the arc visualization UI
        /// </summary>
        public void Hide()
        {
            if (arcVisualizationPanel != null)
                arcVisualizationPanel.SetActive(false);
        }
        
        /// <summary>
        /// Toggle the arc visualization visibility
        /// </summary>
        public void Toggle()
        {
            if (arcVisualizationPanel != null)
                arcVisualizationPanel.SetActive(!arcVisualizationPanel.activeSelf);
        }
        
        /// <summary>
        /// Force refresh the arc data
        /// </summary>
        public async void Refresh()
        {
            await LoadArcs();
        }
        
        /// <summary>
        /// Select a specific arc by ID
        /// </summary>
        public void SelectArcById(string arcId)
        {
            var arc = allArcs.FirstOrDefault(a => a.Id == arcId);
            if (arc != null)
            {
                SelectArc(arc);
            }
        }
        
        /// <summary>
        /// Get the currently selected arc
        /// </summary>
        public ArcModel GetSelectedArc()
        {
            return selectedArc;
        }
        
        #endregion
    }
} 