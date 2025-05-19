using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using UnityEngine;

namespace VisualDM.Systems.Quest
{
    [Serializable]
    public class PlayerChoiceRecord
    {
        public string QuestId;
        public string ChoiceId;
        public DateTime Timestamp;
        public float Impact;
        public float Importance;
    }

    [Serializable]
    public class WorldStateSnapshot
    {
        public DateTime Timestamp;
        public Dictionary<string, object> StateDiff = new();
        public List<string> AffectedEntities = new();
    }

    /// <summary>
    /// Persistent memory system for player choices and world state history.
    /// </summary>
    public class QuestMemorySystem
    {
        private static QuestMemorySystem _instance;
        public static QuestMemorySystem Instance => _instance ??= new QuestMemorySystem();

        private readonly List<PlayerChoiceRecord> _playerChoices = new();
        private readonly List<WorldStateSnapshot> _worldStateHistory = new();
        private readonly object _lock = new();

        private QuestMemorySystem() { }

        public void RecordPlayerChoice(string questId, string choiceId, float impact, float importance)
        {
            lock (_lock)
            {
                _playerChoices.Add(new PlayerChoiceRecord
                {
                    QuestId = questId,
                    ChoiceId = choiceId,
                    Timestamp = DateTime.UtcNow,
                    Impact = impact,
                    Importance = importance
                });
            }
        }

        public void RecordWorldStateSnapshot(Dictionary<string, object> diff, List<string> affectedEntities)
        {
            lock (_lock)
            {
                _worldStateHistory.Add(new WorldStateSnapshot
                {
                    Timestamp = DateTime.UtcNow,
                    StateDiff = new Dictionary<string, object>(diff),
                    AffectedEntities = new List<string>(affectedEntities)
                });
            }
        }

        public List<PlayerChoiceRecord> QueryPlayerChoices(string questId = null, float minImportance = 0.0f)
        {
            lock (_lock)
            {
                return _playerChoices
                    .Where(c => (questId == null || c.QuestId == questId) && c.Importance >= minImportance)
                    .OrderByDescending(c => c.Importance)
                    .ToList();
            }
        }

        public List<WorldStateSnapshot> QueryWorldStateHistory(DateTime? since = null)
        {
            lock (_lock)
            {
                return _worldStateHistory
                    .Where(s => !since.HasValue || s.Timestamp >= since.Value)
                    .OrderBy(s => s.Timestamp)
                    .ToList();
            }
        }

        /// <summary>
        /// Decay/importance algorithm: reduce importance of old/insignificant choices.
        /// </summary>
        public void DecayChoices(float decayRate = 0.95f, float minImportance = 0.1f)
        {
            lock (_lock)
            {
                foreach (var c in _playerChoices)
                {
                    var ageDays = (float)(DateTime.UtcNow - c.Timestamp).TotalDays;
                    c.Importance *= Mathf.Pow(decayRate, ageDays);
                }
                _playerChoices.RemoveAll(c => c.Importance < minImportance);
            }
        }

        /// <summary>
        /// State diffing: compare two world state snapshots and return the diff.
        /// </summary>
        public static Dictionary<string, (object oldValue, object newValue)> DiffStates(Dictionary<string, object> oldState, Dictionary<string, object> newState)
        {
            var diff = new Dictionary<string, (object, object)>();
            foreach (var key in newState.Keys)
            {
                if (!oldState.ContainsKey(key) || !Equals(oldState[key], newState[key]))
                    diff[key] = (oldState.ContainsKey(key) ? oldState[key] : null, newState[key]);
            }
            return diff;
        }

        /// <summary>
        /// Serialize all memory and world state data to JSON.
        /// </summary>
        public string SerializeAll()
        {
            lock (_lock)
            {
                var data = new MemoryData
                {
                    PlayerChoices = _playerChoices,
                    WorldStateHistory = _worldStateHistory
                };
                return JsonUtility.ToJson(data);
            }
        }

        /// <summary>
        /// Deserialize all memory and world state data from JSON.
        /// </summary>
        public void DeserializeAll(string json)
        {
            lock (_lock)
            {
                var data = JsonUtility.FromJson<MemoryData>(json);
                _playerChoices.Clear();
                _playerChoices.AddRange(data.PlayerChoices);
                _worldStateHistory.Clear();
                _worldStateHistory.AddRange(data.WorldStateHistory);
            }
        }

        [Serializable]
        private class MemoryData
        {
            public List<PlayerChoiceRecord> PlayerChoices = new();
            public List<WorldStateSnapshot> WorldStateHistory = new();
        }
    }
} 