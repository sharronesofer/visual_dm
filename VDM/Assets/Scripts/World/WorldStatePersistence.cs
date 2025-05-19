using System;
using System.Collections.Generic;
using System.IO;
using UnityEngine;
using VisualDM.Entities;
using System.Linq;
using VisualDM.World;

namespace VisualDM.World
{
    [Serializable]
    public class SerializableWorldState
    {
        public Dictionary<string, string> GlobalProperties = new Dictionary<string, string>();
        public List<SerializableRegionWorldState> Regions = new List<SerializableRegionWorldState>();
        public int SchemaVersion = 1; // For migration
    }

    [Serializable]
    public class SerializableRegionWorldState
    {
        public string RegionId;
        public Dictionary<string, string> RegionalProperties = new Dictionary<string, string>();
    }

    public static class WorldStatePersistence
    {
        private static string SavePath => Path.Combine(Application.persistentDataPath, "worldstate.json");

        // Save the current world state to disk
        public static void Save(WorldStateManager manager)
        {
            var data = new SerializableWorldState();
            // Serialize global properties
            foreach (var kvp in manager.GetAllGlobalProperties())
            {
                data.GlobalProperties[kvp.Key] = JsonUtility.ToJson(kvp.Value);
            }
            // Save time, calendar, and events
            var worldManagerObj = UnityEngine.GameObject.FindObjectOfType<WorldManager>();
            if (worldManagerObj != null)
            {
                data.GlobalProperties["WorldTime"] = JsonUtility.ToJson(worldManagerObj.TimeSystem.GetSerializableData());
                data.GlobalProperties["Calendar"] = JsonUtility.ToJson(worldManagerObj.CalendarSystem.GetSerializableData());
                data.GlobalProperties["RecurringEvents"] = JsonUtility.ToJson(worldManagerObj.RecurringEventSystem.GetSerializableData());
            }
            // --- Advanced Faction System: Save all factions ---
            var worldManagerObj = GameObject.Find("WorldManager");
            if (worldManagerObj != null)
            {
                // Use dynamic to avoid type error if WorldManager is not found
                dynamic worldManager = worldManagerObj.GetComponent("WorldManager"); // TODO: Replace with strong type if available
                if (worldManager != null && worldManager.FactionSystem != null)
                {
                    var factions = worldManager.FactionSystem.GetAllFactions();
                    var factionStates = new List<Dictionary<string, object>>();
                    foreach (var faction in factions)
                    {
                        // Save basic and advanced state
                        var state = new Dictionary<string, object>
                        {
                            {"Id", faction.Id},
                            {"Name", faction.Name},
                            {"Description", faction.Description},
                            {"Advanced", faction.SaveAdvancedState()}
                        };
                        factionStates.Add(state);
                    }
                    data.GlobalProperties["Factions"] = JsonUtility.ToJson(factionStates);
                }
            }
            // Serialize regions
            foreach (var region in manager.GetAllRegions())
            {
                var regionData = new SerializableRegionWorldState
                {
                    RegionId = region.Region.RegionId
                };
                foreach (var prop in region.GetAllRegionalProperties())
                {
                    regionData.RegionalProperties[prop.Key] = JsonUtility.ToJson(prop.Value);
                }
                data.Regions.Add(regionData);
            }
            // Write to disk
            var json = JsonUtility.ToJson(data, true);
            File.WriteAllText(SavePath, json);
        }

        // Load world state from disk
        public static void Load(WorldStateManager manager)
        {
            if (!File.Exists(SavePath))
                return;
            var json = File.ReadAllText(SavePath);
            var data = JsonUtility.FromJson<SerializableWorldState>(json);
            if (data == null)
                return;
            // Migration hook
            if (data.SchemaVersion < 1)
            {
                // Add migration logic here for future schema changes
            }
            // Restore global properties
            foreach (var kvp in data.GlobalProperties)
            {
                if (kvp.Key == "Factions")
                {
                    // --- Advanced Faction System: Load all factions ---
                    var worldManagerObj = GameObject.Find("WorldManager");
                    if (worldManagerObj != null)
                    {
                        // Use dynamic to avoid type error if WorldManager is not found
                        dynamic worldManager = worldManagerObj.GetComponent("WorldManager"); // TODO: Replace with strong type if available
                        if (worldManager != null && worldManager.FactionSystem != null)
                        {
                            // Deserialize faction list
                            var factionStates = JsonUtility.FromJson<List<Dictionary<string, object>>>(kvp.Value);
                            // TODO: Clear existing factions if needed
                            foreach (var fdata in factionStates)
                            {
                                var id = fdata["Id"] as string;
                                var name = fdata["Name"] as string;
                                var desc = fdata["Description"] as string;
                                var faction = new VisualDM.Entities.Faction(id, name, desc);
                                // Load advanced state
                                if (fdata.TryGetValue("Advanced", out var advObj) && advObj is Dictionary<string, object> adv)
                                {
                                    // Workaround: extract lambda to delegate before passing to dynamic
                                    Func<string, VisualDM.Entities.Faction> resolver = fid => (VisualDM.Entities.Faction)((IEnumerable<dynamic>)worldManager.FactionSystem.GetAllFactions()).FirstOrDefault(f => f.Id == fid);
                                    faction.LoadAdvancedState(adv, resolver);
                                }
                                // Add to FactionSystem (implement AddFaction if needed)
                                // worldManager.FactionSystem.AddFaction(faction); // Uncomment if AddFaction(Faction) exists
                            }
                        }
                    }
                }
                else
                {
                    var obj = JsonUtility.FromJson<object>(kvp.Value);
                    manager.SetProperty(kvp.Key, obj);
                }
            }
            // Restore time, calendar, and events
            var worldManagerObj = UnityEngine.GameObject.FindObjectOfType<WorldManager>();
            if (worldManagerObj != null)
            {
                if (data.GlobalProperties.TryGetValue("WorldTime", out var timeJson))
                {
                    var timeData = JsonUtility.FromJson<WorldTimeSystem.WorldTimeData>(timeJson);
                    worldManagerObj.TimeSystem.LoadFromData(timeData);
                }
                if (data.GlobalProperties.TryGetValue("Calendar", out var calJson))
                {
                    var calData = JsonUtility.FromJson<CalendarSystem.CalendarData>(calJson);
                    worldManagerObj.CalendarSystem.LoadFromData(calData);
                }
                if (data.GlobalProperties.TryGetValue("RecurringEvents", out var eventsJson))
                {
                    var eventList = JsonUtility.FromJson<List<RecurringEventSystem.ScheduledEvent>>(eventsJson);
                    worldManagerObj.RecurringEventSystem.LoadFromData(eventList);
                }
            }
            // Restore regions
            foreach (var regionData in data.Regions)
            {
                var region = manager.GetRegionWorldState(regionData.RegionId);
                if (region == null)
                    continue;
                foreach (var prop in regionData.RegionalProperties)
                {
                    var obj = JsonUtility.FromJson<object>(prop.Value);
                    region.SetProperty(prop.Key, obj);
                }
            }
        }
    }

    // Extension methods for WorldStateManager and RegionWorldState
    public static class WorldStateExtensions
    {
        public static Dictionary<string, object> GetAllGlobalProperties(this WorldStateManager manager)
        {
            var type = manager.GetType();
            var field = type.GetField("_globalProperties", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);
            return field?.GetValue(manager) as Dictionary<string, object>;
        }

        public static List<RegionWorldState> GetAllRegions(this WorldStateManager manager)
        {
            var type = manager.GetType();
            var field = type.GetField("_regions", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);
            var dict = field?.GetValue(manager) as Dictionary<string, RegionWorldState>;
            return dict != null ? new List<RegionWorldState>(dict.Values) : new List<RegionWorldState>();
        }

        public static Dictionary<string, object> GetAllRegionalProperties(this RegionWorldState region)
        {
            var type = region.GetType();
            var field = type.GetField("_regionalProperties", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);
            return field?.GetValue(region) as Dictionary<string, object>;
        }
    }
}