using System;
using System.Collections.Generic;
using VisualDM.Systems.EventSystem;
using VisualDM.Utilities;

namespace VisualDM.NPC
{
    public enum RelationshipState { Neutral, Rival, Nemesis }

    public class RelationshipStateChangedEvent
    {
        public string NPCId { get; }
        public string TargetId { get; }
        public RelationshipState OldState { get; }
        public RelationshipState NewState { get; }
        public float Intensity { get; }
        public DateTime Timestamp { get; }
        public RelationshipStateChangedEvent(string npcId, string targetId, RelationshipState oldState, RelationshipState newState, float intensity)
        {
            NPCId = npcId;
            TargetId = targetId;
            OldState = oldState;
            NewState = newState;
            Intensity = intensity;
            Timestamp = DateTime.UtcNow;
        }
    }

    public class RelationshipStateMachine
    {
        private readonly string _npcId;
        private readonly Dictionary<string, RelationshipState> _states = new();
        private readonly Dictionary<string, float> _intensity = new();
        private readonly Dictionary<string, DateTime> _nemesisCooldowns = new();
        private readonly float _rivalThreshold = 50f;
        private readonly float _nemesisThreshold = 100f;
        private readonly float _decayRate = 1f; // per minute
        private readonly TimeSpan _nemesisCooldown = TimeSpan.FromMinutes(30);

        public RelationshipStateMachine(string npcId)
        {
            _npcId = npcId;
        }

        public RelationshipState GetState(string targetId)
        {
            if (_states.TryGetValue(targetId, out var state))
                return state;
            return RelationshipState.Neutral;
        }

        public float GetIntensity(string targetId)
        {
            _intensity.TryGetValue(targetId, out var value);
            return value;
        }

        public bool IsNemesisCooldown(string targetId)
        {
            if (_nemesisCooldowns.TryGetValue(targetId, out var until))
                return DateTime.UtcNow < until;
            return false;
        }

        public void RegisterEvent(string targetId, float eventScore)
        {
            if (IsNemesisCooldown(targetId))
                return;
            float oldIntensity = GetIntensity(targetId);
            float newIntensity = Math.Max(0, oldIntensity + eventScore);
            _intensity[targetId] = newIntensity;
            var oldState = GetState(targetId);
            var newState = CalculateState(newIntensity);
            if (newState != oldState)
            {
                _states[targetId] = newState;
                EventBus.Instance.Publish(new RelationshipStateChangedEvent(_npcId, targetId, oldState, newState, newIntensity));
                if (newState == RelationshipState.Nemesis)
                    _nemesisCooldowns[targetId] = DateTime.UtcNow + _nemesisCooldown;
            }
        }

        public void DecayAll(float deltaMinutes)
        {
            foreach (var targetId in new List<string>(_intensity.Keys))
            {
                float old = _intensity[targetId];
                float decayed = Math.Max(0, old - _decayRate * deltaMinutes);
                _intensity[targetId] = decayed;
                var oldState = GetState(targetId);
                var newState = CalculateState(decayed);
                if (newState != oldState)
                {
                    _states[targetId] = newState;
                    EventBus.Instance.Publish(new RelationshipStateChangedEvent(_npcId, targetId, oldState, newState, decayed));
                }
            }
        }

        private RelationshipState CalculateState(float intensity)
        {
            if (intensity >= _nemesisThreshold) return RelationshipState.Nemesis;
            if (intensity >= _rivalThreshold) return RelationshipState.Rival;
            return RelationshipState.Neutral;
        }

        // Persistence hooks (to be integrated with storage system)
        public Dictionary<string, object> SaveState()
        {
            return new Dictionary<string, object>
            {
                { "states", new Dictionary<string, RelationshipState>(_states) },
                { "intensity", new Dictionary<string, float>(_intensity) },
                { "nemesisCooldowns", new Dictionary<string, DateTime>(_nemesisCooldowns) }
            };
        }
        public void LoadState(Dictionary<string, object> data)
        {
            if (data.TryGetValue("states", out var s) && s is Dictionary<string, RelationshipState> states)
                foreach (var kv in states) _states[kv.Key] = kv.Value;
            if (data.TryGetValue("intensity", out var i) && i is Dictionary<string, float> intensity)
                foreach (var kv in intensity) _intensity[kv.Key] = kv.Value;
            if (data.TryGetValue("nemesisCooldowns", out var n) && n is Dictionary<string, DateTime> cooldowns)
                foreach (var kv in cooldowns) _nemesisCooldowns[kv.Key] = kv.Value;
        }

        // --- Nemesis/Rival System Extensions ---
        public bool IsRival(string targetId) => GetState(targetId) == RelationshipState.Rival;
        public bool IsNemesis(string targetId) => GetState(targetId) == RelationshipState.Nemesis;

        public void PromoteToRival(string targetId, float initialIntensity = 51f)
        {
            _intensity[targetId] = Math.Max(_intensity.GetValueOrDefault(targetId, 0f), initialIntensity);
            _states[targetId] = RelationshipState.Rival;
            EventBus.Instance.Publish(new RelationshipStateChangedEvent(_npcId, targetId, RelationshipState.Neutral, RelationshipState.Rival, initialIntensity));
        }

        public void PromoteToNemesis(string targetId, float initialIntensity = 101f)
        {
            _intensity[targetId] = Math.Max(_intensity.GetValueOrDefault(targetId, 0f), initialIntensity);
            _states[targetId] = RelationshipState.Nemesis;
            _nemesisCooldowns[targetId] = DateTime.UtcNow + _nemesisCooldown;
            EventBus.Instance.Publish(new RelationshipStateChangedEvent(_npcId, targetId, RelationshipState.Rival, RelationshipState.Nemesis, initialIntensity));
        }

        public IEnumerable<string> GetRivals()
        {
            foreach (var kv in _states)
                if (kv.Value == RelationshipState.Rival)
                    yield return kv.Key;
        }
        public IEnumerable<string> GetNemeses()
        {
            foreach (var kv in _states)
                if (kv.Value == RelationshipState.Nemesis)
                    yield return kv.Key;
        }
        // Integration hook: update from GrudgePointManager
        public void SyncWithGrudgePoints(string targetId, int grudgePoints)
        {
            float oldIntensity = GetIntensity(targetId);
            float newIntensity = Math.Max(0, oldIntensity + grudgePoints);
            _intensity[targetId] = newIntensity;
            var oldState = GetState(targetId);
            var newState = CalculateState(newIntensity);
            if (newState != oldState)
            {
                _states[targetId] = newState;
                EventBus.Instance.Publish(new RelationshipStateChangedEvent(_npcId, targetId, oldState, newState, newIntensity));
                if (newState == RelationshipState.Nemesis)
                    _nemesisCooldowns[targetId] = DateTime.UtcNow + _nemesisCooldown;
            }
        }
    }
}