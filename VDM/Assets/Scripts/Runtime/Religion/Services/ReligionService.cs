using System.Collections.Generic;
using System.Threading.Tasks;
using System;
using UnityEngine;
using VDM.Runtime.Core.Models;
using VDM.Runtime.Religion.Models;
using VDM.Runtime.Services.Http;


namespace VDM.Runtime.Religion.Services
{
    /// <summary>
    /// Service for managing religion-related HTTP API operations
    /// </summary>
    public class ReligionService : BaseHttpService
    {
        private const string BASE_ENDPOINT = "/api/religion";

        public ReligionService(IHttpClient httpClient) : base(httpClient)
        {
        }

        /// <summary>
        /// Get all religions
        /// </summary>
        public async Task<APIResponse<List<ReligionDTO>>> GetReligionsAsync()
        {
            try
            {
                var response = await _httpClient.GetAsync<ReligionListResponseDTO>($"{BASE_ENDPOINT}/");
                
                if (response.Success && response.Data != null)
                {
                    return new APIResponse<List<ReligionDTO>>
                    {
                        Success = true,
                        Data = response.Data.Religions,
                        Message = response.Data.Message
                    };
                }

                return new APIResponse<List<ReligionDTO>>
                {
                    Success = false,
                    Message = response.Message,
                    Errors = response.Errors
                };
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error getting religions: {ex.Message}");
                return new APIResponse<List<ReligionDTO>>
                {
                    Success = false,
                    Message = "Failed to get religions",
                    Errors = new List<string> { ex.Message }
                };
            }
        }

        /// <summary>
        /// Get a specific religion by ID
        /// </summary>
        public async Task<APIResponse<ReligionDTO>> GetReligionAsync(string religionId)
        {
            try
            {
                var response = await _httpClient.GetAsync<ReligionResponseDTO>($"{BASE_ENDPOINT}/{religionId}");
                
                if (response.Success && response.Data != null)
                {
                    return new APIResponse<ReligionDTO>
                    {
                        Success = true,
                        Data = response.Data.Religion,
                        Message = response.Data.Message
                    };
                }

                return new APIResponse<ReligionDTO>
                {
                    Success = false,
                    Message = response.Message,
                    Errors = response.Errors
                };
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error getting religion {religionId}: {ex.Message}");
                return new APIResponse<ReligionDTO>
                {
                    Success = false,
                    Message = "Failed to get religion",
                    Errors = new List<string> { ex.Message }
                };
            }
        }

        /// <summary>
        /// Create a new religion
        /// </summary>
        public async Task<APIResponse<ReligionDTO>> CreateReligionAsync(CreateReligionRequestDTO request)
        {
            try
            {
                var response = await _httpClient.PostAsync<ReligionResponseDTO>($"{BASE_ENDPOINT}/", request);
                
                if (response.Success && response.Data != null)
                {
                    return new APIResponse<ReligionDTO>
                    {
                        Success = true,
                        Data = response.Data.Religion,
                        Message = response.Data.Message
                    };
                }

                return new APIResponse<ReligionDTO>
                {
                    Success = false,
                    Message = response.Message,
                    Errors = response.Errors
                };
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error creating religion: {ex.Message}");
                return new APIResponse<ReligionDTO>
                {
                    Success = false,
                    Message = "Failed to create religion",
                    Errors = new List<string> { ex.Message }
                };
            }
        }

        /// <summary>
        /// Update an existing religion
        /// </summary>
        public async Task<APIResponse<ReligionDTO>> UpdateReligionAsync(string religionId, UpdateReligionRequestDTO request)
        {
            try
            {
                var response = await _httpClient.PutAsync<ReligionResponseDTO>($"{BASE_ENDPOINT}/{religionId}", request);
                
                if (response.Success && response.Data != null)
                {
                    return new APIResponse<ReligionDTO>
                    {
                        Success = true,
                        Data = response.Data.Religion,
                        Message = response.Data.Message
                    };
                }

                return new APIResponse<ReligionDTO>
                {
                    Success = false,
                    Message = response.Message,
                    Errors = response.Errors
                };
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error updating religion {religionId}: {ex.Message}");
                return new APIResponse<ReligionDTO>
                {
                    Success = false,
                    Message = "Failed to update religion",
                    Errors = new List<string> { ex.Message }
                };
            }
        }

        /// <summary>
        /// Delete a religion
        /// </summary>
        public async Task<APIResponse<bool>> DeleteReligionAsync(string religionId)
        {
            try
            {
                var response = await _httpClient.DeleteAsync($"{BASE_ENDPOINT}/{religionId}");
                
                return new APIResponse<bool>
                {
                    Success = response.Success,
                    Data = response.Success,
                    Message = response.Message,
                    Errors = response.Errors
                };
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error deleting religion {religionId}: {ex.Message}");
                return new APIResponse<bool>
                {
                    Success = false,
                    Data = false,
                    Message = "Failed to delete religion",
                    Errors = new List<string> { ex.Message }
                };
            }
        }

        /// <summary>
        /// Get religions by region
        /// </summary>
        public async Task<APIResponse<List<ReligionDTO>>> GetReligionsByRegionAsync(string regionId)
        {
            try
            {
                var response = await _httpClient.GetAsync<ReligionListResponseDTO>($"{BASE_ENDPOINT}/region/{regionId}");
                
                if (response.Success && response.Data != null)
                {
                    return new APIResponse<List<ReligionDTO>>
                    {
                        Success = true,
                        Data = response.Data.Religions,
                        Message = response.Data.Message
                    };
                }

                return new APIResponse<List<ReligionDTO>>
                {
                    Success = false,
                    Message = response.Message,
                    Errors = response.Errors
                };
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error getting religions for region {regionId}: {ex.Message}");
                return new APIResponse<List<ReligionDTO>>
                {
                    Success = false,
                    Message = "Failed to get religions for region",
                    Errors = new List<string> { ex.Message }
                };
            }
        }

        /// <summary>
        /// Get religions by faction
        /// </summary>
        public async Task<APIResponse<List<ReligionDTO>>> GetReligionsByFactionAsync(string factionId)
        {
            try
            {
                var response = await _httpClient.GetAsync<ReligionListResponseDTO>($"{BASE_ENDPOINT}/faction/{factionId}");
                
                if (response.Success && response.Data != null)
                {
                    return new APIResponse<List<ReligionDTO>>
                    {
                        Success = true,
                        Data = response.Data.Religions,
                        Message = response.Data.Message
                    };
                }

                return new APIResponse<List<ReligionDTO>>
                {
                    Success = false,
                    Message = response.Message,
                    Errors = response.Errors
                };
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error getting religions for faction {factionId}: {ex.Message}");
                return new APIResponse<List<ReligionDTO>>
                {
                    Success = false,
                    Message = "Failed to get religions for faction",
                    Errors = new List<string> { ex.Message }
                };
            }
        }

        /// <summary>
        /// Get religion membership for an entity
        /// </summary>
        public async Task<APIResponse<List<ReligionMembershipDTO>>> GetEntityMembershipsAsync(string entityId)
        {
            try
            {
                var response = await _httpClient.GetAsync<List<ReligionMembershipDTO>>($"{BASE_ENDPOINT}/membership/entity/{entityId}");
                
                return new APIResponse<List<ReligionMembershipDTO>>
                {
                    Success = response.Success,
                    Data = response.Data ?? new List<ReligionMembershipDTO>(),
                    Message = response.Message,
                    Errors = response.Errors
                };
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error getting memberships for entity {entityId}: {ex.Message}");
                return new APIResponse<List<ReligionMembershipDTO>>
                {
                    Success = false,
                    Message = "Failed to get entity memberships",
                    Errors = new List<string> { ex.Message }
                };
            }
        }

        /// <summary>
        /// Join a religion
        /// </summary>
        public async Task<APIResponse<ReligionMembershipDTO>> JoinReligionAsync(string entityId, string religionId, float devotionLevel = 0.5f)
        {
            try
            {
                var request = new
                {
                    entity_id = entityId,
                    religion_id = religionId,
                    devotion_level = devotionLevel
                };

                var response = await _httpClient.PostAsync<ReligionMembershipDTO>($"{BASE_ENDPOINT}/membership/join", request);
                
                return new APIResponse<ReligionMembershipDTO>
                {
                    Success = response.Success,
                    Data = response.Data,
                    Message = response.Message,
                    Errors = response.Errors
                };
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error joining religion: {ex.Message}");
                return new APIResponse<ReligionMembershipDTO>
                {
                    Success = false,
                    Message = "Failed to join religion",
                    Errors = new List<string> { ex.Message }
                };
            }
        }

        /// <summary>
        /// Leave a religion
        /// </summary>
        public async Task<APIResponse<bool>> LeaveReligionAsync(string entityId, string religionId)
        {
            try
            {
                var response = await _httpClient.DeleteAsync($"{BASE_ENDPOINT}/membership/{entityId}/{religionId}");
                
                return new APIResponse<bool>
                {
                    Success = response.Success,
                    Data = response.Success,
                    Message = response.Message,
                    Errors = response.Errors
                };
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error leaving religion: {ex.Message}");
                return new APIResponse<bool>
                {
                    Success = false,
                    Data = false,
                    Message = "Failed to leave religion",
                    Errors = new List<string> { ex.Message }
                };
            }
        }
    }
} 