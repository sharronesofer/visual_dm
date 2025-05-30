using System.Collections.Generic;
using System.Linq;
using System;
using TMPro;
using UnityEngine.UI;
using UnityEngine;
using VDM.Runtime.Religion.Models;
using VDM.Runtime.Religion.Services;
using VDM.Runtime.UI.Core;


namespace VDM.Runtime.Religion.UI
{
    /// <summary>
    /// UI controller for religion management panel
    /// </summary>
    public class ReligionPanelController : UIController
    {
        [Header("Religion Panel Components")]
        [SerializeField] private GameObject religionListPanel;
        [SerializeField] private GameObject religionDetailPanel;
        [SerializeField] private GameObject religionCreatePanel;
        
        [Header("Religion List")]
        [SerializeField] private Transform religionListContainer;
        [SerializeField] private GameObject religionItemPrefab;
        [SerializeField] private TMP_InputField searchInput;
        [SerializeField] private TMP_Dropdown typeFilter;
        [SerializeField] private Button createReligionButton;
        [SerializeField] private Button refreshButton;
        
        [Header("Religion Detail")]
        [SerializeField] private TextMeshProUGUI religionNameText;
        [SerializeField] private TextMeshProUGUI religionDescriptionText;
        [SerializeField] private TextMeshProUGUI religionTypeText;
        [SerializeField] private Transform tenetsContainer;
        [SerializeField] private Transform holyPlacesContainer;
        [SerializeField] private Transform sacredTextsContainer;
        [SerializeField] private Button editReligionButton;
        [SerializeField] private Button deleteReligionButton;
        [SerializeField] private Button backToListButton;
        
        [Header("Religion Creation")]
        [SerializeField] private TMP_InputField nameInput;
        [SerializeField] private TMP_InputField descriptionInput;
        [SerializeField] private TMP_Dropdown typeDropdown;
        [SerializeField] private TMP_InputField tenetsInput;
        [SerializeField] private TMP_InputField holyPlacesInput;
        [SerializeField] private TMP_InputField sacredTextsInput;
        [SerializeField] private Button saveReligionButton;
        [SerializeField] private Button cancelCreateButton;
        
        [Header("Membership Panel")]
        [SerializeField] private GameObject membershipPanel;
        [SerializeField] private Transform membershipContainer;
        [SerializeField] private GameObject membershipItemPrefab;
        [SerializeField] private Button joinReligionButton;
        [SerializeField] private Button leaveReligionButton;
        [SerializeField] private Slider devotionSlider;
        [SerializeField] private TextMeshProUGUI devotionValueText;

        private ReligionService _religionService;
        private List<ReligionDTO> _religions = new();
        private List<ReligionDTO> _filteredReligions = new();
        private ReligionDTO _selectedReligion;
        private List<ReligionMembershipDTO> _currentMemberships = new();
        private string _currentEntityId;

        public event Action<ReligionDTO> OnReligionSelected;
        public event Action<ReligionDTO> OnReligionCreated;
        public event Action<ReligionDTO> OnReligionUpdated;
        public event Action<string> OnReligionDeleted;

        protected override void Awake()
        {
            base.Awake();
            InitializeComponents();
        }

        private void InitializeComponents()
        {
            // Initialize religion service
            var httpClient = FindObjectOfType<HttpClient>();
            _religionService = new ReligionService(httpClient);

            // Setup button listeners
            if (createReligionButton) createReligionButton.onClick.AddListener(ShowCreatePanel);
            if (refreshButton) refreshButton.onClick.AddListener(RefreshReligions);
            if (editReligionButton) editReligionButton.onClick.AddListener(EditSelectedReligion);
            if (deleteReligionButton) deleteReligionButton.onClick.AddListener(DeleteSelectedReligion);
            if (backToListButton) backToListButton.onClick.AddListener(ShowListPanel);
            if (saveReligionButton) saveReligionButton.onClick.AddListener(SaveReligion);
            if (cancelCreateButton) cancelCreateButton.onClick.AddListener(ShowListPanel);
            if (joinReligionButton) joinReligionButton.onClick.AddListener(JoinSelectedReligion);
            if (leaveReligionButton) leaveReligionButton.onClick.AddListener(LeaveSelectedReligion);

            // Setup input listeners
            if (searchInput) searchInput.onValueChanged.AddListener(OnSearchChanged);
            if (typeFilter) typeFilter.onValueChanged.AddListener(OnTypeFilterChanged);
            if (devotionSlider) devotionSlider.onValueChanged.AddListener(OnDevotionChanged);

            // Initialize dropdowns
            InitializeTypeDropdowns();

            // Show list panel by default
            ShowListPanel();
        }

        private void InitializeTypeDropdowns()
        {
            var typeOptions = Enum.GetNames(typeof(ReligionType)).ToList();
            
            if (typeFilter)
            {
                typeFilter.ClearOptions();
                typeFilter.AddOptions(new List<string> { "All Types" }.Concat(typeOptions).ToList());
            }

            if (typeDropdown)
            {
                typeDropdown.ClearOptions();
                typeDropdown.AddOptions(typeOptions);
            }
        }

        public async void Initialize(string entityId = null)
        {
            _currentEntityId = entityId;
            await RefreshReligions();
            
            if (!string.IsNullOrEmpty(entityId))
            {
                await LoadEntityMemberships(entityId);
            }
        }

        public async void RefreshReligions()
        {
            try
            {
                var response = await _religionService.GetReligionsAsync();
                if (response.Success)
                {
                    _religions = response.Data ?? new List<ReligionDTO>();
                    ApplyFilters();
                    UpdateReligionList();
                }
                else
                {
                    Debug.LogError($"Failed to load religions: {response.Message}");
                    ShowNotification("Failed to load religions", NotificationType.Error);
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error refreshing religions: {ex.Message}");
                ShowNotification("Error loading religions", NotificationType.Error);
            }
        }

        private async void LoadEntityMemberships(string entityId)
        {
            try
            {
                var response = await _religionService.GetEntityMembershipsAsync(entityId);
                if (response.Success)
                {
                    _currentMemberships = response.Data ?? new List<ReligionMembershipDTO>();
                    UpdateMembershipDisplay();
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error loading memberships: {ex.Message}");
            }
        }

        private void ApplyFilters()
        {
            _filteredReligions = _religions.ToList();

            // Apply search filter
            if (searchInput && !string.IsNullOrEmpty(searchInput.text))
            {
                var searchTerm = searchInput.text.ToLower();
                _filteredReligions = _filteredReligions.Where(r => 
                    r.Name.ToLower().Contains(searchTerm) ||
                    r.Description.ToLower().Contains(searchTerm) ||
                    r.Tags.Any(tag => tag.ToLower().Contains(searchTerm))
                ).ToList();
            }

            // Apply type filter
            if (typeFilter && typeFilter.value > 0)
            {
                var selectedType = (ReligionType)(typeFilter.value - 1);
                _filteredReligions = _filteredReligions.Where(r => r.Type == selectedType).ToList();
            }
        }

        private void UpdateReligionList()
        {
            if (!religionListContainer) return;

            // Clear existing items
            foreach (Transform child in religionListContainer)
            {
                Destroy(child.gameObject);
            }

            // Create new items
            foreach (var religion in _filteredReligions)
            {
                CreateReligionListItem(religion);
            }
        }

        private void CreateReligionListItem(ReligionDTO religion)
        {
            if (!religionItemPrefab) return;

            var item = Instantiate(religionItemPrefab, religionListContainer);
            var itemController = item.GetComponent<ReligionListItemController>();
            
            if (itemController)
            {
                itemController.Initialize(religion, _currentMemberships);
                itemController.OnSelected += SelectReligion;
            }
        }

        private void SelectReligion(ReligionDTO religion)
        {
            _selectedReligion = religion;
            UpdateReligionDetail();
            ShowDetailPanel();
            OnReligionSelected?.Invoke(religion);
        }

        private void UpdateReligionDetail()
        {
            if (_selectedReligion == null) return;

            if (religionNameText) religionNameText.text = _selectedReligion.Name;
            if (religionDescriptionText) religionDescriptionText.text = _selectedReligion.Description;
            if (religionTypeText) religionTypeText.text = _selectedReligion.Type.ToString();

            UpdateDetailList(tenetsContainer, _selectedReligion.Tenets);
            UpdateDetailList(holyPlacesContainer, _selectedReligion.HolyPlaces);
            UpdateDetailList(sacredTextsContainer, _selectedReligion.SacredTexts);

            UpdateMembershipButtons();
        }

        private void UpdateDetailList(Transform container, List<string> items)
        {
            if (!container) return;

            foreach (Transform child in container)
            {
                Destroy(child.gameObject);
            }

            foreach (var item in items)
            {
                var textObj = new GameObject("ListItem");
                textObj.transform.SetParent(container);
                var text = textObj.AddComponent<TextMeshProUGUI>();
                text.text = $"• {item}";
                text.fontSize = 14;
            }
        }

        private void UpdateMembershipButtons()
        {
            if (_selectedReligion == null || string.IsNullOrEmpty(_currentEntityId))
            {
                if (joinReligionButton) joinReligionButton.gameObject.SetActive(false);
                if (leaveReligionButton) leaveReligionButton.gameObject.SetActive(false);
                return;
            }

            var membership = _currentMemberships.FirstOrDefault(m => m.ReligionId == _selectedReligion.Id);
            bool isMember = membership != null;

            if (joinReligionButton) joinReligionButton.gameObject.SetActive(!isMember);
            if (leaveReligionButton) leaveReligionButton.gameObject.SetActive(isMember);

            if (isMember && devotionSlider)
            {
                devotionSlider.value = membership.DevotionLevel;
                UpdateDevotionDisplay(membership.DevotionLevel);
            }
        }

        private void UpdateMembershipDisplay()
        {
            if (!membershipContainer) return;

            foreach (Transform child in membershipContainer)
            {
                Destroy(child.gameObject);
            }

            foreach (var membership in _currentMemberships)
            {
                var religion = _religions.FirstOrDefault(r => r.Id == membership.ReligionId);
                if (religion != null)
                {
                    CreateMembershipItem(membership, religion);
                }
            }
        }

        private void CreateMembershipItem(ReligionMembershipDTO membership, ReligionDTO religion)
        {
            if (!membershipItemPrefab) return;

            var item = Instantiate(membershipItemPrefab, membershipContainer);
            var itemController = item.GetComponent<ReligionMembershipItemController>();
            
            if (itemController)
            {
                itemController.Initialize(membership, religion);
            }
        }

        private void ShowListPanel()
        {
            if (religionListPanel) religionListPanel.SetActive(true);
            if (religionDetailPanel) religionDetailPanel.SetActive(false);
            if (religionCreatePanel) religionCreatePanel.SetActive(false);
        }

        private void ShowDetailPanel()
        {
            if (religionListPanel) religionListPanel.SetActive(false);
            if (religionDetailPanel) religionDetailPanel.SetActive(true);
            if (religionCreatePanel) religionCreatePanel.SetActive(false);
        }

        private void ShowCreatePanel()
        {
            if (religionListPanel) religionListPanel.SetActive(false);
            if (religionDetailPanel) religionDetailPanel.SetActive(false);
            if (religionCreatePanel) religionCreatePanel.SetActive(true);
            ClearCreateForm();
        }

        private void ClearCreateForm()
        {
            if (nameInput) nameInput.text = "";
            if (descriptionInput) descriptionInput.text = "";
            if (typeDropdown) typeDropdown.value = 0;
            if (tenetsInput) tenetsInput.text = "";
            if (holyPlacesInput) holyPlacesInput.text = "";
            if (sacredTextsInput) sacredTextsInput.text = "";
        }

        private async void SaveReligion()
        {
            try
            {
                var request = new CreateReligionRequestDTO
                {
                    Name = nameInput?.text ?? "",
                    Description = descriptionInput?.text ?? "",
                    Type = (ReligionType)(typeDropdown?.value ?? 0),
                    Tenets = ParseListInput(tenetsInput?.text),
                    HolyPlaces = ParseListInput(holyPlacesInput?.text),
                    SacredTexts = ParseListInput(sacredTextsInput?.text)
                };

                var response = await _religionService.CreateReligionAsync(request);
                if (response.Success)
                {
                    ShowNotification("Religion created successfully", NotificationType.Success);
                    OnReligionCreated?.Invoke(response.Data);
                    await RefreshReligions();
                    ShowListPanel();
                }
                else
                {
                    ShowNotification($"Failed to create religion: {response.Message}", NotificationType.Error);
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error creating religion: {ex.Message}");
                ShowNotification("Error creating religion", NotificationType.Error);
            }
        }

        private List<string> ParseListInput(string input)
        {
            if (string.IsNullOrEmpty(input)) return new List<string>();
            return input.Split(',').Select(s => s.Trim()).Where(s => !string.IsNullOrEmpty(s)).ToList();
        }

        private async void EditSelectedReligion()
        {
            // Implementation for editing religion
            // This would show an edit form similar to create form
            Debug.Log("Edit religion functionality not yet implemented");
        }

        private async void DeleteSelectedReligion()
        {
            if (_selectedReligion == null) return;

            try
            {
                var response = await _religionService.DeleteReligionAsync(_selectedReligion.Id);
                if (response.Success)
                {
                    ShowNotification("Religion deleted successfully", NotificationType.Success);
                    OnReligionDeleted?.Invoke(_selectedReligion.Id);
                    await RefreshReligions();
                    ShowListPanel();
                }
                else
                {
                    ShowNotification($"Failed to delete religion: {response.Message}", NotificationType.Error);
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error deleting religion: {ex.Message}");
                ShowNotification("Error deleting religion", NotificationType.Error);
            }
        }

        private async void JoinSelectedReligion()
        {
            if (_selectedReligion == null || string.IsNullOrEmpty(_currentEntityId)) return;

            try
            {
                var devotion = devotionSlider?.value ?? 0.5f;
                var response = await _religionService.JoinReligionAsync(_currentEntityId, _selectedReligion.Id, devotion);
                
                if (response.Success)
                {
                    ShowNotification("Joined religion successfully", NotificationType.Success);
                    await LoadEntityMemberships(_currentEntityId);
                    UpdateMembershipButtons();
                }
                else
                {
                    ShowNotification($"Failed to join religion: {response.Message}", NotificationType.Error);
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error joining religion: {ex.Message}");
                ShowNotification("Error joining religion", NotificationType.Error);
            }
        }

        private async void LeaveSelectedReligion()
        {
            if (_selectedReligion == null || string.IsNullOrEmpty(_currentEntityId)) return;

            try
            {
                var response = await _religionService.LeaveReligionAsync(_currentEntityId, _selectedReligion.Id);
                
                if (response.Success)
                {
                    ShowNotification("Left religion successfully", NotificationType.Success);
                    await LoadEntityMemberships(_currentEntityId);
                    UpdateMembershipButtons();
                }
                else
                {
                    ShowNotification($"Failed to leave religion: {response.Message}", NotificationType.Error);
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error leaving religion: {ex.Message}");
                ShowNotification("Error leaving religion", NotificationType.Error);
            }
        }

        private void OnSearchChanged(string searchTerm)
        {
            ApplyFilters();
            UpdateReligionList();
        }

        private void OnTypeFilterChanged(int filterIndex)
        {
            ApplyFilters();
            UpdateReligionList();
        }

        private void OnDevotionChanged(float value)
        {
            UpdateDevotionDisplay(value);
        }

        private void UpdateDevotionDisplay(float value)
        {
            if (devotionValueText)
            {
                devotionValueText.text = $"{value:P0}";
            }
        }
    }

    /// <summary>
    /// Controller for individual religion list items
    /// </summary>
    public class ReligionListItemController : MonoBehaviour
    {
        [SerializeField] private TextMeshProUGUI nameText;
        [SerializeField] private TextMeshProUGUI typeText;
        [SerializeField] private TextMeshProUGUI membershipText;
        [SerializeField] private Button selectButton;

        private ReligionDTO _religion;
        public event Action<ReligionDTO> OnSelected;

        private void Awake()
        {
            if (selectButton) selectButton.onClick.AddListener(() => OnSelected?.Invoke(_religion));
        }

        public void Initialize(ReligionDTO religion, List<ReligionMembershipDTO> memberships)
        {
            _religion = religion;
            
            if (nameText) nameText.text = religion.Name;
            if (typeText) typeText.text = religion.Type.ToString();
            
            var membership = memberships.FirstOrDefault(m => m.ReligionId == religion.Id);
            if (membershipText)
            {
                membershipText.text = membership != null ? $"Member ({membership.DevotionLevel:P0})" : "Not a member";
            }
        }
    }

    /// <summary>
    /// Controller for membership items
    /// </summary>
    public class ReligionMembershipItemController : MonoBehaviour
    {
        [SerializeField] private TextMeshProUGUI religionNameText;
        [SerializeField] private TextMeshProUGUI devotionText;
        [SerializeField] private TextMeshProUGUI roleText;
        [SerializeField] private TextMeshProUGUI joinedDateText;

        public void Initialize(ReligionMembershipDTO membership, ReligionDTO religion)
        {
            if (religionNameText) religionNameText.text = religion.Name;
            if (devotionText) devotionText.text = $"Devotion: {membership.DevotionLevel:P0}";
            if (roleText) roleText.text = $"Role: {membership.Role}";
            if (joinedDateText) joinedDateText.text = $"Joined: {membership.JoinedAt:yyyy-MM-dd}";
        }
    }
} 