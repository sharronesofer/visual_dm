using System;
using System.Collections.Generic;
using VisualDM.UI;
using VisualDM.Systems.EventSystem;
using UnityEngine;

namespace VisualDM.World
{
    public class FactionSystem
    {
        public class Faction
        {
            public string Name;
            public float Influence;
            public HashSet<string> Territories;
        }

        private Dictionary<string, Faction> factions = new Dictionary<string, Faction>();
        private Dictionary<(string, string), float> relationships = new Dictionary<(string, string), float>();

        // --- Advanced Faction System Extensions ---
        public event Action<Faction, Faction, float> OnRelationshipChanged;
        public event Action<Faction, Faction> OnSchism;
        public event Action<string, Faction, Faction> OnAllegianceChanged; // entityId, old, new

        public void AddFaction(string name)
        {
            if (!factions.ContainsKey(name))
                factions[name] = new Faction { Name = name, Influence = 0f, Territories = new HashSet<string>() };
        }

        public void SetRelationship(string factionA, string factionB, float value)
        {
            relationships[(factionA, factionB)] = value;
            relationships[(factionB, factionA)] = value;
        }

        public float GetRelationship(string factionA, string factionB)
        {
            if (relationships.TryGetValue((factionA, factionB), out float value))
                return value;
            return 0f;
        }

        public void UpdateInfluence(string faction, float delta)
        {
            if (factions.TryGetValue(faction, out var f))
                f.Influence += delta;
        }

        public void AddTerritory(string faction, string territory)
        {
            if (factions.TryGetValue(faction, out var f))
                f.Territories.Add(territory);
        }

        public void RemoveTerritory(string faction, string territory)
        {
            if (factions.TryGetValue(faction, out var f))
                f.Territories.Remove(territory);
        }

        public IEnumerable<Faction> GetAllFactions() => factions.Values;

        // Schism logic
        public Faction CreateSchism(Faction parent, string newFactionId, string newName, string newDesc)
        {
            var child = new Faction(newFactionId, newName, newDesc);
            child.SetParentFaction(parent);
            child.AddSchism(parent.Id);
            // Inherit properties/resources/relationships
            foreach (var kv in parent.RelationshipWeights)
                child.SetRelationshipWeight(kv.Key, kv.Value);
            // Inherit allegiances (split based on affinity)
            foreach (var kv in parent.Allegiances)
            {
                if (kv.Value.Affinity < 0) continue; // Only positive affinity
                if (kv.Value.Affinity > 0.5f) // Example: high affinity splits
                    child.SetAllegiance(kv.Key, new FactionAllegiance(kv.Key, child, kv.Value.Affinity * 0.8f));
            }
            AddFaction(child.Name);
            OnSchism?.Invoke(parent, child);
            // Fire UI feedback
            SystemsManager.Instance?.ShowFactionSchism(Vector2.zero, parent.Name, child.Name);
            // Publish event
            EventBus.Instance?.Publish(new FactionSchismEvent(parent, child));
            return child;
        }
        // Affinity-based switching
        public void SwitchAllegiance(string entityId, Faction from, Faction to, float threshold = 0.6f)
        {
            var oldAlleg = from.GetAllegiance(entityId);
            if (oldAlleg == null || oldAlleg.Affinity < threshold) return;
            from.SetAllegiance(entityId, null);
            to.SetAllegiance(entityId, new FactionAllegiance(entityId, to, 1.0f));
            OnAllegianceChanged?.Invoke(entityId, from, to);
            // Fire UI feedback
            SystemsManager.Instance?.ShowFactionSwitch(Vector2.zero, entityId, from.Name, to.Name);
            // Publish event
            EventBus.Instance?.Publish(new FactionSwitchEvent(entityId, from, to));
        }
        // Multi-faction support: add allegiance
        public void AddAllegiance(string entityId, Faction faction, float affinity)
        {
            faction.SetAllegiance(entityId, new FactionAllegiance(entityId, faction, affinity));
        }
        // Event-driven relationship change
        public void ChangeRelationship(Faction a, Faction b, float delta)
        {
            float old = a.GetRelationshipWeight(b.Id);
            float nw = old + delta;
            a.SetRelationshipWeight(b.Id, nw);
            b.SetRelationshipWeight(a.Id, nw);
            OnRelationshipChanged?.Invoke(a, b, nw);
            // Fire UI feedback
            SystemsManager.Instance?.ShowFactionRelationshipChanged(Vector2.zero, a.Name, b.Name, nw);
            // Publish event
            EventBus.Instance?.Publish(new FactionRelationshipChangedEvent(a, b, nw));
        }
    }

    // --- Event types for event bus integration ---
    public struct FactionSchismEvent
    {
        public VisualDM.Entities.Faction Parent;
        public VisualDM.Entities.Faction Child;
        public FactionSchismEvent(VisualDM.Entities.Faction parent, VisualDM.Entities.Faction child)
        {
            Parent = parent;
            Child = child;
        }
    }
    public struct FactionSwitchEvent
    {
        public string EntityId;
        public VisualDM.Entities.Faction From;
        public VisualDM.Entities.Faction To;
        public FactionSwitchEvent(string entityId, VisualDM.Entities.Faction from, VisualDM.Entities.Faction to)
        {
            EntityId = entityId;
            From = from;
            To = to;
        }
    }
    public struct FactionRelationshipChangedEvent
    {
        public VisualDM.Entities.Faction A;
        public VisualDM.Entities.Faction B;
        public float Value;
        public FactionRelationshipChangedEvent(VisualDM.Entities.Faction a, VisualDM.Entities.Faction b, float value)
        {
            A = a;
            B = b;
            Value = value;
        }
    }
} 