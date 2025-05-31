using System.Collections.Generic;
using System.Threading.Tasks;
using System;
using UnityEngine;
using VDM.Infrastructure.Services;
using VDM.Systems.Npc.Models;


namespace VDM.Systems.Npc.Services
{
    /// <summary>
    /// Service for handling NPC operations via HTTP API
    /// </summary>
    public class NpcService : BaseHttpService
    {
        private const string BaseEndpoint = "/api/npc";
        
        #region NPC Management
        
        /// <summary>
        /// Get all NPCs with optional filtering and pagination
        /// </summary>
        public async Task<NpcListResponse> GetNpcsAsync(int page = 1, int pageSize = 50, string search = null, List<string> tags = null, bool? isActive = null)
        {
            try
            {
                var queryParams = new List<string>();
                
                if (page > 1)
                    queryParams.Add($"page={page}");
                
                if (pageSize != 50)
                    queryParams.Add($"page_size={pageSize}");
                
                if (!string.IsNullOrEmpty(search))
                    queryParams.Add($"search={Uri.EscapeDataString(search)}");
                
                if (tags != null && tags.Count > 0)
                    queryParams.Add($"tags={string.Join(",", tags)}");
                
                if (isActive.HasValue)
                    queryParams.Add($"is_active={isActive.Value.ToString().ToLower()}");
                
                var queryString = queryParams.Count > 0 ? "?" + string.Join("&", queryParams) : "";
                var response = await GetAsync<NpcListResponse>($"{BaseEndpoint}/npcs{queryString}");
                return response ?? new NpcListResponse();
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get NPCs: {ex.Message}");
                throw;
            }
        }
        
        /// <summary>
        /// Get a specific NPC by ID
        /// </summary>
        public async Task<NpcModel> GetNpcAsync(string npcId)
        {
            try
            {
                var response = await GetAsync<NpcModel>($"{BaseEndpoint}/npcs/{npcId}");
                return response;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get NPC {npcId}: {ex.Message}");
                throw;
            }
        }
        
        /// <summary>
        /// Create a new NPC
        /// </summary>
        public async Task<NpcModel> CreateNpcAsync(CreateNpcRequest request)
        {
            try
            {
                var response = await PostAsync<NpcModel>($"{BaseEndpoint}/npcs", request);
                return response;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to create NPC: {ex.Message}");
                throw;
            }
        }
        
        /// <summary>
        /// Update an existing NPC
        /// </summary>
        public async Task<NpcModel> UpdateNpcAsync(string npcId, UpdateNpcRequest request)
        {
            try
            {
                var response = await PutAsync<NpcModel>($"{BaseEndpoint}/npcs/{npcId}", request);
                return response;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to update NPC {npcId}: {ex.Message}");
                throw;
            }
        }
        
        /// <summary>
        /// Delete an NPC
        /// </summary>
        public async Task<bool> DeleteNpcAsync(string npcId)
        {
            try
            {
                await DeleteAsync($"{BaseEndpoint}/npcs/{npcId}");
                return true;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to delete NPC {npcId}: {ex.Message}");
                return false;
            }
        }
        
        /// <summary>
        /// Duplicate an existing NPC with modifications
        /// </summary>
        public async Task<NpcModel> DuplicateNpcAsync(string npcId, string newName = null, Dictionary<string, object> modifications = null)
        {
            try
            {
                var request = new
                {
                    new_name = newName,
                    modifications = modifications ?? new Dictionary<string, object>()
                };
                
                var response = await PostAsync<NpcModel>($"{BaseEndpoint}/npcs/{npcId}/duplicate", request);
                return response;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to duplicate NPC {npcId}: {ex.Message}");
                throw;
            }
        }
        
        #endregion
        
        #region NPC Generation and Building
        
        /// <summary>
        /// Generate a random NPC using the NPC builder
        /// </summary>
        public async Task<NpcModel> GenerateRandomNpcAsync(Dictionary<string, object> parameters = null)
        {
            try
            {
                var request = new
                {
                    generation_method = "random",
                    parameters = parameters ?? new Dictionary<string, object>()
                };
                
                var response = await PostAsync<NpcModel>($"{BaseEndpoint}/generate", request);
                return response;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to generate random NPC: {ex.Message}");
                throw;
            }
        }
        
        /// <summary>
        /// Generate an NPC from a template
        /// </summary>
        public async Task<NpcModel> GenerateNpcFromTemplateAsync(string templateId, Dictionary<string, object> parameters = null)
        {
            try
            {
                var request = new
                {
                    generation_method = "template",
                    template_id = templateId,
                    parameters = parameters ?? new Dictionary<string, object>()
                };
                
                var response = await PostAsync<NpcModel>($"{BaseEndpoint}/generate", request);
                return response;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to generate NPC from template {templateId}: {ex.Message}");
                throw;
            }
        }
        
        /// <summary>
        /// Generate an NPC using AI with specific requirements
        /// </summary>
        public async Task<NpcModel> GenerateAiNpcAsync(string description, Dictionary<string, object> requirements = null)
        {
            try
            {
                var request = new
                {
                    generation_method = "ai",
                    description = description,
                    requirements = requirements ?? new Dictionary<string, object>()
                };
                
                var response = await PostAsync<NpcModel>($"{BaseEndpoint}/generate", request);
                return response;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to generate AI NPC: {ex.Message}");
                throw;
            }
        }
        
        /// <summary>
        /// Get available NPC templates
        /// </summary>
        public async Task<List<Dictionary<string, object>>> GetNpcTemplatesAsync()
        {
            try
            {
                var response = await GetAsync<List<Dictionary<string, object>>>($"{BaseEndpoint}/templates");
                return response ?? new List<Dictionary<string, object>>();
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get NPC templates: {ex.Message}");
                throw;
            }
        }
        
        /// <summary>
        /// Get NPC generation parameters and options
        /// </summary>
        public async Task<Dictionary<string, object>> GetGenerationOptionsAsync()
        {
            try
            {
                var response = await GetAsync<Dictionary<string, object>>($"{BaseEndpoint}/generation-options");
                return response ?? new Dictionary<string, object>();
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get generation options: {ex.Message}");
                throw;
            }
        }
        
        #endregion
        
        #region Memory Management
        
        /// <summary>
        /// Get memories for an NPC with filtering and pagination
        /// </summary>
        public async Task<NpcMemoryResponse> GetNpcMemoriesAsync(string npcId, int page = 1, int pageSize = 50, MemoryType? memoryType = null, MemoryImportance? importance = null)
        {
            try
            {
                var queryParams = new List<string>();
                
                if (page > 1)
                    queryParams.Add($"page={page}");
                
                if (pageSize != 50)
                    queryParams.Add($"page_size={pageSize}");
                
                if (memoryType.HasValue)
                    queryParams.Add($"memory_type={memoryType.Value}");
                
                if (importance.HasValue)
                    queryParams.Add($"importance={importance.Value}");
                
                var queryString = queryParams.Count > 0 ? "?" + string.Join("&", queryParams) : "";
                var response = await GetAsync<NpcMemoryResponse>($"{BaseEndpoint}/npcs/{npcId}/memories{queryString}");
                return response ?? new NpcMemoryResponse();
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get memories for NPC {npcId}: {ex.Message}");
                throw;
            }
        }
        
        /// <summary>
        /// Add a memory to an NPC
        /// </summary>
        public async Task<NpcMemoryModel> AddNpcMemoryAsync(string npcId, AddNpcMemoryRequest request)
        {
            try
            {
                var response = await PostAsync<NpcMemoryModel>($"{BaseEndpoint}/npcs/{npcId}/memories", request);
                return response;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to add memory to NPC {npcId}: {ex.Message}");
                throw;
            }
        }
        
        /// <summary>
        /// Update an NPC memory
        /// </summary>
        public async Task<NpcMemoryModel> UpdateNpcMemoryAsync(string npcId, string memoryId, AddNpcMemoryRequest request)
        {
            try
            {
                var response = await PutAsync<NpcMemoryModel>($"{BaseEndpoint}/npcs/{npcId}/memories/{memoryId}", request);
                return response;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to update memory {memoryId} for NPC {npcId}: {ex.Message}");
                throw;
            }
        }
        
        /// <summary>
        /// Delete an NPC memory
        /// </summary>
        public async Task<bool> DeleteNpcMemoryAsync(string npcId, string memoryId)
        {
            try
            {
                await DeleteAsync($"{BaseEndpoint}/npcs/{npcId}/memories/{memoryId}");
                return true;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to delete memory {memoryId} for NPC {npcId}: {ex.Message}");
                return false;
            }
        }
        
        /// <summary>
        /// Search NPC memories by content
        /// </summary>
        public async Task<List<NpcMemoryModel>> SearchNpcMemoriesAsync(string npcId, string query, MemoryType? memoryType = null)
        {
            try
            {
                var queryParams = new List<string>();
                queryParams.Add($"q={Uri.EscapeDataString(query)}");
                
                if (memoryType.HasValue)
                    queryParams.Add($"memory_type={memoryType.Value}");
                
                var queryString = "?" + string.Join("&", queryParams);
                var response = await GetAsync<List<NpcMemoryModel>>($"{BaseEndpoint}/npcs/{npcId}/memories/search{queryString}");
                return response ?? new List<NpcMemoryModel>();
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to search memories for NPC {npcId}: {ex.Message}");
                throw;
            }
        }
        
        /// <summary>
        /// Get memories related to a specific character
        /// </summary>
        public async Task<List<NpcMemoryModel>> GetMemoriesAboutCharacterAsync(string npcId, string characterId)
        {
            try
            {
                var response = await GetAsync<List<NpcMemoryModel>>($"{BaseEndpoint}/npcs/{npcId}/memories/character/{characterId}");
                return response ?? new List<NpcMemoryModel>();
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get memories about character {characterId} for NPC {npcId}: {ex.Message}");
                throw;
            }
        }
        
        /// <summary>
        /// Decay old memories based on importance and access patterns
        /// </summary>
        public async Task<bool> DecayNpcMemoriesAsync(string npcId, float decayFactor = 0.1f)
        {
            try
            {
                var request = new { decay_factor = decayFactor };
                await PostAsync($"{BaseEndpoint}/npcs/{npcId}/memories/decay", request);
                return true;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to decay memories for NPC {npcId}: {ex.Message}");
                return false;
            }
        }
        
        #endregion
        
        #region Rumor System
        
        /// <summary>
        /// Add a rumor to an NPC's knowledge
        /// </summary>
        public async Task<bool> AddNpcRumorAsync(string npcId, AddNpcRumorRequest request)
        {
            try
            {
                await PostAsync($"{BaseEndpoint}/npcs/{npcId}/rumors", request);
                return true;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to add rumor to NPC {npcId}: {ex.Message}");
                return false;
            }
        }
        
        /// <summary>
        /// Get all rumors known by an NPC
        /// </summary>
        public async Task<List<Dictionary<string, object>>> GetNpcRumorsAsync(string npcId)
        {
            try
            {
                var response = await GetAsync<List<Dictionary<string, object>>>($"{BaseEndpoint}/npcs/{npcId}/rumors");
                return response ?? new List<Dictionary<string, object>>();
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get rumors for NPC {npcId}: {ex.Message}");
                throw;
            }
        }
        
        /// <summary>
        /// Spread rumors between NPCs
        /// </summary>
        public async Task<bool> SpreadRumorAsync(string fromNpcId, string toNpcId, string rumorId)
        {
            try
            {
                var request = new
                {
                    from_npc_id = fromNpcId,
                    to_npc_id = toNpcId,
                    rumor_id = rumorId
                };
                
                await PostAsync($"{BaseEndpoint}/rumors/spread", request);
                return true;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to spread rumor from {fromNpcId} to {toNpcId}: {ex.Message}");
                return false;
            }
        }
        
        #endregion
        
        #region Relationships
        
        /// <summary>
        /// Get all relationships for an NPC
        /// </summary>
        public async Task<Dictionary<string, float>> GetNpcRelationshipsAsync(string npcId)
        {
            try
            {
                var response = await GetAsync<Dictionary<string, float>>($"{BaseEndpoint}/npcs/{npcId}/relationships");
                return response ?? new Dictionary<string, float>();
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get relationships for NPC {npcId}: {ex.Message}");
                throw;
            }
        }
        
        /// <summary>
        /// Update relationship between two NPCs
        /// </summary>
        public async Task<bool> UpdateNpcRelationshipAsync(string npcId, string targetId, float newLevel)
        {
            try
            {
                var request = new
                {
                    target_id = targetId,
                    relationship_level = newLevel
                };
                
                await PutAsync($"{BaseEndpoint}/npcs/{npcId}/relationships/{targetId}", request);
                return true;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to update relationship between {npcId} and {targetId}: {ex.Message}");
                return false;
            }
        }
        
        /// <summary>
        /// Modify relationship by a delta amount
        /// </summary>
        public async Task<float> ModifyNpcRelationshipAsync(string npcId, string targetId, float change)
        {
            try
            {
                var request = new
                {
                    target_id = targetId,
                    relationship_change = change
                };
                
                var response = await PostAsync<Dictionary<string, object>>($"{BaseEndpoint}/npcs/{npcId}/relationships/{targetId}/modify", request);
                if (response != null && response.TryGetValue("new_level", out var newLevel))
                {
                    return Convert.ToSingle(newLevel);
                }
                return 0f;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to modify relationship between {npcId} and {targetId}: {ex.Message}");
                return 0f;
            }
        }
        
        /// <summary>
        /// Get relationship level between two NPCs
        /// </summary>
        public async Task<float> GetRelationshipLevelAsync(string npcId, string targetId)
        {
            try
            {
                var response = await GetAsync<Dictionary<string, object>>($"{BaseEndpoint}/npcs/{npcId}/relationships/{targetId}");
                if (response != null && response.TryGetValue("relationship_level", out var level))
                {
                    return Convert.ToSingle(level);
                }
                return 0f;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get relationship level between {npcId} and {targetId}: {ex.Message}");
                return 0f;
            }
        }
        
        #endregion
        
        #region Behavior and AI
        
        /// <summary>
        /// Update NPC behavior configuration
        /// </summary>
        public async Task<bool> UpdateNpcBehaviorAsync(string npcId, NpcBehaviorModel behavior)
        {
            try
            {
                await PutAsync($"{BaseEndpoint}/npcs/{npcId}/behavior", behavior);
                return true;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to update behavior for NPC {npcId}: {ex.Message}");
                return false;
            }
        }
        
        /// <summary>
        /// Get current NPC behavior state
        /// </summary>
        public async Task<Dictionary<string, object>> GetNpcBehaviorStateAsync(string npcId)
        {
            try
            {
                var response = await GetAsync<Dictionary<string, object>>($"{BaseEndpoint}/npcs/{npcId}/behavior/state");
                return response ?? new Dictionary<string, object>();
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get behavior state for NPC {npcId}: {ex.Message}");
                throw;
            }
        }
        
        /// <summary>
        /// Trigger a behavior change for an NPC
        /// </summary>
        public async Task<bool> TriggerBehaviorChangeAsync(string npcId, string trigger, Dictionary<string, object> context = null)
        {
            try
            {
                var request = new
                {
                    trigger = trigger,
                    context = context ?? new Dictionary<string, object>()
                };
                
                await PostAsync($"{BaseEndpoint}/npcs/{npcId}/behavior/trigger", request);
                return true;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to trigger behavior change for NPC {npcId}: {ex.Message}");
                return false;
            }
        }
        
        /// <summary>
        /// Get AI decision factors for an NPC
        /// </summary>
        public async Task<Dictionary<string, float>> GetDecisionFactorsAsync(string npcId)
        {
            try
            {
                var response = await GetAsync<Dictionary<string, float>>($"{BaseEndpoint}/npcs/{npcId}/ai/decision-factors");
                return response ?? new Dictionary<string, float>();
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get decision factors for NPC {npcId}: {ex.Message}");
                throw;
            }
        }
        
        /// <summary>
        /// Update AI decision factors for an NPC
        /// </summary>
        public async Task<bool> UpdateDecisionFactorsAsync(string npcId, Dictionary<string, float> factors)
        {
            try
            {
                await PutAsync($"{BaseEndpoint}/npcs/{npcId}/ai/decision-factors", factors);
                return true;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to update decision factors for NPC {npcId}: {ex.Message}");
                return false;
            }
        }
        
        #endregion
        
        #region Location and Movement
        
        /// <summary>
        /// Update NPC location
        /// </summary>
        public async Task<bool> UpdateNpcLocationAsync(string npcId, NpcLocationModel location)
        {
            try
            {
                await PutAsync($"{BaseEndpoint}/npcs/{npcId}/location", location);
                return true;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to update location for NPC {npcId}: {ex.Message}");
                return false;
            }
        }
        
        /// <summary>
        /// Get NPCs in a specific region
        /// </summary>
        public async Task<List<NpcModel>> GetNpcsInRegionAsync(string regionId, bool activeOnly = true)
        {
            try
            {
                var queryString = activeOnly ? "?active_only=true" : "";
                var response = await GetAsync<List<NpcModel>>($"{BaseEndpoint}/npcs/region/{regionId}{queryString}");
                return response ?? new List<NpcModel>();
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get NPCs in region {regionId}: {ex.Message}");
                throw;
            }
        }
        
        /// <summary>
        /// Get NPCs near a position within a radius
        /// </summary>
        public async Task<List<NpcModel>> GetNearbyNpcsAsync(Vector3 position, float radius, bool activeOnly = true)
        {
            try
            {
                var request = new
                {
                    position = new { x = position.x, y = position.y, z = position.z },
                    radius = radius,
                    active_only = activeOnly
                };
                
                var response = await PostAsync<List<NpcModel>>($"{BaseEndpoint}/npcs/nearby", request);
                return response ?? new List<NpcModel>();
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get nearby NPCs: {ex.Message}");
                throw;
            }
        }
        
        /// <summary>
        /// Move NPC to a new position
        /// </summary>
        public async Task<bool> MoveNpcAsync(string npcId, Vector3 newPosition, bool updateHistory = true)
        {
            try
            {
                var request = new
                {
                    position = new { x = newPosition.x, y = newPosition.y, z = newPosition.z },
                    update_history = updateHistory
                };
                
                await PostAsync($"{BaseEndpoint}/npcs/{npcId}/move", request);
                return true;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to move NPC {npcId}: {ex.Message}");
                return false;
            }
        }
        
        #endregion
        
        #region Analytics and Statistics
        
        /// <summary>
        /// Get analytics for an NPC
        /// </summary>
        public async Task<NpcAnalyticsModel> GetNpcAnalyticsAsync(string npcId)
        {
            try
            {
                var response = await GetAsync<NpcAnalyticsModel>($"{BaseEndpoint}/npcs/{npcId}/analytics");
                return response;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get analytics for NPC {npcId}: {ex.Message}");
                throw;
            }
        }
        
        /// <summary>
        /// Get aggregate analytics for multiple NPCs
        /// </summary>
        public async Task<Dictionary<string, object>> GetNpcPopulationAnalyticsAsync(string regionId = null, List<string> tags = null)
        {
            try
            {
                var queryParams = new List<string>();
                
                if (!string.IsNullOrEmpty(regionId))
                    queryParams.Add($"region_id={regionId}");
                
                if (tags != null && tags.Count > 0)
                    queryParams.Add($"tags={string.Join(",", tags)}");
                
                var queryString = queryParams.Count > 0 ? "?" + string.Join("&", queryParams) : "";
                var response = await GetAsync<Dictionary<string, object>>($"{BaseEndpoint}/analytics/population{queryString}");
                return response ?? new Dictionary<string, object>();
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get population analytics: {ex.Message}");
                throw;
            }
        }
        
        #endregion
        
        #region Search and Filtering
        
        /// <summary>
        /// Search NPCs by various criteria
        /// </summary>
        public async Task<List<NpcModel>> SearchNpcsAsync(string query, List<string> tags = null, string regionId = null, BehaviorType? behaviorType = null)
        {
            try
            {
                var queryParams = new List<string>();
                
                if (!string.IsNullOrEmpty(query))
                    queryParams.Add($"q={Uri.EscapeDataString(query)}");
                
                if (tags != null && tags.Count > 0)
                    queryParams.Add($"tags={string.Join(",", tags)}");
                
                if (!string.IsNullOrEmpty(regionId))
                    queryParams.Add($"region_id={regionId}");
                
                if (behaviorType.HasValue)
                    queryParams.Add($"behavior_type={behaviorType.Value}");
                
                var queryString = queryParams.Count > 0 ? "?" + string.Join("&", queryParams) : "";
                var response = await GetAsync<List<NpcModel>>($"{BaseEndpoint}/npcs/search{queryString}");
                return response ?? new List<NpcModel>();
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to search NPCs: {ex.Message}");
                throw;
            }
        }
        
        /// <summary>
        /// Get NPCs by personality traits
        /// </summary>
        public async Task<List<NpcModel>> GetNpcsByTraitsAsync(List<PersonalityTrait> traits, bool matchAll = false)
        {
            try
            {
                var request = new
                {
                    traits = traits.ConvertAll(t => t.ToString()),
                    match_all = matchAll
                };
                
                var response = await PostAsync<List<NpcModel>>($"{BaseEndpoint}/npcs/search/traits", request);
                return response ?? new List<NpcModel>();
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to search NPCs by traits: {ex.Message}");
                throw;
            }
        }
        
        /// <summary>
        /// Get NPCs with specific skills
        /// </summary>
        public async Task<List<NpcModel>> GetNpcsBySkillsAsync(Dictionary<string, int> requiredSkills, bool requireAll = false)
        {
            try
            {
                var request = new
                {
                    required_skills = requiredSkills,
                    require_all = requireAll
                };
                
                var response = await PostAsync<List<NpcModel>>($"{BaseEndpoint}/npcs/search/skills", request);
                return response ?? new List<NpcModel>();
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to search NPCs by skills: {ex.Message}");
                throw;
            }
        }
        
        #endregion
    }
} 