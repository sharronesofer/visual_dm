using System;
using System.Collections.Generic;

namespace Visual_DM.WorldState
{
    // Represents a region in the game world
    public class Region
    {
        public string RegionId { get; private set; }
        public string Name { get; private set; }
        // Add more region-specific properties as needed

        public Region(string regionId, string name)
        {
            RegionId = regionId;
            Name = name;
        }
    }

    // Holds world state for a specific region, with inheritance from global state
    public class RegionWorldState
    {
        public Region Region { get; private set; }
        private readonly Dictionary<string, object> _regionalProperties = new Dictionary<string, object>();
        private readonly WorldStateManager _globalState;

        public RegionWorldState(Region region, WorldStateManager globalState)
        {
            Region = region;
            _globalState = globalState;
        }

        // Set a region-specific property (overrides global)
        public void SetProperty<T>(string key, T value)
        {
            _regionalProperties[key] = value;
        }

        // Get a property, falling back to global if not set regionally
        public T GetProperty<T>(string key)
        {
            if (_regionalProperties.TryGetValue(key, out var value) && value is T typedValue)
                return typedValue;
            // Fallback to global state if available
            var globalProp = _globalState.GetProperty<T>(key);
            return globalProp;
        }

        // Remove a region-specific override
        public void RemoveProperty(string key)
        {
            _regionalProperties.Remove(key);
        }
    }

    // Extension to WorldStateManager for hierarchical/global property access
    public partial class WorldStateManager
    {
        private readonly Dictionary<string, object> _globalProperties = new Dictionary<string, object>();
        private readonly Dictionary<string, RegionWorldState> _regions = new Dictionary<string, RegionWorldState>();

        // Set a global property
        public void SetProperty<T>(string key, T value)
        {
            _globalProperties[key] = value;
        }

        // Get a global property
        public T GetProperty<T>(string key)
        {
            if (_globalProperties.TryGetValue(key, out var value) && value is T typedValue)
                return typedValue;
            return default;
        }

        // Register a region
        public RegionWorldState RegisterRegion(Region region)
        {
            if (!_regions.ContainsKey(region.RegionId))
            {
                var regionState = new RegionWorldState(region, this);
                _regions[region.RegionId] = regionState;
            }
            return _regions[region.RegionId];
        }

        // Get a region's world state
        public RegionWorldState GetRegionWorldState(string regionId)
        {
            _regions.TryGetValue(regionId, out var regionState);
            return regionState;
        }
    }
}