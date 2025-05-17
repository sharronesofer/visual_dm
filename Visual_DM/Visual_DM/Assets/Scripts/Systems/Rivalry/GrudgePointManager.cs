using System;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using VisualDM.NPC;
using Newtonsoft.Json;

namespace VisualDM.Systems.Rivalry
{
    /// <summary>
    /// GrudgePointManager manages grudge points, state transitions, and integration with the Nemesis/Rival system.
    /// Provides persistence, decay, event notification, and hooks for relationship state machines.
    /// </summary>
    public class GrudgePointManager
    {
        // Singleton pattern for global access
        private static GrudgePointManager _instance;
        public static GrudgePointManager Instance => _instance ??= new GrudgePointManager();

        // Reference to the configuration asset (must be assigned at runtime)
        public GrudgeConfig Config { get; set; }

        // Grudge data per NPC (keyed by NPC ID)
        private readonly Dictionary<string, Dictionary<string, List<GrudgeEntry>>> _grudgePoints = new();

        // Tracks last known grudge level for each source-target pair
        private readonly Dictionary<string, Dictionary<string, string>> _lastKnownLevels = new();

        // Configurable maximum history length per source-target pair
        public int MaxHistoryEntries { get; set; } = 100;

        // Versioning for migration support
        private const int CurrentSaveVersion = 1;

        /// <summary>
        /// Version of the GrudgePointManager data model for future extensions.
        /// </summary>
        public int DataModelVersion => CurrentSaveVersion;

        [Serializable]
        private class GrudgeSaveData
        {
            public int Version;
            public Dictionary<string, Dictionary<string, List<GrudgeEntry>>> GrudgePoints;
            public Dictionary<string, Dictionary<string, string>> LastKnownLevels;
        }

        // Data structure for a single grudge event
        public class GrudgeEntry
        {
            public int Points;
            public string Category;
            public string Reason;
            public DateTime Timestamp;
            public GrudgeEntry(int points, string category, string reason, DateTime timestamp)
            {
                Points = points;
                Category = category;
                Reason = reason;
                Timestamp = timestamp;
            }
        }

        /// <summary>
        /// Internal helper to update and fire events if grudge level changes.
        /// </summary>
        private void CheckAndFireLevelChange(string sourceNpcId, string targetNpcId)
        {
            string oldLevel = GetLastKnownLevel(sourceNpcId, targetNpcId);
            string newLevel = GetGrudgeLevel(sourceNpcId, targetNpcId);
            if (oldLevel != newLevel)
            {
                int total = GetTotalGrudgePoints(sourceNpcId, targetNpcId);
                _lastKnownLevels.TryAdd(sourceNpcId, new Dictionary<string, string>());
                _lastKnownLevels[sourceNpcId][targetNpcId] = newLevel;
                VisualDM.Systems.EventSystem.EventBus.Instance.Publish(
                    new VisualDM.Systems.EventSystem.GrudgeLevelChangedEvent(
                        sourceNpcId, targetNpcId, oldLevel, newLevel, total, DateTime.UtcNow));
            }
        }

        private string GetLastKnownLevel(string sourceNpcId, string targetNpcId)
        {
            if (_lastKnownLevels.TryGetValue(sourceNpcId, out var targets) && targets.TryGetValue(targetNpcId, out var level))
                return level;
            return "None";
        }

        /// <summary>
        /// Adds a grudge entry between source and target NPCs, using config for point value.
        /// Prunes oldest entries if above MaxHistoryEntries.
        /// </summary>
        public void AddGrudgePoints(string sourceNpcId, string targetNpcId, int amount, string reason, string category)
        {
            if (!_grudgePoints.ContainsKey(sourceNpcId))
                _grudgePoints[sourceNpcId] = new Dictionary<string, List<GrudgeEntry>>();
            if (!_grudgePoints[sourceNpcId].ContainsKey(targetNpcId))
                _grudgePoints[sourceNpcId][targetNpcId] = new List<GrudgeEntry>();
            var entries = _grudgePoints[sourceNpcId][targetNpcId];
            entries.Add(new GrudgeEntry(amount, category, reason, DateTime.UtcNow));
            // Prune oldest if above max
            while (entries.Count > MaxHistoryEntries)
                entries.RemoveAt(0);
            CheckAndFireLevelChange(sourceNpcId, targetNpcId);
        }

        /// <summary>
        /// Removes grudge points (by amount) between source and target NPCs. Removes oldest entries first.
        /// </summary>
        public void RemoveGrudgePoints(string sourceNpcId, string targetNpcId, int amount, string reason = "Forgiveness")
        {
            var entries = GetGrudgeEntries(sourceNpcId, targetNpcId);
            int toRemove = amount;
            for (int i = 0; i < entries.Count && toRemove > 0; i++)
            {
                if (entries[i].Points <= toRemove)
                {
                    toRemove -= entries[i].Points;
                    entries[i].Points = 0;
                }
                else
                {
                    entries[i].Points -= toRemove;
                    toRemove = 0;
                }
            }
            // Optionally, add a forgiveness entry
            if (amount > 0)
                entries.Add(new GrudgeEntry(-amount, "Forgiveness", reason, DateTime.UtcNow));
            CheckAndFireLevelChange(sourceNpcId, targetNpcId);
        }

        /// <summary>
        /// Gets all grudge entries between source and target NPCs.
        /// </summary>
        public List<GrudgeEntry> GetGrudgeEntries(string sourceNpcId, string targetNpcId)
        {
            if (_grudgePoints.TryGetValue(sourceNpcId, out var targets) && targets.TryGetValue(targetNpcId, out var entries))
                return entries;
            return new List<GrudgeEntry>();
        }

        /// <summary>
        /// Gets the total grudge points (after decay) between source and target NPCs.
        /// </summary>
        public int GetTotalGrudgePoints(string sourceNpcId, string targetNpcId, Func<GrudgeEntry, int> decayFunc = null)
        {
            int total = 0;
            foreach (var entry in GetGrudgeEntries(sourceNpcId, targetNpcId))
            {
                total += decayFunc != null ? decayFunc(entry) : entry.Points;
            }
            return total;
        }

        /// <summary>
        /// Gets the current grudge level (Annoyed, Angry, Vengeful, Nemesis) for a target NPC.
        /// </summary>
        public string GetGrudgeLevel(string sourceNpcId, string targetNpcId)
        {
            int total = GetTotalGrudgePoints(sourceNpcId, targetNpcId);
            if (Config == null) return "Unknown";
            if (total >= Config.NemesisThreshold) return "Nemesis";
            if (total >= Config.VengefulThreshold) return "Vengeful";
            if (total >= Config.AngryThreshold) return "Angry";
            if (total >= Config.AnnoyedThreshold) return "Annoyed";
            return "None";
        }

        /// <summary>
        /// Gets the grudge history (all entries) for a target NPC.
        /// </summary>
        public List<GrudgeEntry> GetGrudgeHistory(string sourceNpcId, string targetNpcId)
        {
            return GetGrudgeEntries(sourceNpcId, targetNpcId);
        }

        /// <summary>
        /// Query grudge history for a source-target pair by time period.
        /// </summary>
        public List<GrudgeEntry> GetGrudgeHistoryByTime(string sourceNpcId, string targetNpcId, DateTime from, DateTime to)
        {
            return GetGrudgeEntries(sourceNpcId, targetNpcId)
                .FindAll(e => e.Timestamp >= from && e.Timestamp <= to);
        }

        /// <summary>
        /// Query grudge history for a source-target pair by category (severity).
        /// </summary>
        public List<GrudgeEntry> GetGrudgeHistoryByCategory(string sourceNpcId, string targetNpcId, string category)
        {
            return GetGrudgeEntries(sourceNpcId, targetNpcId)
                .FindAll(e => e.Category == category);
        }

        /// <summary>
        /// Decays all grudge entries for all NPCs based on elapsed time (in days).
        /// Optionally supports per-NPC personality decay multipliers.
        /// </summary>
        public void DecayAll(float elapsedDays, Func<string, float> npcDecayMultiplier = null)
        {
            foreach (var sourceNpc in _grudgePoints.Keys)
            {
                float sourceMultiplier = npcDecayMultiplier?.Invoke(sourceNpc) ?? 1f;
                foreach (var targetNpc in _grudgePoints[sourceNpc].Keys)
                {
                    var entries = _grudgePoints[sourceNpc][targetNpc];
                    foreach (var entry in entries)
                    {
                        float decayRate = GetDecayRate(entry.Category, entry.Points);
                        int decayAmount = Mathf.FloorToInt(decayRate * elapsedDays * sourceMultiplier);
                        entry.Points = Math.Max(0, entry.Points - decayAmount);
                    }
                    CheckAndFireLevelChange(sourceNpc, targetNpc);
                }
            }
        }

        /// <summary>
        /// Gets the decay rate for a given category and point value (severity).
        /// </summary>
        private float GetDecayRate(string category, int points)
        {
            if (Config == null || Config.Categories == null)
                return 1f;
            var cat = Config.Categories.FirstOrDefault(c => c.CategoryName == category);
            if (cat == null)
                return Config.DefaultDecayRate;
            if (points <= cat.MinorValue) return cat.MinorDecayRate;
            if (points <= cat.ModerateValue) return cat.ModerateDecayRate;
            return cat.MajorDecayRate;
        }

        /// <summary>
        /// Call this method from a game loop or tick system to decay grudge points over time.
        /// </summary>
        public void UpdateDecay(float deltaDays)
        {
            DecayAll(deltaDays);
        }

        /// <summary>
        /// Serializes the entire grudge state to a JSON string for persistence.
        /// </summary>
        public string SerializeGrudgeState()
        {
            var data = new GrudgeSaveData
            {
                Version = CurrentSaveVersion,
                GrudgePoints = _grudgePoints,
                LastKnownLevels = _lastKnownLevels
            };
            return JsonConvert.SerializeObject(data);
        }

        /// <summary>
        /// Deserializes the grudge state from a JSON string. Handles migration and fallback.
        /// </summary>
        public void DeserializeGrudgeState(string json)
        {
            try
            {
                var data = JsonConvert.DeserializeObject<GrudgeSaveData>(json);
                if (data == null || data.GrudgePoints == null)
                    throw new Exception("Invalid or empty grudge save data");
                _grudgePoints.Clear();
                foreach (var s in data.GrudgePoints)
                    _grudgePoints[s.Key] = s.Value;
                _lastKnownLevels.Clear();
                if (data.LastKnownLevels != null)
                    foreach (var s in data.LastKnownLevels)
                        _lastKnownLevels[s.Key] = s.Value;
                // Migration: handle future version changes here
                // (e.g., if (data.Version < 2) { ... })
            }
            catch (Exception ex)
            {
                Debug.LogError($"[GrudgePointManager] Failed to load grudge state: {ex.Message}. Resetting to empty state.");
                _grudgePoints.Clear();
                _lastKnownLevels.Clear();
            }
        }

        // Persistence API:
        // - SerializeGrudgeState(): string (call when saving game state)
        // - DeserializeGrudgeState(string): void (call when loading game state)
        // - Handles migration/versioning and fallback for corrupted data.

        // API Documentation:
        // AddGrudgePoints(string sourceNpcId, string targetNpcId, int amount, string reason, string category)
        // RemoveGrudgePoints(string sourceNpcId, string targetNpcId, int amount, string reason = "Forgiveness")
        // GetGrudgeLevel(string sourceNpcId, string targetNpcId) => "Annoyed"|"Angry"|"Vengeful"|"Nemesis"|"None"
        // GetGrudgeHistory(string sourceNpcId, string targetNpcId) => List<GrudgeEntry>
        // GetTotalGrudgePoints(string sourceNpcId, string targetNpcId, Func<GrudgeEntry, int> decayFunc = null)

        // TODO: Add decay logic, integration with RelationshipStateMachine, and persistence hooks.

        /// <summary>
        /// Struct for exposing grudge level info to UI.
        /// </summary>
        public struct GrudgeLevelInfo
        {
            public string Level;
            public int TotalPoints;
            public TimeSpan TimeSinceLastChange;
        }

        /// <summary>
        /// Returns GrudgeLevelInfo for a source-target pair (for UI display).
        /// </summary>
        public GrudgeLevelInfo GetGrudgeLevelInfo(string sourceNpcId, string targetNpcId)
        {
            string level = GetGrudgeLevel(sourceNpcId, targetNpcId);
            int points = GetTotalGrudgePoints(sourceNpcId, targetNpcId);
            DateTime lastChange = DateTime.MinValue;
            if (_lastKnownLevels.TryGetValue(sourceNpcId, out var targets) && targets.TryGetValue(targetNpcId, out var _))
            {
                // Find the most recent entry in history for this pair
                var entries = GetGrudgeEntries(sourceNpcId, targetNpcId);
                if (entries.Count > 0)
                    lastChange = entries[^1].Timestamp;
            }
            return new GrudgeLevelInfo
            {
                Level = level,
                TotalPoints = points,
                TimeSinceLastChange = lastChange == DateTime.MinValue ? TimeSpan.MaxValue : (DateTime.UtcNow - lastChange)
            };
        }

        /// <summary>
        /// Returns a visual indicator (string or enum) for a grudge level (for UI icons/colors).
        /// </summary>
        public string GetVisualIndicator(string level)
        {
            return level switch
            {
                "Annoyed" => "icon_annoyed",
                "Angry" => "icon_angry",
                "Vengeful" => "icon_vengeful",
                "Nemesis" => "icon_nemesis",
                _ => "icon_none"
            };
        }

        /// <summary>
        /// Allows UI or other systems to subscribe to grudge level changes for notifications.
        /// </summary>
        public void SubscribeToGrudgeLevelChanges(Action<VisualDM.Systems.EventSystem.GrudgeLevelChangedEvent> handler)
        {
            VisualDM.Systems.EventSystem.EventBus.Instance.Subscribe(handler);
        }

        // Visualization/notification support:
        // - GetGrudgeLevelInfo: for UI display of level, points, and time since last change
        // - GetVisualIndicator: for UI icons/colors per level
        // - SubscribeToGrudgeLevelChanges: for UI notifications on threshold crossing

        /// <summary>
        /// Notifies a RelationshipStateMachine of grudge-based state changes for a given NPC pair.
        /// Use this to synchronize grudge points with relationship state transitions.
        /// </summary>
        public void NotifyRelationshipStateMachine(VisualDM.NPC.RelationshipStateMachine stateMachine, string targetId)
        {
            int grudgePoints = GetTotalGrudgePoints(stateMachine.GetType().GetProperty("_npcId", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)?.GetValue(stateMachine) as string, targetId);
            stateMachine.SyncWithGrudgePoints(targetId, grudgePoints);
        }
    }
}