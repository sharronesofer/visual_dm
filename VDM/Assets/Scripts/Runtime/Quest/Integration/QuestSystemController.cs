using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using System;
using UnityEngine;
using VDM.Runtime.Core;
using VDM.Runtime.Events;
using VDM.Runtime.Quest.Models;
using VDM.Runtime.Quest.Services;
using VDM.Runtime.Quest.UI;


namespace VDM.Runtime.Quest.Integration
{
    /// <summary>
    /// Main controller for the Quest system, coordinating all quest-related functionality
    /// </summary>
    public class QuestSystemController : MonoBehaviour, IGameSystem
    {
        [Header("System References")]
        [SerializeField] private QuestService questService;
        [SerializeField] private QuestLogUI questLogUI;
        [SerializeField] private QuestEventIntegration eventIntegration;
        
        [Header("Settings")]
        [SerializeField] private bool autoStartSystem = true;
        [SerializeField] private float questSyncInterval = 30f;
        [SerializeField] private int maxCachedQuests = 100;
        [SerializeField] private bool enableDebugLogs = false;
        
        // Quest data cache
        private Dictionary<string, QuestDTO> questCache = new Dictionary<string, QuestDTO>();
        private Dictionary<string, List<QuestDTO>> characterQuests = new Dictionary<string, List<QuestDTO>>();
        private List<QuestDTO> allQuests = new List<QuestDTO>();
        
        // System state
        private bool isInitialized = false;
        private bool isSystemActive = false;
        private DateTime lastSyncTime = DateTime.MinValue;
        
        // Events
        public event Action<QuestDTO> OnQuestAdded;
        public event Action<QuestDTO> OnQuestUpdated;
        public event Action<QuestDTO> OnQuestCompleted;
        public event Action<QuestDTO> OnQuestFailed;
        public event Action<QuestDTO> OnQuestStarted;
        public event Action<string> OnQuestRemoved;
        
        #region IGameSystem Implementation
        
        public string SystemName => "Quest System";
        public bool IsInitialized => isInitialized;
        public bool IsActive => isSystemActive;
        
        public async Task<bool> InitializeAsync()
        {
            try
            {
                DebugLog("Initializing Quest System...");
                
                // Initialize service if not already set
                if (questService == null)
                {
                    questService = FindObjectOfType<QuestService>();
                    if (questService == null)
                    {
                        GameObject serviceGO = new GameObject("QuestService");
                        serviceGO.transform.SetParent(transform);
                        questService = serviceGO.AddComponent<QuestService>();
                    }
                }
                
                // Initialize UI if not already set
                if (questLogUI == null)
                {
                    questLogUI = FindObjectOfType<QuestLogUI>();
                }
                
                // Initialize event integration if not already set
                if (eventIntegration == null)
                {
                    eventIntegration = FindObjectOfType<QuestEventIntegration>();
                    if (eventIntegration == null)
                    {
                        GameObject integrationGO = new GameObject("QuestEventIntegration");
                        integrationGO.transform.SetParent(transform);
                        eventIntegration = integrationGO.AddComponent<QuestEventIntegration>();
                    }
                }
                
                // Set up event handlers
                SetupEventHandlers();
                
                // Load initial quest data
                await LoadQuestData();
                
                isInitialized = true;
                DebugLog("Quest System initialized successfully");
                
                return true;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to initialize Quest System: {ex.Message}");
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
            DebugLog("Quest System started");
            
            // Start periodic sync
            InvokeRepeating(nameof(PeriodicSync), questSyncInterval, questSyncInterval);
        }
        
        public async Task StopAsync()
        {
            isSystemActive = false;
            CancelInvoke(nameof(PeriodicSync));
            DebugLog("Quest System stopped");
        }
        
        public async Task ShutdownAsync()
        {
            await StopAsync();
            CleanupEventHandlers();
            ClearCache();
            isInitialized = false;
            DebugLog("Quest System shutdown");
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
        
        #region Quest Management
        
        /// <summary>
        /// Get all quests for a specific character
        /// </summary>
        /// <param name="characterId">Character ID</param>
        /// <returns>List of character quests</returns>
        public async Task<List<QuestDTO>> GetCharacterQuestsAsync(string characterId)
        {
            try
            {
                // Check cache first
                if (characterQuests.ContainsKey(characterId))
                {
                    return characterQuests[characterId];
                }
                
                // Fetch from service
                var quests = await questService.GetActiveQuestsAsync(characterId);
                
                // Update cache
                characterQuests[characterId] = quests;
                
                return quests;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get character quests: {ex.Message}");
                return new List<QuestDTO>();
            }
        }
        
        /// <summary>
        /// Start a quest for a character
        /// </summary>
        /// <param name="questId">Quest ID</param>
        /// <param name="characterId">Character ID</param>
        /// <returns>Success status</returns>
        public async Task<bool> StartQuestAsync(string questId, string characterId)
        {
            try
            {
                var success = await questService.StartQuestAsync(questId, characterId);
                
                if (success)
                {
                    // Update cache
                    await RefreshQuestCache(questId);
                    
                    // Get updated quest and fire event
                    var quest = await questService.GetQuestAsync(questId);
                    if (quest != null)
                    {
                        OnQuestStarted?.Invoke(quest);
                    }
                }
                
                return success;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to start quest {questId}: {ex.Message}");
                return false;
            }
        }
        
        /// <summary>
        /// Complete a quest
        /// </summary>
        /// <param name="questId">Quest ID</param>
        /// <param name="characterId">Character ID</param>
        /// <returns>Success status</returns>
        public async Task<bool> CompleteQuestAsync(string questId, string characterId)
        {
            try
            {
                var success = await questService.CompleteQuestAsync(questId, characterId);
                
                if (success)
                {
                    // Update cache
                    await RefreshQuestCache(questId);
                    
                    // Get updated quest and fire event
                    var quest = await questService.GetQuestAsync(questId);
                    if (quest != null)
                    {
                        OnQuestCompleted?.Invoke(quest);
                    }
                }
                
                return success;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to complete quest {questId}: {ex.Message}");
                return false;
            }
        }
        
        /// <summary>
        /// Update quest step progress
        /// </summary>
        /// <param name="questId">Quest ID</param>
        /// <param name="stepId">Step ID</param>
        /// <param name="progress">Progress update</param>
        /// <returns>Success status</returns>
        public async Task<bool> UpdateQuestStepAsync(string questId, string stepId, QuestStepUpdateDTO progress)
        {
            try
            {
                var success = await questService.UpdateQuestStepAsync(questId, stepId, progress);
                
                if (success)
                {
                    // Update cache
                    await RefreshQuestCache(questId);
                    
                    // Get updated quest and fire event
                    var quest = await questService.GetQuestAsync(questId);
                    if (quest != null)
                    {
                        OnQuestUpdated?.Invoke(quest);
                    }
                }
                
                return success;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to update quest step {stepId}: {ex.Message}");
                return false;
            }
        }
        
        /// <summary>
        /// Generate new quests for a character
        /// </summary>
        /// <param name="characterId">Character ID</param>
        /// <param name="count">Number of quests to generate</param>
        /// <returns>Generated quests</returns>
        public async Task<List<QuestDTO>> GenerateQuestsAsync(string characterId, int count = 3)
        {
            try
            {
                var request = new
                {
                    CharacterId = characterId,
                    Count = count,
                    Timestamp = DateTime.UtcNow
                };
                
                var quests = await questService.GenerateQuestsAsync(request);
                
                // Update cache
                foreach (var quest in quests)
                {
                    UpdateQuestInCache(quest);
                    OnQuestAdded?.Invoke(quest);
                }
                
                return quests;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to generate quests: {ex.Message}");
                return new List<QuestDTO>();
            }
        }
        
        #endregion
        
        #region Cache Management
        
        /// <summary>
        /// Load initial quest data into cache
        /// </summary>
        private async Task LoadQuestData()
        {
            try
            {
                // Load all quests
                allQuests = await questService.GetQuestsAsync();
                
                // Populate cache
                questCache.Clear();
                foreach (var quest in allQuests)
                {
                    questCache[quest.Id] = quest;
                }
                
                lastSyncTime = DateTime.UtcNow;
                DebugLog($"Loaded {allQuests.Count} quests into cache");
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to load quest data: {ex.Message}");
            }
        }
        
        /// <summary>
        /// Refresh a specific quest in cache
        /// </summary>
        /// <param name="questId">Quest ID to refresh</param>
        private async Task RefreshQuestCache(string questId)
        {
            try
            {
                var quest = await questService.GetQuestAsync(questId);
                if (quest != null)
                {
                    UpdateQuestInCache(quest);
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to refresh quest cache for {questId}: {ex.Message}");
            }
        }
        
        /// <summary>
        /// Update a quest in the cache
        /// </summary>
        /// <param name="quest">Quest to update</param>
        private void UpdateQuestInCache(QuestDTO quest)
        {
            questCache[quest.Id] = quest;
            
            // Update in allQuests list
            var existingIndex = allQuests.FindIndex(q => q.Id == quest.Id);
            if (existingIndex >= 0)
            {
                allQuests[existingIndex] = quest;
            }
            else
            {
                allQuests.Add(quest);
            }
            
            // Clear character quest cache to force refresh
            characterQuests.Clear();
        }
        
        /// <summary>
        /// Clear all cached data
        /// </summary>
        private void ClearCache()
        {
            questCache.Clear();
            characterQuests.Clear();
            allQuests.Clear();
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
                eventIntegration.OnQuestGenerated += HandleQuestGenerated;
                eventIntegration.OnQuestProgress += HandleQuestProgress;
            }
            
            if (questLogUI != null)
            {
                questLogUI.OnQuestStartRequested += StartQuestAsync;
                questLogUI.OnQuestCompleteRequested += CompleteQuestAsync;
            }
        }
        
        /// <summary>
        /// Clean up event handlers
        /// </summary>
        private void CleanupEventHandlers()
        {
            if (eventIntegration != null)
            {
                eventIntegration.OnQuestGenerated -= HandleQuestGenerated;
                eventIntegration.OnQuestProgress -= HandleQuestProgress;
            }
            
            if (questLogUI != null)
            {
                questLogUI.OnQuestStartRequested -= StartQuestAsync;
                questLogUI.OnQuestCompleteRequested -= CompleteQuestAsync;
            }
        }
        
        /// <summary>
        /// Handle quest generation events
        /// </summary>
        /// <param name="quest">Generated quest</param>
        private void HandleQuestGenerated(QuestDTO quest)
        {
            UpdateQuestInCache(quest);
            OnQuestAdded?.Invoke(quest);
        }
        
        /// <summary>
        /// Handle quest progress events
        /// </summary>
        /// <param name="questId">Quest ID</param>
        /// <param name="progress">Progress data</param>
        private async void HandleQuestProgress(string questId, object progress)
        {
            await RefreshQuestCache(questId);
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
                await LoadQuestData();
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
                Debug.Log($"[QuestSystem] {message}");
            }
        }
        
        /// <summary>
        /// Get quest from cache
        /// </summary>
        /// <param name="questId">Quest ID</param>
        /// <returns>Cached quest or null</returns>
        public QuestDTO GetCachedQuest(string questId)
        {
            return questCache.TryGetValue(questId, out var quest) ? quest : null;
        }
        
        /// <summary>
        /// Get all cached quests
        /// </summary>
        /// <returns>List of all cached quests</returns>
        public List<QuestDTO> GetAllCachedQuests()
        {
            return new List<QuestDTO>(allQuests);
        }
        
        /// <summary>
        /// Check if quest is available for character
        /// </summary>
        /// <param name="questId">Quest ID</param>
        /// <param name="characterId">Character ID</param>
        /// <returns>True if quest is available</returns>
        public bool IsQuestAvailable(string questId, string characterId)
        {
            var quest = GetCachedQuest(questId);
            if (quest == null) return false;
            
            // Check prerequisites, level requirements, etc.
            // Implementation would depend on game logic
            return quest.Status?.ToLower() == "available";
        }
        
        #endregion
    }
} 