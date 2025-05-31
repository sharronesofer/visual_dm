using System;
using System.Collections.Generic;

namespace VDM.Systems.Diplomacy.Models
{
    [Serializable]
    public class TreatyViolationModel
    {
        public string Id { get; set; }
        public string TreatyId { get; set; }
        public string ViolatorId { get; set; }
        public object ViolationType { get; set; }
        public object Description { get; set; }
        public Dictionary<string, object> Evidence { get; set; }
        public string ReportedBy { get; set; }
        public DateTime Timestamp { get; set; }
        public int Severity { get; set; }
        public bool Acknowledged { get; set; }
        public bool Resolved { get; set; }
        public object ResolutionDetails { get; set; }
    }
}
