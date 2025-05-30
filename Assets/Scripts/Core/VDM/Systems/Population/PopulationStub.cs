using System;
using System.Collections.Generic;
using UnityEngine;

namespace VDM.Systems.Population
{
    /// <summary>
    /// Population system components for VDM
    /// </summary>
    
    public class PopulationManager : MonoBehaviour
    {
        [Header("Population Settings")]
        public int maxPopulation = 1000;
        public float growthRate = 0.02f;
        
        private List<PopulationData> _populationGroups = new List<PopulationData>();
        private bool _isInitialized = false;
        
        public bool IsInitialized => _isInitialized;
        public int TotalPopulation => GetTotalPopulation();
        public List<PopulationData> PopulationGroups => new List<PopulationData>(_populationGroups);
        
        void Start()
        {
            Initialize();
        }
        
        public void Initialize()
        {
            if (_isInitialized) return;
            
            _populationGroups.Clear();
            _isInitialized = true;
            
            Debug.Log("[PopulationManager] Population system initialized");
        }
        
        public void Shutdown()
        {
            _populationGroups.Clear();
            _isInitialized = false;
            
            Debug.Log("[PopulationManager] Population system shutdown");
        }
        
        public PopulationData CreatePopulationGroup(string regionId, string groupName, int initialSize)
        {
            if (!_isInitialized)
            {
                Debug.LogError("[PopulationManager] Cannot create population group - system not initialized");
                return null;
            }
            
            var populationData = new PopulationData
            {
                RegionId = regionId,
                GroupName = groupName,
                Size = initialSize,
                GrowthRate = growthRate,
                LastUpdated = DateTime.UtcNow
            };
            
            _populationGroups.Add(populationData);
            
            Debug.Log($"[PopulationManager] Created population group '{groupName}' in region '{regionId}' with {initialSize} individuals");
            
            return populationData;
        }
        
        public PopulationData GetPopulationGroup(string regionId, string groupName)
        {
            return _populationGroups.Find(p => p.RegionId == regionId && p.GroupName == groupName);
        }
        
        public List<PopulationData> GetRegionPopulation(string regionId)
        {
            return _populationGroups.FindAll(p => p.RegionId == regionId);
        }
        
        public void UpdatePopulation()
        {
            if (!_isInitialized) return;
            
            var currentTime = DateTime.UtcNow;
            
            foreach (var group in _populationGroups)
            {
                // Simple population growth calculation
                var timeDelta = (currentTime - group.LastUpdated).TotalDays;
                if (timeDelta > 0)
                {
                    var growth = Mathf.FloorToInt(group.Size * group.GrowthRate * (float)timeDelta);
                    group.Size = Mathf.Min(group.Size + growth, maxPopulation);
                    group.LastUpdated = currentTime;
                }
            }
        }
        
        public void RemovePopulationGroup(string regionId, string groupName)
        {
            var group = GetPopulationGroup(regionId, groupName);
            if (group != null)
            {
                _populationGroups.Remove(group);
                Debug.Log($"[PopulationManager] Removed population group '{groupName}' from region '{regionId}'");
            }
        }
        
        public void ClearAllPopulation()
        {
            _populationGroups.Clear();
            Debug.Log("[PopulationManager] Cleared all population data");
        }
        
        private int GetTotalPopulation()
        {
            int total = 0;
            foreach (var group in _populationGroups)
            {
                total += group.Size;
            }
            return total;
        }
        
        public PopulationStats GetPopulationStats()
        {
            return new PopulationStats
            {
                TotalPopulation = TotalPopulation,
                TotalGroups = _populationGroups.Count,
                AverageGroupSize = _populationGroups.Count > 0 ? TotalPopulation / _populationGroups.Count : 0,
                MaxPopulation = maxPopulation,
                GrowthRate = growthRate
            };
        }
    }
    
    [Serializable]
    public class PopulationData
    {
        public string RegionId;
        public string GroupName;
        public int Size;
        public float GrowthRate;
        public DateTime LastUpdated;
        public Dictionary<string, object> Properties = new Dictionary<string, object>();
        
        public PopulationData()
        {
            LastUpdated = DateTime.UtcNow;
        }
    }
    
    [Serializable]
    public class PopulationStats
    {
        public int TotalPopulation;
        public int TotalGroups;
        public int AverageGroupSize;
        public int MaxPopulation;
        public float GrowthRate;
    }
} 