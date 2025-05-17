using System.Collections.Generic;
using VisualDM.Simulation;

namespace Visual_DM.Timeline.Models
{
    public class CharacterBuild
    {
        public string Name { get; set; }
        public CharacterStats Stats { get; set; }
        public string Role { get; set; } // e.g., "Tank", "DPS", "Support"
        public string Playstyle { get; set; } // e.g., "Aggressive", "Defensive", "Balanced"
        public List<Feat> SelectedFeats { get; set; } = new List<Feat>();
        public int Level { get; set; }
    }
} 