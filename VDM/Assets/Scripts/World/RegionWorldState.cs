using System;
using System.Collections.Generic;

namespace VisualDM.World
{
    /// <summary>
    /// Represents a region in the game world for world state tracking.
    /// Used by RegionWorldState and WorldStateManager for state persistence and access.
    /// </summary>
    public class Region
    {
        /// <summary>Unique region identifier.</summary>
        public string RegionId { get; private set; }
        /// <summary>Human-readable region name.</summary>
        public string Name { get; private set; }
        // Add more region-specific properties as needed

        public Region(string regionId, string name)
        {
            RegionId = regionId;
            Name = name;
        }
    }

    /// <summary>
    /// Holds world state for a specific region, with inheritance from global state.
    /// Allows region-specific overrides and fallback to global properties.
    /// </summary>
    public class RegionWorldState
    {
        /// <summary>The region this state belongs to.</summary>
        public Region Region { get; private set; }
        private readonly Dictionary<string, object> _regionalProperties = new Dictionary<string, object>();
        private readonly WorldStateManager _globalState;

        public RegionWorldState(Region region, WorldStateManager globalState)
        {
            Region = region;
            _globalState = globalState;
        }

        /// <summary>
        /// Set a region-specific property (overrides global).
        /// </summary>
        public void SetProperty<T>(string key, T value)
        {
            _regionalProperties[key] = value;
        }

        /// <summary>
        /// Get a property, falling back to global if not set regionally.
        /// </summary>
        public T GetProperty<T>(string key)
        {
            if (_regionalProperties.TryGetValue(key, out var value) && value is T typedValue)
                return typedValue;
            // Fallback to global state via WorldStateSystem
            var globalValue = WorldStateSystem.Instance.Get(key);
            if (globalValue is T tVal) return tVal;
            return default;
        }

        /// <summary>
        /// Remove a region-specific override.
        /// </summary>
        public void RemoveProperty(string key)
        {
            _regionalProperties.Remove(key);
        }
    }
}