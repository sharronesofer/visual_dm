using System.Collections.Generic;
using System;
using UnityEngine;

namespace VDM.Runtime.Region.Models
{
    /// <summary>
    /// Models for Region system based on backend/systems/region structure
    /// </summary>

    [Serializable]
    public class RegionModel
    {
        public string Id { get; set; } = string.Empty;
        public string Name { get; set; } = string.Empty;
        public string ContinentId { get; set; } = string.Empty;
        public CoordinateSchemaDTO Coordinates { get; set; } = new CoordinateSchemaDTO();
        public RegionTypeDTO BiomeType { get; set; } = RegionTypeDTO.Plains;
        public EnvironmentalProfile Environment { get; set; } = new EnvironmentalProfile();
        public GeographicData Geography { get; set; } = new GeographicData();
        public List<string> ResourceIds { get; set; } = new List<string>();
        public List<string> FeatureIds { get; set; } = new List<string>();
        public List<string> PoiIds { get; set; } = new List<string>();
        public PoliticalData Politics { get; set; } = new PoliticalData();
        public EconomicData Economics { get; set; } = new EconomicData();
        public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
        public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;
        public Dictionary<string, object> Metadata { get; set; } = new Dictionary<string, object>();
    }

    [Serializable]
    public class EnvironmentalProfile
    {
        public float Temperature { get; set; } = 0.5f; // 0-1 scale
        public float Humidity { get; set; } = 0.5f; // 0-1 scale
        public float Elevation { get; set; } = 0.5f; // 0-1 scale
        public float Ruggedness { get; set; } = 0.5f; // 0-1 scale
        public WeatherPattern Weather { get; set; } = new WeatherPattern();
        public List<string> EnvironmentalFeatures { get; set; } = new List<string>();
    }

    [Serializable]
    public class WeatherPattern
    {
        public string CurrentWeather { get; set; } = "Clear";
        public float Temperature { get; set; } = 20.0f; // Celsius
        public float Precipitation { get; set; } = 0.0f; // mm/hour
        public float WindSpeed { get; set; } = 5.0f; // km/h
        public string WindDirection { get; set; } = "N";
        public float Visibility { get; set; } = 10.0f; // km
        public List<WeatherForecast> Forecast { get; set; } = new List<WeatherForecast>();
    }

    [Serializable]
    public class WeatherForecast
    {
        public DateTime Date { get; set; } = DateTime.UtcNow;
        public string Condition { get; set; } = "Clear";
        public float HighTemp { get; set; } = 25.0f;
        public float LowTemp { get; set; } = 15.0f;
        public float PrecipitationChance { get; set; } = 0.0f;
    }

    [Serializable]
    public class GeographicData
    {
        public float Latitude { get; set; } = 0.0f;
        public float Longitude { get; set; } = 0.0f;
        public float Area { get; set; } = 39.0f; // sq km
        public List<string> AdjacentRegionIds { get; set; } = new List<string>();
        public List<RiverDTO> Rivers { get; set; } = new List<RiverDTO>();
        public List<RoadDTO> Roads { get; set; } = new List<RoadDTO>();
        public List<LandmarkData> Landmarks { get; set; } = new List<LandmarkData>();
    }

    [Serializable]
    public class LandmarkData
    {
        public string Id { get; set; } = string.Empty;
        public string Name { get; set; } = string.Empty;
        public string Type { get; set; } = string.Empty;
        public CoordinateSchemaDTO Position { get; set; } = new CoordinateSchemaDTO();
        public string Description { get; set; } = string.Empty;
        public bool IsVisible { get; set; } = true;
        public Dictionary<string, object> Properties { get; set; } = new Dictionary<string, object>();
    }

    [Serializable]
    public class PoliticalData
    {
        public string ControllingFactionId { get; set; } = string.Empty;
        public List<string> InfluencingFactionIds { get; set; } = new List<string>();
        public float StabilityIndex { get; set; } = 0.5f; // 0-1 scale
        public string GovernmentType { get; set; } = "None";
        public List<PoliticalEvent> RecentEvents { get; set; } = new List<PoliticalEvent>();
        public Dictionary<string, float> FactionInfluence { get; set; } = new Dictionary<string, float>();
    }

    [Serializable]
    public class PoliticalEvent
    {
        public string Id { get; set; } = string.Empty;
        public string Type { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
        public DateTime OccurredAt { get; set; } = DateTime.UtcNow;
        public List<string> InvolvedFactionIds { get; set; } = new List<string>();
        public float ImpactSeverity { get; set; } = 0.0f; // -1 to 1 scale
    }

    [Serializable]
    public class EconomicData
    {
        public float WealthLevel { get; set; } = 0.5f; // 0-1 scale
        public float TradeActivity { get; set; } = 0.5f; // 0-1 scale
        public List<string> PrimaryIndustries { get; set; } = new List<string>();
        public List<string> TradeRouteIds { get; set; } = new List<string>();
        public Dictionary<string, float> ResourceProduction { get; set; } = new Dictionary<string, float>();
        public Dictionary<string, float> ResourceDemand { get; set; } = new Dictionary<string, float>();
        public List<MarketData> Markets { get; set; } = new List<MarketData>();
    }

    [Serializable]
    public class MarketData
    {
        public string Id { get; set; } = string.Empty;
        public string Name { get; set; } = string.Empty;
        public string Type { get; set; } = "General";
        public CoordinateSchemaDTO Location { get; set; } = new CoordinateSchemaDTO();
        public Dictionary<string, float> ItemPrices { get; set; } = new Dictionary<string, float>();
        public float ActivityLevel { get; set; } = 0.5f; // 0-1 scale
    }

    [Serializable]
    public class RegionQueryParams
    {
        public string ContinentId { get; set; } = string.Empty;
        public RegionTypeDTO? BiomeType { get; set; }
        public float? MinTemperature { get; set; }
        public float? MaxTemperature { get; set; }
        public float? MinElevation { get; set; }
        public float? MaxElevation { get; set; }
        public string ControllingFactionId { get; set; } = string.Empty;
        public bool? HasResources { get; set; }
        public int? MinPopulation { get; set; }
        public int? MaxPopulation { get; set; }
        public int Page { get; set; } = 1;
        public int PageSize { get; set; } = 50;
    }

    [Serializable]
    public class RegionUpdateRequest
    {
        public string Name { get; set; }
        public string Description { get; set; }
        public EnvironmentalProfile Environment { get; set; }
        public PoliticalData Politics { get; set; }
        public EconomicData Economics { get; set; }
        public Dictionary<string, object> Metadata { get; set; }
    }

    [Serializable]
    public class RegionAnalytics
    {
        public string RegionId { get; set; } = string.Empty;
        public int TotalPopulation { get; set; } = 0;
        public int NumberOfSettlements { get; set; } = 0;
        public int NumberOfPOIs { get; set; } = 0;
        public float AverageWealthLevel { get; set; } = 0.0f;
        public float StabilityTrend { get; set; } = 0.0f;
        public float EconomicGrowth { get; set; } = 0.0f;
        public Dictionary<string, int> ResourceCounts { get; set; } = new Dictionary<string, int>();
        public Dictionary<string, float> FactionPresence { get; set; } = new Dictionary<string, float>();
        public DateTime LastUpdated { get; set; } = DateTime.UtcNow;
    }
} 