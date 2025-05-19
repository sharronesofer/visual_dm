using System;
using UnityEngine;

namespace VDM.Systems.War
{
    /// <summary>
    /// Serializable war event for battles, negotiations, sanctions, etc.
    /// </summary>
    [Serializable]
    public class WarEvent
    {
        public string EventType;
        public string FactionA;
        public string FactionB;
        public DateTime Timestamp;
        public string Outcome;
        [TextArea]
        public string Description;
    }
} 