using System;
using System.Collections.Generic;

namespace VDM.Systems.Diplomacy.Models
{
    [Serializable]
    public class DiplomaticIncidentModel
    {
        public string Id { get; set; }
        public object IncidentType { get; set; }
        public string PerpetratorId { get; set; }
        public string VictimId { get; set; }
        public object Description { get; set; }
        public Dictionary<string, object> Evidence { get; set; }
        public object Severity { get; set; }
        public int TensionImpact { get; set; }
        public bool Public { get; set; }
        public DateTime Timestamp { get; set; }
        public string WitnessedBy { get; set; }
        public string RelatedEventId { get; set; }
        public string RelatedTreatyId { get; set; }
        public bool Resolved { get; set; }
        public object ResolutionDetails { get; set; }
        public DateTime ResolutionDate { get; set; }
    }
}
