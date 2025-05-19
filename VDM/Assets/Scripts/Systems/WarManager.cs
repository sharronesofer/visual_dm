using System;
using System.Collections.Generic;
using UnityEngine;
using VDM.Entities;
using VDM.POI;
using VDM.World;
using VDM.Core;

namespace VDM.Systems.War
{
    /// <summary>
    /// Singleton manager for all war and tension systems between factions.
    /// Handles tension tracking, war simulation, resource/population impact, and event integration.
    /// </summary>
    public class WarManager : MonoBehaviour
    {
        private static WarManager _instance;
        public static WarManager Instance
        {
            get
            {
                if (_instance == null)
                {
                    var go = new GameObject("WarManager");
                    _instance = go.AddComponent<WarManager>();
                    DontDestroyOnLoad(go);
                }
                return _instance;
            }
        }

        // Tension trackers for each faction pair
        private readonly Dictionary<(string, string), TensionTracker> _tensionTrackers = new();
        // Active wars
        private readonly List<WarState> _activeWars = new();

        // Event: Tension changed
        public event Action<string, string, float> OnTensionChanged;
        // Event: War started/ended
        public event Action<WarState, bool> OnWarStateChanged;

        /// <summary>
        /// Get or create a TensionTracker for a faction pair.
        /// </summary>
        public TensionTracker GetTensionTracker(string factionA, string factionB)
        {
            var key = (factionA, factionB);
            if (!_tensionTrackers.TryGetValue(key, out var tracker))
            {
                tracker = new TensionTracker(factionA, factionB);
                tracker.OnTensionChanged += (a, b, value) => OnTensionChanged?.Invoke(a, b, value);
                _tensionTrackers[key] = tracker;
            }
            return tracker;
        }

        /// <summary>
        /// Start a war between two factions.
        /// </summary>
        public WarState StartWar(string factionA, string factionB)
        {
            var war = new WarState(factionA, factionB);
            _activeWars.Add(war);
            OnWarStateChanged?.Invoke(war, true);
            // TODO: Integrate with POI, analytics, etc.
            return war;
        }

        /// <summary>
        /// End a war between two factions.
        /// </summary>
        public void EndWar(WarState war)
        {
            if (_activeWars.Remove(war))
            {
                OnWarStateChanged?.Invoke(war, false);
                // TODO: Resource/population impact, POI state, analytics
            }
        }

        /// <summary>
        /// Simulate all active wars (call periodically).
        /// </summary>
        public void SimulateWars(float deltaTime)
        {
            foreach (var war in _activeWars)
            {
                war.Simulate(deltaTime);
            }
        }

        // TODO: Serialization, analytics integration, event-driven hooks
    }

    /// <summary>
    /// Tracks tension between two factions, with modifiers and decay.
    /// </summary>
    public class TensionTracker
    {
        public string FactionA { get; }
        public string FactionB { get; }
        private float _tension;
        public float Tension => _tension;
        public event Action<string, string, float> OnTensionChanged;

        // Modifiers (could be ScriptableObjects)
        private readonly List<ITensionModifier> _modifiers = new();
        private float _decayRate = 0.1f; // per day

        public TensionTracker(string a, string b)
        {
            FactionA = a;
            FactionB = b;
            _tension = 0f;
        }

        public void AddModifier(ITensionModifier mod) => _modifiers.Add(mod);
        public void RemoveModifier(ITensionModifier mod) => _modifiers.Remove(mod);

        public void ApplyEvent(float delta)
        {
            _tension = Mathf.Clamp(_tension + delta, 0, 100);
            OnTensionChanged?.Invoke(FactionA, FactionB, _tension);
        }

        public void Decay(float deltaTime)
        {
            float decay = _decayRate * deltaTime;
            _tension = Mathf.Max(0, _tension - decay);
            OnTensionChanged?.Invoke(FactionA, FactionB, _tension);
        }
    }

    /// <summary>
    /// Interface for tension modifiers (e.g., ScriptableObjects).
    /// </summary>
    public interface ITensionModifier
    {
        float GetModifier();
    }

    /// <summary>
    /// Represents an active war between two factions.
    /// </summary>
    public class WarState
    {
        public string FactionA { get; }
        public string FactionB { get; }
        public float WarExhaustionA { get; private set; }
        public float WarExhaustionB { get; private set; }
        public bool IsActive { get; private set; } = true;
        // TODO: Add alliances, battle events, outcomes, etc.

        public WarState(string a, string b)
        {
            FactionA = a;
            FactionB = b;
            WarExhaustionA = 0f;
            WarExhaustionB = 0f;
        }

        public void Simulate(float deltaTime)
        {
            // Example: Increase exhaustion
            WarExhaustionA += deltaTime * UnityEngine.Random.Range(0.1f, 0.5f);
            WarExhaustionB += deltaTime * UnityEngine.Random.Range(0.1f, 0.5f);
            // TODO: Simulate battles, resource impact, population migration, etc.
        }

        public void EndWar()
        {
            IsActive = false;
            // TODO: Trigger peace negotiation, resource/territory exchange
        }
    }
} 