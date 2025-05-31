using NativeWebSocket;
using Newtonsoft.Json;
using System.Collections.Generic;
using System.Collections;
using System;
using UnityEngine;
using VDM.DTOs.Core;
using VDM.Systems.Character;
using VDM.Infrastructure.Services;
using VDM.DTOs.Character;
using VDM.Infrastructure.Services.Services.Websocket;
using VDM.Infrastructure.Services.Services.Http;


namespace VDM.Infrastructure.Services
{
    /// <summary>
    /// Enhanced Character Service that uses OptimizedHTTPClient for better network performance
    /// Demonstrates how to integrate network optimizations with existing services
    /// </summary>
    public class EnhancedCharacterService : MonoBehaviour
    {
        [Header("Character Service Configuration")]
        [SerializeField] private bool autoSyncCharacters = true;
        [SerializeField] private float syncInterval = 30f;
        [SerializeField] private bool useNetworkOptimizations = true;
        [SerializeField] private bool enableDeltaUpdates = true;

        [Header("Performance Settings")]
        [SerializeField] private int maxCacheSize = 100;
        [SerializeField] private float cacheTimeout = 300f; // 5 minutes
        [SerializeField] private bool enableCompression = true;

        // Network clients
        private OptimizedHttpClient optimizedHttpClient;
        private OptimizedWebSocketClient optimizedWebSocketClient;
        
        // Character events
        public event Action<CharacterResponseDTO> OnCharacterCreated;
        public event Action<CharacterResponseDTO> OnCharacterUpdated;
        public event Action<string> OnCharacterDeleted;
        public event Action<List<CharacterResponseDTO>> OnCharactersLoaded;
        public event Action<CharacterResponseDTO> OnCharacterLevelUp;
        public event Action<CharacterResponseDTO, string> OnCharacterSkillIncreased;
        public event Action<CharacterResponseDTO, string> OnCharacterAbilityGained;

        // Performance monitoring
        public event Action<NetworkPerformanceStats> OnPerformanceStatsUpdated;

        // Local character cache with metadata
        private Dictionary<string, CachedCharacterData> characterCache = new Dictionary<string, CachedCharacterData>();
        private Dictionary<string, CharacterModel> characterModels = new Dictionary<string, CharacterModel>();
        
        // Delta tracking for optimization
        private Dictionary<string, CharacterResponseDTO> lastKnownStates = new Dictionary<string, CharacterResponseDTO>();

        // Coroutines
        private Coroutine autoSyncCoroutine;
        private Coroutine performanceMonitoringCoroutine;

        private bool isInitialized = false;

        private void Awake()
        {
            InitializeService();
        }

        private void Start()
        {
            if (useNetworkOptimizations)
            {
                StartPerformanceMonitoring();
            }

            if (autoSyncCharacters)
            {
                StartAutoSync();
            }
        }

        #region Initialization

        private void InitializeService()
        {
            // Get or create OptimizedHTTPClient
            optimizedHttpClient = FindObjectOfType<OptimizedHttpClient>();
            if (optimizedHttpClient == null)
            {
                var httpClientGO = new GameObject("OptimizedHTTPClient");
                optimizedHttpClient = httpClientGO.AddComponent<OptimizedHttpClient>();
            }

            // Get OptimizedWebSocketClient instance
            optimizedWebSocketClient = OptimizedWebSocketClient.Instance;
            if (optimizedWebSocketClient != null)
            {
                // Subscribe to WebSocket events
                optimizedWebSocketClient.OnMessageReceived += HandleWebSocketMessage;
                optimizedWebSocketClient.OnConnected += OnWebSocketConnected;
                optimizedWebSocketClient.OnDisconnected += OnWebSocketDisconnected;
            }

            isInitialized = true;
            Debug.Log("[EnhancedCharacterService] Service initialized with network optimizations");
        }

        #endregion

        #region Optimized Character Operations

        /// <summary>
        /// Create a new character using optimized HTTP client
        /// </summary>
        public void CreateCharacter(CharacterCreateDTO characterData, Action<bool, CharacterResponseDTO> callback = null)
        {
            if (!isInitialized) InitializeService();

            StartCoroutine(CreateCharacterOptimized(characterData, callback));
        }

        private IEnumerator CreateCharacterOptimized(CharacterCreateDTO characterData, Action<bool, CharacterResponseDTO> callback)
        {
            bool success = false;
            CharacterResponseDTO character = null;

            // Use optimized POST request with compression and delta updates disabled for creation
            optimizedHttpClient.PostOptimized("/characters", characterData, (requestSuccess, response) =>
            {
                success = requestSuccess;
                if (success && !string.IsNullOrEmpty(response))
                {
                    try
                    {
                        character = JsonConvert.DeserializeObject<CharacterResponseDTO>(response);
                        if (character != null)
                        {
                            // Cache the new character
                            CacheCharacter(character);
                            
                            // Store initial state for delta tracking
                            if (enableDeltaUpdates)
                            {
                                lastKnownStates[character.Id] = character;
                            }

                            OnCharacterCreated?.Invoke(character);
                            Debug.Log($"[EnhancedCharacterService] Created character: {character.CharacterName} (ID: {character.Id})");
                        }
                    }
                    catch (Exception ex)
                    {
                        Debug.LogError($"[EnhancedCharacterService] Failed to deserialize character: {ex.Message}");
                        success = false;
                    }
                }
            }, false); // Don't use delta for creation

            // Wait for completion
            yield return new WaitUntil(() => success || !string.IsNullOrEmpty(character?.Id));

            callback?.Invoke(success, character);
        }

        /// <summary>
        /// Get a character with caching and optimization
        /// </summary>
        public void GetCharacter(string characterId, Action<bool, CharacterResponseDTO> callback = null, bool useCache = true)
        {
            if (!isInitialized) InitializeService();

            // Check cache first if enabled
            if (useCache && IsCharacterCached(characterId, out CharacterResponseDTO cachedCharacter))
            {
                callback?.Invoke(true, cachedCharacter);
                return;
            }

            StartCoroutine(GetCharacterOptimized(characterId, callback, useCache));
        }

        private IEnumerator GetCharacterOptimized(string characterId, Action<bool, CharacterResponseDTO> callback, bool useCache)
        {
            bool success = false;
            CharacterResponseDTO character = null;

            // Use optimized GET request with caching
            optimizedHttpClient.GetOptimized($"/characters/{characterId}", (requestSuccess, response) =>
            {
                success = requestSuccess;
                if (success && !string.IsNullOrEmpty(response))
                {
                    try
                    {
                        character = JsonConvert.DeserializeObject<CharacterResponseDTO>(response);
                        if (character != null && useCache)
                        {
                            CacheCharacter(character);
                        }
                    }
                    catch (Exception ex)
                    {
                        Debug.LogError($"[EnhancedCharacterService] Failed to deserialize character: {ex.Message}");
                        success = false;
                    }
                }
            }, useCache);

            // Wait for completion
            yield return new WaitUntil(() => success || character != null);

            callback?.Invoke(success, character);
        }

        /// <summary>
        /// Update character with delta optimization
        /// </summary>
        public void UpdateCharacter(string characterId, CharacterUpdateDTO updates, Action<bool, CharacterResponseDTO> callback = null)
        {
            if (!isInitialized) InitializeService();

            StartCoroutine(UpdateCharacterOptimized(characterId, updates, callback));
        }

        private IEnumerator UpdateCharacterOptimized(string characterId, CharacterUpdateDTO updates, Action<bool, CharacterResponseDTO> callback)
        {
            bool success = false;
            CharacterResponseDTO character = null;

            // Create delta update if we have previous state
            object dataToSend = updates;
            if (enableDeltaUpdates && lastKnownStates.TryGetValue(characterId, out CharacterResponseDTO lastState))
            {
                dataToSend = CreateCharacterDelta(lastState, updates);
            }

            // Use optimized POST request with delta updates
            optimizedHttpClient.PostOptimized($"/characters/{characterId}", dataToSend, (requestSuccess, response) =>
            {
                success = requestSuccess;
                if (success && !string.IsNullOrEmpty(response))
                {
                    try
                    {
                        character = JsonConvert.DeserializeObject<CharacterResponseDTO>(response);
                        if (character != null)
                        {
                            // Update cache and delta state
                            CacheCharacter(character);
                            if (enableDeltaUpdates)
                            {
                                lastKnownStates[character.Id] = character;
                            }

                            OnCharacterUpdated?.Invoke(character);
                        }
                    }
                    catch (Exception ex)
                    {
                        Debug.LogError($"[EnhancedCharacterService] Failed to deserialize updated character: {ex.Message}");
                        success = false;
                    }
                }
            }, enableDeltaUpdates);

            yield return new WaitUntil(() => success || character != null);

            callback?.Invoke(success, character);
        }

        /// <summary>
        /// Grant experience with optimized request
        /// </summary>
        public void GrantExperience(string characterId, ExperienceGrantDTO xpGrant, Action<bool, CharacterResponseDTO> callback = null)
        {
            if (!isInitialized) InitializeService();

            StartCoroutine(GrantExperienceOptimized(characterId, xpGrant, callback));
        }

        private IEnumerator GrantExperienceOptimized(string characterId, ExperienceGrantDTO xpGrant, Action<bool, CharacterResponseDTO> callback)
        {
            bool success = false;
            CharacterResponseDTO character = null;

            optimizedHttpClient.PostOptimized($"/characters/{characterId}/experience", xpGrant, (requestSuccess, response) =>
            {
                success = requestSuccess;
                if (success && !string.IsNullOrEmpty(response))
                {
                    try
                    {
                        character = JsonConvert.DeserializeObject<CharacterResponseDTO>(response);
                        if (character != null)
                        {
                            CacheCharacter(character);
                            
                            // Check if character leveled up
                            if (lastKnownStates.TryGetValue(characterId, out CharacterResponseDTO lastState) &&
                                character.Level > lastState.Level)
                            {
                                OnCharacterLevelUp?.Invoke(character);
                            }

                            lastKnownStates[character.Id] = character;
                        }
                    }
                    catch (Exception ex)
                    {
                        Debug.LogError($"[EnhancedCharacterService] Failed to process experience grant: {ex.Message}");
                        success = false;
                    }
                }
            });

            yield return new WaitUntil(() => success || character != null);

            callback?.Invoke(success, character);
        }

        #endregion

        #region WebSocket Integration

        private void OnWebSocketConnected()
        {
            Debug.Log("[EnhancedCharacterService] WebSocket connected for real-time character updates");

            // Subscribe to character-specific events
            if (optimizedWebSocketClient != null)
            {
                var subscriptionMessage = new OptimizedWebSocketClient.WebSocketMessage
                {
                    type = "subscribe",
                    data = new { topic = "characters", events = new[] { "update", "level_up", "skill_increase", "ability_gained" } }
                };

                optimizedWebSocketClient.SendMessage(subscriptionMessage);
            }
        }

        private void OnWebSocketDisconnected()
        {
            Debug.Log("[EnhancedCharacterService] WebSocket disconnected");
        }

        private void HandleWebSocketMessage(WebSocketMessage message)
        {
            switch (message.Type)
            {
                case "character_update":
                    HandleCharacterUpdate(message);
                    break;
                case "character_level_up":
                    HandleCharacterLevelUp(message);
                    break;
                case "character_skill_increase":
                    HandleCharacterSkillIncrease(message);
                    break;
                case "character_ability_gained":
                    HandleCharacterAbilityGained(message);
                    break;
            }
        }

        private void HandleCharacterUpdate(WebSocketMessage message)
        {
            try
            {
                var character = JsonConvert.DeserializeObject<CharacterResponseDTO>(message.Data.ToString());
                if (character != null)
                {
                    CacheCharacter(character);
                    OnCharacterUpdated?.Invoke(character);
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"[EnhancedCharacterService] Failed to handle character update: {ex.Message}");
            }
        }

        private void HandleCharacterLevelUp(WebSocketMessage message)
        {
            try
            {
                var character = JsonConvert.DeserializeObject<CharacterResponseDTO>(message.Data.ToString());
                if (character != null)
                {
                    CacheCharacter(character);
                    OnCharacterLevelUp?.Invoke(character);
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"[EnhancedCharacterService] Failed to handle character level up: {ex.Message}");
            }
        }

        private void HandleCharacterSkillIncrease(WebSocketMessage message)
        {
            try
            {
                var data = JsonConvert.DeserializeObject<dynamic>(message.Data.ToString());
                var character = JsonConvert.DeserializeObject<CharacterResponseDTO>(data.character.ToString());
                var skillName = data.skillName.ToString();
                
                if (character != null)
                {
                    CacheCharacter(character);
                    OnCharacterSkillIncreased?.Invoke(character, skillName);
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"[EnhancedCharacterService] Failed to handle character skill increase: {ex.Message}");
            }
        }

        private void HandleCharacterAbilityGained(WebSocketMessage message)
        {
            try
            {
                var data = JsonConvert.DeserializeObject<dynamic>(message.Data.ToString());
                var character = JsonConvert.DeserializeObject<CharacterResponseDTO>(data.character.ToString());
                var abilityName = data.abilityName.ToString();
                
                if (character != null)
                {
                    CacheCharacter(character);
                    OnCharacterAbilityGained?.Invoke(character, abilityName);
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"[EnhancedCharacterService] Failed to handle character ability gained: {ex.Message}");
            }
        }

        #endregion

        #region Delta Updates and Optimization

        private object CreateCharacterDelta(CharacterResponseDTO lastState, CharacterUpdateDTO newData)
        {
            // Create a delta object containing only changed fields
            var delta = new Dictionary<string, object>();

            // Compare key fields and only include changes
            var newDataDict = JsonConvert.DeserializeObject<Dictionary<string, object>>(JsonConvert.SerializeObject(newData));
            
            foreach (var kvp in newDataDict)
            {
                // In a real implementation, you would compare with lastState properties
                // For now, we'll include all non-null values
                if (kvp.Value != null)
                {
                    delta[kvp.Key] = kvp.Value;
                }
            }

            return new { delta = true, changes = delta, characterId = lastState.Id };
        }

        #endregion

        #region Caching

        private void CacheCharacter(CharacterResponseDTO character)
        {
            if (character?.Id == null) return;

            var cachedData = new CachedCharacterData
            {
                character = character,
                cacheTime = DateTime.UtcNow,
                accessCount = characterCache.ContainsKey(character.Id) ? characterCache[character.Id].accessCount + 1 : 1
            };

            characterCache[character.Id] = cachedData;

            // Limit cache size
            if (characterCache.Count > maxCacheSize)
            {
                CleanupCache();
            }
        }

        private bool IsCharacterCached(string characterId, out CharacterResponseDTO character)
        {
            character = null;

            if (characterCache.TryGetValue(characterId, out CachedCharacterData cachedData))
            {
                // Check if cache entry is still valid
                if (DateTime.UtcNow.Subtract(cachedData.cacheTime).TotalSeconds < cacheTimeout)
                {
                    cachedData.accessCount++;
                    character = cachedData.character;
                    return true;
                }

                // Cache expired, remove it
                characterCache.Remove(characterId);
            }

            return false;
        }

        private void CleanupCache()
        {
            // Remove oldest entries when cache is full
            var sortedEntries = new List<KeyValuePair<string, CachedCharacterData>>(characterCache);
            sortedEntries.Sort((x, y) => DateTime.Compare(x.Value.cacheTime, y.Value.cacheTime));

            // Remove oldest 25% of entries
            int entriesToRemove = maxCacheSize / 4;
            for (int i = 0; i < entriesToRemove && i < sortedEntries.Count; i++)
            {
                characterCache.Remove(sortedEntries[i].Key);
                lastKnownStates.Remove(sortedEntries[i].Key);
            }

            Debug.Log($"[EnhancedCharacterService] Cache cleanup: removed {entriesToRemove} entries");
        }

        public void ClearCache()
        {
            characterCache.Clear();
            lastKnownStates.Clear();
            Debug.Log("[EnhancedCharacterService] Cache cleared");
        }

        #endregion

        #region Performance Monitoring

        private void StartPerformanceMonitoring()
        {
            performanceMonitoringCoroutine = StartCoroutine(PerformanceMonitoringRoutine());
        }

        private IEnumerator PerformanceMonitoringRoutine()
        {
            while (enabled)
            {
                yield return new WaitForSeconds(10f);

                // Collect performance stats
                var httpStats = optimizedHttpClient?.GetPerformanceStats();
                var wsStats = optimizedWebSocketClient?.GetPerformanceStats();

                if (httpStats != null && wsStats != null)
                {
                    var combinedStats = new NetworkPerformanceStats
                    {
                        httpCacheHitRatio = httpStats.cacheHitRatio,
                        httpActiveConnections = httpStats.activeConnections,
                        httpQueuedRequests = httpStats.queuedRequests,
                        wsBatchesSent = wsStats.batchesSent,
                        wsAverageLatency = wsStats.averageLatency,
                        charactersCached = characterCache.Count,
                        deltaUpdatesEnabled = enableDeltaUpdates
                    };

                    OnPerformanceStatsUpdated?.Invoke(combinedStats);
                }
            }
        }

        #endregion

        #region Auto Sync

        private void StartAutoSync()
        {
            autoSyncCoroutine = StartCoroutine(AutoSyncRoutine());
        }

        private IEnumerator AutoSyncRoutine()
        {
            while (enabled)
            {
                yield return new WaitForSeconds(syncInterval);

                // Sync cached characters with server
                var characterIds = new List<string>(characterCache.Keys);
                foreach (string characterId in characterIds)
                {
                    GetCharacter(characterId, null, false); // Force refresh from server
                    yield return new WaitForSeconds(0.1f); // Small delay between requests
                }

                Debug.Log($"[EnhancedCharacterService] Auto-sync completed for {characterIds.Count} characters");
            }
        }

        #endregion

        #region Public API

        public List<CharacterResponseDTO> GetCachedCharacters()
        {
            var characters = new List<CharacterResponseDTO>();
            foreach (var cachedData in characterCache.Values)
            {
                characters.Add(cachedData.character);
            }
            return characters;
        }

        public NetworkPerformanceStats GetCurrentPerformanceStats()
        {
            var httpStats = optimizedHttpClient?.GetPerformanceStats();
            var wsStats = optimizedWebSocketClient?.GetPerformanceStats();

            return new NetworkPerformanceStats
            {
                httpCacheHitRatio = httpStats?.cacheHitRatio ?? 0f,
                httpActiveConnections = httpStats?.activeConnections ?? 0,
                httpQueuedRequests = httpStats?.queuedRequests ?? 0,
                wsBatchesSent = wsStats?.batchesSent ?? 0,
                wsAverageLatency = wsStats?.averageLatency ?? 0f,
                charactersCached = characterCache.Count,
                deltaUpdatesEnabled = enableDeltaUpdates
            };
        }

        public void EnableOptimizations(bool enable)
        {
            useNetworkOptimizations = enable;
            enableDeltaUpdates = enable;
            
            if (enable && performanceMonitoringCoroutine == null)
            {
                StartPerformanceMonitoring();
            }
            else if (!enable && performanceMonitoringCoroutine != null)
            {
                StopCoroutine(performanceMonitoringCoroutine);
                performanceMonitoringCoroutine = null;
            }
        }

        #endregion

        #region Data Classes

        [System.Serializable]
        public class CachedCharacterData
        {
            public CharacterResponseDTO character;
            public DateTime cacheTime;
            public int accessCount;
        }

        [System.Serializable]
        public class NetworkPerformanceStats
        {
            public float httpCacheHitRatio;
            public int httpActiveConnections;
            public int httpQueuedRequests;
            public int wsBatchesSent;
            public float wsAverageLatency;
            public int charactersCached;
            public bool deltaUpdatesEnabled;
        }

        #endregion

        private void OnDestroy()
        {
            // Clean up WebSocket subscriptions
            if (optimizedWebSocketClient != null)
            {
                optimizedWebSocketClient.OnMessageReceived -= HandleWebSocketMessage;
                optimizedWebSocketClient.OnConnected -= OnWebSocketConnected;
                optimizedWebSocketClient.OnDisconnected -= OnWebSocketDisconnected;
            }

            // Stop coroutines
            if (autoSyncCoroutine != null)
            {
                StopCoroutine(autoSyncCoroutine);
            }

            if (performanceMonitoringCoroutine != null)
            {
                StopCoroutine(performanceMonitoringCoroutine);
            }
        }
    }
} 