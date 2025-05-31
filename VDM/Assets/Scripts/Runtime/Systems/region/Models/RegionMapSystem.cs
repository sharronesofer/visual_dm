using System;
using System.Collections.Generic;
using UnityEngine;
using VDM.Systems.Region.Models;
using VDM.Systems.Region.Services;

namespace VDM.Systems.Region.Integration
{
    /// <summary>
    /// Unity integration for region map management
    /// </summary>
    public class RegionMapSystem : MonoBehaviour
    {
        [Header("Map Configuration")]
        [SerializeField] private bool enableAutoRefresh = true;
        [SerializeField] private float refreshInterval = 30f;

        // Services
        private RegionService regionService;
        
        // State
        private Dictionary<string, RegionMapDTO> cachedMaps = new Dictionary<string, RegionMapDTO>();
        private float lastRefreshTime;

        // Events
        public event Action<string, RegionMapDTO> OnMapLoaded;
        public event Action<string> OnMapLoadFailed;

        private void Awake()
        {
            regionService = new RegionService();
        }

        private void Update()
        {
            if (enableAutoRefresh && Time.time - lastRefreshTime > refreshInterval)
            {
                RefreshCachedMaps();
                lastRefreshTime = Time.time;
            }
        }

        /// <summary>
        /// Load map for specific region
        /// </summary>
        public async void LoadRegionMap(string regionId)
        {
            try
            {
                var map = await regionService.GetRegionMapAsync(regionId);
                if (map != null)
                {
                    cachedMaps[regionId] = map;
                    OnMapLoaded?.Invoke(regionId, map);
                }
                else
                {
                    OnMapLoadFailed?.Invoke(regionId);
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to load map for region {regionId}: {ex.Message}");
                OnMapLoadFailed?.Invoke(regionId);
            }
        }

        /// <summary>
        /// Get cached map for region
        /// </summary>
        public RegionMapDTO GetCachedMap(string regionId)
        {
            return cachedMaps.TryGetValue(regionId, out var map) ? map : null;
        }

        /// <summary>
        /// Refresh all cached maps
        /// </summary>
        private async void RefreshCachedMaps()
        {
            var regionIds = new List<string>(cachedMaps.Keys);
            foreach (var regionId in regionIds)
            {
                try
                {
                    var map = await regionService.GetRegionMapAsync(regionId);
                    if (map != null)
                    {
                        cachedMaps[regionId] = map;
                    }
                }
                catch (Exception ex)
                {
                    Debug.LogError($"Failed to refresh map for region {regionId}: {ex.Message}");
                }
            }
        }

        /// <summary>
        /// Clear all cached maps
        /// </summary>
        public void ClearCache()
        {
            cachedMaps.Clear();
        }
    }
} 