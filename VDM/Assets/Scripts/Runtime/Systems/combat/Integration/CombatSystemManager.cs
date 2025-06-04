using NativeWebSocket;
using System.Collections.Generic;
using System.Collections;
using System;
using UnityEngine;
using VDM.Systems.Combat.Models;
using VDM.Systems.Combat.Services;
using VDM.Systems.Combat.Models;
using VDM.Infrastructure.Core.Core.Systems;
using VDM.Infrastructure.Core.Core.Patterns;
using VDM.Infrastructure.Services;
using VDM.Systems.Combat.Ui;

namespace VDM.Systems.Combat.Integration
{
    /// <summary>
    /// Manages the combat system integration with Unity
    /// </summary>
    public class CombatSystemManager : MonoBehaviour, ISystemManager
    {
        [Header("Combat Configuration")]
        [SerializeField] private bool autoStartCombat = false;
        [SerializeField] private float combatUpdateInterval = 0.1f;
        [SerializeField] private int maxConcurrentCombats = 5;
        
        [Header("UI References")]
        [SerializeField] private CombatUIController combatUIController;
        [SerializeField] private Canvas combatCanvas;
        
        // Services
        private CombatService _combatService;
        private CombatWebSocketHandler _webSocketHandler;
        
        // State
        private Dictionary<string, CombatState> _activeCombats = new Dictionary<string, CombatState>();
        private string _currentPlayerCombatId;
        private bool _isInitialized = false;
        
        // Events
        public event Action<string> OnCombatStarted;
        public event Action<string> OnCombatEnded;
        public event Action<CombatEvent> OnCombatEventReceived;
        
        // ISystemManager implementation
        public string SystemName => "Combat";
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
            
            if (_activeCombats.Count >= maxConcurrentCombats)
                return SystemHealthStatus.Warning;
                
            return SystemHealthStatus.Healthy;
        }
        
        private void Awake()
        {
            // Register with service locator
            ServiceLocator.Instance.RegisterService<CombatSystemManager>(this);
            HealthStatus = SystemHealthStatus.Unknown;
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
        /// Initialize the combat system
        /// </summary>
        public async void InitializeAsync()
        {
            try
            {
                Debug.Log("Initializing Combat System...");
                
                // Get or create services
                _combatService = ServiceLocator.Instance.GetService<CombatService>();
                if (_combatService == null)
                {
                    _combatService = new CombatService();
                    ServiceLocator.Instance.RegisterService(_combatService);
                }
                
                _webSocketHandler = ServiceLocator.Instance.GetService<CombatWebSocketHandler>();
                if (_webSocketHandler == null)
                {
                    _webSocketHandler = new CombatWebSocketHandler();
                    ServiceLocator.Instance.RegisterService(_webSocketHandler);
                }
                
                // Initialize services
                await _combatService.InitializeAsync();
                await _webSocketHandler.ConnectAsync();
                
                // Subscribe to events
                _combatService.OnCombatStarted += HandleCombatStarted;
                _combatService.OnCombatEnded += HandleCombatEnded;
                _webSocketHandler.OnCombatEventReceived += HandleCombatEvent;
                _webSocketHandler.OnCombatStateUpdated += HandleCombatStateUpdate;
                
                // Initialize UI
                if (combatUIController != null)
                {
                    combatUIController.OnActionSelected += HandleActionSelected;
                    combatUIController.OnTurnEnded += HandleTurnEnded;
                    combatUIController.OnCombatExited += HandleCombatExited;
                }
                
                _isInitialized = true;
                Debug.Log("Combat System initialized successfully");
                
                // Auto-start combat if configured
                if (autoStartCombat)
                {
                    StartTestCombat();
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to initialize Combat System: {ex.Message}");
            }
        }
        
        /// <summary>
        /// Shutdown the combat system
        /// </summary>
        public void Shutdown()
        {
            try
            {
                Debug.Log("Shutting down Combat System...");
                
                // End all active combats
                foreach (var combatId in _activeCombats.Keys)
                {
                    EndCombat(combatId, "system_shutdown");
                }
                
                // Unsubscribe from events
                if (_combatService != null)
                {
                    _combatService.OnCombatStarted -= HandleCombatStarted;
                    _combatService.OnCombatEnded -= HandleCombatEnded;
                }
                
                if (_webSocketHandler != null)
                {
                    _webSocketHandler.OnCombatEventReceived -= HandleCombatEvent;
                    _webSocketHandler.OnCombatStateUpdated -= HandleCombatStateUpdate;
                    _webSocketHandler.DisconnectAsync();
                }
                
                if (combatUIController != null)
                {
                    combatUIController.OnActionSelected -= HandleActionSelected;
                    combatUIController.OnTurnEnded -= HandleTurnEnded;
                    combatUIController.OnCombatExited -= HandleCombatExited;
                }
                
                _isInitialized = false;
                Debug.Log("Combat System shut down");
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error shutting down Combat System: {ex.Message}");
            }
        }
        
        /// <summary>
        /// Start a new combat encounter
        /// </summary>
        public async void StartCombat(List<string> participantIds, string encounterType = "standard")
        {
            if (!_isInitialized)
            {
                Debug.LogError("Combat System not initialized");
                return;
            }
            
            if (_activeCombats.Count >= maxConcurrentCombats)
            {
                Debug.LogWarning("Maximum concurrent combats reached");
                return;
            }
            
            try
            {
                string combatId = await _combatService.StartCombatAsync(participantIds, encounterType);
                
                // If this is a player combat, show UI
                if (participantIds.Contains("player"))
                {
                    _currentPlayerCombatId = combatId;
                    ShowCombatUI(combatId);
                }
                
                Debug.Log($"Combat started: {combatId}");
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to start combat: {ex.Message}");
            }
        }
        
        /// <summary>
        /// End a combat encounter
        /// </summary>
        public async void EndCombat(string combatId, string reason = "completed")
        {
            if (!_isInitialized || string.IsNullOrEmpty(combatId))
            {
                return;
            }
            
            try
            {
                await _combatService.EndCombatAsync(combatId, reason);
                
                // Hide UI if this was the player's combat
                if (combatId == _currentPlayerCombatId)
                {
                    HideCombatUI();
                    _currentPlayerCombatId = null;
                }
                
                Debug.Log($"Combat ended: {combatId}");
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to end combat: {ex.Message}");
            }
        }
        
        /// <summary>
        /// Get the current player combat state
        /// </summary>
        public CombatState GetPlayerCombatState()
        {
            if (string.IsNullOrEmpty(_currentPlayerCombatId))
            {
                return null;
            }
            
            return _activeCombats.TryGetValue(_currentPlayerCombatId, out var state) ? state : null;
        }
        
        /// <summary>
        /// Check if player is currently in combat
        /// </summary>
        public bool IsPlayerInCombat()
        {
            return !string.IsNullOrEmpty(_currentPlayerCombatId);
        }
        
        /// <summary>
        /// Get all active combat IDs
        /// </summary>
        public List<string> GetActiveCombatIds()
        {
            return new List<string>(_activeCombats.Keys);
        }
        
        /// <summary>
        /// Start a test combat for development
        /// </summary>
        [ContextMenu("Start Test Combat")]
        public void StartTestCombat()
        {
            var participants = new List<string> { "player", "test_enemy_1", "test_enemy_2" };
            StartCombat(participants, "test");
        }
        
        private void ShowCombatUI(string combatId)
        {
            if (combatUIController != null)
            {
                combatUIController.InitializeCombat(combatId);
            }
            
            if (combatCanvas != null)
            {
                combatCanvas.gameObject.SetActive(true);
            }
        }
        
        private void HideCombatUI()
        {
            if (combatUIController != null)
            {
                combatUIController.CloseCombat();
            }
            
            if (combatCanvas != null)
            {
                combatCanvas.gameObject.SetActive(false);
            }
        }
        
        private void Update()
        {
            if (!_isInitialized || !IsEnabled)
            {
                return;
            }
            
            // Update combat states periodically
            UpdateCombatStates();
            
            if (_isInitialized && _activeCombats.Count > 0)
            {
                HealthStatus = GetHealthStatus();
            }
        }
        
        private float _lastUpdateTime = 0f;
        
        private void UpdateCombatStates()
        {
            if (Time.time - _lastUpdateTime < combatUpdateInterval)
            {
                return;
            }
            
            _lastUpdateTime = Time.time;
            
            // Update status effects for all active combats
            foreach (var combat in _activeCombats.Values)
            {
                UpdateStatusEffects(combat);
            }
        }
        
        private void UpdateStatusEffects(CombatState combat)
        {
            foreach (var participant in combat.Participants)
            {
                // Update status effects
                for (int i = participant.StatusEffects.Count - 1; i >= 0; i--)
                {
                    var effect = participant.StatusEffects[i];
                    effect.ApplyEffect(participant);
                    
                    if (effect.IsExpired)
                    {
                        participant.StatusEffects.RemoveAt(i);
                        
                        // Notify about effect removal
                        var removeEvent = new CombatEvent
                        {
                            Type = CombatEventType.StatusEffectRemoved,
                            Participant = participant,
                            Message = $"{participant.Name} is no longer affected by {effect.Name}"
                        };
                        
                        OnCombatEventReceived?.Invoke(removeEvent);
                    }
                }
            }
        }
        
        // Event handlers
        private void HandleCombatStarted(string combatId)
        {
            OnCombatStarted?.Invoke(combatId);
        }
        
        private void HandleCombatEnded(string combatId)
        {
            if (_activeCombats.ContainsKey(combatId))
            {
                _activeCombats.Remove(combatId);
            }
            
            OnCombatEnded?.Invoke(combatId);
        }
        
        private void HandleCombatEvent(CombatEvent combatEvent)
        {
            OnCombatEventReceived?.Invoke(combatEvent);
        }
        
        private void HandleCombatStateUpdate(CombatState state)
        {
            _activeCombats[state.CombatId] = state;
        }
        
        private void HandleActionSelected(VDM.DTOs.Combat.CombatActionDTO action, string targetId)
        {
            Debug.Log($"Action selected: {action.Name} -> {targetId}");
        }
        
        private void HandleTurnEnded()
        {
            Debug.Log("Turn ended");
        }
        
        private void HandleCombatExited()
        {
            Debug.Log("Combat UI exited");
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
                { "active_combats", _activeCombats.Count },
                { "player_in_combat", IsPlayerInCombat() },
                { "current_player_combat", _currentPlayerCombatId ?? "none" }
            };
        }
    }
} 