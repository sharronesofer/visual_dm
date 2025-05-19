using System;
using System.Collections.Generic;
using VisualDM.NPC;

namespace VisualDM.Systems.Rivalry
{
    /// <summary>
    /// RivalRelationship extends the base relationship model with rivalry-specific attributes and memory integration.
    /// </summary>
    [Serializable]
    public class RivalRelationship
    {
        public string SourceNpcId;
        public string TargetNpcId;
        public float RivalryIntensity;
        public List<RelationshipMemory> Memories = new();
        public RivalProfile Profile;
        public DateTime LastInteraction;
        public int GrudgePoints;
        public RivalRelationship(string sourceNpcId, string targetNpcId)
        {
            SourceNpcId = sourceNpcId;
            TargetNpcId = targetNpcId;
            RivalryIntensity = 0f;
            LastInteraction = DateTime.UtcNow;
            GrudgePoints = 0;
        }
    }
}