using System;
using System.Collections.Generic;
using UnityEngine;

namespace VisualDM.Systems.ArcSystem
{
    /// <summary>
    /// Serializable data contract for persisting arc state across sessions.
    /// </summary>
    [Serializable]
    public class ArcStateData
    {
        /// <summary>Unique identifier for the arc.</summary>
        public string ArcId;
        /// <summary>Progress value (e.g., completion percentage or step).</summary>
        public int Progress;
        /// <summary>Player choices made in this arc.</summary>
        public Dictionary<string, string> Choices = new Dictionary<string, string>();
        /// <summary>Dependencies on other arcs (by ID).</summary>
        public List<string> Dependencies = new List<string>();
        /// <summary>Last updated timestamp (Unix epoch ms).</summary>
        public long LastUpdated;
        /// <summary>Version of the serialization format.</summary>
        public int Version = 1;
        /// <summary>Additional metadata for special conditions.</summary>
        public Dictionary<string, string> Metadata = new Dictionary<string, string>();

        /// <summary>
        /// Serialize this ArcStateData to a JSON string.
        /// </summary>
        public string ToJson()
        {
            return JsonUtility.ToJson(this);
        }

        /// <summary>
        /// Deserialize a JSON string to an ArcStateData object.
        /// </summary>
        public static ArcStateData FromJson(string json)
        {
            return JsonUtility.FromJson<ArcStateData>(json);
        }
    }
}