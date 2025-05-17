using System;
using System.Collections.Generic;
using VisualDM.NPC;

namespace VisualDM.Systems.Rivalry
{
    /// <summary>
    /// NemesisRelationship extends the base relationship model with nemesis-specific attributes and memory integration.
    /// </summary>
    [Serializable]
    public class NemesisRelationship
    {
        public string SourceNpcId;
        public string TargetNpcId;
        public float NemesisIntensity;
        public List<RelationshipMemory> Memories = new();
        public NemesisProfile Profile;
        public DateTime LastVendetta;
        public int GrudgePoints;
        public bool IsVendettaActive;
        public NemesisRelationship(string sourceNpcId, string targetNpcId)
        {
            SourceNpcId = sourceNpcId;
            TargetNpcId = targetNpcId;
            NemesisIntensity = 0f;
            LastVendetta = DateTime.UtcNow;
            GrudgePoints = 0;
            IsVendettaActive = false;
        }
    }
}