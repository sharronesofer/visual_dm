using System.Collections.Generic;

namespace VisualDM.Timeline.Models
{
    public class Feat
    {
        public string Id { get; set; }
        public string Name { get; set; }
        public string Description { get; set; }
        public FeatCategory Category { get; set; }
        public int LevelRequirement { get; set; }
        public List<string> Prerequisites { get; set; } = new List<string>();
        public Dictionary<string, object> Metadata { get; set; } = new Dictionary<string, object>();
    }
} 