using System;
using System.Collections.Generic;

namespace Visual_DM.Entities
{
    public class FactionArc
    {
        public string Id { get; private set; }
        public string Title { get; set; }
        public string Description { get; set; }
        public List<Faction> Factions { get; private set; } = new List<Faction>();

        // Example arc progression properties
        public int Stage { get; private set; }
        public bool IsCompleted { get; private set; }

        // Event for arc progression changes
        public event Action<FactionArc, string, int, int> OnArcProgressionChanged;

        public FactionArc(string id, string title, string description)
        {
            Id = id;
            Title = title;
            Description = description;
        }

        public void AddFaction(Faction faction)
        {
            if (!Factions.Contains(faction))
            {
                Factions.Add(faction);
                faction.AddArc(this);
            }
        }

        public void RemoveFaction(Faction faction)
        {
            if (Factions.Contains(faction))
            {
                Factions.Remove(faction);
                faction.RemoveArc(this);
            }
        }

        // Example method to update arc stage
        public void SetStage(int newStage)
        {
            if (Stage != newStage)
            {
                int oldValue = Stage;
                Stage = newStage;
                OnArcProgressionChanged?.Invoke(this, "Stage", oldValue, newStage);
            }
        }

        // Prevent infinite recursion in AddFaction/RemoveFaction
        internal void AddFactionInternal(Faction faction)
        {
            if (!Factions.Contains(faction))
                Factions.Add(faction);
        }

        internal void RemoveFactionInternal(Faction faction)
        {
            Factions.Remove(faction);
        }

        // Similar methods for completion, etc.
    }
}