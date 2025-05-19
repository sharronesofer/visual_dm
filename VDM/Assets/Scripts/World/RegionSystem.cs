using System;
using System.Collections.Generic;
using UnityEngine;
using VisualDM.Systems.Narrative;

namespace VisualDM.World
{
    /// <summary>
    /// Represents a geographic region in the game world, including boundaries, dominant factions, resources, culture, and dynamic state.
    /// Supports association with multiple Regional Arcs for narrative integration.
    /// </summary>
    [Serializable]
    public class Region
    {
        /// <summary>Unique region identifier (GUID).</summary>
        public string Id { get; private set; }
        /// <summary>Human-readable region name.</summary>
        public string Name { get; set; }
        /// <summary>Type/category of the region (e.g., city, province, biome).</summary>
        public string Type { get; set; }
        /// <summary>2D boundary for the region (Rect).</summary>
        public Rect Boundary { get; set; }
        /// <summary>List of dominant faction IDs in the region.</summary>
        public List<string> DominantFactions { get; set; } = new();
        /// <summary>Resource type/quantity mapping for the region.</summary>
        public Dictionary<string, float> ResourceDistribution { get; set; } = new();
        /// <summary>Cultural attributes (arbitrary key-value pairs).</summary>
        public Dictionary<string, object> CulturalAttributes { get; set; } = new();
        /// <summary>Dynamic state dictionary for region-specific state.</summary>
        public Dictionary<string, object> State { get; set; } = new();
        /// <summary>List of associated RegionalArc IDs.</summary>
        public List<string> AssociatedArcIds { get; set; } = new();

        /// <summary>
        /// Constructs a new Region with the given name, type, and boundary.
        /// </summary>
        public Region(string name, string type, Rect boundary)
        {
            Id = Guid.NewGuid().ToString();
            Name = name;
            Type = type;
            Boundary = boundary;
        }

        /// <summary>
        /// Checks if a given position is within the region's boundary.
        /// </summary>
        public bool Contains(Vector2 position) => Boundary.Contains(position);
    }

    /// <summary>
    /// Manages all regions in the world and their association with Regional Arcs.
    /// Provides bidirectional mapping and query methods for region-arc relationships.
    /// </summary>
    public class RegionSystem
    {
        private Dictionary<string, Region> regions = new();
        private Dictionary<string, List<string>> arcToRegion = new(); // arcId -> regionIds
        private Dictionary<string, List<string>> regionToArc = new(); // regionId -> arcIds

        /// <summary>
        /// Adds a region to the system.
        /// </summary>
        public void AddRegion(Region region)
        {
            regions[region.Id] = region;
            if (!regionToArc.ContainsKey(region.Id))
                regionToArc[region.Id] = new List<string>();
        }

        /// <summary>
        /// Associates a RegionalArc with a Region (bidirectional).
        /// </summary>
        public void AssociateArcWithRegion(string arcId, string regionId)
        {
            if (!arcToRegion.ContainsKey(arcId))
                arcToRegion[arcId] = new List<string>();
            if (!regionToArc.ContainsKey(regionId))
                regionToArc[regionId] = new List<string>();
            if (!arcToRegion[arcId].Contains(regionId))
                arcToRegion[arcId].Add(regionId);
            if (!regionToArc[regionId].Contains(arcId))
                regionToArc[regionId].Add(arcId);
        }

        /// <summary>
        /// Gets all regions associated with a given arc ID.
        /// </summary>
        public List<Region> GetRegionsForArc(string arcId)
        {
            if (!arcToRegion.ContainsKey(arcId)) return new List<Region>();
            var ids = arcToRegion[arcId];
            var result = new List<Region>();
            foreach (var id in ids)
                if (regions.ContainsKey(id)) result.Add(regions[id]);
            return result;
        }

        /// <summary>
        /// Gets all RegionalArcs associated with a given region ID.
        /// </summary>
        public List<RegionalArc> GetArcsForRegion(string regionId, List<RegionalArc> allArcs)
        {
            if (!regionToArc.ContainsKey(regionId)) return new List<RegionalArc>();
            var arcIds = regionToArc[regionId];
            var result = new List<RegionalArc>();
            foreach (var arc in allArcs)
                if (arcIds.Contains(arc.Id)) result.Add(arc);
            return result;
        }

        /// <summary>
        /// Returns the first region containing the given position (supports overlapping regions).
        /// </summary>
        public Region GetRegionAtPosition(Vector2 position)
        {
            foreach (var region in regions.Values)
                if (region.Contains(position)) return region;
            return null;
        }

        /// <summary>
        /// Returns all regions containing the given position (for overlapping regions).
        /// </summary>
        public List<Region> GetAllRegionsAtPosition(Vector2 position)
        {
            var result = new List<Region>();
            foreach (var region in regions.Values)
                if (region.Contains(position)) result.Add(region);
            return result;
        }

        /// <summary>
        /// Returns all regions in the system.
        /// </summary>
        public IEnumerable<Region> GetAllRegions() => regions.Values;

        /// <summary>
        /// Serializes the region system to JSON for persistence.
        /// </summary>
        public string Serialize()
        {
            return JsonUtility.ToJson(new RegionSystemDTO(this));
        }
        /// <summary>
        /// Deserializes a region system from JSON.
        /// </summary>
        public static RegionSystem Deserialize(string json)
        {
            var dto = JsonUtility.FromJson<RegionSystemDTO>(json);
            return dto.ToRegionSystem();
        }

        // DTO for serialization
        [Serializable]
        private class RegionSystemDTO
        {
            public List<Region> Regions;
            public Dictionary<string, List<string>> ArcToRegion;
            public Dictionary<string, List<string>> RegionToArc;
            public RegionSystemDTO(RegionSystem sys)
            {
                Regions = new List<Region>(sys.regions.Values);
                ArcToRegion = sys.arcToRegion;
                RegionToArc = sys.regionToArc;
            }
            public RegionSystem ToRegionSystem()
            {
                var sys = new RegionSystem();
                foreach (var region in Regions)
                    sys.AddRegion(region);
                sys.arcToRegion = ArcToRegion;
                sys.regionToArc = RegionToArc;
                return sys;
            }
        }
    }
}