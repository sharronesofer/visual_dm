using System;
using System.Collections.Generic;

namespace Visual_DM.Entities
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
    }
}