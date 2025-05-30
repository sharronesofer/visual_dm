using System.Collections.Generic;
using System;
using UnityEngine;
using VDM.Runtime.Region.Models;

namespace VDM.Runtime.WorldGeneration.Models
{
    /// <summary>
    /// Models for World Generation system based on backend/systems/world_generation structure
    /// </summary>

    [Serializable]
    public class ContinentModel
    {
        public string ContinentId { get; set; } = string.Empty;
        public string Name { get; set; } = string.Empty;
        public string Seed { get; set; } = string.Empty;
        public List<CoordinateSchemaDTO> RegionCoordinates { get; set; } = new List<CoordinateSchemaDTO>();
        public List<string> RegionIds { get; set; } = new List<string>();
        public CoordinateSchemaDTO OriginCoordinate { get; set; } = new CoordinateSchemaDTO();
        public ContinentBoundary Boundary { get; set; } = new ContinentBoundary();
        public DateTime CreationTimestamp { get; set; } = DateTime.UtcNow;
        public int NumRegions { get; set; } = 0;
        public Dictionary<string, object> Metadata { get; set; } = new Dictionary<string, object>();
    }

    [Serializable]
    public class ContinentBoundary
    {
        public int MinX { get; set; }
        public int MaxX { get; set; }
        public int MinY { get; set; }
        public int MaxY { get; set; }
    }

    [Serializable]
    public class WorldGenerationConfig
    {
        public string Name { get; set; } = "New World";
        public string Seed { get; set; } = string.Empty;
        public int NumRegionsTarget { get; set; } = 60;
        public Dictionary<string, object> Metadata { get; set; } = new Dictionary<string, object>();
        public BiomeGenerationParams BiomeParams { get; set; } = new BiomeGenerationParams();
        public SettlementGenerationParams SettlementParams { get; set; } = new SettlementGenerationParams();
    }

    [Serializable]
    public class BiomeGenerationParams
    {
        public float TemperatureVariance { get; set; } = 0.3f;
        public float MoistureVariance { get; set; } = 0.3f;
        public float ElevationVariance { get; set; } = 0.4f;
        public bool AllowOceans { get; set; } = true;
        public bool AllowMountains { get; set; } = true;
        public bool AllowDeserts { get; set; } = true;
        public float BiomeDiversity { get; set; } = 0.7f;
    }

    [Serializable]
    public class SettlementGenerationParams
    {
        public int MinCitiesPerRegion { get; set; } = 1;
        public int MaxCitiesPerRegion { get; set; } = 3;
        public int MinTownsPerRegion { get; set; } = 2;
        public int MaxTownsPerRegion { get; set; } = 5;
        public int MinVillagesPerRegion { get; set; } = 3;
        public int MaxVillagesPerRegion { get; set; } = 8;
        public bool AllowRuins { get; set; } = true;
        public float RuinDensity { get; set; } = 0.2f;
    }

    [Serializable]
    public class WorldGenerationProgress
    {
        public string Stage { get; set; } = "Initializing";
        public float OverallProgress { get; set; } = 0.0f;
        public float CurrentStageProgress { get; set; } = 0.0f;
        public string CurrentTask { get; set; } = string.Empty;
        public List<string> CompletedStages { get; set; } = new List<string>();
        public Dictionary<string, object> StageData { get; set; } = new Dictionary<string, object>();
        public bool IsComplete { get; set; } = false;
        public bool HasError { get; set; } = false;
        public string ErrorMessage { get; set; } = string.Empty;
    }

    [Serializable]
    public class WorldTemplate
    {
        public string Id { get; set; } = string.Empty;
        public string Name { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
        public WorldGenerationConfig Config { get; set; } = new WorldGenerationConfig();
        public string PreviewImagePath { get; set; } = string.Empty;
        public List<string> Tags { get; set; } = new List<string>();
        public bool IsCustom { get; set; } = false;
        public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    }

    [Serializable]
    public class WorldGenerationResult
    {
        public bool Success { get; set; } = false;
        public ContinentModel GeneratedContinent { get; set; }
        public List<RegionDTO> GeneratedRegions { get; set; } = new List<RegionDTO>();
        public WorldGenerationProgress Progress { get; set; } = new WorldGenerationProgress();
        public string Message { get; set; } = string.Empty;
        public Dictionary<string, object> GenerationStats { get; set; } = new Dictionary<string, object>();
    }
} 