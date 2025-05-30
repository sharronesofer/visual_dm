using System.Collections.Generic;
using System.Linq;
using System;
using TMPro;
using UnityEngine.UI;
using UnityEngine;
using VDM.Runtime.Memory.Models;
using VDM.Runtime.Memory.Services;
using VDM.Runtime.UI.Core;


namespace VDM.Runtime.Memory.UI
{
    /// <summary>
    /// UI controller for memory management panel
    /// </summary>
    public class MemoryPanelController : UIController
    {
        [Header("Memory Panel Components")]
        [SerializeField] private GameObject memoryListPanel;
        [SerializeField] private GameObject memoryDetailPanel;
        [SerializeField] private GameObject memoryCreatePanel;
        
        [Header("Memory List")]
        [SerializeField] private Transform memoryListContainer;
        [SerializeField] private GameObject memoryItemPrefab;
        [SerializeField] private TMP_InputField searchInput;
        [SerializeField] private TMP_InputField npcIdInput;
        [SerializeField] private TMP_Dropdown importanceFilter;
        [SerializeField] private TMP_InputField tagFilterInput;
        [SerializeField] private Button loadMemoriesButton;
        [SerializeField] private Button createMemoryButton;
        [SerializeField] private Button refreshButton;
        
        [Header("Memory Detail")]
        [SerializeField] private TextMeshProUGUI memoryIdText;
        [SerializeField] private TextMeshProUGUI memoryContentText;
        [SerializeField] private TextMeshProUGUI memoryImportanceText;
        [SerializeField] private TextMeshProUGUI memoryCreatedAtText;
        [SerializeField] private TextMeshProUGUI memoryLastRecalledText;
        [SerializeField] private TextMeshProUGUI memoryRecallCountText;
        [SerializeField] private Transform memoryTagsContainer;
        [SerializeField] private Transform relatedEntitiesContainer;
        [SerializeField] private Button recallMemoryButton;
        [SerializeField] private Button reinforceMemoryButton;
        [SerializeField] private Button forgetMemoryButton;
        [SerializeField] private Button backToListButton;
        
        [Header("Memory Creation")]
        [SerializeField] private TMP_InputField createNpcIdInput;
        [SerializeField] private TMP_InputField createContentInput;
        [SerializeField] private Slider createImportanceSlider;
        [SerializeField] private TextMeshProUGUI createImportanceLabel;
        [SerializeField] private TMP_InputField createTagsInput;
        [SerializeField] private TMP_InputField createRelatedNpcsInput;
        [SerializeField] private TMP_InputField createRelatedFactionsInput;
        [SerializeField] private TMP_InputField createRelatedLocationsInput;
        [SerializeField] private Button saveMemoryButton;
        [SerializeField] private Button cancelCreateButton;
        
        [Header("Memory Operations")]
        [SerializeField] private GameObject operationsPanel;
        [SerializeField] private TMP_InputField recallContextInput;
        [SerializeField] private Slider reinforceAmountSlider;
        [SerializeField] private TextMeshProUGUI reinforceAmountLabel;
        [SerializeField] private TMP_InputField forgetReasonInput;

        private MemoryService _memoryService;
        private List<MemoryDTO> _memories = new();
        private List<MemoryDTO> _filteredMemories = new();
        private MemoryDTO _selectedMemory;
        private string _currentNpcId;
        private MemorySummaryDTO _currentSummary;

        public event Action<MemoryDTO> OnMemorySelected;
        public event Action<MemoryDTO> OnMemoryCreated;
        public event Action<MemoryDTO> OnMemoryRecalled;
        public event Action<MemoryDTO> OnMemoryReinforced;
        public event Action<string> OnMemoryForgotten;

        protected override void Awake()
        {
            base.Awake();
            InitializeComponents();
        }

        private void InitializeComponents()
        {
            // Initialize memory service
            var httpClient = FindObjectOfType<HttpClient>();
            _memoryService = new MemoryService(httpClient);

            // Setup button listeners
            if (loadMemoriesButton) loadMemoriesButton.onClick.AddListener(LoadMemoriesForNpc);
            if (createMemoryButton) createMemoryButton.onClick.AddListener(ShowCreatePanel);
            if (refreshButton) refreshButton.onClick.AddListener(RefreshMemories);
            if (recallMemoryButton) recallMemoryButton.onClick.AddListener(RecallSelectedMemory);
            if (reinforceMemoryButton) reinforceMemoryButton.onClick.AddListener(ReinforceSelectedMemory);
            if (forgetMemoryButton) forgetMemoryButton.onClick.AddListener(ForgetSelectedMemory);
            if (backToListButton) backToListButton.onClick.AddListener(ShowListPanel);
            if (saveMemoryButton) saveMemoryButton.onClick.AddListener(SaveMemory);
            if (cancelCreateButton) cancelCreateButton.onClick.AddListener(ShowListPanel);

            // Setup input listeners
            if (searchInput) searchInput.onValueChanged.AddListener(OnSearchChanged);
            if (importanceFilter) importanceFilter.onValueChanged.AddListener(OnImportanceFilterChanged);
            if (tagFilterInput) tagFilterInput.onValueChanged.AddListener(OnTagFilterChanged);
            if (createImportanceSlider) createImportanceSlider.onValueChanged.AddListener(OnCreateImportanceChanged);
            if (reinforceAmountSlider) reinforceAmountSlider.onValueChanged.AddListener(OnReinforceAmountChanged);

            // Initialize dropdowns and sliders
            InitializeFiltersAndSliders();

            // Show list panel by default
            ShowListPanel();
        }

        private void InitializeFiltersAndSliders()
        {
            // Initialize importance filter
            if (importanceFilter)
            {
                importanceFilter.ClearOptions();
                var options = new List<string> { "All Importance", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10" };
                importanceFilter.AddOptions(options);
            }

            // Initialize sliders
            if (createImportanceSlider)
            {
                createImportanceSlider.minValue = 1;
                createImportanceSlider.maxValue = 10;
                createImportanceSlider.value = 5;
            }

            if (reinforceAmountSlider)
            {
                reinforceAmountSlider.minValue = 1;
                reinforceAmountSlider.maxValue = 5;
                reinforceAmountSlider.value = 1;
            }

            UpdateSliderLabels();
        }

        public async void Initialize(string npcId = null)
        {
            if (!string.IsNullOrEmpty(npcId))
            {
                _currentNpcId = npcId;
                if (npcIdInput) npcIdInput.text = npcId;
                if (createNpcIdInput) createNpcIdInput.text = npcId;
                await LoadMemoriesForNpc();
            }
        }

        public async void LoadMemoriesForNpc()
        {
            try
            {
                var npcId = npcIdInput?.text?.Trim();
                if (string.IsNullOrEmpty(npcId))
                {
                    ShowNotification("Please enter an NPC ID", NotificationType.Warning);
                    return;
                }

                _currentNpcId = npcId;

                var response = await _memoryService.GetNpcMemoriesAsync(npcId, 100, 0);
                if (response.Success && response.Data != null)
                {
                    _memories = response.Data.Memories ?? new List<MemoryDTO>();
                    ApplyFilters();
                    UpdateMemoryList();

                    // Load summary
                    await LoadMemorySummary(npcId);

                    ShowNotification($"Loaded {_memories.Count} memories for NPC {npcId}", NotificationType.Success);
                }
                else
                {
                    ShowNotification($"Failed to load memories: {response.Message}", NotificationType.Error);
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error loading memories: {ex.Message}");
                ShowNotification("Error loading memories", NotificationType.Error);
            }
        }

        private async void LoadMemorySummary(string npcId)
        {
            try
            {
                var response = await _memoryService.GetMemorySummaryAsync(npcId);
                if (response.Success && response.Data != null)
                {
                    _currentSummary = response.Data.Summary;
                    // Update summary display if you have UI components for it
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error loading memory summary: {ex.Message}");
            }
        }

        public async void RefreshMemories()
        {
            if (!string.IsNullOrEmpty(_currentNpcId))
            {
                await LoadMemoriesForNpc();
            }
        }

        private void ApplyFilters()
        {
            _filteredMemories = _memories.ToList();

            // Apply search filter
            if (searchInput && !string.IsNullOrEmpty(searchInput.text))
            {
                var searchTerm = searchInput.text.ToLower();
                _filteredMemories = _filteredMemories.Where(m => 
                    m.Content.ToLower().Contains(searchTerm) ||
                    m.Tags.Any(tag => tag.ToLower().Contains(searchTerm))
                ).ToList();
            }

            // Apply importance filter
            if (importanceFilter && importanceFilter.value > 0)
            {
                var minImportance = importanceFilter.value;
                _filteredMemories = _filteredMemories.Where(m => m.Importance >= minImportance).ToList();
            }

            // Apply tag filter
            if (tagFilterInput && !string.IsNullOrEmpty(tagFilterInput.text))
            {
                var tagFilter = tagFilterInput.text.ToLower();
                _filteredMemories = _filteredMemories.Where(m => 
                    m.Tags.Any(tag => tag.ToLower().Contains(tagFilter))
                ).ToList();
            }

            // Sort by importance (descending) then by creation date (descending)
            _filteredMemories = _filteredMemories.OrderByDescending(m => m.Importance)
                                                 .ThenByDescending(m => m.CreatedAt)
                                                 .ToList();
        }

        private void UpdateMemoryList()
        {
            if (!memoryListContainer) return;

            // Clear existing items
            foreach (Transform child in memoryListContainer)
            {
                Destroy(child.gameObject);
            }

            // Create new items
            foreach (var memory in _filteredMemories)
            {
                CreateMemoryListItem(memory);
            }
        }

        private void CreateMemoryListItem(MemoryDTO memory)
        {
            if (!memoryItemPrefab) return;

            var item = Instantiate(memoryItemPrefab, memoryListContainer);
            var itemController = item.GetComponent<MemoryListItemController>();
            
            if (itemController)
            {
                itemController.Initialize(memory);
                itemController.OnSelected += SelectMemory;
            }
        }

        private void SelectMemory(MemoryDTO memory)
        {
            _selectedMemory = memory;
            UpdateMemoryDetail();
            ShowDetailPanel();
            OnMemorySelected?.Invoke(memory);
        }

        private void UpdateMemoryDetail()
        {
            if (_selectedMemory == null) return;

            if (memoryIdText) memoryIdText.text = $"ID: {_selectedMemory.MemoryId}";
            if (memoryContentText) memoryContentText.text = _selectedMemory.Content;
            if (memoryImportanceText) memoryImportanceText.text = $"Importance: {_selectedMemory.Importance}/10";
            if (memoryCreatedAtText) memoryCreatedAtText.text = $"Created: {_selectedMemory.CreatedAt}";
            if (memoryLastRecalledText) 
            {
                var lastRecalled = string.IsNullOrEmpty(_selectedMemory.LastRecalled) ? "Never" : _selectedMemory.LastRecalled;
                memoryLastRecalledText.text = $"Last Recalled: {lastRecalled}";
            }
            if (memoryRecallCountText) memoryRecallCountText.text = $"Recall Count: {_selectedMemory.RecallCount}";

            UpdateTagsList(_selectedMemory.Tags);
            UpdateRelatedEntitiesList(_selectedMemory);
        }

        private void UpdateTagsList(List<string> tags)
        {
            if (!memoryTagsContainer) return;

            foreach (Transform child in memoryTagsContainer)
            {
                Destroy(child.gameObject);
            }

            foreach (var tag in tags)
            {
                var tagObj = new GameObject("Tag");
                tagObj.transform.SetParent(memoryTagsContainer);
                var text = tagObj.AddComponent<TextMeshProUGUI>();
                text.text = $"#{tag}";
                text.fontSize = 12;
                text.color = Color.cyan;
            }
        }

        private void UpdateRelatedEntitiesList(MemoryDTO memory)
        {
            if (!relatedEntitiesContainer) return;

            foreach (Transform child in relatedEntitiesContainer)
            {
                Destroy(child.gameObject);
            }

            // Add related NPCs
            foreach (var npcId in memory.RelatedNpcs)
            {
                CreateRelatedEntityItem("NPC", npcId);
            }

            // Add related factions
            foreach (var factionId in memory.RelatedFactions)
            {
                CreateRelatedEntityItem("Faction", factionId);
            }

            // Add related locations
            foreach (var locationId in memory.RelatedLocations)
            {
                CreateRelatedEntityItem("Location", locationId);
            }
        }

        private void CreateRelatedEntityItem(string entityType, string entityId)
        {
            var entityObj = new GameObject($"{entityType}Entity");
            entityObj.transform.SetParent(relatedEntitiesContainer);
            var text = entityObj.AddComponent<TextMeshProUGUI>();
            text.text = $"{entityType}: {entityId}";
            text.fontSize = 12;
        }

        private void ShowListPanel()
        {
            if (memoryListPanel) memoryListPanel.SetActive(true);
            if (memoryDetailPanel) memoryDetailPanel.SetActive(false);
            if (memoryCreatePanel) memoryCreatePanel.SetActive(false);
            if (operationsPanel) operationsPanel.SetActive(false);
        }

        private void ShowDetailPanel()
        {
            if (memoryListPanel) memoryListPanel.SetActive(false);
            if (memoryDetailPanel) memoryDetailPanel.SetActive(true);
            if (memoryCreatePanel) memoryCreatePanel.SetActive(false);
            if (operationsPanel) operationsPanel.SetActive(true);
        }

        private void ShowCreatePanel()
        {
            if (memoryListPanel) memoryListPanel.SetActive(false);
            if (memoryDetailPanel) memoryDetailPanel.SetActive(false);
            if (memoryCreatePanel) memoryCreatePanel.SetActive(true);
            if (operationsPanel) operationsPanel.SetActive(false);
            ClearCreateForm();
        }

        private void ClearCreateForm()
        {
            if (createNpcIdInput) createNpcIdInput.text = _currentNpcId ?? "";
            if (createContentInput) createContentInput.text = "";
            if (createImportanceSlider) createImportanceSlider.value = 5;
            if (createTagsInput) createTagsInput.text = "";
            if (createRelatedNpcsInput) createRelatedNpcsInput.text = "";
            if (createRelatedFactionsInput) createRelatedFactionsInput.text = "";
            if (createRelatedLocationsInput) createRelatedLocationsInput.text = "";
            UpdateSliderLabels();
        }

        private async void SaveMemory()
        {
            try
            {
                var npcId = createNpcIdInput?.text?.Trim();
                var content = createContentInput?.text?.Trim();

                if (string.IsNullOrEmpty(npcId) || string.IsNullOrEmpty(content))
                {
                    ShowNotification("NPC ID and content are required", NotificationType.Warning);
                    return;
                }

                var request = new CreateMemoryRequestDTO
                {
                    Content = content,
                    Importance = Mathf.RoundToInt(createImportanceSlider?.value ?? 5),
                    Tags = ParseListInput(createTagsInput?.text),
                    RelatedNpcs = ParseListInput(createRelatedNpcsInput?.text),
                    RelatedFactions = ParseListInput(createRelatedFactionsInput?.text),
                    RelatedLocations = ParseListInput(createRelatedLocationsInput?.text)
                };

                var response = await _memoryService.AddMemoryToNpcAsync(npcId, request);
                if (response.Success && response.Data != null)
                {
                    ShowNotification("Memory created successfully", NotificationType.Success);
                    OnMemoryCreated?.Invoke(response.Data.Memory);
                    
                    // Refresh if this is the current NPC
                    if (npcId == _currentNpcId)
                    {
                        await RefreshMemories();
                    }
                    ShowListPanel();
                }
                else
                {
                    ShowNotification($"Failed to create memory: {response.Message}", NotificationType.Error);
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error creating memory: {ex.Message}");
                ShowNotification("Error creating memory", NotificationType.Error);
            }
        }

        private async void RecallSelectedMemory()
        {
            if (_selectedMemory == null || string.IsNullOrEmpty(_currentNpcId)) return;

            try
            {
                var request = new RecallMemoryRequestDTO
                {
                    Context = recallContextInput?.text?.Trim() ?? ""
                };

                var response = await _memoryService.RecallMemoryAsync(_currentNpcId, _selectedMemory.MemoryId, request);
                if (response.Success && response.Data != null)
                {
                    ShowNotification("Memory recalled successfully", NotificationType.Success);
                    OnMemoryRecalled?.Invoke(response.Data.Memory);
                    
                    // Update the selected memory
                    _selectedMemory = response.Data.Memory;
                    UpdateMemoryDetail();
                    await RefreshMemories();
                }
                else
                {
                    ShowNotification($"Failed to recall memory: {response.Message}", NotificationType.Error);
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error recalling memory: {ex.Message}");
                ShowNotification("Error recalling memory", NotificationType.Error);
            }
        }

        private async void ReinforceSelectedMemory()
        {
            if (_selectedMemory == null || string.IsNullOrEmpty(_currentNpcId)) return;

            try
            {
                var request = new ReinforceMemoryRequestDTO
                {
                    Reinforcement = Mathf.RoundToInt(reinforceAmountSlider?.value ?? 1)
                };

                var response = await _memoryService.ReinforceMemoryAsync(_currentNpcId, _selectedMemory.MemoryId, request);
                if (response.Success && response.Data != null)
                {
                    ShowNotification("Memory reinforced successfully", NotificationType.Success);
                    OnMemoryReinforced?.Invoke(response.Data.Memory);
                    
                    // Update the selected memory
                    _selectedMemory = response.Data.Memory;
                    UpdateMemoryDetail();
                    await RefreshMemories();
                }
                else
                {
                    ShowNotification($"Failed to reinforce memory: {response.Message}", NotificationType.Error);
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error reinforcing memory: {ex.Message}");
                ShowNotification("Error reinforcing memory", NotificationType.Error);
            }
        }

        private async void ForgetSelectedMemory()
        {
            if (_selectedMemory == null || string.IsNullOrEmpty(_currentNpcId)) return;

            try
            {
                var request = new ForgetMemoryRequestDTO
                {
                    Reason = forgetReasonInput?.text?.Trim() ?? "manual"
                };

                var response = await _memoryService.ForgetMemoryAsync(_currentNpcId, _selectedMemory.MemoryId, request);
                if (response.Success)
                {
                    ShowNotification("Memory forgotten successfully", NotificationType.Success);
                    OnMemoryForgotten?.Invoke(_selectedMemory.MemoryId);
                    
                    await RefreshMemories();
                    ShowListPanel();
                }
                else
                {
                    ShowNotification($"Failed to forget memory: {response.Message}", NotificationType.Error);
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error forgetting memory: {ex.Message}");
                ShowNotification("Error forgetting memory", NotificationType.Error);
            }
        }

        private List<string> ParseListInput(string input)
        {
            if (string.IsNullOrEmpty(input)) return new List<string>();
            return input.Split(',').Select(s => s.Trim()).Where(s => !string.IsNullOrEmpty(s)).ToList();
        }

        private void OnSearchChanged(string searchTerm)
        {
            ApplyFilters();
            UpdateMemoryList();
        }

        private void OnImportanceFilterChanged(int filterIndex)
        {
            ApplyFilters();
            UpdateMemoryList();
        }

        private void OnTagFilterChanged(string tagFilter)
        {
            ApplyFilters();
            UpdateMemoryList();
        }

        private void OnCreateImportanceChanged(float value)
        {
            UpdateSliderLabels();
        }

        private void OnReinforceAmountChanged(float value)
        {
            UpdateSliderLabels();
        }

        private void UpdateSliderLabels()
        {
            if (createImportanceLabel && createImportanceSlider)
            {
                createImportanceLabel.text = $"Importance: {Mathf.RoundToInt(createImportanceSlider.value)}/10";
            }

            if (reinforceAmountLabel && reinforceAmountSlider)
            {
                reinforceAmountLabel.text = $"Reinforce: +{Mathf.RoundToInt(reinforceAmountSlider.value)}";
            }
        }
    }

    /// <summary>
    /// Controller for individual memory list items
    /// </summary>
    public class MemoryListItemController : MonoBehaviour
    {
        [SerializeField] private TextMeshProUGUI contentText;
        [SerializeField] private TextMeshProUGUI importanceText;
        [SerializeField] private TextMeshProUGUI recallCountText;
        [SerializeField] private TextMeshProUGUI tagsText;
        [SerializeField] private Button selectButton;

        private MemoryDTO _memory;
        public event Action<MemoryDTO> OnSelected;

        private void Awake()
        {
            if (selectButton) selectButton.onClick.AddListener(() => OnSelected?.Invoke(_memory));
        }

        public void Initialize(MemoryDTO memory)
        {
            _memory = memory;
            
            if (contentText) 
            {
                var preview = memory.GetPreview(60);
                contentText.text = preview;
            }
            
            if (importanceText) importanceText.text = $"Importance: {memory.Importance}/10";
            if (recallCountText) recallCountText.text = $"Recalls: {memory.RecallCount}";
            
            if (tagsText)
            {
                var tagDisplay = memory.Tags.Count > 0 ? string.Join(", ", memory.Tags.Take(3)) : "No tags";
                if (memory.Tags.Count > 3) tagDisplay += "...";
                tagsText.text = tagDisplay;
            }
        }
    }
} 