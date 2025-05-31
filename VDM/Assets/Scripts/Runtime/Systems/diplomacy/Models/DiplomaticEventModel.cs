using System;
using System.Collections.Generic;

namespace VDM.Systems.Diplomacy.Models
{
    [Serializable]
    public class DiplomaticEventModel
    {
        public string Id { get; set; }
        public object EventType { get; set; }
        public string Factions { get; set; }
        public DateTime Timestamp { get; set; }
        public object Description { get; set; }
        public int Severity { get; set; }
        public bool Public { get; set; }
        public string RelatedTreatyId { get; set; }
        public string RelatedNegotiationId { get; set; }
        public Dictionary<string, object> Metadata { get; set; }
        public Dictionary<string, object> TensionChange { get; set; }
    }
}
