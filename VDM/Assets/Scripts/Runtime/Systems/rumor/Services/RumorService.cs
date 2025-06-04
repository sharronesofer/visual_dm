using System.Collections.Generic;
using System.Threading.Tasks;
using System;
using UnityEngine;
using VDM.Infrastructure.Services;
using VDM.DTOs.Common;
using VDM.Systems.Rumor.Models;


namespace VDM.Systems.Rumor.Services
{
    /// <summary>
    /// Service for managing rumor operations via HTTP API
    /// </summary>
    public class RumorService : BaseHttpService
    {
        private const string BASE_ENDPOINT = "/rumors";

        public RumorService(string baseUrl) : base(baseUrl)
        {
        }

        #region Rumor CRUD Operations

        /// <summary>
        /// Create a new rumor
        /// </summary>
        /// <param name="request">Rumor creation request</param>
        /// <returns>Created rumor</returns>
        public async Task<RumorDTO> CreateRumorAsync(CreateRumorRequestDTO request)
        {
            try
            {
                var response = await PostAsync<RumorDTO>(BASE_ENDPOINT, request);
                Debug.Log($"[RumorService] Created rumor: {response?.Id}");
                return response;
            }
            catch (Exception ex)
            {
                Debug.LogError($"[RumorService] Failed to create rumor: {ex.Message}");
                throw;
            }
        }

        /// <summary>
        /// Get a specific rumor by ID
        /// </summary>
        /// <param name="rumorId">ID of the rumor</param>
        /// <returns>Rumor details</returns>
        public async Task<RumorDTO> GetRumorAsync(string rumorId)
        {
            try
            {
                var response = await GetAsync<RumorDTO>($"{BASE_ENDPOINT}/{rumorId}");
                Debug.Log($"[RumorService] Retrieved rumor: {rumorId}");
                return response;
            }
            catch (Exception ex)
            {
                Debug.LogError($"[RumorService] Failed to get rumor {rumorId}: {ex.Message}");
                throw;
            }
        }

        /// <summary>
        /// List rumors with optional filtering
        /// </summary>
        /// <param name="entityId">Filter by entity who has heard them</param>
        /// <param name="category">Filter by category</param>
        /// <param name="minBelievability">Filter by minimum believability</param>
        /// <param name="limit">Maximum number of results</param>
        /// <returns>List of rumors</returns>
        public async Task<RumorListResponseDTO> ListRumorsAsync(
            string entityId = null, 
            string category = null, 
            float? minBelievability = null, 
            int limit = 10)
        {
            try
            {
                var queryParams = new List<string>();
                
                if (!string.IsNullOrEmpty(entityId))
                    queryParams.Add($"entity_id={entityId}");
                
                if (!string.IsNullOrEmpty(category))
                    queryParams.Add($"category={category}");
                
                if (minBelievability.HasValue)
                    queryParams.Add($"min_believability={minBelievability.Value}");
                
                queryParams.Add($"limit={limit}");

                var queryString = queryParams.Count > 0 ? "?" + string.Join("&", queryParams) : "";
                var response = await GetAsync<RumorListResponseDTO>($"{BASE_ENDPOINT}{queryString}");
                
                Debug.Log($"[RumorService] Listed {response?.Count ?? 0} rumors");
                return response;
            }
            catch (Exception ex)
            {
                Debug.LogError($"[RumorService] Failed to list rumors: {ex.Message}");
                throw;
            }
        }

        /// <summary>
        /// Delete a rumor
        /// </summary>
        /// <param name="rumorId">ID of the rumor to delete</param>
        /// <returns>Operation result</returns>
        public async Task<RumorOperationResponseDTO> DeleteRumorAsync(string rumorId)
        {
            try
            {
                var response = await DeleteAsync<RumorOperationResponseDTO>($"{BASE_ENDPOINT}/{rumorId}");
                Debug.Log($"[RumorService] Deleted rumor: {rumorId}");
                return response;
            }
            catch (Exception ex)
            {
                Debug.LogError($"[RumorService] Failed to delete rumor {rumorId}: {ex.Message}");
                throw;
            }
        }

        #endregion

        #region Rumor Spread Operations

        /// <summary>
        /// Spread a rumor from one entity to another
        /// </summary>
        /// <param name="request">Rumor spread request</param>
        /// <returns>Operation result</returns>
        public async Task<RumorOperationResponseDTO> SpreadRumorAsync(SpreadRumorRequestDTO request)
        {
            try
            {
                var response = await PostAsync<RumorOperationResponseDTO>($"{BASE_ENDPOINT}/spread", request);
                Debug.Log($"[RumorService] Spread rumor {request.RumorId} from {request.FromEntityId} to {request.ToEntityId}");
                return response;
            }
            catch (Exception ex)
            {
                Debug.LogError($"[RumorService] Failed to spread rumor: {ex.Message}");
                throw;
            }
        }

        /// <summary>
        /// Get all rumors known to a specific entity
        /// </summary>
        /// <param name="entityId">ID of the entity</param>
        /// <returns>Entity's known rumors</returns>
        public async Task<EntityRumorsResponseDTO> GetEntityRumorsAsync(string entityId)
        {
            try
            {
                var response = await GetAsync<EntityRumorsResponseDTO>($"{BASE_ENDPOINT}/entity/{entityId}");
                Debug.Log($"[RumorService] Retrieved {response?.Count ?? 0} rumors for entity {entityId}");
                return response;
            }
            catch (Exception ex)
            {
                Debug.LogError($"[RumorService] Failed to get rumors for entity {entityId}: {ex.Message}");
                throw;
            }
        }

        /// <summary>
        /// Apply decay to all rumors
        /// </summary>
        /// <param name="days">Days since last reinforcement to consider for decay</param>
        /// <returns>Operation result</returns>
        public async Task<RumorOperationResponseDTO> DecayRumorsAsync(int days = 7)
        {
            try
            {
                var response = await PostAsync<RumorOperationResponseDTO>($"{BASE_ENDPOINT}/decay?days={days}", null);
                Debug.Log($"[RumorService] Applied rumor decay for {days} days");
                return response;
            }
            catch (Exception ex)
            {
                Debug.LogError($"[RumorService] Failed to apply rumor decay: {ex.Message}");
                throw;
            }
        }

        #endregion

        #region Filtering and Search

        /// <summary>
        /// Get rumors by category
        /// </summary>
        /// <param name="category">Category to filter by</param>
        /// <param name="limit">Maximum number of results</param>
        /// <returns>Filtered rumors</returns>
        public async Task<RumorListResponseDTO> GetRumorsByCategoryAsync(RumorCategory category, int limit = 10)
        {
            return await ListRumorsAsync(category: category.ToString().ToLower(), limit: limit);
        }

        /// <summary>
        /// Get rumors by severity
        /// </summary>
        /// <param name="severity">Minimum severity level</param>
        /// <param name="limit">Maximum number of results</param>
        /// <returns>Filtered rumors</returns>
        public async Task<RumorListResponseDTO> GetRumorsBySeverityAsync(RumorSeverity severity, int limit = 10)
        {
            try
            {
                var allRumors = await ListRumorsAsync(limit: 100); // Get more to filter
                var filteredRumors = new List<RumorDTO>();

                foreach (var rumor in allRumors.Rumors)
                {
                    if (Enum.TryParse<RumorSeverity>(rumor.Severity, true, out var rumorSeverity))
                    {
                        if (rumorSeverity >= severity)
                        {
                            filteredRumors.Add(rumor);
                            if (filteredRumors.Count >= limit) break;
                        }
                    }
                }

                return new RumorListResponseDTO
                {
                    Rumors = filteredRumors,
                    Count = filteredRumors.Count,
                    Total = filteredRumors.Count
                };
            }
            catch (Exception ex)
            {
                Debug.LogError($"[RumorService] Failed to get rumors by severity: {ex.Message}");
                throw;
            }
        }

        /// <summary>
        /// Get highly believable rumors for an entity
        /// </summary>
        /// <param name="entityId">ID of the entity</param>
        /// <param name="minBelievability">Minimum believability threshold</param>
        /// <param name="limit">Maximum number of results</param>
        /// <returns>Believable rumors</returns>
        public async Task<RumorListResponseDTO> GetBelievableRumorsAsync(
            string entityId, 
            float minBelievability = 0.7f, 
            int limit = 10)
        {
            return await ListRumorsAsync(
                entityId: entityId, 
                minBelievability: minBelievability, 
                limit: limit);
        }

        #endregion

        #region Utility Methods

        /// <summary>
        /// Get rumor content as known to a specific entity
        /// </summary>
        /// <param name="rumorId">ID of the rumor</param>
        /// <param name="entityId">ID of the entity</param>
        /// <returns>Content as known to the entity, or null if unknown</returns>
        public async Task<string> GetRumorContentForEntityAsync(string rumorId, string entityId)
        {
            try
            {
                var rumor = await GetRumorAsync(rumorId);
                if (rumor?.Spread == null) return null;

                // Find the latest spread record for this entity
                RumorSpreadDTO latestSpread = null;
                DateTime latestTime = DateTime.MinValue;

                foreach (var spread in rumor.Spread)
                {
                    if (spread.EntityId == entityId && DateTime.TryParse(spread.HeardAt, out var heardTime))
                    {
                        if (heardTime > latestTime)
                        {
                            latestTime = heardTime;
                            latestSpread = spread;
                        }
                    }
                }

                if (latestSpread == null) return null;

                // Find the variant content
                foreach (var variant in rumor.Variants)
                {
                    if (variant.Id == latestSpread.VariantId)
                    {
                        return variant.Content;
                    }
                }

                return rumor.OriginalContent; // Fallback to original
            }
            catch (Exception ex)
            {
                Debug.LogError($"[RumorService] Failed to get rumor content for entity: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Get believability of a rumor for a specific entity
        /// </summary>
        /// <param name="rumorId">ID of the rumor</param>
        /// <param name="entityId">ID of the entity</param>
        /// <returns>Believability value, or null if entity doesn't know the rumor</returns>
        public async Task<float?> GetRumorBelievabilityForEntityAsync(string rumorId, string entityId)
        {
            try
            {
                var rumor = await GetRumorAsync(rumorId);
                if (rumor?.Spread == null) return null;

                // Find the latest spread record for this entity
                RumorSpreadDTO latestSpread = null;
                DateTime latestTime = DateTime.MinValue;

                foreach (var spread in rumor.Spread)
                {
                    if (spread.EntityId == entityId && DateTime.TryParse(spread.HeardAt, out var heardTime))
                    {
                        if (heardTime > latestTime)
                        {
                            latestTime = heardTime;
                            latestSpread = spread;
                        }
                    }
                }

                return latestSpread?.Believability;
            }
            catch (Exception ex)
            {
                Debug.LogError($"[RumorService] Failed to get rumor believability for entity: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Check if an entity knows a specific rumor
        /// </summary>
        /// <param name="rumorId">ID of the rumor</param>
        /// <param name="entityId">ID of the entity</param>
        /// <returns>True if entity knows the rumor</returns>
        public async Task<bool> EntityKnowsRumorAsync(string rumorId, string entityId)
        {
            try
            {
                var rumor = await GetRumorAsync(rumorId);
                if (rumor?.Spread == null) return false;

                foreach (var spread in rumor.Spread)
                {
                    if (spread.EntityId == entityId)
                        return true;
                }

                return false;
            }
            catch (Exception ex)
            {
                Debug.LogError($"[RumorService] Failed to check if entity knows rumor: {ex.Message}");
                return false;
            }
        }

        #endregion
    }
} 