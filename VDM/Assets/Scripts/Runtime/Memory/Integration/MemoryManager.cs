using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using System;
using UnityEngine;
using VDM.Runtime.Core.Models;
using VDM.Runtime.Core.Systems;
using VDM.Runtime.Events;
using VDM.Runtime.Memory.Models;
using VDM.Runtime.Memory.Services;


namespace VDM.Runtime.Memory.Integration
{
    /// <summary>
    /// Integration manager for memory system - handles caching, events, and coordination
    /// </summary>
    public class MemoryManager : SystemManager
    {
        [Header("Memory System Configuration")]
        [SerializeField] private float cacheRefreshInterval = 300f; // 5 minutes
        [SerializeField] private float summaryCacheRefreshInterval = 600f; // 10 minutes
        [SerializeField] private int maxCachedMemoriesPerNpc = 100;
        [SerializeField] private bool enableAutoRefresh = true;
        [SerializeField] private bool enableDebugLogging = false;

        [Header("Memory Operations Configuration")]
        [SerializeField] private float memoryDecayInterval = 3600f; // 1 hour
        [SerializeField] private float memoryDecayAmount = 0.1f;
        [SerializeField] private bool enableMemoryDecay = false;

        private MemoryService _memoryService;
        
        // Caching
        private Dictionary<string, List<MemoryDTO>> _npcMemoriesCache = new();
        private Dictionary<string, MemorySummaryDTO> _npcSummariesCache = new();
        private Dictionary<string, DateTime> _lastMemoryRefresh = new();
        private Dictionary<string, DateTime> _lastSummaryRefresh = new();
        
        // Events
        public event Action<MemoryDTO> OnMemoryCreated;
        public event Action<MemoryDTO> OnMemoryRecalled;
        public event Action<MemoryDTO> OnMemoryReinforced;
        public event Action<string> OnMemoryForgotten;
        public event Action<string> OnMemorySummaryUpdated;

        #region SystemManager Implementation

        public override async Task<bool> InitializeAsync()
        {
            try
            {
                LogDebug("Initializing Memory Manager...");

                // Initialize HTTP service
                var httpClient = FindObjectOfType<HttpClient>() ?? GetComponent<HttpClient>();
                if (httpClient == null)
                {
                    LogError("HttpClient not found. Memory Manager requires HttpClient to function.");
                    return false;
                }

                _memoryService = new MemoryService(httpClient);

                // Setup event listeners
                SetupEventListeners();

                // Start auto-refresh if enabled
                if (enableAutoRefresh)
                {
                    StartCoroutine(AutoRefreshCoroutine());
                }

                // Start memory decay if enabled
                if (enableMemoryDecay)
                {
                    StartCoroutine(MemoryDecayCoroutine());
                }

                LogDebug("Memory Manager initialized successfully");
                return true;
            }
            catch (Exception ex)
            {
                LogError($"Failed to initialize Memory Manager: {ex.Message}");
                return false;
            }
        }

        public override async Task ShutdownAsync()
        {
            try
            {
                LogDebug("Shutting down Memory Manager...");

                // Clear caches
                _npcMemoriesCache.Clear();
                _npcSummariesCache.Clear();
                _lastMemoryRefresh.Clear();
                _lastSummaryRefresh.Clear();

                // Unsubscribe from events
                RemoveEventListeners();

                LogDebug("Memory Manager shut down successfully");
            }
            catch (Exception ex)
            {
                LogError($"Error during Memory Manager shutdown: {ex.Message}");
            }
        }

        public override SystemHealthStatus GetHealthStatus()
        {
            return new SystemHealthStatus
            {
                IsHealthy = _memoryService != null && isActiveAndEnabled,
                SystemName = "Memory Manager",
                StatusMessage = _memoryService != null ? "Operational" : "Service not initialized",
                LastUpdated = DateTime.UtcNow
            };
        }

        #endregion

        #region Public API

        /// <summary>
        /// Get memories for a specific NPC
        /// </summary>
        public async Task<List<MemoryDTO>> GetNpcMemoriesAsync(string npcId, bool forceRefresh = false)
        {
            if (string.IsNullOrEmpty(npcId))
            {
                LogError("NPC ID cannot be null or empty");
                return new List<MemoryDTO>();
            }

            try
            {
                // Check cache first
                if (!forceRefresh && _npcMemoriesCache.ContainsKey(npcId) && IsCacheValid(npcId, _lastMemoryRefresh))
                {
                    LogDebug($"Returning cached memories for NPC: {npcId}");
                    return _npcMemoriesCache[npcId];
                }

                // Fetch from API
                var response = await _memoryService.GetNpcMemoriesAsync(npcId, maxCachedMemoriesPerNpc, 0);
                if (response.Success && response.Data?.Memories != null)
                {
                    var memories = response.Data.Memories;
                    
                    // Update cache
                    _npcMemoriesCache[npcId] = memories;
                    _lastMemoryRefresh[npcId] = DateTime.UtcNow;
                    
                    LogDebug($"Loaded {memories.Count} memories for NPC: {npcId}");
                    return memories;
                }
                else
                {
                    LogError($"Failed to load memories for NPC {npcId}: {response.Message}");
                    return new List<MemoryDTO>();
                }
            }
            catch (Exception ex)
            {
                LogError($"Error getting memories for NPC {npcId}: {ex.Message}");
                return new List<MemoryDTO>();
            }
        }

        /// <summary>
        /// Get memory summary for a specific NPC
        /// </summary>
        public async Task<MemorySummaryDTO> GetNpcMemorySummaryAsync(string npcId, bool forceRefresh = false)
        {
            if (string.IsNullOrEmpty(npcId))
            {
                LogError("NPC ID cannot be null or empty");
                return null;
            }

            try
            {
                // Check cache first
                if (!forceRefresh && _npcSummariesCache.ContainsKey(npcId) && IsCacheValid(npcId, _lastSummaryRefresh))
                {
                    LogDebug($"Returning cached summary for NPC: {npcId}");
                    return _npcSummariesCache[npcId];
                }

                // Fetch from API
                var response = await _memoryService.GetMemorySummaryAsync(npcId);
                if (response.Success && response.Data?.Summary != null)
                {
                    var summary = response.Data.Summary;
                    
                    // Update cache
                    _npcSummariesCache[npcId] = summary;
                    _lastSummaryRefresh[npcId] = DateTime.UtcNow;
                    
                    LogDebug($"Loaded memory summary for NPC: {npcId}");
                    OnMemorySummaryUpdated?.Invoke(npcId);
                    return summary;
                }
                else
                {
                    LogError($"Failed to load memory summary for NPC {npcId}: {response.Message}");
                    return null;
                }
            }
            catch (Exception ex)
            {
                LogError($"Error getting memory summary for NPC {npcId}: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Add a new memory for an NPC
        /// </summary>
        public async Task<MemoryDTO> AddMemoryToNpcAsync(string npcId, CreateMemoryRequestDTO request)
        {
            if (string.IsNullOrEmpty(npcId) || request == null)
            {
                LogError("NPC ID and request cannot be null");
                return null;
            }

            try
            {
                var response = await _memoryService.AddMemoryToNpcAsync(npcId, request);
                if (response.Success && response.Data?.Memory != null)
                {
                    var memory = response.Data.Memory;
                    
                    // Update cache
                    InvalidateNpcCaches(npcId);
                    
                    // Fire event
                    OnMemoryCreated?.Invoke(memory);
                    EventBus.Publish(new MemoryCreatedEvent { Memory = memory, NpcId = npcId });
                    
                    LogDebug($"Created memory {memory.MemoryId} for NPC {npcId}");
                    return memory;
                }
                else
                {
                    LogError($"Failed to create memory for NPC {npcId}: {response.Message}");
                    return null;
                }
            }
            catch (Exception ex)
            {
                LogError($"Error creating memory for NPC {npcId}: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Recall a specific memory
        /// </summary>
        public async Task<MemoryDTO> RecallMemoryAsync(string npcId, string memoryId, RecallMemoryRequestDTO request = null)
        {
            if (string.IsNullOrEmpty(npcId) || string.IsNullOrEmpty(memoryId))
            {
                LogError("NPC ID and Memory ID cannot be null or empty");
                return null;
            }

            try
            {
                request ??= new RecallMemoryRequestDTO { Context = "" };
                
                var response = await _memoryService.RecallMemoryAsync(npcId, memoryId, request);
                if (response.Success && response.Data?.Memory != null)
                {
                    var memory = response.Data.Memory;
                    
                    // Update cache
                    UpdateMemoryInCache(npcId, memory);
                    
                    // Fire event
                    OnMemoryRecalled?.Invoke(memory);
                    EventBus.Publish(new MemoryRecalledEvent { Memory = memory, NpcId = npcId, Context = request.Context });
                    
                    LogDebug($"Recalled memory {memoryId} for NPC {npcId}");
                    return memory;
                }
                else
                {
                    LogError($"Failed to recall memory {memoryId} for NPC {npcId}: {response.Message}");
                    return null;
                }
            }
            catch (Exception ex)
            {
                LogError($"Error recalling memory {memoryId} for NPC {npcId}: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Reinforce a specific memory
        /// </summary>
        public async Task<MemoryDTO> ReinforceMemoryAsync(string npcId, string memoryId, ReinforceMemoryRequestDTO request = null)
        {
            if (string.IsNullOrEmpty(npcId) || string.IsNullOrEmpty(memoryId))
            {
                LogError("NPC ID and Memory ID cannot be null or empty");
                return null;
            }

            try
            {
                request ??= new ReinforceMemoryRequestDTO { Reinforcement = 1 };
                
                var response = await _memoryService.ReinforceMemoryAsync(npcId, memoryId, request);
                if (response.Success && response.Data?.Memory != null)
                {
                    var memory = response.Data.Memory;
                    
                    // Update cache
                    UpdateMemoryInCache(npcId, memory);
                    
                    // Fire event
                    OnMemoryReinforced?.Invoke(memory);
                    EventBus.Publish(new MemoryReinforcedEvent { Memory = memory, NpcId = npcId, Reinforcement = request.Reinforcement });
                    
                    LogDebug($"Reinforced memory {memoryId} for NPC {npcId}");
                    return memory;
                }
                else
                {
                    LogError($"Failed to reinforce memory {memoryId} for NPC {npcId}: {response.Message}");
                    return null;
                }
            }
            catch (Exception ex)
            {
                LogError($"Error reinforcing memory {memoryId} for NPC {npcId}: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Forget a specific memory
        /// </summary>
        public async Task<bool> ForgetMemoryAsync(string npcId, string memoryId, ForgetMemoryRequestDTO request = null)
        {
            if (string.IsNullOrEmpty(npcId) || string.IsNullOrEmpty(memoryId))
            {
                LogError("NPC ID and Memory ID cannot be null or empty");
                return false;
            }

            try
            {
                request ??= new ForgetMemoryRequestDTO { Reason = "manual" };
                
                var response = await _memoryService.ForgetMemoryAsync(npcId, memoryId, request);
                if (response.Success)
                {
                    // Update cache
                    RemoveMemoryFromCache(npcId, memoryId);
                    
                    // Fire event
                    OnMemoryForgotten?.Invoke(memoryId);
                    EventBus.Publish(new MemoryForgottenEvent { MemoryId = memoryId, NpcId = npcId, Reason = request.Reason });
                    
                    LogDebug($"Forgot memory {memoryId} for NPC {npcId}");
                    return true;
                }
                else
                {
                    LogError($"Failed to forget memory {memoryId} for NPC {npcId}: {response.Message}");
                    return false;
                }
            }
            catch (Exception ex)
            {
                LogError($"Error forgetting memory {memoryId} for NPC {npcId}: {ex.Message}");
                return false;
            }
        }

        /// <summary>
        /// Get specific memory by ID
        /// </summary>
        public MemoryDTO GetMemoryById(string npcId, string memoryId)
        {
            if (!_npcMemoriesCache.ContainsKey(npcId)) return null;
            
            return _npcMemoriesCache[npcId].FirstOrDefault(m => m.MemoryId == memoryId);
        }

        /// <summary>
        /// Get cached memories for multiple NPCs
        /// </summary>
        public Dictionary<string, List<MemoryDTO>> GetCachedMemories()
        {
            return new Dictionary<string, List<MemoryDTO>>(_npcMemoriesCache);
        }

        /// <summary>
        /// Clear all caches
        /// </summary>
        public void ClearCaches()
        {
            _npcMemoriesCache.Clear();
            _npcSummariesCache.Clear();
            _lastMemoryRefresh.Clear();
            _lastSummaryRefresh.Clear();
            LogDebug("All memory caches cleared");
        }

        /// <summary>
        /// Clear cache for specific NPC
        /// </summary>
        public void ClearNpcCache(string npcId)
        {
            if (string.IsNullOrEmpty(npcId)) return;
            
            _npcMemoriesCache.Remove(npcId);
            _npcSummariesCache.Remove(npcId);
            _lastMemoryRefresh.Remove(npcId);
            _lastSummaryRefresh.Remove(npcId);
            LogDebug($"Cleared cache for NPC: {npcId}");
        }

        #endregion

        #region Cache Management

        private bool IsCacheValid(string npcId, Dictionary<string, DateTime> refreshTimes)
        {
            if (!refreshTimes.ContainsKey(npcId)) return false;
            
            var lastRefresh = refreshTimes[npcId];
            var interval = refreshTimes == _lastSummaryRefresh ? summaryCacheRefreshInterval : cacheRefreshInterval;
            return (DateTime.UtcNow - lastRefresh).TotalSeconds < interval;
        }

        private void InvalidateNpcCaches(string npcId)
        {
            _npcMemoriesCache.Remove(npcId);
            _npcSummariesCache.Remove(npcId);
            _lastMemoryRefresh.Remove(npcId);
            _lastSummaryRefresh.Remove(npcId);
        }

        private void UpdateMemoryInCache(string npcId, MemoryDTO updatedMemory)
        {
            if (!_npcMemoriesCache.ContainsKey(npcId)) return;
            
            var memories = _npcMemoriesCache[npcId];
            var index = memories.FindIndex(m => m.MemoryId == updatedMemory.MemoryId);
            if (index >= 0)
            {
                memories[index] = updatedMemory;
            }
        }

        private void RemoveMemoryFromCache(string npcId, string memoryId)
        {
            if (!_npcMemoriesCache.ContainsKey(npcId)) return;
            
            var memories = _npcMemoriesCache[npcId];
            memories.RemoveAll(m => m.MemoryId == memoryId);
        }

        #endregion

        #region Event System

        private void SetupEventListeners()
        {
            // Listen for character events
            EventBus.Subscribe<CharacterCreatedEvent>(OnCharacterCreated);
            EventBus.Subscribe<CharacterDeletedEvent>(OnCharacterDeleted);
            EventBus.Subscribe<CharacterUpdatedEvent>(OnCharacterUpdated);
            
            // Listen for faction events
            EventBus.Subscribe<FactionCreatedEvent>(OnFactionEvent);
            EventBus.Subscribe<FactionDeletedEvent>(OnFactionEvent);
            EventBus.Subscribe<FactionUpdatedEvent>(OnFactionEvent);
            
            // Listen for region events
            EventBus.Subscribe<RegionCreatedEvent>(OnRegionEvent);
            EventBus.Subscribe<RegionDeletedEvent>(OnRegionEvent);
            EventBus.Subscribe<RegionUpdatedEvent>(OnRegionEvent);
        }

        private void RemoveEventListeners()
        {
            EventBus.Unsubscribe<CharacterCreatedEvent>(OnCharacterCreated);
            EventBus.Unsubscribe<CharacterDeletedEvent>(OnCharacterDeleted);
            EventBus.Unsubscribe<CharacterUpdatedEvent>(OnCharacterUpdated);
            EventBus.Unsubscribe<FactionCreatedEvent>(OnFactionEvent);
            EventBus.Unsubscribe<FactionDeletedEvent>(OnFactionEvent);
            EventBus.Unsubscribe<FactionUpdatedEvent>(OnFactionEvent);
            EventBus.Unsubscribe<RegionCreatedEvent>(OnRegionEvent);
            EventBus.Unsubscribe<RegionDeletedEvent>(OnRegionEvent);
            EventBus.Unsubscribe<RegionUpdatedEvent>(OnRegionEvent);
        }

        private void OnCharacterCreated(CharacterCreatedEvent eventData)
        {
            LogDebug($"Character created: {eventData.CharacterId}. Initializing memory system.");
            // Character memories will be loaded on-demand
        }

        private void OnCharacterDeleted(CharacterDeletedEvent eventData)
        {
            LogDebug($"Character deleted: {eventData.CharacterId}. Clearing memory cache.");
            ClearNpcCache(eventData.CharacterId);
        }

        private void OnCharacterUpdated(CharacterUpdatedEvent eventData)
        {
            // Character update might affect memory context, could invalidate summary cache
            if (_npcSummariesCache.ContainsKey(eventData.CharacterId))
            {
                _npcSummariesCache.Remove(eventData.CharacterId);
                _lastSummaryRefresh.Remove(eventData.CharacterId);
                LogDebug($"Character updated: {eventData.CharacterId}. Invalidated memory summary cache.");
            }
        }

        private void OnFactionEvent(object eventData)
        {
            // Faction changes might affect memories related to that faction
            // For now, we'll just log it - specific handling could be added
            LogDebug("Faction event received. Memory system could be affected.");
        }

        private void OnRegionEvent(object eventData)
        {
            // Region changes might affect memories related to that region
            // For now, we'll just log it - specific handling could be added
            LogDebug("Region event received. Memory system could be affected.");
        }

        #endregion

        #region Coroutines

        private System.Collections.IEnumerator AutoRefreshCoroutine()
        {
            while (enableAutoRefresh && isActiveAndEnabled)
            {
                yield return new WaitForSeconds(cacheRefreshInterval);
                
                try
                {
                    await RefreshExpiredCaches();
                }
                catch (Exception ex)
                {
                    LogError($"Error during auto-refresh: {ex.Message}");
                }
            }
        }

        private System.Collections.IEnumerator MemoryDecayCoroutine()
        {
            while (enableMemoryDecay && isActiveAndEnabled)
            {
                yield return new WaitForSeconds(memoryDecayInterval);
                
                try
                {
                    await ProcessMemoryDecay();
                }
                catch (Exception ex)
                {
                    LogError($"Error during memory decay: {ex.Message}");
                }
            }
        }

        private async Task RefreshExpiredCaches()
        {
            var now = DateTime.UtcNow;
            var expiredNpcs = new List<string>();
            
            // Check for expired memory caches
            foreach (var kvp in _lastMemoryRefresh)
            {
                if ((now - kvp.Value).TotalSeconds > cacheRefreshInterval)
                {
                    expiredNpcs.Add(kvp.Key);
                }
            }
            
            // Refresh expired caches
            foreach (var npcId in expiredNpcs)
            {
                await GetNpcMemoriesAsync(npcId, true);
                await GetNpcMemorySummaryAsync(npcId, true);
            }
            
            if (expiredNpcs.Count > 0)
            {
                LogDebug($"Refreshed {expiredNpcs.Count} expired memory caches");
            }
        }

        private async Task ProcessMemoryDecay()
        {
            // This would implement memory decay logic
            // For now, this is a placeholder - actual implementation would
            // need to call backend APIs for memory decay operations
            LogDebug("Processing memory decay...");
        }

        #endregion

        #region Logging

        private void LogDebug(string message)
        {
            if (enableDebugLogging)
            {
                Debug.Log($"[MemoryManager] {message}");
            }
        }

        private void LogError(string message)
        {
            Debug.LogError($"[MemoryManager] {message}");
        }

        #endregion
    }

    #region Event Classes

    public class MemoryCreatedEvent
    {
        public MemoryDTO Memory { get; set; }
        public string NpcId { get; set; }
    }

    public class MemoryRecalledEvent
    {
        public MemoryDTO Memory { get; set; }
        public string NpcId { get; set; }
        public string Context { get; set; }
    }

    public class MemoryReinforcedEvent
    {
        public MemoryDTO Memory { get; set; }
        public string NpcId { get; set; }
        public int Reinforcement { get; set; }
    }

    public class MemoryForgottenEvent
    {
        public string MemoryId { get; set; }
        public string NpcId { get; set; }
        public string Reason { get; set; }
    }

    #endregion
} 