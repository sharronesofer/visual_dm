using System;
using System.Collections.Generic;

namespace VDM.DTOs.Common
{
    [Serializable]
    public class WorldGenerationConfig
    {
        public int seed;
        public string worldType;
        public Dictionary<string, object> parameters = new Dictionary<string, object>();
    }

    [Serializable]
    public class ContinentModel
    {
        public string id;
        public string name;
        public string description;
        public List<string> regionIds = new List<string>();
    }

    [Serializable]
    public class ReligionDTO
    {
        public string id;
        public string name;
        public string description;
        public List<string> deities = new List<string>();
    }

    [Serializable]
    public class PerformanceData
    {
        public float frameRate;
        public long memoryUsage;
        public Dictionary<string, object> metrics = new Dictionary<string, object>();
    }

    [Serializable]
    public class SessionData
    {
        public string sessionId;
        public string userId;
        public DateTime startTime;
        public Dictionary<string, object> sessionInfo = new Dictionary<string, object>();
    }

    [Serializable]
    public class DatabaseConfig
    {
        public string connectionString;
        public string databaseType;
        public Dictionary<string, string> settings = new Dictionary<string, string>();
    }

    [Serializable]
    public class RegionWeatherData
    {
        public string regionId;
        public string weatherType;
        public float temperature;
        public Dictionary<string, object> conditions = new Dictionary<string, object>();
    }

    [Serializable]
    public class InventoryItemData
    {
        public string itemId;
        public string itemType;
        public int quantity;
        public Dictionary<string, object> properties = new Dictionary<string, object>();
    }

    [Serializable]
    public class EconomyData
    {
        public string currencyType;
        public float exchangeRate;
        public Dictionary<string, float> prices = new Dictionary<string, float>();
    }

    [Serializable]
    public class FactionData
    {
        public string factionId;
        public string name;
        public string description;
        public Dictionary<string, object> relations = new Dictionary<string, object>();
    }
} 