using System;
using System.Collections.Generic;

namespace VDM.Systems.Diplomacy.Models
{
    [Serializable]
    public class SanctionModel
    {
        public string Id { get; set; }
        public string ImposerId { get; set; }
        public string TargetId { get; set; }
        public object SanctionType { get; set; }
        public object Description { get; set; }
        public object Status { get; set; }
        public object Justification { get; set; }
        public DateTime ImposedDate { get; set; }
        public DateTime EndDate { get; set; }
        public DateTime LiftedDate { get; set; }
        public Dictionary<string, object> ConditionsForLifting { get; set; }
        public int Severity { get; set; }
        public int EconomicImpact { get; set; }
        public int DiplomaticImpact { get; set; }
        public Dictionary<string, object> EnforcementMeasures { get; set; }
        public string SupportingFactions { get; set; }
        public string OpposingFactions { get; set; }
        public List<object> Violations { get; set; }
        public bool IsPublic { get; set; }
    }
}
