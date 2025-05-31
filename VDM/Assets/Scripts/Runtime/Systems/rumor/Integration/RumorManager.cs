using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using System;
using UnityEngine;
using VDM.Systems.Events.Integration;
using VDM.Infrastructure.Services;
using VDM.DTOs.Common;
using VDM.Systems.Rumor.Services;
using VDM.Systems.Rumor.Ui;


namespace VDM.Systems.Rumor.Integration
{
    /// <summary>
    /// Manager for the Rumor system, coordinating between services and UI
    /// </summary>
    public class RumorManager : SystemManager
    {
        [Header("Rumor Configuration")]
        [SerializeField] private string apiBaseUrl = "http://localhost:8000";
        [SerializeField] private float autoRefreshInterval = 30f;
        [SerializeField] private int maxCachedRumors = 100;
        [SerializeField] private bool enableAutoDecay = true;
        [SerializeField] private float decayInterval = 3600f; // 1 hour in seconds

        [Header("UI References")]
        [SerializeField] private RumorPanelController rumorPanelController;

        // Services
        private RumorService rumorService;

        // Caching
        private Dictionary<string, RumorDTO> rumorCache = new Dictionary<string, RumorDTO>();
        private Dictionary<string, List<RumorDTO>> entityRumorCache = new Dictionary<string, List<RumorDTO>>();
        private DateTime lastCacheUpdate = DateTime.MinValue;

        // Auto-refresh
        private float lastRefreshTime;
        private float lastDecayTime;

        public override string SystemName => "Rumor System";
        public string SystemVersion => "1.0.0";

        #region SystemManager Implementation

        protected override void OnInitializeSystem()
        {
            try
            {
                Debug.Log("[RumorManager] Initializing Rumor System...");

                // Initialize service
                rumorService = new RumorService(apiBaseUrl);

                // Initialize UI
                if (rumorPanelController != null)
                {
                    rumorPanelController.Initialize(rumorService);
                }

                // Subscribe to events
                SubscribeToEvents();

                // Initial data load
                _ = RefreshRumorCacheAsync();

                Debug.Log("[RumorManager] Rumor System initialized successfully");
            }
            catch (Exception ex)
            {
                Debug.LogError($"[RumorManager] Failed to initialize Rumor System: {ex.Message}");
            }
        }

        protected override void OnShutdownSystem()
        {
            try
            {
                Debug.Log("[RumorManager] Shutting down Rumor System...");

                // Unsubscribe from events
                UnsubscribeFromEvents();

                // Clear caches
                rumorCache.Clear();
                entityRumorCache.Clear();

                Debug.Log("[RumorManager] Rumor System shutdown complete");
            }
            catch (Exception ex)
            {
                Debug.LogError($"[RumorManager] Error during Rumor System shutdown: {ex.Message}");
            }
        }

        protected override void OnUpdateSystem()
        {
            // Auto-refresh cache
            if (Time.time - lastRefreshTime >= autoRefreshInterval)
            {
                _ = RefreshRumorCacheAsync();
                lastRefreshTime = Time.time;
            }

            // Auto-decay rumors
            if (enableAutoDecay && Time.time - lastDecayTime >= decayInterval)
            {
                _ = ApplyRumorDecayAsync();
                lastDecayTime = Time.time;
            }
        }

        #endregion

        #region Event Management

        private void SubscribeToEvents()
        {
            EventBus.Instance.Subscribe<CharacterCreatedEvent>(OnCharacterCreated);
            EventBus.Instance.Subscribe<CharacterDeletedEvent>(OnCharacterDeleted);
            EventBus.Instance.Subscribe<FactionCreatedEvent>(OnFactionCreated);
            EventBus.Instance.Subscribe<FactionDeletedEvent>(OnFactionDeleted);
            EventBus.Instance.Subscribe<RegionCreatedEvent>(OnRegionCreated);
            EventBus.Instance.Subscribe<RegionDeletedEvent>(OnRegionDeleted);
        }

        private void UnsubscribeFromEvents()
        {
            EventBus.Instance.Unsubscribe<CharacterCreatedEvent>(OnCharacterCreated);
            EventBus.Instance.Unsubscribe<CharacterDeletedEvent>(OnCharacterDeleted);
            EventBus.Instance.Unsubscribe<FactionCreatedEvent>(OnFactionCreated);
            EventBus.Instance.Unsubscribe<FactionDeletedEvent>(OnFactionDeleted);
            EventBus.Instance.Unsubscribe<RegionCreatedEvent>(OnRegionCreated);
            EventBus.Instance.Unsubscribe<RegionDeletedEvent>(OnRegionDeleted);
        }

        #endregion

        #region Public API

        /// <summary>
        /// Create a new rumor
        /// </summary>
        /// <param name="originatorId">ID of the entity creating the rumor</param>
        /// <param name="content">Content of the rumor</param>
        /// <param name="categories">Categories for the rumor</param>
        /// <param name="severity">Severity level</param>
        /// <param name="truthValue">How true the rumor is (0.0 to 1.0)</param>
        /// <returns>Created rumor</returns>
        public async Task<RumorDTO> CreateRumorAsync(
            string originatorId, 
            string content, 
            List<RumorCategory> categories = null, 
            RumorSeverity severity = RumorSeverity.Minor, 
            float truthValue = 0.5f)
        {
            try
            {
                var request = new CreateRumorRequestDTO
                {
                    OriginatorId = originatorId,
                    Content = content,
                    Categories = categories?.Select(c => c.ToString().ToLower()).ToList() ?? new List<string> { "other" },
                    Severity = severity.ToString().ToLower(),
                    TruthValue = Mathf.Clamp01(truthValue)
                };

                var rumor = await rumorService.CreateRumorAsync(request);
                
                if (rumor != null)
                {
                    // Update cache
                    rumorCache[rumor.Id] = rumor;
                    InvalidateEntityCache(originatorId);

                    // Emit event
                    EventBus.Instance.Publish(new RumorCreatedEvent
                    {
                        RumorId = rumor.Id,
                        OriginatorId = originatorId,
                        Content = content,
                        Categories = categories?.Select(c => c.ToString()).ToList() ?? new List<string>(),
                        Severity = severity.ToString(),
                        TruthValue = truthValue
                    });

                    Debug.Log($"[RumorManager] Created rumor: {rumor.Id}");
                }

                return rumor;
            }
            catch (Exception ex)
            {
                Debug.LogError($"[RumorManager] Failed to create rumor: {ex.Message}");
                throw;
            }
        }

        /// <summary>
        /// Spread a rumor from one entity to another
        /// </summary>
        /// <param name="rumorId">ID of the rumor to spread</param>
        /// <param name="fromEntityId">ID of the entity spreading the rumor</param>
        /// <param name="toEntityId">ID of the entity receiving the rumor</param>
        /// <param name="mutationProbability">Probability of mutation (0.0 to 1.0)</param>
        /// <param name="relationshipFactor">Relationship strength (-1.0 to 1.0)</param>
        /// <returns>True if spread was successful</returns>
        public async Task<bool> SpreadRumorAsync(
            string rumorId, 
            string fromEntityId, 
            string toEntityId, 
            float mutationProbability = 0.2f, 
            float? relationshipFactor = null)
        {
            try
            {
                var request = new SpreadRumorRequestDTO
                {
                    RumorId = rumorId,
                    FromEntityId = fromEntityId,
                    ToEntityId = toEntityId,
                    MutationProbability = Mathf.Clamp01(mutationProbability),
                    RelationshipFactor = relationshipFactor
                };

                var result = await rumorService.SpreadRumorAsync(request);
                
                if (result?.Success == true)
                {
                    // Invalidate caches
                    rumorCache.Remove(rumorId);
                    InvalidateEntityCache(fromEntityId);
                    InvalidateEntityCache(toEntityId);

                    // Emit event
                    EventBus.Instance.Publish(new RumorSpreadEvent
                    {
                        RumorId = rumorId,
                        FromEntityId = fromEntityId,
                        ToEntityId = toEntityId,
                        MutationProbability = mutationProbability,
                        RelationshipFactor = relationshipFactor
                    });

                    Debug.Log($"[RumorManager] Spread rumor {rumorId} from {fromEntityId} to {toEntityId}");
                    return true;
                }

                return false;
            }
            catch (Exception ex)
            {
                Debug.LogError($"[RumorManager] Failed to spread rumor: {ex.Message}");
                return false;
            }
        }

        /// <summary>
        /// Get a rumor by ID
        /// </summary>
        /// <param name="rumorId">ID of the rumor</param>
        /// <param name="useCache">Whether to use cached data</param>
        /// <returns>Rumor data</returns>
        public async Task<RumorDTO> GetRumorAsync(string rumorId, bool useCache = true)
        {
            try
            {
                // Check cache first
                if (useCache && rumorCache.TryGetValue(rumorId, out var cachedRumor))
                {
                    return cachedRumor;
                }

                // Fetch from service
                var rumor = await rumorService.GetRumorAsync(rumorId);
                
                if (rumor != null)
                {
                    rumorCache[rumorId] = rumor;
                }

                return rumor;
            }
            catch (Exception ex)
            {
                Debug.LogError($"[RumorManager] Failed to get rumor {rumorId}: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Get all rumors known to an entity
        /// </summary>
        /// <param name="entityId">ID of the entity</param>
        /// <param name="useCache">Whether to use cached data</param>
        /// <returns>List of rumors known to the entity</returns>
        public async Task<List<RumorDTO>> GetEntityRumorsAsync(string entityId, bool useCache = true)
        {
            try
            {
                // Check cache first
                if (useCache && entityRumorCache.TryGetValue(entityId, out var cachedRumors))
                {
                    return cachedRumors;
                }

                // Fetch from service
                var response = await rumorService.GetEntityRumorsAsync(entityId);
                var rumors = response?.Rumors ?? new List<RumorDTO>();

                // Update cache
                entityRumorCache[entityId] = rumors;

                return rumors;
            }
            catch (Exception ex)
            {
                Debug.LogError($"[RumorManager] Failed to get rumors for entity {entityId}: {ex.Message}");
                return new List<RumorDTO>();
            }
        }

        /// <summary>
        /// Get rumors by category
        /// </summary>
        /// <param name="category">Category to filter by</param>
        /// <param name="limit">Maximum number of results</param>
        /// <returns>Filtered rumors</returns>
        public async Task<List<RumorDTO>> GetRumorsByCategoryAsync(RumorCategory category, int limit = 10)
        {
            try
            {
                var response = await rumorService.GetRumorsByCategoryAsync(category, limit);
                return response?.Rumors ?? new List<RumorDTO>();
            }
            catch (Exception ex)
            {
                Debug.LogError($"[RumorManager] Failed to get rumors by category {category}: {ex.Message}");
                return new List<RumorDTO>();
            }
        }

        /// <summary>
        /// Get rumors by minimum severity
        /// </summary>
        /// <param name="severity">Minimum severity level</param>
        /// <param name="limit">Maximum number of results</param>
        /// <returns>Filtered rumors</returns>
        public async Task<List<RumorDTO>> GetRumorsBySeverityAsync(RumorSeverity severity, int limit = 10)
        {
            try
            {
                var response = await rumorService.GetRumorsBySeverityAsync(severity, limit);
                return response?.Rumors ?? new List<RumorDTO>();
            }
            catch (Exception ex)
            {
                Debug.LogError($"[RumorManager] Failed to get rumors by severity {severity}: {ex.Message}");
                return new List<RumorDTO>();
            }
        }

        /// <summary>
        /// Get highly believable rumors for an entity
        /// </summary>
        /// <param name="entityId">ID of the entity</param>
        /// <param name="minBelievability">Minimum believability threshold</param>
        /// <param name="limit">Maximum number of results</param>
        /// <returns>Believable rumors</returns>
        public async Task<List<RumorDTO>> GetBelievableRumorsAsync(
            string entityId, 
            float minBelievability = 0.7f, 
            int limit = 10)
        {
            try
            {
                var response = await rumorService.GetBelievableRumorsAsync(entityId, minBelievability, limit);
                return response?.Rumors ?? new List<RumorDTO>();
            }
            catch (Exception ex)
            {
                Debug.LogError($"[RumorManager] Failed to get believable rumors for entity {entityId}: {ex.Message}");
                return new List<RumorDTO>();
            }
        }

        /// <summary>
        /// Delete a rumor
        /// </summary>
        /// <param name="rumorId">ID of the rumor to delete</param>
        /// <returns>True if deletion was successful</returns>
        public async Task<bool> DeleteRumorAsync(string rumorId)
        {
            try
            {
                var result = await rumorService.DeleteRumorAsync(rumorId);
                
                if (result?.Success == true)
                {
                    // Remove from cache
                    rumorCache.Remove(rumorId);
                    
                    // Clear entity caches (rumor might be known by multiple entities)
                    entityRumorCache.Clear();

                    // Emit event
                    EventBus.Instance.Publish(new RumorDeletedEvent
                    {
                        RumorId = rumorId
                    });

                    Debug.Log($"[RumorManager] Deleted rumor: {rumorId}");
                    return true;
                }

                return false;
            }
            catch (Exception ex)
            {
                Debug.LogError($"[RumorManager] Failed to delete rumor {rumorId}: {ex.Message}");
                return false;
            }
        }

        /// <summary>
        /// Apply decay to all rumors
        /// </summary>
        /// <param name="days">Days since last reinforcement to consider for decay</param>
        /// <returns>True if decay was applied successfully</returns>
        public async Task<bool> ApplyRumorDecayAsync(int days = 7)
        {
            try
            {
                var result = await rumorService.DecayRumorsAsync(days);
                
                if (result?.Success == true)
                {
                    // Clear all caches as believability values may have changed
                    rumorCache.Clear();
                    entityRumorCache.Clear();

                    // Emit event
                    EventBus.Instance.Publish(new RumorDecayAppliedEvent
                    {
                        Days = days,
                        AppliedAt = DateTime.UtcNow
                    });

                    Debug.Log($"[RumorManager] Applied rumor decay for {days} days");
                    return true;
                }

                return false;
            }
            catch (Exception ex)
            {
                Debug.LogError($"[RumorManager] Failed to apply rumor decay: {ex.Message}");
                return false;
            }
        }

        /// <summary>
        /// Check if an entity knows a specific rumor
        /// </summary>
        /// <param name="rumorId">ID of the rumor</param>
        /// <param name="entityId">ID of the entity</param>
        /// <returns>True if entity knows the rumor</returns>
        public async Task<bool> EntityKnowsRumorAsync(string rumorId, string entityId)
        {
            try
            {
                return await rumorService.EntityKnowsRumorAsync(rumorId, entityId);
            }
            catch (Exception ex)
            {
                Debug.LogError($"[RumorManager] Failed to check if entity knows rumor: {ex.Message}");
                return false;
            }
        }

        /// <summary>
        /// Get rumor content as known to a specific entity
        /// </summary>
        /// <param name="rumorId">ID of the rumor</param>
        /// <param name="entityId">ID of the entity</param>
        /// <returns>Content as known to the entity, or null if unknown</returns>
        public async Task<string> GetRumorContentForEntityAsync(string rumorId, string entityId)
        {
            try
            {
                return await rumorService.GetRumorContentForEntityAsync(rumorId, entityId);
            }
            catch (Exception ex)
            {
                Debug.LogError($"[RumorManager] Failed to get rumor content for entity: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Get believability of a rumor for a specific entity
        /// </summary>
        /// <param name="rumorId">ID of the rumor</param>
        /// <param name="entityId">ID of the entity</param>
        /// <returns>Believability value, or null if entity doesn't know the rumor</returns>
        public async Task<float?> GetRumorBelievabilityForEntityAsync(string rumorId, string entityId)
        {
            try
            {
                return await rumorService.GetRumorBelievabilityForEntityAsync(rumorId, entityId);
            }
            catch (Exception ex)
            {
                Debug.LogError($"[RumorManager] Failed to get rumor believability for entity: {ex.Message}");
                return null;
            }
        }

        #endregion

        #region Cache Management

        private async Task RefreshRumorCacheAsync()
        {
            try
            {
                var response = await rumorService.ListRumorsAsync(limit: maxCachedRumors);
                var rumors = response?.Rumors ?? new List<RumorDTO>();

                // Update cache
                rumorCache.Clear();
                foreach (var rumor in rumors)
                {
                    rumorCache[rumor.Id] = rumor;
                }

                lastCacheUpdate = DateTime.UtcNow;
                Debug.Log($"[RumorManager] Refreshed cache with {rumors.Count} rumors");
            }
            catch (Exception ex)
            {
                Debug.LogError($"[RumorManager] Failed to refresh rumor cache: {ex.Message}");
            }
        }

        private void InvalidateEntityCache(string entityId)
        {
            entityRumorCache.Remove(entityId);
        }

        private void ClearAllCaches()
        {
            rumorCache.Clear();
            entityRumorCache.Clear();
        }

        #endregion

        #region Event Handlers

        private void OnCharacterCreated(CharacterCreatedEvent eventData)
        {
            Debug.Log($"[RumorManager] Character created: {eventData.CharacterId}");
            // Character creation doesn't require immediate action for rumors
        }

        private void OnCharacterDeleted(CharacterDeletedEvent eventData)
        {
            Debug.Log($"[RumorManager] Character deleted: {eventData.CharacterId}");
            // Remove from entity cache
            InvalidateEntityCache(eventData.CharacterId);
        }

        private void OnFactionCreated(FactionCreatedEvent eventData)
        {
            Debug.Log($"[RumorManager] Faction created: {eventData.FactionId}");
            // Faction creation doesn't require immediate action for rumors
        }

        private void OnFactionDeleted(FactionDeletedEvent eventData)
        {
            Debug.Log($"[RumorManager] Faction deleted: {eventData.FactionId}");
            // Remove from entity cache
            InvalidateEntityCache(eventData.FactionId);
        }

        private void OnRegionCreated(RegionCreatedEvent eventData)
        {
            Debug.Log($"[RumorManager] Region created: {eventData.RegionId}");
            // Region creation doesn't require immediate action for rumors
        }

        private void OnRegionDeleted(RegionDeletedEvent eventData)
        {
            Debug.Log($"[RumorManager] Region deleted: {eventData.RegionId}");
            // Region deletion doesn't directly affect rumors, but may affect entities
        }

        #endregion
    }

    #region Events

    public class RumorCreatedEvent
    {
        public string RumorId { get; set; }
        public string OriginatorId { get; set; }
        public string Content { get; set; }
        public List<string> Categories { get; set; }
        public string Severity { get; set; }
        public float TruthValue { get; set; }
        public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    }

    public class RumorSpreadEvent
    {
        public string RumorId { get; set; }
        public string FromEntityId { get; set; }
        public string ToEntityId { get; set; }
        public float MutationProbability { get; set; }
        public float? RelationshipFactor { get; set; }
        public DateTime SpreadAt { get; set; } = DateTime.UtcNow;
    }

    public class RumorDeletedEvent
    {
        public string RumorId { get; set; }
        public DateTime DeletedAt { get; set; } = DateTime.UtcNow;
    }

    public class RumorDecayAppliedEvent
    {
        public int Days { get; set; }
        public DateTime AppliedAt { get; set; }
    }

    // External events we listen to
    public class CharacterCreatedEvent
    {
        public string CharacterId { get; set; }
    }

    public class CharacterDeletedEvent
    {
        public string CharacterId { get; set; }
    }

    public class FactionCreatedEvent
    {
        public string FactionId { get; set; }
    }

    public class FactionDeletedEvent
    {
        public string FactionId { get; set; }
    }

    public class RegionCreatedEvent
    {
        public string RegionId { get; set; }
    }

    public class RegionDeletedEvent
    {
        public string RegionId { get; set; }
    }

    #endregion
} 