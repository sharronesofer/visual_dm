using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using System;
using TMPro;
using VDM.UI.Core;
using VDM.Systems.Faction.Models;
using VDM.Systems.Faction.Services;
using VDM.Infrastructure.Services;
using VDM.DTOs.Common;


namespace VDM.Systems.Faction.Ui
{
    /// <summary>
    /// Main faction display and management panel
    /// Provides comprehensive faction information display and diplomatic interaction controls
    /// </summary>
    public class FactionPanel : UIPanel
    {
        [Header("Faction Info Display")]
        [SerializeField] private TextMeshProUGUI factionNameText;
        [SerializeField] private TextMeshProUGUI factionTypeText;
        [SerializeField] private TextMeshProUGUI alignmentText;
        [SerializeField] private TextMeshProUGUI descriptionText;
        [SerializeField] private Image factionBanner;
        
        [Header("Faction Stats")]
        [SerializeField] private Slider influenceSlider;
        [SerializeField] private TextMeshProUGUI influenceText;
        [SerializeField] private Slider powerSlider;
        [SerializeField] private TextMeshProUGUI powerText;
        [SerializeField] private Slider wealthSlider;
        [SerializeField] private TextMeshProUGUI wealthText;
        [SerializeField] private TextMeshProUGUI reputationText;
        
        [Header("Leadership")]
        [SerializeField] private TextMeshProUGUI leaderText;
        [SerializeField] private Button leaderButton;
        [SerializeField] private TextMeshProUGUI headquartersText;
        [SerializeField] private Button headquartersButton;
        
        [Header("Members Section")]
        [SerializeField] private Transform membersContainer;
        [SerializeField] private GameObject memberItemPrefab;
        [SerializeField] private TextMeshProUGUI memberCountText;
        [SerializeField] private Button viewAllMembersButton;
        
        [Header("Relationships Section")]
        [SerializeField] private Transform relationshipsContainer;
        [SerializeField] private GameObject relationshipItemPrefab;
        [SerializeField] private Button manageRelationshipsButton;
        
        [Header("Resources")]
        [SerializeField] private TextMeshProUGUI goldText;
        [SerializeField] private Transform resourcesContainer;
        [SerializeField] private GameObject resourceItemPrefab;
        
        [Header("Goals and Policies")]
        [SerializeField] private Transform currentGoalsContainer;
        [SerializeField] private Transform completedGoalsContainer;
        [SerializeField] private GameObject goalItemPrefab;
        [SerializeField] private Button managePoliciesButton;
        
        [Header("Action Buttons")]
        [SerializeField] private Button editFactionButton;
        [SerializeField] private Button diplomaticActionsButton;
        [SerializeField] private Button territoryButton;
        [SerializeField] private Button financeButton;
        
        [Header("Recent Activity")]
        [SerializeField] private Transform recentEventsContainer;
        [SerializeField] private GameObject eventItemPrefab;

        // Services and data
        private FactionService _factionService;
        private FactionResponseDTO _currentFaction;
        private List<GameObject> _memberItems = new List<GameObject>();
        private List<GameObject> _relationshipItems = new List<GameObject>();
        private List<GameObject> _resourceItems = new List<GameObject>();
        private List<GameObject> _goalItems = new List<GameObject>();
        private List<GameObject> _eventItems = new List<GameObject>();

        // Events
        public event Action<FactionResponseDTO> OnFactionSelected;
        public event Action<FactionResponseDTO> OnEditRequested;
        public event Action<FactionResponseDTO> OnDiplomaticActionsRequested;
        public event Action<FactionResponseDTO> OnTerritoryRequested;
        public event Action<FactionResponseDTO> OnFinanceRequested;
        public event Action<int> OnLeaderRequested; // character ID
        public event Action<int> OnHeadquartersRequested; // location ID

        protected override void Awake()
        {
            base.Awake();
            
            // Find faction service
            _factionService = FindObjectOfType<FactionService>();
            
            // Setup button listeners
            SetupButtonListeners();
        }

        private void SetupButtonListeners()
        {
            if (editFactionButton != null)
                editFactionButton.onClick.AddListener(() => OnEditRequested?.Invoke(_currentFaction));
            
            if (diplomaticActionsButton != null)
                diplomaticActionsButton.onClick.AddListener(() => OnDiplomaticActionsRequested?.Invoke(_currentFaction));
            
            if (territoryButton != null)
                territoryButton.onClick.AddListener(() => OnTerritoryRequested?.Invoke(_currentFaction));
            
            if (financeButton != null)
                financeButton.onClick.AddListener(() => OnFinanceRequested?.Invoke(_currentFaction));
            
            if (leaderButton != null)
                leaderButton.onClick.AddListener(() => {
                    if (_currentFaction?.LeaderId.HasValue == true)
                        OnLeaderRequested?.Invoke(_currentFaction.LeaderId.Value);
                });
            
            if (headquartersButton != null)
                headquartersButton.onClick.AddListener(() => {
                    if (_currentFaction?.HeadquartersId.HasValue == true)
                        OnHeadquartersRequested?.Invoke(_currentFaction.HeadquartersId.Value);
                });
            
            if (viewAllMembersButton != null)
                viewAllMembersButton.onClick.AddListener(LoadAllMembers);
            
            if (manageRelationshipsButton != null)
                manageRelationshipsButton.onClick.AddListener(LoadAllRelationships);
            
            if (managePoliciesButton != null)
                managePoliciesButton.onClick.AddListener(OpenPoliciesPanel);
        }

        protected override void OnEnable()
        {
            base.OnEnable();
            
            if (_factionService != null)
            {
                _factionService.OnFactionUpdated += HandleFactionUpdated;
                _factionService.OnRelationshipChanged += HandleRelationshipChanged;
                _factionService.OnMembershipChanged += HandleMembershipChanged;
                _factionService.OnDiplomaticEvent += HandleDiplomaticEvent;
            }
        }

        protected override void OnDisable()
        {
            base.OnDisable();
            
            if (_factionService != null)
            {
                _factionService.OnFactionUpdated -= HandleFactionUpdated;
                _factionService.OnRelationshipChanged -= HandleRelationshipChanged;
                _factionService.OnMembershipChanged -= HandleMembershipChanged;
                _factionService.OnDiplomaticEvent -= HandleDiplomaticEvent;
            }
        }

        /// <summary>
        /// Display faction information in the panel
        /// </summary>
        public void DisplayFaction(FactionResponseDTO faction)
        {
            if (faction == null)
            {
                ClearDisplay();
                return;
            }

            _currentFaction = faction;
            UpdateFactionDisplay();
            OnFactionSelected?.Invoke(faction);
        }

        /// <summary>
        /// Load and display faction by ID
        /// </summary>
        public void LoadFaction(int factionId)
        {
            if (_factionService == null)
            {
                Debug.LogError("[FactionPanel] FactionService not found!");
                return;
            }

            _factionService.GetFaction(factionId, (success, faction) =>
            {
                if (success && faction != null)
                {
                    DisplayFaction(faction);
                }
                else
                {
                    Debug.LogError($"[FactionPanel] Failed to load faction {factionId}");
                    ClearDisplay();
                }
            });
        }

        private void UpdateFactionDisplay()
        {
            if (_currentFaction == null) return;

            // Basic faction info
            SetTextSafe(factionNameText, _currentFaction.Name);
            SetTextSafe(factionTypeText, _currentFaction.FactionType.ToString());
            SetTextSafe(alignmentText, _currentFaction.FactionAlignment?.ToString() ?? "Unaligned");
            SetTextSafe(descriptionText, _currentFaction.Description);

            // Faction stats
            UpdateStatsDisplay();

            // Leadership
            UpdateLeadershipDisplay();

            // Resources
            UpdateResourcesDisplay();

            // Members
            UpdateMembersDisplay();

            // Relationships
            UpdateRelationshipsDisplay();

            // Goals
            UpdateGoalsDisplay();

            // Recent activity
            UpdateRecentActivityDisplay();

            // Enable action buttons
            SetButtonsInteractable(true);
        }

        private void UpdateStatsDisplay()
        {
            // Influence
            SetTextSafe(influenceText, $"Influence: {_currentFaction.Influence:F1}%");
            SetSliderValue(influenceSlider, _currentFaction.Influence, 100);

            // Power
            SetTextSafe(powerText, $"Power: {_currentFaction.Power:F1}");
            SetSliderValue(powerSlider, _currentFaction.Power, 10); // Assuming max power of 10

            // Wealth
            SetTextSafe(wealthText, $"Wealth: {_currentFaction.Wealth:F0} gold");
            SetSliderValue(wealthSlider, _currentFaction.Wealth, 10000); // Assuming max wealth for display

            // Reputation
            SetTextSafe(reputationText, $"Reputation: {_currentFaction.Reputation:F1}");
        }

        private void UpdateLeadershipDisplay()
        {
            if (_currentFaction.LeaderId.HasValue)
            {
                SetTextSafe(leaderText, $"Leader ID: {_currentFaction.LeaderId.Value}");
                if (leaderButton != null) leaderButton.interactable = true;
            }
            else
            {
                SetTextSafe(leaderText, "No Leader");
                if (leaderButton != null) leaderButton.interactable = false;
            }

            if (_currentFaction.HeadquartersId.HasValue)
            {
                SetTextSafe(headquartersText, $"HQ ID: {_currentFaction.HeadquartersId.Value}");
                if (headquartersButton != null) headquartersButton.interactable = true;
            }
            else
            {
                SetTextSafe(headquartersText, "No Headquarters");
                if (headquartersButton != null) headquartersButton.interactable = false;
            }
        }

        private void UpdateResourcesDisplay()
        {
            ClearResourceItems();

            if (_currentFaction.Resources != null)
            {
                SetTextSafe(goldText, $"Gold: {_currentFaction.Resources.Gold:F0}");

                // Display materials
                foreach (var material in _currentFaction.Resources.Materials)
                {
                    CreateResourceItem($"{material.Key}: {material.Value:F0}");
                }

                // Display special resources
                foreach (var resource in _currentFaction.Resources.SpecialResources)
                {
                    CreateResourceItem($"{resource.Key}: {resource.Value:F0}", true);
                }
            }
            else
            {
                SetTextSafe(goldText, "Gold: 0");
            }
        }

        private void UpdateMembersDisplay()
        {
            ClearMemberItems();

            if (_currentFaction.State?.Statistics != null)
            {
                int memberCount = _currentFaction.State.Statistics.MembersCount;
                SetTextSafe(memberCountText, $"Members: {memberCount}");

                // Load and display a few sample members
                LoadSampleMembers();
            }
            else
            {
                SetTextSafe(memberCountText, "Members: 0");
            }
        }

        private void UpdateRelationshipsDisplay()
        {
            ClearRelationshipItems();

            if (_currentFaction.Relationships != null)
            {
                // Display allies
                foreach (var ally in _currentFaction.Relationships.Allies)
                {
                    CreateRelationshipItem(ally, "Allied", Color.green);
                }

                // Display enemies
                foreach (var enemy in _currentFaction.Relationships.Enemies)
                {
                    CreateRelationshipItem(enemy, "Enemy", Color.red);
                }

                // Display neutral factions
                foreach (var neutral in _currentFaction.Relationships.Neutral)
                {
                    CreateRelationshipItem(neutral, "Neutral", Color.gray);
                }
            }
        }

        private void UpdateGoalsDisplay()
        {
            ClearGoalItems();

            if (_currentFaction.Goals != null)
            {
                // Current goals
                foreach (var goal in _currentFaction.Goals.Current)
                {
                    CreateGoalItem(goal, currentGoalsContainer, Color.yellow);
                }

                // Completed goals
                foreach (var goal in _currentFaction.Goals.Completed)
                {
                    CreateGoalItem(goal, completedGoalsContainer, Color.green);
                }
            }
        }

        private void UpdateRecentActivityDisplay()
        {
            ClearEventItems();

            if (_currentFaction.State?.RecentEvents != null)
            {
                foreach (var eventText in _currentFaction.State.RecentEvents)
                {
                    CreateEventItem(eventText);
                }
            }
        }

        private void CreateResourceItem(string text, bool isSpecial = false)
        {
            if (resourcesContainer == null || resourceItemPrefab == null) return;

            GameObject item = Instantiate(resourceItemPrefab, resourcesContainer);
            _resourceItems.Add(item);

            var textComponent = item.GetComponentInChildren<TextMeshProUGUI>();
            if (textComponent != null)
            {
                textComponent.text = text;
                if (isSpecial)
                    textComponent.color = Color.cyan; // Highlight special resources
            }
        }

        private void CreateRelationshipItem(string factionName, string relationshipType, Color color)
        {
            if (relationshipsContainer == null || relationshipItemPrefab == null) return;

            GameObject item = Instantiate(relationshipItemPrefab, relationshipsContainer);
            _relationshipItems.Add(item);

            var textComponent = item.GetComponentInChildren<TextMeshProUGUI>();
            if (textComponent != null)
            {
                textComponent.text = $"{factionName} ({relationshipType})";
                textComponent.color = color;
            }
        }

        private void CreateGoalItem(string goal, Transform container, Color color)
        {
            if (container == null || goalItemPrefab == null) return;

            GameObject item = Instantiate(goalItemPrefab, container);
            _goalItems.Add(item);

            var textComponent = item.GetComponentInChildren<TextMeshProUGUI>();
            if (textComponent != null)
            {
                textComponent.text = goal;
                textComponent.color = color;
            }
        }

        private void CreateEventItem(string eventText)
        {
            if (recentEventsContainer == null || eventItemPrefab == null) return;

            GameObject item = Instantiate(eventItemPrefab, recentEventsContainer);
            _eventItems.Add(item);

            var textComponent = item.GetComponentInChildren<TextMeshProUGUI>();
            if (textComponent != null)
            {
                textComponent.text = eventText;
            }
        }

        private void LoadSampleMembers()
        {
            if (_factionService == null || _currentFaction == null) return;

            _factionService.GetFactionMembers(_currentFaction.Id, (success, members) =>
            {
                if (success && members != null)
                {
                    // Display first few members
                    int displayCount = Mathf.Min(5, members.Count);
                    for (int i = 0; i < displayCount; i++)
                    {
                        CreateMemberItem(members[i]);
                    }
                }
            });
        }

        private void CreateMemberItem(FactionMembershipResponseDTO member)
        {
            if (membersContainer == null || memberItemPrefab == null) return;

            GameObject item = Instantiate(memberItemPrefab, membersContainer);
            _memberItems.Add(item);

            var textComponent = item.GetComponentInChildren<TextMeshProUGUI>();
            if (textComponent != null)
            {
                textComponent.text = $"Character {member.CharacterId} - {member.Role} (Rank {member.Rank})";
            }
        }

        private void LoadAllMembers()
        {
            // TODO: Open members management panel
            Debug.Log("[FactionPanel] Opening all members view");
        }

        private void LoadAllRelationships()
        {
            // TODO: Open relationships management panel
            Debug.Log("[FactionPanel] Opening relationships management");
        }

        private void OpenPoliciesPanel()
        {
            // TODO: Open policies management panel
            Debug.Log("[FactionPanel] Opening policies management");
        }

        private void ClearDisplay()
        {
            _currentFaction = null;

            // Clear text fields
            SetTextSafe(factionNameText, "No Faction Selected");
            SetTextSafe(factionTypeText, "");
            SetTextSafe(alignmentText, "");
            SetTextSafe(descriptionText, "");
            SetTextSafe(influenceText, "");
            SetTextSafe(powerText, "");
            SetTextSafe(wealthText, "");
            SetTextSafe(reputationText, "");
            SetTextSafe(leaderText, "");
            SetTextSafe(headquartersText, "");
            SetTextSafe(memberCountText, "");
            SetTextSafe(goldText, "");

            // Clear sliders
            SetSliderValue(influenceSlider, 0, 1);
            SetSliderValue(powerSlider, 0, 1);
            SetSliderValue(wealthSlider, 0, 1);

            // Clear all item lists
            ClearAllItems();

            // Disable action buttons
            SetButtonsInteractable(false);
        }

        private void ClearAllItems()
        {
            ClearMemberItems();
            ClearRelationshipItems();
            ClearResourceItems();
            ClearGoalItems();
            ClearEventItems();
        }

        private void ClearMemberItems()
        {
            foreach (var item in _memberItems)
            {
                if (item != null) DestroyImmediate(item);
            }
            _memberItems.Clear();
        }

        private void ClearRelationshipItems()
        {
            foreach (var item in _relationshipItems)
            {
                if (item != null) DestroyImmediate(item);
            }
            _relationshipItems.Clear();
        }

        private void ClearResourceItems()
        {
            foreach (var item in _resourceItems)
            {
                if (item != null) DestroyImmediate(item);
            }
            _resourceItems.Clear();
        }

        private void ClearGoalItems()
        {
            foreach (var item in _goalItems)
            {
                if (item != null) DestroyImmediate(item);
            }
            _goalItems.Clear();
        }

        private void ClearEventItems()
        {
            foreach (var item in _eventItems)
            {
                if (item != null) DestroyImmediate(item);
            }
            _eventItems.Clear();
        }

        private void SetButtonsInteractable(bool interactable)
        {
            if (editFactionButton != null) editFactionButton.interactable = interactable;
            if (diplomaticActionsButton != null) diplomaticActionsButton.interactable = interactable;
            if (territoryButton != null) territoryButton.interactable = interactable;
            if (financeButton != null) financeButton.interactable = interactable;
            if (viewAllMembersButton != null) viewAllMembersButton.interactable = interactable;
            if (manageRelationshipsButton != null) manageRelationshipsButton.interactable = interactable;
            if (managePoliciesButton != null) managePoliciesButton.interactable = interactable;
        }

        #region Event Handlers

        private void HandleFactionUpdated(FactionResponseDTO faction)
        {
            if (_currentFaction != null && faction.Id == _currentFaction.Id)
            {
                DisplayFaction(faction);
            }
        }

        private void HandleRelationshipChanged(FactionRelationshipResponseDTO relationship)
        {
            if (_currentFaction != null && 
                (relationship.FactionId == _currentFaction.Id || relationship.OtherFactionId == _currentFaction.Id))
            {
                // Refresh relationships display
                UpdateRelationshipsDisplay();
                ShowNotification($"Relationship changed with faction {relationship.OtherFactionId}", NotificationType.Info);
            }
        }

        private void HandleMembershipChanged(FactionMembershipResponseDTO membership)
        {
            if (_currentFaction != null && membership.FactionId == _currentFaction.Id)
            {
                // Refresh members display
                UpdateMembersDisplay();
                ShowNotification($"Membership changed for character {membership.CharacterId}", NotificationType.Info);
            }
        }

        private void HandleDiplomaticEvent(int faction1Id, int faction2Id, string eventType)
        {
            if (_currentFaction != null && (faction1Id == _currentFaction.Id || faction2Id == _currentFaction.Id))
            {
                // Refresh the display to show updated relationships
                LoadFaction(_currentFaction.Id);
                ShowNotification($"Diplomatic event: {eventType}", NotificationType.Warning);
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

        private void ShowNotification(string message, NotificationType type)
        {
            // TODO: Implement notification system
            Debug.Log($"[FactionPanel] {type}: {message}");
        }

        #endregion
    }
} 