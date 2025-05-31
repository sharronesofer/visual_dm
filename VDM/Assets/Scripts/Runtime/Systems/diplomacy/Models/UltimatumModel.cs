using System;
using System.Collections.Generic;

namespace VDM.Systems.Diplomacy.Models
{
    [Serializable]
    public class UltimatumModel
    {
        public string Id { get; set; }
        public string IssuerId { get; set; }
        public string RecipientId { get; set; }
        public Dictionary<string, object> Demands { get; set; }
        public Dictionary<string, object> Consequences { get; set; }
        public object Status { get; set; }
        public DateTime IssueDate { get; set; }
        public DateTime Deadline { get; set; }
        public DateTime ResponseDate { get; set; }
        public object Justification { get; set; }
        public bool Public { get; set; }
        public string WitnessedBy { get; set; }
        public string RelatedIncidentId { get; set; }
        public string RelatedTreatyId { get; set; }
        public string RelatedEventId { get; set; }
        public int TensionChangeOnIssue { get; set; }
        public int TensionChangeOnAccept { get; set; }
        public int TensionChangeOnReject { get; set; }
    }
}
