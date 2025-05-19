using System;
using System.Collections.Generic;

namespace VisualDM.Entities
{
    /// <summary>
    /// RivalProfile tracks rivalry intensity, competition types, and scores for the Rival system.
    /// </summary>
    [Serializable]
    public class RivalProfile
    {
        public float Intensity;
        public List<string> CompetitionTypes = new();
        public Dictionary<string, float> CompetitionScores = new();
        public RivalProfile()
        {
            Intensity = 0f;
        }
    }
}