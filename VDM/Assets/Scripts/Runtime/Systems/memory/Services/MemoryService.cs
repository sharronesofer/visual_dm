using System.Collections.Generic;
using System.Threading.Tasks;
using System;
using UnityEngine;
using VDM.Infrastructure.Services;
using VDM.DTOs.Common;
using VDM.DTOs.Social.Memory;


namespace VDM.Systems.Memory.Services
{
    /// <summary>
    /// Service for memory-related HTTP API operations
    /// </summary>
    public class MemoryService : BaseHttpService
    {
        private const string BASE_ENDPOINT = "/api/memory";

        /// <summary>
        /// Get memories for an NPC with optional filters
        /// </summary>
        public async Task<MemoriesResponseDTO> GetNpcMemoriesAsync(string npcId, int limit = 10, int offset = 0, List<string> tags = null)
        {
            try
            {
                var queryParams = new List<string>();
                
                if (limit != 10)
                    queryParams.Add($"limit={limit}");
                
                if (offset > 0)
                    queryParams.Add($"offset={offset}");
                    
                if (tags != null && tags.Count > 0)
                    queryParams.Add($"tags={string.Join(",", tags)}");

                var queryString = queryParams.Count > 0 ? "?" + string.Join("&", queryParams) : "";
                var response = await GetAsync<MemoriesResponseDTO>($"{BASE_ENDPOINT}/{npcId}/memories{queryString}");
                return response ?? new MemoriesResponseDTO();
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error getting NPC memories: {ex.Message}");
                return new MemoriesResponseDTO();
            }
        }

        /// <summary>
        /// Create a new memory for an NPC
        /// </summary>
        public async Task<MemoryResponseDTO> CreateMemoryAsync(string npcId, CreateMemoryRequestDTO request)
        {
            try
            {
                var response = await PostAsync<CreateMemoryRequestDTO, MemoryResponseDTO>($"{BASE_ENDPOINT}/{npcId}/memories", request);
                return response ?? new MemoryResponseDTO();
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error creating memory: {ex.Message}");
                return new MemoryResponseDTO { Success = false, Message = ex.Message };
            }
        }

        /// <summary>
        /// Recall memories based on a query
        /// </summary>
        public async Task<MemoriesResponseDTO> RecallMemoriesAsync(string npcId, RecallMemoryRequestDTO request)
        {
            try
            {
                var response = await PostAsync<RecallMemoryRequestDTO, MemoriesResponseDTO>($"{BASE_ENDPOINT}/{npcId}/recall", request);
                return response ?? new MemoriesResponseDTO();
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error recalling memories: {ex.Message}");
                return new MemoriesResponseDTO();
            }
        }

        /// <summary>
        /// Recall a specific memory by ID
        /// </summary>
        public async Task<MemoryResponseDTO> RecallMemoryAsync(string npcId, string memoryId, RecallMemoryRequestDTO request = null)
        {
            try
            {
                if (request == null)
                    request = new RecallMemoryRequestDTO();

                var response = await PostAsync<RecallMemoryRequestDTO, MemoryResponseDTO>($"{BASE_ENDPOINT}/{npcId}/memories/{memoryId}/recall", request);
                return response ?? new MemoryResponseDTO { Success = false, Message = "Failed to recall memory" };
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error recalling memory: {ex.Message}");
                return new MemoryResponseDTO { Success = false, Message = ex.Message };
            }
        }

        /// <summary>
        /// Reinforce a memory (increase importance/accessibility)
        /// </summary>
        public async Task<MemoryResponseDTO> ReinforceMemoryAsync(string npcId, string memoryId, ReinforceMemoryRequestDTO request = null)
        {
            try
            {
                if (request == null)
                    request = new ReinforceMemoryRequestDTO();

                var response = await PostAsync<ReinforceMemoryRequestDTO, MemoryResponseDTO>($"{BASE_ENDPOINT}/{npcId}/memories/{memoryId}/reinforce", request);
                return response ?? new MemoryResponseDTO { Success = false, Message = "Failed to reinforce memory" };
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error reinforcing memory: {ex.Message}");
                return new MemoryResponseDTO { Success = false, Message = ex.Message };
            }
        }

        /// <summary>
        /// Make an NPC forget a memory
        /// </summary>
        public async Task<MemoryResponseDTO> ForgetMemoryAsync(string npcId, string memoryId, ForgetMemoryRequestDTO request = null)
        {
            try
            {
                await DeleteAsync($"{BASE_ENDPOINT}/{npcId}/memories/{memoryId}");
                return new MemoryResponseDTO 
                { 
                    Success = true, 
                    Message = "Memory forgotten successfully",
                    MemoryId = memoryId
                };
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error forgetting memory: {ex.Message}");
                return new MemoryResponseDTO { Success = false, Message = ex.Message };
            }
        }

        /// <summary>
        /// Get memory summary for an NPC
        /// </summary>
        public async Task<MemorySummaryResponseDTO> GetMemorySummaryAsync(string npcId)
        {
            try
            {
                var response = await GetAsync<MemorySummaryResponseDTO>($"/api/npc/memories/{npcId}/summary");
                return response ?? new MemorySummaryResponseDTO();
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error getting memory summary: {ex.Message}");
                return new MemorySummaryResponseDTO();
            }
        }

        /// <summary>
        /// Get memories filtered by tags
        /// </summary>
        public async Task<MemoriesResponseDTO> GetMemoriesByTagsAsync(string npcId, List<string> tags, int limit = 10, int offset = 0)
        {
            return await GetNpcMemoriesAsync(npcId, limit, offset, tags);
        }

        /// <summary>
        /// Get memories related to specific entities
        /// </summary>
        public async Task<List<MemoryDTO>> GetMemoriesRelatedToEntityAsync(string npcId, string entityId)
        {
            try
            {
                var memoriesResponse = await GetNpcMemoriesAsync(npcId, 100, 0);
                
                if (memoriesResponse?.Memories != null)
                {
                    var relatedMemories = memoriesResponse.Memories.FindAll(m => m.IsRelatedTo(entityId));
                    return relatedMemories;
                }

                return new List<MemoryDTO>();
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error getting memories related to entity: {ex.Message}");
                return new List<MemoryDTO>();
            }
        }

        /// <summary>
        /// Check if an NPC has any memories containing specific content
        /// </summary>
        public async Task<bool> HasMemoryContainingAsync(string npcId, string searchContent)
        {
            try
            {
                var memoriesResponse = await GetNpcMemoriesAsync(npcId, 100, 0);
                
                if (memoriesResponse?.Memories != null)
                {
                    return memoriesResponse.Memories.Exists(m => 
                        m.Content.Contains(searchContent, StringComparison.OrdinalIgnoreCase));
                }

                return false;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error checking for memory content: {ex.Message}");
                return false;
            }
        }
    }

    /// <summary>
    /// Temporary memory summary DTO for compatibility
    /// </summary>
    [System.Serializable]
    public class MemorySummaryDTO
    {
        public string EntityId { get; set; }
        public int TotalMemories { get; set; }
        public int ImportantMemories { get; set; }
        public float AverageImportance { get; set; }
        public string MostRecentMemory { get; set; }
        public List<string> CommonTags { get; set; } = new List<string>();
    }

    /// <summary>
    /// Temporary memory summary response DTO for compatibility
    /// </summary>
    [System.Serializable]
    public class MemorySummaryResponseDTO : SuccessResponseDTO
    {
        public MemorySummaryDTO Data { get; set; }
    }
} 