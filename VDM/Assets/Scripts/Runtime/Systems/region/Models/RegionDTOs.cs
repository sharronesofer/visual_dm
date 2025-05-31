using System;
using System.Collections.Generic;
using Newtonsoft.Json;

namespace VDM.Systems.Region.Models
{
    /// <summary>
    /// Region Data Transfer Object
    /// </summary>
    [Serializable]
    public class RegionDTO
    {
        [JsonProperty("id")]
        public string Id { get; set; } = string.Empty;

        [JsonProperty("name")]
        public string Name { get; set; } = string.Empty;

        [JsonProperty("type")]
        public RegionTypeDTO Type { get; set; } = new RegionTypeDTO();

        [JsonProperty("coordinates")]
        public CoordinateSchemaDTO Coordinates { get; set; } = new CoordinateSchemaDTO();

        [JsonProperty("biome")]
        public string Biome { get; set; } = string.Empty;

        [JsonProperty("climate")]
        public string Climate { get; set; } = string.Empty;

        [JsonProperty("population")]
        public int Population { get; set; } = 0;

        [JsonProperty("controlling_faction_id")]
        public string ControllingFactionId { get; set; } = string.Empty;

        [JsonProperty("description")]
        public string Description { get; set; } = string.Empty;

        [JsonProperty("resources")]
        public Dictionary<string, object> Resources { get; set; } = new Dictionary<string, object>();
    }

    /// <summary>
    /// Region Type Data Transfer Object
    /// </summary>
    [Serializable]
    public class RegionTypeDTO
    {
        [JsonProperty("id")]
        public string Id { get; set; } = string.Empty;

        [JsonProperty("name")]
        public string Name { get; set; } = string.Empty;

        [JsonProperty("category")]
        public string Category { get; set; } = string.Empty;

        [JsonProperty("description")]
        public string Description { get; set; } = string.Empty;
    }

    /// <summary>
    /// Coordinate Schema Data Transfer Object
    /// </summary>
    [Serializable]
    public class CoordinateSchemaDTO
    {
        [JsonProperty("x")]
        public float X { get; set; } = 0f;

        [JsonProperty("y")]
        public float Y { get; set; } = 0f;

        [JsonProperty("z")]
        public float Z { get; set; } = 0f;

        [JsonProperty("latitude")]
        public double Latitude { get; set; } = 0.0;

        [JsonProperty("longitude")]
        public double Longitude { get; set; } = 0.0;
    }

    /// <summary>
    /// Region Map Data Transfer Object
    /// </summary>
    [Serializable]
    public class RegionMapDTO
    {
        [JsonProperty("region_id")]
        public string RegionId { get; set; } = string.Empty;

        [JsonProperty("map_data")]
        public Dictionary<string, object> MapData { get; set; } = new Dictionary<string, object>();

        [JsonProperty("tiles")]
        public List<TileDTO> Tiles { get; set; } = new List<TileDTO>();

        [JsonProperty("rivers")]
        public List<RiverDTO> Rivers { get; set; } = new List<RiverDTO>();

        [JsonProperty("roads")]
        public List<RoadDTO> Roads { get; set; } = new List<RoadDTO>();

        [JsonProperty("boundaries")]
        public CoordinateSchemaDTO[] Boundaries { get; set; } = new CoordinateSchemaDTO[0];
    }

    /// <summary>
    /// Tile Data Transfer Object
    /// </summary>
    [Serializable]
    public class TileDTO
    {
        [JsonProperty("id")]
        public string Id { get; set; } = string.Empty;

        [JsonProperty("coordinates")]
        public CoordinateSchemaDTO Coordinates { get; set; } = new CoordinateSchemaDTO();

        [JsonProperty("biome")]
        public string Biome { get; set; } = string.Empty;

        [JsonProperty("elevation")]
        public float Elevation { get; set; } = 0f;

        [JsonProperty("terrain")]
        public string Terrain { get; set; } = string.Empty;

        [JsonProperty("resources")]
        public Dictionary<string, object> Resources { get; set; } = new Dictionary<string, object>();
    }

    /// <summary>
    /// River Data Transfer Object
    /// </summary>
    [Serializable]
    public class RiverDTO
    {
        [JsonProperty("id")]
        public string Id { get; set; } = string.Empty;

        [JsonProperty("name")]
        public string Name { get; set; } = string.Empty;

        [JsonProperty("source")]
        public CoordinateSchemaDTO Source { get; set; } = new CoordinateSchemaDTO();

        [JsonProperty("mouth")]
        public CoordinateSchemaDTO Mouth { get; set; } = new CoordinateSchemaDTO();

        [JsonProperty("path")]
        public List<CoordinateSchemaDTO> Path { get; set; } = new List<CoordinateSchemaDTO>();

        [JsonProperty("width")]
        public float Width { get; set; } = 1f;

        [JsonProperty("depth")]
        public float Depth { get; set; } = 1f;
    }

    /// <summary>
    /// Road Data Transfer Object
    /// </summary>
    [Serializable]
    public class RoadDTO
    {
        [JsonProperty("id")]
        public string Id { get; set; } = string.Empty;

        [JsonProperty("name")]
        public string Name { get; set; } = string.Empty;

        [JsonProperty("type")]
        public string Type { get; set; } = "dirt_road";

        [JsonProperty("start")]
        public CoordinateSchemaDTO Start { get; set; } = new CoordinateSchemaDTO();

        [JsonProperty("end")]
        public CoordinateSchemaDTO End { get; set; } = new CoordinateSchemaDTO();

        [JsonProperty("path")]
        public List<CoordinateSchemaDTO> Path { get; set; } = new List<CoordinateSchemaDTO>();

        [JsonProperty("width")]
        public float Width { get; set; } = 3f;

        [JsonProperty("condition")]
        public string Condition { get; set; } = "good";
    }
} 