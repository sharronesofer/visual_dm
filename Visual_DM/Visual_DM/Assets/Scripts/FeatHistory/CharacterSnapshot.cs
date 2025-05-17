using System;
using System.Collections.Generic;

namespace Visual_DM.FeatHistory
{
    [Serializable]
    public class CharacterSnapshot
    {
        public int Level { get; set; }
        public int Health { get; set; }
        public int Mana { get; set; }
        public int Strength { get; set; }
        public int Dexterity { get; set; }
        public int Intelligence { get; set; }
        public Dictionary<string, int> CustomStats { get; set; } // For extensibility

        public CharacterSnapshot()
        {
            CustomStats = new Dictionary<string, int>();
        }
    }
} 