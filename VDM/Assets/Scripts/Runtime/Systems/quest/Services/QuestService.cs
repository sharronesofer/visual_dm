using System.Collections.Generic;
using System.Threading.Tasks;
using System;
using UnityEngine;
using VDM.Infrastructure.Services;
using VDM.Systems.Quest.Models;
using VDM.DTOs.Common;
using System.Linq;
using QuestDTO = VDM.Systems.Quest.Models.QuestDTO;

namespace VDM.Systems.Quest.Services
{
    /// <summary>
    /// Service for Quest HTTP API communication with backend
    /// </summary>
    public class QuestService : BaseHTTPClient
    {
        private static QuestService _instance;
        public static QuestService Instance
        {
            get
            {
                if (_instance == null)
                {
                    _instance = FindObjectOfType<QuestService>();
                    if (_instance == null)
                    {
                        GameObject go = new GameObject("QuestService");
                        _instance = go.AddComponent<QuestService>();
                        DontDestroyOnLoad(go);
                    }
                }
                return _instance;
            }
        }

        [Header("Quest Service Settings")]
        [SerializeField] private bool enableLogging = true;
        
        private List<QuestDTO> activeQuests = new List<QuestDTO>();
        private List<QuestDTO> completedQuests = new List<QuestDTO>();

        protected override string GetClientName()
        {
            return "QuestService";
        }
        
        void Start()
        {
            if (_instance != null && _instance != this)
            {
                Destroy(gameObject);
                return;
            }
            
            _instance = this;
            DontDestroyOnLoad(gameObject);
            InitializeClient();
        }
        
        /// <summary>
        /// Get all quests with optional filtering
        /// </summary>
        /// <param name="status">Filter by quest status</param>
        /// <param name="type">Filter by quest type</param>
        /// <param name="characterId">Filter by character ID</param>
        /// <param name="factionId">Filter by faction ID</param>
        /// <param name="regionId">Filter by region ID</param>
        /// <param name="arcId">Filter by arc ID</param>
        /// <returns>List of quest DTOs</returns>
        public async Task<List<QuestDTO>> GetQuestsAsync(
            string status = null, 
            string type = null, 
            string characterId = null,
            string factionId = null,
            string regionId = null,
            string arcId = null)
        {
            return await Task.Run(() =>
            {
                var tcs = new TaskCompletionSource<List<QuestDTO>>();
                
                try
                {
                    var queryParams = new List<string>();
                    
                    if (!string.IsNullOrEmpty(status))
                        queryParams.Add($"status={status}");
                    if (!string.IsNullOrEmpty(type))
                        queryParams.Add($"type={type}");
                    if (!string.IsNullOrEmpty(characterId))
                        queryParams.Add($"character_id={characterId}");
                    if (!string.IsNullOrEmpty(factionId))
                        queryParams.Add($"faction_id={factionId}");
                    if (!string.IsNullOrEmpty(regionId))
                        queryParams.Add($"region_id={regionId}");
                    if (!string.IsNullOrEmpty(arcId))
                        queryParams.Add($"arc_id={arcId}");
                    
                    var query = queryParams.Count > 0 ? "?" + string.Join("&", queryParams) : "";
                    var endpoint = $"/quest{query}";
                    
                    StartCoroutine(GetRequestCoroutine(endpoint, (success, response) =>
                    {
                        if (success)
                        {
                            var result = SafeDeserializeList<QuestDTO>(response);
                            tcs.SetResult(result ?? new List<QuestDTO>());
                        }
                        else
                        {
                            if (enableLogging)
                                Debug.LogError($"Failed to get quests: {response}");
                            tcs.SetResult(new List<QuestDTO>());
                        }
                    }));
                }
                catch (Exception ex)
                {
                    if (enableLogging)
                        Debug.LogError($"Failed to get quests: {ex.Message}");
                    tcs.SetResult(new List<QuestDTO>());
                }
                
                return tcs.Task;
            });
        }
        
        /// <summary>
        /// Get a specific quest by ID
        /// </summary>
        /// <param name="questId">Quest ID</param>
        /// <returns>Quest DTO or null if not found</returns>
        public async Task<QuestDTO> GetQuestAsync(string questId)
        {
            return await Task.Run(() =>
            {
                var tcs = new TaskCompletionSource<QuestDTO>();
                
                try
                {
                    if (enableLogging)
                        Debug.Log($"QuestService: Getting quest {questId}");
                    
                    if (string.IsNullOrEmpty(questId))
                    {
                        if (enableLogging)
                            Debug.LogError("Quest ID cannot be null or empty");
                        tcs.SetResult(null);
                        return tcs.Task;
                    }
                    
                    var endpoint = $"/quest/{questId}";
                    StartCoroutine(GetRequestCoroutine(endpoint, (success, response) =>
                    {
                        if (success)
                        {
                            var result = SafeDeserialize<QuestDTO>(response);
                            tcs.SetResult(result);
                        }
                        else
                        {
                            if (enableLogging)
                                Debug.LogError($"QuestService: Failed to get quest {questId} - {response}");
                            tcs.SetResult(null);
                        }
                    }));
                }
                catch (Exception ex)
                {
                    if (enableLogging)
                        Debug.LogError($"QuestService: Failed to get quest {questId} - {ex.Message}");
                    tcs.SetResult(null);
                }
                
                return tcs.Task;
            });
        }
        
        /// <summary>
        /// Create a new quest
        /// </summary>
        /// <param name="request">Quest creation request</param>
        /// <returns>Created quest DTO</returns>
        public async Task<QuestDTO> CreateQuestAsync(CreateQuestRequestDTO request)
        {
            return await Task.Run(() =>
            {
                var tcs = new TaskCompletionSource<QuestDTO>();
                
                try
                {
                    if (request == null)
                    {
                        if (enableLogging)
                            Debug.LogError("Create quest request cannot be null");
                        tcs.SetResult(null);
                        return tcs.Task;
                    }
                    
                    StartCoroutine(PostRequestCoroutine("/quest", request, (success, response) =>
                    {
                        if (success)
                        {
                            var result = SafeDeserialize<QuestDTO>(response);
                            tcs.SetResult(result);
                        }
                        else
                        {
                            if (enableLogging)
                                Debug.LogError($"Failed to create quest: {response}");
                            tcs.SetResult(null);
                        }
                    }));
                }
                catch (Exception ex)
                {
                    if (enableLogging)
                        Debug.LogError($"Failed to create quest: {ex.Message}");
                    tcs.SetResult(null);
                }
                
                return tcs.Task;
            });
        }
        
        /// <summary>
        /// Update an existing quest
        /// </summary>
        /// <param name="questId">Quest ID to update</param>
        /// <param name="request">Quest update request</param>
        /// <returns>Updated quest DTO</returns>
        public async Task<QuestDTO> UpdateQuestAsync(string questId, UpdateQuestRequestDTO request)
        {
            try
            {
                if (string.IsNullOrEmpty(questId))
                {
                    if (enableLogging)
                        Debug.LogError("Quest ID cannot be null or empty");
                    return null;
                }
                
                if (request == null)
                {
                    if (enableLogging)
                        Debug.LogError("Update quest request cannot be null");
                    return null;
                }
                
                var url = $"/quest/{questId}";
                return await PutAsync<QuestDTO>(url, request);
            }
            catch (Exception ex)
            {
                if (enableLogging)
                    Debug.LogError($"Failed to update quest {questId}: {ex.Message}");
                return null;
            }
        }
        
        /// <summary>
        /// Delete a quest
        /// </summary>
        /// <param name="questId">Quest ID to delete</param>
        /// <returns>True if successful</returns>
        public async Task<bool> DeleteQuestAsync(string questId)
        {
            try
            {
                if (string.IsNullOrEmpty(questId))
                {
                    if (enableLogging)
                        Debug.LogError("Quest ID cannot be null or empty");
                    return false;
                }
                
                var url = $"/quest/{questId}";
                return await DeleteAsync(url);
            }
            catch (Exception ex)
            {
                if (enableLogging)
                    Debug.LogError($"Failed to delete quest {questId}: {ex.Message}");
                return false;
            }
        }
        
        /// <summary>
        /// Start a quest for a character
        /// </summary>
        /// <param name="questId">Quest ID to start</param>
        /// <param name="characterId">Character ID</param>
        /// <returns>Updated quest DTO</returns>
        public async Task<QuestDTO> StartQuestAsync(string questId, string characterId)
        {
            try
            {
                if (string.IsNullOrEmpty(questId) || string.IsNullOrEmpty(characterId))
                {
                    if (enableLogging)
                        Debug.LogError("Quest ID and Character ID cannot be null or empty");
                    return null;
                }
                
                var url = $"/quest/{questId}/start";
                var request = new { character_id = characterId };
                return await PostAsync<QuestDTO>(url, request);
            }
            catch (Exception ex)
            {
                if (enableLogging)
                    Debug.LogError($"Failed to start quest {questId} for character {characterId}: {ex.Message}");
                return null;
            }
        }
        
        /// <summary>
        /// Complete a quest for a character
        /// </summary>
        /// <param name="questId">Quest ID to complete</param>
        /// <param name="characterId">Character ID</param>
        /// <returns>Updated quest DTO</returns>
        public async Task<QuestDTO> CompleteQuestAsync(string questId, string characterId)
        {
            try
            {
                if (string.IsNullOrEmpty(questId) || string.IsNullOrEmpty(characterId))
                {
                    if (enableLogging)
                        Debug.LogError("Quest ID and Character ID cannot be null or empty");
                    return null;
                }
                
                var url = $"/quest/{questId}/complete";
                var request = new { character_id = characterId };
                return await PostAsync<QuestDTO>(url, request);
            }
            catch (Exception ex)
            {
                if (enableLogging)
                    Debug.LogError($"Failed to complete quest {questId} for character {characterId}: {ex.Message}");
                return null;
            }
        }
        
        /// <summary>
        /// Update quest step progress
        /// </summary>
        /// <param name="questId">Quest ID</param>
        /// <param name="stepId">Step ID</param>
        /// <param name="progress">Progress data</param>
        /// <returns>Updated quest DTO</returns>
        public async Task<QuestDTO> UpdateQuestStepAsync(string questId, int stepId, Dictionary<string, object> progress)
        {
            try
            {
                if (string.IsNullOrEmpty(questId))
                {
                    if (enableLogging)
                        Debug.LogError("Quest ID cannot be null or empty");
                    return null;
                }
                
                var url = $"/quest/{questId}/steps/{stepId}";
                return await PutAsync<QuestDTO>(url, progress);
            }
            catch (Exception ex)
            {
                if (enableLogging)
                    Debug.LogError($"Failed to update quest step {stepId} for quest {questId}: {ex.Message}");
                return null;
            }
        }
        
        /// <summary>
        /// Get available quests for a character based on their progress and requirements
        /// </summary>
        /// <param name="characterId">Character ID</param>
        /// <returns>List of available quest DTOs</returns>
        public async Task<List<QuestDTO>> GetAvailableQuestsAsync(string characterId)
        {
            try
            {
                if (string.IsNullOrEmpty(characterId))
                {
                    if (enableLogging)
                        Debug.LogError("Character ID cannot be null or empty");
                    return new List<QuestDTO>();
                }
                
                var url = $"/quest/available/{characterId}";
                var response = await GetAsync<List<QuestDTO>>(url);
                
                return response ?? new List<QuestDTO>();
            }
            catch (Exception ex)
            {
                if (enableLogging)
                    Debug.LogError($"Failed to get available quests for character {characterId}: {ex.Message}");
                return new List<QuestDTO>();
            }
        }
        
        /// <summary>
        /// Get active quests for a character
        /// </summary>
        /// <param name="characterId">Character ID</param>
        /// <returns>List of active quest DTOs</returns>
        public async Task<List<QuestDTO>> GetActiveQuestsAsync(string characterId)
        {
            try
            {
                if (string.IsNullOrEmpty(characterId))
                {
                    if (enableLogging)
                        Debug.LogError("Character ID cannot be null or empty");
                    return new List<QuestDTO>();
                }
                
                var url = $"/quest/active/{characterId}";
                var response = await GetAsync<List<QuestDTO>>(url);
                
                return response ?? new List<QuestDTO>();
            }
            catch (Exception ex)
            {
                if (enableLogging)
                    Debug.LogError($"Failed to get active quests for character {characterId}: {ex.Message}");
                return new List<QuestDTO>();
            }
        }
        
        /// <summary>
        /// Get completed quests for a character
        /// </summary>
        /// <param name="characterId">Character ID</param>
        /// <returns>List of completed quest DTOs</returns>
        public async Task<List<QuestDTO>> GetCompletedQuestsAsync(string characterId)
        {
            try
            {
                if (string.IsNullOrEmpty(characterId))
                {
                    if (enableLogging)
                        Debug.LogError("Character ID cannot be null or empty");
                    return new List<QuestDTO>();
                }
                
                var url = $"/quest/completed/{characterId}";
                var response = await GetAsync<List<QuestDTO>>(url);
                
                return response ?? new List<QuestDTO>();
            }
            catch (Exception ex)
            {
                if (enableLogging)
                    Debug.LogError($"Failed to get completed quests for character {characterId}: {ex.Message}");
                return new List<QuestDTO>();
            }
        }
        
        /// <summary>
        /// Generate new quests based on character, faction, and world state
        /// </summary>
        /// <param name="parameters">Quest generation parameters</param>
        /// <returns>List of generated quest DTOs</returns>
        public async Task<List<QuestDTO>> GenerateQuestsAsync(Dictionary<string, object> parameters)
        {
            try
            {
                var url = $"/quest/generate";
                var response = await PostAsync<List<QuestDTO>>(url, parameters);
                
                return response ?? new List<QuestDTO>();
            }
            catch (Exception ex)
            {
                if (enableLogging)
                    Debug.LogError($"Failed to generate quests: {ex.Message}");
                return new List<QuestDTO>();
            }
        }
        
        /// <summary>
        /// Get quest statistics and analytics
        /// </summary>
        /// <param name="characterId">Optional character ID for character-specific stats</param>
        /// <returns>Quest statistics data</returns>
        public async Task<Dictionary<string, object>> GetQuestStatsAsync(string characterId = null)
        {
            try
            {
                var url = $"/quest/stats";
                if (!string.IsNullOrEmpty(characterId))
                {
                    url += $"?character_id={characterId}";
                }
                
                var response = await GetAsync<Dictionary<string, object>>(url);
                return response ?? new Dictionary<string, object>();
            }
            catch (Exception ex)
            {
                if (enableLogging)
                    Debug.LogError($"Failed to get quest stats: {ex.Message}");
                return new Dictionary<string, object>();
            }
        }

        public void AddQuest(QuestDTO quest)
        {
            if (quest != null && !activeQuests.Exists(q => q.id == quest.id))
            {
                activeQuests.Add(quest);
                if (enableLogging)
                    Debug.Log($"QuestService: Added quest {quest.id}");
            }
        }
    }

    [Serializable]
    public class QuestDTO
    {
        public string id;
        public string title;
        public string description;
        public string status;
        public List<string> objectives;
        public Dictionary<string, object> rewards;
        public DateTime createdAt;
        public DateTime? completedAt;
        
        public QuestDTO()
        {
            objectives = new List<string>();
            rewards = new Dictionary<string, object>();
            status = "active";
            createdAt = DateTime.UtcNow;
        }
    }
} 