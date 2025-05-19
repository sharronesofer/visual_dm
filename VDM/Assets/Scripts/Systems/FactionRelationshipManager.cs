using System;
using System.Collections.Generic;
using VisualDM.Entities;
using UnityEngine;

namespace VisualDM.Systems
{
    public enum FactionRelationshipType
    {
        Neutral,
        Allied,
        Hostile
    }

    public class FactionRelationshipManager
    {
        private static FactionRelationshipManager _instance;
        public static FactionRelationshipManager Instance => _instance ?? (_instance = new FactionRelationshipManager());

        private Dictionary<(Faction, Faction), FactionRelationshipType> relationships = new Dictionary<(Faction, Faction), FactionRelationshipType>();

        private FactionRelationshipManager() { }

        // Propagate relationship changes to arcs and resolve conflicts
        private void PropagateRelationshipChange(Faction a, Faction b, FactionRelationshipType type)
        {
            var arcsA = FactionLinkManager.Instance.GetArcsForFaction(a);
            var arcsB = FactionLinkManager.Instance.GetArcsForFaction(b);
            foreach (var arc in arcsA)
            {
                // arc.HandleFactionRelationshipChange(a, b, type);
            }
            foreach (var arc in arcsB)
            {
                // arc.HandleFactionRelationshipChange(b, a, type);
            }
            // Example: Conflict resolution logic (placeholder)
            if (type == FactionRelationshipType.Hostile)
            {
                // If both factions are in the same arc, trigger conflict resolution
                foreach (var arc in arcsA)
                {
                    if (arcsB.Contains(arc))
                    {
                        // arc.ResolveFactionConflict(a, b);
                    }
                }
            }
        }

        public void SetRelationship(Faction a, Faction b, FactionRelationshipType type)
        {
            relationships[(a, b)] = type;
            relationships[(b, a)] = type;
            PropagateRelationshipChange(a, b, type);
        }

        public FactionRelationshipType GetRelationship(Faction a, Faction b)
        {
            if (relationships.TryGetValue((a, b), out var type))
                return type;
            return FactionRelationshipType.Neutral;
        }

        public void RemoveRelationship(Faction a, Faction b)
        {
            relationships.Remove((a, b));
            relationships.Remove((b, a));
        }

        // Persistence (serialization/deserialization)
        [Serializable]
        private class RelationshipEntry
        {
            public string factionAId;
            public string factionBId;
            public FactionRelationshipType type;
        }

        public string SerializeRelationships()
        {
            var entries = new List<RelationshipEntry>();
            foreach (var kvp in relationships)
            {
                entries.Add(new RelationshipEntry
                {
                    factionAId = kvp.Key.Item1.Id,
                    factionBId = kvp.Key.Item2.Id,
                    type = kvp.Value
                });
            }
            return JsonUtility.ToJson(new { relationships = entries });
        }

        public void DeserializeRelationships(string json, Func<string, Faction> factionResolver)
        {
            var wrapper = JsonUtility.FromJson<RelationshipWrapper>(json);
            relationships.Clear();
            foreach (var entry in wrapper.relationships)
            {
                var a = factionResolver(entry.factionAId);
                var b = factionResolver(entry.factionBId);
                if (a != null && b != null)
                {
                    relationships[(a, b)] = entry.type;
                }
            }
        }

        [Serializable]
        private class RelationshipWrapper
        {
            public List<RelationshipEntry> relationships;
        }
    }
}