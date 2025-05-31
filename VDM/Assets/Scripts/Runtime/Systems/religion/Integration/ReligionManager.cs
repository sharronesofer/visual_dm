using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using UnityEngine;
using VDM.DTOs.Common;
using VDM.Systems.Religion.Services;
using VDM.Systems.Religion.Ui;
using VDM.Systems.Faction.Models;
using VDM.Systems.Events.Integration;
using VDM.Infrastructure.Services;

namespace VDM.Systems.Religion.Integration
{
    /// <summary>
    /// Unity integration manager for the Religion system
    /// Coordinates between UI, services, and Unity-specific functionality
    /// </summary>
    public class ReligionManager : SystemManager
    {
        [Header("Religion System Configuration")]
        [SerializeField] private bool enableAutoRefresh = true;
        [SerializeField] private float refreshInterval = 30f;
        [SerializeField] private bool enableRealTimeUpdates = true;
        [SerializeField] private bool enableNotifications = true;

        [Header("UI References")]
        [SerializeField] private ReligionPanelController religionPanel;
        [SerializeField] private GameObject religionPanelPrefab;

        [Header("Debug Settings")]
        [SerializeField] private bool debugMode = false;
        [SerializeField] private bool logReligionEvents = false;

        // Services
        private ReligionService _religionService;
        
        // State
        private List<ReligionDTO> _cachedReligions = new();
        private Dictionary<string, List<ReligionMembershipDTO>> _cachedMemberships = new();
        private float _lastRefreshTime;
        private bool _isInitialized = false;

        // Events
        public event Action<ReligionDTO> OnReligionCreated;
        public event Action<ReligionDTO> OnReligionUpdated;
        public event Action<string> OnReligionDeleted;
        public event Action<ReligionMembershipDTO> OnMembershipChanged;
        public event Action<List<ReligionDTO>> OnReligionsLoaded;

        protected void Awake()
        {
            InitializeServices();
        }

        private void InitializeServices()
        {
            try
            {
                _religionService = new ReligionService();
                
                if (debugMode)
                {
                    Debug.Log("ReligionManager: Services initialized successfully");
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"ReligionManager: Failed to initialize services: {ex.Message}");
            }
        }

        protected override void OnInitializeSystem()
        {
            try
            {
                if (_religionService == null)
                {
                    Debug.LogError("ReligionManager: Cannot initialize - services not available");
                    return;
                }

                // Initialize UI if not already set
                if (religionPanel == null && religionPanelPrefab != null)
                {
                    var panelObj = Instantiate(religionPanelPrefab);
                    religionPanel = panelObj.GetComponent<ReligionPanelController>();
                }

                // Setup UI event handlers
                if (religionPanel != null)
                {
                    religionPanel.OnReligionCreated += HandleReligionCreated;
                    religionPanel.OnReligionUpdated += HandleReligionUpdated;
                    religionPanel.OnReligionDeleted += HandleReligionDeleted;
                    religionPanel.OnReligionSelected += HandleReligionSelected;
                }

                // Load initial data
                _ = RefreshReligionsAsync();

                // Subscribe to events
                SubscribeToEvents();

                _isInitialized = true;
                
                if (debugMode)
                {
                    Debug.Log("ReligionManager: Initialization completed successfully");
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"ReligionManager: Initialization failed: {ex.Message}");
            }
        }

        protected override void OnShutdownSystem()
        {
            try
            {
                // Unsubscribe from events
                UnsubscribeFromEvents();

                // Cleanup UI event handlers
                if (religionPanel != null)
                {
                    religionPanel.OnReligionCreated -= HandleReligionCreated;
                    religionPanel.OnReligionUpdated -= HandleReligionUpdated;
                    religionPanel.OnReligionDeleted -= HandleReligionDeleted;
                    religionPanel.OnReligionSelected -= HandleReligionSelected;
                }

                // Clear caches
                _cachedReligions.Clear();
                _cachedMemberships.Clear();

                _isInitialized = false;
                
                if (debugMode)
                {
                    Debug.Log("ReligionManager: Shutdown completed successfully");
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"ReligionManager: Shutdown failed: {ex.Message}");
            }
        }

        private void SubscribeToEvents()
        {
            // Subscribe to relevant game events when the event system is available
            if (debugMode)
            {
                Debug.Log("ReligionManager: Events subscribed");
            }
        }

        private void UnsubscribeFromEvents()
        {
            // Unsubscribe from events when the event system is available
            if (debugMode)
            {
                Debug.Log("ReligionManager: Events unsubscribed");
            }
        }

        #region Public Methods

        /// <summary>
        /// Get cached religions
        /// </summary>
        public List<ReligionDTO> GetReligions()
        {
            return _cachedReligions.ToList();
        }

        /// <summary>
        /// Get religion by ID
        /// </summary>
        public ReligionDTO GetReligion(string religionId)
        {
            return _cachedReligions.FirstOrDefault(r => r.Id == religionId);
        }

        /// <summary>
        /// Get religions by type
        /// </summary>
        public List<ReligionDTO> GetReligionsByType(ReligionType type)
        {
            return _cachedReligions.Where(r => r.Type == type).ToList();
        }

        /// <summary>
        /// Get entity memberships from cache
        /// </summary>
        public List<ReligionMembershipDTO> GetEntityMemberships(string entityId)
        {
            return _cachedMemberships.TryGetValue(entityId, out var memberships) 
                ? memberships.ToList() 
                : new List<ReligionMembershipDTO>();
        }

        /// <summary>
        /// Check if entity is member of religion
        /// </summary>
        public bool IsEntityMember(string entityId, string religionId)
        {
            var memberships = GetEntityMemberships(entityId);
            return memberships.Any(m => m.ReligionId == religionId);
        }

        /// <summary>
        /// Get entity devotion level to religion
        /// </summary>
        public float GetEntityDevotion(string entityId, string religionId)
        {
            var memberships = GetEntityMemberships(entityId);
            var membership = memberships.FirstOrDefault(m => m.ReligionId == religionId);
            return membership?.DevotionLevel ?? 0f;
        }

        /// <summary>
        /// Create a new religion
        /// </summary>
        public async Task<ReligionDTO> CreateReligionAsync(CreateReligionRequestDTO request)
        {
            try
            {
                var result = await _religionService.CreateReligionAsync(request);
                if (result != null)
                {
                    await RefreshReligionsAsync();
                    return result;
                }
                
                Debug.LogError("Failed to create religion");
                return null;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error creating religion: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Update an existing religion
        /// </summary>
        public async Task<ReligionDTO> UpdateReligionAsync(string religionId, UpdateReligionRequestDTO request)
        {
            try
            {
                var result = await _religionService.UpdateReligionAsync(religionId, request);
                if (result != null)
                {
                    await RefreshReligionsAsync();
                    return result;
                }
                
                Debug.LogError("Failed to update religion");
                return null;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error updating religion: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Delete a religion
        /// </summary>
        public async Task<bool> DeleteReligionAsync(string religionId)
        {
            try
            {
                var result = await _religionService.DeleteReligionAsync(religionId);
                if (result)
                {
                    await RefreshReligionsAsync();
                    return true;
                }
                
                Debug.LogError("Failed to delete religion");
                return false;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error deleting religion: {ex.Message}");
                return false;
            }
        }

        /// <summary>
        /// Join a religion
        /// </summary>
        public async Task<ReligionMembershipDTO> JoinReligionAsync(string entityId, string religionId, float devotionLevel = 0.5f)
        {
            try
            {
                // This would need to be implemented when entity membership system is available
                Debug.Log($"Join religion {religionId} for entity {entityId} with devotion {devotionLevel}");
                return null;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error joining religion: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Leave a religion
        /// </summary>
        public async Task<bool> LeaveReligionAsync(string entityId, string religionId)
        {
            try
            {
                // This would need to be implemented when entity membership system is available
                Debug.Log($"Leave religion {religionId} for entity {entityId}");
                return false;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error leaving religion: {ex.Message}");
                return false;
            }
        }

        /// <summary>
        /// Show religion panel for entity
        /// </summary>
        public void ShowReligionPanel(string entityId = null)
        {
            if (religionPanel != null)
            {
                religionPanel.gameObject.SetActive(true);
                religionPanel.Initialize(entityId);
            }
            else
            {
                Debug.LogWarning("ReligionManager: Religion panel not available");
            }
        }

        /// <summary>
        /// Hide religion panel
        /// </summary>
        public void HideReligionPanel()
        {
            if (religionPanel != null)
            {
                religionPanel.gameObject.SetActive(false);
            }
        }

        /// <summary>
        /// Refresh religions from server
        /// </summary>
        public async Task RefreshReligionsAsync()
        {
            try
            {
                _cachedReligions = await _religionService.GetReligionsAsync();
                _lastRefreshTime = Time.time;
                OnReligionsLoaded?.Invoke(_cachedReligions);
                
                if (debugMode)
                {
                    Debug.Log($"ReligionManager: Loaded {_cachedReligions.Count} religions");
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error refreshing religions: {ex.Message}");
            }
        }

        /// <summary>
        /// Refresh entity memberships
        /// </summary>
        public async Task RefreshEntityMembershipsAsync(string entityId)
        {
            try
            {
                // This would need to be implemented when entity membership system is available
                Debug.Log($"Refreshing memberships for entity: {entityId}");
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error refreshing memberships for entity {entityId}: {ex.Message}");
            }
        }

        #endregion

        #region Event Handlers

        private void HandleReligionCreated(ReligionDTO religion)
        {
            OnReligionCreated?.Invoke(religion);
            
            if (logReligionEvents)
            {
                Debug.Log($"Religion created: {religion.Name}");
            }
        }

        private void HandleReligionUpdated(ReligionDTO religion)
        {
            OnReligionUpdated?.Invoke(religion);
            
            if (logReligionEvents)
            {
                Debug.Log($"Religion updated: {religion.Name}");
            }
        }

        private void HandleReligionDeleted(string religionId)
        {
            OnReligionDeleted?.Invoke(religionId);
            
            if (logReligionEvents)
            {
                Debug.Log($"Religion deleted: {religionId}");
            }
        }

        private void HandleReligionSelected(ReligionDTO religion)
        {
            if (logReligionEvents)
            {
                Debug.Log($"Religion selected: {religion.Name}");
            }
        }

        private void HandleMembershipChanged(ReligionMembershipDTO membership)
        {
            OnMembershipChanged?.Invoke(membership);
            
            if (logReligionEvents)
            {
                Debug.Log($"Membership changed: {membership.EntityId} - {membership.ReligionId}");
            }
        }

        // Game event handlers
        private void OnCharacterCreated(CharacterCreatedEvent evt)
        {
            if (logReligionEvents)
            {
                Debug.Log($"ReligionManager: Character created - {evt.Character.Name}");
            }
        }

        private void OnCharacterDeleted(CharacterDeletedEvent evt)
        {
            // Remove memberships for deleted character
            if (_cachedMemberships.ContainsKey(evt.CharacterId))
            {
                _cachedMemberships.Remove(evt.CharacterId);
            }
            
            if (logReligionEvents)
            {
                Debug.Log($"ReligionManager: Character deleted - {evt.CharacterId}");
            }
        }

        private void OnFactionCreated(FactionCreatedEvent evt)
        {
            // Factions might have state religions
            if (logReligionEvents)
            {
                Debug.Log($"ReligionManager: Faction created - {evt.Faction.Name}");
            }
        }

        private void OnRegionCreated(RegionCreatedEvent evt)
        {
            // Regions might have dominant religions
            if (logReligionEvents)
            {
                Debug.Log($"ReligionManager: Region created - {evt.Region.Name}");
            }
        }

        #endregion

        #region Unity Lifecycle

        private void Update()
        {
            if (!_isInitialized || !enableAutoRefresh) return;

            // Auto-refresh religions periodically
            if (Time.time - _lastRefreshTime > refreshInterval)
            {
                _ = RefreshReligionsAsync();
            }
        }

        private void OnDestroy()
        {
            UnsubscribeFromEvents();
            
            if (religionPanel != null)
            {
                religionPanel.OnReligionCreated -= HandleReligionCreated;
                religionPanel.OnReligionUpdated -= HandleReligionUpdated;
                religionPanel.OnReligionDeleted -= HandleReligionDeleted;
                religionPanel.OnReligionSelected -= HandleReligionSelected;
            }
            
            base.OnDestroy();
        }

        #endregion
    }

    #region Religion Events

    public class ReligionCreatedEvent : GameEvent
    {
        public ReligionDTO Religion { get; set; }
    }

    public class ReligionUpdatedEvent : GameEvent
    {
        public ReligionDTO Religion { get; set; }
    }

    public class ReligionDeletedEvent : GameEvent
    {
        public string ReligionId { get; set; }
    }

    public class ReligionSelectedEvent : GameEvent
    {
        public ReligionDTO Religion { get; set; }
    }

    public class ReligionMembershipChangedEvent : GameEvent
    {
        public string EntityId { get; set; }
        public string ReligionId { get; set; }
        public bool IsJoining { get; set; }
        public float DevotionLevel { get; set; }
    }

    public class FactionCreatedEvent : GameEvent
    {
        public FactionDTO Faction { get; set; }
    }

    public class RegionCreatedEvent : GameEvent
    {
        public RegionDTO Region { get; set; }
    }

    #endregion
} 