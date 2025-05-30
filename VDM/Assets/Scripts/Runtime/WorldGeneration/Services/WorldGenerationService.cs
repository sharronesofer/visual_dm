using System.Collections.Generic;
using System.Threading.Tasks;
using System;
using UnityEngine;
using VDM.Runtime.Core.Services;
using VDM.Runtime.Region.Models;
using VDM.Runtime.WorldGeneration.Models;


namespace VDM.Runtime.WorldGeneration.Services
{
    /// <summary>
    /// HTTP service for world generation API communication
    /// Mirrors backend/systems/world_generation/api.py endpoints
    /// </summary>
    public class WorldGenerationService : BaseHttpService
    {
        private const string WORLDGEN_BASE_ENDPOINT = "/worldgen";
        private const string BIOMES_ENDPOINT = "/worldgen/biomes";
        private const string CONTINENTS_ENDPOINT = "/worldgen/continents";
        private const string TEMPLATES_ENDPOINT = "/worldgen/templates";

        /// <summary>
        /// Get all available biomes from the backend
        /// GET /worldgen/biomes
        /// </summary>
        public async Task<APIResponse<List<BiomeConfigDTO>>> GetBiomesAsync()
        {
            try
            {
                return await GetAsync<List<BiomeConfigDTO>>(BIOMES_ENDPOINT);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get biomes: {ex.Message}");
                return APIResponse<List<BiomeConfigDTO>>.Failure($"Failed to get biomes: {ex.Message}");
            }
        }

        /// <summary>
        /// Get specific biome configuration
        /// GET /worldgen/biomes/{biome_id}
        /// </summary>
        public async Task<APIResponse<BiomeConfigDTO>> GetBiomeAsync(string biomeId)
        {
            try
            {
                return await GetAsync<BiomeConfigDTO>($"{BIOMES_ENDPOINT}/{biomeId}");
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get biome {biomeId}: {ex.Message}");
                return APIResponse<BiomeConfigDTO>.Failure($"Failed to get biome: {ex.Message}");
            }
        }

        /// <summary>
        /// Create a new continent with specified parameters
        /// POST /worldgen/continents
        /// </summary>
        public async Task<APIResponse<ContinentModel>> CreateContinentAsync(WorldGenerationConfig config)
        {
            try
            {
                var requestData = new
                {
                    name = config.Name,
                    seed = config.Seed,
                    num_regions_target = config.NumRegionsTarget,
                    metadata = config.Metadata
                };

                return await PostAsync<ContinentModel>(CONTINENTS_ENDPOINT, requestData);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to create continent: {ex.Message}");
                return APIResponse<ContinentModel>.Failure($"Failed to create continent: {ex.Message}");
            }
        }

        /// <summary>
        /// Get all continents
        /// GET /worldgen/continents
        /// </summary>
        public async Task<APIResponse<List<ContinentModel>>> GetContinentsAsync()
        {
            try
            {
                return await GetAsync<List<ContinentModel>>(CONTINENTS_ENDPOINT);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get continents: {ex.Message}");
                return APIResponse<List<ContinentModel>>.Failure($"Failed to get continents: {ex.Message}");
            }
        }

        /// <summary>
        /// Get specific continent
        /// GET /worldgen/continents/{continent_id}
        /// </summary>
        public async Task<APIResponse<ContinentModel>> GetContinentAsync(string continentId)
        {
            try
            {
                return await GetAsync<ContinentModel>($"{CONTINENTS_ENDPOINT}/{continentId}");
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get continent {continentId}: {ex.Message}");
                return APIResponse<ContinentModel>.Failure($"Failed to get continent: {ex.Message}");
            }
        }

        /// <summary>
        /// Generate regions for a continent
        /// POST /worldgen/continents/{continent_id}/generate-regions
        /// </summary>
        public async Task<APIResponse<List<RegionDTO>>> GenerateRegionsAsync(string continentId, WorldGenerationConfig config)
        {
            try
            {
                var requestData = new
                {
                    biome_params = config.BiomeParams,
                    settlement_params = config.SettlementParams
                };

                return await PostAsync<List<RegionDTO>>($"{CONTINENTS_ENDPOINT}/{continentId}/generate-regions", requestData);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to generate regions for continent {continentId}: {ex.Message}");
                return APIResponse<List<RegionDTO>>.Failure($"Failed to generate regions: {ex.Message}");
            }
        }

        /// <summary>
        /// Get world generation progress
        /// GET /worldgen/progress/{generation_id}
        /// </summary>
        public async Task<APIResponse<WorldGenerationProgress>> GetGenerationProgressAsync(string generationId)
        {
            try
            {
                return await GetAsync<WorldGenerationProgress>($"/worldgen/progress/{generationId}");
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get generation progress {generationId}: {ex.Message}");
                return APIResponse<WorldGenerationProgress>.Failure($"Failed to get generation progress: {ex.Message}");
            }
        }

        /// <summary>
        /// Get available world templates
        /// GET /worldgen/templates
        /// </summary>
        public async Task<APIResponse<List<WorldTemplate>>> GetWorldTemplatesAsync()
        {
            try
            {
                return await GetAsync<List<WorldTemplate>>(TEMPLATES_ENDPOINT);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get world templates: {ex.Message}");
                return APIResponse<List<WorldTemplate>>.Failure($"Failed to get world templates: {ex.Message}");
            }
        }

        /// <summary>
        /// Create a new world template
        /// POST /worldgen/templates
        /// </summary>
        public async Task<APIResponse<WorldTemplate>> CreateWorldTemplateAsync(WorldTemplate template)
        {
            try
            {
                return await PostAsync<WorldTemplate>(TEMPLATES_ENDPOINT, template);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to create world template: {ex.Message}");
                return APIResponse<WorldTemplate>.Failure($"Failed to create world template: {ex.Message}");
            }
        }

        /// <summary>
        /// Update existing world template
        /// PUT /worldgen/templates/{template_id}
        /// </summary>
        public async Task<APIResponse<WorldTemplate>> UpdateWorldTemplateAsync(string templateId, WorldTemplate template)
        {
            try
            {
                return await PutAsync<WorldTemplate>($"{TEMPLATES_ENDPOINT}/{templateId}", template);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to update world template {templateId}: {ex.Message}");
                return APIResponse<WorldTemplate>.Failure($"Failed to update world template: {ex.Message}");
            }
        }

        /// <summary>
        /// Delete world template
        /// DELETE /worldgen/templates/{template_id}
        /// </summary>
        public async Task<APIResponse<bool>> DeleteWorldTemplateAsync(string templateId)
        {
            try
            {
                return await DeleteAsync<bool>($"{TEMPLATES_ENDPOINT}/{templateId}");
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to delete world template {templateId}: {ex.Message}");
                return APIResponse<bool>.Failure($"Failed to delete world template: {ex.Message}");
            }
        }

        /// <summary>
        /// Validate world generation configuration
        /// POST /worldgen/validate
        /// </summary>
        public async Task<APIResponse<bool>> ValidateWorldConfigAsync(WorldGenerationConfig config)
        {
            try
            {
                return await PostAsync<bool>("/worldgen/validate", config);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to validate world config: {ex.Message}");
                return APIResponse<bool>.Failure($"Failed to validate world config: {ex.Message}");
            }
        }

        /// <summary>
        /// Get world generation statistics
        /// GET /worldgen/stats
        /// </summary>
        public async Task<APIResponse<Dictionary<string, object>>> GetGenerationStatsAsync()
        {
            try
            {
                return await GetAsync<Dictionary<string, object>>("/worldgen/stats");
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get generation stats: {ex.Message}");
                return APIResponse<Dictionary<string, object>>.Failure($"Failed to get generation stats: {ex.Message}");
            }
        }
    }
} 