using System;
using System.Collections.Generic;

namespace VDM.Systems.Diplomacy.Models
{
    [Serializable]
    public class TreatyModel
    {
        public string Id { get; set; }
        public object Name { get; set; }
        public object Type { get; set; }
        public string Parties { get; set; }
        public Dictionary<string, object> Terms { get; set; }
        public DateTime StartDate { get; set; }
        public DateTime EndDate { get; set; }
        public bool IsActive { get; set; }
        public bool IsPublic { get; set; }
        public DateTime CreatedAt { get; set; }
        public DateTime UpdatedAt { get; set; }
        public string NegotiationId { get; set; }
    }
}
