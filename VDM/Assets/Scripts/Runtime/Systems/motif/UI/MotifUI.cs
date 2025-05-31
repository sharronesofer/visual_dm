using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using System;
using TMPro;
using System.Linq;
using VDM.Systems.Motifs.Models;
using VDM.Systems.Motifs.Services;

namespace VDM.Systems.Motifs.Ui
{
    /// <summary>
    /// Main UI controller for motif management interface.
    /// Provides comprehensive motif browsing, filtering, creation, and editing capabilities.
    /// </summary>
    public class MotifUI : MonoBehaviour
    {
        [Header("UI References")]
        [SerializeField] private Transform _motifListContainer;
        [SerializeField] private GameObject _motifListItemPrefab;
        [SerializeField] private Button _refreshButton;
        [SerializeField] private Button _createNewButton;
        [SerializeField] private TMP_InputField _searchField;
        [SerializeField] private Toggle _showActiveOnlyToggle;
        [SerializeField] private TMP_Dropdown _categoryFilterDropdown;
        [SerializeField] private TMP_Dropdown _scopeFilterDropdown;
        [SerializeField] private TMP_Dropdown _lifecycleFilterDropdown;
        [SerializeField] private Slider _intensityMinSlider;
        [SerializeField] private Slider _intensityMaxSlider;
        [SerializeField] private TextMeshProUGUI _motifCountText;
        [SerializeField] private TextMeshProUGUI _statusText;

        [Header("Detail Panel")]
        [SerializeField] private GameObject _detailPanel;
        [SerializeField] private TextMeshProUGUI _detailTitle;
        [SerializeField] private TextMeshProUGUI _detailDescription;
        [SerializeField] private TextMeshProUGUI _detailCategory;
        [SerializeField] private TextMeshProUGUI _detailScope;
        [SerializeField] private TextMeshProUGUI _detailLifecycle;
        [SerializeField] private TextMeshProUGUI _detailIntensity;
        [SerializeField] private TextMeshProUGUI _detailDuration;
        [SerializeField] private TextMeshProUGUI _detailLocation;
        [SerializeField] private Transform _detailEffectsContainer;
        [SerializeField] private GameObject _effectItemPrefab;
        [SerializeField] private Button _editMotifButton;
        [SerializeField] private Button _deleteMotifButton;
        [SerializeField] private Button _closeDetailButton;

        [Header("Creation Panel")]
        [SerializeField] private GameObject _creationPanel;
        [SerializeField] private TMP_InputField _createNameField;
        [SerializeField] private TMP_InputField _createDescriptionField;
        [SerializeField] private TMP_Dropdown _createCategoryDropdown;
        [SerializeField] private TMP_Dropdown _createScopeDropdown;
        [SerializeField] private TMP_Dropdown _createLifecycleDropdown;
        [SerializeField] private Slider _createIntensitySlider;
        [SerializeField] private TMP_InputField _createDurationField;
        [SerializeField] private TMP_InputField _createThemeField;
        [SerializeField] private Button _saveMotifButton;
        [SerializeField] private Button _cancelCreateButton;

        [Header("Settings")]
        [SerializeField] private bool _autoRefreshOnStart = true;
        [SerializeField] private float _refreshInterval = 30f;
        [SerializeField] private int _maxMotifsDisplayed = 100;

        private List<Motif> _currentMotifs = new List<Motif>();
        private List<Motif> _filteredMotifs = new List<Motif>();
        private List<MotifListItem> _motifListItems = new List<MotifListItem>();
        private Motif _selectedMotif;
        private bool _isEditMode = false;

        #region Unity Lifecycle

        private void Start()
        {
            InitializeUI();
            SetupEventListeners();
            
            if (_autoRefreshOnStart)
            {
                RefreshMotifs();
            }
        }

        private void OnEnable()
        {
            SubscribeToManagerEvents();
        }

        private void OnDisable()
        {
            UnsubscribeFromManagerEvents();
        }

        #endregion

        #region Initialization

        private void InitializeUI()
        {
            // Initialize dropdowns
            SetupCategoryDropdown();
            SetupScopeDropdown();
            SetupLifecycleDropdown();
            
            // Set default values
            _intensityMinSlider.value = 1;
            _intensityMaxSlider.value = 10;
            _showActiveOnlyToggle.isOn = true;
            
            // Hide panels initially
            _detailPanel?.SetActive(false);
            _creationPanel?.SetActive(false);
            
            UpdateStatusText("Ready");
        }

        private void SetupEventListeners()
        {
            _refreshButton?.onClick.AddListener(() => RefreshMotifs());
            _createNewButton?.onClick.AddListener(ShowCreatePanel);
            _searchField?.onValueChanged.AddListener(_ => ApplyFilters());
            _showActiveOnlyToggle?.onValueChanged.AddListener(_ => ApplyFilters());
            _categoryFilterDropdown?.onValueChanged.AddListener(_ => ApplyFilters());
            _scopeFilterDropdown?.onValueChanged.AddListener(_ => ApplyFilters());
            _lifecycleFilterDropdown?.onValueChanged.AddListener(_ => ApplyFilters());
            _intensityMinSlider?.onValueChanged.AddListener(_ => ApplyFilters());
            _intensityMaxSlider?.onValueChanged.AddListener(_ => ApplyFilters());
            
            // Detail panel
            _editMotifButton?.onClick.AddListener(EditSelectedMotif);
            _deleteMotifButton?.onClick.AddListener(DeleteSelectedMotif);
            _closeDetailButton?.onClick.AddListener(() => _detailPanel?.SetActive(false));
            
            // Creation panel
            _saveMotifButton?.onClick.AddListener(SaveNewMotif);
            _cancelCreateButton?.onClick.AddListener(() => _creationPanel?.SetActive(false));
            
            // Update intensity display
            _createIntensitySlider?.onValueChanged.AddListener(value => 
                UpdateIntensityDisplay((int)value));
        }

        private void SubscribeToManagerEvents()
        {
            if (MotifManager.Instance != null)
            {
                MotifManager.Instance.OnMotifsUpdated += OnMotifsUpdated;
                MotifManager.Instance.OnMotifCreated += OnMotifCreated;
                MotifManager.Instance.OnMotifUpdated += OnMotifUpdated;
                MotifManager.Instance.OnMotifDeleted += OnMotifDeleted;
                MotifManager.Instance.OnError += OnError;
            }
        }

        private void UnsubscribeFromManagerEvents()
        {
            if (MotifManager.Instance != null)
            {
                MotifManager.Instance.OnMotifsUpdated -= OnMotifsUpdated;
                MotifManager.Instance.OnMotifCreated -= OnMotifCreated;
                MotifManager.Instance.OnMotifUpdated -= OnMotifUpdated;
                MotifManager.Instance.OnMotifDeleted -= OnMotifDeleted;
                MotifManager.Instance.OnError -= OnError;
            }
        }

        #endregion

        #region Dropdown Setup

        private void SetupCategoryDropdown()
        {
            if (_categoryFilterDropdown == null) return;
            
            _categoryFilterDropdown.ClearOptions();
            var options = new List<string> { "All Categories" };
            options.AddRange(Enum.GetNames(typeof(MotifCategory)));
            _categoryFilterDropdown.AddOptions(options);
            
            if (_createCategoryDropdown != null)
            {
                _createCategoryDropdown.ClearOptions();
                _createCategoryDropdown.AddOptions(Enum.GetNames(typeof(MotifCategory)).ToList());
            }
        }

        private void SetupScopeDropdown()
        {
            if (_scopeFilterDropdown == null) return;
            
            _scopeFilterDropdown.ClearOptions();
            var options = new List<string> { "All Scopes" };
            options.AddRange(Enum.GetNames(typeof(MotifScope)));
            _scopeFilterDropdown.AddOptions(options);
            
            if (_createScopeDropdown != null)
            {
                _createScopeDropdown.ClearOptions();
                _createScopeDropdown.AddOptions(Enum.GetNames(typeof(MotifScope)).ToList());
            }
        }

        private void SetupLifecycleDropdown()
        {
            if (_lifecycleFilterDropdown == null) return;
            
            _lifecycleFilterDropdown.ClearOptions();
            var options = new List<string> { "All Lifecycles" };
            options.AddRange(Enum.GetNames(typeof(MotifLifecycle)));
            _lifecycleFilterDropdown.AddOptions(options);
            
            if (_createLifecycleDropdown != null)
            {
                _createLifecycleDropdown.ClearOptions();
                _createLifecycleDropdown.AddOptions(Enum.GetNames(typeof(MotifLifecycle)).ToList());
                _createLifecycleDropdown.value = (int)MotifLifecycle.Emerging; // Default to Emerging
            }
        }

        #endregion

        #region Motif Management

        public async void RefreshMotifs()
        {
            UpdateStatusText("Loading motifs...");
            
            try
            {
                var motifs = await MotifManager.Instance.GetMotifsAsync();
                _currentMotifs = motifs;
                ApplyFilters();
                UpdateStatusText($"Loaded {motifs.Count} motifs");
            }
            catch (Exception ex)
            {
                UpdateStatusText($"Error loading motifs: {ex.Message}");
                Debug.LogError($"MotifUI: Error refreshing motifs: {ex.Message}");
            }
        }

        private void ApplyFilters()
        {
            if (_currentMotifs == null) return;
            
            _filteredMotifs = _currentMotifs.Where(motif => 
            {
                // Search filter
                if (!string.IsNullOrEmpty(_searchField?.text))
                {
                    string searchTerm = _searchField.text.ToLower();
                    if (!motif.name.ToLower().Contains(searchTerm) && 
                        !motif.description.ToLower().Contains(searchTerm))
                        return false;
                }
                
                // Active only filter
                if (_showActiveOnlyToggle?.isOn == true && !motif.IsActive())
                    return false;
                
                // Category filter
                if (_categoryFilterDropdown?.value > 0)
                {
                    var selectedCategory = (MotifCategory)(_categoryFilterDropdown.value - 1);
                    if (motif.category != selectedCategory)
                        return false;
                }
                
                // Scope filter
                if (_scopeFilterDropdown?.value > 0)
                {
                    var selectedScope = (MotifScope)(_scopeFilterDropdown.value - 1);
                    if (motif.scope != selectedScope)
                        return false;
                }
                
                // Lifecycle filter
                if (_lifecycleFilterDropdown?.value > 0)
                {
                    var selectedLifecycle = (MotifLifecycle)(_lifecycleFilterDropdown.value - 1);
                    if (motif.lifecycle != selectedLifecycle)
                        return false;
                }
                
                // Intensity filter
                if (_intensityMinSlider != null && _intensityMaxSlider != null)
                {
                    if (motif.intensity < _intensityMinSlider.value || 
                        motif.intensity > _intensityMaxSlider.value)
                        return false;
                }
                
                return true;
            }).Take(_maxMotifsDisplayed).ToList();
            
            UpdateMotifList();
            UpdateMotifCount();
        }

        private void UpdateMotifList()
        {
            // Clear existing items
            foreach (var item in _motifListItems)
            {
                if (item != null)
                    Destroy(item.gameObject);
            }
            _motifListItems.Clear();
            
            // Create new items
            foreach (var motif in _filteredMotifs)
            {
                CreateMotifListItem(motif);
            }
        }

        private void CreateMotifListItem(Motif motif)
        {
            if (_motifListItemPrefab == null || _motifListContainer == null) return;
            
            GameObject itemObj = Instantiate(_motifListItemPrefab, _motifListContainer);
            MotifListItem item = itemObj.GetComponent<MotifListItem>();
            
            if (item != null)
            {
                item.Initialize(motif, OnMotifSelected);
                _motifListItems.Add(item);
            }
        }

        private void OnMotifSelected(Motif motif)
        {
            _selectedMotif = motif;
            ShowMotifDetails(motif);
        }

        #endregion

        #region Detail Panel

        private void ShowMotifDetails(Motif motif)
        {
            if (_detailPanel == null || motif == null) return;
            
            _detailTitle.text = motif.name;
            _detailDescription.text = motif.description;
            _detailCategory.text = motif.category.ToString();
            _detailScope.text = motif.scope.ToString();
            _detailLifecycle.text = motif.lifecycle.ToString();
            _detailIntensity.text = $"{motif.intensity}/10";
            _detailDuration.text = $"{motif.durationDays} days";
            
            // Location info
            if (motif.location != null && motif.scope != MotifScope.Global)
            {
                _detailLocation.text = $"Region: {motif.location.regionId}\nPosition: ({motif.location.position.x}, {motif.location.position.y})";
            }
            else
            {
                _detailLocation.text = motif.scope == MotifScope.Global ? "Global" : "No location";
            }
            
            // Effects
            ShowMotifEffects(motif.effects);
            
            _detailPanel.SetActive(true);
        }

        private void ShowMotifEffects(List<MotifEffect> effects)
        {
            if (_detailEffectsContainer == null || _effectItemPrefab == null) return;
            
            // Clear existing effect items
            foreach (Transform child in _detailEffectsContainer)
            {
                Destroy(child.gameObject);
            }
            
            // Create effect items
            foreach (var effect in effects)
            {
                GameObject effectObj = Instantiate(_effectItemPrefab, _detailEffectsContainer);
                var effectText = effectObj.GetComponent<TextMeshProUGUI>();
                if (effectText != null)
                {
                    effectText.text = $"{effect.target}: {effect.description} (Intensity: {effect.intensity})";
                }
            }
        }

        #endregion

        #region Creation Panel

        private void ShowCreatePanel()
        {
            if (_creationPanel == null) return;
            
            // Reset form
            _createNameField.text = "";
            _createDescriptionField.text = "";
            _createCategoryDropdown.value = 0;
            _createScopeDropdown.value = 0;
            _createLifecycleDropdown.value = (int)MotifLifecycle.Emerging;
            _createIntensitySlider.value = 5;
            _createDurationField.text = "14";
            _createThemeField.text = "general";
            
            _isEditMode = false;
            _creationPanel.SetActive(true);
        }

        private void EditSelectedMotif()
        {
            if (_selectedMotif == null || _creationPanel == null) return;
            
            // Fill form with selected motif data
            _createNameField.text = _selectedMotif.name;
            _createDescriptionField.text = _selectedMotif.description;
            _createCategoryDropdown.value = (int)_selectedMotif.category;
            _createScopeDropdown.value = (int)_selectedMotif.scope;
            _createLifecycleDropdown.value = (int)_selectedMotif.lifecycle;
            _createIntensitySlider.value = _selectedMotif.intensity;
            _createDurationField.text = _selectedMotif.durationDays.ToString();
            _createThemeField.text = _selectedMotif.theme;
            
            _isEditMode = true;
            _creationPanel.SetActive(true);
            _detailPanel?.SetActive(false);
        }

        private async void SaveNewMotif()
        {
            try
            {
                if (_isEditMode)
                {
                    await UpdateExistingMotif();
                }
                else
                {
                    await CreateNewMotif();
                }
                
                _creationPanel?.SetActive(false);
            }
            catch (Exception ex)
            {
                UpdateStatusText($"Error saving motif: {ex.Message}");
                Debug.LogError($"MotifUI: Error saving motif: {ex.Message}");
            }
        }

        private async Task CreateNewMotif()
        {
            var motifData = new MotifCreateData
            {
                name = _createNameField.text,
                description = _createDescriptionField.text,
                category = (MotifCategory)_createCategoryDropdown.value,
                scope = (MotifScope)_createScopeDropdown.value,
                lifecycle = (MotifLifecycle)_createLifecycleDropdown.value,
                intensity = (int)_createIntensitySlider.value,
                durationDays = int.Parse(_createDurationField.text),
                theme = _createThemeField.text,
                effects = new List<MotifEffect>(),
                metadata = new Dictionary<string, object>()
            };
            
            UpdateStatusText("Creating motif...");
            await MotifManager.Instance.CreateMotifAsync(motifData);
        }

        private async Task UpdateExistingMotif()
        {
            if (_selectedMotif == null) return;
            
            var updateData = new MotifUpdateData
            {
                name = _createNameField.text,
                description = _createDescriptionField.text,
                category = (MotifCategory)_createCategoryDropdown.value,
                scope = (MotifScope)_createScopeDropdown.value,
                lifecycle = (MotifLifecycle)_createLifecycleDropdown.value,
                intensity = (int)_createIntensitySlider.value,
                durationDays = int.Parse(_createDurationField.text),
                theme = _createThemeField.text
            };
            
            UpdateStatusText("Updating motif...");
            await MotifManager.Instance.UpdateMotifAsync(_selectedMotif.id, updateData);
        }

        private async void DeleteSelectedMotif()
        {
            if (_selectedMotif == null) return;
            
            UpdateStatusText("Deleting motif...");
            bool success = await MotifManager.Instance.DeleteMotifAsync(_selectedMotif.id);
            
            if (success)
            {
                _detailPanel?.SetActive(false);
                _selectedMotif = null;
            }
        }

        #endregion

        #region Event Handlers

        private void OnMotifsUpdated(List<Motif> motifs)
        {
            _currentMotifs = motifs;
            ApplyFilters();
        }

        private void OnMotifCreated(Motif motif)
        {
            UpdateStatusText($"Created motif: {motif.name}");
            RefreshMotifs();
        }

        private void OnMotifUpdated(Motif motif)
        {
            UpdateStatusText($"Updated motif: {motif.name}");
            RefreshMotifs();
        }

        private void OnMotifDeleted(string motifId)
        {
            UpdateStatusText("Motif deleted");
            RefreshMotifs();
        }

        private void OnError(string errorMessage)
        {
            UpdateStatusText($"Error: {errorMessage}");
        }

        #endregion

        #region UI Helpers

        private void UpdateMotifCount()
        {
            if (_motifCountText != null)
            {
                _motifCountText.text = $"Showing {_filteredMotifs.Count} of {_currentMotifs.Count} motifs";
            }
        }

        private void UpdateStatusText(string status)
        {
            if (_statusText != null)
            {
                _statusText.text = status;
            }
        }

        private void UpdateIntensityDisplay(int intensity)
        {
            // You can add intensity display logic here
            // For example, updating a text field that shows the intensity value
        }

        #endregion

        #region Public API

        public void ShowMotif(string motifId)
        {
            var motif = _currentMotifs.FirstOrDefault(m => m.id == motifId);
            if (motif != null)
            {
                OnMotifSelected(motif);
            }
        }

        public void FilterByCategory(MotifCategory category)
        {
            if (_categoryFilterDropdown != null)
            {
                _categoryFilterDropdown.value = (int)category + 1;
                ApplyFilters();
            }
        }

        public void ClearFilters()
        {
            _searchField.text = "";
            _categoryFilterDropdown.value = 0;
            _scopeFilterDropdown.value = 0;
            _lifecycleFilterDropdown.value = 0;
            _intensityMinSlider.value = 1;
            _intensityMaxSlider.value = 10;
            _showActiveOnlyToggle.isOn = true;
            ApplyFilters();
        }

        #endregion
    }
} 