using System.Collections.Generic;
using System.Linq;
using System;
using TMPro;
using UnityEngine.UI;
using UnityEngine;
using VDM.Runtime.Magic.Models;
using VDM.Runtime.Magic.Services;
using VDM.Runtime.UI;


namespace VDM.Runtime.Magic.UI
{
    /// <summary>
    /// Controls the magic system user interface and spell casting interactions
    /// </summary>
    public class MagicUIController : UIController
    {
        [Header("Magic UI References")]
        [SerializeField] private GameObject magicPanel;
        [SerializeField] private Transform spellbookContainer;
        [SerializeField] private Transform preparedSpellsContainer;
        [SerializeField] private Transform activeEffectsContainer;
        [SerializeField] private ScrollRect spellLogScrollRect;
        [SerializeField] private Transform spellLogContent;
        [SerializeField] private Button castSelectedSpellButton;
        [SerializeField] private Button longRestButton;
        
        [Header("Resource Display")]
        [SerializeField] private Slider manaSlider;
        [SerializeField] private TextMeshProUGUI manaText;
        [SerializeField] private Slider concentrationSlider;
        [SerializeField] private TextMeshProUGUI concentrationText;
        [SerializeField] private TextMeshProUGUI casterLevelText;
        
        [Header("Spell Filtering")]
        [SerializeField] private Dropdown schoolFilterDropdown;
        [SerializeField] private Dropdown domainFilterDropdown;
        [SerializeField] private TMP_InputField spellSearchField;
        [SerializeField] private Toggle showOnlyPreparedToggle;
        
        [Header("Prefabs")]
        [SerializeField] private GameObject spellButtonPrefab;
        [SerializeField] private GameObject activeEffectPrefab;
        [SerializeField] private GameObject spellLogEntryPrefab;
        
        [Header("Magic Configuration")]
        [SerializeField] private float castingAnimationDuration = 2f;
        [SerializeField] private int maxLogEntries = 100;
        
        // Services
        private MagicService _magicService;
        private MagicWebSocketHandler _webSocketHandler;
        
        // State
        private string _currentCasterId;
        private Spellcaster _currentCaster;
        private List<Spell> _availableSpells = new List<Spell>();
        private List<Spell> _filteredSpells = new List<Spell>();
        private Spell _selectedSpell;
        private string _selectedTargetId;
        
        // Events
        public event Action<Spell, string> OnSpellCast;
        public event Action<string> OnSpellLearned;
        public event Action<List<string>> OnSpellsPrepared;
        
        protected override void Awake()
        {
            base.Awake();
            
            // Get services
            _magicService = ServiceLocator.Get<MagicService>();
            _webSocketHandler = ServiceLocator.Get<MagicWebSocketHandler>();
            
            // Setup UI events
            if (castSelectedSpellButton != null)
            {
                castSelectedSpellButton.onClick.AddListener(CastSelectedSpell);
            }
            
            if (longRestButton != null)
            {
                longRestButton.onClick.AddListener(TakeLongRest);
            }
            
            if (spellSearchField != null)
            {
                spellSearchField.onValueChanged.AddListener(OnSearchChanged);
            }
            
            if (schoolFilterDropdown != null)
            {
                schoolFilterDropdown.onValueChanged.AddListener(OnSchoolFilterChanged);
            }
            
            if (domainFilterDropdown != null)
            {
                domainFilterDropdown.onValueChanged.AddListener(OnDomainFilterChanged);
            }
            
            if (showOnlyPreparedToggle != null)
            {
                showOnlyPreparedToggle.onValueChanged.AddListener(OnPreparedFilterChanged);
            }
        }
        
        protected override void OnEnable()
        {
            base.OnEnable();
            
            // Subscribe to magic events
            if (_webSocketHandler != null)
            {
                _webSocketHandler.OnMagicEvent += HandleMagicEvent;
                _webSocketHandler.OnMagicStateUpdated += HandleMagicStateUpdated;
                _webSocketHandler.OnSpellCast += HandleSpellCast;
                _webSocketHandler.OnSpellEffectAdded += HandleSpellEffectAdded;
                _webSocketHandler.OnSpellEffectRemoved += HandleSpellEffectRemoved;
                _webSocketHandler.OnSpellcasterUpdated += HandleSpellcasterUpdated;
                _webSocketHandler.OnManaChanged += HandleManaChanged;
                _webSocketHandler.OnConcentrationChanged += HandleConcentrationChanged;
            }
        }
        
        protected override void OnDisable()
        {
            base.OnDisable();
            
            // Unsubscribe from magic events
            if (_webSocketHandler != null)
            {
                _webSocketHandler.OnMagicEvent -= HandleMagicEvent;
                _webSocketHandler.OnMagicStateUpdated -= HandleMagicStateUpdated;
                _webSocketHandler.OnSpellCast -= HandleSpellCast;
                _webSocketHandler.OnSpellEffectAdded -= HandleSpellEffectAdded;
                _webSocketHandler.OnSpellEffectRemoved -= HandleSpellEffectRemoved;
                _webSocketHandler.OnSpellcasterUpdated -= HandleSpellcasterUpdated;
                _webSocketHandler.OnManaChanged -= HandleManaChanged;
                _webSocketHandler.OnConcentrationChanged -= HandleConcentrationChanged;
            }
        }
        
        /// <summary>
        /// Initialize magic UI with spellcaster data
        /// </summary>
        public void InitializeMagic(string casterId, Spellcaster caster = null)
        {
            _currentCasterId = casterId;
            _currentCaster = caster;
            
            // Show magic panel
            if (magicPanel != null)
            {
                magicPanel.SetActive(true);
            }
            
            // Join WebSocket session for real-time updates
            _webSocketHandler?.JoinMagicSession(casterId);
            
            // Initialize dropdowns
            InitializeFilters();
            
            // Load data if not provided
            if (caster == null)
            {
                LoadSpellcasterData();
            }
            else
            {
                UpdateMagicUI(caster);
            }
            
            LoadAvailableSpells();
        }
        
        /// <summary>
        /// Close magic UI and clean up
        /// </summary>
        public void CloseMagic()
        {
            // Leave WebSocket session
            if (!string.IsNullOrEmpty(_currentCasterId))
            {
                _webSocketHandler?.LeaveMagicSession();
            }
            
            // Hide magic panel
            if (magicPanel != null)
            {
                magicPanel.SetActive(false);
            }
            
            // Clear state
            _currentCasterId = null;
            _currentCaster = null;
            _availableSpells.Clear();
            _filteredSpells.Clear();
            _selectedSpell = null;
            _selectedTargetId = null;
        }
        
        /// <summary>
        /// Cast the currently selected spell
        /// </summary>
        public async void CastSelectedSpell()
        {
            if (_selectedSpell == null || string.IsNullOrEmpty(_currentCasterId))
            {
                Debug.LogError("No spell selected or no caster ID");
                return;
            }
            
            try
            {
                // Disable casting controls during animation
                SetCastingEnabled(false);
                
                // Show casting animation/feedback
                AddSpellLogEntry($"Casting {_selectedSpell.Name}...");
                
                // Cast spell via service
                var result = await _magicService.CastSpellAsync(_currentCasterId, _selectedSpell.Id, _selectedTargetId);
                
                // Update UI based on result
                if (result.Result == CastingResult.Success)
                {
                    AddSpellLogEntry($"Successfully cast {_selectedSpell.Name}!");
                    OnSpellCast?.Invoke(_selectedSpell, _selectedTargetId);
                }
                else
                {
                    AddSpellLogEntry($"Failed to cast {_selectedSpell.Name}: {result.Message}");
                }
                
                // Clear selection
                _selectedSpell = null;
                _selectedTargetId = null;
                UpdateSpellSelection();
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to cast spell: {ex.Message}");
                AddSpellLogEntry($"Casting failed: {ex.Message}");
            }
            finally
            {
                // Re-enable casting controls
                SetCastingEnabled(true);
            }
        }
        
        /// <summary>
        /// Learn a new spell
        /// </summary>
        public async void LearnSpell(string spellId)
        {
            if (string.IsNullOrEmpty(_currentCasterId) || string.IsNullOrEmpty(spellId))
            {
                return;
            }
            
            try
            {
                bool success = await _magicService.LearnSpellAsync(_currentCasterId, spellId);
                if (success)
                {
                    AddSpellLogEntry($"Learned new spell!");
                    OnSpellLearned?.Invoke(spellId);
                    LoadSpellcasterData(); // Refresh data
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to learn spell: {ex.Message}");
            }
        }
        
        /// <summary>
        /// Prepare spells for casting
        /// </summary>
        public async void PrepareSpells(List<string> spellIds)
        {
            if (string.IsNullOrEmpty(_currentCasterId) || spellIds == null)
            {
                return;
            }
            
            try
            {
                bool success = await _magicService.PrepareSpellsAsync(_currentCasterId, spellIds);
                if (success)
                {
                    AddSpellLogEntry($"Prepared {spellIds.Count} spells");
                    OnSpellsPrepared?.Invoke(spellIds);
                    LoadSpellcasterData(); // Refresh data
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to prepare spells: {ex.Message}");
            }
        }
        
        /// <summary>
        /// Take a long rest to restore resources
        /// </summary>
        public async void TakeLongRest()
        {
            if (string.IsNullOrEmpty(_currentCasterId))
            {
                return;
            }
            
            try
            {
                bool success = await _magicService.LongRestAsync(_currentCasterId);
                if (success)
                {
                    AddSpellLogEntry("Took a long rest - resources restored!");
                    LoadSpellcasterData(); // Refresh data
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to take long rest: {ex.Message}");
            }
        }
        
        private async void LoadSpellcasterData()
        {
            if (string.IsNullOrEmpty(_currentCasterId))
            {
                return;
            }
            
            try
            {
                var caster = await _magicService.GetSpellcasterAsync(_currentCasterId);
                if (caster != null)
                {
                    _currentCaster = caster;
                    UpdateMagicUI(caster);
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to load spellcaster data: {ex.Message}");
            }
        }
        
        private async void LoadAvailableSpells()
        {
            try
            {
                var spells = await _magicService.GetSpellsAsync();
                _availableSpells = spells;
                FilterSpells();
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to load available spells: {ex.Message}");
            }
        }
        
        private void UpdateMagicUI(Spellcaster caster)
        {
            // Update resource displays
            UpdateResourceDisplay(caster);
            
            // Update spell lists
            UpdateSpellbookUI(caster);
            UpdatePreparedSpellsUI(caster);
            UpdateActiveEffectsUI(caster);
        }
        
        private void UpdateResourceDisplay(Spellcaster caster)
        {
            // Update mana
            if (manaSlider != null)
            {
                manaSlider.maxValue = caster.MaxMana;
                manaSlider.value = caster.CurrentMana;
            }
            
            if (manaText != null)
            {
                manaText.text = $"{caster.CurrentMana}/{caster.MaxMana}";
            }
            
            // Update concentration
            if (concentrationSlider != null)
            {
                concentrationSlider.maxValue = caster.MaxConcentration;
                concentrationSlider.value = caster.CurrentConcentration;
            }
            
            if (concentrationText != null)
            {
                concentrationText.text = $"{caster.CurrentConcentration}/{caster.MaxConcentration}";
            }
            
            // Update level
            if (casterLevelText != null)
            {
                casterLevelText.text = $"Level {caster.Level} {caster.PrimaryDomain} Caster";
            }
        }
        
        private void UpdateSpellbookUI(Spellcaster caster)
        {
            if (spellbookContainer == null || spellButtonPrefab == null)
            {
                return;
            }
            
            // Clear existing spells
            foreach (Transform child in spellbookContainer)
            {
                Destroy(child.gameObject);
            }
            
            // Create buttons for filtered spells
            foreach (var spell in _filteredSpells)
            {
                var buttonObject = Instantiate(spellButtonPrefab, spellbookContainer);
                var spellButton = buttonObject.GetComponent<SpellButton>();
                
                if (spellButton != null)
                {
                    spellButton.Initialize(spell, caster.KnownSpells.Contains(spell.Id));
                    spellButton.OnSpellSelected += SelectSpell;
                }
            }
        }
        
        private void UpdatePreparedSpellsUI(Spellcaster caster)
        {
            if (preparedSpellsContainer == null || spellButtonPrefab == null)
            {
                return;
            }
            
            // Clear existing spells
            foreach (Transform child in preparedSpellsContainer)
            {
                Destroy(child.gameObject);
            }
            
            // Create buttons for prepared spells
            var preparedSpells = _availableSpells.Where(s => caster.PreparedSpells.Contains(s.Id)).ToList();
            foreach (var spell in preparedSpells)
            {
                var buttonObject = Instantiate(spellButtonPrefab, preparedSpellsContainer);
                var spellButton = buttonObject.GetComponent<SpellButton>();
                
                if (spellButton != null)
                {
                    spellButton.Initialize(spell, true, true); // Known and prepared
                    spellButton.OnSpellSelected += SelectSpell;
                }
            }
        }
        
        private void UpdateActiveEffectsUI(Spellcaster caster)
        {
            if (activeEffectsContainer == null || activeEffectPrefab == null)
            {
                return;
            }
            
            // Clear existing effects
            foreach (Transform child in activeEffectsContainer)
            {
                Destroy(child.gameObject);
            }
            
            // Create UI for active effects
            foreach (var effect in caster.ActiveEffects)
            {
                var effectObject = Instantiate(activeEffectPrefab, activeEffectsContainer);
                var effectUI = effectObject.GetComponent<ActiveEffectUI>();
                
                if (effectUI != null)
                {
                    effectUI.Initialize(effect);
                }
            }
        }
        
        private void SelectSpell(Spell spell)
        {
            _selectedSpell = spell;
            UpdateSpellSelection();
        }
        
        private void UpdateSpellSelection()
        {
            // Update cast button
            if (castSelectedSpellButton != null)
            {
                castSelectedSpellButton.interactable = _selectedSpell != null && 
                    _currentCaster != null && 
                    _selectedSpell.CanCast(_currentCaster);
                
                var buttonText = castSelectedSpellButton.GetComponentInChildren<TextMeshProUGUI>();
                if (buttonText != null)
                {
                    buttonText.text = _selectedSpell != null ? $"Cast {_selectedSpell.Name}" : "Select Spell";
                }
            }
        }
        
        private void InitializeFilters()
        {
            // Initialize school filter
            if (schoolFilterDropdown != null)
            {
                schoolFilterDropdown.ClearOptions();
                var schoolOptions = new List<string> { "All Schools" };
                schoolOptions.AddRange(Enum.GetNames(typeof(MagicSchool)));
                schoolFilterDropdown.AddOptions(schoolOptions);
            }
            
            // Initialize domain filter
            if (domainFilterDropdown != null)
            {
                domainFilterDropdown.ClearOptions();
                var domainOptions = new List<string> { "All Domains" };
                domainOptions.AddRange(Enum.GetNames(typeof(MagicDomain)));
                domainFilterDropdown.AddOptions(domainOptions);
            }
        }
        
        private void FilterSpells()
        {
            _filteredSpells = _availableSpells.ToList();
            
            // Apply search filter
            if (spellSearchField != null && !string.IsNullOrEmpty(spellSearchField.text))
            {
                string searchTerm = spellSearchField.text.ToLower();
                _filteredSpells = _filteredSpells.Where(s => 
                    s.Name.ToLower().Contains(searchTerm) || 
                    s.Description.ToLower().Contains(searchTerm)).ToList();
            }
            
            // Apply school filter
            if (schoolFilterDropdown != null && schoolFilterDropdown.value > 0)
            {
                var selectedSchool = (MagicSchool)(schoolFilterDropdown.value - 1);
                _filteredSpells = _filteredSpells.Where(s => s.School == selectedSchool).ToList();
            }
            
            // Apply domain filter
            if (domainFilterDropdown != null && domainFilterDropdown.value > 0)
            {
                var selectedDomain = (MagicDomain)(domainFilterDropdown.value - 1);
                _filteredSpells = _filteredSpells.Where(s => s.Domain == selectedDomain).ToList();
            }
            
            // Apply prepared filter
            if (showOnlyPreparedToggle != null && showOnlyPreparedToggle.isOn && _currentCaster != null)
            {
                _filteredSpells = _filteredSpells.Where(s => _currentCaster.PreparedSpells.Contains(s.Id)).ToList();
            }
            
            // Update UI
            if (_currentCaster != null)
            {
                UpdateSpellbookUI(_currentCaster);
            }
        }
        
        private void SetCastingEnabled(bool enabled)
        {
            if (castSelectedSpellButton != null)
            {
                castSelectedSpellButton.interactable = enabled;
            }
            
            if (spellbookContainer != null)
            {
                foreach (Transform child in spellbookContainer)
                {
                    var button = child.GetComponent<Button>();
                    if (button != null)
                    {
                        button.interactable = enabled;
                    }
                }
            }
        }
        
        private void AddSpellLogEntry(string message)
        {
            if (spellLogContent == null || spellLogEntryPrefab == null)
            {
                return;
            }
            
            // Create log entry
            var entryObject = Instantiate(spellLogEntryPrefab, spellLogContent);
            var text = entryObject.GetComponentInChildren<TextMeshProUGUI>();
            
            if (text != null)
            {
                text.text = $"[{DateTime.Now:HH:mm:ss}] {message}";
            }
            
            // Limit number of log entries
            if (spellLogContent.childCount > maxLogEntries)
            {
                Destroy(spellLogContent.GetChild(0).gameObject);
            }
            
            // Scroll to bottom
            Canvas.ForceUpdateCanvases();
            spellLogScrollRect.verticalNormalizedPosition = 0f;
        }
        
        // Filter event handlers
        private void OnSearchChanged(string searchTerm)
        {
            FilterSpells();
        }
        
        private void OnSchoolFilterChanged(int value)
        {
            FilterSpells();
        }
        
        private void OnDomainFilterChanged(int value)
        {
            FilterSpells();
        }
        
        private void OnPreparedFilterChanged(bool value)
        {
            FilterSpells();
        }
        
        // WebSocket event handlers
        private void HandleMagicEvent(MagicEvent magicEvent)
        {
            AddSpellLogEntry($"Magic Event: {magicEvent.EventType}");
        }
        
        private void HandleMagicStateUpdated(MagicSystemState state)
        {
            // Update UI if our caster is in the state
            var ourCaster = state.ActiveCasters.Find(c => c.Name == _currentCasterId);
            if (ourCaster != null)
            {
                _currentCaster = ourCaster;
                UpdateMagicUI(ourCaster);
            }
        }
        
        private void HandleSpellCast(SpellCastingResult result)
        {
            if (result.Caster?.Name == _currentCasterId)
            {
                AddSpellLogEntry($"Spell cast: {result.Spell?.Name} - {result.Result}");
            }
        }
        
        private void HandleSpellEffectAdded(ActiveSpellEffect effect)
        {
            if (effect.Caster?.Name == _currentCasterId)
            {
                AddSpellLogEntry($"Spell effect added: {effect.SpellId}");
                LoadSpellcasterData(); // Refresh to show new effect
            }
        }
        
        private void HandleSpellEffectRemoved(string effectId)
        {
            AddSpellLogEntry($"Spell effect removed: {effectId}");
            LoadSpellcasterData(); // Refresh to remove effect
        }
        
        private void HandleSpellcasterUpdated(Spellcaster caster)
        {
            if (caster.Name == _currentCasterId)
            {
                _currentCaster = caster;
                UpdateMagicUI(caster);
            }
        }
        
        private void HandleManaChanged(string casterId, int newMana)
        {
            if (casterId == _currentCasterId && _currentCaster != null)
            {
                _currentCaster.CurrentMana = newMana;
                UpdateResourceDisplay(_currentCaster);
            }
        }
        
        private void HandleConcentrationChanged(string casterId, int newConcentration)
        {
            if (casterId == _currentCasterId && _currentCaster != null)
            {
                _currentCaster.CurrentConcentration = newConcentration;
                UpdateResourceDisplay(_currentCaster);
            }
        }
    }
} 