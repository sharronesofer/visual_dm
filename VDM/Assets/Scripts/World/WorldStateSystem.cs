using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using UnityEngine;
using System.IO;

namespace VisualDM.World
{
    /// <summary>
    /// Hierarchical, versioned, transactional, event-driven world state system with rollback and historical queries.
    /// </summary>
    public class WorldStateSystem : MonoBehaviour
    {
        // Singleton instance
        private static WorldStateSystem _instance;
        public static WorldStateSystem Instance
        {
            get
            {
                if (_instance == null)
                {
                    var go = new GameObject("WorldStateSystem");
                    _instance = go.AddComponent<WorldStateSystem>();
                    DontDestroyOnLoad(go);
                }
                return _instance;
            }
        }

        // State entry with versioning
        [Serializable]
        public class StateEntry
        {
            public string Key;
            public object Value;
            public long Timestamp; // Unix ms
            public int Version;
        }

        // State history: key -> list of versions (sorted by time)
        private readonly Dictionary<string, List<StateEntry>> _stateHistory = new Dictionary<string, List<StateEntry>>();
        // Current state: key -> latest value
        private readonly Dictionary<string, object> _currentState = new Dictionary<string, object>();
        // Version counter
        private int _versionCounter = 0;
        // Lock for thread safety
        private readonly object _lock = new object();

        // Event for state changes
        [Serializable]
        public class StateChangedEvent : UnityEngine.Events.UnityEvent<string, object, object, long, int> { }
        public StateChangedEvent OnStateChanged = new StateChangedEvent();

        // Set a state value (records version, emits event)
        public void Set(string key, object value)
        {
            lock (_lock)
            {
                object oldValue = _currentState.ContainsKey(key) ? _currentState[key] : null;
                long now = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds();
                int version = ++_versionCounter;
                var entry = new StateEntry { Key = key, Value = value, Timestamp = now, Version = version };
                if (!_stateHistory.ContainsKey(key))
                    _stateHistory[key] = new List<StateEntry>();
                _stateHistory[key].Add(entry);
                _currentState[key] = value;
                OnStateChanged.Invoke(key, value, oldValue, now, version);
            }
        }

        // Get current value
        public object Get(string key)
        {
            lock (_lock)
            {
                return _currentState.TryGetValue(key, out var value) ? value : null;
            }
        }

        // Get value at a specific timestamp (or closest before)
        public object GetAt(string key, long timestamp)
        {
            lock (_lock)
            {
                if (!_stateHistory.ContainsKey(key)) return null;
                var list = _stateHistory[key];
                var entry = list.LastOrDefault(e => e.Timestamp <= timestamp);
                return entry != null ? entry.Value : null;
            }
        }

        // Rollback all state to a specific timestamp
        public void RollbackTo(long timestamp)
        {
            lock (_lock)
            {
                foreach (var key in _stateHistory.Keys.ToList())
                {
                    var list = _stateHistory[key];
                    var entry = list.LastOrDefault(e => e.Timestamp <= timestamp);
                    if (entry != null)
                        _currentState[key] = entry.Value;
                    else
                        _currentState.Remove(key);
                }
            }
        }

        // Get all changes for a key in a time range
        public List<StateEntry> GetChanges(string key, long startTime, long endTime)
        {
            lock (_lock)
            {
                if (!_stateHistory.ContainsKey(key)) return new List<StateEntry>();
                return _stateHistory[key].Where(e => e.Timestamp >= startTime && e.Timestamp <= endTime).ToList();
            }
        }

        // Transaction support
        public class Transaction : IDisposable
        {
            private readonly WorldStateSystem _system;
            private readonly List<(string key, object oldValue, object newValue, int version, long timestamp)> _changes = new();
            private bool _committed = false;
            public Transaction(WorldStateSystem system) { _system = system; }
            public void Set(string key, object value)
            {
                lock (_system._lock)
                {
                    object oldValue = _system._currentState.ContainsKey(key) ? _system._currentState[key] : null;
                    long now = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds();
                    int version = ++_system._versionCounter;
                    _changes.Add((key, oldValue, value, version, now));
                }
            }
            public void Commit()
            {
                lock (_system._lock)
                {
                    foreach (var (key, oldValue, newValue, version, timestamp) in _changes)
                    {
                        var entry = new StateEntry { Key = key, Value = newValue, Timestamp = timestamp, Version = version };
                        if (!_system._stateHistory.ContainsKey(key))
                            _system._stateHistory[key] = new List<StateEntry>();
                        _system._stateHistory[key].Add(entry);
                        _system._currentState[key] = newValue;
                        _system.OnStateChanged.Invoke(key, newValue, oldValue, timestamp, version);
                    }
                    _committed = true;
                }
            }
            public void Rollback()
            {
                _changes.Clear();
            }
            public void Dispose()
            {
                if (!_committed) Rollback();
            }
        }
        public Transaction BeginTransaction() => new Transaction(this);

        // Delta compression: prune redundant history (keep only changes, configurable retention)
        public void PruneHistory(int maxVersionsPerKey = 100)
        {
            lock (_lock)
            {
                foreach (var key in _stateHistory.Keys.ToList())
                {
                    var list = _stateHistory[key];
                    if (list.Count > maxVersionsPerKey)
                        _stateHistory[key] = list.Skip(list.Count - maxVersionsPerKey).ToList();
                }
            }
        }

        // Serialization (JSON, binary)
        [Serializable]
        private class SerializableStateHistory
        {
            public List<StateEntry> Entries = new();
            public int VersionCounter;
        }
        private string SavePath => Path.Combine(Application.persistentDataPath, "worldstate_v2.json");
        public void Save()
        {
            lock (_lock)
            {
                var allEntries = _stateHistory.SelectMany(kvp => kvp.Value).ToList();
                var data = new SerializableStateHistory { Entries = allEntries, VersionCounter = _versionCounter };
                var json = JsonUtility.ToJson(data, true);
                File.WriteAllText(SavePath, json);
            }
        }
        public void Load()
        {
            lock (_lock)
            {
                if (!File.Exists(SavePath)) return;
                var json = File.ReadAllText(SavePath);
                var data = JsonUtility.FromJson<SerializableStateHistory>(json);
                _stateHistory.Clear();
                _currentState.Clear();
                foreach (var entry in data.Entries)
                {
                    if (!_stateHistory.ContainsKey(entry.Key))
                        _stateHistory[entry.Key] = new List<StateEntry>();
                    _stateHistory[entry.Key].Add(entry);
                    _currentState[entry.Key] = entry.Value;
                }
                _versionCounter = data.VersionCounter;
            }
        }

        // Integration hooks (call these from other systems as needed)
        public void EmitEvent(string key, object value, object oldValue, long timestamp, int version)
        {
            OnStateChanged.Invoke(key, value, oldValue, timestamp, version);
        }

        // Example: subscribe to state changes
        public void Subscribe(UnityEngine.Events.UnityAction<string, object, object, long, int> handler)
        {
            OnStateChanged.AddListener(handler);
        }
        public void Unsubscribe(UnityEngine.Events.UnityAction<string, object, object, long, int> handler)
        {
            OnStateChanged.RemoveListener(handler);
        }

        // Usage example (see docs/WorldStateSystem.md for more)
    }
} 