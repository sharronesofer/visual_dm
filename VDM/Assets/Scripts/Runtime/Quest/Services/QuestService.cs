using System.Collections.Generic;
using System.Threading.Tasks;
using System;
using UnityEngine;
using VDM.Runtime.Core;
using VDM.Runtime.Quest.Models;
using VDM.Runtime.Services;


namespace VDM.Runtime.Quest.Services
{
    /// <summary>
    /// Service for Quest HTTP API communication with backend
    /// </summary>
    public class QuestService : BaseHttpService
    {
        private readonly string _baseUrl;
        
        public QuestService() : base()
        {
            _baseUrl = "/api/v1/quests";
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
            try
            {
                var queryParams = new Dictionary<string, string>();
                
                if (!string.IsNullOrEmpty(status))
                    queryParams.Add("status", status);
                if (!string.IsNullOrEmpty(type))
                    queryParams.Add("type", type);
                if (!string.IsNullOrEmpty(characterId))
                    queryParams.Add("character_id", characterId);
                if (!string.IsNullOrEmpty(factionId))
                    queryParams.Add("faction_id", factionId);
                if (!string.IsNullOrEmpty(regionId))
                    queryParams.Add("region_id", regionId);
                if (!string.IsNullOrEmpty(arcId))
                    queryParams.Add("arc_id", arcId);
                
                var url = BuildUrlWithQuery(_baseUrl, queryParams);
                var response = await GetAsync<List<QuestDTO>>(url);
                
                return response ?? new List<QuestDTO>();
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get quests: {ex.Message}");
                return new List<QuestDTO>();
            }
        }
        
        /// <summary>
        /// Get a specific quest by ID
        /// </summary>
        /// <param name="questId">Quest ID</param>
        /// <returns>Quest DTO or null if not found</returns>
        public async Task<QuestDTO> GetQuestAsync(string questId)
        {
            try
            {
                if (string.IsNullOrEmpty(questId))
                {
                    Debug.LogError("Quest ID cannot be null or empty");
                    return null;
                }
                
                var url = $"{_baseUrl}/{questId}";
                return await GetAsync<QuestDTO>(url);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get quest {questId}: {ex.Message}");
                return null;
            }
        }
        
        /// <summary>
        /// Create a new quest
        /// </summary>
        /// <param name="request">Quest creation request</param>
        /// <returns>Created quest DTO</returns>
        public async Task<QuestDTO> CreateQuestAsync(CreateQuestRequestDTO request)
        {
            try
            {
                if (request == null)
                {
                    Debug.LogError("Create quest request cannot be null");
                    return null;
                }
                
                return await PostAsync<QuestDTO>(_baseUrl, request);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to create quest: {ex.Message}");
                return null;
            }
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
                    Debug.LogError("Quest ID cannot be null or empty");
                    return null;
                }
                
                if (request == null)
                {
                    Debug.LogError("Update quest request cannot be null");
                    return null;
                }
                
                var url = $"{_baseUrl}/{questId}";
                return await PutAsync<QuestDTO>(url, request);
            }
            catch (Exception ex)
            {
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
                    Debug.LogError("Quest ID cannot be null or empty");
                    return false;
                }
                
                var url = $"{_baseUrl}/{questId}";
                return await DeleteAsync(url);
            }
            catch (Exception ex)
            {
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
                    Debug.LogError("Quest ID and Character ID cannot be null or empty");
                    return null;
                }
                
                var url = $"{_baseUrl}/{questId}/start";
                var request = new { character_id = characterId };
                return await PostAsync<QuestDTO>(url, request);
            }
            catch (Exception ex)
            {
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
                    Debug.LogError("Quest ID and Character ID cannot be null or empty");
                    return null;
                }
                
                var url = $"{_baseUrl}/{questId}/complete";
                var request = new { character_id = characterId };
                return await PostAsync<QuestDTO>(url, request);
            }
            catch (Exception ex)
            {
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
                    Debug.LogError("Quest ID cannot be null or empty");
                    return null;
                }
                
                var url = $"{_baseUrl}/{questId}/steps/{stepId}";
                return await PutAsync<QuestDTO>(url, progress);
            }
            catch (Exception ex)
            {
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
                    Debug.LogError("Character ID cannot be null or empty");
                    return new List<QuestDTO>();
                }
                
                var url = $"{_baseUrl}/available/{characterId}";
                var response = await GetAsync<List<QuestDTO>>(url);
                
                return response ?? new List<QuestDTO>();
            }
            catch (Exception ex)
            {
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
                    Debug.LogError("Character ID cannot be null or empty");
                    return new List<QuestDTO>();
                }
                
                var url = $"{_baseUrl}/active/{characterId}";
                var response = await GetAsync<List<QuestDTO>>(url);
                
                return response ?? new List<QuestDTO>();
            }
            catch (Exception ex)
            {
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
                    Debug.LogError("Character ID cannot be null or empty");
                    return new List<QuestDTO>();
                }
                
                var url = $"{_baseUrl}/completed/{characterId}";
                var response = await GetAsync<List<QuestDTO>>(url);
                
                return response ?? new List<QuestDTO>();
            }
            catch (Exception ex)
            {
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
                var url = $"{_baseUrl}/generate";
                var response = await PostAsync<List<QuestDTO>>(url, parameters);
                
                return response ?? new List<QuestDTO>();
            }
            catch (Exception ex)
            {
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
                var url = $"{_baseUrl}/stats";
                if (!string.IsNullOrEmpty(characterId))
                {
                    url += $"?character_id={characterId}";
                }
                
                var response = await GetAsync<Dictionary<string, object>>(url);
                return response ?? new Dictionary<string, object>();
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get quest stats: {ex.Message}");
                return new Dictionary<string, object>();
            }
        }
    }
} 