using System.Collections.Generic;
using System.Threading.Tasks;
using System;
using UnityEngine;
using VDM.Runtime.Core.Models;
using VDM.Runtime.Memory.Models;
using VDM.Runtime.Services.Http;


namespace VDM.Runtime.Memory.Services
{
    /// <summary>
    /// Service for managing memory-related HTTP API operations
    /// </summary>
    public class MemoryService : BaseHttpService
    {
        private const string BASE_ENDPOINT = "/api/npc";

        public MemoryService(IHttpClient httpClient) : base(httpClient)
        {
        }

        /// <summary>
        /// Get memories for a specific NPC
        /// </summary>
        public async Task<APIResponse<MemoryListResponseDTO>> GetNpcMemoriesAsync(
            string npcId, 
            int limit = 10, 
            int offset = 0, 
            List<string> tags = null)
        {
            try
            {
                var queryParams = new List<string>
                {
                    $"limit={limit}",
                    $"offset={offset}"
                };

                if (tags != null && tags.Count > 0)
                {
                    foreach (var tag in tags)
                    {
                        queryParams.Add($"tags={tag}");
                    }
                }

                var queryString = string.Join("&", queryParams);
                var endpoint = $"{BASE_ENDPOINT}/{npcId}/memories?{queryString}";

                var response = await _httpClient.GetAsync<List<MemoryDTO>>(endpoint);
                
                if (response.Success && response.Data != null)
                {
                    return new APIResponse<MemoryListResponseDTO>
                    {
                        Success = true,
                        Data = new MemoryListResponseDTO
                        {
                            Success = true,
                            NpcId = npcId,
                            Memories = response.Data,
                            TotalCount = response.Data.Count,
                            Limit = limit,
                            Offset = offset,
                            Message = "Memories retrieved successfully"
                        }
                    };
                }

                return new APIResponse<MemoryListResponseDTO>
                {
                    Success = false,
                    Message = response.Message,
                    Errors = response.Errors
                };
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error getting NPC memories: {ex.Message}");
                return new APIResponse<MemoryListResponseDTO>
                {
                    Success = false,
                    Message = $"Failed to get NPC memories: {ex.Message}"
                };
            }
        }

        /// <summary>
        /// Add a memory to an NPC
        /// </summary>
        public async Task<APIResponse<MemoryResponseDTO>> AddMemoryToNpcAsync(string npcId, CreateMemoryRequestDTO request)
        {
            try
            {
                var endpoint = $"{BASE_ENDPOINT}/{npcId}/memories";
                var response = await _httpClient.PostAsync<CreateMemoryRequestDTO, MemoryResponseDTO>(endpoint, request);
                
                if (response.Success && response.Data != null)
                {
                    return new APIResponse<MemoryResponseDTO>
                    {
                        Success = true,
                        Data = response.Data,
                        Message = response.Data.Message
                    };
                }

                return new APIResponse<MemoryResponseDTO>
                {
                    Success = false,
                    Message = response.Message,
                    Errors = response.Errors
                };
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error adding memory to NPC: {ex.Message}");
                return new APIResponse<MemoryResponseDTO>
                {
                    Success = false,
                    Message = $"Failed to add memory: {ex.Message}"
                };
            }
        }

        /// <summary>
        /// Recall a specific memory for an NPC
        /// </summary>
        public async Task<APIResponse<MemoryResponseDTO>> RecallMemoryAsync(string npcId, string memoryId, RecallMemoryRequestDTO request = null)
        {
            try
            {
                var endpoint = $"{BASE_ENDPOINT}/{npcId}/memories/{memoryId}/recall";
                
                if (request == null)
                {
                    request = new RecallMemoryRequestDTO();
                }

                var response = await _httpClient.PostAsync<RecallMemoryRequestDTO, MemoryResponseDTO>(endpoint, request);
                
                if (response.Success && response.Data != null)
                {
                    return new APIResponse<MemoryResponseDTO>
                    {
                        Success = true,
                        Data = response.Data,
                        Message = response.Data.Message
                    };
                }

                return new APIResponse<MemoryResponseDTO>
                {
                    Success = false,
                    Message = response.Message,
                    Errors = response.Errors
                };
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error recalling memory: {ex.Message}");
                return new APIResponse<MemoryResponseDTO>
                {
                    Success = false,
                    Message = $"Failed to recall memory: {ex.Message}"
                };
            }
        }

        /// <summary>
        /// Reinforce a memory for an NPC
        /// </summary>
        public async Task<APIResponse<MemoryResponseDTO>> ReinforceMemoryAsync(string npcId, string memoryId, ReinforceMemoryRequestDTO request)
        {
            try
            {
                var endpoint = $"{BASE_ENDPOINT}/{npcId}/memories/{memoryId}/reinforce";
                var response = await _httpClient.PostAsync<ReinforceMemoryRequestDTO, MemoryResponseDTO>(endpoint, request);
                
                if (response.Success && response.Data != null)
                {
                    return new APIResponse<MemoryResponseDTO>
                    {
                        Success = true,
                        Data = response.Data,
                        Message = response.Data.Message
                    };
                }

                return new APIResponse<MemoryResponseDTO>
                {
                    Success = false,
                    Message = response.Message,
                    Errors = response.Errors
                };
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error reinforcing memory: {ex.Message}");
                return new APIResponse<MemoryResponseDTO>
                {
                    Success = false,
                    Message = $"Failed to reinforce memory: {ex.Message}"
                };
            }
        }

        /// <summary>
        /// Make an NPC forget a memory
        /// </summary>
        public async Task<APIResponse<MemoryResponseDTO>> ForgetMemoryAsync(string npcId, string memoryId, ForgetMemoryRequestDTO request = null)
        {
            try
            {
                var endpoint = $"{BASE_ENDPOINT}/{npcId}/memories/{memoryId}";
                
                if (request == null)
                {
                    request = new ForgetMemoryRequestDTO();
                }

                var response = await _httpClient.DeleteAsync<MemoryResponseDTO>(endpoint);
                
                if (response.Success)
                {
                    return new APIResponse<MemoryResponseDTO>
                    {
                        Success = true,
                        Data = new MemoryResponseDTO
                        {
                            Success = true,
                            Message = "Memory forgotten successfully",
                            MemoryId = memoryId
                        }
                    };
                }

                return new APIResponse<MemoryResponseDTO>
                {
                    Success = false,
                    Message = response.Message,
                    Errors = response.Errors
                };
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error forgetting memory: {ex.Message}");
                return new APIResponse<MemoryResponseDTO>
                {
                    Success = false,
                    Message = $"Failed to forget memory: {ex.Message}"
                };
            }
        }

        /// <summary>
        /// Get memory summary for an NPC
        /// </summary>
        public async Task<APIResponse<MemorySummaryResponseDTO>> GetMemorySummaryAsync(string npcId)
        {
            try
            {
                var endpoint = $"/api/npc/memories/{npcId}/summary";
                var response = await _httpClient.GetAsync<MemorySummaryResponseDTO>(endpoint);
                
                if (response.Success && response.Data != null)
                {
                    return new APIResponse<MemorySummaryResponseDTO>
                    {
                        Success = true,
                        Data = response.Data,
                        Message = response.Data.Message
                    };
                }

                return new APIResponse<MemorySummaryResponseDTO>
                {
                    Success = false,
                    Message = response.Message,
                    Errors = response.Errors
                };
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error getting memory summary: {ex.Message}");
                return new APIResponse<MemorySummaryResponseDTO>
                {
                    Success = false,
                    Message = $"Failed to get memory summary: {ex.Message}"
                };
            }
        }

        /// <summary>
        /// Get memories filtered by tags
        /// </summary>
        public async Task<APIResponse<MemoryListResponseDTO>> GetMemoriesByTagsAsync(string npcId, List<string> tags, int limit = 10, int offset = 0)
        {
            return await GetNpcMemoriesAsync(npcId, limit, offset, tags);
        }

        /// <summary>
        /// Get memories related to specific entities
        /// </summary>
        public async Task<APIResponse<List<MemoryDTO>>> GetMemoriesRelatedToEntityAsync(string npcId, string entityId)
        {
            try
            {
                var memoriesResponse = await GetNpcMemoriesAsync(npcId, 100, 0);
                
                if (memoriesResponse.Success && memoriesResponse.Data?.Memories != null)
                {
                    var relatedMemories = memoriesResponse.Data.Memories.FindAll(m => m.IsRelatedTo(entityId));
                    
                    return new APIResponse<List<MemoryDTO>>
                    {
                        Success = true,
                        Data = relatedMemories,
                        Message = $"Found {relatedMemories.Count} memories related to entity {entityId}"
                    };
                }

                return new APIResponse<List<MemoryDTO>>
                {
                    Success = false,
                    Message = memoriesResponse.Message
                };
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error getting memories related to entity: {ex.Message}");
                return new APIResponse<List<MemoryDTO>>
                {
                    Success = false,
                    Message = $"Failed to get related memories: {ex.Message}"
                };
            }
        }

        /// <summary>
        /// Check if an NPC has any memories containing specific content
        /// </summary>
        public async Task<APIResponse<bool>> HasMemoryContainingAsync(string npcId, string searchContent)
        {
            try
            {
                var memoriesResponse = await GetNpcMemoriesAsync(npcId, 100, 0);
                
                if (memoriesResponse.Success && memoriesResponse.Data?.Memories != null)
                {
                    var hasMemory = memoriesResponse.Data.Memories.Exists(m => 
                        m.Content.Contains(searchContent, StringComparison.OrdinalIgnoreCase));
                    
                    return new APIResponse<bool>
                    {
                        Success = true,
                        Data = hasMemory,
                        Message = hasMemory ? "Memory found" : "No matching memory found"
                    };
                }

                return new APIResponse<bool>
                {
                    Success = false,
                    Data = false,
                    Message = memoriesResponse.Message
                };
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error checking for memory content: {ex.Message}");
                return new APIResponse<bool>
                {
                    Success = false,
                    Data = false,
                    Message = $"Failed to check memory content: {ex.Message}"
                };
            }
        }
    }
} 