using System;
using System.Collections;
using System.Collections.Generic;
using System.Threading.Tasks;
using UnityEngine;
using UnityEngine.UI;
using TMPro;
using VDM.Infrastructure.Core;
using VDM.DTOs.Common;
using VDM.Systems.Region.Models;
using VDM.Systems.Region.Services;

namespace VDM.Systems.Region.Integration
{
    /// <summary>
    /// Main controller for region systems
    /// Coordinates between different region subsystems
    /// </summary>
    public class RegionSystemController : MonoBehaviour
    {
        [Header("Region Management")]
        public bool autoInitialize = true;
        public RegionTypeDTO defaultBiome = RegionTypeDTO.Plains;
        
        [Header("System Components")]
        public RegionMapSystem mapSystem;
        
        private Dictionary<string, RegionDTO> _activeRegions = new Dictionary<string, RegionDTO>();
        private bool _isInitialized = false;

        void Start()
        {
            if (autoInitialize)
            {
                Initialize();
            }
        }

        public void Initialize()
        {
            if (_isInitialized)
            {
                Debug.LogWarning("RegionSystemController already initialized");
                return;
            }

            // Initialize map system if not already assigned
            if (mapSystem == null)
            {
                mapSystem = FindObjectOfType<RegionMapSystem>();
                if (mapSystem == null)
                {
                    GameObject mapSystemObj = new GameObject("RegionMapSystem");
                    mapSystemObj.transform.SetParent(transform);
                    mapSystem = mapSystemObj.AddComponent<RegionMapSystem>();
                }
            }

            _isInitialized = true;
            Debug.Log("RegionSystemController initialized successfully");
        }

        public RegionDTO CreateRegion(string regionId, string name, RegionTypeDTO biomeType)
        {
            if (string.IsNullOrEmpty(regionId))
            {
                Debug.LogError("Cannot create region with null or empty ID");
                return null;
            }

            if (_activeRegions.ContainsKey(regionId))
            {
                Debug.LogWarning($"Region with ID '{regionId}' already exists");
                return _activeRegions[regionId];
            }

            var region = new RegionDTO
            {
                RegionId = regionId,
                Name = name,
                BiomeType = biomeType,
                CreatedAt = DateTime.UtcNow,
                UpdatedAt = DateTime.UtcNow
            };

            _activeRegions[regionId] = region;

            // Generate map for the region
            if (mapSystem != null)
            {
                mapSystem.GenerateRegionMap(regionId, biomeType);
            }

            Debug.Log($"Created region '{name}' ({regionId}) with biome {biomeType}");
            return region;
        }

        public RegionDTO GetRegion(string regionId)
        {
            return _activeRegions.ContainsKey(regionId) ? _activeRegions[regionId] : null;
        }

        public List<RegionDTO> GetAllRegions()
        {
            return new List<RegionDTO>(_activeRegions.Values);
        }

        public bool RemoveRegion(string regionId)
        {
            if (_activeRegions.ContainsKey(regionId))
            {
                _activeRegions.Remove(regionId);
                Debug.Log($"Removed region {regionId}");
                return true;
            }
            return false;
        }

        public RegionMapDTO GetRegionMap(string regionId)
        {
            return mapSystem?.GetRegionMap(regionId);
        }

        public bool IsInitialized => _isInitialized;

        // Integration status check for other systems
        public string GetIntegrationStatus()
        {
            var status = _isInitialized ? "successful" : "failed";
            return $"RegionSystemController integration: {status}";
        }

        void OnValidate()
        {
            // Ensure we have required components
            if (mapSystem == null)
            {
                mapSystem = GetComponentInChildren<RegionMapSystem>();
            }
        }
    }
} 