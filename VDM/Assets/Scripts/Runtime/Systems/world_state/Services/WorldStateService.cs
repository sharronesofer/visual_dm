using System.Collections.Generic;
using System.Threading.Tasks;
using System;
using UnityEngine;
using VDM.DTOs.Common;
using VDM.Systems.Character.Models;
using VDM.Infrastructure.Services;
using VDM.Infrastructure.Services;


namespace VDM.Systems.Worldstate.Services
{
    /// <summary>
    /// Service for managing world state operations via HTTP API
    /// </summary>
    public class WorldStateService : MonoBehaviour
    {
        [Header("Configuration")]
        [SerializeField] private string baseUrl = "http://localhost:8000";
        [SerializeField] private float requestTimeout = 30f;
        [SerializeField] private bool enableLogging = true;

        private HttpService httpService;

        private void Awake()
        {
            httpService = new HttpService(baseUrl);
            if (enableLogging)
            {
                Debug.Log("WorldStateService initialized with HttpService");
            }
        }

        #region World Regions

        /// <summary>
        /// Get all world regions
        /// </summary>
        public async Task<WorldStateResponse<List<WorldRegion>>> GetRegionsAsync(WorldStateQueryParams queryParams = null)
        {
            try
            {
                var url = $"{baseUrl}/api/world-state/regions";
                if (queryParams != null)
                {
                    url += BuildQueryString(queryParams);
                }

                if (enableLogging)
                    Debug.Log($"[WorldStateService] Getting regions from: {url}");

                var response = await httpService.GetAsync<WorldStateResponse<List<WorldRegion>>>(url);
                return response;
            }
            catch (Exception ex)
            {
                Debug.LogError($"[WorldStateService] Error getting regions: {ex.Message}");
                return new WorldStateResponse<List<WorldRegion>>
                {
                    success = false,
                    errors = new List<string> { ex.Message }
                };
            }
        }

        /// <summary>
        /// Get a specific world region by ID
        /// </summary>
        public async Task<WorldStateResponse<WorldRegion>> GetRegionAsync(string regionId)
        {
            try
            {
                var url = $"{baseUrl}/api/world-state/regions/{regionId}";

                if (enableLogging)
                    Debug.Log($"[WorldStateService] Getting region: {regionId}");

                var response = await httpService.GetAsync<WorldStateResponse<WorldRegion>>(url);
                return response;
            }
            catch (Exception ex)
            {
                Debug.LogError($"[WorldStateService] Error getting region {regionId}: {ex.Message}");
                return new WorldStateResponse<WorldRegion>
                {
                    success = false,
                    errors = new List<string> { ex.Message }
                };
            }
        }

        /// <summary>
        /// Create a new world region
        /// </summary>
        public async Task<WorldStateResponse<WorldRegion>> CreateRegionAsync(WorldRegion region)
        {
            try
            {
                var url = $"{baseUrl}/api/world-state/regions";

                if (enableLogging)
                    Debug.Log($"[WorldStateService] Creating region: {region.name}");

                var response = await httpService.PostAsync<WorldRegion, WorldStateResponse<WorldRegion>>(url, region);
                return response;
            }
            catch (Exception ex)
            {
                Debug.LogError($"[WorldStateService] Error creating region: {ex.Message}");
                return new WorldStateResponse<WorldRegion>
                {
                    success = false,
                    errors = new List<string> { ex.Message }
                };
            }
        }

        /// <summary>
        /// Update an existing world region
        /// </summary>
        public async Task<WorldStateResponse<WorldRegion>> UpdateRegionAsync(string regionId, WorldRegion region)
        {
            try
            {
                var url = $"{baseUrl}/api/world-state/regions/{regionId}";

                if (enableLogging)
                    Debug.Log($"[WorldStateService] Updating region: {regionId}");

                var response = await httpService.PutAsync<WorldRegion, WorldStateResponse<WorldRegion>>(url, region);
                return response;
            }
            catch (Exception ex)
            {
                Debug.LogError($"[WorldStateService] Error updating region {regionId}: {ex.Message}");
                return new WorldStateResponse<WorldRegion>
                {
                    success = false,
                    errors = new List<string> { ex.Message }
                };
            }
        }

        /// <summary>
        /// Delete a world region
        /// </summary>
        public async Task<WorldStateResponse<bool>> DeleteRegionAsync(string regionId)
        {
            try
            {
                var url = $"{baseUrl}/api/world-state/regions/{regionId}";

                if (enableLogging)
                    Debug.Log($"[WorldStateService] Deleting region: {regionId}");

                await httpService.DeleteAsync(url);
                return new WorldStateResponse<bool>
                {
                    success = true,
                    data = true
                };
            }
            catch (Exception ex)
            {
                Debug.LogError($"[WorldStateService] Error deleting region {regionId}: {ex.Message}");
                return new WorldStateResponse<bool>
                {
                    success = false,
                    errors = new List<string> { ex.Message }
                };
            }
        }

        #endregion

        #region Region State Management

        /// <summary>
        /// Get state for a specific region and category
        /// </summary>
        public async Task<WorldStateResponse<Dictionary<string, object>>> GetRegionStateAsync(string regionId, StateCategory category)
        {
            try
            {
                var url = $"{baseUrl}/api/world-state/regions/{regionId}/state/{category}";

                if (enableLogging)
                    Debug.Log($"[WorldStateService] Getting region state: {regionId}, category: {category}");

                var response = await httpService.GetAsync<WorldStateResponse<Dictionary<string, object>>>(url);
                return response;
            }
            catch (Exception ex)
            {
                Debug.LogError($"[WorldStateService] Error getting region state: {ex.Message}");
                return new WorldStateResponse<Dictionary<string, object>>
                {
                    success = false,
                    errors = new List<string> { ex.Message }
                };
            }
        }

        /// <summary>
        /// Set state for a specific region and category
        /// </summary>
        public async Task<WorldStateResponse<bool>> SetRegionStateAsync(string regionId, StateCategory category, Dictionary<string, object> stateData)
        {
            try
            {
                var url = $"{baseUrl}/api/world-state/regions/{regionId}/state/{category}";

                if (enableLogging)
                    Debug.Log($"[WorldStateService] Setting region state: {regionId}, category: {category}");

                var response = await httpService.PutAsync<Dictionary<string, object>, WorldStateResponse<bool>>(url, stateData);
                return response;
            }
            catch (Exception ex)
            {
                Debug.LogError($"[WorldStateService] Error setting region state: {ex.Message}");
                return new WorldStateResponse<bool>
                {
                    success = false,
                    errors = new List<string> { ex.Message }
                };
            }
        }

        /// <summary>
        /// Update state for a specific region and category
        /// </summary>
        public async Task<WorldStateResponse<bool>> UpdateRegionStateAsync(string regionId, StateCategory category, Dictionary<string, object> updates)
        {
            try
            {
                var url = $"{baseUrl}/api/world-state/regions/{regionId}/state/{category}/update";

                if (enableLogging)
                    Debug.Log($"[WorldStateService] Updating region state: {regionId}, category: {category}");

                var response = await httpService.PatchAsync<Dictionary<string, object>, WorldStateResponse<bool>>(url, updates);
                return response;
            }
            catch (Exception ex)
            {
                Debug.LogError($"[WorldStateService] Error updating region state: {ex.Message}");
                return new WorldStateResponse<bool>
                {
                    success = false,
                    errors = new List<string> { ex.Message }
                };
            }
        }

        #endregion

        #region World Maps

        /// <summary>
        /// Get all world maps
        /// </summary>
        public async Task<WorldStateResponse<List<WorldMap>>> GetMapsAsync()
        {
            try
            {
                var url = $"{baseUrl}/api/world-state/maps";

                if (enableLogging)
                    Debug.Log($"[WorldStateService] Getting world maps");

                var response = await httpService.GetAsync<WorldStateResponse<List<WorldMap>>>(url);
                return response;
            }
            catch (Exception ex)
            {
                Debug.LogError($"[WorldStateService] Error getting maps: {ex.Message}");
                return new WorldStateResponse<List<WorldMap>>
                {
                    success = false,
                    errors = new List<string> { ex.Message }
                };
            }
        }

        /// <summary>
        /// Get a specific world map by ID
        /// </summary>
        public async Task<WorldStateResponse<WorldMap>> GetMapAsync(string mapId)
        {
            try
            {
                var url = $"{baseUrl}/api/world-state/maps/{mapId}";

                if (enableLogging)
                    Debug.Log($"[WorldStateService] Getting map: {mapId}");

                var response = await httpService.GetAsync<WorldStateResponse<WorldMap>>(url);
                return response;
            }
            catch (Exception ex)
            {
                Debug.LogError($"[WorldStateService] Error getting map {mapId}: {ex.Message}");
                return new WorldStateResponse<WorldMap>
                {
                    success = false,
                    errors = new List<string> { ex.Message }
                };
            }
        }

        /// <summary>
        /// Create a new world map
        /// </summary>
        public async Task<WorldStateResponse<WorldMap>> CreateMapAsync(WorldMap map)
        {
            try
            {
                var url = $"{baseUrl}/api/world-state/maps";

                if (enableLogging)
                    Debug.Log($"[WorldStateService] Creating map: {map.name}");

                var response = await httpService.PostAsync<WorldMap, WorldStateResponse<WorldMap>>(url, map);
                return response;
            }
            catch (Exception ex)
            {
                Debug.LogError($"[WorldStateService] Error creating map: {ex.Message}");
                return new WorldStateResponse<WorldMap>
                {
                    success = false,
                    errors = new List<string> { ex.Message }
                };
            }
        }

        #endregion

        #region Snapshots

        /// <summary>
        /// Get all world state snapshots
        /// </summary>
        public async Task<WorldStateResponse<List<WorldStateSnapshot>>> GetSnapshotsAsync()
        {
            try
            {
                var url = $"{baseUrl}/api/world-state/snapshots";

                if (enableLogging)
                    Debug.Log($"[WorldStateService] Getting snapshots");

                var response = await httpService.GetAsync<WorldStateResponse<List<WorldStateSnapshot>>>(url);
                return response;
            }
            catch (Exception ex)
            {
                Debug.LogError($"[WorldStateService] Error getting snapshots: {ex.Message}");
                return new WorldStateResponse<List<WorldStateSnapshot>>
                {
                    success = false,
                    errors = new List<string> { ex.Message }
                };
            }
        }

        /// <summary>
        /// Create a world state snapshot
        /// </summary>
        public async Task<WorldStateResponse<WorldStateSnapshot>> CreateSnapshotAsync(CreateSnapshotRequest request)
        {
            try
            {
                var url = $"{baseUrl}/api/world-state/snapshots";

                if (enableLogging)
                    Debug.Log($"[WorldStateService] Creating snapshot: {request.name}");

                var response = await httpService.PostAsync<CreateSnapshotRequest, WorldStateResponse<WorldStateSnapshot>>(url, request);
                return response;
            }
            catch (Exception ex)
            {
                Debug.LogError($"[WorldStateService] Error creating snapshot: {ex.Message}");
                return new WorldStateResponse<WorldStateSnapshot>
                {
                    success = false,
                    errors = new List<string> { ex.Message }
                };
            }
        }

        /// <summary>
        /// Restore world state from a snapshot
        /// </summary>
        public async Task<WorldStateResponse<bool>> RestoreSnapshotAsync(RestoreSnapshotRequest request)
        {
            try
            {
                var url = $"{baseUrl}/api/world-state/snapshots/{request.snapshotId}/restore";

                if (enableLogging)
                    Debug.Log($"[WorldStateService] Restoring snapshot: {request.snapshotId}");

                var response = await httpService.PostAsync<RestoreSnapshotRequest, WorldStateResponse<bool>>(url, request);
                return response;
            }
            catch (Exception ex)
            {
                Debug.LogError($"[WorldStateService] Error restoring snapshot: {ex.Message}");
                return new WorldStateResponse<bool>
                {
                    success = false,
                    errors = new List<string> { ex.Message }
                };
            }
        }

        /// <summary>
        /// Delete a world state snapshot
        /// </summary>
        public async Task<WorldStateResponse<bool>> DeleteSnapshotAsync(string snapshotId)
        {
            try
            {
                var url = $"{baseUrl}/api/world-state/snapshots/{snapshotId}";

                if (enableLogging)
                    Debug.Log($"[WorldStateService] Deleting snapshot: {snapshotId}");

                await httpService.DeleteAsync(url);
                return new WorldStateResponse<bool>
                {
                    success = true,
                    data = true
                };
            }
            catch (Exception ex)
            {
                Debug.LogError($"[WorldStateService] Error deleting snapshot: {ex.Message}");
                return new WorldStateResponse<bool>
                {
                    success = false,
                    errors = new List<string> { ex.Message }
                };
            }
        }

        #endregion

        #region State Changes

        /// <summary>
        /// Get state change history
        /// </summary>
        public async Task<WorldStateResponse<List<StateChangeRecord>>> GetStateChangesAsync(WorldStateQueryParams queryParams = null)
        {
            try
            {
                var url = $"{baseUrl}/api/world-state/changes";
                if (queryParams != null)
                {
                    url += BuildQueryString(queryParams);
                }

                if (enableLogging)
                    Debug.Log($"[WorldStateService] Getting state changes");

                var response = await httpService.GetAsync<WorldStateResponse<List<StateChangeRecord>>>(url);
                return response;
            }
            catch (Exception ex)
            {
                Debug.LogError($"[WorldStateService] Error getting state changes: {ex.Message}");
                return new WorldStateResponse<List<StateChangeRecord>>
                {
                    success = false,
                    errors = new List<string> { ex.Message }
                };
            }
        }

        #endregion

        #region Analytics

        /// <summary>
        /// Get world state analytics
        /// </summary>
        public async Task<WorldStateResponse<WorldStateAnalytics>> GetAnalyticsAsync()
        {
            try
            {
                var url = $"{baseUrl}/api/world-state/analytics";

                if (enableLogging)
                    Debug.Log($"[WorldStateService] Getting analytics");

                var response = await httpService.GetAsync<WorldStateResponse<WorldStateAnalytics>>(url);
                return response;
            }
            catch (Exception ex)
            {
                Debug.LogError($"[WorldStateService] Error getting analytics: {ex.Message}");
                return new WorldStateResponse<WorldStateAnalytics>
                {
                    success = false,
                    errors = new List<string> { ex.Message }
                };
            }
        }

        #endregion

        #region Utility Methods

        /// <summary>
        /// Build query string from parameters
        /// </summary>
        private string BuildQueryString(WorldStateQueryParams queryParams)
        {
            var parameters = new List<string>();

            if (queryParams.categories != null && queryParams.categories.Count > 0)
            {
                parameters.Add($"categories={string.Join(",", queryParams.categories)}");
            }

            if (queryParams.regionIds != null && queryParams.regionIds.Count > 0)
            {
                parameters.Add($"regionIds={string.Join(",", queryParams.regionIds)}");
            }

            if (queryParams.fromDate.HasValue)
            {
                parameters.Add($"fromDate={queryParams.fromDate.Value:yyyy-MM-ddTHH:mm:ssZ}");
            }

            if (queryParams.toDate.HasValue)
            {
                parameters.Add($"toDate={queryParams.toDate.Value:yyyy-MM-ddTHH:mm:ssZ}");
            }

            if (queryParams.limit.HasValue)
            {
                parameters.Add($"limit={queryParams.limit.Value}");
            }

            if (queryParams.offset.HasValue)
            {
                parameters.Add($"offset={queryParams.offset.Value}");
            }

            if (!string.IsNullOrEmpty(queryParams.search))
            {
                parameters.Add($"search={UnityEngine.Networking.UnityWebRequest.EscapeURL(queryParams.search)}");
            }

            return parameters.Count > 0 ? "?" + string.Join("&", parameters) : "";
        }

        #endregion
    }
} 