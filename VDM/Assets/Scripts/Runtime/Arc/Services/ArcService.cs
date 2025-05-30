using System.Collections.Generic;
using System.Threading.Tasks;
using System;
using UnityEngine;
using VDM.Runtime.Core;
using VDM.Runtime.Arc.Models;
using VDM.Runtime.Services;


namespace VDM.Runtime.Arc.Services
{
    /// <summary>
    /// Service for Arc HTTP API communication with backend
    /// </summary>
    public class ArcService : BaseHttpService
    {
        private readonly string _baseUrl;
        
        public ArcService() : base()
        {
            _baseUrl = "/api/v1/arcs";
        }
        
        #region Arc CRUD Operations
        
        /// <summary>
        /// Get all arcs with optional filtering
        /// </summary>
        /// <param name="arcType">Filter by arc type</param>
        /// <param name="status">Filter by arc status</param>
        /// <param name="characterId">Filter by character ID</param>
        /// <param name="factionId">Filter by faction ID</param>
        /// <param name="regionId">Filter by region ID</param>
        /// <param name="priority">Filter by priority level</param>
        /// <returns>List of arc models</returns>
        public async Task<List<ArcModel>> GetArcsAsync(
            ArcType? arcType = null,
            ArcStatus? status = null,
            string characterId = null,
            string factionId = null,
            string regionId = null,
            ArcPriority? priority = null)
        {
            try
            {
                var queryParams = new Dictionary<string, string>();
                
                if (arcType.HasValue)
                    queryParams.Add("arc_type", arcType.Value.ToString().ToLower());
                if (status.HasValue)
                    queryParams.Add("status", status.Value.ToString().ToLower());
                if (!string.IsNullOrEmpty(characterId))
                    queryParams.Add("character_id", characterId);
                if (!string.IsNullOrEmpty(factionId))
                    queryParams.Add("faction_id", factionId);
                if (!string.IsNullOrEmpty(regionId))
                    queryParams.Add("region_id", regionId);
                if (priority.HasValue)
                    queryParams.Add("priority", priority.Value.ToString().ToLower());
                
                var url = BuildUrlWithQuery(_baseUrl, queryParams);
                var response = await GetAsync<List<ArcModel>>(url);
                
                return response ?? new List<ArcModel>();
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get arcs: {ex.Message}");
                return new List<ArcModel>();
            }
        }
        
        /// <summary>
        /// Get a specific arc by ID
        /// </summary>
        /// <param name="arcId">Arc ID</param>
        /// <returns>Arc model or null if not found</returns>
        public async Task<ArcModel> GetArcAsync(string arcId)
        {
            try
            {
                if (string.IsNullOrEmpty(arcId))
                {
                    Debug.LogError("Arc ID cannot be null or empty");
                    return null;
                }
                
                var url = $"{_baseUrl}/{arcId}";
                var response = await GetAsync<ArcModel>(url);
                
                return response;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get arc {arcId}: {ex.Message}");
                return null;
            }
        }
        
        /// <summary>
        /// Create a new arc
        /// </summary>
        /// <param name="createRequest">Arc creation request</param>
        /// <returns>Created arc model</returns>
        public async Task<ArcModel> CreateArcAsync(CreateArcRequestModel createRequest)
        {
            try
            {
                if (createRequest == null)
                {
                    Debug.LogError("Create request cannot be null");
                    return null;
                }
                
                var response = await PostAsync<ArcModel>(_baseUrl, createRequest);
                
                return response;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to create arc: {ex.Message}");
                return null;
            }
        }
        
        /// <summary>
        /// Update an existing arc
        /// </summary>
        /// <param name="arcId">Arc ID to update</param>
        /// <param name="updateRequest">Arc update request</param>
        /// <returns>Updated arc model</returns>
        public async Task<ArcModel> UpdateArcAsync(string arcId, UpdateArcRequestModel updateRequest)
        {
            try
            {
                if (string.IsNullOrEmpty(arcId))
                {
                    Debug.LogError("Arc ID cannot be null or empty");
                    return null;
                }
                
                if (updateRequest == null)
                {
                    Debug.LogError("Update request cannot be null");
                    return null;
                }
                
                var url = $"{_baseUrl}/{arcId}";
                var response = await PutAsync<ArcModel>(url, updateRequest);
                
                return response;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to update arc {arcId}: {ex.Message}");
                return null;
            }
        }
        
        /// <summary>
        /// Delete an arc
        /// </summary>
        /// <param name="arcId">Arc ID to delete</param>
        /// <returns>True if deleted successfully</returns>
        public async Task<bool> DeleteArcAsync(string arcId)
        {
            try
            {
                if (string.IsNullOrEmpty(arcId))
                {
                    Debug.LogError("Arc ID cannot be null or empty");
                    return false;
                }
                
                var url = $"{_baseUrl}/{arcId}";
                await DeleteAsync(url);
                
                return true;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to delete arc {arcId}: {ex.Message}");
                return false;
            }
        }
        
        #endregion
        
        #region Arc Steps
        
        /// <summary>
        /// Get steps for a specific arc
        /// </summary>
        /// <param name="arcId">Arc ID</param>
        /// <returns>List of arc step models</returns>
        public async Task<List<ArcStepModel>> GetArcStepsAsync(string arcId)
        {
            try
            {
                if (string.IsNullOrEmpty(arcId))
                {
                    Debug.LogError("Arc ID cannot be null or empty");
                    return new List<ArcStepModel>();
                }
                
                var url = $"{_baseUrl}/{arcId}/steps";
                var response = await GetAsync<List<ArcStepModel>>(url);
                
                return response ?? new List<ArcStepModel>();
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get arc steps for {arcId}: {ex.Message}");
                return new List<ArcStepModel>();
            }
        }
        
        /// <summary>
        /// Get a specific arc step
        /// </summary>
        /// <param name="arcId">Arc ID</param>
        /// <param name="stepId">Step ID</param>
        /// <returns>Arc step model or null if not found</returns>
        public async Task<ArcStepModel> GetArcStepAsync(string arcId, int stepId)
        {
            try
            {
                if (string.IsNullOrEmpty(arcId))
                {
                    Debug.LogError("Arc ID cannot be null or empty");
                    return null;
                }
                
                var url = $"{_baseUrl}/{arcId}/steps/{stepId}";
                var response = await GetAsync<ArcStepModel>(url);
                
                return response;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get arc step {stepId} for arc {arcId}: {ex.Message}");
                return null;
            }
        }
        
        /// <summary>
        /// Update arc step status
        /// </summary>
        /// <param name="arcId">Arc ID</param>
        /// <param name="stepId">Step ID</param>
        /// <param name="status">New step status</param>
        /// <returns>Updated arc step model</returns>
        public async Task<ArcStepModel> UpdateStepStatusAsync(string arcId, int stepId, ArcStepStatus status)
        {
            try
            {
                if (string.IsNullOrEmpty(arcId))
                {
                    Debug.LogError("Arc ID cannot be null or empty");
                    return null;
                }
                
                var url = $"{_baseUrl}/{arcId}/steps/{stepId}/status";
                var requestData = new { status = status.ToString().ToLower() };
                var response = await PutAsync<ArcStepModel>(url, requestData);
                
                return response;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to update step {stepId} status for arc {arcId}: {ex.Message}");
                return null;
            }
        }
        
        #endregion
        
        #region Arc Progression
        
        /// <summary>
        /// Get arc progression data
        /// </summary>
        /// <param name="arcId">Arc ID</param>
        /// <param name="characterId">Character ID (optional)</param>
        /// <returns>Arc progression model</returns>
        public async Task<ArcProgressionModel> GetProgressionAsync(string arcId, string characterId = null)
        {
            try
            {
                if (string.IsNullOrEmpty(arcId))
                {
                    Debug.LogError("Arc ID cannot be null or empty");
                    return null;
                }
                
                var queryParams = new Dictionary<string, string>();
                if (!string.IsNullOrEmpty(characterId))
                    queryParams.Add("character_id", characterId);
                
                var url = BuildUrlWithQuery($"{_baseUrl}/{arcId}/progression", queryParams);
                var response = await GetAsync<ArcProgressionModel>(url);
                
                return response;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get progression for arc {arcId}: {ex.Message}");
                return null;
            }
        }
        
        /// <summary>
        /// Update arc progression
        /// </summary>
        /// <param name="arcId">Arc ID</param>
        /// <param name="characterId">Character ID</param>
        /// <param name="currentStep">Current step index</param>
        /// <param name="completionPercentage">Completion percentage</param>
        /// <returns>Updated progression model</returns>
        public async Task<ArcProgressionModel> UpdateProgressionAsync(
            string arcId, 
            string characterId, 
            int currentStep, 
            float completionPercentage)
        {
            try
            {
                if (string.IsNullOrEmpty(arcId))
                {
                    Debug.LogError("Arc ID cannot be null or empty");
                    return null;
                }
                
                var url = $"{_baseUrl}/{arcId}/progression";
                var requestData = new
                {
                    character_id = characterId,
                    current_step = currentStep,
                    completion_percentage = completionPercentage
                };
                
                var response = await PutAsync<ArcProgressionModel>(url, requestData);
                
                return response;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to update progression for arc {arcId}: {ex.Message}");
                return null;
            }
        }
        
        #endregion
        
        #region Arc Generation and Integration
        
        /// <summary>
        /// Generate a new arc using AI
        /// </summary>
        /// <param name="generateRequest">Arc generation request</param>
        /// <returns>Generated arc model</returns>
        public async Task<ArcModel> GenerateArcAsync(ArcGenerateRequestModel generateRequest)
        {
            try
            {
                if (generateRequest == null)
                {
                    Debug.LogError("Generate request cannot be null");
                    return null;
                }
                
                var url = $"{_baseUrl}/generate";
                var response = await PostAsync<ArcModel>(url, generateRequest);
                
                return response;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to generate arc: {ex.Message}");
                return null;
            }
        }
        
        /// <summary>
        /// Get quest opportunities for an arc
        /// </summary>
        /// <param name="arcId">Arc ID</param>
        /// <param name="characterId">Character ID (optional)</param>
        /// <returns>List of quest opportunities</returns>
        public async Task<List<QuestOpportunityModel>> GetQuestOpportunitiesAsync(string arcId, string characterId = null)
        {
            try
            {
                if (string.IsNullOrEmpty(arcId))
                {
                    Debug.LogError("Arc ID cannot be null or empty");
                    return new List<QuestOpportunityModel>();
                }
                
                var queryParams = new Dictionary<string, string>();
                if (!string.IsNullOrEmpty(characterId))
                    queryParams.Add("character_id", characterId);
                
                var url = BuildUrlWithQuery($"{_baseUrl}/{arcId}/quest-opportunities", queryParams);
                var response = await GetAsync<List<QuestOpportunityModel>>(url);
                
                return response ?? new List<QuestOpportunityModel>();
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get quest opportunities for arc {arcId}: {ex.Message}");
                return new List<QuestOpportunityModel>();
            }
        }
        
        /// <summary>
        /// Get arc analytics
        /// </summary>
        /// <param name="arcId">Arc ID</param>
        /// <returns>Arc analytics model</returns>
        public async Task<ArcAnalyticsModel> GetAnalyticsAsync(string arcId)
        {
            try
            {
                if (string.IsNullOrEmpty(arcId))
                {
                    Debug.LogError("Arc ID cannot be null or empty");
                    return null;
                }
                
                var url = $"{_baseUrl}/{arcId}/analytics";
                var response = await GetAsync<ArcAnalyticsModel>(url);
                
                return response;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get analytics for arc {arcId}: {ex.Message}");
                return null;
            }
        }
        
        #endregion
        
        #region Search and Filtering
        
        /// <summary>
        /// Search arcs by keyword
        /// </summary>
        /// <param name="query">Search query</param>
        /// <param name="arcType">Filter by arc type</param>
        /// <param name="limit">Maximum results to return</param>
        /// <returns>List of matching arc models</returns>
        public async Task<List<ArcModel>> SearchArcsAsync(string query, ArcType? arcType = null, int limit = 50)
        {
            try
            {
                if (string.IsNullOrEmpty(query))
                {
                    Debug.LogError("Search query cannot be null or empty");
                    return new List<ArcModel>();
                }
                
                var queryParams = new Dictionary<string, string>
                {
                    ["q"] = query,
                    ["limit"] = limit.ToString()
                };
                
                if (arcType.HasValue)
                    queryParams.Add("arc_type", arcType.Value.ToString().ToLower());
                
                var url = BuildUrlWithQuery($"{_baseUrl}/search", queryParams);
                var response = await GetAsync<List<ArcModel>>(url);
                
                return response ?? new List<ArcModel>();
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to search arcs with query '{query}': {ex.Message}");
                return new List<ArcModel>();
            }
        }
        
        /// <summary>
        /// Get arcs by tags
        /// </summary>
        /// <param name="tags">List of tags to filter by</param>
        /// <param name="matchAll">Whether to match all tags or any tag</param>
        /// <returns>List of matching arc models</returns>
        public async Task<List<ArcModel>> GetArcsByTagsAsync(List<string> tags, bool matchAll = false)
        {
            try
            {
                if (tags == null || tags.Count == 0)
                {
                    Debug.LogError("Tags list cannot be null or empty");
                    return new List<ArcModel>();
                }
                
                var queryParams = new Dictionary<string, string>
                {
                    ["tags"] = string.Join(",", tags),
                    ["match_all"] = matchAll.ToString().ToLower()
                };
                
                var url = BuildUrlWithQuery($"{_baseUrl}/by-tags", queryParams);
                var response = await GetAsync<List<ArcModel>>(url);
                
                return response ?? new List<ArcModel>();
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get arcs by tags: {ex.Message}");
                return new List<ArcModel>();
            }
        }
        
        #endregion
    }
} 