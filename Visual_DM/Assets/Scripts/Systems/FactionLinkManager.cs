using System;
using System.Collections.Generic;
using Visual_DM.Entities;
using UnityEngine;

namespace Visual_DM.Systems
{
    /// <summary>
    /// Manages bidirectional links between Factions and FactionArcs, provides APIs for linking, querying, player interaction, persistence, and integration.
    /// </summary>
    public class FactionLinkManager
    {
        private static FactionLinkManager _instance;
        public static FactionLinkManager Instance => _instance ?? (_instance = new FactionLinkManager());

        private Dictionary<Faction, List<FactionArc>> factionToArcs = new Dictionary<Faction, List<FactionArc>>();
        private Dictionary<FactionArc, List<Faction>> arcToFactions = new Dictionary<FactionArc, List<Faction>>();

        private FactionLinkManager() { }

        /// <summary>
        /// Link a Faction and a FactionArc bidirectionally.
        /// </summary>
        public void Link(Faction faction, FactionArc arc)
        {
            if (!factionToArcs.ContainsKey(faction))
                factionToArcs[faction] = new List<FactionArc>();
            if (!arcToFactions.ContainsKey(arc))
                arcToFactions[arc] = new List<Faction>();

            if (!factionToArcs[faction].Contains(arc))
            {
                factionToArcs[faction].Add(arc);
                arcToFactions[arc].Add(faction);
                faction.AddArc(arc);
                arc.AddFaction(faction);
            }
        }

        /// <summary>
        /// Unlink a Faction and a FactionArc bidirectionally.
        /// </summary>
        public void Unlink(Faction faction, FactionArc arc)
        {
            if (factionToArcs.ContainsKey(faction))
                factionToArcs[faction].Remove(arc);
            if (arcToFactions.ContainsKey(arc))
                arcToFactions[arc].Remove(faction);
            faction.RemoveArc(arc);
            arc.RemoveFaction(faction);
        }

        /// <summary>
        /// Get all arcs for a given faction.
        /// </summary>
        public List<FactionArc> GetArcsForFaction(Faction faction)
        {
            return factionToArcs.ContainsKey(faction) ? factionToArcs[faction] : new List<FactionArc>();
        }

        /// <summary>
        /// Get all factions for a given arc.
        /// </summary>
        public List<Faction> GetFactionsForArc(FactionArc arc)
        {
            return arcToFactions.ContainsKey(arc) ? arcToFactions[arc] : new List<Faction>();
        }

        /// <summary>
        /// Register a faction for status change event propagation.
        /// </summary>
        public void RegisterFactionStatusListener(Faction faction)
        {
            faction.OnStatusChanged += OnFactionStatusChanged;
        }

        private void OnFactionStatusChanged(Faction faction, string property, int oldValue, int newValue)
        {
            // Propagate to relevant arcs
            foreach (var arc in GetArcsForFaction(faction))
            {
                // Custom logic for arc progression
                // arc.HandleFactionStatusChange(faction, property, oldValue, newValue);
            }
        }

        /// <summary>
        /// Register all factions for status change event propagation.
        /// </summary>
        public void RegisterAllFactions(IEnumerable<Faction> factions)
        {
            foreach (var faction in factions)
            {
                RegisterFactionStatusListener(faction);
            }
        }

        /// <summary>
        /// Perform an atomic update to a faction's status and propagate changes to arcs.
        /// </summary>
        // Transaction logic for atomic updates
        public void UpdateFactionStatusAtomic(Faction faction, Action<Faction> updateAction)
        {
            // Begin transaction (could be extended for rollback)
            var affectedArcs = GetArcsForFaction(faction);
            updateAction(faction);
            // After update, propagate to all affected arcs
            foreach (var arc in affectedArcs)
            {
                // arc.HandleFactionStatusChange(faction, ...);
            }
            // End transaction
        }

        // Player interaction API
        public bool PlayerInfluenceFactionRelationship(Faction playerFaction, Faction targetFaction, FactionRelationshipType newType, out string feedback)
        {
            // Validation logic (example: prevent self-relationship)
            if (playerFaction == targetFaction)
            {
                feedback = "Cannot change relationship with self.";
                return false;
            }
            // Additional validation can be added here
            FactionRelationshipManager.Instance.SetRelationship(playerFaction, targetFaction, newType);
            feedback = $"Relationship between {playerFaction.Name} and {targetFaction.Name} set to {newType}.";
            return true;
        }

        public bool PlayerProgressArc(FactionArc arc, Faction actingFaction, int newStage, out string feedback)
        {
            // Validation logic (example: check if actingFaction is part of arc)
            if (!arc.Factions.Contains(actingFaction))
            {
                feedback = $"Faction {actingFaction.Name} is not part of this arc.";
                return false;
            }
            // Example: Only allow forward progression
            if (newStage <= arc.Stage)
            {
                feedback = "Cannot regress or repeat arc stage.";
                return false;
            }
            arc.SetStage(newStage);
            feedback = $"Arc {arc.Title} progressed to stage {newStage} by {actingFaction.Name}.";
            return true;
        }

        // Persistence (serialization/deserialization)
        [Serializable]
        private class FactionLinkData
        {
            public List<string> factionIds = new List<string>();
            public List<string> arcIds = new List<string>();
            public List<LinkEntry> links = new List<LinkEntry>();
        }
        [Serializable]
        private class LinkEntry
        {
            public string factionId;
            public string arcId;
        }

        public string SerializeLinks()
        {
            var data = new FactionLinkData();
            foreach (var kvp in factionToArcs)
            {
                data.factionIds.Add(kvp.Key.Id);
                foreach (var arc in kvp.Value)
                {
                    data.arcIds.Add(arc.Id);
                    data.links.Add(new LinkEntry { factionId = kvp.Key.Id, arcId = arc.Id });
                }
            }
            return JsonUtility.ToJson(data);
        }

        public void DeserializeLinks(string json, Func<string, Faction> factionResolver, Func<string, FactionArc> arcResolver)
        {
            var data = JsonUtility.FromJson<FactionLinkData>(json);
            factionToArcs.Clear();
            arcToFactions.Clear();
            foreach (var link in data.links)
            {
                var faction = factionResolver(link.factionId);
                var arc = arcResolver(link.arcId);
                if (faction != null && arc != null)
                {
                    Link(faction, arc);
                }
            }
        }

        // Integration points for RegionalArc and GlobalArc systems
        // These would be implemented as the corresponding systems are developed
        public void IntegrateWithRegionalArc(object regionalArc)
        {
            // TODO: Implement integration logic
        }

        public void IntegrateWithGlobalArc(object globalArc)
        {
            // TODO: Implement integration logic
        }
    }
}