using UnityEngine;
using UnityEngine.UI;
using TMPro;
using VDM.UI.Core;
using VDM.Systems.Quest.Models;
using VDM.Systems.Quest.Services;
using System.Collections.Generic;
using System.Linq;

namespace VDM.UI.Systems.Quest
{
    /// <summary>
    /// UI panel for quest log display and quest management
    /// </summary>
    public class QuestLogPanel : BaseUIPanel
    {
        [Header("Quest Categories")]
        [SerializeField] private Button activeQuestsTabButton;
        [SerializeField] private Button completedQuestsTabButton;
        [SerializeField] private Button failedQuestsTabButton;
        [SerializeField] private Button allQuestsTabButton;
        
        [Header("Quest List")]
        [SerializeField] private ScrollRect questListScrollRect;
        [SerializeField] private Transform questListParent;
        [SerializeField] private GameObject questEntryPrefab;
        [SerializeField] private TextMeshProUGUI questCountText;
        
        [Header("Quest Details")]
        [SerializeField] private GameObject questDetailsPanel;
        [SerializeField] private TextMeshProUGUI questTitleText;
        [SerializeField] private TextMeshProUGUI questDescriptionText;
        [SerializeField] private TextMeshProUGUI questGiverText;
        [SerializeField] private TextMeshProUGUI questLocationText;
        [SerializeField] private TextMeshProUGUI questRewardText;
        [SerializeField] private TextMeshProUGUI questStatusText;
        [SerializeField] private Image questStatusIcon;
        
        [Header("Objectives")]
        [SerializeField] private Transform objectivesParent;
        [SerializeField] private GameObject objectiveEntryPrefab;
        [SerializeField] private TextMeshProUGUI objectivesHeaderText;
        
        [Header("Quest Actions")]
        [SerializeField] private Button trackQuestButton;
        [SerializeField] private Button untrackQuestButton;
        [SerializeField] private Button abandonQuestButton;
        [SerializeField] private Button shareQuestButton;
        [SerializeField] private Button showOnMapButton;
        
        [Header("Filtering & Sorting")]
        [SerializeField] private TMP_InputField searchInputField;
        [SerializeField] private TMP_Dropdown sortDropdown;
        [SerializeField] private TMP_Dropdown filterDropdown;
        [SerializeField] private Button sortAscendingButton;
        [SerializeField] private Button sortDescendingButton;
        
        [Header("Quest Progress")]
        [SerializeField] private GameObject questProgressPanel;
        [SerializeField] private Slider questProgressSlider;
        [SerializeField] private TextMeshProUGUI questProgressText;
        
        [Header("Rewards Preview")]
        [SerializeField] private Transform rewardsParent;
        [SerializeField] private GameObject rewardItemPrefab;
        
        private QuestService questService;
        private List<GameObject> questEntries = new List<GameObject>();
        private List<GameObject> objectiveEntries = new List<GameObject>();
        private List<GameObject> rewardItems = new List<GameObject>();
        private QuestModel selectedQuest;
        private QuestCategory currentCategory = QuestCategory.Active;
        private QuestSortCriteria currentSortCriteria = QuestSortCriteria.Priority;
        private QuestFilter currentFilter = QuestFilter.All;
        private bool sortAscending = false;
        private string searchFilter = "";
        
        private enum QuestCategory
        {
            Active,
            Completed,
            Failed,
            All
        }
        
        private enum QuestSortCriteria
        {
            Priority,
            Name,
            Level,
            Location,
            Progress,
            DateReceived
        }
        
        private enum QuestFilter
        {
            All,
            MainQuests,
            SideQuests,
            DailyQuests,
            GuildQuests,
            PersonalQuests
        }
        
        protected override void Awake()
        {
            base.Awake();
            questService = FindObjectOfType<QuestService>();
            
            // Setup category tabs
            if (activeQuestsTabButton != null)
                activeQuestsTabButton.onClick.AddListener(() => ShowCategory(QuestCategory.Active));
            if (completedQuestsTabButton != null)
                completedQuestsTabButton.onClick.AddListener(() => ShowCategory(QuestCategory.Completed));
            if (failedQuestsTabButton != null)
                failedQuestsTabButton.onClick.AddListener(() => ShowCategory(QuestCategory.Failed));
            if (allQuestsTabButton != null)
                allQuestsTabButton.onClick.AddListener(() => ShowCategory(QuestCategory.All));
            
            // Setup quest actions
            if (trackQuestButton != null)
                trackQuestButton.onClick.AddListener(TrackSelectedQuest);
            if (untrackQuestButton != null)
                untrackQuestButton.onClick.AddListener(UntrackSelectedQuest);
            if (abandonQuestButton != null)
                abandonQuestButton.onClick.AddListener(AbandonSelectedQuest);
            if (shareQuestButton != null)
                shareQuestButton.onClick.AddListener(ShareSelectedQuest);
            if (showOnMapButton != null)
                showOnMapButton.onClick.AddListener(ShowQuestOnMap);
            
            // Setup filtering and sorting
            if (searchInputField != null)
                searchInputField.onValueChanged.AddListener(OnSearchFilterChanged);
            if (sortDropdown != null)
                sortDropdown.onValueChanged.AddListener(OnSortCriteriaChanged);
            if (filterDropdown != null)
                filterDropdown.onValueChanged.AddListener(OnFilterChanged);
            if (sortAscendingButton != null)
                sortAscendingButton.onClick.AddListener(() => SetSortOrder(true));
            if (sortDescendingButton != null)
                sortDescendingButton.onClick.AddListener(() => SetSortOrder(false));
        }
        
        protected override void OnEnable()
        {
            base.OnEnable();
            if (questService != null)
            {
                questService.OnQuestAdded += OnQuestAdded;
                questService.OnQuestCompleted += OnQuestCompleted;
                questService.OnQuestFailed += OnQuestFailed;
                questService.OnQuestAbandoned += OnQuestAbandoned;
                questService.OnQuestProgressUpdated += OnQuestProgressUpdated;
                questService.OnObjectiveCompleted += OnObjectiveCompleted;
            }
        }
        
        protected override void OnDisable()
        {
            base.OnDisable();
            if (questService != null)
            {
                questService.OnQuestAdded -= OnQuestAdded;
                questService.OnQuestCompleted -= OnQuestCompleted;
                questService.OnQuestFailed -= OnQuestFailed;
                questService.OnQuestAbandoned -= OnQuestAbandoned;
                questService.OnQuestProgressUpdated -= OnQuestProgressUpdated;
                questService.OnObjectiveCompleted -= OnObjectiveCompleted;
            }
        }
        
        /// <summary>
        /// Initialize quest log display
        /// </summary>
        public void InitializeQuestLog()
        {
            ShowCategory(QuestCategory.Active);
            
            if (questDetailsPanel != null)
                questDetailsPanel.SetActive(false);
        }
        
        /// <summary>
        /// Show quests for a specific category
        /// </summary>
        private void ShowCategory(QuestCategory category)
        {
            currentCategory = category;
            RefreshQuestList();
            UpdateTabButtonStates();
        }
        
        /// <summary>
        /// Refresh the quest list display
        /// </summary>
        private void RefreshQuestList()
        {
            ClearQuestEntries();
            
            if (questService == null || questListParent == null || questEntryPrefab == null)
                return;
            
            var filteredQuests = GetFilteredAndSortedQuests();
            
            foreach (var quest in filteredQuests)
            {
                GameObject questEntry = Instantiate(questEntryPrefab, questListParent);
                QuestEntry entryComponent = questEntry.GetComponent<QuestEntry>();
                
                if (entryComponent != null)
                {
                    entryComponent.Initialize(quest, OnQuestSelected);
                }
                
                questEntries.Add(questEntry);
            }
            
            UpdateQuestCount(filteredQuests.Count);
        }
        
        /// <summary>
        /// Get filtered and sorted quests based on current settings
        /// </summary>
        private List<QuestModel> GetFilteredAndSortedQuests()
        {
            if (questService?.GetAllQuests() == null)
                return new List<QuestModel>();
            
            var quests = questService.GetAllQuests().AsEnumerable();
            
            // Apply category filter
            quests = currentCategory switch
            {
                QuestCategory.Active => quests.Where(q => q.Status == QuestStatus.Active),
                QuestCategory.Completed => quests.Where(q => q.Status == QuestStatus.Completed),
                QuestCategory.Failed => quests.Where(q => q.Status == QuestStatus.Failed),
                _ => quests
            };
            
            // Apply type filter
            quests = currentFilter switch
            {
                QuestFilter.MainQuests => quests.Where(q => q.Type == QuestType.Main),
                QuestFilter.SideQuests => quests.Where(q => q.Type == QuestType.Side),
                QuestFilter.DailyQuests => quests.Where(q => q.Type == QuestType.Daily),
                QuestFilter.GuildQuests => quests.Where(q => q.Type == QuestType.Guild),
                QuestFilter.PersonalQuests => quests.Where(q => q.Type == QuestType.Personal),
                _ => quests
            };
            
            // Apply search filter
            if (!string.IsNullOrEmpty(searchFilter))
            {
                quests = quests.Where(q => q.Title.ToLower().Contains(searchFilter.ToLower()) ||
                                          q.Description.ToLower().Contains(searchFilter.ToLower()) ||
                                          q.QuestGiver.ToLower().Contains(searchFilter.ToLower()));
            }
            
            // Apply sorting
            quests = currentSortCriteria switch
            {
                QuestSortCriteria.Priority => sortAscending ? quests.OrderBy(q => q.Priority) : quests.OrderByDescending(q => q.Priority),
                QuestSortCriteria.Name => sortAscending ? quests.OrderBy(q => q.Title) : quests.OrderByDescending(q => q.Title),
                QuestSortCriteria.Level => sortAscending ? quests.OrderBy(q => q.RecommendedLevel) : quests.OrderByDescending(q => q.RecommendedLevel),
                QuestSortCriteria.Location => sortAscending ? quests.OrderBy(q => q.Location) : quests.OrderByDescending(q => q.Location),
                QuestSortCriteria.Progress => sortAscending ? quests.OrderBy(q => q.ProgressPercentage) : quests.OrderByDescending(q => q.ProgressPercentage),
                QuestSortCriteria.DateReceived => sortAscending ? quests.OrderBy(q => q.DateReceived) : quests.OrderByDescending(q => q.DateReceived),
                _ => quests.OrderByDescending(q => q.Priority)
            };
            
            return quests.ToList();
        }
        
        /// <summary>
        /// Show details for selected quest
        /// </summary>
        private void ShowQuestDetails(QuestModel quest)
        {
            selectedQuest = quest;
            
            if (questDetailsPanel == null) return;
            
            questDetailsPanel.SetActive(true);
            
            // Update quest information
            if (questTitleText != null)
                questTitleText.text = quest.Title;
            if (questDescriptionText != null)
                questDescriptionText.text = quest.Description;
            if (questGiverText != null)
                questGiverText.text = $"Quest Giver: {quest.QuestGiver}";
            if (questLocationText != null)
                questLocationText.text = $"Location: {quest.Location}";
            if (questStatusText != null)
            {
                questStatusText.text = quest.Status.ToString();
                questStatusText.color = GetQuestStatusColor(quest.Status);
            }
            
            // Update quest status icon
            if (questStatusIcon != null)
                questStatusIcon.sprite = GetQuestStatusIcon(quest.Status);
            
            // Update rewards
            if (questRewardText != null)
                questRewardText.text = GetRewardText(quest);
            
            // Update progress
            UpdateQuestProgress(quest);
            
            // Update objectives
            UpdateObjectives(quest);
            
            // Update reward items
            UpdateRewardItems(quest);
            
            // Update action buttons
            UpdateActionButtons(quest);
        }
        
        /// <summary>
        /// Update quest progress display
        /// </summary>
        private void UpdateQuestProgress(QuestModel quest)
        {
            if (questProgressPanel == null) return;
            
            bool showProgress = quest.Status == QuestStatus.Active && quest.HasProgressTracking;
            questProgressPanel.SetActive(showProgress);
            
            if (showProgress)
            {
                if (questProgressSlider != null)
                    questProgressSlider.value = quest.ProgressPercentage / 100f;
                if (questProgressText != null)
                    questProgressText.text = $"Progress: {quest.ProgressPercentage:F0}%";
            }
        }
        
        /// <summary>
        /// Update objectives display
        /// </summary>
        private void UpdateObjectives(QuestModel quest)
        {
            ClearObjectiveEntries();
            
            if (quest.Objectives == null || objectivesParent == null || objectiveEntryPrefab == null)
                return;
            
            if (objectivesHeaderText != null)
                objectivesHeaderText.text = $"Objectives ({quest.CompletedObjectives}/{quest.Objectives.Count})";
            
            foreach (var objective in quest.Objectives)
            {
                GameObject objectiveEntry = Instantiate(objectiveEntryPrefab, objectivesParent);
                ObjectiveEntry entryComponent = objectiveEntry.GetComponent<ObjectiveEntry>();
                
                if (entryComponent != null)
                {
                    entryComponent.Initialize(objective);
                }
                
                objectiveEntries.Add(objectiveEntry);
            }
        }
        
        /// <summary>
        /// Update reward items display
        /// </summary>
        private void UpdateRewardItems(QuestModel quest)
        {
            ClearRewardItems();
            
            if (quest.Rewards?.Items == null || rewardsParent == null || rewardItemPrefab == null)
                return;
            
            foreach (var rewardItem in quest.Rewards.Items)
            {
                GameObject rewardEntry = Instantiate(rewardItemPrefab, rewardsParent);
                RewardItem rewardComponent = rewardEntry.GetComponent<RewardItem>();
                
                if (rewardComponent != null)
                {
                    rewardComponent.Initialize(rewardItem);
                }
                
                rewardItems.Add(rewardEntry);
            }
        }
        
        /// <summary>
        /// Update action button states
        /// </summary>
        private void UpdateActionButtons(QuestModel quest)
        {
            if (trackQuestButton != null)
                trackQuestButton.interactable = quest.Status == QuestStatus.Active && !quest.IsTracked;
            if (untrackQuestButton != null)
                untrackQuestButton.interactable = quest.IsTracked;
            if (abandonQuestButton != null)
                abandonQuestButton.interactable = quest.Status == QuestStatus.Active && quest.CanAbandon;
            if (shareQuestButton != null)
                shareQuestButton.interactable = quest.CanShare;
            if (showOnMapButton != null)
                showOnMapButton.interactable = !string.IsNullOrEmpty(quest.Location);
        }
        
        /// <summary>
        /// Get formatted reward text
        /// </summary>
        private string GetRewardText(QuestModel quest)
        {
            if (quest.Rewards == null) return "No rewards";
            
            var rewards = new List<string>();
            
            if (quest.Rewards.Experience > 0)
                rewards.Add($"{quest.Rewards.Experience:N0} XP");
            if (quest.Rewards.Gold > 0)
                rewards.Add($"{quest.Rewards.Gold:N0} Gold");
            if (quest.Rewards.Items?.Count > 0)
                rewards.Add($"{quest.Rewards.Items.Count} Item(s)");
            
            return rewards.Count > 0 ? string.Join(", ", rewards) : "No rewards";
        }
        
        /// <summary>
        /// Get color for quest status
        /// </summary>
        private Color GetQuestStatusColor(QuestStatus status)
        {
            return status switch
            {
                QuestStatus.Active => Color.yellow,
                QuestStatus.Completed => Color.green,
                QuestStatus.Failed => Color.red,
                QuestStatus.Abandoned => Color.gray,
                _ => Color.white
            };
        }
        
        /// <summary>
        /// Get icon for quest status
        /// </summary>
        private Sprite GetQuestStatusIcon(QuestStatus status)
        {
            string iconPath = status switch
            {
                QuestStatus.Active => "Icons/quest_active",
                QuestStatus.Completed => "Icons/quest_completed",
                QuestStatus.Failed => "Icons/quest_failed",
                QuestStatus.Abandoned => "Icons/quest_abandoned",
                _ => "Icons/quest_default"
            };
            
            return Resources.Load<Sprite>(iconPath);
        }
        
        /// <summary>
        /// Update quest count display
        /// </summary>
        private void UpdateQuestCount(int count)
        {
            if (questCountText != null)
            {
                string categoryName = currentCategory.ToString();
                questCountText.text = $"{categoryName} Quests: {count}";
            }
        }
        
        /// <summary>
        /// Update tab button visual states
        /// </summary>
        private void UpdateTabButtonStates()
        {
            SetTabButtonState(activeQuestsTabButton, currentCategory == QuestCategory.Active);
            SetTabButtonState(completedQuestsTabButton, currentCategory == QuestCategory.Completed);
            SetTabButtonState(failedQuestsTabButton, currentCategory == QuestCategory.Failed);
            SetTabButtonState(allQuestsTabButton, currentCategory == QuestCategory.All);
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
        
        #region Clear Methods
        
        private void ClearQuestEntries()
        {
            foreach (var entry in questEntries)
            {
                if (entry != null)
                    DestroyImmediate(entry);
            }
            questEntries.Clear();
        }
        
        private void ClearObjectiveEntries()
        {
            foreach (var entry in objectiveEntries)
            {
                if (entry != null)
                    DestroyImmediate(entry);
            }
            objectiveEntries.Clear();
        }
        
        private void ClearRewardItems()
        {
            foreach (var item in rewardItems)
            {
                if (item != null)
                    DestroyImmediate(item);
            }
            rewardItems.Clear();
        }
        
        #endregion
        
        #region Event Handlers
        
        private void OnQuestSelected(QuestModel quest)
        {
            ShowQuestDetails(quest);
        }
        
        private void OnSearchFilterChanged(string filter)
        {
            searchFilter = filter;
            RefreshQuestList();
        }
        
        private void OnSortCriteriaChanged(int index)
        {
            currentSortCriteria = (QuestSortCriteria)index;
            RefreshQuestList();
        }
        
        private void OnFilterChanged(int index)
        {
            currentFilter = (QuestFilter)index;
            RefreshQuestList();
        }
        
        private void SetSortOrder(bool ascending)
        {
            sortAscending = ascending;
            RefreshQuestList();
        }
        
        private void OnQuestAdded(QuestModel quest)
        {
            RefreshQuestList();
            NotificationSystem.Instance?.ShowNotification(
                $"New quest received: {quest.Title}",
                NotificationType.Info
            );
        }
        
        private void OnQuestCompleted(QuestModel quest)
        {
            RefreshQuestList();
            if (selectedQuest?.Id == quest.Id)
                ShowQuestDetails(quest);
            
            NotificationSystem.Instance?.ShowNotification(
                $"Quest completed: {quest.Title}",
                NotificationType.Success
            );
        }
        
        private void OnQuestFailed(QuestModel quest)
        {
            RefreshQuestList();
            if (selectedQuest?.Id == quest.Id)
                ShowQuestDetails(quest);
            
            NotificationSystem.Instance?.ShowNotification(
                $"Quest failed: {quest.Title}",
                NotificationType.Warning
            );
        }
        
        private void OnQuestAbandoned(QuestModel quest)
        {
            RefreshQuestList();
            if (selectedQuest?.Id == quest.Id)
            {
                selectedQuest = null;
                if (questDetailsPanel != null)
                    questDetailsPanel.SetActive(false);
            }
        }
        
        private void OnQuestProgressUpdated(QuestModel quest)
        {
            if (selectedQuest?.Id == quest.Id)
            {
                UpdateQuestProgress(quest);
                UpdateObjectives(quest);
            }
        }
        
        private void OnObjectiveCompleted(QuestModel quest, ObjectiveModel objective)
        {
            if (selectedQuest?.Id == quest.Id)
            {
                UpdateObjectives(quest);
                UpdateQuestProgress(quest);
            }
            
            NotificationSystem.Instance?.ShowNotification(
                $"Objective completed: {objective.Description}",
                NotificationType.Success
            );
        }
        
        #endregion
        
        #region Action Methods
        
        private void TrackSelectedQuest()
        {
            if (selectedQuest != null && questService != null)
            {
                questService.TrackQuest(selectedQuest.Id);
                UpdateActionButtons(selectedQuest);
            }
        }
        
        private void UntrackSelectedQuest()
        {
            if (selectedQuest != null && questService != null)
            {
                questService.UntrackQuest(selectedQuest.Id);
                UpdateActionButtons(selectedQuest);
            }
        }
        
        private void AbandonSelectedQuest()
        {
            if (selectedQuest != null && questService != null)
            {
                ModalSystem.Instance?.ShowConfirmation(
                    "Abandon Quest",
                    $"Are you sure you want to abandon '{selectedQuest.Title}'? This action cannot be undone.",
                    () => questService.AbandonQuest(selectedQuest.Id),
                    null
                );
            }
        }
        
        private void ShareSelectedQuest()
        {
            if (selectedQuest != null && questService != null)
            {
                questService.ShareQuest(selectedQuest.Id);
                NotificationSystem.Instance?.ShowNotification(
                    $"Quest shared: {selectedQuest.Title}",
                    NotificationType.Info
                );
            }
        }
        
        private void ShowQuestOnMap()
        {
            if (selectedQuest != null)
            {
                // Open world map and highlight quest location
                UIManager.Instance?.ShowPanel("WorldMapPanel");
                // Additional logic to highlight quest location on map
            }
        }
        
        #endregion
    }
} 