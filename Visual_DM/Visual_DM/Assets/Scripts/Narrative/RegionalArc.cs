using System;
using System.Collections.Generic;
using VisualDM.Core;
using VisualDM.World;

namespace VisualDM.Narrative
{
    /// <summary>
    /// Represents a regional narrative arc, extending GlobalArc with region-specific attributes and logic.
    /// </summary>
    [Serializable]
    public class RegionalArc : GlobalArc
    {
        // --- Region Identification ---
        /// <summary>Unique region identifier.</summary>
        public string RegionId { get; set; }
        /// <summary>Human-readable region name.</summary>
        public string RegionName { get; set; }
        /// <summary>Type/category of the region (e.g., city, province, biome).</summary>
        public string RegionType { get; set; }

        // --- Local Narrative Elements ---
        /// <summary>Story beats unique to this region.</summary>
        public List<RegionalStoryBeat> RegionalStoryBeats { get; set; } = new();
        /// <summary>Characters unique to this region.</summary>
        public List<string> RegionalCharacters { get; set; } = new();
        /// <summary>Locations unique to this region.</summary>
        public List<string> RegionalLocations { get; set; } = new();

        // --- Regional Progression Triggers ---
        public List<IArcCondition> EntryConditions { get; set; } = new();
        public List<IArcCondition> ProgressionEvents { get; set; } = new();
        public List<IArcCondition> ExitConditions { get; set; } = new();

        // --- Relationship to Global Arc ---
        public string ParentGlobalArcId { get; set; }
        public float InfluenceLevel { get; set; } = 1.0f; // 0 = no influence, 1 = full
        public List<OverrideRule> OverrideRules { get; set; } = new();

        // --- Regional World State Effects ---
        public List<RegionalStateChange> RegionalStateChanges { get; set; } = new();
        public List<string> PersistentEffects { get; set; } = new();
        public List<string> TemporaryEffects { get; set; } = new();

        // --- Completion Criteria ---
        public List<IArcCondition> CompletionConditions { get; set; } = new();
        public List<string> Rewards { get; set; } = new();
        public List<string> FollowUpArcs { get; set; } = new();

        /// <summary>
        /// Constructs a new RegionalArc, extending a GlobalArc.
        /// </summary>
        public RegionalArc(string title, string description, string narrativePurpose, string regionId, string regionName, string regionType, string parentGlobalArcId)
            : base(title, description, narrativePurpose)
        {
            RegionId = regionId;
            RegionName = regionName;
            RegionType = regionType;
            ParentGlobalArcId = parentGlobalArcId;
        }

        /// <summary>
        /// Validates the regional arc's properties and relationships.
        /// </summary>
        public void Validate(List<RegionalArc> allRegionalArcs, List<GlobalArc> allGlobalArcs)
        {
            base.Validate(allGlobalArcs);
            if (string.IsNullOrWhiteSpace(RegionId)) throw new ArgumentException("RegionId is required");
            if (string.IsNullOrWhiteSpace(RegionName)) throw new ArgumentException("RegionName is required");
            if (string.IsNullOrWhiteSpace(ParentGlobalArcId)) throw new ArgumentException("ParentGlobalArcId is required");
            // Validate parent exists
            if (!allGlobalArcs.Exists(a => a.Id == ParentGlobalArcId))
                throw new InvalidOperationException($"Parent GlobalArc {ParentGlobalArcId} not found");
            // Validate completion conditions
            if (CompletionConditions == null || CompletionConditions.Count == 0)
                throw new ArgumentException("At least one completion condition is required");
        }

        /// <summary>
        /// Checks if the regional arc is complete.
        /// </summary>
        public bool IsComplete(GameState state)
        {
            foreach (var cond in CompletionConditions)
                if (!cond.IsMet(state, this)) return false;
            return true;
        }

        // --- Region-System Integration ---
        public Region GetRegion(RegionSystem regionSystem)
        {
            return regionSystem.GetAllRegions().FirstOrDefault(r => r.Id == RegionId);
        }

        public void UpdateRegionState(RegionSystem regionSystem, Dictionary<string, object> newState)
        {
            var region = GetRegion(regionSystem);
            if (region != null)
            {
                foreach (var kv in newState)
                    region.State[kv.Key] = kv.Value;
            }
        }

        public void TriggerRegionNarrativeEvent(RegionSystem regionSystem, string eventKey)
        {
            // Stub: Implement region-specific narrative event triggers
            var region = GetRegion(regionSystem);
            if (region != null)
            {
                // Example: region.State["LastNarrativeEvent"] = eventKey;
            }
        }

        // --- Serialization/Deserialization support can be added via DTO/Mapper pattern (see GlobalArc) ---
    }

    /// <summary>
    /// Represents a story beat unique to a region.
    /// </summary>
    [Serializable]
    public class RegionalStoryBeat
    {
        public string Id { get; set; } = IdGenerator.GenerateGuid();
        public string Title { get; set; }
        public string Description { get; set; }
        public Dictionary<string, object> Metadata { get; set; } = new();
    }

    /// <summary>
    /// Represents a rule for overriding global arc behavior in a region.
    /// </summary>
    [Serializable]
    public class OverrideRule
    {
        public string RuleType { get; set; }
        public string Description { get; set; }
        public Dictionary<string, object> Parameters { get; set; } = new();
    }

    /// <summary>
    /// Represents a change to the regional world state.
    /// </summary>
    [Serializable]
    public class RegionalStateChange
    {
        public string StateKey { get; set; }
        public object Value { get; set; }
        public bool IsPersistent { get; set; }
    }
}