using System;
using System.Collections.Generic;
using UnityEngine;

namespace VisualDM.AI
{
    /// <summary>
    /// Global manager for all active rumors in the game world.
    /// Handles creation, lookup, removal, and integration with propagation, mutation, and believability systems.
    /// </summary>
    public class RumorManager : MonoBehaviour
    {
        private static RumorManager _instance;
        public static RumorManager Instance
        {
            get
            {
                if (_instance == null)
                {
                    var go = new GameObject("RumorManager");
                    _instance = go.AddComponent<RumorManager>();
                    DontDestroyOnLoad(go);
                }
                return _instance;
            }
        }

        // Global registry of rumors by unique ID
        private readonly Dictionary<string, Rumor> _rumors = new();

        /// <summary>
        /// Create a new rumor and add it to the registry.
        /// </summary>
        public Rumor CreateRumor(string coreContent, RumorOriginMetadata origin, float importance = 0.5f, List<string> tags = null)
        {
            var rumor = new Rumor
            {
                CoreContent = coreContent,
                Origin = origin,
                Importance = importance,
            };
            string rumorId = GenerateRumorId(rumor);
            _rumors[rumorId] = rumor;
            return rumor;
        }

        /// <summary>
        /// Get a rumor by its unique ID.
        /// </summary>
        public Rumor GetRumor(string rumorId)
        {
            _rumors.TryGetValue(rumorId, out var rumor);
            return rumor;
        }

        /// <summary>
        /// Remove a rumor from the registry.
        /// </summary>
        public void RemoveRumor(string rumorId)
        {
            _rumors.Remove(rumorId);
        }

        /// <summary>
        /// Get all active rumors.
        /// </summary>
        public IReadOnlyDictionary<string, Rumor> GetAllRumors() => _rumors;

        /// <summary>
        /// Generate a unique rumor ID based on core content and origin.
        /// </summary>
        private string GenerateRumorId(Rumor rumor)
        {
            string baseString = rumor.CoreContent + (rumor.Origin?.OriginNpcId ?? "") + (rumor.Origin?.OriginTimestamp.ToString() ?? "");
            return baseString.GetHashCode().ToString();
        }

        /// <summary>
        /// Serialize all rumors for save game compatibility.
        /// </summary>
        public string Serialize()
        {
            // Use a DTO or lightweight serialization for performance
            return JsonUtility.ToJson(new RumorListWrapper { Rumors = new List<Rumor>(_rumors.Values) });
        }

        /// <summary>
        /// Deserialize rumors from save data.
        /// </summary>
        public void Deserialize(string json)
        {
            var wrapper = JsonUtility.FromJson<RumorListWrapper>(json);
            _rumors.Clear();
            if (wrapper?.Rumors != null)
            {
                foreach (var rumor in wrapper.Rumors)
                {
                    string rumorId = GenerateRumorId(rumor);
                    _rumors[rumorId] = rumor;
                }
            }
        }

        [Serializable]
        private class RumorListWrapper
        {
            public List<Rumor> Rumors;
        }
    }
} 