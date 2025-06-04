using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using TMPro;
using VDM.Infrastructure.Services;
using VDM.Systems.Motifs.Models;
using VDM.Systems.Motifs.Services;
using VDM.Infrastructure.Core.Core.Ui;

namespace VDM.Systems.Motifs.Ui
{
    /// <summary>
    /// UI panel for managing motifs in the game
    /// </summary>
    public class MotifManagementPanel : BaseUIComponent
    {
        [Header("UI References")]
        [SerializeField] private Transform motifListParent;
        [SerializeField] private GameObject motifItemPrefab;
        [SerializeField] private Button refreshButton;
        [SerializeField] private Button createMotifButton;
        [SerializeField] private Button generateRandomButton;
        [SerializeField] private TMP_Dropdown categoryFilter;
        [SerializeField] private TMP_Dropdown scopeFilter;
        [SerializeField] private TMP_Dropdown lifecycleFilter;
        [SerializeField] private Toggle activeOnlyToggle;
        [SerializeField] private TMP_InputField searchField;
        [SerializeField] private TextMeshProUGUI statusText;
        [SerializeField] private TextMeshProUGUI motifCountText;

        [Header("Create Motif Panel")]
        [SerializeField] private GameObject createMotifPanel;
        [SerializeField] private TMP_InputField nameInput;
        [SerializeField] private TMP_InputField descriptionInput;
        [SerializeField] private TMP_Dropdown categoryDropdown;
        [SerializeField] private TMP_Dropdown scopeDropdown;
        [SerializeField] private Slider intensitySlider;
        [SerializeField] private TMP_InputField durationInput;
        [SerializeField] private Button confirmCreateButton;
        [SerializeField] private Button cancelCreateButton;

        [Header("Motif Details Panel")]
        [SerializeField] private GameObject motifDetailsPanel;
        [SerializeField] private TextMeshProUGUI detailsNameText;
        [SerializeField] private TextMeshProUGUI detailsDescriptionText;
        [SerializeField] private TextMeshProUGUI detailsCategoryText;
        [SerializeField] private TextMeshProUGUI detailsScopeText;
        [SerializeField] private TextMeshProUGUI detailsLifecycleText;
        [SerializeField] private TextMeshProUGUI detailsIntensityText;
        [SerializeField] private Button editMotifButton;
        [SerializeField] private Button deleteMotifButton;
        [SerializeField] private Button closeDetailsButton;

        // State
        private List<Motif> _currentMotifs = new List<Motif>();
        private List<MotifItemUI> _motifItems = new List<MotifItemUI>();
        private Motif _selectedMotif;
        private MotifFilter _currentFilter = new MotifFilter();

        // Services
        private MotifManager _motifManager;

        #region Unity Lifecycle

        protected override void OnInitialize()
        {
            base.OnInitialize();
            
            _motifManager = MotifManager.Instance;
            
            SetupEventListeners();
            SetupDropdowns();
            SetupFilters();
            
            // Hide panels initially
            if (createMotifPanel != null)
                createMotifPanel.SetActive(false);
            if (motifDetailsPanel != null)
                motifDetailsPanel.SetActive(false);
        }

        private void OnDestroy()
        {
            if (_motifManager != null)
            {
                _motifManager.OnMotifsLoaded -= OnMotifsLoaded;
                _motifManager.OnMotifAdded -= OnMotifAdded;
                _motifManager.OnMotifUpdated -= OnMotifUpdated;
                _motifManager.OnMotifRemoved -= OnMotifRemoved;
                _motifManager.OnError -= OnError;
            }
        }

        #endregion

        #region Setup

        private void SetupEventListeners()
        {
            // Motif Manager events
            if (_motifManager != null)
            {
                _motifManager.OnMotifsLoaded += OnMotifsLoaded;
                _motifManager.OnMotifAdded += OnMotifAdded;
                _motifManager.OnMotifUpdated += OnMotifUpdated;
                _motifManager.OnMotifRemoved += OnMotifRemoved;
                _motifManager.OnError += OnError;
            }

            // UI Button events
            if (refreshButton != null)
                refreshButton.onClick.AddListener(RefreshMotifs);
            
            if (createMotifButton != null)
                createMotifButton.onClick.AddListener(ShowCreateMotifPanel);
            
            if (generateRandomButton != null)
                generateRandomButton.onClick.AddListener(GenerateRandomMotif);

            // Filter events
            if (categoryFilter != null)
                categoryFilter.onValueChanged.AddListener(OnFilterChanged);
            
            if (scopeFilter != null)
                scopeFilter.onValueChanged.AddListener(OnFilterChanged);
            
            if (lifecycleFilter != null)
                lifecycleFilter.onValueChanged.AddListener(OnFilterChanged);
            
            if (activeOnlyToggle != null)
                activeOnlyToggle.onValueChanged.AddListener(OnActiveOnlyChanged);
            
            if (searchField != null)
                searchField.onValueChanged.AddListener(OnSearchChanged);

            // Create motif panel events
            if (confirmCreateButton != null)
                confirmCreateButton.onClick.AddListener(CreateMotif);
            
            if (cancelCreateButton != null)
                cancelCreateButton.onClick.AddListener(HideCreateMotifPanel);

            // Details panel events
            if (editMotifButton != null)
                editMotifButton.onClick.AddListener(EditSelectedMotif);
            
            if (deleteMotifButton != null)
                deleteMotifButton.onClick.AddListener(DeleteSelectedMotif);
            
            if (closeDetailsButton != null)
                closeDetailsButton.onClick.AddListener(HideDetailsPanel);
        }

        private void SetupDropdowns()
        {
            // Setup category filter
            if (categoryFilter != null)
            {
                var categoryOptions = new List<string> { "All Categories" };
                categoryOptions.AddRange(System.Enum.GetNames(typeof(MotifCategory)));
                categoryFilter.ClearOptions();
                categoryFilter.AddOptions(categoryOptions);
            }

            // Setup scope filter
            if (scopeFilter != null)
            {
                var scopeOptions = new List<string> { "All Scopes" };
                scopeOptions.AddRange(System.Enum.GetNames(typeof(MotifScope)));
                scopeFilter.ClearOptions();
                scopeFilter.AddOptions(scopeOptions);
            }

            // Setup lifecycle filter
            if (lifecycleFilter != null)
            {
                var lifecycleOptions = new List<string> { "All Lifecycles" };
                lifecycleOptions.AddRange(System.Enum.GetNames(typeof(MotifLifecycle)));
                lifecycleFilter.ClearOptions();
                lifecycleFilter.AddOptions(lifecycleOptions);
            }

            // Setup create motif dropdowns
            if (categoryDropdown != null)
            {
                var categoryOptions = System.Enum.GetNames(typeof(MotifCategory)).ToList();
                categoryDropdown.ClearOptions();
                categoryDropdown.AddOptions(categoryOptions);
            }

            if (scopeDropdown != null)
            {
                var scopeOptions = System.Enum.GetNames(typeof(MotifScope)).ToList();
                scopeDropdown.ClearOptions();
                scopeDropdown.AddOptions(scopeOptions);
            }
        }

        private void SetupFilters()
        {
            _currentFilter.activeOnly = true;
            if (activeOnlyToggle != null)
                activeOnlyToggle.isOn = true;
        }

        #endregion

        #region Public API

        /// <summary>
        /// Refresh the motif list
        /// </summary>
        public async void RefreshMotifs()
        {
            SetStatus("Refreshing motifs...");
            
            try
            {
                var motifs = await _motifManager.GetMotifsAsync(_currentFilter);
                UpdateMotifList(motifs);
                SetStatus($"Loaded {motifs.Count} motifs");
            }
            catch (System.Exception ex)
            {
                SetStatus($"Error: {ex.Message}");
            }
        }

        /// <summary>
        /// Show the create motif panel
        /// </summary>
        public void ShowCreateMotifPanel()
        {
            if (createMotifPanel != null)
            {
                createMotifPanel.SetActive(true);
                ClearCreateMotifForm();
            }
        }

        /// <summary>
        /// Hide the create motif panel
        /// </summary>
        public void HideCreateMotifPanel()
        {
            if (createMotifPanel != null)
                createMotifPanel.SetActive(false);
        }

        /// <summary>
        /// Show details for a specific motif
        /// </summary>
        public void ShowMotifDetails(Motif motif)
        {
            _selectedMotif = motif;
            
            if (motifDetailsPanel != null)
            {
                motifDetailsPanel.SetActive(true);
                UpdateDetailsPanel();
            }
        }

        /// <summary>
        /// Hide the details panel
        /// </summary>
        public void HideDetailsPanel()
        {
            if (motifDetailsPanel != null)
                motifDetailsPanel.SetActive(false);
            
            _selectedMotif = null;
        }

        #endregion

        #region Event Handlers

        private void OnMotifsLoaded(List<Motif> motifs)
        {
            UpdateMotifList(motifs);
            SetStatus($"Loaded {motifs.Count} motifs");
        }

        private void OnMotifAdded(Motif motif)
        {
            if (ShouldShowMotif(motif))
            {
                _currentMotifs.Add(motif);
                CreateMotifItem(motif);
                UpdateMotifCount();
            }
        }

        private void OnMotifUpdated(Motif motif)
        {
            var existingItem = _motifItems.FirstOrDefault(item => item.MotifId == motif.id);
            if (existingItem != null)
            {
                if (ShouldShowMotif(motif))
                {
                    existingItem.UpdateMotif(motif);
                    
                    // Update details panel if this motif is selected
                    if (_selectedMotif?.id == motif.id)
                    {
                        _selectedMotif = motif;
                        UpdateDetailsPanel();
                    }
                }
                else
                {
                    // Remove from list if it no longer matches filter
                    RemoveMotifItem(motif.id);
                }
            }
            else if (ShouldShowMotif(motif))
            {
                // Add to list if it now matches filter
                _currentMotifs.Add(motif);
                CreateMotifItem(motif);
                UpdateMotifCount();
            }
        }

        private void OnMotifRemoved(string motifId)
        {
            RemoveMotifItem(motifId);
            
            if (_selectedMotif?.id == motifId)
            {
                HideDetailsPanel();
            }
        }

        private void OnError(string error)
        {
            SetStatus($"Error: {error}");
        }

        private void OnFilterChanged(int value)
        {
            UpdateFilter();
            RefreshMotifs();
        }

        private void OnActiveOnlyChanged(bool value)
        {
            _currentFilter.activeOnly = value;
            RefreshMotifs();
        }

        private void OnSearchChanged(string searchText)
        {
            FilterMotifsBySearch(searchText);
        }

        #endregion

        #region UI Updates

        private void UpdateMotifList(List<Motif> motifs)
        {
            _currentMotifs = motifs;
            
            // Clear existing items
            ClearMotifItems();
            
            // Create new items
            foreach (var motif in motifs)
            {
                if (ShouldShowMotif(motif))
                {
                    CreateMotifItem(motif);
                }
            }
            
            UpdateMotifCount();
        }

        private void CreateMotifItem(Motif motif)
        {
            if (motifItemPrefab == null || motifListParent == null) return;

            var itemGO = Instantiate(motifItemPrefab, motifListParent);
            var motifItem = itemGO.GetComponent<MotifItemUI>();
            
            if (motifItem != null)
            {
                motifItem.Initialize(motif, this);
                _motifItems.Add(motifItem);
            }
        }

        private void RemoveMotifItem(string motifId)
        {
            var item = _motifItems.FirstOrDefault(item => item.MotifId == motifId);
            if (item != null)
            {
                _motifItems.Remove(item);
                _currentMotifs.RemoveAll(m => m.id == motifId);
                
                if (item.gameObject != null)
                    Destroy(item.gameObject);
                
                UpdateMotifCount();
            }
        }

        private void ClearMotifItems()
        {
            foreach (var item in _motifItems)
            {
                if (item != null && item.gameObject != null)
                    Destroy(item.gameObject);
            }
            
            _motifItems.Clear();
        }

        private void UpdateDetailsPanel()
        {
            if (_selectedMotif == null || motifDetailsPanel == null) return;

            if (detailsNameText != null)
                detailsNameText.text = _selectedMotif.name;
            
            if (detailsDescriptionText != null)
                detailsDescriptionText.text = _selectedMotif.description;
            
            if (detailsCategoryText != null)
                detailsCategoryText.text = _selectedMotif.category.ToString();
            
            if (detailsScopeText != null)
                detailsScopeText.text = _selectedMotif.scope.ToString();
            
            if (detailsLifecycleText != null)
                detailsLifecycleText.text = _selectedMotif.lifecycle.ToString();
            
            if (detailsIntensityText != null)
                detailsIntensityText.text = $"{_selectedMotif.intensity}/10";
        }

        private void UpdateFilter()
        {
            _currentFilter = new MotifFilter();
            
            // Category filter
            if (categoryFilter != null && categoryFilter.value > 0)
            {
                var categoryName = categoryFilter.options[categoryFilter.value].text;
                if (System.Enum.TryParse<MotifCategory>(categoryName, out var category))
                {
                    _currentFilter.categories.Add(category);
                }
            }

            // Scope filter
            if (scopeFilter != null && scopeFilter.value > 0)
            {
                var scopeName = scopeFilter.options[scopeFilter.value].text;
                if (System.Enum.TryParse<MotifScope>(scopeName, out var scope))
                {
                    _currentFilter.scopes.Add(scope);
                }
            }

            // Lifecycle filter
            if (lifecycleFilter != null && lifecycleFilter.value > 0)
            {
                var lifecycleName = lifecycleFilter.options[lifecycleFilter.value].text;
                if (System.Enum.TryParse<MotifLifecycle>(lifecycleName, out var lifecycle))
                {
                    _currentFilter.lifecycles.Add(lifecycle);
                }
            }

            // Active only
            if (activeOnlyToggle != null)
                _currentFilter.activeOnly = activeOnlyToggle.isOn;
        }

        private void FilterMotifsBySearch(string searchText)
        {
            foreach (var item in _motifItems)
            {
                if (item != null && item.gameObject != null)
                {
                    bool matches = string.IsNullOrEmpty(searchText) || 
                                 item.GetMotif().name.ToLower().Contains(searchText.ToLower()) ||
                                 item.GetMotif().description.ToLower().Contains(searchText.ToLower());
                    
                    item.gameObject.SetActive(matches);
                }
            }
        }

        private void UpdateMotifCount()
        {
            if (motifCountText != null)
            {
                int visibleCount = _motifItems.Count(item => item.gameObject.activeInHierarchy);
                motifCountText.text = $"{visibleCount} motifs";
            }
        }

        private void SetStatus(string message)
        {
            if (statusText != null)
                statusText.text = message;
        }

        #endregion

        #region Motif Operations

        private async void CreateMotif()
        {
            if (!ValidateCreateMotifForm()) return;

            var createData = new MotifCreateData
            {
                name = nameInput.text,
                description = descriptionInput.text,
                category = (MotifCategory)categoryDropdown.value,
                scope = (MotifScope)scopeDropdown.value,
                intensity = Mathf.RoundToInt(intensitySlider.value),
                durationDays = int.TryParse(durationInput.text, out int duration) ? duration : 14
            };

            SetStatus("Creating motif...");
            
            try
            {
                var motif = await _motifManager.CreateMotifAsync(createData);
                if (motif != null)
                {
                    SetStatus($"Created motif: {motif.name}");
                    HideCreateMotifPanel();
                }
                else
                {
                    SetStatus("Failed to create motif");
                }
            }
            catch (System.Exception ex)
            {
                SetStatus($"Error creating motif: {ex.Message}");
            }
        }

        private async void GenerateRandomMotif()
        {
            SetStatus("Generating random motif...");
            
            try
            {
                var motif = await _motifManager.GenerateRandomMotifAsync(MotifScope.Local);
                if (motif != null)
                {
                    SetStatus($"Generated motif: {motif.name}");
                }
                else
                {
                    SetStatus("Failed to generate motif");
                }
            }
            catch (System.Exception ex)
            {
                SetStatus($"Error generating motif: {ex.Message}");
            }
        }

        private void EditSelectedMotif()
        {
            if (_selectedMotif == null) return;
            
            // TODO: Implement edit functionality
            SetStatus("Edit functionality not yet implemented");
        }

        private async void DeleteSelectedMotif()
        {
            if (_selectedMotif == null) return;

            SetStatus($"Deleting motif: {_selectedMotif.name}...");
            
            try
            {
                bool success = await _motifManager.DeleteMotifAsync(_selectedMotif.id);
                if (success)
                {
                    SetStatus($"Deleted motif: {_selectedMotif.name}");
                    HideDetailsPanel();
                }
                else
                {
                    SetStatus("Failed to delete motif");
                }
            }
            catch (System.Exception ex)
            {
                SetStatus($"Error deleting motif: {ex.Message}");
            }
        }

        #endregion

        #region Helper Methods

        private bool ShouldShowMotif(Motif motif)
        {
            if (_currentFilter.activeOnly && !motif.IsActive())
                return false;

            if (_currentFilter.categories.Count > 0 && !_currentFilter.categories.Contains(motif.category))
                return false;

            if (_currentFilter.scopes.Count > 0 && !_currentFilter.scopes.Contains(motif.scope))
                return false;

            if (_currentFilter.lifecycles.Count > 0 && !_currentFilter.lifecycles.Contains(motif.lifecycle))
                return false;

            return true;
        }

        private bool ValidateCreateMotifForm()
        {
            if (string.IsNullOrEmpty(nameInput.text))
            {
                SetStatus("Name is required");
                return false;
            }

            if (string.IsNullOrEmpty(descriptionInput.text))
            {
                SetStatus("Description is required");
                return false;
            }

            return true;
        }

        private void ClearCreateMotifForm()
        {
            if (nameInput != null) nameInput.text = "";
            if (descriptionInput != null) descriptionInput.text = "";
            if (categoryDropdown != null) categoryDropdown.value = 0;
            if (scopeDropdown != null) scopeDropdown.value = 0;
            if (intensitySlider != null) intensitySlider.value = 5;
            if (durationInput != null) durationInput.text = "14";
        }

        #endregion
    }

    /// <summary>
    /// UI component for individual motif items in the list
    /// </summary>
    public class MotifItemUI : MonoBehaviour
    {
        [Header("UI References")]
        [SerializeField] private TextMeshProUGUI nameText;
        [SerializeField] private TextMeshProUGUI categoryText;
        [SerializeField] private TextMeshProUGUI lifecycleText;
        [SerializeField] private Image categoryIcon;
        [SerializeField] private Button selectButton;

        private Motif _motif;
        private MotifManagementPanel _parentPanel;

        public string MotifId => _motif?.id;

        public void Initialize(Motif motif, MotifManagementPanel parentPanel)
        {
            _motif = motif;
            _parentPanel = parentPanel;
            
            UpdateDisplay();
            
            if (selectButton != null)
                selectButton.onClick.AddListener(OnSelectClicked);
        }

        public void UpdateMotif(Motif motif)
        {
            _motif = motif;
            UpdateDisplay();
        }

        public Motif GetMotif()
        {
            return _motif;
        }

        private void UpdateDisplay()
        {
            if (_motif == null) return;

            if (nameText != null)
                nameText.text = _motif.name;
            
            if (categoryText != null)
                categoryText.text = _motif.category.ToString();
            
            if (lifecycleText != null)
                lifecycleText.text = _motif.lifecycle.ToString();
            
            // TODO: Set category icon based on motif category
        }

        private void OnSelectClicked()
        {
            _parentPanel?.ShowMotifDetails(_motif);
        }
    }
} 