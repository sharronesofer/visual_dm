using System;
using System.Collections.Generic;
using UnityEngine;

namespace VDM.Systems.Population.Models
{
    /// <summary>
    /// Core population system models for Unity frontend
    /// Mirrors backend population system structure
    /// </summary>
    
    [Serializable]
    public class PopulationData
    {
        public string regionId;
        public int totalPopulation;
        public Dictionary<string, int> ageGroups;
        public Dictionary<string, int> occupations;
        public float growthRate;
        public float migrationRate;
    }
    
    [Serializable]
    public class DemographicInfo
    {
        public int children;
        public int adults;
        public int elderly;
        public float birthRate;
        public float deathRate;
        public float lifeExpectancy;
    }
    
    [Serializable]
    public class MigrationPattern
    {
        public string fromRegionId;
        public string toRegionId;
        public int migrantCount;
        public string reason;
        public float probability;
    }
    
    [Serializable]
    public class SettlementInfo
    {
        public string id;
        public string name;
        public Vector3 position;
        public int population;
        public string settlementType;
        public float prosperity;
        public List<string> resources;
    }
} 