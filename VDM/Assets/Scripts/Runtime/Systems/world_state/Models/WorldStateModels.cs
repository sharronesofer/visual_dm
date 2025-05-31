using System.Collections.Generic;
using System;
using UnityEngine;
using VDM.Systems.Region.Models;

namespace VDM.Systems.Worldstate.Models
{
    /// <summary>
    /// Categories for different types of world state
    /// </summary>
    public enum StateCategory
    {
        Global,
        Regional,
        Local,
        Temporal,
        Environmental,
        Political,
        Economic,
        Social
    }

    /// <summary>
    /// Types of state changes that can occur
    /// </summary>
    public enum StateChangeType
    {
        Created,
        Updated,
        Deleted,
        Merged,
        Split,
        Archived
    }

    /// <summary>
    /// Represents a terrain type in the world
    /// </summary>
    [Serializable]
    public class TerrainType
    {
        public string id;
        public string name;
        public string description;
        public float movementCost = 1.0f;
        public float visibilityModifier = 1.0f;
        public List<string> resources = new List<string>();
        public List<string> features = new List<string>();
        public Dictionary<string, object> metadata = new Dictionary<string, object>();
    }

    /// <summary>
    /// Represents a level range for regions
    /// </summary>
    [Serializable]
    public class LevelRange
    {
        public int minLevel;
        public int maxLevel;

        public LevelRange(int min = 1, int max = 20)
        {
            minLevel = Mathf.Clamp(min, 1, 20);
            maxLevel = Mathf.Clamp(max, 1, 20);
        }

        public bool IsValidLevel(int level)
        {
            return level >= minLevel && level <= maxLevel;
        }
    }

    /// <summary>
    /// Represents a state variable with metadata
    /// </summary>
    [Serializable]
    public class StateVariable
    {
        public string name;
        public object value;
        public StateCategory category;
        public DateTime lastUpdated;
        public Dictionary<string, object> metadata = new Dictionary<string, object>();
    }

    /// <summary>
    /// Records a change in world state
    /// </summary>
    [Serializable]
    public class StateChangeRecord
    {
        public string id;
        public string regionId;
        public StateChangeType changeType;
        public StateCategory category;
        public string description;
        public Dictionary<string, object> oldValues = new Dictionary<string, object>();
        public Dictionary<string, object> newValues = new Dictionary<string, object>();
        public DateTime timestamp;
        public string userId;
        public Dictionary<string, object> metadata = new Dictionary<string, object>();
    }

    /// <summary>
    /// Represents a world region with comprehensive state management
    /// </summary>
    [Serializable]
    public class WorldRegion
    {
        public string id;
        public string name;
        public string description;
        public LevelRange levelRange = new LevelRange();
        public List<string> terrainTypes = new List<string>();
        public List<string> pointsOfInterest = new List<string>();
        public List<string> factions = new List<string>();
        public string climate;
        public DateTime createdAt;
        public DateTime updatedAt;
        public Dictionary<string, object> metadata = new Dictionary<string, object>();

        // Consolidation/Q&A fields
        public string primaryCapitolId;
        public string secondaryCapitolId;
        public string metropolisType;
        public List<string> motifPool = new List<string>();
        public List<string> motifHistory = new List<string>();
        public List<Dictionary<string, object>> memory = new List<Dictionary<string, object>>();
        public string arc;
        public List<string> arcHistory = new List<string>();
        public List<Dictionary<string, object>> history = new List<Dictionary<string, object>>();
        public int population;
        public int tensionLevel;

        // State management
        public Dictionary<StateCategory, Dictionary<string, object>> state = 
            new Dictionary<StateCategory, Dictionary<string, object>>();

        public Dictionary<string, object> GetState(StateCategory category)
        {
            return state.ContainsKey(category) ? state[category] : new Dictionary<string, object>();
        }

        public void SetState(StateCategory category, Dictionary<string, object> stateData)
        {
            state[category] = stateData;
            updatedAt = DateTime.UtcNow;
        }

        public void UpdateState(StateCategory category, Dictionary<string, object> updates)
        {
            if (!state.ContainsKey(category))
            {
                state[category] = new Dictionary<string, object>();
            }

            foreach (var kvp in updates)
            {
                state[category][kvp.Key] = kvp.Value;
            }
            updatedAt = DateTime.UtcNow;
        }
    }

    /// <summary>
    /// Represents a snapshot of world state at a specific time
    /// </summary>
    [Serializable]
    public class WorldStateSnapshot
    {
        public string id;
        public string name;
        public string description;
        public DateTime timestamp;
        public List<WorldRegion> regions = new List<WorldRegion>();
        public Dictionary<string, object> globalState = new Dictionary<string, object>();
        public List<StateChangeRecord> changes = new List<StateChangeRecord>();
        public Dictionary<string, object> metadata = new Dictionary<string, object>();
    }

    /// <summary>
    /// Represents a world map with regions and their relationships
    /// </summary>
    [Serializable]
    public class WorldMap
    {
        public string id;
        public string name;
        public string description;
        public int width;
        public int height;
        public List<WorldRegion> regions = new List<WorldRegion>();
        public Dictionary<string, List<string>> adjacencies = new Dictionary<string, List<string>>();
        public Dictionary<string, object> metadata = new Dictionary<string, object>();
        public DateTime createdAt;
        public DateTime updatedAt;

        public List<string> GetAdjacentRegions(string regionId)
        {
            return adjacencies.ContainsKey(regionId) ? adjacencies[regionId] : new List<string>();
        }

        public void AddAdjacency(string regionId1, string regionId2)
        {
            if (!adjacencies.ContainsKey(regionId1))
                adjacencies[regionId1] = new List<string>();
            if (!adjacencies.ContainsKey(regionId2))
                adjacencies[regionId2] = new List<string>();

            if (!adjacencies[regionId1].Contains(regionId2))
                adjacencies[regionId1].Add(regionId2);
            if (!adjacencies[regionId2].Contains(regionId1))
                adjacencies[regionId2].Add(regionId1);

            updatedAt = DateTime.UtcNow;
        }
    }

    /// <summary>
    /// Request model for creating world state snapshots
    /// </summary>
    [Serializable]
    public class CreateSnapshotRequest
    {
        public string name;
        public string description;
        public List<string> regionIds = new List<string>();
        public bool includeGlobalState = true;
        public Dictionary<string, object> metadata = new Dictionary<string, object>();
    }

    /// <summary>
    /// Request model for restoring world state from snapshot
    /// </summary>
    [Serializable]
    public class RestoreSnapshotRequest
    {
        public string snapshotId;
        public List<string> regionIds = new List<string>();
        public bool restoreGlobalState = true;
        public bool createBackup = true;
        public Dictionary<string, object> metadata = new Dictionary<string, object>();
    }

    /// <summary>
    /// Query parameters for world state operations
    /// </summary>
    [Serializable]
    public class WorldStateQueryParams
    {
        public List<StateCategory> categories = new List<StateCategory>();
        public List<string> regionIds = new List<string>();
        public DateTime? fromDate;
        public DateTime? toDate;
        public int? limit;
        public int? offset;
        public string search;
        public Dictionary<string, object> filters = new Dictionary<string, object>();
    }

    /// <summary>
    /// Response model for world state operations
    /// </summary>
    [Serializable]
    public class WorldStateResponse<T>
    {
        public bool success;
        public T data;
        public string message;
        public List<string> errors = new List<string>();
        public Dictionary<string, object> metadata = new Dictionary<string, object>();
    }

    /// <summary>
    /// Analytics data for world state
    /// </summary>
    [Serializable]
    public class WorldStateAnalytics
    {
        public int totalRegions;
        public int totalSnapshots;
        public int totalStateChanges;
        public Dictionary<StateCategory, int> statesByCategory = new Dictionary<StateCategory, int>();
        public Dictionary<StateChangeType, int> changesByType = new Dictionary<StateChangeType, int>();
        public DateTime lastUpdate;
        public Dictionary<string, object> metrics = new Dictionary<string, object>();
    }
} 