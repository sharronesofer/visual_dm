using System.Collections.Generic;
using System.Threading.Tasks;
using System;
using UnityEngine;
using VDM.Systems.Region.Models;
using VDM.Infrastructure.Services;


namespace VDM.Systems.Region.Services
{
    /// <summary>
    /// HTTP service for region API communication
    /// Mirrors backend/systems/region/router.py endpoints
    /// </summary>
    public class RegionService : BaseHttpService
    {
        private const string REGIONS_ENDPOINT = "/regions";
        private const string WEATHER_ENDPOINT = "/regions/weather";
        private const string ANALYTICS_ENDPOINT = "/regions/analytics";

        /// <summary>
        /// Get all regions with optional filtering
        /// GET /regions
        /// </summary>
        public async Task<List<RegionDTO>> GetRegionsAsync(RegionQueryParams queryParams = null)
        {
            try
            {
                var endpoint = REGIONS_ENDPOINT;
                if (queryParams != null)
                {
                    var queryString = BuildQueryString(queryParams);
                    if (!string.IsNullOrEmpty(queryString))
                    {
                        endpoint += "?" + queryString;
                    }
                }

                return await GetAsync<List<RegionDTO>>(endpoint);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get regions: {ex.Message}");
                throw;
            }
        }

        /// <summary>
        /// Get specific region by ID
        /// GET /regions/{region_id}
        /// </summary>
        public async Task<RegionModel> GetRegionAsync(string regionId)
        {
            try
            {
                return await GetAsync<RegionModel>($"{REGIONS_ENDPOINT}/{regionId}");
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get region {regionId}: {ex.Message}");
                throw;
            }
        }

        /// <summary>
        /// Create a new region
        /// POST /regions
        /// </summary>
        public async Task<RegionModel> CreateRegionAsync(RegionModel region)
        {
            try
            {
                return await PostAsync<RegionModel>(REGIONS_ENDPOINT, region);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to create region: {ex.Message}");
                throw;
            }
        }

        /// <summary>
        /// Update existing region
        /// PUT /regions/{region_id}
        /// </summary>
        public async Task<RegionModel> UpdateRegionAsync(string regionId, RegionUpdateRequest updateRequest)
        {
            try
            {
                return await PutAsync<RegionModel>($"{REGIONS_ENDPOINT}/{regionId}", updateRequest);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to update region {regionId}: {ex.Message}");
                throw;
            }
        }

        /// <summary>
        /// Delete region
        /// DELETE /regions/{region_id}
        /// </summary>
        public async Task<bool> DeleteRegionAsync(string regionId)
        {
            try
            {
                return await DeleteAsync<bool>($"{REGIONS_ENDPOINT}/{regionId}");
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to delete region {regionId}: {ex.Message}");
                throw;
            }
        }

        /// <summary>
        /// Get region map data
        /// GET /regions/{region_id}/map
        /// </summary>
        public async Task<RegionMapDTO> GetRegionMapAsync(string regionId)
        {
            try
            {
                return await GetAsync<RegionMapDTO>($"{REGIONS_ENDPOINT}/{regionId}/map");
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get region map {regionId}: {ex.Message}");
                throw;
            }
        }

        /// <summary>
        /// Get regions by continent
        /// GET /regions/continent/{continent_id}
        /// </summary>
        public async Task<List<RegionDTO>> GetRegionsByContinentAsync(string continentId)
        {
            try
            {
                return await GetAsync<List<RegionDTO>>($"{REGIONS_ENDPOINT}/continent/{continentId}");
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get regions for continent {continentId}: {ex.Message}");
                throw;
            }
        }

        /// <summary>
        /// Get adjacent regions
        /// GET /regions/{region_id}/adjacent
        /// </summary>
        public async Task<List<RegionDTO>> GetAdjacentRegionsAsync(string regionId)
        {
            try
            {
                return await GetAsync<List<RegionDTO>>($"{REGIONS_ENDPOINT}/{regionId}/adjacent");
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get adjacent regions for {regionId}: {ex.Message}");
                throw;
            }
        }

        /// <summary>
        /// Get current weather for region
        /// GET /regions/{region_id}/weather
        /// </summary>
        public async Task<WeatherPattern> GetCurrentWeatherAsync(string regionId)
        {
            try
            {
                return await GetAsync<WeatherPattern>($"{REGIONS_ENDPOINT}/{regionId}/weather");
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get weather for region {regionId}: {ex.Message}");
                throw;
            }
        }

        /// <summary>
        /// Get weather forecast for region
        /// GET /regions/{region_id}/weather/forecast
        /// </summary>
        public async Task<List<WeatherForecast>> GetWeatherForecastAsync(string regionId, int days = 7)
        {
            try
            {
                return await GetAsync<List<WeatherForecast>>($"{REGIONS_ENDPOINT}/{regionId}/weather/forecast?days={days}");
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get weather forecast for region {regionId}: {ex.Message}");
                throw;
            }
        }

        /// <summary>
        /// Get region analytics
        /// GET /regions/{region_id}/analytics
        /// </summary>
        public async Task<RegionAnalytics> GetRegionAnalyticsAsync(string regionId)
        {
            try
            {
                return await GetAsync<RegionAnalytics>($"{REGIONS_ENDPOINT}/{regionId}/analytics");
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get analytics for region {regionId}: {ex.Message}");
                throw;
            }
        }

        /// <summary>
        /// Get POIs in region
        /// GET /regions/{region_id}/pois
        /// </summary>
        public async Task<List<object>> GetRegionPOIsAsync(string regionId)
        {
            try
            {
                return await GetAsync<List<object>>($"{REGIONS_ENDPOINT}/{regionId}/pois");
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get POIs for region {regionId}: {ex.Message}");
                throw;
            }
        }

        /// <summary>
        /// Get settlements in region
        /// GET /regions/{region_id}/settlements
        /// </summary>
        public async Task<List<object>> GetRegionSettlementsAsync(string regionId)
        {
            try
            {
                return await GetAsync<List<object>>($"{REGIONS_ENDPOINT}/{regionId}/settlements");
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get settlements for region {regionId}: {ex.Message}");
                throw;
            }
        }

        /// <summary>
        /// Initialize region system
        /// POST /regions/initialize
        /// </summary>
        public async Task<bool> InitializeRegionSystemAsync(string seed = null)
        {
            try
            {
                var requestData = new { seed = seed };
                return await PostAsync<bool>($"{REGIONS_ENDPOINT}/initialize", requestData);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to initialize region system: {ex.Message}");
                throw;
            }
        }

        private string BuildQueryString(RegionQueryParams queryParams)
        {
            var parameters = new List<string>();

            if (!string.IsNullOrEmpty(queryParams.ContinentId))
                parameters.Add($"continent_id={Uri.EscapeDataString(queryParams.ContinentId)}");

            if (queryParams.BiomeType.HasValue)
                parameters.Add($"biome_type={queryParams.BiomeType.Value}");

            if (queryParams.MinTemperature.HasValue)
                parameters.Add($"min_temperature={queryParams.MinTemperature.Value}");

            if (queryParams.MaxTemperature.HasValue)
                parameters.Add($"max_temperature={queryParams.MaxTemperature.Value}");

            if (queryParams.MinElevation.HasValue)
                parameters.Add($"min_elevation={queryParams.MinElevation.Value}");

            if (queryParams.MaxElevation.HasValue)
                parameters.Add($"max_elevation={queryParams.MaxElevation.Value}");

            if (!string.IsNullOrEmpty(queryParams.ControllingFactionId))
                parameters.Add($"controlling_faction_id={Uri.EscapeDataString(queryParams.ControllingFactionId)}");

            if (queryParams.HasResources.HasValue)
                parameters.Add($"has_resources={queryParams.HasResources.Value}");

            if (queryParams.MinPopulation.HasValue)
                parameters.Add($"min_population={queryParams.MinPopulation.Value}");

            if (queryParams.MaxPopulation.HasValue)
                parameters.Add($"max_population={queryParams.MaxPopulation.Value}");

            parameters.Add($"page={queryParams.Page}");
            parameters.Add($"page_size={queryParams.PageSize}");

            return string.Join("&", parameters);
        }
    }
} 