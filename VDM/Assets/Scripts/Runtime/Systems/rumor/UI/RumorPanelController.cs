using System.Collections.Generic;
using System.Linq;
using System;
using TMPro;
using UnityEngine.UI;
using UnityEngine;
using VDM.Systems.Events.Integration;
using VDM.DTOs.Common;
using VDM.Systems.Rumor.Services;
using VDM.Systems.Events.Models;
using VDM.Systems.Rumor.Models;


namespace VDM.Systems.Rumor.Ui
{
    /// <summary>
    /// Controller for the rumor management UI panel
    /// </summary>
    public class RumorPanelController : MonoBehaviour
    {
        [Header("Panel References")]
        [SerializeField] private GameObject rumorListPanel;
        [SerializeField] private GameObject rumorDetailPanel;
        [SerializeField] private GameObject rumorCreationPanel;
        [SerializeField] private GameObject rumorSpreadPanel;

        [Header("List Panel Components")]
        [SerializeField] private Transform rumorListContainer;
        [SerializeField] private GameObject rumorListItemPrefab;
        [SerializeField] private TMP_InputField searchInput;
        [SerializeField] private TMP_Dropdown categoryFilter;
        [SerializeField] private TMP_Dropdown severityFilter;
        [SerializeField] private Button refreshButton;
        [SerializeField] private Button createRumorButton;

        [Header("Detail Panel Components")]
        [SerializeField] private TextMeshProUGUI detailTitle;
        [SerializeField] private TextMeshProUGUI detailContent;
        [SerializeField] private TextMeshProUGUI detailOriginator;
        [SerializeField] private TextMeshProUGUI detailCategories;
        [SerializeField] private TextMeshProUGUI detailSeverity;
        [SerializeField] private TextMeshProUGUI detailTruthValue;
        [SerializeField] private TextMeshProUGUI detailCreatedAt;
        [SerializeField] private Transform variantListContainer;
        [SerializeField] private GameObject variantListItemPrefab;
        [SerializeField] private Transform spreadListContainer;
        [SerializeField] private GameObject spreadListItemPrefab;
        [SerializeField] private Button spreadRumorButton;
        [SerializeField] private Button deleteRumorButton;
        [SerializeField] private Button backToListButton;

        [Header("Creation Panel Components")]
        [SerializeField] private TMP_InputField creationContentInput;
        [SerializeField] private TMP_InputField creationOriginatorInput;
        [SerializeField] private TMP_Dropdown creationCategoryDropdown;
        [SerializeField] private TMP_Dropdown creationSeverityDropdown;
        [SerializeField] private Slider creationTruthSlider;
        [SerializeField] private TextMeshProUGUI creationTruthLabel;
        [SerializeField] private Button createConfirmButton;
        [SerializeField] private Button createCancelButton;

        [Header("Spread Panel Components")]
        [SerializeField] private TMP_InputField spreadFromEntityInput;
        [SerializeField] private TMP_InputField spreadToEntityInput;
        [SerializeField] private Slider spreadMutationSlider;
        [SerializeField] private TextMeshProUGUI spreadMutationLabel;
        [SerializeField] private Slider spreadRelationshipSlider;
        [SerializeField] private TextMeshProUGUI spreadRelationshipLabel;
        [SerializeField] private Button spreadConfirmButton;
        [SerializeField] private Button spreadCancelButton;

        private RumorService rumorService;
        private List<RumorDTO> currentRumors = new List<RumorDTO>();
        private RumorDTO selectedRumor;
        private string currentSearchTerm = "";
        private RumorCategory? currentCategoryFilter;
        private RumorSeverity? currentSeverityFilter;

        private void Start()
        {
            InitializeUI();
            SetupEventListeners();
            ShowListPanel();
        }

        private void InitializeUI()
        {
            // Initialize category filter dropdown
            var categoryOptions = new List<string> { "All Categories" };
            categoryOptions.AddRange(Enum.GetNames(typeof(RumorCategory)));
            categoryFilter.ClearOptions();
            categoryFilter.AddOptions(categoryOptions);

            // Initialize severity filter dropdown
            var severityOptions = new List<string> { "All Severities" };
            severityOptions.AddRange(Enum.GetNames(typeof(RumorSeverity)));
            severityFilter.ClearOptions();
            severityFilter.AddOptions(severityOptions);

            // Initialize creation dropdowns
            var creationCategoryOptions = Enum.GetNames(typeof(RumorCategory)).ToList();
            creationCategoryDropdown.ClearOptions();
            creationCategoryDropdown.AddOptions(creationCategoryOptions);

            var creationSeverityOptions = Enum.GetNames(typeof(RumorSeverity)).ToList();
            creationSeverityDropdown.ClearOptions();
            creationSeverityDropdown.AddOptions(creationSeverityOptions);

            // Initialize sliders
            creationTruthSlider.value = 0.5f;
            spreadMutationSlider.value = 0.2f;
            spreadRelationshipSlider.value = 0.0f;

            UpdateSliderLabels();
        }

        private void SetupEventListeners()
        {
            // List panel events
            refreshButton.onClick.AddListener(RefreshRumorList);
            createRumorButton.onClick.AddListener(ShowCreationPanel);
            searchInput.onValueChanged.AddListener(OnSearchChanged);
            categoryFilter.onValueChanged.AddListener(OnCategoryFilterChanged);
            severityFilter.onValueChanged.AddListener(OnSeverityFilterChanged);

            // Detail panel events
            spreadRumorButton.onClick.AddListener(ShowSpreadPanel);
            deleteRumorButton.onClick.AddListener(DeleteSelectedRumor);
            backToListButton.onClick.AddListener(ShowListPanel);

            // Creation panel events
            createConfirmButton.onClick.AddListener(CreateRumor);
            createCancelButton.onClick.AddListener(ShowListPanel);
            creationTruthSlider.onValueChanged.AddListener(OnTruthSliderChanged);

            // Spread panel events
            spreadConfirmButton.onClick.AddListener(SpreadRumor);
            spreadCancelButton.onClick.AddListener(ShowDetailPanel);
            spreadMutationSlider.onValueChanged.AddListener(OnMutationSliderChanged);
            spreadRelationshipSlider.onValueChanged.AddListener(OnRelationshipSliderChanged);
        }

        public void Initialize(RumorService service)
        {
            rumorService = service;
            RefreshRumorList();
        }

        #region Panel Management

        private void ShowListPanel()
        {
            rumorListPanel.SetActive(true);
            rumorDetailPanel.SetActive(false);
            rumorCreationPanel.SetActive(false);
            rumorSpreadPanel.SetActive(false);
        }

        private void ShowDetailPanel()
        {
            rumorListPanel.SetActive(false);
            rumorDetailPanel.SetActive(true);
            rumorCreationPanel.SetActive(false);
            rumorSpreadPanel.SetActive(false);
        }

        private void ShowCreationPanel()
        {
            rumorListPanel.SetActive(false);
            rumorDetailPanel.SetActive(false);
            rumorCreationPanel.SetActive(true);
            rumorSpreadPanel.SetActive(false);

            // Reset creation form
            creationContentInput.text = "";
            creationOriginatorInput.text = "";
            creationCategoryDropdown.value = 0;
            creationSeverityDropdown.value = 1; // Default to Minor
            creationTruthSlider.value = 0.5f;
            UpdateSliderLabels();
        }

        private void ShowSpreadPanel()
        {
            rumorListPanel.SetActive(false);
            rumorDetailPanel.SetActive(false);
            rumorCreationPanel.SetActive(false);
            rumorSpreadPanel.SetActive(true);

            // Reset spread form
            spreadFromEntityInput.text = "";
            spreadToEntityInput.text = "";
            spreadMutationSlider.value = 0.2f;
            spreadRelationshipSlider.value = 0.0f;
            UpdateSliderLabels();
        }

        #endregion

        #region Rumor List Management

        private async void RefreshRumorList()
        {
            if (rumorService == null) return;

            try
            {
                var response = await rumorService.ListRumorsAsync(
                    category: currentCategoryFilter?.ToString().ToLower(),
                    limit: 50
                );

                currentRumors = response?.Rumors ?? new List<RumorDTO>();
                UpdateRumorListDisplay();
            }
            catch (Exception ex)
            {
                Debug.LogError($"[RumorPanelController] Failed to refresh rumor list: {ex.Message}");
            }
        }

        private void UpdateRumorListDisplay()
        {
            // Clear existing items
            foreach (Transform child in rumorListContainer)
            {
                Destroy(child.gameObject);
            }

            // Filter rumors based on current filters
            var filteredRumors = FilterRumors(currentRumors);

            // Create list items
            foreach (var rumor in filteredRumors)
            {
                var listItem = Instantiate(rumorListItemPrefab, rumorListContainer);
                var controller = listItem.GetComponent<RumorListItemController>();
                if (controller != null)
                {
                    controller.Initialize(rumor, OnRumorSelected);
                }
            }
        }

        private List<RumorDTO> FilterRumors(List<RumorDTO> rumors)
        {
            var filtered = rumors.AsEnumerable();

            // Apply search filter
            if (!string.IsNullOrEmpty(currentSearchTerm))
            {
                filtered = filtered.Where(r => 
                    r.OriginalContent.ToLower().Contains(currentSearchTerm.ToLower()) ||
                    r.Categories.Any(c => c.ToLower().Contains(currentSearchTerm.ToLower()))
                );
            }

            // Apply category filter
            if (currentCategoryFilter.HasValue)
            {
                var categoryString = currentCategoryFilter.Value.ToString().ToLower();
                filtered = filtered.Where(r => r.Categories.Any(c => c.ToLower() == categoryString));
            }

            // Apply severity filter
            if (currentSeverityFilter.HasValue)
            {
                var severityString = currentSeverityFilter.Value.ToString().ToLower();
                filtered = filtered.Where(r => r.Severity.ToLower() == severityString);
            }

            return filtered.ToList();
        }

        private void OnRumorSelected(RumorDTO rumor)
        {
            selectedRumor = rumor;
            UpdateDetailPanel();
            ShowDetailPanel();
        }

        #endregion

        #region Detail Panel Management

        private void UpdateDetailPanel()
        {
            if (selectedRumor == null) return;

            detailTitle.text = $"Rumor: {selectedRumor.Id.Substring(0, 8)}...";
            detailContent.text = selectedRumor.OriginalContent;
            detailOriginator.text = $"Originator: {selectedRumor.OriginatorId}";
            detailCategories.text = $"Categories: {string.Join(", ", selectedRumor.Categories)}";
            detailSeverity.text = $"Severity: {selectedRumor.Severity}";
            detailTruthValue.text = $"Truth Value: {selectedRumor.TruthValue:P0}";
            detailCreatedAt.text = $"Created: {selectedRumor.CreatedAt}";

            UpdateVariantsList();
            UpdateSpreadList();
        }

        private void UpdateVariantsList()
        {
            // Clear existing items
            foreach (Transform child in variantListContainer)
            {
                Destroy(child.gameObject);
            }

            // Create variant items
            foreach (var variant in selectedRumor.Variants)
            {
                var listItem = Instantiate(variantListItemPrefab, variantListContainer);
                var controller = listItem.GetComponent<RumorVariantItemController>();
                if (controller != null)
                {
                    controller.Initialize(variant);
                }
            }
        }

        private void UpdateSpreadList()
        {
            // Clear existing items
            foreach (Transform child in spreadListContainer)
            {
                Destroy(child.gameObject);
            }

            // Create spread items
            foreach (var spread in selectedRumor.Spread)
            {
                var listItem = Instantiate(spreadListItemPrefab, spreadListContainer);
                var controller = listItem.GetComponent<RumorSpreadItemController>();
                if (controller != null)
                {
                    controller.Initialize(spread);
                }
            }
        }

        #endregion

        #region Rumor Operations

        private async void CreateRumor()
        {
            if (rumorService == null) return;

            try
            {
                var request = new CreateRumorRequestDTO
                {
                    OriginatorId = creationOriginatorInput.text,
                    Content = creationContentInput.text,
                    Categories = new List<string> { Enum.GetNames(typeof(RumorCategory))[creationCategoryDropdown.value].ToLower() },
                    Severity = Enum.GetNames(typeof(RumorSeverity))[creationSeverityDropdown.value].ToLower(),
                    TruthValue = creationTruthSlider.value
                };

                var createdRumor = await rumorService.CreateRumorAsync(request);
                
                if (createdRumor != null)
                {
                    Debug.Log($"[RumorPanelController] Created rumor: {createdRumor.Id}");
                    
                    // Emit event
                    EventBus.Instance.Publish(new RumorCreatedEvent
                    {
                        RumorId = createdRumor.Id,
                        Content = createdRumor.OriginalContent,
                        OriginatorId = createdRumor.OriginatorId
                    });

                    RefreshRumorList();
                    ShowListPanel();
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"[RumorPanelController] Failed to create rumor: {ex.Message}");
            }
        }

        private async void SpreadRumor()
        {
            if (rumorService == null || selectedRumor == null) return;

            try
            {
                var request = new SpreadRumorRequestDTO
                {
                    RumorId = selectedRumor.Id,
                    FromEntityId = spreadFromEntityInput.text,
                    ToEntityId = spreadToEntityInput.text,
                    MutationProbability = spreadMutationSlider.value,
                    RelationshipFactor = spreadRelationshipSlider.value
                };

                var result = await rumorService.SpreadRumorAsync(request);
                
                if (result?.Success == true)
                {
                    Debug.Log($"[RumorPanelController] Spread rumor successfully");
                    
                    // Emit event
                    EventBus.Instance.Publish(new RumorSpreadEvent
                    {
                        RumorId = selectedRumor.Id,
                        FromEntityId = request.FromEntityId,
                        ToEntityId = request.ToEntityId
                    });

                    // Refresh the selected rumor to show updated spread
                    selectedRumor = await rumorService.GetRumorAsync(selectedRumor.Id);
                    UpdateDetailPanel();
                    ShowDetailPanel();
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"[RumorPanelController] Failed to spread rumor: {ex.Message}");
            }
        }

        private async void DeleteSelectedRumor()
        {
            if (rumorService == null || selectedRumor == null) return;

            try
            {
                var result = await rumorService.DeleteRumorAsync(selectedRumor.Id);
                
                if (result?.Success == true)
                {
                    Debug.Log($"[RumorPanelController] Deleted rumor: {selectedRumor.Id}");
                    
                    // Emit event
                    EventBus.Instance.Publish(new RumorDeletedEvent
                    {
                        RumorId = selectedRumor.Id
                    });

                    selectedRumor = null;
                    RefreshRumorList();
                    ShowListPanel();
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"[RumorPanelController] Failed to delete rumor: {ex.Message}");
            }
        }

        #endregion

        #region Event Handlers

        private void OnSearchChanged(string searchTerm)
        {
            currentSearchTerm = searchTerm;
            UpdateRumorListDisplay();
        }

        private void OnCategoryFilterChanged(int index)
        {
            if (index == 0)
            {
                currentCategoryFilter = null;
            }
            else
            {
                var categoryName = Enum.GetNames(typeof(RumorCategory))[index - 1];
                currentCategoryFilter = (RumorCategory)Enum.Parse(typeof(RumorCategory), categoryName);
            }
            UpdateRumorListDisplay();
        }

        private void OnSeverityFilterChanged(int index)
        {
            if (index == 0)
            {
                currentSeverityFilter = null;
            }
            else
            {
                var severityName = Enum.GetNames(typeof(RumorSeverity))[index - 1];
                currentSeverityFilter = (RumorSeverity)Enum.Parse(typeof(RumorSeverity), severityName);
            }
            UpdateRumorListDisplay();
        }

        private void OnTruthSliderChanged(float value)
        {
            UpdateSliderLabels();
        }

        private void OnMutationSliderChanged(float value)
        {
            UpdateSliderLabels();
        }

        private void OnRelationshipSliderChanged(float value)
        {
            UpdateSliderLabels();
        }

        private void UpdateSliderLabels()
        {
            if (creationTruthLabel != null)
                creationTruthLabel.text = $"Truth Value: {creationTruthSlider.value:P0}";
            
            if (spreadMutationLabel != null)
                spreadMutationLabel.text = $"Mutation Chance: {spreadMutationSlider.value:P0}";
            
            if (spreadRelationshipLabel != null)
                spreadRelationshipLabel.text = $"Relationship: {spreadRelationshipSlider.value:+0.0;-0.0;0.0}";
        }

        #endregion
    }

    #region List Item Controllers

    /// <summary>
    /// Controller for individual rumor list items
    /// </summary>
    public class RumorListItemController : MonoBehaviour
    {
        [SerializeField] private TextMeshProUGUI contentText;
        [SerializeField] private TextMeshProUGUI categoriesText;
        [SerializeField] private TextMeshProUGUI severityText;
        [SerializeField] private TextMeshProUGUI spreadCountText;
        [SerializeField] private Button selectButton;

        private RumorDTO rumor;
        private Action<RumorDTO> onSelected;

        public void Initialize(RumorDTO rumorData, Action<RumorDTO> onSelectedCallback)
        {
            rumor = rumorData;
            onSelected = onSelectedCallback;

            contentText.text = rumor.OriginalContent.Length > 50 
                ? rumor.OriginalContent.Substring(0, 50) + "..." 
                : rumor.OriginalContent;
            
            categoriesText.text = string.Join(", ", rumor.Categories);
            severityText.text = rumor.Severity;
            spreadCountText.text = $"Spread: {rumor.Spread?.Count ?? 0}";

            selectButton.onClick.AddListener(() => onSelected?.Invoke(rumor));
        }
    }

    /// <summary>
    /// Controller for rumor variant items
    /// </summary>
    public class RumorVariantItemController : MonoBehaviour
    {
        [SerializeField] private TextMeshProUGUI contentText;
        [SerializeField] private TextMeshProUGUI entityText;
        [SerializeField] private TextMeshProUGUI createdAtText;

        public void Initialize(RumorVariantDTO variant)
        {
            contentText.text = variant.Content.Length > 100 
                ? variant.Content.Substring(0, 100) + "..." 
                : variant.Content;
            
            entityText.text = $"By: {variant.EntityId}";
            createdAtText.text = variant.CreatedAt;
        }
    }

    /// <summary>
    /// Controller for rumor spread items
    /// </summary>
    public class RumorSpreadItemController : MonoBehaviour
    {
        [SerializeField] private TextMeshProUGUI entityText;
        [SerializeField] private TextMeshProUGUI believabilityText;
        [SerializeField] private TextMeshProUGUI heardFromText;
        [SerializeField] private TextMeshProUGUI heardAtText;

        public void Initialize(RumorSpreadDTO spread)
        {
            entityText.text = spread.EntityId;
            believabilityText.text = $"Believes: {spread.Believability:P0}";
            heardFromText.text = string.IsNullOrEmpty(spread.HeardFromEntityId) 
                ? "Original" 
                : $"From: {spread.HeardFromEntityId}";
            heardAtText.text = spread.HeardAt;
        }
    }

    #endregion

    #region Events

    public class RumorCreatedEvent : IEvent
    {
        public string EventId { get; } = Guid.NewGuid().ToString();
        public string EventType => "rumor.created";
        public DateTime Timestamp { get; } = DateTime.UtcNow;
        public string Source => "RumorPanelController";
        public EventPriority Priority => EventPriority.Normal;

        public string RumorId { get; set; }
        public string Content { get; set; }
        public string OriginatorId { get; set; }
    }

    public class RumorSpreadEvent : IEvent
    {
        public string EventId { get; } = Guid.NewGuid().ToString();
        public string EventType => "rumor.spread";
        public DateTime Timestamp { get; } = DateTime.UtcNow;
        public string Source => "RumorPanelController";
        public EventPriority Priority => EventPriority.Normal;

        public string RumorId { get; set; }
        public string FromEntityId { get; set; }
        public string ToEntityId { get; set; }
    }

    public class RumorDeletedEvent : IEvent
    {
        public string EventId { get; } = Guid.NewGuid().ToString();
        public string EventType => "rumor.deleted";
        public DateTime Timestamp { get; } = DateTime.UtcNow;
        public string Source => "RumorPanelController";
        public EventPriority Priority => EventPriority.Normal;

        public string RumorId { get; set; }
    }

    #endregion
} 