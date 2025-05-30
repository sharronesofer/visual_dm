using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using System;
using UnityEngine;
using VDM.Runtime.Core.Integration;
using VDM.Runtime.Events;
using VDM.Runtime.Religion.Models;
using VDM.Runtime.Religion.Services;
using VDM.Runtime.Religion.UI;


namespace VDM.Runtime.Religion.Integration
{
    /// <summary>
    /// Unity integration manager for the Religion system
    /// Coordinates between UI, services, and Unity-specific functionality
    /// </summary>
    public class ReligionManager : SystemManager<ReligionManager>
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

        protected override void Awake()
        {
            base.Awake();
            InitializeServices();
        }

        protected override void Start()
        {
            base.Start();
            _ = InitializeAsync();
        }

        protected override void Update()
        {
            base.Update();
            
            if (enableAutoRefresh && _isInitialized)
            {
                if (Time.time - _lastRefreshTime > refreshInterval)
                {
                    _ = RefreshReligionsAsync();
                }
            }
        }

        private void InitializeServices()
        {
            try
            {
                var httpClient = FindObjectOfType<HttpClient>();
                if (httpClient == null)
                {
                    Debug.LogError("ReligionManager: HttpClient not found. Religion system will not function properly.");
                    return;
                }

                _religionService = new ReligionService(httpClient);
                
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

        private async Task InitializeAsync()
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
                await RefreshReligionsAsync();

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

        private void SubscribeToEvents()
        {
            // Subscribe to relevant game events
            EventBus.Subscribe<CharacterCreatedEvent>(OnCharacterCreated);
            EventBus.Subscribe<CharacterDeletedEvent>(OnCharacterDeleted);
            EventBus.Subscribe<FactionCreatedEvent>(OnFactionCreated);
            EventBus.Subscribe<RegionCreatedEvent>(OnRegionCreated);
        }

        private void UnsubscribeFromEvents()
        {
            EventBus.Unsubscribe<CharacterCreatedEvent>(OnCharacterCreated);
            EventBus.Unsubscribe<CharacterDeletedEvent>(OnCharacterDeleted);
            EventBus.Unsubscribe<FactionCreatedEvent>(OnFactionCreated);
            EventBus.Unsubscribe<RegionCreatedEvent>(OnRegionCreated);
        }

        #region Public API

        /// <summary>
        /// Get all cached religions
        /// </summary>
        public List<ReligionDTO> GetReligions()
        {
            return _cachedReligions.ToList();
        }

        /// <summary>
        /// Get a specific religion by ID
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
        /// Get religions by region
        /// </summary>
        public List<ReligionDTO> GetReligionsByRegion(string regionId)
        {
            return _cachedReligions.Where(r => r.RegionIds.Contains(regionId)).ToList();
        }

        /// <summary>
        /// Get religions by faction
        /// </summary>
        public List<ReligionDTO> GetReligionsByFaction(string factionId)
        {
            return _cachedReligions.Where(r => r.FactionId == factionId).ToList();
        }

        /// <summary>
        /// Get entity memberships
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
                var response = await _religionService.CreateReligionAsync(request);
                if (response.Success)
                {
                    await RefreshReligionsAsync();
                    return response.Data;
                }
                
                Debug.LogError($"Failed to create religion: {response.Message}");
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
                var response = await _religionService.UpdateReligionAsync(religionId, request);
                if (response.Success)
                {
                    await RefreshReligionsAsync();
                    return response.Data;
                }
                
                Debug.LogError($"Failed to update religion: {response.Message}");
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
                var response = await _religionService.DeleteReligionAsync(religionId);
                if (response.Success)
                {
                    await RefreshReligionsAsync();
                    return true;
                }
                
                Debug.LogError($"Failed to delete religion: {response.Message}");
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
                var response = await _religionService.JoinReligionAsync(entityId, religionId, devotionLevel);
                if (response.Success)
                {
                    await RefreshEntityMembershipsAsync(entityId);
                    return response.Data;
                }
                
                Debug.LogError($"Failed to join religion: {response.Message}");
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
                var response = await _religionService.LeaveReligionAsync(entityId, religionId);
                if (response.Success)
                {
                    await RefreshEntityMembershipsAsync(entityId);
                    return true;
                }
                
                Debug.LogError($"Failed to leave religion: {response.Message}");
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
                var response = await _religionService.GetReligionsAsync();
                if (response.Success)
                {
                    _cachedReligions = response.Data ?? new List<ReligionDTO>();
                    _lastRefreshTime = Time.time;
                    OnReligionsLoaded?.Invoke(_cachedReligions);
                    
                    if (debugMode)
                    {
                        Debug.Log($"ReligionManager: Loaded {_cachedReligions.Count} religions");
                    }
                }
                else
                {
                    Debug.LogError($"Failed to refresh religions: {response.Message}");
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
                var response = await _religionService.GetEntityMembershipsAsync(entityId);
                if (response.Success)
                {
                    _cachedMemberships[entityId] = response.Data ?? new List<ReligionMembershipDTO>();
                    
                    if (debugMode)
                    {
                        Debug.Log($"ReligionManager: Loaded {_cachedMemberships[entityId].Count} memberships for entity {entityId}");
                    }
                }
                else
                {
                    Debug.LogError($"Failed to refresh memberships for entity {entityId}: {response.Message}");
                }
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
            if (logReligionEvents)
            {
                Debug.Log($"Religion created: {religion.Name}");
            }
            
            OnReligionCreated?.Invoke(religion);
            
            // Broadcast event
            EventBus.Publish(new ReligionCreatedEvent { Religion = religion });
        }

        private void HandleReligionUpdated(ReligionDTO religion)
        {
            if (logReligionEvents)
            {
                Debug.Log($"Religion updated: {religion.Name}");
            }
            
            OnReligionUpdated?.Invoke(religion);
            
            // Broadcast event
            EventBus.Publish(new ReligionUpdatedEvent { Religion = religion });
        }

        private void HandleReligionDeleted(string religionId)
        {
            if (logReligionEvents)
            {
                Debug.Log($"Religion deleted: {religionId}");
            }
            
            OnReligionDeleted?.Invoke(religionId);
            
            // Broadcast event
            EventBus.Publish(new ReligionDeletedEvent { ReligionId = religionId });
        }

        private void HandleReligionSelected(ReligionDTO religion)
        {
            if (logReligionEvents)
            {
                Debug.Log($"Religion selected: {religion.Name}");
            }
            
            // Broadcast event
            EventBus.Publish(new ReligionSelectedEvent { Religion = religion });
        }

        private void OnCharacterCreated(CharacterCreatedEvent evt)
        {
            // Optionally load memberships for new character
            if (enableAutoRefresh)
            {
                _ = RefreshEntityMembershipsAsync(evt.CharacterId);
            }
        }

        private void OnCharacterDeleted(CharacterDeletedEvent evt)
        {
            // Clean up cached memberships
            _cachedMemberships.Remove(evt.CharacterId);
        }

        private void OnFactionCreated(FactionCreatedEvent evt)
        {
            // Refresh religions as new faction might affect religion data
            if (enableAutoRefresh)
            {
                _ = RefreshReligionsAsync();
            }
        }

        private void OnRegionCreated(RegionCreatedEvent evt)
        {
            // Refresh religions as new region might affect religion data
            if (enableAutoRefresh)
            {
                _ = RefreshReligionsAsync();
            }
        }

        #endregion

        #region Unity Lifecycle

        protected override void OnDestroy()
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

    public class ReligionCreatedEvent : IEvent
    {
        public ReligionDTO Religion { get; set; }
    }

    public class ReligionUpdatedEvent : IEvent
    {
        public ReligionDTO Religion { get; set; }
    }

    public class ReligionDeletedEvent : IEvent
    {
        public string ReligionId { get; set; }
    }

    public class ReligionSelectedEvent : IEvent
    {
        public ReligionDTO Religion { get; set; }
    }

    public class ReligionMembershipChangedEvent : IEvent
    {
        public string EntityId { get; set; }
        public string ReligionId { get; set; }
        public bool IsJoining { get; set; }
        public float DevotionLevel { get; set; }
    }

    #endregion
} 