using System.Collections.Generic;
using System;
using UnityEngine;
using VDM.DTOs.Common;

namespace VDM.Systems.Worldgeneration.Models
{
    /// <summary>
    /// Models for World Generation system based on backend/systems/world_generation structure
    /// </summary>

    [Serializable]
    public class BiomeConfigDTO
    {
        public string Id { get; set; } = string.Empty;
        public string Name { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
        public float Temperature { get; set; } = 0f;
        public float Humidity { get; set; } = 0f;
        public float Elevation { get; set; } = 0f;
        public string Climate { get; set; } = string.Empty;
        public List<string> Flora { get; set; } = new List<string>();
        public List<string> Fauna { get; set; } = new List<string>();
        public List<string> Resources { get; set; } = new List<string>();
        public Dictionary<string, object> Properties { get; set; } = new Dictionary<string, object>();
    }

    [Serializable]
    public class BiomeModel
    {
        public string Id { get; set; } = string.Empty;
        public string Name { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
        public BiomeConfigDTO Config { get; set; } = new BiomeConfigDTO();
        public bool IsActive { get; set; } = true;
        public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    }

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

        // Legacy compatibility
        public string id => ContinentId;
        public string name => Name;
        public string description => Metadata.TryGetValue("description", out var desc) ? desc.ToString() : "";
        public List<Vector2> boundaryData => new List<Vector2>();
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
        public float BiomeDiversity { get; set; } = 0.5f;
        public float TemperatureVariation { get; set; } = 0.3f;
        public float HumidityVariation { get; set; } = 0.3f;
        public float ElevationVariation { get; set; } = 0.4f;
        public Dictionary<string, float> BiomeWeights { get; set; } = new Dictionary<string, float>();
    }

    [Serializable]
    public class SettlementGenerationParams
    {
        public float SettlementDensity { get; set; } = 0.3f;
        public float ResourceDensity { get; set; } = 0.4f;
        public float TradeRouteFrequency { get; set; } = 0.2f;
        public Dictionary<string, float> SettlementTypes { get; set; } = new Dictionary<string, float>();
    }

    [Serializable]
    public class WorldGenerationProgress
    {
        public string GenerationId { get; set; } = string.Empty;
        public string Stage { get; set; } = string.Empty;
        public float OverallProgress { get; set; } = 0f;
        public float StageProgress { get; set; } = 0f;
        public string CurrentTask { get; set; } = string.Empty;
        public DateTime StartTime { get; set; } = DateTime.UtcNow;
        public TimeSpan ElapsedTime { get; set; } = TimeSpan.Zero;
        public TimeSpan EstimatedTimeRemaining { get; set; } = TimeSpan.Zero;
        public Dictionary<string, object> StageData { get; set; } = new Dictionary<string, object>();
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

        // Legacy compatibility
        public Dictionary<string, object> parameters => new Dictionary<string, object>();
        public string name => Name;
        public string description => Description;
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

        // Legacy compatibility
        public string worldName => GeneratedContinent?.Name ?? "Unknown World";
    }

    [Serializable]
    public class RegionGenerationParams
    {
        public int NumRegions { get; set; } = 60;
        public BiomeGenerationParams BiomeParams { get; set; } = new BiomeGenerationParams();
        public SettlementGenerationParams SettlementParams { get; set; } = new SettlementGenerationParams();
        public Dictionary<string, object> CustomParams { get; set; } = new Dictionary<string, object>();
    }

    [Serializable]
    public class RegionGenerationResult
    {
        public string RegionId { get; set; } = string.Empty;
        public RegionDTO Region { get; set; }
        public bool Success { get; set; } = false;
        public string ErrorMessage { get; set; } = string.Empty;
        public Dictionary<string, object> GenerationData { get; set; } = new Dictionary<string, object>();
    }

    /// <summary>
    /// Coordinate schema for world generation
    /// </summary>
    [Serializable]
    public class CoordinateSchemaDTO
    {
        public string Id { get; set; } = string.Empty;
        public string Name { get; set; } = string.Empty;
        public int Width { get; set; } = 100;
        public int Height { get; set; } = 100;
        public Vector2 Origin { get; set; } = Vector2.zero;
        public float Scale { get; set; } = 1.0f;
        public string CoordinateSystem { get; set; } = "cartesian";
    }

    /// <summary>
    /// Template generation config
    /// </summary>
    [Serializable]
    public class TemplateGenerationConfig
    {
        public string Id { get; set; } = string.Empty;
        public string TemplateName { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
        public Dictionary<string, object> Parameters { get; set; } = new Dictionary<string, object>();
        public CoordinateSchemaDTO CoordinateSchema { get; set; } = new CoordinateSchemaDTO();
        public List<BiomeConfigDTO> Biomes { get; set; } = new List<BiomeConfigDTO>();
        public Dictionary<string, float> GenerationWeights { get; set; } = new Dictionary<string, float>();
    }

    /// <summary>
    /// Continent data transfer object
    /// </summary>
    [Serializable]
    public class ContinentDTO
    {
        public string Id { get; set; } = string.Empty;
        public string Name { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
        public Vector2 Position { get; set; } = Vector2.zero;
        public Vector2 Size { get; set; } = Vector2.one;
        public List<string> RegionIds { get; set; } = new List<string>();
        public Dictionary<string, object> Properties { get; set; } = new Dictionary<string, object>();
    }

    /// <summary>
    /// Region data transfer object (simplified version for WorldGeneration)
    /// </summary>
    [Serializable]
    public class RegionDTO
    {
        public string Id { get; set; } = string.Empty;
        public string Name { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
        public Vector2 Position { get; set; } = Vector2.zero;
        public Vector2 Size { get; set; } = Vector2.one;
        public string BiomeId { get; set; } = string.Empty;
        public string ContinentId { get; set; } = string.Empty;
        public Dictionary<string, object> Properties { get; set; } = new Dictionary<string, object>();
    }

    /// <summary>
    /// Template generation request
    /// </summary>
    [Serializable]
    public class TemplateGenerationRequest
    {
        public string Name { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
        public int RegionCount { get; set; } = 10;
        public List<string> BiomeTypes { get; set; } = new List<string>();
        public Dictionary<string, object> Parameters { get; set; } = new Dictionary<string, object>();
    }

    /// <summary>
    /// Configuration for continent generation
    /// </summary>
    [Serializable]
    public class ContinentGenerationConfig
    {
        public int ContinentCount { get; set; } = 3;
        public Vector2 SizeRange { get; set; } = new Vector2(100, 500);
        public float SeparationDistance { get; set; } = 50f;
        public Dictionary<string, object> TerrainParams { get; set; } = new Dictionary<string, object>();
        public Dictionary<string, object> ClimateParams { get; set; } = new Dictionary<string, object>();
        public string GenerationType { get; set; } = "procedural";
    }

    /// <summary>
    /// Configuration for biome generation
    /// </summary>
    [Serializable]
    public class BiomeGenerationConfig
    {
        public string ContinentId { get; set; } = string.Empty;
        public List<string> BiomeTypes { get; set; } = new List<string>();
        public Dictionary<string, float> BiomeWeights { get; set; } = new Dictionary<string, float>();
        public float TemperatureVariance { get; set; } = 0.2f;
        public float HumidityVariance { get; set; } = 0.2f;
        public float ElevationInfluence { get; set; } = 0.3f;
        public int Seed { get; set; } = 42;
    }

    /// <summary>
    /// Configuration for region generation
    /// </summary>
    [Serializable]
    public class RegionGenerationConfig
    {
        public int RegionCount { get; set; } = 20;
        public Dictionary<string, float> BiomeDistribution { get; set; } = new Dictionary<string, float>();
        public float SizeVariance { get; set; } = 0.3f;
        public float ConnectivityFactor { get; set; } = 0.7f;
        public Dictionary<string, object> ElevationParams { get; set; } = new Dictionary<string, object>();
        public Dictionary<string, object> ClimateParams { get; set; } = new Dictionary<string, object>();
        public Dictionary<string, object> ResourceParams { get; set; } = new Dictionary<string, object>();
        public Dictionary<string, object> SettlementParams { get; set; } = new Dictionary<string, object>();
    }
} 