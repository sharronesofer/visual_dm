using System;
using System.Collections.Generic;

namespace VDM.Systems.Diplomacy.Models
{
    [Serializable]
    public class NegotiationModel
    {
        public string Id { get; set; }
        public string Parties { get; set; }
        public string InitiatorId { get; set; }
        public object Status { get; set; }
        public List<object> Offers { get; set; }
        public string CurrentOfferId { get; set; }
        public object TreatyType { get; set; }
        public DateTime StartDate { get; set; }
        public DateTime EndDate { get; set; }
        public string ResultTreatyId { get; set; }
        public Dictionary<string, object> Metadata { get; set; }
    }
}
