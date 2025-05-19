using System;
using UnityEngine;

namespace VisualDM.AI
{
    /// <summary>
    /// Stores an original event, its transformed rumor, and the calculated truth value.
    /// </summary>
    [Serializable]
    public class RumorRecord
    {
        public RumorEvent OriginalEvent;
        public string Rumor;
        [Range(0f, 1f)] public float TruthValue;

        public RumorRecord(RumorEvent originalEvent, string rumor, float truthValue)
        {
            OriginalEvent = originalEvent;
            Rumor = rumor;
            TruthValue = truthValue;
        }
    }
}