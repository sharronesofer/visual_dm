using System;
using System.Collections.Generic;
using UnityEngine;
using VisualDM.DTOs.World.Region;

namespace VDM.Systems.Region
{
    /// <summary>
    /// Region map generation and management system
    /// This is a simplified stub implementation for compilation.
    /// </summary>
    public class RegionMapSystem : MonoBehaviour
    {
        private Dictionary<string, RegionMapDTO> _regionMaps = new Dictionary<string, RegionMapDTO>();
        private Dictionary<RegionTypeDTO, BiomeConfigDTO> _biomeConfigurations = new Dictionary<RegionTypeDTO, BiomeConfigDTO>();

        void Start()
        {
            InitializeDefaultBiomes();
        }

        public RegionMapDTO GenerateRegionMap(string regionId, RegionTypeDTO biomeType, int width = 50, int height = 50)
        {
            var regionMap = new RegionMapDTO
            {
                RegionId = regionId,
                Width = width,
                Height = height
            };

            // Initialize basic maps
            regionMap.ElevationMap = new float[width, height];
            regionMap.BiomeMap = new RegionTypeDTO[width, height];
            regionMap.TemperatureMap = new float[width, height];
            regionMap.MoistureMap = new float[width, height];

            // Fill with basic data
            for (int x = 0; x < width; x++)
            {
                for (int y = 0; y < height; y++)
                {
                    regionMap.ElevationMap[x, y] = UnityEngine.Random.Range(0f, 100f);
                    regionMap.BiomeMap[x, y] = biomeType;
                    regionMap.TemperatureMap[x, y] = UnityEngine.Random.Range(0f, 40f);
                    regionMap.MoistureMap[x, y] = UnityEngine.Random.Range(0f, 100f);
                }
            }

            _regionMaps[regionId] = regionMap;
            return regionMap;
        }

        public RegionMapDTO GetRegionMap(string regionId)
        {
            return _regionMaps.ContainsKey(regionId) ? _regionMaps[regionId] : null;
        }

        public BiomeConfigDTO GetBiomeConfiguration(RegionTypeDTO biomeType)
        {
            return _biomeConfigurations.ContainsKey(biomeType) ? _biomeConfigurations[biomeType] : new BiomeConfigDTO();
        }

        public bool AreAdjacent(RegionTypeDTO biome1, RegionTypeDTO biome2)
        {
            var config1 = GetBiomeConfiguration(biome1);
            var config2 = GetBiomeConfiguration(biome2);
            
            // Simple adjacency check
            return config1.AdjacencyRules.Exists(rule => rule.AllowedNeighbors.Contains(biome2));
        }

        private void InitializeDefaultBiomes()
        {
            // Initialize basic biome configurations
            foreach (RegionTypeDTO biomeType in Enum.GetValues(typeof(RegionTypeDTO)))
            {
                var config = new BiomeConfigDTO
                {
                    Name = biomeType.ToString(),
                    TemperatureRange = new LevelRangeDTO { Min = 1, Max = 10 },
                    RainfallRange = new LevelRangeDTO { Min = 1, Max = 10 },
                    ElevationRange = new LevelRangeDTO { Min = 1, Max = 10 }
                };

                // Add basic terrain types
                config.TerrainTypes.Add(TerrainTypeDTO.Grassland);
                
                _biomeConfigurations[biomeType] = config;
            }

            Debug.Log("RegionMapSystem: Default biomes initialized");
        }
    }
} 