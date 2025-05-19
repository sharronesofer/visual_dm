using System;
using System.Collections.Generic;
using VisualDM.Systems.EventSystem;
using VisualDM.Systems.Utilities;

namespace VisualDM.Entities
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

        /// <summary>
        /// Canonical relationship types supported by the system.
        /// </summary>
        public enum CanonicalRelationshipType { Faction, Quest, Spatial, Auth, Rivalry }

        /// <summary>
        /// Represents a character's relationship with a faction, including reputation and standing.
        /// </summary>
        [Serializable]
        public class FactionRelationship
        {
            /// <summary>Faction identifier.</summary>
            public string FactionId;
            /// <summary>Reputation score with the faction.</summary>
            public int Reputation;
            /// <summary>Standing (e.g., Ally, Neutral, Enemy).</summary>
            public string Standing;
        }

        /// <summary>
        /// Represents a character's relationship to a quest, including status and progress.
        /// </summary>
        [Serializable]
        public class QuestRelationship
        {
            /// <summary>Quest identifier.</summary>
            public string QuestId;
            /// <summary>Status (active, completed, failed).</summary>
            public string Status;
            /// <summary>Progress (0.0 to 1.0).</summary>
            public float Progress;
        }

        /// <summary>
        /// Represents a spatial relationship (e.g., proximity) to a location.
        /// </summary>
        [Serializable]
        public class SpatialRelationship
        {
            /// <summary>Location identifier.</summary>
            public string LocationId;
            /// <summary>Distance to the location.</summary>
            public float Distance;
        }

        /// <summary>
        /// Represents an authentication/ownership relationship between a user and a character.
        /// </summary>
        [Serializable]
        public class AuthRelationship
        {
            /// <summary>User identifier.</summary>
            public string UserId;
            /// <summary>List of permissions (e.g., play, edit).</summary>
            public List<string> Permissions;
            /// <summary>True if the user is the owner.</summary>
            public bool Owner;
        }

        // Canonical relationship stores
        private readonly Dictionary<string, FactionRelationship> _factionRelationships = new();
        private readonly Dictionary<string, QuestRelationship> _questRelationships = new();
        private readonly Dictionary<string, SpatialRelationship> _spatialRelationships = new();
        private readonly Dictionary<string, AuthRelationship> _authRelationships = new();

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

        /// <summary>
        /// Update or add a faction relationship.
        /// </summary>
        /// <param name="factionId">Faction identifier.</param>
        /// <param name="reputation">Reputation score.</param>
        /// <param name="standing">Standing string.</param>
        public void UpdateFactionRelationship(string factionId, int reputation, string standing)
        {
            _factionRelationships[factionId] = new FactionRelationship { FactionId = factionId, Reputation = reputation, Standing = standing };
        }

        /// <summary>
        /// Update or add a quest relationship.
        /// </summary>
        /// <param name="questId">Quest identifier.</param>
        /// <param name="status">Quest status.</param>
        /// <param name="progress">Quest progress.</param>
        public void UpdateQuestRelationship(string questId, string status, float progress)
        {
            _questRelationships[questId] = new QuestRelationship { QuestId = questId, Status = status, Progress = progress };
        }

        /// <summary>
        /// Update or add a spatial relationship.
        /// </summary>
        /// <param name="locationId">Location identifier.</param>
        /// <param name="distance">Distance to location.</param>
        public void UpdateSpatialRelationship(string locationId, float distance)
        {
            _spatialRelationships[locationId] = new SpatialRelationship { LocationId = locationId, Distance = distance };
        }

        /// <summary>
        /// Update or add an authentication relationship.
        /// </summary>
        /// <param name="userId">User identifier.</param>
        /// <param name="permissions">List of permissions.</param>
        /// <param name="owner">True if user is owner.</param>
        public void UpdateAuthRelationship(string userId, List<string> permissions, bool owner)
        {
            _authRelationships[userId] = new AuthRelationship { UserId = userId, Permissions = permissions, Owner = owner };
        }

        /// <summary>
        /// Serialize all canonical relationships for backend sync.
        /// </summary>
        /// <returns>Dictionary of relationship type to list of relationships.</returns>
        public Dictionary<string, object> SerializeCanonicalRelationships()
        {
            return new Dictionary<string, object>
            {
                { "faction", new List<FactionRelationship>(_factionRelationships.Values) },
                { "quest", new List<QuestRelationship>(_questRelationships.Values) },
                { "spatial", new List<SpatialRelationship>(_spatialRelationships.Values) },
                { "auth", new List<AuthRelationship>(_authRelationships.Values) }
            };
        }

        /// <summary>
        /// Load canonical relationships from backend data.
        /// </summary>
        /// <param name="data">Dictionary of relationship type to list of relationships.</param>
        public void LoadCanonicalRelationships(Dictionary<string, object> data)
        {
            if (data.TryGetValue("faction", out var f) && f is List<FactionRelationship> factions)
                foreach (var rel in factions) _factionRelationships[rel.FactionId] = rel;
            if (data.TryGetValue("quest", out var q) && q is List<QuestRelationship> quests)
                foreach (var rel in quests) _questRelationships[rel.QuestId] = rel;
            if (data.TryGetValue("spatial", out var s) && s is List<SpatialRelationship> spatials)
                foreach (var rel in spatials) _spatialRelationships[rel.LocationId] = rel;
            if (data.TryGetValue("auth", out var a) && a is List<AuthRelationship> auths)
                foreach (var rel in auths) _authRelationships[rel.UserId] = rel;
        }

        /// <summary>
        /// Synchronize canonical relationships with the backend (REST or WebSocket).
        /// </summary>
        /// <remarks>
        /// This method should be called after any relationship update to push changes to the backend,
        /// or periodically to pull the latest state. Actual network logic should be implemented in the
        /// appropriate service or manager class.
        /// </remarks>
        public void SyncWithBackend()
        {
            // TODO: Implement backend sync logic (REST API or WebSocket message)
            // Example: BackendAPI.UpdateRelationships(_npcId, SerializeCanonicalRelationships());
            // Or: WebSocketManager.SendRelationshipUpdate(_npcId, SerializeCanonicalRelationships());
        }
    }
}