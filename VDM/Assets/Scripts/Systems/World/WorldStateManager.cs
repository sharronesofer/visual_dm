using System;
using System.Collections.Generic;
using UnityEngine;

namespace VDM.Systems.World
{
    // Canonical world state variable types:
    // Population, Resource, Motif, FactionStatus, POIState, Weather, Time, QuestStatus, WarStatus, EventFlag, Economy, Law, Custom
    [Serializable]
    public class StateEntry
    {
        public string Key;
        public object Value;
        public int Version;
        public DateTime Timestamp;
        public string Category;
        public string Region;
        // Extend with additional fields as needed
    }

    public class WorldStateManager : MonoBehaviour
    {
        private static WorldStateManager _instance;
        public static WorldStateManager Instance
        {
            get
            {
                if (_instance == null)
                {
                    var go = new GameObject("WorldStateManager");
                    _instance = go.AddComponent<WorldStateManager>();
                    DontDestroyOnLoad(go);
                }
                return _instance;
            }
        }

        private readonly Dictionary<string, List<StateEntry>> stateHistory = new Dictionary<string, List<StateEntry>>();
        private readonly Dictionary<string, StateEntry> latestState = new Dictionary<string, StateEntry>();
        private int version = 0;

        public event Action<StateEntry> OnWorldStateChanged;

        public void SetState(string key, object value, string category = null, string region = null)
        {
            var entry = new StateEntry
            {
                Key = key,
                Value = value,
                Version = ++version,
                Timestamp = DateTime.UtcNow,
                Category = category,
                Region = region
            };
            if (!stateHistory.ContainsKey(key))
                stateHistory[key] = new List<StateEntry>();
            stateHistory[key].Add(entry);
            latestState[key] = entry;
            OnWorldStateChanged?.Invoke(entry);
        }

        public StateEntry GetLatest(string key)
        {
            return latestState.ContainsKey(key) ? latestState[key] : null;
        }

        public List<StateEntry> GetHistory(string key)
        {
            return stateHistory.ContainsKey(key) ? new List<StateEntry>(stateHistory[key]) : new List<StateEntry>();
        }

        public StateEntry GetValueAtTime(string key, DateTime timestamp)
        {
            if (!stateHistory.ContainsKey(key)) return null;
            StateEntry closest = null;
            foreach (var entry in stateHistory[key])
            {
                if (entry.Timestamp <= timestamp)
                    closest = entry;
                else
                    break;
            }
            return closest;
        }
    }
} 