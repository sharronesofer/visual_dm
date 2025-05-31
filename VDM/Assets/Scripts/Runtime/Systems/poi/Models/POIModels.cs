using System;
using System.Collections.Generic;
using Newtonsoft.Json;

namespace VDM.Systems.Poi.Models
{
    /// <summary>
    /// Point of Interest model for Unity frontend
    /// </summary>
    [Serializable]
    public class POIModel
    {
        [JsonProperty("id")]
        public string Id { get; set; } = string.Empty;

        [JsonProperty("name")]
        public string Name { get; set; } = string.Empty;

        [JsonProperty("type")]
        public string Type { get; set; } = string.Empty;

        [JsonProperty("coordinates")]
        public float[] Coordinates { get; set; } = new float[2];

        [JsonProperty("region_id")]
        public string RegionId { get; set; } = string.Empty;

        [JsonProperty("description")]
        public string Description { get; set; } = string.Empty;

        [JsonProperty("state")]
        public string State { get; set; } = "active";

        [JsonProperty("population")]
        public int Population { get; set; } = 0;

        [JsonProperty("faction_id")]
        public string FactionId { get; set; } = string.Empty;

        [JsonProperty("resources")]
        public Dictionary<string, object> Resources { get; set; } = new Dictionary<string, object>();

        [JsonProperty("metadata")]
        public Dictionary<string, object> Metadata { get; set; } = new Dictionary<string, object>();
    }

    /// <summary>
    /// Settlement model for Unity frontend
    /// </summary>
    [Serializable]
    public class SettlementModel
    {
        [JsonProperty("id")]
        public string Id { get; set; } = string.Empty;

        [JsonProperty("name")]
        public string Name { get; set; } = string.Empty;

        [JsonProperty("type")]
        public string Type { get; set; } = "village";

        [JsonProperty("coordinates")]
        public float[] Coordinates { get; set; } = new float[2];

        [JsonProperty("region_id")]
        public string RegionId { get; set; } = string.Empty;

        [JsonProperty("population")]
        public int Population { get; set; } = 0;

        [JsonProperty("prosperity")]
        public string Prosperity { get; set; } = "average";

        [JsonProperty("primary_industry")]
        public string PrimaryIndustry { get; set; } = string.Empty;

        [JsonProperty("faction_control")]
        public string FactionControl { get; set; } = string.Empty;

        [JsonProperty("state")]
        public string State { get; set; } = "normal";

        [JsonProperty("notable_features")]
        public List<string> NotableFeatures { get; set; } = new List<string>();

        [JsonProperty("description")]
        public string Description { get; set; } = string.Empty;

        [JsonProperty("resources")]
        public Dictionary<string, object> Resources { get; set; } = new Dictionary<string, object>();

        [JsonProperty("points_of_interest")]
        public List<POIModel> PointsOfInterest { get; set; } = new List<POIModel>();

        [JsonProperty("metadata")]
        public Dictionary<string, object> Metadata { get; set; } = new Dictionary<string, object>();
    }
} 