using System;
using System.Collections.Generic;
using System.Linq;

namespace VisualDM.Entities
{
    public class Faction
    {
        public string Id { get; private set; }
        public string Name { get; set; }
        public string Description { get; set; }
        public List<FactionArc> FactionArcs { get; private set; } = new List<FactionArc>();

        // Example status properties
        public int Reputation { get; private set; }
        public int Power { get; private set; }
        public int TerritoryControl { get; private set; }

        // Event for status changes
        public event Action<Faction, string, int, int> OnStatusChanged;

        // --- Advanced Faction System Extensions ---
        /// <summary>
        /// The parent faction in a hierarchical structure. Null if this is a root faction.
        /// </summary>
        public Faction ParentFaction { get; private set; }
        /// <summary>
        /// List of child factions (e.g., from schisms).
        /// </summary>
        public List<Faction> ChildFactions { get; private set; } = new List<Faction>();
        /// <summary>
        /// List of ancestor faction IDs representing the schism lineage.
        /// </summary>
        public List<string> SchismLineage { get; private set; } = new List<string>(); // Faction IDs
        /// <summary>
        /// Maps entity IDs to their allegiance object for this faction.
        /// </summary>
        public Dictionary<string, FactionAllegiance> Allegiances { get; private set; } = new Dictionary<string, FactionAllegiance>();
        /// <summary>
        /// Maps other faction IDs to the relationship weight (affinity/hostility).
        /// </summary>
        public Dictionary<string, float> RelationshipWeights { get; private set; } = new Dictionary<string, float>();

        public Faction(string id, string name, string description)
        {
            Id = id;
            Name = name;
            Description = description;
        }

        public void AddArc(FactionArc arc)
        {
            if (!FactionArcs.Contains(arc))
            {
                FactionArcs.Add(arc);
                arc.AddFactionInternal(this);
            }
        }

        public void RemoveArc(FactionArc arc)
        {
            if (FactionArcs.Contains(arc))
            {
                FactionArcs.Remove(arc);
                arc.RemoveFactionInternal(this);
            }
        }

        // Example method to update reputation
        public void SetReputation(int newReputation)
        {
            if (Reputation != newReputation)
            {
                int oldValue = Reputation;
                Reputation = newReputation;
                OnStatusChanged?.Invoke(this, "Reputation", oldValue, newReputation);
            }
        }

        // Example method to update power
        public void SetPower(int newPower)
        {
            if (Power != newPower)
            {
                int oldValue = Power;
                Power = newPower;
                OnStatusChanged?.Invoke(this, "Power", oldValue, newPower);
            }
        }

        // Example method to update territory control
        public void SetTerritoryControl(int newTerritory)
        {
            if (TerritoryControl != newTerritory)
            {
                int oldValue = TerritoryControl;
                TerritoryControl = newTerritory;
                OnStatusChanged?.Invoke(this, "TerritoryControl", oldValue, newTerritory);
            }
        }

        // Prevent infinite recursion in AddArc/RemoveArc
        internal void AddArcInternal(FactionArc arc)
        {
            if (!FactionArcs.Contains(arc))
                FactionArcs.Add(arc);
        }

        internal void RemoveArcInternal(FactionArc arc)
        {
            FactionArcs.Remove(arc);
        }

        /// <summary>
        /// Sets the parent faction and updates the parent's child list.
        /// </summary>
        public void SetParentFaction(Faction parent)
        {
            ParentFaction = parent;
            if (parent != null && !parent.ChildFactions.Contains(this))
                parent.ChildFactions.Add(this);
        }
        /// <summary>
        /// Adds a child faction and sets this as its parent.
        /// </summary>
        public void AddChildFaction(Faction child)
        {
            if (!ChildFactions.Contains(child))
            {
                ChildFactions.Add(child);
                child.ParentFaction = this;
            }
        }
        /// <summary>
        /// Adds an ancestor faction ID to the schism lineage.
        /// </summary>
        public void AddSchism(string ancestorId)
        {
            if (!SchismLineage.Contains(ancestorId))
                SchismLineage.Add(ancestorId);
        }
        /// <summary>
        /// Sets the relationship weight with another faction.
        /// </summary>
        public void SetRelationshipWeight(string otherFactionId, float weight)
        {
            RelationshipWeights[otherFactionId] = weight;
        }
        /// <summary>
        /// Gets the relationship weight with another faction.
        /// </summary>
        public float GetRelationshipWeight(string otherFactionId)
        {
            return RelationshipWeights.TryGetValue(otherFactionId, out var w) ? w : 0f;
        }
        /// <summary>
        /// Sets the allegiance object for an entity.
        /// </summary>
        public void SetAllegiance(string entityId, FactionAllegiance allegiance)
        {
            Allegiances[entityId] = allegiance;
        }
        /// <summary>
        /// Gets the allegiance object for an entity.
        /// </summary>
        public FactionAllegiance GetAllegiance(string entityId)
        {
            return Allegiances.TryGetValue(entityId, out var a) ? a : null;
        }
        /// <summary>
        /// Serializes advanced faction state for save/load.
        /// </summary>
        public Dictionary<string, object> SaveAdvancedState()
        {
            return new Dictionary<string, object>
            {
                {"ParentFactionId", ParentFaction?.Id},
                {"ChildFactionIds", ChildFactions.ConvertAll(f => f.Id)},
                {"SchismLineage", new List<string>(SchismLineage)},
                {"RelationshipWeights", new Dictionary<string, float>(RelationshipWeights)},
                {"Allegiances", Allegiances.ToDictionary(kv => kv.Key, kv => (object)kv.Value)}
            };
        }
        /// <summary>
        /// Loads advanced faction state from serialized data.
        /// </summary>
        public void LoadAdvancedState(Dictionary<string, object> data, Func<string, Faction> factionResolver)
        {
            if (data.TryGetValue("ParentFactionId", out var pid) && pid is string parentId && !string.IsNullOrEmpty(parentId))
                SetParentFaction(factionResolver(parentId));
            if (data.TryGetValue("ChildFactionIds", out var cids) && cids is List<string> childIds)
                foreach (var cid in childIds) AddChildFaction(factionResolver(cid));
            if (data.TryGetValue("SchismLineage", out var lineage) && lineage is List<string> lineageList)
                SchismLineage = new List<string>(lineageList);
            if (data.TryGetValue("RelationshipWeights", out var rels) && rels is Dictionary<string, float> relDict)
                RelationshipWeights = new Dictionary<string, float>(relDict);
            if (data.TryGetValue("Allegiances", out var al) && al is Dictionary<string, object> allegiances)
            {
                // TODO: Implement deserialization logic for FactionAllegiance objects
                Allegiances = new Dictionary<string, FactionAllegiance>();
            }
        }
    }

    // --- Helper class for allegiance ---
    /// <summary>
    /// Represents an entity's allegiance to a faction, including affinity and status.
    /// </summary>
    public class FactionAllegiance
    {
        public string EntityId { get; set; }
        public Faction Faction { get; set; }
        public float Affinity { get; set; } // -1 to 1
        public DateTime LastChanged { get; set; }
        public AllegianceStatus Status { get; set; }
        public enum AllegianceStatus { Active, Inactive, Switching, Banned }
        /// <summary>
        /// Create a new allegiance object.
        /// </summary>
        public FactionAllegiance(string entityId, Faction faction, float affinity, AllegianceStatus status = AllegianceStatus.Active)
        {
            EntityId = entityId;
            Faction = faction;
            Affinity = affinity;
            Status = status;
            LastChanged = DateTime.UtcNow;
        }
    }
}