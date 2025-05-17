using System;
using System.Collections.Generic;
using UnityEngine;

namespace VisualDM.Quest
{
    /// <summary>
    /// Singleton system for tracking player reputation with factions.
    /// </summary>
    public class FactionRelationshipSystem : MonoBehaviour
    {
        private static FactionRelationshipSystem _instance;
        public static FactionRelationshipSystem Instance
        {
            get
            {
                if (_instance == null)
                {
                    var go = new GameObject("FactionRelationshipSystem");
                    _instance = go.AddComponent<FactionRelationshipSystem>();
                    DontDestroyOnLoad(go);
                }
                return _instance;
            }
        }

        public enum FactionStanding { Hostile, Neutral, Friendly, Allied }

        [Serializable]
        public class ReputationChangeEvent : UnityEngine.Events.UnityEvent<string, float> { }

        [SerializeField] private Dictionary<string, float> factionReputation = new Dictionary<string, float>();
        public ReputationChangeEvent OnReputationChanged = new ReputationChangeEvent();

        // Thresholds for standings
        public float HostileThreshold = -50f;
        public float NeutralThreshold = 0f;
        public float FriendlyThreshold = 50f;
        public float AlliedThreshold = 100f;

        /// <summary>
        /// Gets the current reputation with a faction.
        /// </summary>
        public float GetReputation(string faction)
        {
            factionReputation.TryGetValue(faction, out var value);
            return value;
        }

        /// <summary>
        /// Sets the reputation with a faction and notifies listeners.
        /// </summary>
        public void SetReputation(string faction, float value)
        {
            factionReputation[faction] = value;
            OnReputationChanged.Invoke(faction, value);
        }

        /// <summary>
        /// Modifies the reputation with a faction by delta.
        /// </summary>
        public void ModifyReputation(string faction, float delta)
        {
            SetReputation(faction, GetReputation(faction) + delta);
        }

        /// <summary>
        /// Gets the standing with a faction based on reputation value.
        /// </summary>
        public FactionStanding GetStanding(string faction)
        {
            float rep = GetReputation(faction);
            if (rep <= HostileThreshold) return FactionStanding.Hostile;
            if (rep < FriendlyThreshold) return rep < NeutralThreshold ? FactionStanding.Neutral : FactionStanding.Friendly;
            if (rep < AlliedThreshold) return FactionStanding.Friendly;
            return FactionStanding.Allied;
        }
    }
} 