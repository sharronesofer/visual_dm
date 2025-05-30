using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using System;
using UnityEngine;
using VDM.Runtime.Core;
using VDM.Runtime.Arc.Models;
using VDM.Runtime.Arc.Services;
using VDM.Runtime.Arc.UI;
using VDM.Runtime.Events;


namespace VDM.Runtime.Arc.Integration
{
    /// <summary>
    /// Main controller for the Arc system, coordinating all arc-related functionality
    /// </summary>
    public class ArcSystemController : MonoBehaviour, IGameSystem
    {
        [Header("System References")]
        [SerializeField] private ArcService arcService;
        [SerializeField] private ArcProgressionUI arcProgressionUI;
        [SerializeField] private ArcEventIntegration eventIntegration;
        
        [Header("Settings")]
        [SerializeField] private bool autoStartSystem = true;
        [SerializeField] private float arcSyncInterval = 60f;
        [SerializeField] private int maxCachedArcs = 50;
        [SerializeField] private bool enableDebugLogs = false;
        [SerializeField] private bool enableAutoProgression = true;
        
        // Arc data cache
        private Dictionary<string, ArcDTO> arcCache = new Dictionary<string, ArcDTO>();
        private Dictionary<string, List<ArcDTO>> characterArcs = new Dictionary<string, List<ArcDTO>>();
        private Dictionary<string, List<ArcDTO>> factionArcs = new Dictionary<string, List<ArcDTO>>();
        private Dictionary<string, List<ArcDTO>> regionArcs = new Dictionary<string, List<ArcDTO>>();
        private List<ArcDTO> allArcs = new List<ArcDTO>();
        
        // System state
        private bool isInitialized = false;
        private bool isSystemActive = false;
        private DateTime lastSyncTime = DateTime.MinValue;
        
        // Events
        public event Action<ArcDTO> OnArcAdded;
        public event Action<ArcDTO> OnArcUpdated;
        public event Action<ArcDTO> OnArcCompleted;
        public event Action<ArcDTO> OnArcStalled;
        public event Action<ArcDTO> OnArcStarted;
        public event Action<string> OnArcRemoved;
        
        #region IGameSystem Implementation
        
        public string SystemName => "Arc System";
        public bool IsInitialized => isInitialized;
        public bool IsActive => isSystemActive;
        
        public async Task<bool> InitializeAsync()
        {
            try
            {
                DebugLog("Initializing Arc System...");
                
                // Initialize service if not already set
                if (arcService == null)
                {
                    arcService = FindObjectOfType<ArcService>();
                    if (arcService == null)
                    {
                        GameObject serviceGO = new GameObject("ArcService");
                        serviceGO.transform.SetParent(transform);
                        arcService = serviceGO.AddComponent<ArcService>();
                    }
                }
                
                // Initialize UI if not already set
                if (arcProgressionUI == null)
                {
                    arcProgressionUI = FindObjectOfType<ArcProgressionUI>();
                }
                
                // Initialize event integration if not already set
                if (eventIntegration == null)
                {
                    eventIntegration = FindObjectOfType<ArcEventIntegration>();
                    if (eventIntegration == null)
                    {
                        GameObject integrationGO = new GameObject("ArcEventIntegration");
                        integrationGO.transform.SetParent(transform);
                        eventIntegration = integrationGO.AddComponent<ArcEventIntegration>();
                    }
                }
                
                // Set up event handlers
                SetupEventHandlers();
                
                // Load initial arc data
                await LoadArcData();
                
                isInitialized = true;
                DebugLog("Arc System initialized successfully");
                
                return true;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to initialize Arc System: {ex.Message}");
                return false;
            }
        }
        
        public async Task StartAsync()
        {
            if (!isInitialized)
            {
                await InitializeAsync();
            }
            
            isSystemActive = true;
            DebugLog("Arc System started");
            
            // Start periodic sync
            InvokeRepeating(nameof(PeriodicSync), arcSyncInterval, arcSyncInterval);
            
            // Start stalled arc monitoring
            InvokeRepeating(nameof(MonitorStalledArcs), 300f, 300f); // Every 5 minutes
        }
        
        public async Task StopAsync()
        {
            isSystemActive = false;
            CancelInvoke(nameof(PeriodicSync));
            CancelInvoke(nameof(MonitorStalledArcs));
            DebugLog("Arc System stopped");
        }
        
        public async Task ShutdownAsync()
        {
            await StopAsync();
            CleanupEventHandlers();
            ClearCache();
            isInitialized = false;
            DebugLog("Arc System shutdown");
        }
        
        #endregion
        
        #region Unity Lifecycle
        
        private async void Start()
        {
            if (autoStartSystem)
            {
                await StartAsync();
            }
        }
        
        private async void OnDestroy()
        {
            await ShutdownAsync();
        }
        
        #endregion
        
        #region Arc Management
        
        /// <summary>
        /// Get all arcs for a specific character
        /// </summary>
        /// <param name="characterId">Character ID</param>
        /// <returns>List of character arcs</returns>
        public async Task<List<ArcDTO>> GetCharacterArcsAsync(string characterId)
        {
            try
            {
                // Check cache first
                if (characterArcs.ContainsKey(characterId))
                {
                    return characterArcs[characterId];
                }
                
                // Fetch from service
                var arcs = await arcService.GetActiveArcsForCharacterAsync(characterId);
                
                // Update cache
                characterArcs[characterId] = arcs;
                
                return arcs;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get character arcs: {ex.Message}");
                return new List<ArcDTO>();
            }
        }
        
        /// <summary>
        /// Get all arcs for a specific faction
        /// </summary>
        /// <param name="factionId">Faction ID</param>
        /// <returns>List of faction arcs</returns>
        public async Task<List<ArcDTO>> GetFactionArcsAsync(string factionId)
        {
            try
            {
                // Check cache first
                if (factionArcs.ContainsKey(factionId))
                {
                    return factionArcs[factionId];
                }
                
                // Fetch from service
                var arcs = await arcService.GetActiveArcsForFactionAsync(factionId);
                
                // Update cache
                factionArcs[factionId] = arcs;
                
                return arcs;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get faction arcs: {ex.Message}");
                return new List<ArcDTO>();
            }
        }
        
        /// <summary>
        /// Start an arc
        /// </summary>
        /// <param name="arcId">Arc ID</param>
        /// <param name="initiatorId">ID of the entity starting the arc</param>
        /// <returns>Success status</returns>
        public async Task<bool> StartArcAsync(string arcId, string initiatorId)
        {
            try
            {
                var success = await arcService.StartArcAsync(arcId, initiatorId);
                
                if (success)
                {
                    // Update cache
                    await RefreshArcCache(arcId);
                    
                    // Get updated arc and fire event
                    var arc = await arcService.GetArcAsync(arcId);
                    if (arc != null)
                    {
                        OnArcStarted?.Invoke(arc);
                    }
                }
                
                return success;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to start arc {arcId}: {ex.Message}");
                return false;
            }
        }
        
        /// <summary>
        /// Progress an arc to the next step
        /// </summary>
        /// <param name="arcId">Arc ID</param>
        /// <param name="progressData">Progress data</param>
        /// <returns>Success status</returns>
        public async Task<bool> ProgressArcAsync(string arcId, object progressData)
        {
            try
            {
                var success = await arcService.ProgressArcAsync(arcId, progressData);
                
                if (success)
                {
                    // Update cache
                    await RefreshArcCache(arcId);
                    
                    // Get updated arc and fire event
                    var arc = await arcService.GetArcAsync(arcId);
                    if (arc != null)
                    {
                        OnArcUpdated?.Invoke(arc);
                    }
                }
                
                return success;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to progress arc {arcId}: {ex.Message}");
                return false;
            }
        }
        
        /// <summary>
        /// Complete an arc
        /// </summary>
        /// <param name="arcId">Arc ID</param>
        /// <param name="completionData">Completion data</param>
        /// <returns>Success status</returns>
        public async Task<bool> CompleteArcAsync(string arcId, object completionData)
        {
            try
            {
                var success = await arcService.CompleteArcAsync(arcId, completionData);
                
                if (success)
                {
                    // Update cache
                    await RefreshArcCache(arcId);
                    
                    // Get updated arc and fire event
                    var arc = await arcService.GetArcAsync(arcId);
                    if (arc != null)
                    {
                        OnArcCompleted?.Invoke(arc);
                    }
                }
                
                return success;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to complete arc {arcId}: {ex.Message}");
                return false;
            }
        }
        
        /// <summary>
        /// Update an arc step
        /// </summary>
        /// <param name="arcId">Arc ID</param>
        /// <param name="stepId">Step ID</param>
        /// <param name="updateData">Update data</param>
        /// <returns>Success status</returns>
        public async Task<bool> UpdateArcStepAsync(string arcId, string stepId, ArcStepUpdateDTO updateData)
        {
            try
            {
                var success = await arcService.UpdateArcStepAsync(arcId, stepId, updateData);
                
                if (success)
                {
                    // Update cache
                    await RefreshArcCache(arcId);
                    
                    // Get updated arc and fire event
                    var arc = await arcService.GetArcAsync(arcId);
                    if (arc != null)
                    {
                        OnArcUpdated?.Invoke(arc);
                    }
                }
                
                return success;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to update arc step {stepId}: {ex.Message}");
                return false;
            }
        }
        
        /// <summary>
        /// Generate new arcs based on current game state
        /// </summary>
        /// <param name="context">Generation context</param>
        /// <returns>Generated arcs</returns>
        public async Task<List<ArcDTO>> GenerateArcsAsync(object context)
        {
            try
            {
                var arcs = await arcService.GenerateArcsAsync(context);
                
                // Update cache
                foreach (var arc in arcs)
                {
                    UpdateArcInCache(arc);
                    OnArcAdded?.Invoke(arc);
                }
                
                return arcs;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to generate arcs: {ex.Message}");
                return new List<ArcDTO>();
            }
        }
        
        #endregion
        
        #region Cache Management
        
        /// <summary>
        /// Load initial arc data into cache
        /// </summary>
        private async Task LoadArcData()
        {
            try
            {
                // Load all arcs
                allArcs = await arcService.GetArcsAsync();
                
                // Populate cache
                arcCache.Clear();
                foreach (var arc in allArcs)
                {
                    arcCache[arc.Id] = arc;
                }
                
                lastSyncTime = DateTime.UtcNow;
                DebugLog($"Loaded {allArcs.Count} arcs into cache");
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to load arc data: {ex.Message}");
            }
        }
        
        /// <summary>
        /// Refresh a specific arc in cache
        /// </summary>
        /// <param name="arcId">Arc ID to refresh</param>
        private async Task RefreshArcCache(string arcId)
        {
            try
            {
                var arc = await arcService.GetArcAsync(arcId);
                if (arc != null)
                {
                    UpdateArcInCache(arc);
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to refresh arc cache for {arcId}: {ex.Message}");
            }
        }
        
        /// <summary>
        /// Update an arc in the cache
        /// </summary>
        /// <param name="arc">Arc to update</param>
        private void UpdateArcInCache(ArcDTO arc)
        {
            arcCache[arc.Id] = arc;
            
            // Update in allArcs list
            var existingIndex = allArcs.FindIndex(a => a.Id == arc.Id);
            if (existingIndex >= 0)
            {
                allArcs[existingIndex] = arc;
            }
            else
            {
                allArcs.Add(arc);
            }
            
            // Clear entity-specific caches to force refresh
            characterArcs.Clear();
            factionArcs.Clear();
            regionArcs.Clear();
        }
        
        /// <summary>
        /// Clear all cached data
        /// </summary>
        private void ClearCache()
        {
            arcCache.Clear();
            characterArcs.Clear();
            factionArcs.Clear();
            regionArcs.Clear();
            allArcs.Clear();
        }
        
        #endregion
        
        #region Event Handling
        
        /// <summary>
        /// Set up event handlers
        /// </summary>
        private void SetupEventHandlers()
        {
            if (eventIntegration != null)
            {
                eventIntegration.OnArcGenerated += HandleArcGenerated;
                eventIntegration.OnArcProgression += HandleArcProgression;
                eventIntegration.OnArcStalled += HandleArcStalled;
            }
            
            if (arcProgressionUI != null)
            {
                arcProgressionUI.OnArcStartRequested += StartArcAsync;
                arcProgressionUI.OnArcCompleteRequested += CompleteArcAsync;
                arcProgressionUI.OnArcProgressRequested += ProgressArcAsync;
            }
        }
        
        /// <summary>
        /// Clean up event handlers
        /// </summary>
        private void CleanupEventHandlers()
        {
            if (eventIntegration != null)
            {
                eventIntegration.OnArcGenerated -= HandleArcGenerated;
                eventIntegration.OnArcProgression -= HandleArcProgression;
                eventIntegration.OnArcStalled -= HandleArcStalled;
            }
            
            if (arcProgressionUI != null)
            {
                arcProgressionUI.OnArcStartRequested -= StartArcAsync;
                arcProgressionUI.OnArcCompleteRequested -= CompleteArcAsync;
                arcProgressionUI.OnArcProgressRequested -= ProgressArcAsync;
            }
        }
        
        /// <summary>
        /// Handle arc generation events
        /// </summary>
        /// <param name="arc">Generated arc</param>
        private void HandleArcGenerated(ArcDTO arc)
        {
            UpdateArcInCache(arc);
            OnArcAdded?.Invoke(arc);
        }
        
        /// <summary>
        /// Handle arc progression events
        /// </summary>
        /// <param name="arcId">Arc ID</param>
        /// <param name="progressData">Progress data</param>
        private async void HandleArcProgression(string arcId, object progressData)
        {
            await RefreshArcCache(arcId);
        }
        
        /// <summary>
        /// Handle arc stalled events
        /// </summary>
        /// <param name="arc">Stalled arc</param>
        private void HandleArcStalled(ArcDTO arc)
        {
            UpdateArcInCache(arc);
            OnArcStalled?.Invoke(arc);
        }
        
        #endregion
        
        #region Monitoring & Analytics
        
        /// <summary>
        /// Monitor for stalled arcs and take action
        /// </summary>
        private async void MonitorStalledArcs()
        {
            if (!isSystemActive) return;
            
            try
            {
                var stalledArcs = await arcService.GetStalledArcsAsync();
                
                foreach (var arc in stalledArcs)
                {
                    DebugLog($"Arc {arc.Id} is stalled: {arc.Title}");
                    OnArcStalled?.Invoke(arc);
                    
                    // Optionally trigger automatic resolution attempts
                    if (enableAutoProgression)
                    {
                        await AttemptArcResolution(arc);
                    }
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to monitor stalled arcs: {ex.Message}");
            }
        }
        
        /// <summary>
        /// Attempt to resolve a stalled arc
        /// </summary>
        /// <param name="arc">Stalled arc</param>
        private async Task AttemptArcResolution(ArcDTO arc)
        {
            try
            {
                // Implementation would depend on game logic
                // Could involve generating new events, adjusting requirements, etc.
                DebugLog($"Attempting to resolve stalled arc: {arc.Title}");
                
                // For now, just log the attempt
                // In a full implementation, this would contain logic to:
                // - Generate new story hooks
                // - Adjust arc requirements
                // - Create alternative progression paths
                // - Notify relevant systems
                
                await Task.Delay(100); // Placeholder
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to resolve stalled arc {arc.Id}: {ex.Message}");
            }
        }
        
        #endregion
        
        #region Utility Methods
        
        /// <summary>
        /// Periodic sync with backend
        /// </summary>
        private async void PeriodicSync()
        {
            if (!isSystemActive) return;
            
            try
            {
                await LoadArcData();
            }
            catch (Exception ex)
            {
                Debug.LogError($"Periodic sync failed: {ex.Message}");
            }
        }
        
        /// <summary>
        /// Debug logging with system prefix
        /// </summary>
        /// <param name="message">Message to log</param>
        private void DebugLog(string message)
        {
            if (enableDebugLogs)
            {
                Debug.Log($"[ArcSystem] {message}");
            }
        }
        
        /// <summary>
        /// Get arc from cache
        /// </summary>
        /// <param name="arcId">Arc ID</param>
        /// <returns>Cached arc or null</returns>
        public ArcDTO GetCachedArc(string arcId)
        {
            return arcCache.TryGetValue(arcId, out var arc) ? arc : null;
        }
        
        /// <summary>
        /// Get all cached arcs
        /// </summary>
        /// <returns>List of all cached arcs</returns>
        public List<ArcDTO> GetAllCachedArcs()
        {
            return new List<ArcDTO>(allArcs);
        }
        
        /// <summary>
        /// Get arcs by type
        /// </summary>
        /// <param name="arcType">Arc type</param>
        /// <returns>Arcs of specified type</returns>
        public List<ArcDTO> GetArcsByType(ArcType arcType)
        {
            return allArcs.Where(a => a.Type == arcType).ToList();
        }
        
        /// <summary>
        /// Get arcs by status
        /// </summary>
        /// <param name="status">Arc status</param>
        /// <returns>Arcs with specified status</returns>
        public List<ArcDTO> GetArcsByStatus(ArcStatus status)
        {
            return allArcs.Where(a => a.Status == status).ToList();
        }
        
        /// <summary>
        /// Check if arc can be started
        /// </summary>
        /// <param name="arcId">Arc ID</param>
        /// <param name="initiatorId">Initiator ID</param>
        /// <returns>True if arc can be started</returns>
        public bool CanStartArc(string arcId, string initiatorId)
        {
            var arc = GetCachedArc(arcId);
            if (arc == null) return false;
            
            // Check prerequisites, trigger conditions, etc.
            // Implementation would depend on game logic
            return arc.Status == ArcStatus.Pending;
        }
        
        #endregion
    }
} 