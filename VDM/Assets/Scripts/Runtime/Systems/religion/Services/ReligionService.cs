using System.Collections.Generic;
using System.Threading.Tasks;
using System;
using UnityEngine;
using VDM.Systems.Religion.Models;
using VDM.Infrastructure.Services;

namespace VDM.Systems.Religion.Services
{
    /// <summary>
    /// Service for managing religion-related HTTP API operations
    /// </summary>
    public class ReligionService : BaseHttpService
    {
        private const string BASE_ENDPOINT = "/api/religion";

        /// <summary>
        /// Get all religions
        /// </summary>
        public async Task<List<ReligionDTO>> GetReligionsAsync()
        {
            try
            {
                var response = await GetAsync<ReligionListResponseDTO>($"{BASE_ENDPOINT}/");
                return response?.Religions ?? new List<ReligionDTO>();
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error getting religions: {ex.Message}");
                return new List<ReligionDTO>();
            }
        }

        /// <summary>
        /// Get a specific religion by ID
        /// </summary>
        public async Task<ReligionDTO> GetReligionAsync(string religionId)
        {
            try
            {
                var response = await GetAsync<ReligionResponseDTO>($"{BASE_ENDPOINT}/{religionId}");
                return response?.Religion;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error getting religion {religionId}: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Create a new religion
        /// </summary>
        public async Task<ReligionDTO> CreateReligionAsync(CreateReligionRequestDTO request)
        {
            try
            {
                var response = await PostAsync<CreateReligionRequestDTO, ReligionResponseDTO>($"{BASE_ENDPOINT}/", request);
                return response?.Religion;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error creating religion: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Update an existing religion
        /// </summary>
        public async Task<ReligionDTO> UpdateReligionAsync(string religionId, UpdateReligionRequestDTO request)
        {
            try
            {
                var response = await PutAsync<UpdateReligionRequestDTO, ReligionResponseDTO>($"{BASE_ENDPOINT}/{religionId}", request);
                return response?.Religion;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error updating religion {religionId}: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Delete a religion
        /// </summary>
        public async Task<bool> DeleteReligionAsync(string religionId)
        {
            try
            {
                await DeleteAsync($"{BASE_ENDPOINT}/{religionId}");
                return true;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error deleting religion {religionId}: {ex.Message}");
                return false;
            }
        }

        /// <summary>
        /// Get religions by pantheon
        /// </summary>
        public async Task<List<ReligionDTO>> GetReligionsByPantheonAsync(string pantheonId)
        {
            try
            {
                var response = await GetAsync<ReligionListResponseDTO>($"{BASE_ENDPOINT}/pantheon/{pantheonId}");
                return response?.Religions ?? new List<ReligionDTO>();
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error getting religions for pantheon {pantheonId}: {ex.Message}");
                return new List<ReligionDTO>();
            }
        }

        /// <summary>
        /// Get religious practices for a religion
        /// </summary>
        public async Task<List<ReligiousPracticeDTO>> GetReligiousPracticesAsync(string religionId)
        {
            try
            {
                var response = await GetAsync<List<ReligiousPracticeDTO>>($"{BASE_ENDPOINT}/{religionId}/practices");
                return response ?? new List<ReligiousPracticeDTO>();
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error getting religious practices for religion {religionId}: {ex.Message}");
                return new List<ReligiousPracticeDTO>();
            }
        }

        /// <summary>
        /// Add religious practice to a religion
        /// </summary>
        public async Task<ReligiousPracticeDTO> AddReligiousPracticeAsync(string religionId, CreateReligiousPracticeRequestDTO request)
        {
            try
            {
                var response = await PostAsync<CreateReligiousPracticeRequestDTO, ReligiousPracticeDTO>($"{BASE_ENDPOINT}/{religionId}/practices", request);
                return response;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error adding religious practice to religion {religionId}: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Get deity information for a religion
        /// </summary>
        public async Task<List<DeityDTO>> GetDeitiesAsync(string religionId)
        {
            try
            {
                var response = await GetAsync<List<DeityDTO>>($"{BASE_ENDPOINT}/{religionId}/deities");
                return response ?? new List<DeityDTO>();
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error getting deities for religion {religionId}: {ex.Message}");
                return new List<DeityDTO>();
            }
        }

        /// <summary>
        /// Create a new deity for a religion
        /// </summary>
        public async Task<DeityDTO> CreateDeityAsync(string religionId, CreateDeityRequestDTO request)
        {
            try
            {
                var response = await PostAsync<CreateDeityRequestDTO, DeityDTO>($"{BASE_ENDPOINT}/{religionId}/deities", request);
                return response;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error creating deity for religion {religionId}: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Get religious calendar events
        /// </summary>
        public async Task<List<ReligiousEventDTO>> GetReligiousEventsAsync(string religionId)
        {
            try
            {
                var response = await GetAsync<List<ReligiousEventDTO>>($"{BASE_ENDPOINT}/{religionId}/events");
                return response ?? new List<ReligiousEventDTO>();
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error getting religious events for religion {religionId}: {ex.Message}");
                return new List<ReligiousEventDTO>();
            }
        }

        /// <summary>
        /// Create a religious event
        /// </summary>
        public async Task<ReligiousEventDTO> CreateReligiousEventAsync(string religionId, CreateReligiousEventRequestDTO request)
        {
            try
            {
                var response = await PostAsync<CreateReligiousEventRequestDTO, ReligiousEventDTO>($"{BASE_ENDPOINT}/{religionId}/events", request);
                return response;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error creating religious event for religion {religionId}: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Get religious influence in a region
        /// </summary>
        public async Task<ReligiousInfluenceDTO> GetReligiousInfluenceAsync(string religionId, string regionId)
        {
            try
            {
                var response = await GetAsync<ReligiousInfluenceDTO>($"{BASE_ENDPOINT}/{religionId}/influence/{regionId}");
                return response;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error getting religious influence for religion {religionId} in region {regionId}: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Update religious influence in a region
        /// </summary>
        public async Task<ReligiousInfluenceDTO> UpdateReligiousInfluenceAsync(string religionId, string regionId, UpdateReligiousInfluenceRequestDTO request)
        {
            try
            {
                var response = await PutAsync<UpdateReligiousInfluenceRequestDTO, ReligiousInfluenceDTO>($"{BASE_ENDPOINT}/{religionId}/influence/{regionId}", request);
                return response;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error updating religious influence for religion {religionId} in region {regionId}: {ex.Message}");
                return null;
            }
        }
    }
} 