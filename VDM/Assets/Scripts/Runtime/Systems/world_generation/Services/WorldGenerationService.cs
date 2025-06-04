using System.Collections.Generic;
using System.Threading.Tasks;
using System;
using UnityEngine;
using VDM.Systems.Region.Models;
using VDM.Systems.Worldgeneration.Models;
using VDM.Infrastructure.Services;


namespace VDM.Systems.Worldgeneration.Services
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
        public async Task<List<BiomeConfigDTO>> GetBiomesAsync()
        {
            try
            {
                var result = await GetAsync<List<BiomeConfigDTO>>(BIOMES_ENDPOINT);
                return result ?? new List<BiomeConfigDTO>();
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get biomes: {ex.Message}");
                return new List<BiomeConfigDTO>();
            }
        }

        /// <summary>
        /// Get specific biome configuration
        /// GET /worldgen/biomes/{biome_id}
        /// </summary>
        public async Task<BiomeConfigDTO> GetBiomeAsync(string biomeId)
        {
            try
            {
                return await GetAsync<BiomeConfigDTO>($"{BIOMES_ENDPOINT}/{biomeId}");
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get biome {biomeId}: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Create a new continent with specified parameters
        /// POST /worldgen/continents
        /// </summary>
        public async Task<ContinentModel> CreateContinentAsync(WorldGenerationConfig config)
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
                return null;
            }
        }

        /// <summary>
        /// Get all continents
        /// GET /worldgen/continents
        /// </summary>
        public async Task<List<ContinentModel>> GetContinentsAsync()
        {
            try
            {
                var result = await GetAsync<List<ContinentModel>>(CONTINENTS_ENDPOINT);
                return result ?? new List<ContinentModel>();
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get continents: {ex.Message}");
                return new List<ContinentModel>();
            }
        }

        /// <summary>
        /// Get specific continent
        /// GET /worldgen/continents/{continent_id}
        /// </summary>
        public async Task<ContinentModel> GetContinentAsync(string continentId)
        {
            try
            {
                return await GetAsync<ContinentModel>($"{CONTINENTS_ENDPOINT}/{continentId}");
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get continent {continentId}: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Delete a continent
        /// DELETE /worldgen/continents/{continent_id}
        /// </summary>
        public async Task<bool> DeleteContinentAsync(string continentId)
        {
            try
            {
                await DeleteAsync($"{CONTINENTS_ENDPOINT}/{continentId}");
                return true;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to delete continent {continentId}: {ex.Message}");
                return false;
            }
        }

        /// <summary>
        /// Generate regions for a specific continent
        /// POST /worldgen/continents/{continent_id}/generate-regions
        /// </summary>
        public async Task<List<VDM.Systems.Worldgeneration.Models.RegionDTO>> GenerateRegionsForContinentAsync(string continentId, RegionGenerationConfig config)
        {
            try
            {
                var requestData = new
                {
                    config.NumRegions,
                    biome_params = config.BiomeParams,
                    settlement_params = config.SettlementParams,
                    custom_params = config.CustomParams
                };

                var response = await PostAsync<List<VDM.Systems.Worldgeneration.Models.RegionDTO>>($"{CONTINENTS_ENDPOINT}/{continentId}/generate-regions", requestData);
                return response ?? new List<VDM.Systems.Worldgeneration.Models.RegionDTO>();
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error generating regions for continent: {ex.Message}");
                return new List<VDM.Systems.Worldgeneration.Models.RegionDTO>();
            }
        }

        /// <summary>
        /// Generate continents based on configuration
        /// </summary>
        public async Task<List<ContinentDTO>> GenerateContinentsAsync(ContinentGenerationConfig config)
        {
            try
            {
                var response = await PostAsync<List<ContinentDTO>>($"{CONTINENTS_ENDPOINT}/generate", config);
                return response ?? new List<ContinentDTO>();
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error generating continents: {ex.Message}");
                return new List<ContinentDTO>();
            }
        }

        /// <summary>
        /// Generate biomes for a continent
        /// </summary>
        public async Task<List<BiomeConfigDTO>> GenerateBiomesAsync(BiomeGenerationConfig config)
        {
            try
            {
                var response = await PostAsync<List<BiomeConfigDTO>>($"{BIOMES_ENDPOINT}/generate", config);
                return response ?? new List<BiomeConfigDTO>();
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error generating biomes: {ex.Message}");
                return new List<BiomeConfigDTO>();
            }
        }

        /// <summary>
        /// Generate templates
        /// </summary>
        public async Task<List<TemplateGenerationConfig>> GenerateTemplatesAsync(TemplateGenerationRequest request)
        {
            try
            {
                var response = await PostAsync<List<TemplateGenerationConfig>>($"{TEMPLATES_ENDPOINT}/generate", request);
                return response ?? new List<TemplateGenerationConfig>();
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error generating templates: {ex.Message}");
                return new List<TemplateGenerationConfig>();
            }
        }

        /// <summary>
        /// Generate regions using template
        /// </summary>
        public async Task<List<VDM.Systems.Worldgeneration.Models.RegionDTO>> GenerateRegionsFromTemplateAsync(string templateId, RegionGenerationConfig config)
        {
            try
            {
                var response = await PostAsync<List<VDM.Systems.Worldgeneration.Models.RegionDTO>>($"{TEMPLATES_ENDPOINT}/{templateId}/generate-regions", config);
                return response ?? new List<VDM.Systems.Worldgeneration.Models.RegionDTO>();
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error generating regions from template: {ex.Message}");
                return new List<VDM.Systems.Worldgeneration.Models.RegionDTO>();
            }
        }

        /// <summary>
        /// Get generation progress
        /// </summary>
        public async Task<WorldGenerationProgress> GetGenerationProgressAsync(string jobId)
        {
            try
            {
                var response = await GetAsync<WorldGenerationProgress>($"{WORLDGEN_BASE_ENDPOINT}/progress/{jobId}");
                return response ?? new WorldGenerationProgress();
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error getting generation progress: {ex.Message}");
                return new WorldGenerationProgress();
            }
        }

        /// <summary>
        /// Get available world templates
        /// </summary>
        public async Task<List<WorldTemplate>> GetWorldTemplatesAsync()
        {
            try
            {
                var response = await GetAsync<List<WorldTemplate>>(TEMPLATES_ENDPOINT);
                return response ?? new List<WorldTemplate>();
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get world templates: {ex.Message}");
                return new List<WorldTemplate>();
            }
        }

        /// <summary>
        /// Create a new world template
        /// </summary>
        public async Task<WorldTemplate> CreateWorldTemplateAsync(WorldTemplate template)
        {
            try
            {
                var response = await PostAsync<WorldTemplate>(TEMPLATES_ENDPOINT, template);
                return response;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to create world template: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Update existing world template
        /// </summary>
        public async Task<WorldTemplate> UpdateWorldTemplateAsync(string templateId, WorldTemplate template)
        {
            try
            {
                var response = await PutAsync<WorldTemplate>($"{TEMPLATES_ENDPOINT}/{templateId}", template);
                return response;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to update world template {templateId}: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Delete world template
        /// </summary>
        public async Task<bool> DeleteWorldTemplateAsync(string templateId)
        {
            try
            {
                await DeleteAsync($"{TEMPLATES_ENDPOINT}/{templateId}");
                return true;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to delete world template {templateId}: {ex.Message}");
                return false;
            }
        }

        /// <summary>
        /// Validate world generation configuration
        /// </summary>
        public async Task<bool> ValidateWorldConfigAsync(WorldGenerationConfig config)
        {
            try
            {
                var response = await PostAsync<bool>("/worldgen/validate", config);
                return response;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to validate world config: {ex.Message}");
                return false;
            }
        }

        /// <summary>
        /// Get world generation statistics
        /// </summary>
        public async Task<Dictionary<string, object>> GetGenerationStatsAsync()
        {
            try
            {
                var response = await GetAsync<Dictionary<string, object>>("/worldgen/stats");
                return response ?? new Dictionary<string, object>();
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get generation stats: {ex.Message}");
                return new Dictionary<string, object>();
            }
        }
    }
} 