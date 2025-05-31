using System;
using System.Collections.Generic;
using UnityEngine;

namespace VisualDM.DTOs.World.Region
{
    /// <summary>
    /// Region types based on biome/environment
    /// </summary>
    public enum RegionTypeDTO
    {
        Plains,
        Forest,
        Desert,
        Mountain,
        Swamp,
        Tundra,
        Jungle,
        Coast,
        Steppe,
        Volcanic,
        Urban,
        River,
        Lake,
        Custom
    }

    /// <summary>
    /// Terrain types for tiles
    /// </summary>
    public enum TerrainTypeDTO
    {
        Grassland,
        Forest,
        Mountain,
        Hill,
        Water,
        Desert,
        Swamp,
        Tundra,
        Jungle,
        Coast,
        Ocean,
        Lake,
        River,
        Cave,
        Wasteland,
        Volcanic,
        Ice,
        Snow
    }

    /// <summary>
    /// Coordinate representation for positions
    /// </summary>
    [Serializable]
    public class CoordinateSchemaDTO
    {
        public float X { get; set; } = 0.0f;
        public float Y { get; set; } = 0.0f;
        public float? Z { get; set; }
    }

    /// <summary>
    /// Level range for scaling
    /// </summary>
    [Serializable]
    public class LevelRangeDTO
    {
        public int Min { get; set; } = 1;
        public int Max { get; set; } = 10;
        public float Average => (Min + Max) / 2.0f;
        public bool IsValid => Min <= Max;
    }

    /// <summary>
    /// River data transfer object
    /// </summary>
    [Serializable]
    public class RiverDTO
    {
        public string Name { get; set; } = string.Empty;
        public List<CoordinateSchemaDTO> Path { get; set; } = new List<CoordinateSchemaDTO>();
        public float Width { get; set; } = 1.0f;
    }

    /// <summary>
    /// Road data transfer object
    /// </summary>
    [Serializable]
    public class RoadDTO
    {
        public string Name { get; set; } = string.Empty;
        public List<CoordinateSchemaDTO> Path { get; set; } = new List<CoordinateSchemaDTO>();
        public string Type { get; set; } = "Dirt";
    }

    /// <summary>
    /// Adjacency rules for biomes
    /// </summary>
    [Serializable]
    public class AdjacencyRuleDTO
    {
        public RegionTypeDTO BiomeType { get; set; }
        public List<RegionTypeDTO> AllowedNeighbors { get; set; } = new List<RegionTypeDTO>();
        public float PreferenceWeight { get; set; } = 1.0f;
    }

    /// <summary>
    /// Biome configuration
    /// </summary>
    [Serializable]
    public class BiomeConfigDTO
    {
        public string Name { get; set; } = string.Empty;
        public LevelRangeDTO TemperatureRange { get; set; } = new LevelRangeDTO();
        public LevelRangeDTO RainfallRange { get; set; } = new LevelRangeDTO();
        public LevelRangeDTO ElevationRange { get; set; } = new LevelRangeDTO();
        public List<TerrainTypeDTO> TerrainTypes { get; set; } = new List<TerrainTypeDTO>();
        public List<string> ResourceTypes { get; set; } = new List<string>();
        public List<AdjacencyRuleDTO> AdjacencyRules { get; set; } = new List<AdjacencyRuleDTO>();
    }

    /// <summary>
    /// Region map data
    /// </summary>
    [Serializable]
    public class RegionMapDTO
    {
        public string RegionId { get; set; } = string.Empty;
        public int Width { get; set; } = 50;
        public int Height { get; set; } = 50;
        public float[,] ElevationMap { get; set; }
        public RegionTypeDTO[,] BiomeMap { get; set; }
        public float[,] TemperatureMap { get; set; }
        public float[,] MoistureMap { get; set; }
        public List<List<TileDTO>> Tiles { get; set; } = new List<List<TileDTO>>();
        public List<RiverDTO> Rivers { get; set; } = new List<RiverDTO>();
        public List<RoadDTO> Roads { get; set; } = new List<RoadDTO>();

        public RegionMapDTO()
        {
            ElevationMap = new float[Width, Height];
            BiomeMap = new RegionTypeDTO[Width, Height];
            TemperatureMap = new float[Width, Height];
            MoistureMap = new float[Width, Height];
        }
    }

    /// <summary>
    /// Region metadata
    /// </summary>
    [Serializable]
    public class RegionDTO
    {
        public string RegionId { get; set; } = string.Empty;
        public string Name { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
        public CoordinateSchemaDTO Coordinates { get; set; } = new CoordinateSchemaDTO();
        public RegionTypeDTO BiomeType { get; set; } = RegionTypeDTO.Plains;
        public LevelRangeDTO LevelRange { get; set; } = new LevelRangeDTO();
        public int Size { get; set; } = 5;
        public int TotalPopulation { get; set; } = 0;
        public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
        public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;
    }
} 