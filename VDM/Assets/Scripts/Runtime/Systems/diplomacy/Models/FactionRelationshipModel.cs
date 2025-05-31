using System;
using System.Collections.Generic;

namespace VDM.Systems.Diplomacy.Models
{
    [Serializable]
    public class FactionRelationshipModel
    {
        public string FactionAId { get; set; }
        public string FactionBId { get; set; }
        public object Status { get; set; }
        public int Tension { get; set; }
        public string Treaties { get; set; }
        public DateTime LastStatusChange { get; set; }
        public string Negotiations { get; set; }
    }
}
