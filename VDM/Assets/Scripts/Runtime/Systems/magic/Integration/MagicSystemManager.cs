using NativeWebSocket;
using System.Collections.Generic;
using System;
using System.Threading.Tasks;
using UnityEngine;
using VDM.Infrastructure.Core;
using VDM.Systems.Magic.Models;
using VDM.Systems.Magic.Services;
using VDM.Systems.Magic.Models;
using VDM.Infrastructure.Services;
using VDM.Infrastructure.Core.Core.Systems;
using VDM.Systems.Magic.Ui;


namespace VDM.Systems.Magic.Integration
{
    /// <summary>
    /// Manages the magic system integration with Unity
    /// </summary>
    public class MagicSystemManager : MonoBehaviour, ISystemManager
    {
        [Header("Magic Configuration")]
        [SerializeField] private bool autoInitializeMagic = false;
        [SerializeField] private float magicUpdateInterval = 0.1f;
        [SerializeField] private int maxActiveCasters = 20;
        [SerializeField] private bool debugMode = false;
        
        [Header("UI References")]
        [SerializeField] private MagicUIController magicUIController;
        [SerializeField] private Canvas magicCanvas;
        
        // Services
        private MagicService _magicService;
        private MagicWebSocketHandler _webSocketHandler;
        
        // State
        private MagicSystemState _magicSystemState;
        private Dictionary<string, Spellcaster> _activeCasters = new Dictionary<string, Spellcaster>();
        private string _currentPlayerCasterId;
        private bool _isInitialized = false;
        
        // Events
        public event Action<string> OnMagicSessionStarted;
        public event Action<string> OnMagicSessionEnded;
        public event Action<MagicEvent> OnMagicEventReceived;
        public event Action<Spellcaster> OnSpellcasterAdded;
        public event Action<string> OnSpellcasterRemoved;
        
        // ISystemManager implementation
        public string SystemName => "Magic";
        public bool IsInitialized => _isInitialized;
        public bool IsEnabled { get; private set; } = true;
        public SystemHealthStatus HealthStatus { get; private set; } = SystemHealthStatus.Unknown;
        
        // ISystemManager required methods
        public void InitializeSystem()
        {
            InitializeAsync();
        }
        
        public void ShutdownSystem()
        {
            Shutdown();
        }
        
        public void UpdateSystem()
        {
            Update();
        }
        
        public SystemHealthStatus GetHealthStatus()
        {
            if (!_isInitialized)
                return SystemHealthStatus.Error;
            
            if (_activeCasters.Count >= maxActiveCasters)
                return SystemHealthStatus.Warning;
                
            return SystemHealthStatus.Healthy;
        }
        
        private void Awake()
        {
            // Register with ServiceLocator
            ServiceLocator.Instance.RegisterService<MagicSystemManager>(this);
            HealthStatus = SystemHealthStatus.Unknown;
            
            // Initialize magic system state
            _magicSystemState = new MagicSystemState();
        }
        
        private void Start()
        {
            InitializeAsync();
        }
        
        private void OnDestroy()
        {
            Shutdown();
        }
        
        /// <summary>
        /// Initialize the magic system
        /// </summary>
        public async void InitializeAsync()
        {
            try
            {
                Debug.Log("Initializing Magic System...");
                
                // Get or create services
                _magicService = ServiceLocator.Instance.GetService<MagicService>();
                if (_magicService == null)
                {
                    _magicService = new MagicService();
                    ServiceLocator.Instance.RegisterService(_magicService);
                }
                
                _webSocketHandler = ServiceLocator.Instance.GetService<MagicWebSocketHandler>();
                if (_webSocketHandler == null)
                {
                    _webSocketHandler = new MagicWebSocketHandler();
                    ServiceLocator.Instance.RegisterService(_webSocketHandler);
                }
                
                // Initialize services
                await _magicService.InitializeAsync();
                await _webSocketHandler.ConnectAsync();
                
                // Subscribe to events
                _webSocketHandler.OnMagicEvent += HandleMagicEvent;
                _webSocketHandler.OnMagicStateUpdated += HandleMagicStateUpdate;
                _webSocketHandler.OnSpellCast += HandleSpellCast;
                _webSocketHandler.OnSpellEffectAdded += HandleSpellEffectAdded;
                _webSocketHandler.OnSpellEffectRemoved += HandleSpellEffectRemoved;
                _webSocketHandler.OnSpellcasterUpdated += HandleSpellcasterUpdated;
                _webSocketHandler.OnManaChanged += HandleManaChanged;
                _webSocketHandler.OnConcentrationChanged += HandleConcentrationChanged;
                
                // Initialize UI
                if (magicUIController != null)
                {
                    magicUIController.OnSpellCast += HandleSpellCastFromUI;
                    magicUIController.OnSpellLearned += HandleSpellLearned;
                    magicUIController.OnSpellsPrepared += HandleSpellsPrepared;
                }
                
                // Load initial magic system state
                await LoadMagicSystemState();
                
                _isInitialized = true;
                Debug.Log("Magic System initialized successfully");
                
                // Auto-initialize magic session if configured
                if (autoInitializeMagic)
                {
                    StartPlayerMagicSession();
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to initialize Magic System: {ex.Message}");
            }
        }
        
        /// <summary>
        /// Shutdown the magic system
        /// </summary>
        public void Shutdown()
        {
            try
            {
                Debug.Log("Shutting down Magic System...");
                
                // End player magic session
                if (!string.IsNullOrEmpty(_currentPlayerCasterId))
                {
                    EndPlayerMagicSession();
                }
                
                // Unsubscribe from events
                if (_webSocketHandler != null)
                {
                    _webSocketHandler.OnMagicEvent -= HandleMagicEvent;
                    _webSocketHandler.OnMagicStateUpdated -= HandleMagicStateUpdate;
                    _webSocketHandler.OnSpellCast -= HandleSpellCast;
                    _webSocketHandler.OnSpellEffectAdded -= HandleSpellEffectAdded;
                    _webSocketHandler.OnSpellEffectRemoved -= HandleSpellEffectRemoved;
                    _webSocketHandler.OnSpellcasterUpdated -= HandleSpellcasterUpdated;
                    _webSocketHandler.OnManaChanged -= HandleManaChanged;
                    _webSocketHandler.OnConcentrationChanged -= HandleConcentrationChanged;
                    _webSocketHandler.DisconnectAsync();
                }
                
                if (magicUIController != null)
                {
                    magicUIController.OnSpellCast -= HandleSpellCastFromUI;
                    magicUIController.OnSpellLearned -= HandleSpellLearned;
                    magicUIController.OnSpellsPrepared -= HandleSpellsPrepared;
                }
                
                _isInitialized = false;
                Debug.Log("Magic System shut down");
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error shutting down Magic System: {ex.Message}");
            }
        }
        
        /// <summary>
        /// Start a magic session for the player
        /// </summary>
        public void StartPlayerMagicSession(string casterId = "player")
        {
            if (!_isInitialized)
            {
                Debug.LogError("Magic System not initialized");
                return;
            }
            
            if (!string.IsNullOrEmpty(_currentPlayerCasterId))
            {
                Debug.LogWarning("Player magic session already active");
                return;
            }
            
            _currentPlayerCasterId = casterId;
            ShowMagicUI(casterId);
            OnMagicSessionStarted?.Invoke(casterId);
            
            Debug.Log($"Player magic session started: {casterId}");
        }
        
        /// <summary>
        /// End the player's magic session
        /// </summary>
        public void EndPlayerMagicSession()
        {
            if (string.IsNullOrEmpty(_currentPlayerCasterId))
            {
                return;
            }
            
            string casterId = _currentPlayerCasterId;
            _currentPlayerCasterId = null;
            
            HideMagicUI();
            OnMagicSessionEnded?.Invoke(casterId);
            
            Debug.Log($"Player magic session ended: {casterId}");
        }
        
        /// <summary>
        /// Add a spellcaster to the system
        /// </summary>
        public void AddSpellcaster(Spellcaster caster)
        {
            if (caster == null || string.IsNullOrEmpty(caster.Name))
            {
                Debug.LogError("Invalid spellcaster");
                return;
            }
            
            if (_activeCasters.Count >= maxActiveCasters)
            {
                Debug.LogWarning("Maximum active casters reached");
                return;
            }
            
            _activeCasters[caster.Name] = caster;
            _magicSystemState.ActiveCasters.Add(caster);
            OnSpellcasterAdded?.Invoke(caster);
            
            if (debugMode)
            {
                Debug.Log($"Added spellcaster: {caster.Name}");
            }
        }
        
        /// <summary>
        /// Remove a spellcaster from the system
        /// </summary>
        public void RemoveSpellcaster(string casterId)
        {
            if (string.IsNullOrEmpty(casterId))
            {
                return;
            }
            
            if (_activeCasters.ContainsKey(casterId))
            {
                _activeCasters.Remove(casterId);
                _magicSystemState.ActiveCasters.RemoveAll(c => c.Name == casterId);
                OnSpellcasterRemoved?.Invoke(casterId);
                
                if (debugMode)
                {
                    Debug.Log($"Removed spellcaster: {casterId}");
                }
            }
        }
        
        /// <summary>
        /// Get the current player spellcaster
        /// </summary>
        public Spellcaster GetPlayerSpellcaster()
        {
            if (string.IsNullOrEmpty(_currentPlayerCasterId))
            {
                return null;
            }
            
            return _activeCasters.TryGetValue(_currentPlayerCasterId, out var caster) ? caster : null;
        }
        
        /// <summary>
        /// Check if player has an active magic session
        /// </summary>
        public bool IsPlayerMagicSessionActive()
        {
            return !string.IsNullOrEmpty(_currentPlayerCasterId);
        }
        
        /// <summary>
        /// Get all active spellcasters
        /// </summary>
        public Dictionary<string, Spellcaster> GetActiveSpellcasters()
        {
            return new Dictionary<string, Spellcaster>(_activeCasters);
        }
        
        /// <summary>
        /// Get the current magic system state
        /// </summary>
        public MagicSystemState GetMagicSystemState()
        {
            return _magicSystemState;
        }
        
        /// <summary>
        /// Create a test spellcaster for development
        /// </summary>
        [ContextMenu("Create Test Spellcaster")]
        public void CreateTestSpellcaster()
        {
            var testCaster = new Spellcaster
            {
                Name = "Test Wizard",
                Level = 5,
                PrimaryDomain = MagicDomain.Arcane,
                MaxMana = 100,
                CurrentMana = 100,
                MaxConcentration = 50,
                CurrentConcentration = 50,
                ManaRegenRate = 5,
                ConcentrationRegenRate = 3,
                SpellAttackBonus = 7,
                SpellSaveDC = 15,
                SpellcastingAbilityModifier = 3
            };
            
            // Add some test spells
            testCaster.KnownSpells.Add("magic_missile");
            testCaster.KnownSpells.Add("fireball");
            testCaster.KnownSpells.Add("shield");
            testCaster.PreparedSpells.Add("magic_missile");
            testCaster.PreparedSpells.Add("shield");
            
            AddSpellcaster(testCaster);
            
            // Start player session with test caster
            if (string.IsNullOrEmpty(_currentPlayerCasterId))
            {
                StartPlayerMagicSession(testCaster.Name);
            }
        }
        
        private async void LoadMagicSystemState()
        {
            try
            {
                var state = await _magicService.GetMagicSystemStateAsync();
                if (state != null)
                {
                    _magicSystemState = state;
                    
                    // Update active casters dictionary
                    _activeCasters.Clear();
                    foreach (var caster in state.ActiveCasters)
                    {
                        _activeCasters[caster.Name] = caster;
                    }
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to load magic system state: {ex.Message}");
            }
        }
        
        private void ShowMagicUI(string casterId)
        {
            if (magicUIController != null)
            {
                var caster = _activeCasters.TryGetValue(casterId, out var c) ? c : null;
                magicUIController.InitializeMagic(casterId, caster);
            }
            
            if (magicCanvas != null)
            {
                magicCanvas.gameObject.SetActive(true);
            }
        }
        
        private void HideMagicUI()
        {
            if (magicUIController != null)
            {
                magicUIController.CloseMagic();
            }
            
            if (magicCanvas != null)
            {
                magicCanvas.gameObject.SetActive(false);
            }
        }
        
        private void Update()
        {
            if (!_isInitialized || !IsEnabled)
            {
                return;
            }
            
            // Update magic system periodically
            UpdateMagicSystem();
            
            // Update health status
            if (_isInitialized)
            {
                HealthStatus = GetHealthStatus();
            }
        }
        
        private float _lastUpdateTime = 0f;
        
        private void UpdateMagicSystem()
        {
            if (Time.time - _lastUpdateTime < magicUpdateInterval)
            {
                return;
            }
            
            _lastUpdateTime = Time.time;
            
            // Update magic system state
            _magicSystemState.UpdateSystem(magicUpdateInterval);
            
            // Update active casters
            foreach (var caster in _activeCasters.Values)
            {
                caster.RegenerateMana(magicUpdateInterval);
                caster.RegenerateConcentration(magicUpdateInterval);
                caster.UpdateActiveEffects(magicUpdateInterval);
            }
        }
        
        // Event handlers
        private void HandleMagicEvent(MagicEvent magicEvent)
        {
            _magicSystemState.AddEvent(magicEvent);
            OnMagicEventReceived?.Invoke(magicEvent);
            
            if (debugMode)
            {
                Debug.Log($"Magic event: {magicEvent.EventType}");
            }
        }
        
        private void HandleMagicStateUpdate(MagicSystemState state)
        {
            _magicSystemState = state;
            
            // Update active casters
            _activeCasters.Clear();
            foreach (var caster in state.ActiveCasters)
            {
                _activeCasters[caster.Name] = caster;
            }
        }
        
        private void HandleSpellCast(SpellCastingResult result)
        {
            if (debugMode)
            {
                Debug.Log($"Spell cast: {result.Spell?.Name} by {result.Caster?.Name} - Result: {result.Result}");
            }
        }
        
        private void HandleSpellEffectAdded(ActiveSpellEffect effect)
        {
            _magicSystemState.GlobalEffects.Add(effect);
            
            if (debugMode)
            {
                Debug.Log($"Spell effect added: {effect.SpellId}");
            }
        }
        
        private void HandleSpellEffectRemoved(string effectId)
        {
            _magicSystemState.GlobalEffects.RemoveAll(e => e.EffectId == effectId);
            
            if (debugMode)
            {
                Debug.Log($"Spell effect removed: {effectId}");
            }
        }
        
        private void HandleSpellcasterUpdated(Spellcaster caster)
        {
            if (caster != null && !string.IsNullOrEmpty(caster.Name))
            {
                _activeCasters[caster.Name] = caster;
                
                // Update in magic system state
                var existingCaster = _magicSystemState.ActiveCasters.Find(c => c.Name == caster.Name);
                if (existingCaster != null)
                {
                    var index = _magicSystemState.ActiveCasters.IndexOf(existingCaster);
                    _magicSystemState.ActiveCasters[index] = caster;
                }
                else
                {
                    _magicSystemState.ActiveCasters.Add(caster);
                }
            }
        }
        
        private void HandleManaChanged(string casterId, int newMana)
        {
            if (_activeCasters.TryGetValue(casterId, out var caster))
            {
                caster.CurrentMana = newMana;
            }
        }
        
        private void HandleConcentrationChanged(string casterId, int newConcentration)
        {
            if (_activeCasters.TryGetValue(casterId, out var caster))
            {
                caster.CurrentConcentration = newConcentration;
            }
        }
        
        // UI event handlers
        private void HandleSpellCastFromUI(Spell spell, string targetId)
        {
            if (debugMode)
            {
                Debug.Log($"Spell cast from UI: {spell.Name} -> {targetId}");
            }
        }
        
        private void HandleSpellLearned(string spellId)
        {
            if (debugMode)
            {
                Debug.Log($"Spell learned: {spellId}");
            }
        }
        
        private void HandleSpellsPrepared(List<string> spellIds)
        {
            if (debugMode)
            {
                Debug.Log($"Spells prepared: {string.Join(", ", spellIds)}");
            }
        }
        
        // ISystemManager interface
        public void Enable()
        {
            IsEnabled = true;
        }
        
        public void Disable()
        {
            IsEnabled = false;
        }
        
        public void Restart()
        {
            Shutdown();
            InitializeAsync();
        }
        
        public Dictionary<string, object> GetSystemStatus()
        {
            return new Dictionary<string, object>
            {
                { "initialized", _isInitialized },
                { "enabled", IsEnabled },
                { "active_casters", _activeCasters.Count },
                { "player_session_active", IsPlayerMagicSessionActive() },
                { "current_player_caster", _currentPlayerCasterId ?? "none" },
                { "global_effects", _magicSystemState.GlobalEffects.Count },
                { "magic_suppressed", _magicSystemState.MagicSuppressed },
                { "magic_intensity", _magicSystemState.MagicIntensity }
            };
        }
    }
} 