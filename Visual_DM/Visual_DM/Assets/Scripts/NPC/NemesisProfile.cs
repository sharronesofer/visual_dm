using System;
using System.Collections.Generic;

namespace VisualDM.NPC
{
    /// <summary>
    /// NemesisProfile tracks nemesis power scaling, vendetta status, and special abilities for the Nemesis system.
    /// </summary>
    [Serializable]
    public class NemesisProfile
    {
        public float PowerLevel;
        public bool VendettaActive;
        public List<string> SpecialAbilities = new();
        public Dictionary<string, object> Attributes = new();
        public NemesisProfile()
        {
            PowerLevel = 1.0f;
            VendettaActive = false;
        }
    }
}