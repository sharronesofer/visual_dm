using System;
using System.Collections.Generic;

namespace VDM.Systems.War
{
    /// <summary>
    /// Serializable data structure for saving/loading war and tension state.
    /// </summary>
    [Serializable]
    public class SerializableWarState
    {
        public List<SerializableWar> ActiveWars = new();
        public List<SerializableTension> Tensions = new();
        public List<WarEvent> RecentEvents = new();
    }

    [Serializable]
    public class SerializableWar
    {
        public string FactionA;
        public string FactionB;
        public float WarExhaustionA;
        public float WarExhaustionB;
        public bool IsActive;
        public List<WarEvent> Events = new();
    }

    [Serializable]
    public class SerializableTension
    {
        public string FactionA;
        public string FactionB;
        public float Tension;
    }
} 