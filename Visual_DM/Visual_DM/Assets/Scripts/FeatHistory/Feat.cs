using System;
using System.Collections.Generic;

namespace Visual_DM.FeatHistory
{
    [Serializable]
    public class Feat
    {
        public string Id { get; set; }
        public string Name { get; set; }
        public string Description { get; set; }
        public Dictionary<string, string> Metadata { get; set; }

        public Feat()
        {
            Metadata = new Dictionary<string, string>();
        }
    }
} 