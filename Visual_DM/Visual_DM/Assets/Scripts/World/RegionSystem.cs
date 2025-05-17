using System;
using System.Collections.Generic;
using UnityEngine;
using VisualDM.Narrative;

namespace VisualDM.World
{
    [Serializable]
    public class Region
    {
        public string Id { get; private set; }
        public string Name { get; set; }
        public string Type { get; set; } // e.g., city, province, biome
        public Rect Boundary { get; set; } // 2D boundary for region
        public List<string> DominantFactions { get; set; } = new();
        public Dictionary<string, float> ResourceDistribution { get; set; } = new();
        public Dictionary<string, object> CulturalAttributes { get; set; } = new();
        public Dictionary<string, object> State { get; set; } = new(); // Dynamic state
        public List<string> AssociatedArcIds { get; set; } = new(); // RegionalArc IDs

        public Region(string name, string type, Rect boundary)
        {
            Id = Guid.NewGuid().ToString();
            Name = name;
            Type = type;
            Boundary = boundary;
        }

        public bool Contains(Vector2 position) => Boundary.Contains(position);
    }

    public class RegionSystem
    {
        private Dictionary<string, Region> regions = new();
        private Dictionary<string, List<string>> arcToRegion = new(); // arcId -> regionIds
        private Dictionary<string, List<string>> regionToArc = new(); // regionId -> arcIds

        public void AddRegion(Region region)
        {
            regions[region.Id] = region;
            if (!regionToArc.ContainsKey(region.Id))
                regionToArc[region.Id] = new List<string>();
        }

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

        public List<Region> GetRegionsForArc(string arcId)
        {
            if (!arcToRegion.ContainsKey(arcId)) return new List<Region>();
            var ids = arcToRegion[arcId];
            var result = new List<Region>();
            foreach (var id in ids)
                if (regions.ContainsKey(id)) result.Add(regions[id]);
            return result;
        }

        public List<RegionalArc> GetArcsForRegion(string regionId, List<RegionalArc> allArcs)
        {
            if (!regionToArc.ContainsKey(regionId)) return new List<RegionalArc>();
            var arcIds = regionToArc[regionId];
            var result = new List<RegionalArc>();
            foreach (var arc in allArcs)
                if (arcIds.Contains(arc.Id)) result.Add(arc);
            return result;
        }

        public Region GetRegionAtPosition(Vector2 position)
        {
            // Returns the first region containing the position (supports overlapping regions)
            foreach (var region in regions.Values)
                if (region.Contains(position)) return region;
            return null;
        }

        public List<Region> GetAllRegionsAtPosition(Vector2 position)
        {
            var result = new List<Region>();
            foreach (var region in regions.Values)
                if (region.Contains(position)) result.Add(region);
            return result;
        }

        public IEnumerable<Region> GetAllRegions() => regions.Values;

        // Serialization/deserialization for persistence
        public string Serialize()
        {
            return JsonUtility.ToJson(new RegionSystemDTO(this));
        }
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