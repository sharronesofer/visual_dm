using System;
using System.Collections.Generic;

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
    }
} 