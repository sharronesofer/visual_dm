using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using UnityEngine;
using VDM.Systems.Motifs.Models;

namespace VDM.Systems.Motifs.Services
{
    /// <summary>
    /// Singleton manager for motif operations in Unity.
    /// Handles caching, event dispatching, and coordinates with the backend API.
    /// </summary>
    public class MotifManager : MonoBehaviour
    {
        [Header("Configuration")]
        [SerializeField] private string _backendUrl = "http://localhost:8000/api";
        [SerializeField] private string _apiKey = "";
        [SerializeField] private float _cacheTimeToLive = 60f; // seconds
        [SerializeField] private float _refreshInterval = 30f; // seconds
        [SerializeField] private bool _enableAutoRefresh = true;
        [SerializeField] private bool _enableDebugLogging = false;

        private static MotifManager _instance;
        public static MotifManager Instance
        {
            get
            {
                if (_instance == null)
                {
                    _instance = FindObjectOfType<MotifManager>();
                    if (_instance == null)
                    {
                        GameObject go = new GameObject("MotifManager");
                        _instance = go.AddComponent<MotifManager>();
                        DontDestroyOnLoad(go);
                    }
                }
                return _instance;
            }
        }

        private MotifApiClient _apiClient;
        private Dictionary<string, (Motif motif, DateTime cacheTime)> _motifCache;
        private List<Motif> _allMotifsCache;
        private DateTime _allMotifsCacheTime;
        private bool _isInitialized = false;

        // Events
        public event Action<List<Motif>> OnMotifsUpdated;
        public event Action<Motif> OnMotifCreated;
        public event Action<Motif> OnMotifUpdated;
        public event Action<string> OnMotifDeleted;
        public event Action<string> OnError;

        #region Unity Lifecycle

        private void Awake()
        {
            if (_instance == null)
            {
                _instance = this;
                DontDestroyOnLoad(gameObject);
                Initialize();
            }
            else if (_instance != this)
            {
                Destroy(gameObject);
            }
        }

        private void Start()
        {
            if (_enableAutoRefresh)
            {
                InvokeRepeating(nameof(RefreshMotifs), _refreshInterval, _refreshInterval);
            }
        }

        private void OnDestroy()
        {
            if (_instance == this)
            {
                _instance = null;
            }
        }

        #endregion

        #region Initialization

        private void Initialize()
        {
            if (_isInitialized) return;

            _apiClient = new MotifApiClient(_backendUrl, _apiKey);
            _motifCache = new Dictionary<string, (Motif, DateTime)>();
            _allMotifsCache = new List<Motif>();
            _allMotifsCacheTime = DateTime.MinValue;

            _isInitialized = true;

            if (_enableDebugLogging)
            {
                Debug.Log("MotifManager: Initialized");
            }
        }

        public void Configure(string backendUrl, string apiKey = null)
        {
            _backendUrl = backendUrl;
            _apiKey = apiKey ?? _apiKey;
            
            if (_isInitialized)
            {
                _apiClient = new MotifApiClient(_backendUrl, _apiKey);
                ClearCache();
            }
        }

        #endregion

        #region Cache Management

        private bool IsCacheValid(DateTime cacheTime)
        {
            return (DateTime.Now - cacheTime).TotalSeconds < _cacheTimeToLive;
        }

        private void ClearCache()
        {
            _motifCache.Clear();
            _allMotifsCache.Clear();
            _allMotifsCacheTime = DateTime.MinValue;

            if (_enableDebugLogging)
            {
                Debug.Log("MotifManager: Cache cleared");
            }
        }

        private void CacheMotif(Motif motif)
        {
            if (motif != null && !string.IsNullOrEmpty(motif.id))
            {
                _motifCache[motif.id] = (motif, DateTime.Now);
            }
        }

        private void RemoveFromCache(string motifId)
        {
            _motifCache.Remove(motifId);
            
            // Also remove from all motifs cache
            if (_allMotifsCache != null)
            {
                _allMotifsCache.RemoveAll(m => m.id == motifId);
            }
        }

        #endregion

        #region Public API - Motif Operations

        /// <summary>
        /// Get all motifs with optional filtering
        /// </summary>
        public async Task<List<Motif>> GetMotifsAsync(MotifFilter filter = null, bool forceRefresh = false)
        {
            try
            {
                // Use cache if valid and no filter applied
                if (!forceRefresh && filter == null && IsCacheValid(_allMotifsCacheTime) && _allMotifsCache != null)
                {
                    return new List<Motif>(_allMotifsCache);
                }

                var motifs = await _apiClient.GetMotifsAsync(filter);
                
                // Cache all motifs if no filter was applied
                if (filter == null)
                {
                    _allMotifsCache = motifs;
                    _allMotifsCacheTime = DateTime.Now;
                    
                    // Also cache individual motifs
                    foreach (var motif in motifs)
                    {
                        CacheMotif(motif);
                    }
                }

                OnMotifsUpdated?.Invoke(motifs);
                return motifs;
            }
            catch (Exception ex)
            {
                LogError($"Failed to get motifs: {ex.Message}");
                OnError?.Invoke($"Failed to get motifs: {ex.Message}");
                return new List<Motif>();
            }
        }

        /// <summary>
        /// Get a specific motif by ID
        /// </summary>
        public async Task<Motif> GetMotifAsync(string motifId, bool forceRefresh = false)
        {
            try
            {
                // Check cache first
                if (!forceRefresh && _motifCache.TryGetValue(motifId, out var cached) && IsCacheValid(cached.cacheTime))
                {
                    return cached.motif;
                }

                var motif = await _apiClient.GetMotifAsync(motifId);
                if (motif != null)
                {
                    CacheMotif(motif);
                }

                return motif;
            }
            catch (Exception ex)
            {
                LogError($"Failed to get motif {motifId}: {ex.Message}");
                OnError?.Invoke($"Failed to get motif: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Create a new motif
        /// </summary>
        public async Task<Motif> CreateMotifAsync(MotifCreateData motifData)
        {
            try
            {
                var motif = await _apiClient.CreateMotifAsync(motifData);
                if (motif != null)
                {
                    CacheMotif(motif);
                    
                    // Add to all motifs cache if it exists
                    if (_allMotifsCache != null)
                    {
                        _allMotifsCache.Add(motif);
                    }

                    OnMotifCreated?.Invoke(motif);
                }

                return motif;
            }
            catch (Exception ex)
            {
                LogError($"Failed to create motif: {ex.Message}");
                OnError?.Invoke($"Failed to create motif: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Update an existing motif
        /// </summary>
        public async Task<Motif> UpdateMotifAsync(string motifId, MotifUpdateData updateData)
        {
            try
            {
                var motif = await _apiClient.UpdateMotifAsync(motifId, updateData);
                if (motif != null)
                {
                    CacheMotif(motif);
                    
                    // Update in all motifs cache if it exists
                    if (_allMotifsCache != null)
                    {
                        var index = _allMotifsCache.FindIndex(m => m.id == motifId);
                        if (index >= 0)
                        {
                            _allMotifsCache[index] = motif;
                        }
                    }

                    OnMotifUpdated?.Invoke(motif);
                }

                return motif;
            }
            catch (Exception ex)
            {
                LogError($"Failed to update motif {motifId}: {ex.Message}");
                OnError?.Invoke($"Failed to update motif: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Delete a motif
        /// </summary>
        public async Task<bool> DeleteMotifAsync(string motifId)
        {
            try
            {
                bool success = await _apiClient.DeleteMotifAsync(motifId);
                if (success)
                {
                    RemoveFromCache(motifId);
                    OnMotifDeleted?.Invoke(motifId);
                }

                return success;
            }
            catch (Exception ex)
            {
                LogError($"Failed to delete motif {motifId}: {ex.Message}");
                OnError?.Invoke($"Failed to delete motif: {ex.Message}");
                return false;
            }
        }

        #endregion

        #region Specialized Queries

        /// <summary>
        /// Get motifs affecting a specific position
        /// </summary>
        public async Task<List<Motif>> GetMotifsAtPositionAsync(Vector2 position, float radius = 0)
        {
            try
            {
                return await _apiClient.GetMotifsAtPositionAsync(position, radius);
            }
            catch (Exception ex)
            {
                LogError($"Failed to get motifs at position: {ex.Message}");
                OnError?.Invoke($"Failed to get motifs at position: {ex.Message}");
                return new List<Motif>();
            }
        }

        /// <summary>
        /// Get global motifs
        /// </summary>
        public async Task<List<Motif>> GetGlobalMotifsAsync()
        {
            try
            {
                return await _apiClient.GetGlobalMotifsAsync();
            }
            catch (Exception ex)
            {
                LogError($"Failed to get global motifs: {ex.Message}");
                OnError?.Invoke($"Failed to get global motifs: {ex.Message}");
                return new List<Motif>();
            }
        }

        /// <summary>
        /// Get regional motifs for a specific region
        /// </summary>
        public async Task<List<Motif>> GetRegionalMotifsAsync(string regionId)
        {
            try
            {
                return await _apiClient.GetRegionalMotifsAsync(regionId);
            }
            catch (Exception ex)
            {
                LogError($"Failed to get regional motifs: {ex.Message}");
                OnError?.Invoke($"Failed to get regional motifs: {ex.Message}");
                return new List<Motif>();
            }
        }

        /// <summary>
        /// Get narrative context for motifs at a location
        /// </summary>
        public async Task<MotifNarrativeContext> GetNarrativeContextAsync(Vector2? position = null, string regionId = null)
        {
            try
            {
                return await _apiClient.GetNarrativeContextAsync(position, regionId);
            }
            catch (Exception ex)
            {
                LogError($"Failed to get narrative context: {ex.Message}");
                OnError?.Invoke($"Failed to get narrative context: {ex.Message}");
                return new MotifNarrativeContext();
            }
        }

        #endregion

        #region Utility Methods

        /// <summary>
        /// Get active motifs (filtered by lifecycle)
        /// </summary>
        public async Task<List<Motif>> GetActiveMotifsAsync()
        {
            var filter = new MotifFilter
            {
                lifecycles = new List<MotifLifecycle> 
                { 
                    MotifLifecycle.Emerging, 
                    MotifLifecycle.Stable, 
                    MotifLifecycle.Waning 
                },
                activeOnly = true
            };
            return await GetMotifsAsync(filter);
        }

        /// <summary>
        /// Get motifs by category
        /// </summary>
        public async Task<List<Motif>> GetMotifsByCategoryAsync(MotifCategory category)
        {
            var filter = new MotifFilter
            {
                categories = new List<MotifCategory> { category },
                activeOnly = true
            };
            return await GetMotifsAsync(filter);
        }

        /// <summary>
        /// Refresh all motifs cache
        /// </summary>
        public async void RefreshMotifs()
        {
            await GetMotifsAsync(forceRefresh: true);
        }

        /// <summary>
        /// Get cached motifs count
        /// </summary>
        public int GetCachedMotifsCount()
        {
            return _motifCache.Count;
        }

        /// <summary>
        /// Check if manager is connected to backend
        /// </summary>
        public async Task<bool> TestConnectionAsync()
        {
            try
            {
                await _apiClient.GetMotifsAsync();
                return true;
            }
            catch
            {
                return false;
            }
        }

        #endregion

        #region Logging

        private void LogError(string message)
        {
            Debug.LogError($"MotifManager: {message}");
        }

        private void LogDebug(string message)
        {
            if (_enableDebugLogging)
            {
                Debug.Log($"MotifManager: {message}");
            }
        }

        #endregion

        #region Editor Support

#if UNITY_EDITOR
        [ContextMenu("Test Connection")]
        public async void TestConnectionFromEditor()
        {
            bool connected = await TestConnectionAsync();
            Debug.Log($"MotifManager: Connection test result: {connected}");
        }

        [ContextMenu("Refresh Motifs")]
        public void RefreshMotifsFromEditor()
        {
            RefreshMotifs();
        }

        [ContextMenu("Clear Cache")]
        public void ClearCacheFromEditor()
        {
            ClearCache();
        }

        [ContextMenu("Show Cache Stats")]
        public void ShowCacheStats()
        {
            Debug.Log($"MotifManager Cache Stats:\n" +
                     $"Individual motifs cached: {_motifCache.Count}\n" +
                     $"All motifs cache valid: {IsCacheValid(_allMotifsCacheTime)}\n" +
                     $"All motifs count: {_allMotifsCache?.Count ?? 0}");
        }
#endif

        #endregion
    }
} 