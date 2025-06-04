using NativeWebSocket;
using System.Collections.Generic;
using System.Linq;
using System;
using TMPro;
using UnityEngine.UI;
using UnityEngine;
using VDM.Infrastructure.Services;
using VDM.Systems.Quest.Models;
using VDM.Systems.Quest.Services;
using QuestDTO = VDM.Systems.Quest.Models.QuestDTO;

namespace VDM.Systems.Quest.Ui
{
    /// <summary>
    /// Comprehensive Quest Log UI with filtering, search, and real-time updates
    /// </summary>
    public class QuestLogUI : MonoBehaviour
    {
        [Header("UI References")]
        [SerializeField] private GameObject questLogPanel;
        [SerializeField] private Transform questListContainer;
        [SerializeField] private GameObject questItemPrefab;
        [SerializeField] private ScrollRect questScrollRect;
        
        [Header("Quest Details")]
        [SerializeField] private GameObject questDetailsPanel;
        [SerializeField] private TextMeshProUGUI questTitleText;
        [SerializeField] private TextMeshProUGUI questDescriptionText;
        [SerializeField] private TextMeshProUGUI questTypeText;
        [SerializeField] private TextMeshProUGUI questStatusText;
        [SerializeField] private TextMeshProUGUI questPriorityText;
        [SerializeField] private Transform questStepsContainer;
        [SerializeField] private GameObject questStepPrefab;
        [SerializeField] private Button questAbandonButton;
        [SerializeField] private Button questTrackButton;
        
        [Header("Filtering and Search")]
        [SerializeField] private TMP_InputField searchInputField;
        [SerializeField] private TMP_Dropdown statusFilterDropdown;
        [SerializeField] private TMP_Dropdown typeFilterDropdown;
        [SerializeField] private TMP_Dropdown priorityFilterDropdown;
        [SerializeField] private Button clearFiltersButton;
        [SerializeField] private Button refreshButton;
        
        [Header("Quest Stats")]
        [SerializeField] private TextMeshProUGUI totalQuestsText;
        [SerializeField] private TextMeshProUGUI activeQuestsText;
        [SerializeField] private TextMeshProUGUI completedQuestsText;
        [SerializeField] private TextMeshProUGUI failedQuestsText;
        
        [Header("Progress Tracking")]
        [SerializeField] private GameObject questTrackerOverlay;
        [SerializeField] private Transform trackedQuestsContainer;
        [SerializeField] private GameObject trackedQuestPrefab;
        [SerializeField] private int maxTrackedQuests = 5;
        
        // Services
        private QuestService questService;
        private QuestWebSocketHandler webSocketHandler;
        
        // Data
        private List<QuestDTO> allQuests = new List<QuestDTO>();
        private List<QuestDTO> filteredQuests = new List<QuestDTO>();
        private QuestDTO selectedQuest;
        private List<QuestDTO> trackedQuests = new List<QuestDTO>();
        
        // UI State
        private Dictionary<string, GameObject> questItemInstances = new Dictionary<string, GameObject>();
        private Dictionary<string, GameObject> trackedQuestInstances = new Dictionary<string, GameObject>();
        private bool isInitialized = false;
        
        // Events
        public event Action<QuestDTO> OnQuestSelected;
        public event Action<QuestDTO> OnQuestTracked;
        public event Action<QuestDTO> OnQuestUntracked;
        public event Action<QuestDTO> OnQuestAbandoned;
        
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
                questService = new QuestService();
                webSocketHandler = new QuestWebSocketHandler();
                
                // Setup UI events
                SetupUIEvents();
                
                // Setup filter dropdowns
                SetupFilterDropdowns();
                
                // Subscribe to WebSocket events
                SubscribeToEvents();
                
                // Initial data load
                await LoadQuests();
                
                // Initialize tracker overlay
                SetupQuestTracker();
                
                isInitialized = true;
                Debug.Log("Quest Log UI initialized successfully");
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to initialize Quest Log UI: {ex.Message}");
            }
        }
        
        private void SetupUIEvents()
        {
            // Search and filtering
            if (searchInputField != null)
                searchInputField.onValueChanged.AddListener(OnSearchChanged);
            
            if (statusFilterDropdown != null)
                statusFilterDropdown.onValueChanged.AddListener(OnStatusFilterChanged);
            
            if (typeFilterDropdown != null)
                typeFilterDropdown.onValueChanged.AddListener(OnTypeFilterChanged);
            
            if (priorityFilterDropdown != null)
                priorityFilterDropdown.onValueChanged.AddListener(OnPriorityFilterChanged);
            
            if (clearFiltersButton != null)
                clearFiltersButton.onClick.AddListener(ClearFilters);
            
            if (refreshButton != null)
                refreshButton.onClick.AddListener(async () => await LoadQuests());
            
            // Quest actions
            if (questAbandonButton != null)
                questAbandonButton.onClick.AddListener(AbandonSelectedQuest);
            
            if (questTrackButton != null)
                questTrackButton.onClick.AddListener(ToggleQuestTracking);
        }
        
        private void SetupFilterDropdowns()
        {
            // Status filter
            if (statusFilterDropdown != null)
            {
                statusFilterDropdown.options.Clear();
                statusFilterDropdown.options.Add(new TMP_Dropdown.OptionData("All Status"));
                statusFilterDropdown.options.Add(new TMP_Dropdown.OptionData("Active"));
                statusFilterDropdown.options.Add(new TMP_Dropdown.OptionData("Completed"));
                statusFilterDropdown.options.Add(new TMP_Dropdown.OptionData("Failed"));
                statusFilterDropdown.options.Add(new TMP_Dropdown.OptionData("Pending"));
                statusFilterDropdown.value = 0;
            }
            
            // Type filter
            if (typeFilterDropdown != null)
            {
                typeFilterDropdown.options.Clear();
                typeFilterDropdown.options.Add(new TMP_Dropdown.OptionData("All Types"));
                typeFilterDropdown.options.Add(new TMP_Dropdown.OptionData("Main"));
                typeFilterDropdown.options.Add(new TMP_Dropdown.OptionData("Side"));
                typeFilterDropdown.options.Add(new TMP_Dropdown.OptionData("Daily"));
                typeFilterDropdown.options.Add(new TMP_Dropdown.OptionData("Faction"));
                typeFilterDropdown.value = 0;
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
        
        private void SetupQuestTracker()
        {
            if (questTrackerOverlay != null)
            {
                questTrackerOverlay.SetActive(trackedQuests.Count > 0);
            }
        }
        
        #endregion
        
        #region Data Loading
        
        private async System.Threading.Tasks.Task LoadQuests()
        {
            try
            {
                var quests = await questService.GetQuestsAsync();
                
                allQuests.Clear();
                allQuests.AddRange(quests);
                
                ApplyFilters();
                UpdateQuestStats();
                
                Debug.Log($"Loaded {allQuests.Count} quests");
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to load quests: {ex.Message}");
            }
        }
        
        #endregion
        
        #region Filtering and Search
        
        private void ApplyFilters()
        {
            filteredQuests.Clear();
            
            var searchTerm = searchInputField?.text?.ToLower() ?? "";
            var statusFilter = GetSelectedStatusFilter();
            var typeFilter = GetSelectedTypeFilter();
            var priorityFilter = GetSelectedPriorityFilter();
            
            foreach (var quest in allQuests)
            {
                // Search filter
                if (!string.IsNullOrEmpty(searchTerm))
                {
                    if (!quest.Title.ToLower().Contains(searchTerm) && 
                        !quest.Description.ToLower().Contains(searchTerm))
                        continue;
                }
                
                // Status filter
                if (!string.IsNullOrEmpty(statusFilter) && quest.Status != statusFilter)
                    continue;
                
                // Type filter
                if (!string.IsNullOrEmpty(typeFilter) && quest.Type != typeFilter)
                    continue;
                
                // Priority filter
                if (!string.IsNullOrEmpty(priorityFilter) && quest.Priority != priorityFilter)
                    continue;
                
                filteredQuests.Add(quest);
            }
            
            // Sort by priority and creation date
            filteredQuests = filteredQuests.OrderBy(q => GetPriorityOrder(q.Priority))
                                         .ThenByDescending(q => q.CreatedAt)
                                         .ToList();
            
            UpdateQuestList();
        }
        
        private string GetSelectedStatusFilter()
        {
            if (statusFilterDropdown == null || statusFilterDropdown.value == 0)
                return null;
            
            return statusFilterDropdown.options[statusFilterDropdown.value].text.ToLower();
        }
        
        private string GetSelectedTypeFilter()
        {
            if (typeFilterDropdown == null || typeFilterDropdown.value == 0)
                return null;
            
            return typeFilterDropdown.options[typeFilterDropdown.value].text.ToLower();
        }
        
        private string GetSelectedPriorityFilter()
        {
            if (priorityFilterDropdown == null || priorityFilterDropdown.value == 0)
                return null;
            
            return priorityFilterDropdown.options[priorityFilterDropdown.value].text.ToLower();
        }
        
        private int GetPriorityOrder(string priority)
        {
            return priority?.ToLower() switch
            {
                "urgent" => 0,
                "high" => 1,
                "medium" => 2,
                "low" => 3,
                _ => 4
            };
        }
        
        #endregion
        
        #region UI Updates
        
        private void UpdateQuestList()
        {
            if (questListContainer == null || questItemPrefab == null)
                return;
            
            // Clear existing items
            foreach (var item in questItemInstances.Values)
            {
                if (item != null)
                    Destroy(item);
            }
            questItemInstances.Clear();
            
            // Create new items
            foreach (var quest in filteredQuests)
            {
                CreateQuestListItem(quest);
            }
            
            // Update scroll rect
            if (questScrollRect != null)
            {
                Canvas.ForceUpdateCanvases();
                questScrollRect.verticalNormalizedPosition = 1f;
            }
        }
        
        private void CreateQuestListItem(QuestDTO quest)
        {
            var itemObject = Instantiate(questItemPrefab, questListContainer);
            questItemInstances[quest.Id] = itemObject;
            
            var questItem = itemObject.GetComponent<QuestListItem>();
            if (questItem != null)
            {
                questItem.Initialize(quest);
                questItem.OnSelected += () => SelectQuest(quest);
                questItem.OnTrackToggled += () => ToggleQuestTracking(quest);
            }
            else
            {
                // Fallback manual setup
                SetupQuestItemManually(itemObject, quest);
            }
        }
        
        private void SetupQuestItemManually(GameObject itemObject, QuestDTO quest)
        {
            // Find and setup UI components manually
            var titleText = itemObject.GetComponentInChildren<TextMeshProUGUI>();
            if (titleText != null)
                titleText.text = quest.Title;
            
            var button = itemObject.GetComponent<Button>();
            if (button != null)
                button.onClick.AddListener(() => SelectQuest(quest));
        }
        
        private void UpdateQuestDetails()
        {
            if (questDetailsPanel == null || selectedQuest == null)
                return;
            
            questDetailsPanel.SetActive(true);
            
            // Update basic info
            if (questTitleText != null)
                questTitleText.text = selectedQuest.Title;
            
            if (questDescriptionText != null)
                questDescriptionText.text = selectedQuest.Description;
            
            if (questTypeText != null)
                questTypeText.text = $"Type: {selectedQuest.Type}";
            
            if (questStatusText != null)
                questStatusText.text = $"Status: {selectedQuest.Status}";
            
            if (questPriorityText != null)
                questPriorityText.text = $"Priority: {selectedQuest.Priority}";
            
            // Update quest steps
            UpdateQuestSteps();
            
            // Update buttons
            UpdateQuestActionButtons();
        }
        
        private void UpdateQuestSteps()
        {
            if (questStepsContainer == null || questStepPrefab == null || selectedQuest?.Steps == null)
                return;
            
            // Clear existing steps
            foreach (Transform child in questStepsContainer)
            {
                Destroy(child.gameObject);
            }
            
            // Create step items
            foreach (var step in selectedQuest.Steps)
            {
                var stepObject = Instantiate(questStepPrefab, questStepsContainer);
                var stepItem = stepObject.GetComponent<QuestStepItem>();
                
                if (stepItem != null)
                {
                    stepItem.Initialize(step);
                }
                else
                {
                    // Fallback manual setup
                    var stepText = stepObject.GetComponentInChildren<TextMeshProUGUI>();
                    if (stepText != null)
                    {
                        var checkmark = step.Completed ? "✓" : "○";
                        stepText.text = $"{checkmark} {step.Description}";
                    }
                }
            }
        }
        
        private void UpdateQuestActionButtons()
        {
            if (questAbandonButton != null)
            {
                questAbandonButton.interactable = selectedQuest?.Status == "active" || selectedQuest?.Status == "pending";
            }
            
            if (questTrackButton != null)
            {
                var isTracked = trackedQuests.Any(q => q.Id == selectedQuest?.Id);
                var buttonText = questTrackButton.GetComponentInChildren<TextMeshProUGUI>();
                if (buttonText != null)
                {
                    buttonText.text = isTracked ? "Untrack" : "Track";
                }
            }
        }
        
        private void UpdateQuestStats()
        {
            var total = allQuests.Count;
            var active = allQuests.Count(q => q.Status == "active");
            var completed = allQuests.Count(q => q.Status == "completed");
            var failed = allQuests.Count(q => q.Status == "failed");
            
            if (totalQuestsText != null)
                totalQuestsText.text = $"Total: {total}";
            
            if (activeQuestsText != null)
                activeQuestsText.text = $"Active: {active}";
            
            if (completedQuestsText != null)
                completedQuestsText.text = $"Completed: {completed}";
            
            if (failedQuestsText != null)
                failedQuestsText.text = $"Failed: {failed}";
        }
        
        #endregion
        
        #region Quest Actions
        
        private void SelectQuest(QuestDTO quest)
        {
            selectedQuest = quest;
            UpdateQuestDetails();
            OnQuestSelected?.Invoke(quest);
        }
        
        private async void AbandonSelectedQuest()
        {
            if (selectedQuest == null)
                return;
            
            try
            {
                var updateRequest = new UpdateQuestRequestDTO
                {
                    Status = "abandoned"
                };
                
                await questService.UpdateQuestAsync(selectedQuest.Id, updateRequest);
                OnQuestAbandoned?.Invoke(selectedQuest);
                
                Debug.Log($"Quest abandoned: {selectedQuest.Title}");
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to abandon quest: {ex.Message}");
            }
        }
        
        private void ToggleQuestTracking()
        {
            if (selectedQuest != null)
            {
                ToggleQuestTracking(selectedQuest);
            }
        }
        
        private void ToggleQuestTracking(QuestDTO quest)
        {
            var isTracked = trackedQuests.Any(q => q.Id == quest.Id);
            
            if (isTracked)
            {
                UntrackQuest(quest);
            }
            else
            {
                TrackQuest(quest);
            }
            
            UpdateQuestActionButtons();
            UpdateQuestTracker();
        }
        
        private void TrackQuest(QuestDTO quest)
        {
            if (trackedQuests.Count >= maxTrackedQuests)
            {
                Debug.LogWarning($"Maximum tracked quests limit reached ({maxTrackedQuests})");
                return;
            }
            
            if (!trackedQuests.Any(q => q.Id == quest.Id))
            {
                trackedQuests.Add(quest);
                OnQuestTracked?.Invoke(quest);
                Debug.Log($"Quest tracked: {quest.Title}");
            }
        }
        
        private void UntrackQuest(QuestDTO quest)
        {
            var trackedQuest = trackedQuests.FirstOrDefault(q => q.Id == quest.Id);
            if (trackedQuest != null)
            {
                trackedQuests.Remove(trackedQuest);
                OnQuestUntracked?.Invoke(quest);
                Debug.Log($"Quest untracked: {quest.Title}");
            }
        }
        
        #endregion
        
        #region Quest Tracker
        
        private void UpdateQuestTracker()
        {
            if (questTrackerOverlay != null)
            {
                questTrackerOverlay.SetActive(trackedQuests.Count > 0);
            }
            
            if (trackedQuestsContainer == null || trackedQuestPrefab == null)
                return;
            
            // Clear existing tracked quest items
            foreach (var item in trackedQuestInstances.Values)
            {
                if (item != null)
                    Destroy(item);
            }
            trackedQuestInstances.Clear();
            
            // Create new tracked quest items
            foreach (var quest in trackedQuests)
            {
                CreateTrackedQuestItem(quest);
            }
        }
        
        private void CreateTrackedQuestItem(QuestDTO quest)
        {
            var itemObject = Instantiate(trackedQuestPrefab, trackedQuestsContainer);
            trackedQuestInstances[quest.Id] = itemObject;
            
            var trackedItem = itemObject.GetComponent<TrackedQuestItem>();
            if (trackedItem != null)
            {
                trackedItem.Initialize(quest);
                trackedItem.OnUntrack += () => UntrackQuest(quest);
            }
        }
        
        #endregion
        
        #region Event Handlers
        
        private void OnSearchChanged(string searchTerm)
        {
            ApplyFilters();
        }
        
        private void OnStatusFilterChanged(int value)
        {
            ApplyFilters();
        }
        
        private void OnTypeFilterChanged(int value)
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
            
            if (statusFilterDropdown != null)
                statusFilterDropdown.value = 0;
            
            if (typeFilterDropdown != null)
                typeFilterDropdown.value = 0;
            
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
                webSocketHandler.OnQuestCreated += HandleQuestCreated;
                webSocketHandler.OnQuestUpdated += HandleQuestUpdated;
                webSocketHandler.OnQuestDeleted += HandleQuestDeleted;
                webSocketHandler.OnQuestCompleted += HandleQuestCompleted;
                webSocketHandler.OnStepUpdated += HandleStepUpdated;
                webSocketHandler.OnProgressUpdated += HandleProgressUpdated;
            }
        }
        
        private void UnsubscribeFromEvents()
        {
            if (webSocketHandler != null)
            {
                webSocketHandler.OnQuestCreated -= HandleQuestCreated;
                webSocketHandler.OnQuestUpdated -= HandleQuestUpdated;
                webSocketHandler.OnQuestDeleted -= HandleQuestDeleted;
                webSocketHandler.OnQuestCompleted -= HandleQuestCompleted;
                webSocketHandler.OnStepUpdated -= HandleStepUpdated;
                webSocketHandler.OnProgressUpdated -= HandleProgressUpdated;
            }
        }
        
        private void HandleQuestCreated(QuestDTO quest)
        {
            allQuests.Add(quest);
            ApplyFilters();
            UpdateQuestStats();
        }
        
        private void HandleQuestUpdated(QuestDTO quest)
        {
            var existingQuest = allQuests.FirstOrDefault(q => q.Id == quest.Id);
            if (existingQuest != null)
            {
                var index = allQuests.IndexOf(existingQuest);
                allQuests[index] = quest;
                
                // Update tracked quest if it's being tracked
                var trackedQuest = trackedQuests.FirstOrDefault(q => q.Id == quest.Id);
                if (trackedQuest != null)
                {
                    var trackedIndex = trackedQuests.IndexOf(trackedQuest);
                    trackedQuests[trackedIndex] = quest;
                    UpdateQuestTracker();
                }
                
                // Update selected quest if it's the one being updated
                if (selectedQuest?.Id == quest.Id)
                {
                    selectedQuest = quest;
                    UpdateQuestDetails();
                }
                
                ApplyFilters();
                UpdateQuestStats();
            }
        }
        
        private void HandleQuestDeleted(string questId)
        {
            allQuests.RemoveAll(q => q.Id == questId);
            trackedQuests.RemoveAll(q => q.Id == questId);
            
            if (selectedQuest?.Id == questId)
            {
                selectedQuest = null;
                if (questDetailsPanel != null)
                    questDetailsPanel.SetActive(false);
            }
            
            ApplyFilters();
            UpdateQuestStats();
            UpdateQuestTracker();
        }
        
        private void HandleQuestCompleted(QuestDTO quest)
        {
            HandleQuestUpdated(quest);
        }
        
        private void HandleStepUpdated(string questId, QuestStepDTO step)
        {
            var quest = allQuests.FirstOrDefault(q => q.Id == questId);
            if (quest != null)
            {
                var existingStep = quest.Steps.FirstOrDefault(s => s.Id == step.Id);
                if (existingStep != null)
                {
                    var stepIndex = quest.Steps.IndexOf(existingStep);
                    quest.Steps[stepIndex] = step;
                    
                    if (selectedQuest?.Id == questId)
                    {
                        UpdateQuestSteps();
                    }
                    
                    // Update tracked quest display
                    if (trackedQuests.Any(q => q.Id == questId))
                    {
                        UpdateQuestTracker();
                    }
                }
            }
        }
        
        private void HandleProgressUpdated(string questId, Dictionary<string, object> progressData)
        {
            var quest = allQuests.FirstOrDefault(q => q.Id == questId);
            if (quest != null)
            {
                quest.ProgressData = progressData;
                
                if (selectedQuest?.Id == questId)
                {
                    UpdateQuestDetails();
                }
                
                if (trackedQuests.Any(q => q.Id == questId))
                {
                    UpdateQuestTracker();
                }
            }
        }
        
        #endregion
        
        #region Public Interface
        
        /// <summary>
        /// Show the quest log UI
        /// </summary>
        public void Show()
        {
            if (questLogPanel != null)
                questLogPanel.SetActive(true);
        }
        
        /// <summary>
        /// Hide the quest log UI
        /// </summary>
        public void Hide()
        {
            if (questLogPanel != null)
                questLogPanel.SetActive(false);
        }
        
        /// <summary>
        /// Toggle the quest log visibility
        /// </summary>
        public void Toggle()
        {
            if (questLogPanel != null)
                questLogPanel.SetActive(!questLogPanel.activeSelf);
        }
        
        /// <summary>
        /// Force refresh the quest data
        /// </summary>
        public async void Refresh()
        {
            await LoadQuests();
        }
        
        /// <summary>
        /// Get currently tracked quests
        /// </summary>
        public List<QuestDTO> GetTrackedQuests()
        {
            return new List<QuestDTO>(trackedQuests);
        }
        
        #endregion
    }
} 